import sqlite3
from datetime import datetime


def create_table():
    with sqlite3.connect('test.db') as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS stocks
            (symbol TEXT PRIMARY KEY, 
            tested_at DATETIME NOT NULL)
        ''')


def insert_data(symbol, tested_at):
    with sqlite3.connect('test.db') as conn:
        c = conn.cursor()
        c.execute("INSERT INTO stocks VALUES (?, ?)", (symbol, tested_at))


def update_data(symbol, tested_at):
    with sqlite3.connect('test.db') as conn:
        c = conn.cursor()
        c.execute("UPDATE stocks SET tested_at = ? WHERE symbol = ?", (tested_at, symbol))


def delete_data(symbol):
    with sqlite3.connect('test.db') as conn:
        print(f"Deleting {symbol} from database ...")
        c = conn.cursor()
        c.execute("DELETE from stocks WHERE symbol = ?", (symbol,))


def read_data(symbol=None):
    with sqlite3.connect('test.db') as conn:
        c = conn.cursor()
        if symbol:
            c.execute("SELECT * FROM stocks WHERE symbol=?", (symbol,))
        else:
            c.execute("SELECT * FROM stocks")
        rows = c.fetchall()
    return rows


def main():
    with open("tickers.txt", "r") as file:
        for line in file:
            symbol = line.strip()
            delete_data(symbol)


def simple_test():
    create_table()
    insert_data('AAPL', datetime.now())
    print(read_data('AAPL'))  # Prints: [('AAPL', '2023-06-13')]
    update_data('AAPL', datetime.now())
    print(read_data('AAPL'))  # Prints: [('AAPL', '2023-06-14')]
    delete_data('AAPL')
    print(read_data())  # Prints: []


if __name__ == '__main__':
    main()
