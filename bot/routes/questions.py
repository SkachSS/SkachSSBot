# -*- coding: utf-8 -*-
#
#  SkachSSBot - Route: questions.
#  Created by Sergey Skachkov at 9/4/22
#
from vkbottle.bot import BotLabeler, Message
from vkbottle.dispatch import BuiltinStateDispenser
from vkbottle.dispatch.rules.base import (CommandRule, PayloadRule)
from vkbottle import BaseStateGroup, Keyboard, KeyboardButtonColor, Text, Location


bl = BotLabeler()
st = BuiltinStateDispenser()


class QuizStates(BaseStateGroup):
    SKY_COLOR = 0  # Какого цвета небо?
    WHAT_IS_SENSE = 1  # Что определяет сознание?
    SPRUCE_COLOR = 2  # Какого цвета Ёлка?
    WHAT_IS_AMPER = 3  # Что такое Ампер?
    MARS_COLOR = 4  # Какого цвета планета Марс?
    CATS_OR_DOGS = 5  # Кошки или собаки?
    LIKE_OSCAR = 6  # Понравился Оскар 2022 года?
    LOCATION = 7  # Запрос местоположения.


@bl.message(CommandRule('quiz_over', ['/']))
@bl.message(PayloadRule({'cmd': 'quiz_over'}))
async def quiz_over(msg: Message):
    await msg.answer('Хорошо, но если захотите ещё раз попробывать, используйте команду /quiz')


@bl.message(CommandRule('quiz', ['/']))
async def start_quiz(msg: Message):
    key = Keyboard(True)
    key.add(
        Text('Синего', {'sky_color': 'blue'}),
        KeyboardButtonColor.PRIMARY)
    key.add(
        Text('Зеленого', {'sky_color': 'green'}),
        KeyboardButtonColor.POSITIVE)
    key.add(
        Text('Красного', {'sky_color': 'red'}),
        KeyboardButtonColor.NEGATIVE)
    key.row()
    key.add(
        Text('Хватит вопросов', {'cmd': 'quiz_over'}),
        KeyboardButtonColor.SECONDARY)
    await msg.answer(
        'Давай я задам тебе пару вопросов!\nИспользуй клавиатуру для ответа.\n\n[1/8] - Какого цвета небо?',
        keyboard=key.get_json())


@bl.message(payload_map=[('sky_color', str)])
async def what_is_sense(msg: Message):
    choice = msg.get_payload_json()['sky_color']
    key = Keyboard(True)
    key.add(
        Text('Созерцание', {'what_is_sense': 'contemplation'}),
        KeyboardButtonColor.PRIMARY)
    key.add(
        Text('Позсознание', {'what_is_sense': 'subconscious'}),
        KeyboardButtonColor.PRIMARY)
    key.row()
    key.add(
        Text('Бытие', {'what_is_sense': 'existence'}),
        KeyboardButtonColor.PRIMARY)
    key.add(
        Text('Жизнь', {'what_is_sense': 'life'}),
        KeyboardButtonColor.PRIMARY)
    key.row()
    key.add(
        Text('Хватит вопросов', {'cmd': 'quiz_over'}),
        KeyboardButtonColor.SECONDARY)
    answer_is = 'Правильно!' if choice == 'blue' else 'Не правильно!'
    await msg.answer(
        f'{answer_is}\n\n[2/8] - Что, согласно историческому материализму, определяет сознание?',
        keyboard=key.get_json())


@bl.message(payload_map=[('what_is_sense', str)])
async def spruce_color(msg: Message):
    choice = msg.get_payload_json()['what_is_sense']
    key = Keyboard(True)
    key.add(
        Text('Красная', {'spruce_color': 'red'}),
        KeyboardButtonColor.NEGATIVE)
    key.add(
        Text('Зелёная', {'spruce_color': 'green'}),
        KeyboardButtonColor.POSITIVE)
    key.row()
    key.add(
        Text('Синяя', {'spruce_color': 'blue'}),
        KeyboardButtonColor.PRIMARY)
    key.add(
        Text('Серая', {'spruce_color': 'grey'}),
        KeyboardButtonColor.SECONDARY)
    key.row()
    key.add(
        Text('Хватит вопросов', {'cmd': 'quiz_over'}),
        KeyboardButtonColor.SECONDARY)
    answer_is = 'Правильно!' if choice == 'existence' else 'Не правильно!'
    await msg.answer(
        f'{answer_is}\n\n[3/8] - Какого цвета Ёлка?',
        keyboard=key.get_json())


@bl.message(payload_map=[('spruce_color', str)])
async def what_is_amper(msg: Message):
    choice = msg.get_payload_json()['spruce_color']
    key = Keyboard(True)
    key.add(
        Text('Человек', {'what_is_amper': 'human'}),
        KeyboardButtonColor.PRIMARY)
    key.add(
        Text('Учёный', {'what_is_amper': 'scientist'}),
        KeyboardButtonColor.PRIMARY)
    key.row()
    key.add(
        Text('Единица измерения', {'what_is_amper': 'unit'}),
        KeyboardButtonColor.PRIMARY)
    key.row()
    key.add(
        Text('Хватит вопросов', {'cmd': 'quiz_over'}),
        KeyboardButtonColor.SECONDARY)
    answer_is = 'Правильно!' if choice == 'green' else 'Не правильно!'
    await msg.answer(
        f'{answer_is}\nСледующие 2 вопроса с подвохом! :D\n\n[4/8] - Кто/Что такое Ампер?',
        keyboard=key.get_json())


@bl.message(payload_map=[('what_is_amper', str)])
async def mars_color(msg: Message):
    key = Keyboard(True)
    key.add(
        Text('Красного', {'mars_color': 'red'}),
        KeyboardButtonColor.POSITIVE)
    key.add(
        Text('Зеленого', {'mars_color': 'green'}),
        KeyboardButtonColor.NEGATIVE)
    key.row()
    key.add(
        Text('Серого', {'mars_color': 'grey'}),
        KeyboardButtonColor.PRIMARY)
    key.add(
        Text('Синего', {'mars_color': 'blue'}),
        KeyboardButtonColor.SECONDARY)
    key.row()
    key.add(
        Text('Хватит вопросов', {'cmd': 'quiz_over'}),
        KeyboardButtonColor.SECONDARY)
    await msg.answer(
        'Любой ответ был правильным! :D\n\n[5/8] - Какого цвета планета Марс?',
        keyboard=key.get_json())


@bl.message(payload_map=[('mars_color', str)])
async def cats_or_dogs(msg: Message):
    choice = msg.get_payload_json()['mars_color']
    key = Keyboard(True)
    key.add(
        Text('Кошки 🐱', {'cats_or_dogs': 'cats'}),
        KeyboardButtonColor.POSITIVE
    )
    key.add(
        Text('Собаки 🐶', {'cats_or_dogs': 'dogs'}),
        KeyboardButtonColor.POSITIVE
    )
    key.row()
    key.add(
        Text('Хватит вопросов', {'cmd': 'quiz_over'}),
        KeyboardButtonColor.SECONDARY)
    answer_is = 'Ну конечно красного!' if choice == 'red' else 'Ты что! Марс - Красная планета.'
    await msg.answer(
        f'{answer_is}\n\n[6/8] - Собачки или Кошки?',
        keyboard=key.get_json())


@bl.message(payload_map=[('cats_or_dogs', str)])
async def like_oscar(msg: Message):
    choice = msg.get_payload_json()['cats_or_dogs']
    key = Keyboard(True)
    key.add(
        Text('Да', {'like_oscar': 'yes'}),
        KeyboardButtonColor.POSITIVE
    )
    key.add(
        Text('Нет', {'like_oscar': 'no'}),
        KeyboardButtonColor.NEGATIVE
    )
    key.row()
    key.add(
        Text('Хватит вопросов', {'cmd': 'quiz_over'}),
        KeyboardButtonColor.SECONDARY)
    answer_is = 'Собаки крутые! 🐕' if choice == 'dogs' else 'Кошки крутые! 🐈'
    await msg.answer(
        f'{answer_is}\n\n[7/8] - Понравился Оскар 2022?',
        keyboard=key.get_json())


@bl.message(payload_map=[('like_oscar', str)])
async def share_location(msg: Message):
    choice = msg.get_payload_json()['like_oscar']
    key = Keyboard(True)
    key.add(Location({'share_location': 'yes'}))
    key.row()
    key.add(
        Text('Нет, спасибо', {'share_location': 'no'}),
        KeyboardButtonColor.NEGATIVE
    )
    answer_is = 'Понимаю, мне тоже.' if choice == 'no' else 'Интересный ответ, ну ладно.'
    await msg.answer(
        f'{answer_is}\n\nЭто был последний вопрос!\nПоделись с нами твоим местоположением для статистики.\n\n(на самом деле никакой статистики нет :D)',
        keyboard=key.get_json())


@bl.message(payload_map=[('share_location', str)])
async def quiz_end(msg: Message):
    choice = msg.get_payload_json()['share_location']
    answer_is = 'Спасибо за местоположение!' if choice == 'yes' else 'Ну и ладно((('
    await msg.answer(answer_is)
