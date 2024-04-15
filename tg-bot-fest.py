import telebot
from telebot import types
import time
import sqlite3
# Bot for the festival. In the future, change the text

# name bot: FestivalQuestBot
bot = telebot.TeleBot('6357823947:AAHxKALq_W8zbSFe13GQSuqvYI25-nMcYYQ')

# info user
user_data = {}

# hello and disclaimer
@bot.message_handler(commands=['start'])
def welcome_new_members(message):
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text="Продолжить", callback_data='continue')
    keyboard.add(button)

    bot.send_message(message.chat.id,
                     "Добро пожаловать в квест-бота “Найди того, не знаю кого” фестиваля “Кибер сказка” 👋\n\n"
                     "Прежде чем начать квест, ознакомьтесь со <b>вступительной информацией.</b>\n⬇️\n\n"
                     "Вся информация о персонаже, включая его личные данные, является полностью вымышленной и предназначена исключительно для развлекательных целей в рамках фестиваля “Кибер сказка”. \n"
                     "Никакие реальные личности или события не имеют отношения к этому персонажу или его истории.\n\n"
                     "Мне всё понятно 👍", reply_markup=keyboard, parse_mode='HTML')

# registration
@bot.callback_query_handler(func=lambda call: call.data == 'continue')
def ask_username(call):
    global user_data

    chat_id = call.message.chat.id
    user_data[chat_id] = {'user_name': call.from_user.first_name, 'id': chat_id, 'mail_user': '',
                          'fio_flag': False, 'prog_lang_flag': False, 'city_flag': False, 'count_win': 0}

    msg = bot.send_message(chat_id, '<b>Важно</b>❗\n\nИнформацию можно ввести только один раз! Не удаляйте данный чат и не регистрируйтесь заново, чтобы не потерять текущий прогресс.\n\nВведите имя:', parse_mode='HTML')
    bot.register_next_step_handler(msg, ask_mailuser)


def ask_mailuser(message):
    global user_data
    user_data[message.chat.id]['user_name'] = message.text
    msg = bot.send_message(message.chat.id, f'Приятно познакомиться, {user_data[message.chat.id]["user_name"]}! Для участия в конкурсе, ведите ваш адрес электронной почты.\n'
                                                 f'Мы обещаем, что он останется в целости и сохранности.')
    bot.register_next_step_handler(msg, save_infouser)

def save_infouser(message):
    global user_data
    user_data[message.chat.id]['mail_user'] = message.text
    user_name = user_data[message.chat.id]['user_name']

    conn = sqlite3.connect('C:\\Users\\pgodunov\\PycharmProjects\\pythonProject\\.venv\\fest-users-data.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, name TEXT, email TEXT)")

    cursor.execute("SELECT * FROM users WHERE user_id=?", (message.chat.id,))
    data = cursor.fetchone()
    if data is not None:
        return

    cursor.execute("INSERT INTO users (user_id, name, email) VALUES (?, ?, ?)",
                   (message.chat.id, user_name, message.text))

    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, 'Спасибо! Ваша информация была сохранена.')

    for i in range(3, 0, -1):
        bot.send_message(message.chat.id, 'Продолжим через: ' + str(i))
        time.sleep(1)
    start_new_game(message)


# story
@bot.message_handler(commands=['ready'])
def start_new_game(message):
    bot.send_message(message.chat.id,"Царь написал вам сообщение в Telegram о том, что ему необходимы данные одного сотрудника. К сожалению, hr-менеджеры, окаянные, потеряли все его документы. Теперь, это дело ложиться на ваши плечи. "
                     "Единственное, что удалось найти, это его номер телефона _ ___ ___ __ __. Сотрудник работает программистом и явно зарегистрирован в социальных сетях, мессенджерах и других источниках. \n"
                     "Ваша задача - восстановить данные этого сотрудника.\n"
                     "Используйте /todolist, чтобы увидеть свой прогресс и список данных, которые необходимо восстановить.\n"
                     "А если потребуется помощь, напишите /help\n\n"
                     "Находите информацию и вписывайте её в любой последовательности. Желаем удачи 🍀")

# Для скриншота чата от царя
# Мне нужны данные нашего сотрудника, но hr-менеджеры окоянные, потеряли все его документы! 😡 Теперь это твоя задача. Мы нашли только его номер телефона _ _ _  . Он работает программистом, так что, наверняка, зарегистрирован в соцсетях и мессенджерах. 🌐
# Твоя задача - восстановить данные этого человека.
# Используй /todolist, чтобы отслеживать свой прогресс и узнать, какие данные надо восстановить. 📝


# help input
@bot.message_handler(commands=['help'])
def user_help(message):
    keyboard = types.InlineKeyboardMarkup()
    key_what = types.InlineKeyboardButton(text='С чего начать?', callback_data='what')
    keyboard.add(key_what)
    key_end = types.InlineKeyboardButton(text='Что показать после выполнения?', callback_data='end')
    keyboard.add(key_end)
    bot.send_message(message.chat.id, 'С чем вам требуется помощь?', reply_markup=keyboard)

# help output
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "what":
        bot.send_message(call.message.chat.id, "Попробуйте найти этого человека в Telegram по его номеру телефона. Возможно, в его профиле будут зацепки.")
    elif call.data == "end":
        bot.send_message(call.message.chat.id, "После прохождения откройте /todolist и покажите. Если все данные собраны, пункты в нём будут выполнены и вы получите характерное сообщение о прохождении.")


# to-do list
@bot.message_handler(commands=['todolist'])
def to_do_list(message):
    global user_data
    tasks = ['ФИО сотрудника', 'Любимый язык программирования', 'Город проживания']
    if message.chat.id not in user_data:
        user_data[message.chat.id] = {'fio_flag': False, 'prog_lang_flag': False, 'city_flag': False, 'count_win': 0}
    user_flags = user_data[message.chat.id]
    bot.send_message(message.chat.id, f"Список данных сотрудника:")
    for task, flag in zip(tasks, ['fio_flag', 'prog_lang_flag', 'city_flag']):
        if flag in user_flags and user_flags[flag]:
            bot.send_message(message.chat.id, f"☑ <del>{task}</del>", parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, f"⬜ {task}")


# Все квесты: fio_flag prog_lang_flag city_flag count_win
@bot.message_handler(content_types=['text'])
def check_answer(message):
    global user_data
    answer = message.text.lower()
    chat_id = message.chat.id

    # print(user_data)

    if chat_id in user_data:
        # FIO search
        if answer == "Датаев Илья Максимович".lower():
            if user_data[chat_id]['fio_flag'] == False:
                user_data[chat_id]['fio_flag'] = True
                user_data[chat_id]['count_win'] += 1
                bot.send_message(message.chat.id, 'ФИО угадано!')
                return
            else:
                bot.send_message(message.chat.id, 'Вы уже нашли ФИО сотрудника.')

        # prog_lang search
        if answer == "JavaScript".lower():
            if user_data[chat_id]['prog_lang_flag'] == False:
                user_data[chat_id]['prog_lang_flag'] = True
                user_data[chat_id]['count_win'] += 1
                bot.send_message(message.chat.id, 'JavaScript - любимый язык программирования отрудника.')
                return
            else:
                bot.send_message(message.chat.id, 'Любимый язык программирования уже угадан.')

        # city search
        if answer == "Москва".lower():
            if user_data[chat_id]['city_flag'] == False:
                user_data[chat_id]['city_flag'] = True
                user_data[chat_id]['count_win'] += 1
                bot.send_message(message.chat.id, 'Верно! Сотрудник живёт в Москве.')
                return
            else:
                bot.send_message(message.chat.id, 'Город проживания уже угадан.')

        if user_data[chat_id]['count_win'] == 3:
            bot.send_message(message.chat.id, 'Вы успешно заершили квест 🙌 \n Покажите выполненный /todolist')

        if answer not in ["Датаев Илья Максимович", "JavaScript", "Москва"]:
            bot.send_message(message.chat.id, 'Такой команды нет.')


bot.polling(non_stop=True)
