import logging

import discord

from logger import logger
from repositories import BotRepository
from services import AssetPaths


def register_lifecycle_events(
    client,
    repository: BotRepository,
    assets: AssetPaths,
    voice_handler,
    running_lock,
) -> None:
    log = logger()

    @client.event
    async def on_ready():
        logging.getLogger("hypercorn.access").setLevel(logging.FATAL)
        log.info("目前登入身份：" + str(client.user))
        repository.initialize(str(client.user))
        assets.ensure_runtime_directories()
        await client.change_presence(activity=discord.Game("聯盟戰棋"))
        running_lock.write_text("running!", encoding="utf-8")

    @client.event
    async def on_disconnect():
        log.err("Gateway disconnected")

    @client.event
    async def on_resumed():
        log.info("Gateway reconnected, checking voice status...")
        await voice_handler.recover()
