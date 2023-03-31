import discord
import openai
import os
from asgiref.sync import sync_to_async
import datetime
from random import choice, choices
from replit import db
import logging
from logger import logger


async def message_handler(message: discord.Message, bot_user: discord.Member):
    log = logging.getLogger('message_handler')
    token_logger = logger('OPEN_AI_TOKEN')
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
                                             datetime.timedelta(minutes=15),
                                             oldest_first=False)]
    pre_messages.reverse()
    # aa.info(str(pre_messages))
    # bb.info(str(pre_messages))
    log.info(str(pre_messages))
    additional_words = [
        '「哭啊」', '「我要吐了」', '「不是誒老哥」', '「有一說一」', '「傑哥你說對不對」', '「我只能說」',
        '「我真的會被氣死」', '「確實」'
    ]
    word_choices = choices(additional_words, k=choice(range(0, 3)))
    # word_message = '在回應中可以加入最多1個以下的口頭禪：' + '、'.
    setting_message = '以下對話都用繁體中文，長度不要超過50個字，你是阿致，工作是在玉山銀行當ARM，脾氣暴躁，口氣不佳，現在在一個dicord群駔當管理員，有人發送訊息，你要回應他。' + (
        ('在回應中可以加入最多1個以下的口頭禪：' + '、'.join(word_choices) + '，')
        if word_choices else '') + '回答中可以加入一些髒話，直接講出阿致要講的話，不要任何冒號或引號，也不要以阿致開頭。'

    system_message = [{"role": "system", "content": setting_message}]
    res = await sync_to_async(openai.ChatCompletion.create
                              )(model="gpt-3.5-turbo",
                                messages=system_message + pre_messages,
                                temperature=1.1,
                                max_tokens=300,
                                presence_penalty=1,
                                frequency_penalty=1)
    answer = res.choices[0]['message']['content']
    log.info(str(system_message))
    await message.channel.send(answer)
    tokens = int(res.usage.total_tokens)
    token_logger.info("Tokens used: " + str(res.usage.total_tokens) + ' = $' +
                      f'{(tokens * 0.002 / 1000):.5f}')
    #db['token'] structure: (month, tokens)
    if(db['token'][0]==datetime.datetime.now().month):
        db['token'][1] += tokens
    else:
        db['token'] = [datetime.datetime.now().month, tokens]