# from keep_alive import keep_alive
import discord
import random
import os
import asyncio
from replit import db
from gtts import gTTS
from pydub import AudioSegment, effects
from logger import logger as log
from audio_player import DC_player
import youtube_dl
from youtube_search import YoutubeSearch

client = discord.Client()

dc_player = DC_player()

verbose = True


@client.event
async def on_ready():
    log.info('目前登入身份：' + str(client.user))


@client.event
async def on_voice_state_update(member, before, after):
    if (db["mode"] == "0"):
        return
    user = member
    if (user == client.user):
        return
    if (user.display_name == "傑哥KTV"):
        return
    voice_channel = None
    if (user.voice):
        voice_channel = user.voice.channel
    guild = user.guild
    for vc in guild.voice_channels:
        if vc.name == '紅隊' or vc.name == '藍隊' or vc.name == '垃圾車':
            if (not vc.members):
                await vc.delete()

    if (voice_channel != None and before.channel != after.channel):
        # player_ids = [x.id for x in voice_channel.members]
        # if (user.id == 429657581313720321):
        #     try:
        #         log.info('Magic Shell back.')
        #         vc = await voice_channel.connect()
        #         await asyncio.sleep(0.2)
        #         audio_source = discord.FFmpegPCMAudio('recording.webm')
        #         vc.play(audio_source, after=None)
        #         vc.source.volume = 10.0
        #         while (vc.is_playing()):
        #             await asyncio.sleep(0.5)
        #         await asyncio.sleep(1)
        #         await vc.disconnect()
        #     except Exception as e:
        #         log.err(e)
        #     return
        # elif (429657581313720321 in player_ids):
        #     return
        if (random.choice(range(1, 10)) == 1
                and user.voice.channel.name != '垃圾車'):
            guild = user.guild
            channel = await guild.create_voice_channel('垃圾車')
            await user.move_to(channel)
            return
        if (user.voice.channel.name == '垃圾車'):
            dc_player.add('trash2.mp3',user.voice.channel)
            await dc_player.play()
            return

        try:
            name = user.display_name
            log.info(name + ' in ' + user.guild.name + '[' +
                     user.voice.channel.name + ']')
            if (name == '楓夜' and random.choice(range(1, 3)) == 1):
                name = '他媽的孫偉夫'
            if (random.choice(range(1, 3)) == 1
                    and db.prefix("random_" + name)):
                names = db.prefix("random_" + name)
                name = db[random.choice(names)]
            elif ("nickname_" + name in db.prefix("nickname_")):
                name = db["nickname_" + name]
            name_voice_file = "name/" + name + ".mp3"
            welcome_num = str(random.choice(range(1, 3)))
            welcome_voice = "welcome" + welcome_num + "/" + name + ".mp3"
            if (not os.path.isfile(welcome_voice)):
                if (not os.path.isfile(name_voice_file)):
                    tts = gTTS(text=name, lang='zh-tw')
                    tts.save(name_voice_file)
                pre_welcome = AudioSegment.from_mp3('prewelcome' +
                                                    welcome_num + '.mp3')
                name_voice_origin = AudioSegment.from_mp3(name_voice_file)
                name_voice = effects.speedup(name_voice_origin, 1.3)
                if (welcome_num == '2'):
                    post_welcome = AudioSegment.from_mp3('postwelcome' +
                                                         welcome_num + '.mp3')
                    welcome = pre_welcome + name_voice + post_welcome
                else:
                    welcome = pre_welcome + name_voice
                welcome.export(welcome_voice, format="mp3")
            print(welcome_voice)
            dc_player.add(welcome_voice, voice_channel)
            file_name = 'voice_' + str(random.choice(range(1, 17))) + '.mp3'
            print(file_name)
            dc_player.add(file_name, voice_channel)
            await dc_player.play()
        except Exception as e:
            print(e)
    elif (user.id == 429657581313720321 and after.channel == None):
        dc_player.add('recording2.webm',before.channel)
        return
    elif (after.channel == None):
        try:
            name = user.display_name
            log.info(name + ' out ' + user.guild.name + '[' +
                     before.channel.name + ']')
            if (name == 'Chi'):
                name = 'Chee'
            if (name == '楓夜' and random.choice(range(1, 3)) == 1):
                name = '他媽的孫偉夫'
            name_voice_file = "name/" + name + ".mp3"
            bye_voice = "bye/" + name + ".mp3"
            if (not os.path.isfile(bye_voice)):
                if (not os.path.isfile(name_voice_file)):
                    tts = gTTS(text=name, lang='zh-tw')
                    tts.save(name_voice_file)
                pre_bye = AudioSegment.from_mp3('bye.mp3')
                name_voice_origin = AudioSegment.from_mp3(name_voice_file)
                name_voice = effects.speedup(name_voice_origin, 1.3)
                bye = name_voice + pre_bye
                bye.export(bye_voice, format="mp3")

            dc_player.add(bye_voice,before.channel)
            await dc_player.play()
        except Exception as e:
            print(e)
            print('that')

    return


@client.event
async def on_message(message):
    global verbose
    mentions = message.mentions
    if message.author == client.user:
        return
    if (message.author.display_name == "傑哥KTV"):
        return

    if message.content == '!阿致當兵':
        await message.channel.send('信仰堅定 紀律嚴明')
        verbose = False
        db["mode"] = "0"
        return

    if message.content == '!阿致放假':
        await message.channel.send('放假啦老哥')
        verbose = True
        db["mode"] = "1"
        user = message.author
        voice_channel = None
        if (user.voice):
            voice_channel = user.voice.channel
        if (voice_channel != None):
            try:
                vc = await voice_channel.connect()
                await asyncio.sleep(0.2)
                audio_source = discord.FFmpegPCMAudio('voice_15.mp3')
                vc.play(audio_source, after=None)
                vc.source.volume = 10.0
                await asyncio.sleep(2)
                await vc.disconnect()
            except:
                print('erroR')
        return

    if message.content == '!阿致嘴閉閉':
        if verbose:
            await message.channel.send('好啊都這樣')
            verbose = False
        else:
            await message.channel.send('到底想怎樣')
        return

    if message.content == '!阿致回來':
        if not verbose:
            await message.channel.send('想不到吧')
            verbose = True
            user = message.author
            voice_channel = None
            if (user.voice):
                voice_channel = user.voice.channel
            if (voice_channel != None):
                try:
                    vc = await voice_channel.connect()
                    await asyncio.sleep(0.2)
                    audio_source = discord.FFmpegPCMAudio('voice_15.mp3')
                    vc.play(audio_source, after=None)
                    vc.source.volume = 10.0
                    await asyncio.sleep(2)
                    await vc.disconnect()
                except:
                    print('erroR')

        else:
            await message.channel.send('回你媽')
        return

    if "!阿致叫我" in message.content:
        random_name = message.content[5:]
        db["random_" + message.author.display_name + "_" +
           str(hash(random_name))] = random_name
        await message.channel.send(random.choice(["考慮", "喔", "我想想", "不要"]))
        return

    if message.content.startswith('!把') and message.content.endswith('拉進垃圾車'):
        guild = message.author.guild
        channel = await guild.create_voice_channel('垃圾車')
        for player in mentions:
            if player.voice:
                await player.move_to(channel)
                await message.channel.send('<@' + str(player.id) + '> 下去')

        return

    if message.content == '!阿致講話':
        user = message.author
        if not user.voice:
            await message.channel.send('先進來講話 北七')
            return
        voice_channel = user.voice.channel
        if voice_channel != None:
            try:
                vc = await voice_channel.connect()
                await asyncio.sleep(0.5)
                audio_source = discord.FFmpegPCMAudio(
                    'voice_' + str(random.choice(range(1, 17))) + '.mp3')
                vc.play(audio_source, after=None)
                vc.source.volume = 10.0
                # while not player.is_done():
                #     await asyncio.sleep(1)
                # player.stop()
                await asyncio.sleep(2)
                await vc.disconnect()
            except:
                print('erroR')
        return

    if message.content == '!垃圾遊戲':
        user = message.author
        voice_channel = user.voice.channel
        if voice_channel != None:
            try:
                vc = await voice_channel.connect()
                await asyncio.sleep(0.5)
                audio_source = discord.FFmpegPCMAudio('voice_2.mp3')
                vc.play(audio_source, after=None)
                vc.source.volume = 10.0
                # while not player.is_done():
                #     await asyncio.sleep(1)
                # player.stop()
                await asyncio.sleep(2)
                await vc.disconnect()
            except:
                print('erroR')
        return

    # if message.content == '!阿致重整':
    #     guild = message.author.guild
    #     channel = await guild.create_voice_channel('廁所')

    #     for player in mentions:
    #         if player.voice:
    #             await player.move_to(channel)
    #             await message.channel.send('<@' + str(player.id) + '> 下去')

    #     return

    if '!阿致分隊' in message.content:
        if message.content == '!阿致分隊 --n':
            l = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            random.shuffle(l)
            blue = []
            red = []
            for i in range(10):
                if (i < 5):
                    blue.append(l[i])
                else:
                    red.append(l[i])
            await message.channel.send('藍方: ' +
                                       ' ,'.join(str(x) for x in sorted(blue)))
            await message.channel.send('紅方: ' +
                                       ' ,'.join(str(x) for x in sorted(red)))
        elif len(mentions) == 10:
            guild = message.author.guild
            random.shuffle(mentions)
            await message.channel.send('藍方: ' +
                                       ' ,'.join('<@' + str(x.id) + '> '
                                                 for x in mentions[:5]))
            await message.channel.send('紅方: ' +
                                       ' ,'.join('<@' + str(x.id) + '> '
                                                 for x in mentions[5:]))
            new_msg = await message.channel.send('倒數5秒')
            for i in range(5):
                await asyncio.sleep(1)
                await new_msg.edit(content='倒數' + str(4 - i) + '秒')
            await asyncio.sleep(1)
            await new_msg.edit(content='下去')
            blue_channel = await guild.create_voice_channel('藍隊')
            for player in mentions[:5]:
                if player.voice:
                    await player.move_to(blue_channel)
            red_channel = await guild.create_voice_channel('紅隊')
            for player in mentions[5:]:
                if player.voice:
                    await player.move_to(red_channel)

        else:
            user = message.author
            if not user.voice:
                await message.channel.send('先進來講話 北七')
                return
            voice_channel = user.voice.channel
            guild = user.guild
            print(voice_channel.members)
            players = voice_channel.members
            if '--no' in message.content:
                for m in mentions:
                    if m in players:
                        players.remove(m)
            print(len(players))
            if len(players) == 10:
                random.shuffle(players)
                await message.channel.send('藍方: ' +
                                           ' ,'.join('<@' + str(x.id) + '> '
                                                     for x in players[:5]))
                await message.channel.send('紅方: ' +
                                           ' ,'.join('<@' + str(x.id) + '> '
                                                     for x in players[5:]))
                new_msg = await message.channel.send('倒數5秒')
                for i in range(5):
                    await asyncio.sleep(1)
                    await new_msg.edit(content='倒數' + str(4 - i) + '秒')
                await asyncio.sleep(1)
                await new_msg.edit(content='下去')
                blue_channel = await guild.create_voice_channel('藍隊')
                for player in players[:5]:
                    if player.voice:
                        await player.move_to(blue_channel)
                red_channel = await guild.create_voice_channel('紅隊')
                for player in players[5:]:
                    if player.voice:
                        await player.move_to(red_channel)
            elif len(players) < 10:
                await message.channel.send('人不夠 北七')
            elif len(players) > 10:
                await message.channel.send('人山人海 北七')
        return

    if message.content == '!阿致挖礦':
        await message.channel.send(
            '邁向財富自由\nhttps://max.maicoin.com/signup?r=1448ee5b')
        return

    # if message.content.startswith('!阿致唱'):
    #     keyword = message.content.split()[1]
    #     results = YoutubeSearch(keyword, max_results=1).to_dict()
    #     url_suffix = results[0]['url_suffix']
    #     await dc_player.play_music('https://www.youtube.com'+url_suffix, message.author.voice.channel)

    # if message.content == '!阿致暫停':
    #     await dc_player.pause(client,message.author.voice.channel)    

    # if message.content == '!阿致繼續':
    #     await dc_player.resume(client,message.author.voice.channel)

    # if message.content == '!阿致停':
    #     await dc_player.stop(client,message.author.voice.channel)
        
    if message.content == '!阿致新功能':
        msg = '''

        !阿致叫我[你想要的名字]: 阿致可能會這樣叫你 e.g.!阿致叫我智障)
        '''
        await message.channel.send(msg)
        return

    if message.content == '!阿致能幹嘛':
        help_msg = '''

        !阿致嘴閉閉: 讓阿致少講點話
!阿致回來: 本來的阿致
!阿致當兵: 停止阿致的語音問候
!阿致放假: 開始問候你全家
!阿致講話: 美妙的發言
!垃圾遊戲: G社不倒遊戲不會好
!阿致叫我[你想要的名字]: 阿致可能會這樣叫你 e.g.!阿致叫我智障)
!阿致挖礦: 恭喜你發現財富密碼
!阿致分隊 [[@user1] [@user2] [...] [@user10] | --no [@user1] [@user2] [...]]:
                    沒有參數:語音裡面剛好10個人分兩隊
                    @10個人: 10個人分兩隊
                    --no @不打的人: 在語音裡面要打的10個人分兩隊

讓阿致更好 歡迎捐款 
BTC : 34H1toJmtK3G2XYoJcX19eUy4LKuC8A2Bh
ETH : 0x257cB5aB793761e6eCF2CFF97BfBD99C0f5feEd3
DOGE: D6kYuic82rrX64Z9VopibgkSmCUdWf54qr
USDT: 0x257cB5aB793761e6eCF2CFF97BfBD99C0f5feEd3(ERC20)            
USDT: TVuWm5qjjSc79Zz1vFkeLvhsHzR3NrFm24(TRC20)

歡迎協作
https://github.com/chichichen10/Magic_Shell_dcbot

        '''
        await message.channel.send(help_msg)
        return

    a_msg = [
        '哭啊', '不是誒老哥', '誒你剛有看到嗎 我剛很強吧', '外掛啦外掛', '這對面很有水準誒', '我要吐了', '那是肯定的'
    ]

    if random.choice([1, 2, 3]) == 1 and verbose:
        await message.channel.send(random.choice(a_msg))


client.run(os.environ['BOT_TOKEN'])
