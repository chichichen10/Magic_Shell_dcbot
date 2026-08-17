import asyncio
import random
import traceback

from pydub import AudioSegment, effects

from config import Settings
from logger import logger
from repositories import BotRepository
from services import AssetPaths, AudioPlayer, TTSService


class VoiceEventHandler:
    def __init__(
        self,
        client,
        player: AudioPlayer,
        tts_service: TTSService,
        assets: AssetPaths,
        repository: BotRepository,
        settings: Settings,
    ):
        self.client = client
        self.player = player
        self.tts = tts_service
        self.assets = assets
        self.repository = repository
        self.settings = settings
        self.log = logger()

    async def recover(self) -> None:
        self.player.clear()
        for voice_client in self.client.voice_clients:
            try:
                await voice_client.disconnect(force=True)
                self.log.info("語音連線壞掉，自動離開")
            except Exception as error:
                self.log.err(f"離開語音頻道失敗：{error}")

    async def handle(self, member, before, after) -> None:
        if self.repository.get_mode() == "0" or member == self.client.user:
            return
        if member.display_name == "傑哥KTV":
            return

        await self._remove_empty_temporary_channels(member.guild)
        if after.channel is not None and before.channel != after.channel:
            await self._handle_join(member, after.channel)
        elif member.id == self.settings.vip_id and after.channel is None:
            self.player.add(self.assets.voice("vip_bye.mp3"), before.channel)
            await self.player.play()
        elif after.channel is None:
            await self._handle_leave(member, before.channel)

    @staticmethod
    async def _remove_empty_temporary_channels(guild) -> None:
        temporary_names = {"紅隊", "藍隊", "垃圾車"}
        for channel in guild.voice_channels:
            if channel.name in temporary_names and not channel.members:
                await channel.delete()

    async def _handle_join(self, member, voice_channel) -> None:
        if random.choice(range(1, 50)) == 25 and voice_channel.name != "垃圾車":
            trash_channel = await member.guild.create_voice_channel("垃圾車")
            await member.move_to(trash_channel)
            return
        if voice_channel.name == "垃圾車":
            self.player.add("trash2.mp3", voice_channel)
            await self.player.play()
            return

        try:
            display_name = self.repository.get_nickname(member.display_name)
            self.log.info(
                f"{member.display_name} in {member.guild.name}[{voice_channel.name}]"
            )
            variant = str(random.choice(range(1, 3)))
            welcome_file = self.assets.welcome(variant, display_name)
            if not welcome_file.is_file():
                name_file = await self._ensure_name_audio(display_name)
                await asyncio.to_thread(
                    self._compose_welcome,
                    variant,
                    name_file,
                    welcome_file,
                )
            self.player.add(welcome_file, voice_channel)

            voice_filename = (
                "voice_"
                + str(random.choice(range(1, self.settings.voice_file_count)))
                + ".mp3"
            )
            if member.id == self.settings.vip_id:
                voice_filename = "voice_angry.mp3"
            self.player.add(self.assets.voice(voice_filename), voice_channel)
            await self.player.play()
        except Exception as error:
            print(traceback.format_exc())
            print(error)

    async def _handle_leave(self, member, voice_channel) -> None:
        try:
            display_name = self.repository.get_nickname(member.display_name)
            self.log.info(
                f"{member.display_name} out {member.guild.name}[{voice_channel.name}]"
            )
            bye_file = self.assets.bye(display_name)
            if not bye_file.is_file():
                name_file = await self._ensure_name_audio(display_name)
                await asyncio.to_thread(
                    self._compose_bye,
                    name_file,
                    bye_file,
                )
            self.player.add(bye_file, voice_channel)
            await self.player.play()
        except Exception as error:
            print(error)

    async def _ensure_name_audio(self, display_name: str):
        name_file = self.assets.name(display_name)
        if not name_file.is_file():
            await self.tts.synthesize(display_name, name_file)
        return name_file

    def _compose_welcome(self, variant, name_file, output_file) -> None:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        pre_welcome = AudioSegment.from_mp3(
            self.assets.voice(f"prewelcome{variant}.mp3")
        )
        name_voice = effects.speedup(AudioSegment.from_mp3(name_file), 1.3)
        welcome = pre_welcome + name_voice
        if variant == "2":
            welcome += AudioSegment.from_mp3(
                self.assets.voice(f"postwelcome{variant}.mp3")
            )
        welcome.export(output_file, format="mp3")

    def _compose_bye(self, name_file, output_file) -> None:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        name_voice = effects.speedup(AudioSegment.from_mp3(name_file), 1.3)
        bye = name_voice + AudioSegment.from_mp3(self.assets.voice("bye.mp3"))
        bye.export(output_file, format="mp3")


def register_voice_events(client, handler: VoiceEventHandler) -> None:
    @client.event
    async def on_voice_state_update(member, before, after):
        await handler.handle(member, before, after)
