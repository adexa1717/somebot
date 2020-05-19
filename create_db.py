import sqlite3

conn = sqlite3.connect('db.db')
c = conn.cursor()
# Создание таблицы

sql = '''
    create table users (
    id integer primary key, 
    personal_id integer, 
    user_name varchar, 
    first_name varchar, 
    last_name varchar,
    wallet_cash varchar,
    created datetime
    )'''

sql1 = '''
    create table incomes (
    id integer primary key, 
    user_id integer,
    income_name varchar,
    income_cash integer,
    created datetime
    )'''

sql2 = '''
    create table expenses (
    id integer primary key, 
    user_id integer,    
    expenses_comm varchar,
    expenses_cash varchar,
    created datetime
    )'''

c.execute(sql)
c.execute(sql1)
c.execute(sql2)
# Сохранение (commit) изменений
conn.commit()
# Закрытие курсора, в случае если он больше не нужен
c.close()
