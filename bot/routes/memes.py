# -*- coding: utf-8 -*-
#
#  SkachSSBot - Route: memes.
#  Created by Sergey Skachkov at 9/4/22
#
import os
import random
import logging
from io import BytesIO

from vkbottle.bot import BotLabeler, Message
from vkbottle import API, PhotoMessageUploader
from vkbottle.dispatch.rules.base import FuncRule
from vkbottle import Keyboard, KeyboardButtonColor, Text

from ..db import Database


bl = BotLabeler()
log = logging.getLogger('skachssbot')
api = API(os.environ.get('BOT_TOKEN', ''))
pmu = PhotoMessageUploader(api)
db = Database()


@bl.message(FuncRule(lambda msg: msg.text.lower() == 'мем'))
async def send_meme(msg: Message):
    await db._create_tables()
    meme_uids = await db.get_all_photo_uids()
    if meme_uids:
        meme_uid = 0
        wait_msg = await msg.answer('Подбираем мем...')
        while True:  # Я думаю это можно сделать лучше, к примеру правильным SQL запросом, но я не знаю его на столько хорошо...
            if len(meme_uids) == 0:
                break
            uid = random.choice(meme_uids)
            if not (await db.is_user_like_photo(uid, msg.peer_id)):
                meme_uid = uid
                break
            del(meme_uids[meme_uids.index(uid)])
            continue
        if meme_uid:
            meme = await db.get_photo(meme_uid)
            if meme:
                key = Keyboard(True)
                key.add(
                    Text('👍', {'set_meme_like': meme_uid}),
                    KeyboardButtonColor.POSITIVE)
                key.add(
                    Text('👎', {'set_meme_dislike': meme_uid}),
                    KeyboardButtonColor.NEGATIVE)
                if meme.get('uri', ''):
                    meme_uri = meme['uri']
                else:
                    meme_uri = (await pmu.upload(BytesIO(meme['photo'])))
                    await db.add_photo_uri(meme_uid, meme_uri)
                await api.request('messages.delete', {'message_ids': f'{wait_msg.message_id}', 'delete_for_all': 1})
                await msg.answer(
                    'Лови мем! 😃\n\nНе забудь поставить лайк/дизлайк!',
                    meme_uri, keyboard=key)
            else:
                # Я не знаю как ты попал в эту часть кода...
                log.error('Unexpected error! Can\'t found meme in DB, but found meme_uid in DB!')
                await api.request('messages.delete', {'message_ids': f'{wait_msg.message_id}', 'delete_for_all': 1})
                await msg.answer('⚠️ Странная ошибка!\n\nОтпиши создателю https://vk.com/0x403.')
        else:
            log.warning(f'Can\'t found meme for user #{msg.peer_id}!')
            await api.request('messages.delete', {'message_ids': f'{wait_msg.message_id}', 'delete_for_all': 1})
            await msg.answer('Прости, мемы на сегодня закончились 😞')
    else:
        log.warning('No memes in DB.')
        await msg.answer('Прости, мемы на сегодня закончились 😞')


@bl.message(payload_map=[('set_meme_like', int)])
async def set_meme_like(msg: Message):
    meme_uid = int(msg.get_payload_json()['set_meme_like'])
    meme = await db.get_photo(meme_uid)
    if meme:
        await db.add_photo_like(meme_uid)
        await db.add_user_action_for_photo(meme_uid, msg.peer_id, True)
        await msg.answer('Вы поставили лайк 👍!')
    else:
        log.error(f'Can\'t found meme #{meme_uid}!')
        await msg.answer('⚠️ Странная ошибка!\n\nОтпиши создателю https://vk.com/0x403.')


@bl.message(payload_map=[('set_meme_dislike', int)])
async def set_meme_dislike(msg: Message):
    meme_uid = int(msg.get_payload_json()['set_meme_dislike'])
    meme = await db.get_photo(meme_uid)
    if meme:
        await db.add_photo_dislike(meme_uid)
        await db.add_user_action_for_photo(meme_uid, msg.peer_id, False)
        await msg.answer('Вы поставили дизлайк 👎!')
    else:
        log.error(f'Can\'t found meme #{meme_uid}!')
        await msg.answer('⚠️ Странная ошибка!\n\nОтпиши создателю https://vk.com/0x403.')


@bl.message(FuncRule(lambda msg: msg.text.lower() == 'статистика'))
async def private_stat(msg: Message):
    stat = await db.get_private_stat(msg.peer_id)
    await msg.answer(f'Ты поставил {stat["likes"]} 👍 и {stat["dislikes"]} 👎')