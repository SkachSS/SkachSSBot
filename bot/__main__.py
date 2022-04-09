# -*- coding: utf-8 -*-
#
#  Vezdekod 2022 - SkachSSBot
#  Created by Sergey Skachkov at 9/4/22
#
import os
import logging

from vkbottle.bot import Bot

from .routes import labelers


DEBUG = False
VERSION = '0.1'
TOKEN = os.environ.get('BOT_TOKEN', '')
bot = Bot(TOKEN)

logging.basicConfig(
    format='[%(levelname)s] %(name)s (%(lineno)d) >> %(funcName)s: %(message)s',
    level=logging.DEBUG if DEBUG else logging.INFO)

log = logging.getLogger('skachssbot')
log.info(f'SkachSSBot v{VERSION}')
log.debug(f'Bot Token: {TOKEN}')

for labeler in labelers:
    bot.labeler.load(labeler)

bot.run_forever()
