import asyncio
import datetime
import logging
import re
from random import choice, choices

import discord
from mechanize import Browser
from openai import OpenAI

from logger import logger
from repositories import BotRepository


URL_PATTERN = re.compile(r"(?P<url>https?://[^\s]+)")


def message_content(message: discord.Message):
    content = message.content
    image_content = None

    if message.attachments:
        attachment = message.attachments[0]
        if attachment.content_type and attachment.content_type.startswith("image"):
            image_content = {
                "type": "image_url",
                "image_url": {"url": attachment.url},
            }

    urls = URL_PATTERN.findall(content)
    if urls:
        browser = Browser()
        browser.set_handle_robots(False)
        for url in urls:
            try:
                browser.open(url)
                content = content.replace(url, "網站標題：" + browser.title())
            except Exception as error:
                logging.getLogger("message_content").error(error)

    if image_content:
        return [
            {"type": "text", "text": content or "看這張圖片"},
            image_content,
        ]

    for mentioned_id in message.raw_mentions:
        user = next(
            (item for item in message.mentions if item.id == mentioned_id),
            None,
        )
        if user is not None:
            content = content.replace(f"<@{mentioned_id}>", f"@{user.display_name}")
    return content


class AIMessageService:
    def __init__(
        self,
        api_key: str,
        model: str,
        repository: BotRepository,
    ):
        self._client = OpenAI(api_key=api_key)
        self._model = model
        self._repository = repository
        self._log = logging.getLogger("message_handler")
        self._token_log = logger("OPEN_AI_TOKEN")

    async def _history(self, message, bot_user):
        messages = [
            {
                "role": "assistant" if item.author == bot_user else "user",
                "content": message_content(item) if len(item.content) <= 5000 else "",
            }
            async for item in message.channel.history(
                limit=15,
                after=message.created_at - datetime.timedelta(minutes=150),
                oldest_first=False,
            )
        ]
        messages.reverse()
        return messages

    @staticmethod
    def _system_prompt(word_choices) -> str:
        optional_words = ""
        if word_choices:
            optional_words = (
                "在回應中可以加入最多1個以下的口頭禪：" + "、".join(word_choices) + "，"
            )
        return (
            "以下對話都用繁體中文，長度不要超過50個字，你是阿致，是政治大學國貿系畢業的菁英，"
            "在玉山銀行當ARM，脾氣暴躁，口氣不佳，目前的目標是成為玉山銀行裡的菁英，"
            "成為年輕有為的銀行家，現在在這個dicord頻道當管理員，有人發送訊息，你要回應他。"
            + optional_words
            + "口頭禪要合理使用，要通順。回答中可以比較粗俗，直接講出阿致要講的話，"
            "不要任何冒號或引號，也不要以阿致開頭。"
        )

    async def respond(self, message: discord.Message, bot_user) -> None:
        if len(message.content) > 4000:
            await message.channel.send("太長了，請節約資源")
            return

        pre_messages = await self._history(message, bot_user)
        if pre_messages and isinstance(pre_messages[-1]["content"], str):
            words_without_mentions = [
                item
                for item in pre_messages[-1]["content"].split(" ")
                if "@" not in item
            ]
            if not words_without_mentions:
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
        selected_words = choices(additional_words, k=choice(range(0, 3)))
        messages = [
            {"role": "system", "content": self._system_prompt(selected_words)}
        ] + pre_messages
        self._log.info(str(pre_messages))

        response = await asyncio.to_thread(
            self._client.chat.completions.create,
            model=self._model,
            messages=messages,
        )
        answer = response.choices[0].message.content
        for member in message.channel.members:
            answer = answer.replace("@" + member.display_name, f"<@{member.id}>")
        await message.channel.send(answer)
        self._record_usage(int(response.usage.total_tokens))

    async def welcome(self, member, channel) -> None:
        prompt = (
            "以下對話都用繁體中文，長度大約300個字，你是阿致，是政治大學國貿系畢業的菁英，"
            "在玉山銀行當ARM，脾氣暴躁，口氣不佳，現在在一個dicord頻道當管理員，"
            f"現在要歡迎 {member.name} 加入這個頻道，並告訴他這裡雖然有很多奇怪的人，"
            "也有可能會吵架，但仍希望他玩得開心。有問題可以找你，雖然你不保證可以解決，"
            "直接講出阿致要講的話，不要任何冒號或引號，也不要以阿致開頭。"
        )
        response = await asyncio.to_thread(
            self._client.chat.completions.create,
            model=self._model,
            messages=[{"role": "system", "content": prompt}],
        )
        answer = response.choices[0].message.content.replace(
            member.name, f"<@{member.id}>"
        )
        await channel.send(answer)
        self._record_usage(int(response.usage.total_tokens))

    def _record_usage(self, tokens: int) -> None:
        self._token_log.info(f"Tokens used: {tokens} = ${(tokens * 0.02 / 1000):.5f}")
        self._repository.add_token_usage(tokens)
