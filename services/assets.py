from pathlib import Path


class AssetPaths:
    def __init__(self, root: Path):
        self.root = root

    def ensure_runtime_directories(self) -> None:
        for name in ("name", "welcome1", "welcome2", "bye"):
            (self.root / name).mkdir(parents=True, exist_ok=True)

    def name(self, display_name: str) -> Path:
        return self.root / "name" / f"{display_name}.mp3"

    def welcome(self, variant: str, display_name: str) -> Path:
        return self.root / f"welcome{variant}" / f"{display_name}.mp3"

    def bye(self, display_name: str) -> Path:
        return self.root / "bye" / f"{display_name}.mp3"

    def voice(self, filename: str) -> Path:
        return self.root / "voice" / filename
