import unittest
from unittest.mock import MagicMock, patch
from application_controller import ApplicationController
from application_dao import ApplicationDAO
from sql_helper import sql_helper


class TestApplicationController(unittest.TestCase):
    def setUp(self):
        self.dao = MagicMock(spec=ApplicationDAO)
        self.controller = ApplicationController()
        self.controller.application = self.dao

    def test_get_salary_trends_valid_user(self):
        self.dao.get_salary_by_company.return_value = [("Google", 120000), ("Meta", 130000)]
        response = self.controller.get_salary_trends("test@example.com")
        self.assertEqual(response.json, [
            {"company": "Google", "salary": 120000},
            {"company": "Meta", "salary": 130000},
        ])
        self.dao.get_salary_by_company.assert_called_once_with("test@example.com")

    def test_get_salary_trends_no_data(self):
        self.dao.get_salary_by_company.return_value = []
        response = self.controller.get_salary_trends("test@example.com")
        self.assertEqual(response.json, [])

    def test_get_salary_trends_invalid_email(self):
        self.dao.get_salary_by_company.side_effect = Exception("Invalid email")
        response = self.controller.get_salary_trends("invalid")
        self.assertIn("error", response.json)

    def test_delete_application_success(self):
        self.dao.delete_application.return_value = True
        result = self.controller.delete(1)
        self.assertTrue(result)

    def test_delete_application_failure(self):
        self.dao.delete_application.return_value = False
        result = self.controller.delete(999)
        self.assertFalse(result)

    @patch("application_controller.jsonify")
    def test_format_salary_trends(self, mock_jsonify):
        self.dao.get_salary_by_company.return_value = [("Google", 120000)]
        self.controller.get_salary_trends("test@example.com")
        mock_jsonify.assert_called_with([{"company": "Google", "salary": 120000}])

    def test_salary_graph_template(self):
        with patch("home.render_template") as mock_render_template:
            from home import salary_graph
            salary_graph()
            mock_render_template.assert_called_with("analytics.html")


class TestApplicationDAO(unittest.TestCase):
    def setUp(self):
        self.dao = ApplicationDAO()
        self.dao.__db = MagicMock(spec=sql_helper)

    def test_get_salary_by_company_valid_user(self):
        self.dao.__db.run_query.return_value = [("Google", 120000)]
        result = self.dao.get_salary_by_company("test@example.com")
        self.assertEqual(result, [("Google", 120000)])
        self.dao.__db.run_query.assert_called_once()

    def test_get_salary_by_company_no_data(self):
        self.dao.__db.run_query.return_value = []
        result = self.dao.get_salary_by_company("unknown@example.com")
        self.assertEqual(result, [])

    def test_get_salary_by_company_invalid_query(self):
        self.dao.__db.run_query.side_effect = Exception("SQL Error")
        with self.assertRaises(Exception):
            self.dao.get_salary_by_company("invalid@example.com")


class TestSQLHelper(unittest.TestCase):
    def setUp(self):
        self.sql = sql_helper()

    @patch("pymysql.connect")
    def test_connect_database_success(self, mock_connect):
        self.sql.connect_database()
        mock_connect.assert_called_once()

    @patch("pymysql.connect")
    def test_connect_database_failure(self, mock_connect):
        mock_connect.side_effect = Exception("Connection Error")
        with self.assertRaises(Exception):
            self.sql.connect_database()

    @patch("pymysql.connect")
    def test_run_query_valid_query(self, mock_connect):
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [("Google", 120000)]
        result = self.sql.run_query("SELECT * FROM company")
        self.assertEqual(result, [("Google", 120000)])

    @patch("pymysql.connect")
    def test_run_query_invalid_query(self, mock_connect):
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("SQL Error")
        mock_connect.return_value.cursor.return_value = mock_cursor
        result = self.sql.run_query("INVALID QUERY")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
