# -*- coding: utf-8 -*-
#
#  SkachSSBot - Route: greetings.
#  Created by Sergey Skachkov at 9/4/22
#
from vkbottle.bot import BotLabeler, Message
from vkbottle.dispatch.rules.base import FuncRule

bl = BotLabeler()


@bl.message(FuncRule(lambda msg: 'привет' in msg.text.lower()))
async def hi(message: Message):
    await message.answer("Привет вездекодерам!")
