import telebot, sqlite3
# new
bot = telebot.TeleBot('token')

user_data = {}

@bot.message_handler(commands=['reg'])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {'user_name': message.from_user.first_name, 'id': chat_id, 'one_flag': False, 'two_flag': False, 'count_win': 0, 'comment_user': ''}
    msg = bot.send_message(message.chat.id, 'Как вас зовут?')
    bot.register_next_step_handler(msg, ask_username)

def ask_username(message):
    chat_id = message.chat.id
    user_data[chat_id]['user_name'] = message.text
    msg = bot.send_message(message.chat.id, 'Дайте комментарий.')
    bot.register_next_step_handler(msg, ask_comment)

def ask_comment(message):
    chat_id = message.chat.id
    user_data[chat_id]['comment_user'] = message.text
    bot.send_message(message.chat.id, 'Ваша информация была сохранена.\nВведите "one" и "two" чтобы выиграть.')

    conn = sqlite3.connect('C:\\Users\\pgodunov\\PycharmProjects\\pythonProject\\.venv\\fest-users-data.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, name TEXT, comment TEXT)")
    cursor.execute("INSERT INTO users (user_id, name, comment) VALUES (?, ?, ?)",
                   (message.chat.id, user_data[chat_id]['user_name'], user_data[chat_id]['comment_user']))
    conn.commit()
    conn.close()

@bot.message_handler(content_types=['text'])
def check_answer(message):
    chat_id = message.chat.id
    answer = message.text.lower()
    print(user_data)
    if chat_id in user_data:
        if answer == "one".lower():
            if user_data[chat_id]['one_flag'] == False:
                user_data[chat_id]['one_flag'] = True
                user_data[chat_id]['count_win'] += 1
                bot.send_message(message.chat.id, '"one" - готово.')
                return
            else:
                bot.send_message(message.chat.id, '"one" - уже отгадано.')

        if answer == "two".lower():
            if user_data[chat_id]['two_flag'] == False:
                user_data[chat_id]['two_flag'] = True
                user_data[chat_id]['count_win'] += 1
                bot.send_message(message.chat.id, '"two" - готово.')
                return
            else:
                bot.send_message(message.chat.id, '"two" - уже отгадано.')

        if 'count_win' in user_data[chat_id] and user_data[chat_id]['count_win'] == 2:
            bot.send_message(message.chat.id, 'Готово!')
            return

        if answer not in ["one", "two"]:
            bot.send_message(message.chat.id, 'Такой команды нет.')

bot.polling(non_stop=True)


