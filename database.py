import sqlite3


class DatabaseManager:
    def __init__(self, db_path='test.db'):
        self.db_path = db_path
        self.conn = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            self.conn.close()

    def create_table(self):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stocks
                (symbol TEXT PRIMARY KEY, 
                tested_at DATETIME NOT NULL)
            ''')

    def insert_data(self, symbol, tested_at):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO stocks VALUES (?, ?)", (symbol, tested_at))

    def update_data(self, symbol, tested_at):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE stocks SET tested_at = ? WHERE symbol = ?", (tested_at, symbol))

    def delete_data(self, symbol):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("DELETE from stocks WHERE symbol = ?", (symbol,))

    def read_data(self, symbol=None):
        cursor = self.conn.cursor()
        query = "SELECT * FROM stocks"
        if symbol:
            query += " WHERE symbol = ?"
            cursor.execute(query, (symbol,))
        else:
            cursor.execute(query)
        return cursor.fetchall()


def refresh():
    with open("tickers.txt", "r") as file:
        with DatabaseManager('test.db') as db:
            for line in file:
                symbol = line.strip()
                db.delete_data(symbol)


def test_run():
    with DatabaseManager('test.db') as db:
        db.create_table()
        db.insert_data('AAPL', '2023-12-22')
        print(db.read_data('AAPL'))
        db.update_data('AAPL', '2023-12-23')
        print(db.read_data('AAPL'))
        db.delete_data('AAPL')
        print(db.read_data())


def main():
    test_run()


if __name__ == '__main__':
    main()
