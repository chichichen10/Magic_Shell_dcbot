import discord
from openai import OpenAI
import os
from asgiref.sync import sync_to_async
import datetime
from random import choice, choices
from replit import db
import logging
from logger import logger
import re
from mechanize import Browser


def message_content_handler(message: discord.Message):
    log = logging.getLogger("message_content_handler")
    ids = message.raw_mentions
    users = message.mentions
    content = message.content
    attachments = message.attachments
    hasImage = False
    image_content = {}
    if len(attachments) > 0:
        attachment = attachments[0]
        if attachment.content_type.startswith("image"):
            hasImage = True
            img_url = attachment.url
            image_content["type"] = "image_url"
            image_content["image_url"] = {}
            image_content["image_url"]["url"] = img_url

    urls = re.findall("(?P<url>https?://[^\s]+)", content)
    br = Browser()
    br.set_handle_robots(False)
    url_titles = []
    if urls:
        for url in urls:
            try:
                br.open(url)
                title = br.title()
                url_titles.append((url, title))
            except Exception as e:
                log.error(e)
    if url_titles:
        for url_title in url_titles:
            message.content = message.content.replace(
                url_title[0], "網站標題：" + url_title[1]
            )

    if hasImage:
        if len(content) < 1:
            content = "看這張圖片"
        return [{"type": "text", "text": content}, image_content]

    # print(ids)
    if len(ids) == 0:
        return message.content
    else:
        content = message.content
        for id in ids:
            name = ""
            for user in users:
                if user.id == id:
                    name = user.display_name

            content = content.replace("<@" + str(id) + ">", "@" + name)
        return content


async def message_handler(
    message: discord.Message,
    bot_user: discord.Member,
    is_welcome=False,
    new_member=None,
    channel=None,
):
    client = OpenAI(api_key=os.environ["OPEN_AI_API_KEY"])
    log = logging.getLogger("message_handler")
    token_logger = logger("OPEN_AI_TOKEN")
    if is_welcome:
        setting_message = f"以下對話都用繁體中文，長度大約300個字，你是阿致，是政治大學國貿系畢業的菁英，在玉山銀行當ARM，脾氣暴躁，口氣不佳，現在在一個dicord頻道當管理員，現在要歡迎 {new_member.name} 加入這個頻道，並告訴他這裡雖然有很多奇怪的人，也有可能會吵架，但仍希望他玩得開心。有問題可以找你，雖然你不保證可以解決，直接講出阿致要講的話，不要任何冒號或引號，也不要以阿致開頭。"
        pre_messages = []
    else:
        msg = message.content
        if len(msg) > 4000:
            await message.channel.send("太長了，請節約資源")
            return

        pre_messages = [
            {
                "role": "assistant" if m.author == bot_user else "user",
                "content": message_content_handler(m) if len(m.content) <= 5000 else "",
            }
            async for m in message.channel.history(
                limit=15,
                after=message.created_at - datetime.timedelta(minutes=150),
                oldest_first=False,
            )
        ]
        pre_messages.reverse()
        # if only @XXX in message content
        if isinstance(pre_messages[-1]["content"], str):
            if not len(
                [i for i in pre_messages[-1]["content"].split(" ") if "@" not in i]
            ):
                pre_messages[-1]["content"] = (
                    "幫我叫 " + pre_messages[-1]["content"] + " 出來"
                )
        if len(pre_messages) == 1:
            pre_prompt = [
                {"role": "user", "content": "嗨阿致"},
                {"role": "assistant", "content": "嗨，有什麼可以幫助你嗎？"},
            ]
            if "@" in pre_messages[0]["content"]:
                pre_prompt = [
                    {"role": "user", "content": "幫我叫 @傑哥 出來"},
                    {"role": "assistant", "content": "@傑哥，有人叫你出來"},
                    {"role": "user", "content": "幫我叫 @威助 @平野 出來"},
                    {"role": "assistant", "content": "@威助 @平野，快出來!!!"},
                ]
            pre_messages = pre_prompt + pre_messages
        log.info(str(pre_messages))
        additional_words = [
            "「哭啊」",
            "「我要吐了」",
            "「不是誒老哥」",
            "「有一說一」",
            "「傑哥你說對不對」",
            "「我只能說」",
            "「我真的會被氣死」",
            "「確實」",
        ]
        word_choices = choices(additional_words, k=choice(range(0, 3)))
        # word_message = '在回應中可以加入最多1個以下的口頭禪：' + '、'.
        setting_message = (
            "以下對話都用繁體中文，長度不要超過50個字，你是阿致，是政治大學國貿系畢業的菁英，在玉山銀行當ARM，脾氣暴躁，口氣不佳，目前的目標是成為玉山銀行裡的菁英，成為年輕有為的銀行家，現在在這個dicord頻道當管理員，有人發送訊息，你要回應他。"
            + (
                (
                    "在回應中可以加入最多1個以下的口頭禪："
                    + "、".join(word_choices)
                    + "，"
                )
                if word_choices
                else ""
            )
            + "口頭禪要合理使用，要通順。回答中可以比較粗俗，直接講出阿致要講的話，不要任何冒號或引號，也不要以阿致開頭。"
        )

    system_message = [{"role": "system", "content": setting_message}]
    res = await sync_to_async(client.chat.completions.create)(
        model="gpt-5.6-luna", messages=system_message + pre_messages
    )
    answer = res.choices[0].message.content
    log.info(str(system_message))
    if is_welcome:
        answer = answer.replace(new_member.name, f"<@{new_member.id}>")
        await channel.send(answer)
    else:
        for member in message.channel.members:
            if "@" + member.display_name in answer:
                answer = answer.replace(
                    "@" + member.display_name, "<@" + str(member.id) + ">"
                )
        await message.channel.send(answer)
    tokens = int(res.usage.total_tokens)
    token_logger.info(
        "Tokens used: "
        + str(res.usage.total_tokens)
        + " = $"
        + f"{(tokens * 0.02 / 1000):.5f}"
    )
    # db['token'] structure: (month, tokens)
    if db["token"][0] == datetime.datetime.now().month:
        db["token"][1] += tokens
    else:
        db["token"] = [datetime.datetime.now().month, tokens]
