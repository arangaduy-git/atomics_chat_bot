import telebot
import config
import messages
from telebot import types
import sqlite3

API_TOKEN = config.BOT_TOKEN
bot = telebot.TeleBot(API_TOKEN)
defaultmarkup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
defaultmarkup.add(types.KeyboardButton('Просмотр мероприятий'))
defaultmarkup.add(types.KeyboardButton('Записаться на мероприятие'))
defaultmarkup.add(types.KeyboardButton('Выписаться с мероприятия'))
defaultmarkup.add(types.KeyboardButton('Мероприятия, на которые я записан'))


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, messages.start_message, reply_markup=defaultmarkup)
    user_id = message.from_user.id

    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    info = cursor.execute('SELECT * FROM users WHERE userid=?', (user_id,))
    if not info.fetchone():
        cursor.execute('INSERT INTO Users (userid, events) VALUES (?, ?)', (user_id, ''))

    connection.commit()
    connection.close()


def filter_true_events(event):
    return True if True in event else False


def filter_false_events(event):
    return False if True in event else True


@bot.message_handler(func=lambda message: message.text == 'Мероприятия, на которые я записан')
def message_reply(message):
    user_id = message.from_user.id
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    info = cursor.execute('SELECT events FROM users WHERE userid=?', (user_id,)).fetchall()

    connection.commit()
    connection.close()
    bot.send_message(message.chat.id, f'Вы записаны на данные мероприятия: "{info[0][0]}"',
                     reply_markup=defaultmarkup)


@bot.message_handler(func=lambda message: message.text == 'Просмотр мероприятий')
def message_reply(message):
    text = '```\nОбъязательные мероприятия:\n'
    events_true = filter(filter_true_events, config.events)
    for event in list(events_true):
        text += ' - '.join(event[0:-1]) + '\n'
    events_false = filter(filter_false_events, config.events)
    text += '\nМероприятия на которые можно записаться:\n'
    for event in list(events_false):
        text += ' - '.join(event[0:-1]) + '\n'
    text += '```'
    bot.send_message(message.chat.id, text, reply_markup=defaultmarkup, parse_mode= 'Markdown')


@bot.message_handler(func=lambda message: message.text == 'Записаться на мероприятие')
def message_reply(message):
    bot.send_message(message.chat.id, 'Введите команду /sign_up "Мероприятие "для записи на мероприятие\n'
                                      'Например: /sign_up Бассейн', reply_markup=defaultmarkup)


@bot.message_handler(func=lambda message: message.text == 'Выписаться с мероприятия')
def message_reply(message):
    bot.send_message(message.chat.id, 'Введите команду /check_out "Мероприятие " для того, чтобы выписаться с мероприятия\n'
                                      'Например: /check_out Бассейн', reply_markup=defaultmarkup)


@bot.message_handler(commands=['events', 'event'])
def message_reply(message):
    text = '```\nОбъязательные мероприятия:\n'
    events_true = filter(filter_true_events, config.events)
    for event in list(events_true):
        text += ' - '.join(event[0:-1]) + '\n'
    events_false = filter(filter_false_events, config.events)
    text += '\nМероприятия на которые можно записаться:\n'
    for event in list(events_false):
        text += ' - '.join(event[0:-1]) + '\n'
    text += '```'
    bot.send_message(message.chat.id, text, reply_markup=defaultmarkup, parse_mode= 'Markdown')


@bot.message_handler(commands=['sign_event', 'sign_events', 'event_sign', 'events_sign', 'sign_up'])
def message_reply(message):
    msg = message.text.split()
    msg = ' '.join(msg[1:len(msg)])
    if not msg:
        bot.send_message(message.chat.id, f'Введите название мероприятия!\n'
                                          f'Например: /sign_up Бассейн', reply_markup=defaultmarkup)
        return
    for event in config.events:
        if msg in event:
            if False in event:
                user_id = message.from_user.id
                connection = sqlite3.connect('users.db')
                cursor = connection.cursor()

                info = cursor.execute('SELECT events FROM users WHERE userid=?', (user_id,)).fetchall()
                if msg not in info[0][0]:
                    cursor.execute('UPDATE Users SET events = ? WHERE userid = ?', (info[0][0] + msg + ', ', user_id))
                else:
                    bot.send_message(message.chat.id, f'Вы уже записаны на мероприятие "{msg}"',
                                     reply_markup=defaultmarkup)
                    connection.commit()
                    connection.close()
                    return

                connection.commit()
                connection.close()
                bot.send_message(message.chat.id, f'Вы успешно записались на мероприятие "{msg}"',
                                 reply_markup=defaultmarkup)
                return
            else:
                bot.send_message(message.chat.id,
                                 f'На это мероприятие нельзя записаться, так как оно объязательное',
                                 reply_markup=defaultmarkup)
                return
    bot.send_message(message.chat.id, f'Мероприятие "{msg}" не найдено!', reply_markup=defaultmarkup)


@bot.message_handler(commands=['check_out', 'out_check', 'sign_out', 'out_sign', 'events_out', 'event_out'])
def message_reply(message):
    msg = message.text.split()
    msg = ' '.join(msg[1:len(msg)])
    if not msg:
        bot.send_message(message.chat.id, f'Введите название мероприятия!\n'
                                          f'Например: /check_out Бассейн', reply_markup=defaultmarkup)
        return
    for event in config.events:
        if msg in event:
            if False in event:
                user_id = message.from_user.id
                connection = sqlite3.connect('users.db')
                cursor = connection.cursor()

                info = cursor.execute('SELECT events FROM users WHERE userid=?', (user_id,)).fetchall()
                if msg in info[0][0]:
                    msg_1 = info[0][0].replace(msg + ', ', '')
                    cursor.execute('UPDATE Users SET events = ? WHERE userid = ?', (msg_1, user_id))
                else:
                    bot.send_message(message.chat.id, f'Вы не записаны на мероприятие "{msg}"',
                                     reply_markup=defaultmarkup)
                    connection.commit()
                    connection.close()
                    return

                connection.commit()
                connection.close()
                bot.send_message(message.chat.id, f'Вы успешно выписались с мероприятия "{msg}"',
                                 reply_markup=defaultmarkup)
                return
            else:
                bot.send_message(message.chat.id,
                                 f'С этого мероприятия нельзя выписаться, так как оно объязательное',
                                 reply_markup=defaultmarkup)
                return
    bot.send_message(message.chat.id, f'Мероприятие "{msg}" не найдено!', reply_markup=defaultmarkup)


@bot.message_handler(commands=['signed_events'])
def message_reply(message):
    user_id = message.from_user.id
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    info = cursor.execute('SELECT events FROM users WHERE userid=?', (user_id,)).fetchall()

    connection.commit()
    connection.close()
    bot.send_message(message.chat.id, f'Вы записаны на данные мероприятия: "{info[0][0]}"',
                     reply_markup=defaultmarkup)


bot.polling()
