import asyncio
import traceback

import discord
from discord import app_commands
from replit import db

from bot.commands import register_general_commands, register_team_commands
from bot.events import (
    VoiceEventHandler,
    register_lifecycle_events,
    register_message_events,
    register_voice_events,
)
from config import Settings
from repositories import BotRepository
from services import (
    AIMessageService,
    AssetPaths,
    AudioPlayer,
    TeamService,
    TTSService,
)
from state import BotState
from web import Dashboard


class BotApplication:
    def __init__(self, settings: Settings):
        self.settings = settings
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        self.client = discord.Client(intents=intents)
        self.tree = app_commands.CommandTree(self.client)

        self.repository = BotRepository(db)
        self.state = BotState()
        self.assets = AssetPaths(settings.asset_root)
        self.player = AudioPlayer()
        self.team_service = TeamService()
        self.tts_service = TTSService(
            settings.fish_audio_api_key, settings.fish_reference_id
        )
        self.ai_service = AIMessageService(
            settings.openai_api_key,
            settings.openai_model,
            self.repository,
        )
        self.voice_handler = VoiceEventHandler(
            self.client,
            self.player,
            self.tts_service,
            self.assets,
            self.repository,
            settings,
        )
        self.dashboard = Dashboard(self.repository)
        self.running_lock = settings.asset_root / "running.lock"
        self._register_handlers()

    def _register_handlers(self) -> None:
        register_general_commands(self.tree, self.state)
        register_team_commands(self.tree, self.team_service)
        register_lifecycle_events(
            self.client,
            self.repository,
            self.assets,
            self.voice_handler,
            self.running_lock,
        )
        register_voice_events(self.client, self.voice_handler)
        register_message_events(
            self.client,
            self.tree,
            self.settings,
            self.ai_service,
            self.team_service,
        )

    async def start(self) -> None:
        async with self.client:
            dashboard_task = asyncio.create_task(
                self.dashboard.app.run_task(
                    host=self.settings.dashboard_host,
                    port=self.settings.dashboard_port,
                )
            )
            try:
                await self.client.start(self.settings.bot_token)
            finally:
                dashboard_task.cancel()


def run() -> None:
    settings = Settings.from_env()
    running_lock = settings.asset_root / "running.lock"
    running_lock.unlink(missing_ok=True)
    try:
        asyncio.run(BotApplication(settings).start())
    except Exception:
        traceback.print_exc()
        raise
    finally:
        running_lock.unlink(missing_ok=True)
