import sqlite3
import datetime
import pytz


def _get_now_formatted() -> str:
    """Возвращает сегодняшнюю дату строкой"""
    return _get_now_datetime().strftime("%Y-%m-%d %H:%M:%S")


def _get_now_datetime() -> datetime.datetime:
    """Возвращает сегодняшний datetime с учётом времненной зоны Алматы"""
    tz = pytz.timezone("Asia/Almaty")
    now = datetime.datetime.now(tz)
    return now


def create_user(personal_id, user_name, first_name, last_name, date_time):
    """создание пользователя"""
    conn = sqlite3.connect('db.db')
    c = conn.cursor()
    c.execute("""insert into users(personal_id, user_name, first_name, last_name, created) values(?, ?, ?, ?, ?)""",
              [personal_id, user_name, first_name, last_name, date_time])
    conn.commit()
    c.close()


def update_user_wallet(personal_id, value):
    """Обновляет кошелек"""
    conn = sqlite3.connect('db.db')
    c = conn.cursor()
    c.execute("""Update users set wallet_cash = ? where personal_id = ?""", [value, personal_id])
    conn.commit()
    c.close()


def find_user_col(personal_id, col):
    """Возвращает конкретный столбец пользователя"""
    conn = sqlite3.connect('db.db')
    c = conn.cursor()
    c.execute(f"SELECT {col} FROM users WHERE personal_id = '{personal_id}'")
    result = c.fetchone()
    return result[0]


def find_user(personal_id):
    """Находит пользователя по его id и возвращает пользователя заранее преобразовав в строку"""
    conn = sqlite3.connect('db.db')
    c = conn.cursor()
    c.execute(f"SELECT * FROM users WHERE personal_id = '{personal_id}'")
    find_arr = c.fetchone()
    if find_arr is None:
        result = None
    else:
        result = ','.join(map(str, find_arr))
    return result


def create_income(personal_id, name, cash, date_time):
    """создание нового дохода"""
    conn = sqlite3.connect('db.db')
    c = conn.cursor()
    c.execute("""insert into incomes(user_id, income_name, income_cash, created) values(?, ?, ?, ?)""",
              [personal_id, name, cash, date_time])
    conn.commit()
    c.execute(f"SELECT * FROM incomes WHERE user_id = '{personal_id}'")
    find_arr = c.fetchone()
    result = ','.join(map(str, find_arr))
    c.close()
    return result


def create_expense(personal_id, cash, comm, date_time):
    """создание нового расхода"""
    conn = sqlite3.connect('db.db')
    c = conn.cursor()
    c.execute("""insert into expenses(user_id, expenses_comm, expenses_cash, created) values(?, ?, ?, ?)""",
              [personal_id, comm, cash, date_time])
    conn.commit()
    c.execute(f"SELECT * FROM expenses WHERE user_id = '{personal_id}'")
    find_arr = c.fetchone()
    result = ','.join(map(str, find_arr))
    c.close()
    return result


def select_table_where_desc(table, personal_id, col, cols='*'):
    conn = sqlite3.connect('db.db')
    c = conn.cursor()
    c.execute(f"SELECT {cols} FROM {table} WHERE {col} = '{personal_id}' ORDER BY created DESC LIMIT 10")
    return c.fetchall()


def select_table_where_asc(table, personal_id, col, cols='*'):
    conn = sqlite3.connect('db.db')
    c = conn.cursor()
    c.execute(f"SELECT {cols} FROM {table} WHERE {col} = '{personal_id}' ORDER BY created ASC")
    return c.fetchall()


def today_report(personal_id):
    conn = sqlite3.connect('db.db')
    c = conn.cursor()
    c.execute(f"select sum(expenses_cash)"
              "from expenses where date(created)=date('now', 'localtime')"
              f"and user_id = '{personal_id}'")
    result1 = c.fetchone()
    c.execute(f"select sum(income_cash)"
              "from incomes where date(created)=date('now', 'localtime')"
              f"and user_id = '{personal_id}'")
    result2 = c.fetchone()
    if not result1[0] and not result2[0]:
        return "Сегодня ещё нет записей"

    today_incomes = result2[0]
    today_expenses = result1[0]
    if today_expenses is None:
        today_expenses = 0
    if today_incomes is None:
        today_incomes = 0
    wall = find_user_col(personal_id, 'wallet_cash')
    return (f"Отчет за сегодня:\n"
            f"доход — {today_incomes} \n"
            f"рассход — {today_expenses}\n"
            f"остаток в кошельке — {wall} ")


def last_month_report(personal_id):
    conn = sqlite3.connect('db.db')
    c = conn.cursor()
    date = f'{(_get_now_datetime() + datetime.timedelta(days=-30)).date()}'
    c.execute(f"select sum(expenses_cash)"
              f"from expenses where date(created)>={date}"
              f" and user_id = '{personal_id}'")
    result1 = c.fetchone()
    c.execute(f"select sum(income_cash)"
              f"from incomes where date(created)>={date}"
              f" and user_id = '{personal_id}'")
    result2 = c.fetchone()
    if not result1[0] and not result2[0]:
        return "Нет записей за последние 30 дней"

    today_incomes = result2[0]
    today_expenses = result1[0]
    if today_expenses is None:
        today_expenses = 0
    if today_incomes is None:
        today_incomes = 0
    wall = find_user_col(personal_id, 'wallet_cash')
    return (f"Отчет за последние 30 дней:\n"
            f"доход — {today_incomes} \n"
            f"рассход — {today_expenses}\n"
            f"остаток в кошельке — {wall} ")


def this_month_report(personal_id):
    conn = sqlite3.connect('db.db')
    c = conn.cursor()
    date = f'{_get_now_datetime().year}-{_get_now_datetime().month}-1'
    c.execute(f"select sum(expenses_cash)"
              f"from expenses where date(created)>={date}"
              f" and user_id = '{personal_id}'")
    result1 = c.fetchone()
    c.execute(f"select sum(income_cash)"
              f"from incomes where date(created)>={date}"
              f" and user_id = '{personal_id}'")
    result2 = c.fetchone()
    if not result1[0] and not result2[0]:
        return "Нет записей за последний месяц"

    today_incomes = result2[0]
    today_expenses = result1[0]
    if today_expenses is None:
        today_expenses = 0
    if today_incomes is None:
        today_incomes = 0
    wall = find_user_col(personal_id, 'wallet_cash')
    return (f"Отчет за последний месяц:\n"
            f"доход — {today_incomes} \n"
            f"рассход — {today_expenses}\n"
            f"остаток в кошельке — {wall} ")



# print(today_report(520536857))

# def get_month_statistics() -> str:
#     """Возвращает строкой статистику расходов за текущий месяц"""
#     now = _get_now_datetime()
#     first_day_of_month = f'{now.year:04d}-{now.month:02d}-01'
#     cursor = db.get_cursor()
#     cursor.execute(f"select sum(amount) "
#                    f"from expense where date(created) >= '{first_day_of_month}'")
#     result = cursor.fetchone()
#     if not result[0]:
#         return "В этом месяце ещё нет расходов"
#     all_today_expenses = result[0]
#     cursor.execute(f"select sum(amount) "
#                    f"from expense where date(created) >= '{first_day_of_month}' "
#                    f"and category_codename in (select codename "
#                    f"from category where is_base_expense=true)")
#     result = cursor.fetchone()
#     base_today_expenses = result[0] if result[0] else 0
#     return (f"Расходы в текущем месяце:\n"
#             f"всего — {all_today_expenses} руб.\n"
#             f"базовые — {base_today_expenses} руб. из "
#             f"{now.day * _get_budget_limit()} руб.")
