import discord
import openai
import os
from asgiref.sync import sync_to_async
import datetime
from logger import logger as log


async def messageHandler(message: discord.Message, bot_user: discord.Member):
    msg = message.content
    if (len(msg) > 100):
        await message.channel.send('太長了，請節約資源')
        return
    openai.api_key = os.environ['OPEN_AI_API_KEY']
    pre_messages = [{
        "role": "assistant" if m.author == bot_user else "user",
        "content": m.content if len(m.content) <= 100 else ""
    } async for m in message.channel.history(limit=15,
                                             after=message.created_at -
                                             datetime.timedelta(minutes=5),
                                             oldest_first=False)]
    pre_messages.reverse()
    print(pre_messages)
    system_message = [{
        "role":
        "system",
        "content":
        "以下對話都用繁體中文，長度不要超過50個字，你是阿致，現在在玉山銀行當ARM，脾氣暴躁，口氣不佳，現在在一個dicord群駔，有人發送訊息，你要回應他。在回應中可以加入最多1個以下的口頭禪：「哭啊」、「我要吐了」、「不是誒老哥」、「有一說一」、「傑哥你說對不對」，一次回答中不要加入超過一個口頭禪，回答中可以加入一些髒話，直接講出你要講的話，不要任何冒號或引號。"
    }]
    res = await sync_to_async(openai.ChatCompletion.create
                              )(model="gpt-3.5-turbo",
                                messages=system_message + pre_messages,
                                temperature=1.1,
                                max_tokens=300,
                                presence_penalty=1,
                                frequency_penalty=1)
    answer = res.choices[0]['message']['content']
    await message.channel.send(answer)
    log.info("Tokens used: " + str(res.usage.total_tokens))
