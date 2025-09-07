from __future__ import annotations


def transcribe_from_twilio_payload(speech_text: str) -> str:
    """For MVP, Twilio provides the transcript already via <Gather input="speech">.
    This function can normalize or post-process the transcript.
    """
    return speech_text.strip()
