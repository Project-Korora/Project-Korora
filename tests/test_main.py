import unittest
from unittest.mock import patch
from src.main import main

class TestMain(unittest.TestCase):
    @patch("builtins.print")
    def test_main_output(self, mock_print):
        main()
        mock_print.assert_called_once_with("Project Kororā")

if __name__ == "__main__":
    unittest.main()
