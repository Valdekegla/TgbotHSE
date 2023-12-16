# import pyautogui
# pyautogui.hotkey('alt', 'f4')
# pyautogui.press('enter')

import time
import datetime
import unittest


def converter(n):
    """
    :param n: Строка из числа и названия месяца
    :return: Заданное время в секундах
    """
    print(n)
    datetime_object = datetime.datetime.fromtimestamp(time.time())
    print(datetime_object)
    dates = {
        'января': 1,
        'февраля': 2,
        'марта': 3,
        'апреля': 4,
        'мая': 5,
        'июня': 6,
        'июля': 7,
        'августа': 8,
        'сентября': 9,
        'октября': 10,
        'ноября': 11,
        'декабря': 12
    }
    if n[1] == 'января' or n[1] == 'февраля':
        return time.mktime(time.strptime('{}-{}-{} {}:{}'.format(
            str(datetime_object).split('-')[0],
            dates[n[1]],
            n[0],
            n[3][0:2],
            n[3][4:6]), "%Y-%m-%d %H:%M")) + 31536000
    else:
        return time.mktime(time.strptime(
            '{}-{}-{} {}:{}'.format(
                str(datetime_object).split('-')[0],
                dates[n[1]],
                n[0],
                n[3][0:2],
                n[3][4:6]), "%Y-%m-%d %H:%M"))

async def exlogging(message):
    print('--Пользователь {} отправляет сообщение {}'.format(message.chat.first_name, message.text))


if __name__ == "__main__":
    pass
