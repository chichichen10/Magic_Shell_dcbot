from dataclasses import dataclass
import asyncio
import os

import discord
import youtube_dl


FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}
YDL_OPTIONS = {"format": "bestaudio"}


@dataclass
class QueuedAudio:
    filename: str
    voice_channel: discord.VoiceChannel


class AudioPlayer:
    def __init__(self):
        self._queue: list[QueuedAudio] = []
        self.is_playing = False
        self.is_paused = False

    def add(self, filename, voice_channel) -> None:
        self._queue.append(QueuedAudio(str(filename), voice_channel))

    def clear(self) -> None:
        self._queue.clear()
        self.is_playing = False

    async def play(self) -> None:
        if self.is_playing or not self._queue:
            return

        opus_path = os.getenv("OPUS_PATH")
        if opus_path and not discord.opus.is_loaded():
            discord.opus.load_opus(os.path.join(opus_path, "libopus.so"))

        voice_channel = self._queue[0].voice_channel
        try:
            voice_client = await voice_channel.connect()
        except discord.errors.ConnectionClosed as error:
            print(f"Voice connect rejected (code {error.code}), clearing queue")
            self._queue.clear()
            return
        except Exception:
            if voice_channel.name == "垃圾車" and self._queue:
                self._queue.pop(0)
            return

        try:
            self.is_playing = True
            while self._queue:
                if self._queue[0].voice_channel != voice_channel:
                    break
                audio = self._queue.pop(0)
                voice_client.play(discord.FFmpegPCMAudio(audio.filename), after=None)
                voice_client.source.volume = 10.0
                await asyncio.sleep(1)
                while voice_client.is_playing():
                    await asyncio.sleep(0.1)
                await asyncio.sleep(1)
        except discord.errors.ConnectionClosed as error:
            print(f"Voice connection lost mid-play (code {error.code}), clearing queue")
            self._queue.clear()
        except Exception as error:
            print(repr(error))
        finally:
            self.is_playing = False
            try:
                await voice_client.disconnect()
            except Exception:
                pass

        if self._queue:
            await self.play()

    async def play_music(self, url, voice_channel) -> None:
        try:
            voice_client = await voice_channel.connect()
        except discord.ClientException:
            return

        try:
            with youtube_dl.YoutubeDL(YDL_OPTIONS) as downloader:
                info = await asyncio.to_thread(
                    downloader.extract_info, url, download=False
                )
                source_url = info["formats"][0]["url"]
                source = await discord.FFmpegOpusAudio.from_probe(
                    source_url, **FFMPEG_OPTIONS
                )
                voice_client.play(source)
                await asyncio.sleep(1)
                while voice_client.is_playing() or self.is_paused:
                    await asyncio.sleep(0.1)
                await asyncio.sleep(1)
        except Exception as error:
            print(error)
        finally:
            await voice_client.disconnect()
            if self._queue:
                await self.play()

    @staticmethod
    def _find_voice_client(client, voice_channel):
        return next(
            (item for item in client.voice_clients if item.channel == voice_channel),
            None,
        )

    async def pause(self, client, voice_channel) -> None:
        voice_client = self._find_voice_client(client, voice_channel)
        if voice_client is None:
            return
        self.is_paused = True
        voice_client.pause()

    async def resume(self, client, voice_channel) -> None:
        voice_client = self._find_voice_client(client, voice_channel)
        if voice_client is None:
            return
        self.is_paused = False
        voice_client.resume()

    async def stop(self, client, voice_channel) -> None:
        voice_client = self._find_voice_client(client, voice_channel)
        if voice_client is not None:
            voice_client.stop()


DC_player = AudioPlayer
