import discord
import asyncio

class dc_player:
    async def play(voice_channel:discord.VoiceChannel,audio_file:str):  
        for i in range(1):
            try:
                vc = await voice_channel.connect()
                break
            except discord.ClientException:
                await asyncio.sleep(0.5)
        if(vc):
            try:
                while (vc.is_playing()):
                    await asyncio.sleep(0.1)
                audio_source2 = discord.FFmpegPCMAudio(audio_file)
                vc.play(audio_source2, after=None)
                vc.source.volume = 10.0
                await asyncio.sleep(1)
                while (vc.is_playing()):
                    await asyncio.sleep(0.1)
                await asyncio.sleep(0.1)
            except:
                pass
            await vc.disconnect()