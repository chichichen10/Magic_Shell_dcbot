from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    bot_token: str
    fish_audio_api_key: str
    openai_api_key: str
    fish_reference_id: str = "f22282c781844c66bfc6e91602bd74c5"
    openai_model: str = "gpt-5.6-luna"
    voice_file_count: int = 25
    vip_id: int = 429657581313720321
    admin_name: str = "Chi"
    dashboard_host: str = "0.0.0.0"
    dashboard_port: int = 80
    asset_root: Path = Path(".")

    @classmethod
    def from_env(cls) -> "Settings":
        required = {
            "BOT_TOKEN": os.getenv("BOT_TOKEN"),
            "FISH_AUDIO_API_KEY": os.getenv("FISH_AUDIO_API_KEY"),
            "OPEN_AI_API_KEY": os.getenv("OPEN_AI_API_KEY"),
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise RuntimeError(
                "Missing required environment variables: " + ", ".join(missing)
            )

        return cls(
            bot_token=required["BOT_TOKEN"],
            fish_audio_api_key=required["FISH_AUDIO_API_KEY"],
            openai_api_key=required["OPEN_AI_API_KEY"],
            fish_reference_id=os.getenv("FISH_REFERENCE_ID", cls.fish_reference_id),
            openai_model=os.getenv("OPEN_AI_MODEL", cls.openai_model),
            dashboard_host=os.getenv("DASHBOARD_HOST", cls.dashboard_host),
            dashboard_port=int(os.getenv("PORT", str(cls.dashboard_port))),
            asset_root=Path(os.getenv("ASSET_ROOT", ".")),
        )
