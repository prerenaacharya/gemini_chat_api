# app/chatroom/utils.py

import google.generativeai as genai
from fastapi.responses import StreamingResponse

from app.config import settings
genai.configure(api_key=settings.GEMINI_API_KEY)


def stream_gemini_response_with_db(prompt: str, db, chatroom_id: int):
    model = genai.GenerativeModel("gemini-2.0-flash")

    response = model.generate_content(prompt, stream=True)

    collected_chunks = []

    def generator():
        for chunk in response:
            if chunk.text:
                collected_chunks.append(chunk.text)
                yield chunk.text

    def finalize():
        from app.chatroom.models import Message
        full_text = "".join(collected_chunks)

        # Find the most recent "ai" message with "(processing...)" content
        ai_msg = db.query(Message).filter(
            Message.chatroom_id == chatroom_id,
            Message.sender == "ai",
            Message.content == "(processing...)"
        ).order_by(Message.id.desc()).first()

        if ai_msg:
            ai_msg.content = full_text
            db.commit()

    # Use StreamingResponse with callback logic
    class ResponseWrapper:
        def __iter__(self):
            for chunk in generator():
                yield chunk
            finalize()

    return StreamingResponse(ResponseWrapper(), media_type="text/plain")
