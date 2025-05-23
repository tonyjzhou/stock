#!/usr/bin/env python3
import asyncio
import logging
import csv
import argparse
import os

import aiosqlite

# Set up basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class DatabaseManager:
    def __init__(self, db_path="test.db", lock=None):
        self.db_path = db_path
        self.conn = None
        self.lock = lock or asyncio.Lock()

    async def __aenter__(self):
        try:
            self.conn = await aiosqlite.connect(self.db_path)
            await self.create_table()
        except aiosqlite.Error as e:
            logging.error(f"Error connecting to database: {e}")
            raise
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self.conn:
            try:
                await self.conn.close()
            except aiosqlite.Error as e:
                logging.error(f"Error closing database connection: {e}")
                raise

    async def create_table(self):
        try:
            async with self.lock:
                await self.conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS stocks
                    (symbol TEXT PRIMARY KEY, 
                    tested_at DATETIME NOT NULL)
                """
                )
                await self.conn.commit()
        except aiosqlite.Error as e:
            logging.error(f"Error creating table: {e}")
            raise

    async def insert_data(self, symbol, tested_at):
        try:
            async with self.lock:
                await self.conn.execute(
                    "INSERT INTO stocks VALUES (?, ?)", (symbol, tested_at)
                )
                await self.conn.commit()
        except aiosqlite.IntegrityError:
            logging.warning(f"Record with symbol {symbol} already exists.")
        except aiosqlite.Error as e:
            logging.error(f"Error inserting data: {e}")
            raise

    async def update_data(self, symbol, tested_at):
        try:
            async with self.lock:
                await self.conn.execute(
                    "UPDATE stocks SET tested_at = ? WHERE symbol = ?",
                    (tested_at, symbol),
                )
                await self.conn.commit()
        except aiosqlite.Error as e:
            logging.error(f"Error updating data: {e}")
            raise

    async def delete_data(self, symbol):
        try:
            async with self.lock:
                await self.conn.execute(
                    "DELETE FROM stocks WHERE symbol = ?", (symbol,)
                )
                await self.conn.commit()
                logging.info(f"Deleted {symbol}")
        except aiosqlite.Error as e:
            logging.error(f"Error deleting data: {e}")
            raise

    async def read_data(self, symbol=None):
        try:
            cursor = await self.conn.cursor()
            if symbol:
                await cursor.execute("SELECT * FROM stocks WHERE symbol = ?", (symbol,))
            else:
                await cursor.execute("SELECT * FROM stocks")
            rows = await cursor.fetchall()
            return rows
        except aiosqlite.Error as e:
            logging.error(f"Error reading data: {e}")
            raise

    @classmethod
    async def refresh(cls, csv_file="Results.csv", db_path="test.db"):
        # Expand user path (e.g., ~/Downloads/Results.csv -> /Users/username/Downloads/Results.csv)
        csv_file = os.path.expanduser(csv_file)

        async with cls(db_path) as db:
            with open(csv_file, newline="", encoding="utf-8-sig") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    symbol = row["Symbol"].strip()
                    await db.delete_data(symbol)


async def test_run():
    async with DatabaseManager("test.db") as db:
        await db.insert_data("AAPL", "2023-12-22")
        logging.info(await db.read_data("AAPL"))
        await db.update_data("AAPL", "2023-12-23")
        logging.info(await db.read_data("AAPL"))
        await db.delete_data("AAPL")
        logging.info(await db.read_data())


def parse_args():
    parser = argparse.ArgumentParser(
        description="Database management for stock symbols."
    )
    parser.add_argument(
        "-c",
        "--csv-file",
        default="Results.csv",
        help="Path to the input CSV file (default: Results.csv)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    asyncio.run(DatabaseManager.refresh(args.csv_file))


if __name__ == "__main__":
    main()
