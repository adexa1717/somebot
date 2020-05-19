from telebot import TeleBot
from telebot import types
from db import *
from datetime import datetime

TOKEN = '1054947562:AAHGY_zF9uRzI7HKlVIAYHFm7_V3BfIhbh8'
base_url = f'https://api.telegram.org/bot{TOKEN}/'

bot = TeleBot(TOKEN)

incomes = {}
expenses = {}


class Expense:
    def __init__(self, user_id, cash):
        self.user_id = user_id
        self.cash = cash
        self.comm = None

    def save(self):
        create_expense(self.user_id, self.cash, self.comm, datetime.now())


class Income:
    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
        self.cash = None

    def save(self):
        create_income(self.user_id, self.name, self.cash, datetime.now())


@bot.message_handler(commands='start')
def create_isnone(message: types.Message):
    if find_user(message.from_user.id) is None:
        create_user(message.from_user.id, message.from_user.username, message.from_user.first_name,
                    message.from_user.last_name, datetime.now())
        bot.send_message(message.chat.id, f"Добро ожаловать, {message.from_user.first_name}!")
    else:
        pass


@bot.message_handler(commands='add_income')
def add_income(message: types.Message):
    msg = bot.send_message(message.chat.id, "Введите название дохода")
    bot.register_next_step_handler(msg, income_name_step)


def income_name_step(message: types.Message):
    try:
        chat_id = message.chat.id
        print(chat_id)
        user_id = message.from_user.id
        income_name = message.text
        income = Income(user_id, income_name)
        print(income)
        incomes[chat_id] = income
        msg = bot.send_message(message.chat.id, "Введите сумму дохода")
        bot.register_next_step_handler(msg, income_cash_step)
    except Exception as e:
        bot.send_message(message.chat.id, "Ууупс, что-то пошло не так")


def income_cash_step(message: types.Message):
    try:
        chat_id = message.chat.id
        cash = message.text
        if not cash.isdigit():
            msg = bot.send_message(chat_id, "Сумма дохода должна быть числом")
            bot.register_next_step_handler(msg, income_cash_step)
        income = incomes[chat_id]
        income.cash = cash
        income.save()
        wallet = find_user_col(message.from_user.id, 'wallet_cash')
        if wallet is None:
            new_wallet = int(cash)
        else:
            new_wallet = int(wallet) + int(cash)
        update_user_wallet(message.from_user.id, new_wallet)
        bot.send_message(message.chat.id, f"Добавлен доход {income.name} суммой {income.cash}")
        bot.send_message(message.chat.id, f"Остаток в кошельке {new_wallet}")

    except Exception as e:
        bot.send_message(message.chat.id, "Ууупс, что-то пошло не так")


@bot.message_handler(commands='add_expense')
def add_expense(message: types.Message):
    msg = bot.send_message(message.chat.id, "Введите сумму рассхода")
    bot.register_next_step_handler(msg, expense_cash_step)


def expense_cash_step(message: types.Message):
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id
        cash = message.text
        if not cash.isdigit():
            msg = bot.send_message(chat_id, "Сумма рассхода должна быть числом")
            bot.register_next_step_handler(msg, expense_cash_step)
        expense = Expense(user_id, cash)
        expenses[chat_id] = expense
        msg = bot.send_message(chat_id, "Добавьте комментарий")
        bot.register_next_step_handler(msg, expense_comm_step)

    except Exception as e:
        bot.send_message(message.chat.id, "Ууупс, что-то пошло не так")


def expense_comm_step(message: types.Message):
    try:
        chat_id = message.chat.id
        comm = message.text
        expense = expenses[chat_id]
        expense.comm = comm
        cash = expense.cash
        expense.save()
        wallet = find_user_col(message.from_user.id, 'wallet_cash')
        if wallet is None:
            new_wallet = -int(cash)
        else:
            new_wallet = int(wallet) - int(cash)
        update_user_wallet(message.from_user.id, new_wallet)
        bot.send_message(message.chat.id, f"Добавлен рассход {expense.comm} суммой {expense.cash}")
        bot.send_message(message.chat.id, f"Остаток в кошельке {new_wallet}")

    except Exception as e:
        bot.send_message(message.chat.id, "Ууупс, что-то пошло не так")


@bot.message_handler(commands='wallet')
def wallet(message: types.Message):
    wall = find_user_col(message.from_user.id, 'wallet_cash')
    bot.send_message(message.chat.id, wall)


@bot.message_handler(commands='expenses')
def show_expenses(message: types.Message):
    user_expenses = select_table_where_desc('expenses', message.from_user.id, 'user_id', 'expenses_comm, expenses_cash')
    bot.send_message(message.chat.id, 'Последние 10 расходов')
    for ms in user_expenses:
        bot.send_message(message.chat.id, f'Рассход суммой {ms[1]} и комментарием "{ms[0]}"')


@bot.message_handler(commands='incomes')
def show_incomes(message: types.Message):
    user_incomes = select_table_where_desc('incomes', message.from_user.id, 'user_id', 'income_name, income_cash')
    bot.send_message(message.chat.id, 'Последние 10 доходов')
    for ms in user_incomes:
        bot.send_message(message.chat.id, f'Доход "{ms[0]}" суммой {ms[1]}')


@bot.message_handler(commands='last_month')
def last_month(message: types.Message):
    bot.send_message(message.chat.id, last_month_report(message.from_user.id))


@bot.message_handler(commands='this_month')
def this_month(message: types.Message):
    bot.send_message(message.chat.id, this_month_report(message.from_user.id))


@bot.message_handler(commands='today')
def today(message: types.Message):
    bot.send_message(message.chat.id, today_report(message.from_user.id))


@bot.message_handler(func=lambda m: True)
def echo_all(message: types.Message):
    bot.send_message(message.chat.id, 'Введите корректную команду')


bot.polling()
