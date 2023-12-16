"""Установленные библиотеки"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters.command import Command
import sqlite3
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from bs4 import BeautifulSoup
import requests
from random import randint
import time
from test import converter, exlogging

"""Парсинг вышкинского сайта"""

# https://www.hse.ru/news/announcements/?domain114721158=on
# https://www.hse.ru/news/announcements/
# https://www.hse.ru/news/announcements/?research_target_220096694=on

url = 'https://www.hse.ru/news/announcements/?research_target_220096694=on'
req = requests.get(url)
source = req.text


def currentevents():
    """
    Функция которая парсит сайты вшэ.
    :returns: список из словарей из данных о мероприятиях
    :rtype: Dict
    """

    allevlist = []
    soup = BeautifulSoup(source, 'lxml')
    allevents = soup.findAll('div', class_='b-events')
    for event in allevents:
        allevlist.append({
            'date': event.find('span', class_='g-day smaller').text +
                    event.find('span', class_='g-day smaller').nextSibling,
            'time': event.find('div', class_='b-events__extra date').text,
            'description': event
            .find('div', class_='b-events__body_title large')
            .find('p').text,
            'href': event.find('div', class_='b-events__body_title large')
            .find('a').get('href')
        })
    return allevlist


"""Работа с апи телеграмма и базой данных"""

b1 = KeyboardButton(text='Вспомнить мои мероприятия🥹')
b2 = KeyboardButton(text='Новое мероприятие🤓')
kb1 = ReplyKeyboardMarkup(keyboard=[[b1, b2]])
in1 = InlineKeyboardButton(text='Убрать что-нибудь', callback_data='delete')
im = sqlite3.connect('studdata.db')
inline = InlineKeyboardMarkup(inline_keyboard=[[in1]])
delinline = InlineKeyboardMarkup(inline_keyboard=[[]])

"""Фильтры для обработчиков сообщений"""


class MyFilter:
    def __init__(self, text):
        self.text = text

    def __call__(self, message):
        return message.text == self.text


class CallFilter:
    def __init__(self, data):
        self.data = data

    def __call__(self, callback):
        return callback.data == self.data


class SpecCallFilter(CallFilter):

    def __call__(self, callback):
        for i in self.data.split():
            if i == callback.data:
                return True
        else:
            return False


class DelCallFilter(CallFilter):

    def __call__(self, callback):
        return self.data in callback.data


""""""

logging.basicConfig(level=logging.INFO)

bot = Bot(token="6824893217:AAHUfEX9FevgtXe0M1dyPbxrDvbBGAcwtV0")

dp: Dispatcher = Dispatcher()

with sqlite3.connect('studdata.db') as con:
    dbcon = con.cursor()

    @dp.message(Command('start'))
    async def cmd_start(message):

        """
        Функция отвечающая на команду start.
        :param message: Сообщения пользователя.
        :type message: aiogram.types.message.Message
        :returns: Реагирует на команду старт, занося имя пользователя и id телеграмма в базу данных
        :rtype: message.answer
        """

        try:
            with sqlite3.connect('studdata.db') as conn:
                conn.cursor().execute('insert into students values (?, ?)',
                                      (message.chat.id, message.chat.first_name))
                await message.answer('Добро пожаловать {}!🙆🏿'.format(message.chat.first_name), reply_markup=kb1)
        except sqlite3.IntegrityError:
            if message.chat.id == 478571763:
                await message.answer(
                    'С возвращением {}!🦝'.format(message.chat.first_name),
                    reply_markup=kb1)
                await bot.send_sticker(chat_id=478571763,
                                       sticker='CAACAgIAAxkBAAJm1mV3a6Z4w4vzMEIfP'
                                               'Oom7Y6LoW82AALdJAACMpVpSRJtw9Kr48TPMwQ')
            else:
                await message.answer(
                    'С возвращением {}!🫦'.format(message.chat.first_name),
                    reply_markup=kb1)
        finally:
            await message.delete()
            await exlogging(message)


    @dp.message(MyFilter('Вспомнить мои мероприятия🥹'))
    async def rem(message):

        """
        Функция выводящая все мероприятия на которые записан пользователь.
        :param message: Сообщение пользователя.
        :type message: aiogram.types.message.Message
        :returns: Присылает пользователю сообщение в котором говорится обо всех мероприятиях на которые он записался
        :rtype: message.answer
        """

        await exlogging(message)

        allev = ''
        dbcon.execute('delete from events where sectime < {mydate}'.format(mydate=int(time.time())))
        dbcon.execute('select * from events where login={}'.format(message.chat.id))
        result = dbcon.fetchall()
        for x in range(len(result)):
            allev += ('{}) {}\n\n{}\n\n\n'.format(x + 1, result[x][2], result[x][1]))

        if len(allev.replace('\n', '')) == 0:
            await message.answer(
                '<i>У вас нет запланированных мероприятий</i>',
                parse_mode='html',
            )
        else:
            await message.answer(
                allev + '\nВот такие <i><b>пироги</b></i>',
                parse_mode='html',
                reply_markup=inline
            )


    @dp.message(MyFilter('Новое мероприятие🤓'))
    async def new_event(message):

        """
        Функция выводящая текущие мероприятоия ВШЭ.
        :param message: Команда Новое мероприятие🤓
        :type message: aiogram.types.message.Message
        :returns: Присылает список всех мероприиятий для выбора
        :rtype: message.answer
        """

        evs = currentevents()[0:8]
        btns = []
        evsmessage = ''
        for one in range(len(evs)):
            evsmessage += '{0})\t{1} в {2}\n\nПройдет: <i>{3}</i>\nПодробнее <a href="{4}">здесь</a>.\n\n\n'.format(
                str(one + 1),
                evs[one]['date'],
                evs[one]['time'],
                evs[one]['description'],
                evs[one]['href']
            )
            btns.append(InlineKeyboardButton(
                text=str(one + 1),
                callback_data=str(one),
            ))
        btns = [btns, [InlineKeyboardButton(text='Не хочу🥶', callback_data='lol')]]
        inl = InlineKeyboardMarkup(inline_keyboard=btns)
        evsmessage += '\n<b>На какое меропиятие хотите записаться?</b>'

        await message.answer(
            evsmessage,
            parse_mode='html',
            reply_markup=inl,
        )


    @dp.callback_query(CallFilter('delete'))
    async def dell(callback):  # !

        """
        Фунеция отлавливающая коллбек запрос на удаление мероприятия.
        :param callback:
        :type callback: aiogram.types.callback.CallBackQuery
        :returns: Реагирует на нажатие кнопки Удалить на инлайн клавиатуре и передает сообщение другой функции
         для последуюшей обработки
        :rtype: callback
        """

        dbcon.execute('select * from events where login={}'.format(callback.message.chat.id))
        con.commit()
        allmy = dbcon.fetchall()
        return await bot.edit_message_reply_markup(
            message_id=callback.message.message_id,
            chat_id=callback.message.chat.id,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=str(x + 1), callback_data='/d ' + str(x)) for x in range(len(allmy))]]
            )
        )


    @dp.callback_query(DelCallFilter('/d'))
    async def final(callback):

        """
        Функция удаляющая выбранное событтие.
        :param callback: Принимает коллбек запрос
        :type callback: aiogram.types.callback.CallBackQuery
        :returns: Обрабатывает запрос с прошлой функции и удаляет выбранное событие
        :rtype: callback
        """

        dbcon.execute('select * from events where login={}'.format(callback.message.chat.id))
        con.commit()
        allmy = dbcon.fetchall()
        print('Passed', allmy)
        dbcon.execute("delete from events where login={} and event='{}'".format(callback.message.chat.id,
                                                                                allmy[int(callback.data.split()[-1])][1]
                                                                                ))
        con.commit()
        await callback.message.delete()
        await bot.send_message(text='Событие удалено🤯', chat_id=callback.message.chat.id)


    @dp.callback_query(CallFilter('lol'))
    async def loll(callback):

        """
        Функция обрабатывающая запрос с инлай клавиатуры сообщения.
        :param callback: Запрос об окончаниии выбора
        :type callback: aiogram.types.callback.CallBackQuery
        :returns: Убирает сообщение с выбором меропритий
        :rtype: callback
        """

        await callback.message.delete()
        await bot.send_sticker(chat_id=callback.message.chat.id,
                               sticker='CAACAgIAAxkBAAJmTWV1vikou8-G2PBSViaOZFwwRq5sAAIaFgACw97xSxLetM2_dAOqMwQ')


    @dp.callback_query(SpecCallFilter('0 1 2 3 4 5 6 7 8 9 10'))
    async def clhandler(callback):

        """
        Функция обрабатывающая запрос с инлай клавиатуры сообщения.
        :param callback: Обрабатывает коллбэк запрос на выбор мероприятия
        :type callback: aiogram.types.callback.CallBackQuery
        :returns: Передает на обработку выбранное мероприятие
        :rtype: callback
        """

        evc = currentevents()
        try:
            dbcon.execute('insert into events values (?, ?, ?, ?)',
                          (
                              callback.message.chat.id,
                              evc[int(callback.data)]['description'],
                              evc[int(callback.data)]['date'] + ' в ' + evc[int(callback.data)]['time'],
                              converter(evc[int(callback.data)]['date'].replace(',', '').split() + [
                                  evc[int(callback.data)]['time']])
                          )
                          )
            con.commit()
            await callback.message.delete()
            await bot.send_message(
                chat_id=callback.message.chat.id,
                text='Записал тебя'
            )
            await bot.send_sticker(chat_id=callback.message.chat.id,
                                   sticker='CAACAgIAAxkBAAJmyGV3LbZbnPqpuBPu2uFP51DagTJmAAKsFQACZj4ISetkezw6-wqpMwQ')
        except sqlite3.IntegrityError:
            await bot.send_message(
                chat_id=callback.message.chat.id,
                text='Вы уже записаны были на данное мероприятие😧'
            )


    @dp.message()
    async def trashcan(message):

        """
        Функция обрабатывающая нежелательные сообщения.
        :param message: Запрос об окончаниии выбора
        :type message: aiogram.types.message.Message
        :returns: Сообщение и стикер
        :rtype: message
        """

        await exlogging(message)

        await message.answer(['Да не понимаю я тебя', 'Ничего не понял', 'Зачем ты так со мной', 'a?',
                              'Семь раз подумай, один раз ээ забыл', 'Еще че', 'No u'][randint(0, 6)])
        await bot.send_sticker(chat_id=message.chat.id,
                               sticker=['CAACAgIAAxkBAAJmXGV17yyRixtJz5FI2f7btSZG4RbQAAJIPQACNJFQSxboe-0TTDGOMwQ',
                                        'CAACAgIAAxkBAAJmamV18vaDxXDq4xqykdURc_p8QfG0AAIaFQAC5EWJSAWIR3DOabUSMwQ',
                                        'CAACAgIAAxkBAAJmbGV180FkSBVY_jzReVTTMbh58bqpAALjIQACMukISc-ratM09ccWMwQ',
                                        'CAACAgIAAxkBAAJmbmV187hfxhWzal8GYSX3Iegh6XlHAAJ9FgACEO0IST90KOVDRRhcMwQ',
                                        'CAACAgIAAxkBAAJmcGV189dZ-Lcbvd1gOTffFpjH9rbnAALeFAACdDRoSBmj4nFVnthIMwQ',
                                        'CAACAgIAAxkBAAJmcmV18-adepSXp2eLPK7MIxx_wMozAAJZFwAC1InpSAifFwVetekTMwQ',
                                        'CAACAgIAAxkBAAJmdGV19A_kBm7ZiRtk2z5UCVNHrywpAALcFAACIjD5SyKhra_cxSi8MwQ',
                                        'CAACAgIAAxkBAAJmdmV19DsX1hbY7GKlthh2B7s5pZRXAAJKFAACHksRSIHyig858ZtFMwQ',
                                        'CAACAgIAAxkBAAJmtmV22wFn_NKgnLGZvWRtekKBq4X9AAJdQQACZYdRSwUGjwXc8rQ6MwQ'][
                                   randint(0, 8)])


    asyncio.run(dp.start_polling(bot))
