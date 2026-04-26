from datetime import datetime

# Takes list of dicts from api and convert to plain text
def build_context(records: list[dict]) -> str:
    
    if not records:
        return "No data found for this container."

    # overall container info from the latest record
    latest = records[-1]
    container_id    = latest["data"].get("containerID", "N/A")
    overall_status  = latest.get("status", "N/A")
    total_records   = len(records)
    verified_count  = sum(1 for r in records if r.get("verified") is True)

    # count warnings vs safe across all records 
    warning_count = sum(1 for r in records if r.get("status") == "WARNING")
    safe_count    = sum(1 for r in records if r.get("status") == "SAFE")

    # latest sensor readings
    latest_data   = latest.get("data", {})
    temperature   = latest_data.get("temperature", "N/A")
    humidity      = latest_data.get("humidity", "N/A")
    gps_location  = latest_data.get("gpsLocation", "N/A")
    reading_time  = latest_data.get("timestamp", "N/A")
    blockchain_hash = latest.get("blockchainHash", "N/A")

    # collect ALL violations across all records 
    all_violations = []
    for r in records:
        for v in r["data"].get("violations", []):
            all_violations.append({
                "type":      v.get("type", "unknown"),
                "value":     v.get("value", "N/A"),
                "threshold": v.get("threshold", "N/A"),
                "severity":  v.get("severity", "N/A"),
                "time":      r["data"].get("timestamp", "N/A"),
            })

    if all_violations:
        violations_lines = "\n".join(
            f"  - {v['type'].upper()} violation: recorded {v['value']} "
            f"(threshold {v['threshold']}, severity {v['severity']}) at {v['time']}"
            for v in all_violations
        )
        violations_text = violations_lines
    else:
        violations_text = "  No violations recorded across all readings."

    # temperature history (all readings) 
    temp_history = "\n".join(
        f"  [{r['data'].get('timestamp', 'N/A')}]  "
        f"Temp: {r['data'].get('temperature', 'N/A')}°C  "
        f"Humidity: {r['data'].get('humidity', 'N/A')}%  "
        f"Status: {r.get('status', 'N/A')}"
        for r in records
    )

    context = f"""
CONTAINER SUMMARY
-----------------
Container ID     : {container_id}
Overall Status   : {overall_status}
Total Records    : {total_records}
Blockchain Verified Records: {verified_count} / {total_records}
Safe Readings    : {safe_count}
Warning Readings : {warning_count}

LATEST SENSOR READING
---------------------
Timestamp        : {reading_time}
Temperature      : {temperature}°C
Humidity         : {humidity}%
GPS Location     : {gps_location}
Blockchain Hash  : {blockchain_hash}

ALL VIOLATIONS DETECTED
-----------------------
{violations_text}

FULL TEMPERATURE & HUMIDITY HISTORY
------------------------------------
{temp_history}
""".strip()

    return context