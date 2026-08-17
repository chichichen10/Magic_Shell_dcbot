import asyncio
from pathlib import Path

from fish import tts


class TTSService:
    def __init__(self, api_key: str, reference_id: str):
        self._api_key = api_key
        self._reference_id = reference_id

    async def synthesize(self, text: str, filename: Path) -> None:
        filename.parent.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread(
            tts,
            text,
            str(filename),
            self._api_key,
            self._reference_id,
        )
