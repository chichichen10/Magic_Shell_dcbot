import discord
import asyncio
import youtube_dl

class Audio:
    def __init__(self,filename:str,voice_channel:discord.VoiceChannel):
        self.filename = filename
        self.voice_channel = voice_channel

class Music:
    def __init__(self,source,voice_channel:discord.VoiceChannel):
        self.source = source
        self.voice_channel = voice_channel

class PlayList:
    def __init__(self):
        self.queue = []
        self.isPlaying = False
    def pop(self):
        return self.queue.pop(0)
    def len(self):
        return len(self.queue)
    def add(self, audio):
        self.queue.append(audio)
    def get_current_channel(self)->discord.VoiceChannel: 
        return self.queue[0].voice_channel

class MusicPlayList:
    def __init__(self):
        self.queue = []
        self.isPlaying = False
    def pop(self):
        return self.queue.pop(0)
    def len(self):
        return len(self.queue)
    def add(self, audio):
        self.queue.append(audio)
    def get_current_channel(self)->discord.VoiceChannel: 
        return self.queue[0].voice_channel

class DC_player:
    def __init__(self):
        self.playList = PlayList()
        self.isPlaying = False
        self.isPause = False
        self.musicPlayList = MusicPlayList()

    def add(self,file,voice_channel):
        self.playList.add(Audio(file,voice_channel))
    
    async def play(self):
        # self.playList.add(Audio(file,voice_channel))
        voice_channel = self.playList.get_current_channel()
        print(voice_channel)
        if(not self.isPlaying):
            try:
                vc = await voice_channel.connect()
            except:
                if(voice_channel.name == '垃圾車'):
                    self.playList.pop()                
                return
            try:
                self.isPlaying = True
                while(self.playList.len()>0):  
                    print(self.playList.queue)
                    if(self.playList.get_current_channel() == voice_channel):
                        audio_source = discord.FFmpegPCMAudio(self.playList.pop().filename)
                        vc.play(audio_source, after=None)
                        vc.source.volume = 10.0
                        await asyncio.sleep(1)
                        while (vc.is_playing()):
                            await asyncio.sleep(0.1)
                        await asyncio.sleep(1)
                    else:
                        break

            except:
                pass
            finally:
                self.isPlaying = False
                await vc.disconnect()
                if(self.playList.len()>0):
                    print('redo')
                    print(self.playList.get_current_channel())
                    await self.play()

    async def add_music_playlist(self, url, voice_channel):
        FFMPEG_OPTIONS = {'before_options':'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options':'-vn'}
        YDL_OPTIONS = {'format':'bestaudio'}
        try:
            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                info =  ydl.extract_info(url, download=False)
                url2 = info['formats'][0]['url']
                source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
                self.musicPlayList.add(Music(source,voice_channel))
                # vc.source = discord.PCMVolumeTransformer(vc.source)
                # vc.source.volume = 0.01        
        except Exception as e:
            print(e)
            pass
        
    
    async def play_music(self,url,voice_channel):
        try:
            vc = await voice_channel.connect()
        except discord.ClientException:
            return
        FFMPEG_OPTIONS = {'before_options':'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options':'-vn'}
        YDL_OPTIONS = {'format':'bestaudio'}
        try:
            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                info =  ydl.extract_info(url, download=False)
                url2 = info['formats'][0]['url']
                source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
                vc.play(source)
                # vc.source = discord.PCMVolumeTransformer(vc.source)
                # vc.source.volume = 0.01
                await asyncio.sleep(1)
                while (vc.is_playing() or self.isPause):
                    await asyncio.sleep(0.1)
                await asyncio.sleep(1)
        except Exception as e:
            print(e)
            pass
        finally:
            await vc.disconnect()
            if(self.playList.len()>0):
                await self.play()

    async def pause(self,client, voice_channel):
        try:
            clients = client.voice_clients
            vc = None
            for c in clients:
                if c.channel == voice_channel:
                    vc = c
                    break
            if vc == None:
                return
        except discord.ClientException:
            return
        self.isPause = True
        vc.pause()

    async def resume(self,client, voice_channel):
        try:
            clients = client.voice_clients
            vc = None
            for c in clients:
                if c.channel == voice_channel:
                    vc = c
                    break
            if vc == None:
                return
        except discord.ClientException:
            return
        self.isPause = False
        vc.resume()

    async def stop(self,client, voice_channel):
        try:
            clients = client.voice_clients
            vc = None
            for c in clients:
                if c.channel == voice_channel:
                    vc = c
                    break
            if vc == None:
                return
        except discord.ClientException:
            return
        vc.pause()
            
        
