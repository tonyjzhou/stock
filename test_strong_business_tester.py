import unittest


def format_table_markdown(data):
    if not data:
        return ""

    # Get headers from the first dictionary
    headers = list(data[0].keys())

    # Create header row
    header_row = "| " + " | ".join(headers) + " |"

    # Create separator row
    separator_row = "| " + " | ".join(["---" for _ in headers]) + " |"

    # Create data rows
    data_rows = []
    for row in data:
        data_rows.append(
            "| " + " | ".join(str(row[header]) for header in headers) + " |"
        )

    # Combine all rows
    return "\n".join([header_row, separator_row] + data_rows)


class TestMarkdownTableFormatting(unittest.TestCase):
    def test_empty_data(self):
        data = []
        result = format_table_markdown(data)
        self.assertEqual(result, "")

    def test_single_row(self):
        data = [{"Symbol": "AAPL", "ROE": 25.5, "Volatility": 35.2}]
        expected = (
            "| Symbol | ROE | Volatility |\n"
            "| --- | --- | --- |\n"
            "| AAPL | 25.5 | 35.2 |"
        )
        result = format_table_markdown(data)
        self.assertEqual(result, expected)

    def test_multiple_rows(self):
        data = [
            {"Symbol": "AAPL", "ROE": 25.5, "Volatility": 35.2},
            {"Symbol": "GOOGL", "ROE": 20.1, "Volatility": 30.5},
        ]
        expected = (
            "| Symbol | ROE | Volatility |\n"
            "| --- | --- | --- |\n"
            "| AAPL | 25.5 | 35.2 |\n"
            "| GOOGL | 20.1 | 30.5 |"
        )
        result = format_table_markdown(data)
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
