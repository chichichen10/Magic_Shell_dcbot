import discord
import openai
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
    log = logging.getLogger('message_content_handler')
    ids = message.raw_mentions
    users = message.mentions
    content = message.content
    urls = re.findall('(?P<url>https?://[^\s]+)',content)
    br = Browser()
    br.set_handle_robots(False)
    url_titles = []
    if(urls):
        for url in urls:
            try:
                br.open(url)
                title = br.title()
                url_titles.append((url,title))
            except Exception as e:
                log.error(e)
    if(url_titles):
        for url_title in url_titles:
            message.content = message.content.replace(url_title[0],'網站標題：'+url_title[1])
    
    # print(ids)
    if (len(ids) == 0):
        return message.content
    else:
        content = message.content
        for id in ids:
            name = ''
            for user in users:
                if (user.id == id):
                    name = user.display_name

            content = content.replace('<@' + str(id) + '>', '@' + name)
        return content


async def message_handler(message: discord.Message, bot_user: discord.Member):
    log = logging.getLogger('message_handler')
    token_logger = logger('OPEN_AI_TOKEN')
    msg = message.content
    if (len(msg) > 200):
        await message.channel.send('太長了，請節約資源')
        return
    openai.api_key = os.environ['OPEN_AI_API_KEY']
    pre_messages = [{
        "role":
        "assistant" if m.author == bot_user else "user",
        "content":
        message_content_handler(m) if len(m.content) <= 100 else ""
    } async for m in message.channel.history(limit=15,
                                             after=message.created_at -
                                             datetime.timedelta(minutes=15),
                                             oldest_first=False)]
    pre_messages.reverse()
    #if only @XXX in message content
    if(not len([i for i in pre_messages[-1]['content'].split(' ') if '@' not in i])):
                pre_messages[-1]['content'] = '幫我叫 ' + pre_messages[-1]['content'] + ' 出來'
    if (len(pre_messages)==1):
        pre_prompt = [{"role":"user","content":"嗨阿致"},{"role":"assistant","content":"嗨，有什麼可以幫助你嗎？"}]
        if('@' in pre_messages[0]['content']):   
            pre_prompt = [{"role":"user","content":"幫我叫 @傑哥 出來"},{"role":"assistant","content":"@傑哥，有人叫你出來"},{"role":"user","content":"幫我叫 @威助 @平野 出來"},{"role":"assistant","content":"@威助 @平野，快出來!!!"}]
        pre_messages = pre_prompt + pre_messages
    log.info(str(pre_messages))
    additional_words = [
        '「哭啊」', '「我要吐了」', '「不是誒老哥」', '「有一說一」', '「傑哥你說對不對」', '「我只能說」',
        '「我真的會被氣死」', '「確實」'
    ]
    word_choices = choices(additional_words, k=choice(range(0, 3)))
    # word_message = '在回應中可以加入最多1個以下的口頭禪：' + '、'.
    setting_message = '以下對話都用繁體中文，長度不要超過50個字，你是阿致，是政治大學國貿系畢業的菁英，在玉山銀行當ARM，脾氣暴躁，口氣不佳，目前正忙著戀愛，現在的工作是在一個dicord頻道當管理員，有人發送訊息，你要回應他。' + (
        ('在回應中可以加入最多1個以下的口頭禪：' + '、'.join(word_choices) + '，')
        if word_choices else '') + '回答中可以加入一些髒話，直接講出阿致要講的話，不要任何冒號或引號，也不要以阿致開頭。句尾可以加入一些戀愛的emoji，盡量不要使用之前用過的emoji，偶爾可以在回答中加入一些戀愛的感覺。'

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
    for member in message.channel.members:
        if('@' + member.display_name in answer):
            answer = answer.replace('@'+ member.display_name,'<@'+str(member.id)+'>')
    await message.channel.send(answer)
    tokens = int(res.usage.total_tokens)
    token_logger.info("Tokens used: " + str(res.usage.total_tokens) + ' = $' +
                      f'{(tokens * 0.002 / 1000):.5f}')
    #db['token'] structure: (month, tokens)
    if (db['token'][0] == datetime.datetime.now().month):
        db['token'][1] += tokens
    else:
        db['token'] = [datetime.datetime.now().month, tokens]
