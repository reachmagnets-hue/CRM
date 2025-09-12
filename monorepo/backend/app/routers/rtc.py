from __future__ import annotations

import asyncio
from typing import Optional, Any
from importlib import import_module

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Optional imports for type checking and runtime flexibility
# runtime: import lazily and tolerate absence
_RTCPeerConnection = None  # type: ignore
_RTCSessionDescription = None  # type: ignore
try:
    _aiortc = import_module("aiortc")
    _RTCPeerConnection = getattr(_aiortc, "RTCPeerConnection")  # type: ignore
    _RTCSessionDescription = getattr(_aiortc, "RTCSessionDescription")  # type: ignore
except Exception:
    pass


router = APIRouter(tags=["rtc"], prefix="/rtc")

# Track live peer connections so they don't get GC'd immediately
_PEERS = set()


class SDP(BaseModel):
    type: str
    sdp: str


@router.get("/health")
async def rtc_health() -> dict:
    return {"ok": True, "pc": bool(_RTCPeerConnection)}


@router.post("/offer")
async def create_answer(offer: SDP) -> dict:
    if _RTCPeerConnection is None or _RTCSessionDescription is None:
        raise HTTPException(status_code=503, detail="RTC not available on server")

    pc: _RTCPeerConnection = _RTCPeerConnection()  # type: ignore[assignment]
    _PEERS.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():  # pragma: no cover - runtime effect only
        if pc.connectionState in ("failed", "closed", "disconnected"):
            await pc.close()
            _PEERS.discard(pc)

    @pc.on("datachannel")
    def on_datachannel(channel):  # pragma: no cover
        # IVR/data messages from client widget
        @channel.on("message")
        def on_message(message: Any):
            # Echo back for now; future: route DTMF/menu selections
            try:
                channel.send(str(message))
            except Exception:
                pass

    # Ensure an "ivr" channel exists (negotiated)
    try:
        pc.createDataChannel("ivr")
    except Exception:
        pass

    remote: _RTCSessionDescription = _RTCSessionDescription(sdp=offer.sdp, type=offer.type)  # type: ignore[assignment]
    await pc.setRemoteDescription(remote)

    # Audio receive: drain frames to keep pipeline active (placeholder sink)
    @pc.on("track")
    def on_track(track):  # pragma: no cover
        if getattr(track, "kind", None) == "audio":
            async def _drain():
                try:
                    while True:
                        frame = await track.recv()
                        # Placeholder: here we could run STT on PCM frames
                        _ = frame  # noqa: F841
                except Exception:
                    try:
                        await track.stop()
                    except Exception:
                        pass
            asyncio.ensure_future(_drain())

    # Create a bare answer (no media until MVP client sends tracks)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    return {"type": pc.localDescription.type, "sdp": pc.localDescription.sdp}
