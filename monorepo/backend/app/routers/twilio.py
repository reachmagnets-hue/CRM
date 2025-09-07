from __future__ import annotations

from fastapi import APIRouter, Form, Request
from fastapi.responses import PlainTextResponse

from ..services.rag import build_prompt, retrieve
from ..services.llm import stream_generate
from ..services.stt import transcribe_from_twilio_payload
from ..services.tts import synthesize_to_file


router = APIRouter(tags=["twilio"])


@router.post("/twilio/voice")
async def twilio_voice(request: Request) -> PlainTextResponse:
    # Simple welcome and gather speech
    base = "How can I help you today?"
    twiml = f"""
<Response>
  <Gather input="speech" action="/api/v1/twilio/handle" method="POST" timeout="5">
    <Say>{base}</Say>
  </Gather>
  <Say>Goodbye</Say>
</Response>
""".strip()
    return PlainTextResponse(twiml, media_type="application/xml")


@router.post("/twilio/handle")
async def twilio_handle(request: Request, SpeechResult: str = Form(default="")) -> PlainTextResponse:  # noqa: N803
    tenant_id = "default"  # For voice, resolve via dedicated number mapping later
    query = transcribe_from_twilio_payload(SpeechResult)
    hits = await retrieve(tenant_id, query, top_k=4)
    messages = build_prompt(query, hits)

    # Accumulate small text before TTS to avoid staccato audio
    text_resp = []
    async for chunk in stream_generate(messages):
        text_resp.append(chunk)
        if len("".join(text_resp)) > 500:
            break
    final_text = "".join(text_resp).strip() or "Sorry, I had trouble answering."
    audio_url = synthesize_to_file(final_text)

    twiml = f"""
<Response>
  <Play>{audio_url}</Play>
  <Gather input="speech" action="/api/v1/twilio/handle" method="POST" timeout="5">
    <Say>You can ask another question.</Say>
  </Gather>
</Response>
""".strip()
    return PlainTextResponse(twiml, media_type="application/xml")
