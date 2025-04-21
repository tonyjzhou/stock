#!/usr/bin/env python3
import unittest
import asyncio
import os
import csv
from datetime import datetime
from unittest.mock import patch
from database import DatabaseManager, parse_args


class TestDatabaseManager(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.test_db = "test_database.db"
        self.test_csv = "test_tickers.csv"
        # Create a test CSV file
        with open(self.test_csv, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Symbol"])
            writer.writerow(["AAPL"])
            writer.writerow(["GOOGL"])
            writer.writerow(["MSFT"])

    def tearDown(self):
        # Clean up test files
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        if os.path.exists(self.test_csv):
            os.remove(self.test_csv)

    async def test_create_table(self):
        """Test table creation"""
        async with DatabaseManager(self.test_db) as db:
            # Table should be created in __aenter__
            cursor = await db.conn.cursor()
            await cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='stocks'"
            )
            result = await cursor.fetchone()
            self.assertIsNotNone(result)
            self.assertEqual(result[0], "stocks")

    async def test_insert_and_read_data(self):
        """Test inserting and reading data"""
        async with DatabaseManager(self.test_db) as db:
            test_time = datetime.now()
            await db.insert_data("AAPL", test_time)

            # Test reading specific symbol
            rows = await db.read_data("AAPL")
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][0], "AAPL")
            self.assertEqual(
                datetime.strptime(rows[0][1], "%Y-%m-%d %H:%M:%S.%f"), test_time
            )

            # Test reading all symbols
            rows = await db.read_data()
            self.assertEqual(len(rows), 1)

    async def test_update_data(self):
        """Test updating data"""
        async with DatabaseManager(self.test_db) as db:
            initial_time = datetime.now()
            await db.insert_data("AAPL", initial_time)

            update_time = datetime.now()
            await db.update_data("AAPL", update_time)

            rows = await db.read_data("AAPL")
            self.assertEqual(len(rows), 1)
            self.assertEqual(
                datetime.strptime(rows[0][1], "%Y-%m-%d %H:%M:%S.%f"), update_time
            )

    async def test_delete_data(self):
        """Test deleting data"""
        async with DatabaseManager(self.test_db) as db:
            await db.insert_data("AAPL", datetime.now())
            await db.delete_data("AAPL")

            rows = await db.read_data("AAPL")
            self.assertEqual(len(rows), 0)

    async def test_refresh_from_csv(self):
        """Test refreshing database from CSV"""
        # First insert some data
        async with DatabaseManager(self.test_db) as db:
            await db.insert_data("AAPL", datetime.now())
            await db.insert_data("GOOGL", datetime.now())
            await db.insert_data("MSFT", datetime.now())

            # Verify initial data
            rows = await db.read_data()
            self.assertEqual(len(rows), 3)

        # Run refresh
        await asyncio.create_task(DatabaseManager.refresh(self.test_csv, self.test_db))

        # Verify data was deleted
        async with DatabaseManager(self.test_db) as db:
            rows = await db.read_data()
            self.assertEqual(len(rows), 0)

    async def test_duplicate_insert(self):
        """Test handling of duplicate inserts"""
        async with DatabaseManager(self.test_db) as db:
            test_time = datetime.now()
            # First insert should succeed
            await db.insert_data("AAPL", test_time)
            # Second insert should not raise an error
            await db.insert_data("AAPL", test_time)

            # Should still only have one record
            rows = await db.read_data("AAPL")
            self.assertEqual(len(rows), 1)

    def test_parse_args(self):
        """Test command line argument parsing"""
        # Test with -c argument
        with patch("sys.argv", ["database.py", "-c", "~/Downloads/Results.csv"]):
            args = parse_args()
            self.assertEqual(args.csv_file, "~/Downloads/Results.csv")

        # Test with --csv-file argument
        with patch(
            "sys.argv", ["database.py", "--csv-file", "~/Downloads/Results.csv"]
        ):
            args = parse_args()
            self.assertEqual(args.csv_file, "~/Downloads/Results.csv")

        # Test default value
        with patch("sys.argv", ["database.py"]):
            args = parse_args()
            self.assertEqual(args.csv_file, "Results.csv")


if __name__ == "__main__":
    unittest.main()
