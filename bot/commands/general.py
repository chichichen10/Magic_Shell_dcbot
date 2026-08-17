import asyncio
import random

import discord

from config import Settings
from state import BotState


HELP_MESSAGE = """

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
"""


async def _play_short_clip(message, filename: str) -> None:
    user = message.author
    if not user.voice:
        await message.channel.send("先進來講話 北七")
        return
    voice_channel = user.voice.channel
    try:
        voice_client = await voice_channel.connect()
        await asyncio.sleep(0.5)
        voice_client.play(discord.FFmpegPCMAudio(filename), after=None)
        voice_client.source.volume = 10.0
        await asyncio.sleep(2)
        await voice_client.disconnect()
    except Exception:
        print("erroR")


async def handle_general_message(
    message,
    client,
    tree,
    settings: Settings,
) -> bool:
    content = message.content
    if content == "!阿致講話":
        await _play_short_clip(
            message, "voice_" + str(random.choice(range(1, 17))) + ".mp3"
        )
    elif content == "!垃圾遊戲":
        await _play_short_clip(message, "voice_2.mp3")
    elif content == "!阿致挖礦":
        await message.channel.send(
            "邁向財富自由\nhttps://max.maicoin.com/signup?r=1448ee5b"
        )
    elif content == ".sync" and message.author.display_name == settings.admin_name:
        tree.clear_commands(guild=message.guild)
        await tree.sync()
        await message.channel.send("done")
    elif content == "!阿致新功能":
        await message.channel.send(
            "\n!阿致叫我[你想要的名字]: 阿致可能會這樣叫你 e.g.!阿致叫我智障)\n"
        )
    elif content == "!阿致能幹嘛":
        await message.channel.send(HELP_MESSAGE)
    else:
        return False
    return True


def register_general_commands(tree, state: BotState) -> None:
    @tree.command(name="測試", description="拉基")
    async def test_command(interaction: discord.Interaction, name: discord.Member):
        await interaction.response.send_message("Test " + name.name)
        await interaction.channel.send("Second " + interaction.user.name)

    @tree.command(name="阿致嘴閉閉", description="叫阿致閉嘴")
    async def silent_command(interaction: discord.Interaction):
        if state.verbose:
            await interaction.response.send_message("好啊都這樣")
            state.verbose = False
        else:
            await interaction.response.send_message("到底想怎樣")

    @tree.command(name="阿致回來", description="回到阿致的懷抱")
    async def back_command(interaction: discord.Interaction):
        if not state.verbose:
            await interaction.response.send_message("想不到吧")
            state.verbose = True
        else:
            await interaction.response.send_message("回你媽")

    @tree.command(name="拉進垃圾車", description="拉~進~垃~圾~車~~~")
    async def trash_command(interaction: discord.Interaction, user: discord.Member):
        channel = await interaction.user.guild.create_voice_channel("垃圾車")
        if user.voice:
            await user.move_to(channel)
            await interaction.response.send_message(f"<@{user.id}> 下去")
        else:
            await interaction.response.send_message("他不在語音頻道", ephemeral=True)
