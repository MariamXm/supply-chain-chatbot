import os
from groq import AsyncGroq
from typing import List

MODEL = "llama-3.3-70b-versatile"

SYSTEM_INSTRUCTION = """You are a helpful supply chain assistant.
Your job is to answer customer questions about their product shipment.

You will be given real sensor and blockchain data for the container.
Answer using ONLY that data and never make up information.If you do not know the answer, just say so honestly.

Rules:
- Keep answers short, clear, and friendly (4 to 6 sentences)
- If a violation exists, explain it calmly — what happened, how serious it is
- If the data does not contain the answer, say so honestly
- Blockchain verified means the data has not been tampered with
- Status WARNING means at least one sensor reading was outside safe range
- Status SAFE means all readings were within acceptable limits"""


async def get_llm_reply(
    context: str,
    conversation_history: List,
    user_message: str
) -> str:

    client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

    system_message = {
        "role": "system",
        "content": f"{SYSTEM_INSTRUCTION}\n\n{context}"
    }

    history_messages = [
        {"role": msg.role, "content": msg.content}
        for msg in conversation_history
    ]

    current_message = {
        "role": "user",
        "content": user_message
    }

    messages = [system_message] + history_messages + [current_message]

    response = await client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=512,
        temperature=0.3,
    )

    return response.choices[0].message.content