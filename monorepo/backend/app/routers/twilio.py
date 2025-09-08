from __future__ import annotations

from fastapi import APIRouter, Form, Request
from fastapi.responses import PlainTextResponse

from ..services.rag import build_prompt, retrieve
from ..services.llm import stream_generate
from ..services.stt import transcribe_from_twilio_payload
from ..services.tts import synthesize_to_file
from ..config import SETTINGS
from ..services.db import open_session, CallLog


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
  # Resolve tenant by called number mapping
  form = await request.form()
  from_number = str(form.get("To", "")).strip() or str(form.get("Called", "")).strip()
  tenant_id = "default"
  # SETTINGS.twilio_number_map: tenant_id -> [numbers]
  for t_id, numbers in SETTINGS.twilio_number_map.items():
    if from_number in numbers:
      tenant_id = t_id
      break

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
  # Determine simple intent
  default_intent = None
  for number, labels in SETTINGS.twilio_service_map.items():
    if from_number == number and labels:
      default_intent = labels[0]
      break
  intent = default_intent
  qlow = (query or "").lower()
  if "book" in qlow or "appointment" in qlow:
    intent = intent or "book_appointment"
  # Log best-effort
  try:
    with open_session() as session:
      session.add(CallLog(site_id=tenant_id, from_number=from_number, customer_id=None, transcript=f"Q: {query}\nA: {final_text}", service_intent=intent, outcome="completed"))
      session.commit()
  except Exception:
    pass
  audio_path = synthesize_to_file(final_text)
  # Build absolute URL when TWILIO_VOICE_WEBHOOK_BASE is set
  base = (SETTINGS.twilio_voice_webhook_base or "").rstrip("/")
  audio_url = f"{base}{audio_path}" if base else audio_path

  twiml = f"""
<Response>
  <Play>{audio_url}</Play>
  <Gather input="speech" action="/api/v1/twilio/handle" method="POST" timeout="5">
    <Say>You can ask another question.</Say>
  </Gather>
</Response>
""".strip()
  return PlainTextResponse(twiml, media_type="application/xml")
