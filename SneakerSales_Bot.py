# coding: utf-8

# In[1]:


import telebot
from telebot import types
import copy
import os

pass_to_project = ""

# In[3]:

token = str(os.environ['token'])

bot = telebot.TeleBot(token)
knownUsers = set()
userStep = {}
profile = {}
registrations = {}
creating_users = {}

sizes = [str(i) + ' EU' for i in range(35, 52)]


# In[ ]:


class user_parameters():
    def __init__(self, model_type):
        if model_type == 'Мужской':
            self.model_type = 'man'
        elif model_type == 'Женский':
            self.model_type = 'woman'
        elif model_type == 'Любой':
            self.model_type = 'any'

        self.sizes = []

    def add_size(self, size):
        self.sizes.append(size)

    def get_russian_model_type(self):
        if self.model_type == 'man':
            return 'Мужской'
        elif self.model_type == 'woman':
            return 'Женский'
        elif self.model_type == 'any':
            return 'Любой'

    def sizes_count(self):
        return len(self.sizes)

    def get_model_type(self):
        return self.model_type

    def get_sizes(self):
        return self.sizes


# In[ ]:


def save_user(id):
    knownUsers.add(id)
    folder_name = creating_users[id].get_model_type()
    for size in creating_users[id].get_sizes():
        size_file = open(
            f'{pass_to_project}sought_for_items/{folder_name}/{folder_name}{size}.txt',
            'a')
        size_file.write(str(id) + '\n')
        size_file.close()


def delete_user_parameters(id):
    sizes = creating_users[id].get_sizes()
    folder_name = creating_users[id].get_model_type()
    for size in sizes:
        file_location = f'{pass_to_project}sought_for_items/{folder_name}/{folder_name}{size}.txt'
        size_file = open(file_location, 'r')
        users = size_file.read().strip().split('\n')
        size_file.close()
        size_file = open(file_location, 'w')
        users.remove(str(id))
        for user in users:
            if user != '':
                size_file.write(user + '\n')
        size_file.close()


# In[ ]:

@bot.message_handler(commands=['help'])
def help_message(message):
    cid = message.chat.id
    text = message.text.strip()
    markup = types.ReplyKeyboardRemove()
    commands = ['/start - запуск',
                '/help - просмотр команд',
                '/edit - изменить параметры',
                '/report - сообщить об ошибке'
                ]
    bot.send_message(cid, '\n\n'.join(commands), reply_markup=markup)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    cid = message.from_user.id
    if cid not in knownUsers:
        bot.send_message(message.from_user.id, """Я помогу Вам мониторить появление скидок на интересующую Вас категорию.
Просто дайте мне Ваш размер и остальные параметры.""")

        markup = types.ReplyKeyboardMarkup()
        buttonA = types.KeyboardButton('Мужской')
        buttonB = types.KeyboardButton('Женский')
        buttonC = types.KeyboardButton('Любой')

        markup.row(buttonA, buttonB, buttonC)

        bot.send_message(cid, 'Выберите пол.', reply_markup=markup)
        userStep[cid] = 1

    else:
        bot.send_message(cid, 'Вы уже оставляли информацию')

        model_type = creating_users[cid].get_russian_model_type()
        sizes = " EU, ".join(map(str, creating_users[cid].get_sizes()))

        bot.send_message(cid,
                         f'Тип модели: {model_type} \nРазмеры: {sizes} EU')


@bot.message_handler(
    func=lambda message: message.chat.id in userStep and userStep[
                                                             message.chat.id] == 1)
def add_model_type(message):
    cid = message.chat.id
    text = message.text.strip()
    if text.lower().strip() in ['мужской', 'женский', 'любой']:
        creating_users[cid] = user_parameters(text)
        markup = types.ReplyKeyboardMarkup(row_width=5)
        for i in range(35, 52):
            markup.add(str(i) + ' EU')
        bot.send_message(cid, 'Выберите размер. \n(Не более трёх)',
                         reply_markup=markup)
        userStep[cid] = 2
    else:
        bot.send_message(cid,
                         "Кажется, Вы ввели что-то не то О_о \n Повторите")


@bot.message_handler(
    func=lambda message: message.chat.id in userStep and userStep[
                                                             message.chat.id] == 2)
def add_size(message):
    cid = message.chat.id
    text = message.text.strip()
    markup = types.ReplyKeyboardRemove(selective=False)
    if text in sizes:
        creating_users[cid].add_size(int(text.split()[0]))

        if len(creating_users[cid].get_sizes()) >= 3:
            userStep[cid] = 3
            save_user(cid)
            markup = types.ReplyKeyboardRemove()
            bot.send_message(cid,
                             'Отлично! \nSneakerSales_Bot оповестит Вас о появившихся скидках \n/edit - изменить параметры',
                             reply_markup=markup)

        else:
            markup = types.ReplyKeyboardMarkup(row_width=5)
            markup.add('Пропустить')
            for i in range(35, 52):
                if i not in creating_users[cid].get_sizes():
                    markup.add(str(i) + ' EU')
            bot.send_message(cid, 'Можете добавить ещё.', reply_markup=markup)

    elif text == 'Пропустить':
        userStep[cid] = 3
        save_user(cid)
        markup = types.ReplyKeyboardRemove()
        bot.send_message(cid,
                         'Отлично! \nSneakerSales_Bot оповестит Вас о появившихся скидках \n/edit - изменить параметры',
                         reply_markup=markup)

    else:
        bot.send_message(cid,
                         "Кажется, Вы ввели что-то не то О_о \n Повторите")


@bot.message_handler(commands=['edit'])
def edit_user_parameters(message):
    cid = message.chat.id
    text = message.text.strip()
    if cid not in knownUsers:
        send_welcome(message)
    else:
        bot.send_message(cid, 'Ваши текущие параметры:')

        model_type = creating_users[cid].get_russian_model_type()
        sizes = " EU, ".join(map(str, creating_users[cid].get_sizes()))

        bot.send_message(cid,
                         f'Тип модели: {model_type} \nРазмеры: {sizes} EU')

        markup = types.ReplyKeyboardMarkup(row_width=5)
        buttonA = types.KeyboardButton('Да')
        buttonB = types.KeyboardButton('Нет')
        markup.row(buttonA, buttonB)
        bot.send_message(cid, f'Хотиете поменять?', reply_markup=markup)
        userStep[cid] = 4


@bot.message_handler(
    func=lambda message: message.chat.id in userStep and userStep[
                                                             message.chat.id] == 4)
def add_size(message):
    cid = message.chat.id
    text = message.text.strip()
    if text.lower().strip() in ['да', 'нет']:
        if text.lower().strip() == 'нет':
            markup = types.ReplyKeyboardRemove()
            bot.send_message(cid, 'Ок', reply_markup=markup)
        else:
            delete_user_parameters(cid)
            markup = types.ReplyKeyboardRemove()
            bot.send_message(cid,
                             'Бот очистил Ваши текущи параметры \nТеперь дайте новые',
                             reply_markup=markup)

            markup = types.ReplyKeyboardMarkup()
            buttonA = types.KeyboardButton('Мужской')
            buttonB = types.KeyboardButton('Женский')
            buttonC = types.KeyboardButton('Любой')

            markup.row(buttonA, buttonB, buttonC)

            bot.send_message(cid, 'Выберите пол.', reply_markup=markup)
            userStep[cid] = 1
    else:
        bot.send_message(cid,
                         "Кажется, Вы ввели что-то не то О_о \n Повторите")


@bot.message_handler(commands=['report'])
def help_message(message):
    cid = message.chat.id
    text = message.text.strip()
    markup = types.ReplyKeyboardRemove()
    bot.send_message(cid, 'Опишите проблему', reply_markup=markup)
    userStep[cid] = 5


@bot.message_handler(
    func=lambda message: message.chat.id in userStep and userStep[
                                                             message.chat.id] == 5)
def add_report(message):
    cid = message.chat.id
    text = message.text.strip()
    reports = open('reports.txt', 'a')
    reports.write(str(cid) + '\n' +
                  text + '\n\n')
    reports.close()
    bot.send_message(cid, 'Понял. Принял. Обработал')


if __name__ == '__main__':
    bot.polling(none_stop=True)