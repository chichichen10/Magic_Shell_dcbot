import asyncio

import discord
from discord import app_commands

from services import TeamService


async def _announce_and_move(channel, guild, blue, red) -> None:
    await channel.send("藍方: " + " ,".join(f"<@{player.id}> " for player in blue))
    await channel.send("紅方: " + " ,".join(f"<@{player.id}> " for player in red))
    countdown = await channel.send("倒數5秒")
    for index in range(5):
        await asyncio.sleep(1)
        await countdown.edit(content="倒數" + str(4 - index) + "秒")
    await asyncio.sleep(1)
    await countdown.edit(content="下去")

    blue_channel = await guild.create_voice_channel("藍隊")
    for player in blue:
        if player.voice:
            await player.move_to(blue_channel)
    red_channel = await guild.create_voice_channel("紅隊")
    for player in red:
        if player.voice:
            await player.move_to(red_channel)


async def handle_team_message(message, service: TeamService) -> bool:
    if "!阿致分隊" not in message.content:
        return False

    if message.content == "!阿致分隊 --n":
        blue, red = service.split_numbers()
        await message.channel.send("藍方: " + " ,".join(map(str, blue)))
        await message.channel.send("紅方: " + " ,".join(map(str, red)))
        return True

    if len(message.mentions) == service.REQUIRED_PLAYERS:
        blue, red = service.split(message.mentions)
        await _announce_and_move(message.channel, message.author.guild, blue, red)
        return True

    user = message.author
    if not user.voice:
        await message.channel.send("先進來講話 北七")
        return True

    players = list(user.voice.channel.members)
    if "--no" in message.content:
        players = [item for item in players if item not in message.mentions]

    if len(players) < service.REQUIRED_PLAYERS:
        await message.channel.send("人不夠 北七")
    elif len(players) > service.REQUIRED_PLAYERS:
        await message.channel.send("人山人海 北七")
    else:
        blue, red = service.split(players)
        await _announce_and_move(message.channel, user.guild, blue, red)
    return True


def register_team_commands(tree, service: TeamService) -> None:
    @tree.command(name="阿致分隊", description="內戰啦內戰")
    async def split_command(interaction: discord.Interaction):
        user = interaction.user
        if not user.voice:
            await interaction.response.send_message("先進語音啦", ephemeral=True)
            return

        players = list(user.voice.channel.members)
        if len(players) < service.REQUIRED_PLAYERS:
            await interaction.response.send_message("人不夠 北七", ephemeral=True)
            return
        if len(players) > service.REQUIRED_PLAYERS:
            await interaction.response.send_message("人山人海 北七", ephemeral=True)
            return

        await interaction.response.defer()
        blue, red = service.split(players)
        await _announce_and_move(interaction.channel, interaction.user.guild, blue, red)

    @tree.command(name="阿致抽籤", description="抽起來~")
    @app_commands.describe(options="選項 (用空格隔開)")
    async def draw_command(interaction: discord.Interaction, options: str):
        option_list = options.split()
        if not option_list:
            await interaction.response.send_message("沒有選項", ephemeral=True)
            return
        import random

        await interaction.response.send_message("就決定是" + random.choice(option_list))
