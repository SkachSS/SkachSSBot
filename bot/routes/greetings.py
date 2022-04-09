# -*- coding: utf-8 -*-
#
#  SkachSSBot - Route: greetings.
#  Created by Sergey Skachkov at 9/4/22
#
from vkbottle.bot import BotLabeler, Message
from vkbottle.dispatch.rules.base import FuncRule
from vkbottle import Keyboard, KeyboardButtonColor, Text


bl = BotLabeler()


@bl.message(FuncRule(lambda msg: 'привет' in msg.text.lower()))
@bl.message(payload={'command': 'start'})
async def hi(message: Message):
    key = Keyboard(True)
    key.add(Text('Мемы'), KeyboardButtonColor.POSITIVE)
    key.row()
    key.add(Text('Вопросы'), KeyboardButtonColor.PRIMARY)
    key.row()
    key.add(Text('Статистика'), KeyboardButtonColor.SECONDARY)
    cnt = 'Привет вездекодерам!\n\n'
    cnt += 'Этот бот умеет кидать мемы, вести по ним статистику и задавать вопросы!\n'
    cnt += 'А ещё ты можешь добавить своих мемов в коллекцию, просто кинь мне фотографию!'
    await message.answer(cnt, keyboard=key.get_json())
