# -*- coding: utf-8 -*-
#
#  SkachSSBot - Route: memes.
#  Created by Sergey Skachkov at 9/4/22
#
import os
import sys
import random
import logging
from io import BytesIO

from vkbottle.bot import BotLabeler, Message
from vkbottle import API, PhotoMessageUploader
from vkbottle.dispatch.rules.base import FuncRule, AttachmentTypeRule
from vkbottle import Keyboard, KeyboardButtonColor, Text

from ..db import Database


bl = BotLabeler()
log = logging.getLogger('skachssbot')
api = API(os.environ.get('BOT_TOKEN', ''))
pmu = PhotoMessageUploader(api)
db = Database()


def get_start_key() -> str:
    '''Возвращает стартовую клавиатуру.

    Returns:
        str: json vk bot keyboard in string.
    '''
    key = Keyboard(True)
    key.add(Text('Мемы'), KeyboardButtonColor.POSITIVE)
    key.row()
    key.add(Text('Вопросы'), KeyboardButtonColor.PRIMARY)
    key.row()
    key.add(Text('Статистика'), KeyboardButtonColor.SECONDARY)
    return key.get_json()


@bl.message(FuncRule(lambda msg: 'мем' in msg.text.lower()))
async def send_meme(msg: Message):
    await db._create_tables()
    meme_uids = await db.get_unviewed_memes_for_user(msg.peer_id)
    if meme_uids:
        meme = random.choice(meme_uids)
        key = Keyboard(True)
        key.add(
            Text('👍', {'set_meme_like': meme['uid']}),
            KeyboardButtonColor.POSITIVE)
        key.add(
            Text('👎', {'set_meme_dislike': meme['uid']}),
            KeyboardButtonColor.NEGATIVE)
        if meme.get('uri', ''):
            meme_uri = meme['uri']
        else:
            meme_uri = (await pmu.upload(BytesIO(meme['photo'])))
            await db.add_photo_uri(meme['uid'], meme_uri)
        await msg.answer(
            'Лови мем! 😃\n\nНе забудь поставить лайк/дизлайк!',
            meme_uri, keyboard=key)
    else:
        log.warning(f'Can\'t found meme for user #{msg.peer_id}')
        await msg.answer('Прости, мемы на сегодня закончились 😞', keyboard=get_start_key())


@bl.message(payload_map=[('set_meme_like', int)])
async def set_meme_like(msg: Message):
    meme_uid = int(msg.get_payload_json()['set_meme_like'])
    meme = await db.get_photo(meme_uid)
    if meme:
        await db.add_photo_like(meme_uid)
        await db.add_user_action_for_photo(meme_uid, msg.peer_id, True)
        await msg.answer('Вы поставили лайк 👍!', keyboard=get_start_key())
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
        await msg.answer('Вы поставили дизлайк 👎!', keyboard=get_start_key())
    else:
        log.error(f'Can\'t found meme #{meme_uid}!')
        await msg.answer('⚠️ Странная ошибка!\n\nОтпиши создателю https://vk.com/0x403.')


@bl.message(FuncRule(lambda msg: msg.text.lower() == 'статистика'))
async def stat(msg: Message):
    wait_msg = await msg.answer('Загружаем статистику...')
    privstat = await db.get_private_stat(msg.peer_id)
    pubstat = await db.get_public_stat()
    top_9 = await db.get_top_9_memes()
    cnt1 = f'Пользователями было всего поставлено {pubstat["likes"]} 👍 и {pubstat["dislikes"]} 👎\n'
    cnt1 += f'Ты поставил {privstat["likes"]} 👍 и {privstat["dislikes"]} 👎'
    for meme in top_9:
        if not meme.get('uri'):
            top_9[top_9.index(meme)]['uri'] = await pmu.upload(meme['photo'])
    try:
        await api.request('messages.delete', {'message_ids': wait_msg.message_id, 'delete_for_all': 1})
    except Exception:
        # Иногда, по какой-то причине, выпадает ошибка о том что смс не найдено.
        log.exception(f'Can\'t found message_id #{wait_msg.message_id}.', exc_info=sys.exc_info())
    await msg.answer(cnt1)
    await msg.answer(
        'Топ 9 залайканных мемов!',
        attachment=','.join([meme['uri'] for meme in top_9]),
        keyboard=get_start_key())


@bl.message(AttachmentTypeRule('photo'))
async def upload_meme(msg: Message):
    for att in msg.attachments:
        uri = f'photo{att.photo.owner_id}_{att.photo.id}_{att.photo.access_key}'
        await db.add_photo(uri=uri)
    await msg.answer('Спасибо за пополнение коллекции мемов!', keyboard=get_start_key())
