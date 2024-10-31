import unittest
from unittest.mock import patch, MagicMock
import os 
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from Controller.email_framework import (s_email, send_registration_email, 
                         status_change_email, password_reset_email, 
                         successful_reset_email)


class TestEmailService(unittest.TestCase):

    @patch('smtplib.SMTP_SSL')
    def test_application_email_success(self, mock_smtp):
        """Test successful application email sending"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = s_email(
            company_name="Google",
            location="Mountain View",
            job_Profile="Software Engineer",
            salary="120000",
            email="test@example.com",
            status="Applied"
        )
        
        self.assertTrue(result)
        mock_server.login.assert_called_once()
        mock_server.sendmail.assert_called_once()

    @patch('smtplib.SMTP_SSL')
    def test_registration_email_success(self, mock_smtp):
        """Test successful registration email sending"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = send_registration_email(
            name="John Doe",
            email="test@example.com"
        )
        
        self.assertTrue(result)
        mock_server.login.assert_called_once()
        mock_server.sendmail.assert_called_once()

    @patch('smtplib.SMTP_SSL')
    def test_status_change_email_success(self, mock_smtp):
        """Test successful status change email sending"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = status_change_email(
            application_id="123",
            email="test@example.com",
            status="Interview Scheduled"
        )
        
        self.assertTrue(result)
        mock_server.login.assert_called_once()
        mock_server.sendmail.assert_called_once()

    @patch('smtplib.SMTP_SSL')
    def test_password_reset_email_success(self, mock_smtp):
        """Test successful password reset email sending"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = password_reset_email(
            email="test@example.com",
            code="123456"
        )
        
        self.assertTrue(result)
        mock_server.login.assert_called_once()
        mock_server.sendmail.assert_called_once()

    @patch('smtplib.SMTP_SSL')
    def test_successful_reset_email_success(self, mock_smtp):
        """Test successful password reset confirmation email"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = successful_reset_email(
            email="test@example.com"
        )
        
        self.assertTrue(result)
        mock_server.login.assert_called_once()
        mock_server.sendmail.assert_called_once()

    @patch('smtplib.SMTP_SSL')
    def test_email_with_invalid_credentials(self, mock_smtp):
        """Test email sending with invalid SMTP credentials"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        mock_server.login.side_effect = Exception("Invalid credentials")
        
        with self.assertRaises(Exception):
            s_email(
                company_name="Google",
                location="Mountain View",
                job_Profile="Software Engineer",
                salary="120000",
                email="test@example.com",
                status="Applied"
            )

    @patch('smtplib.SMTP_SSL')
    def test_email_with_connection_error(self, mock_smtp):
        """Test email sending with SMTP connection error"""
        mock_smtp.side_effect = Exception("Connection refused")
        
        with self.assertRaises(Exception):
            send_registration_email(
                name="John Doe",
                email="test@example.com"
            )

    @patch('smtplib.SMTP_SSL')
    def test_email_with_invalid_recipient(self, mock_smtp):
        """Test email sending with invalid recipient address"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        mock_server.sendmail.side_effect = Exception("Invalid recipient")
        
        with self.assertRaises(Exception):
            status_change_email(
                application_id="123",
                email="invalid@email",
                status="Interview Scheduled"
            )
    @patch('smtplib.SMTP_SSL')
    def test_email_with_empty_fields(self, mock_smtp):
        """Test email sending with empty required fields"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = s_email(
            company_name="",
            location="",
            job_Profile="",
            salary="",
            email="test@example.com",
            status=""
        )

        self.assertTrue(result)
        mock_server.sendmail.assert_called_once()

    @patch('smtplib.SMTP_SSL')
    def test_multiple_emails_sequence(self, mock_smtp):
        """Test sending multiple emails in sequence"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result1 = s_email(
            company_name="Google",
            location="Mountain View",
            job_Profile="Software Engineer",
            salary="120000",
            email="test@example.com",
            status="Applied"
        )
        
        result2 = status_change_email(
            application_id="123",
            email="test@example.com",
            status="Interview Scheduled"
        )
        
        self.assertTrue(result1)
        self.assertTrue(result2)
        self.assertEqual(mock_server.sendmail.call_count, 2)

    @patch('smtplib.SMTP_SSL')
    def test_email_with_special_characters(self, mock_smtp):
        """Test email sending with special characters in fields"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = s_email(
            company_name="Company@#$%",
            location="City!@#",
            job_Profile="Engineer&*()",
            salary="100,000$",
            email="test@example.com",
            status="Applied!"
        )
        
        self.assertTrue(result)
        mock_server.sendmail.assert_called_once()

    @patch('smtplib.SMTP_SSL')
    def test_email_with_very_long_input(self, mock_smtp):
        """Test email sending with very long input fields"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        long_text = "a" * 1000 
        
        result = s_email(
            company_name=long_text,
            location=long_text,
            job_Profile=long_text,
            salary=long_text,
            email="test@example.com",
            status=long_text
        )
        
        self.assertTrue(result)
        mock_server.sendmail.assert_called_once()
    
    @patch('smtplib.SMTP_SSL')
    def test_registration_email_with_special_chars_name(self, mock_smtp):
        """Test registration email with special characters in name"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = send_registration_email(
            name="John@#$% Doe!@#",
            email="test@example.com"
        )
        
        self.assertTrue(result)
        mock_server.sendmail.assert_called_once()

    @patch('smtplib.SMTP_SSL')
    def test_status_change_with_multiple_statuses(self, mock_smtp):
        """Test status change email with different status values"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        statuses = ["Applied", "In Review", "Interview Scheduled", 
                   "Offer Extended", "Rejected", "Accepted"]
        
        for status in statuses:
            result = status_change_email(
                application_id="123",
                email="test@example.com",
                status=status
            )
            self.assertTrue(result)
        
        self.assertEqual(mock_server.sendmail.call_count, len(statuses))

    @patch('smtplib.SMTP_SSL')
    def test_password_reset_with_different_codes(self, mock_smtp):
        """Test password reset email with different code formats"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        test_codes = ["123456", "ABCDEF", "A1B2C3", "!@#$%^"]
        
        for code in test_codes:
            result = password_reset_email(
                email="test@example.com",
                code=code
            )
            self.assertTrue(result)
        
        self.assertEqual(mock_server.sendmail.call_count, len(test_codes))

    @patch('smtplib.SMTP_SSL')
    def test_email_with_unicode_characters(self, mock_smtp):
        """Test email sending with unicode characters"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = s_email(
            company_name="公司名称",  
            location="München",  
            job_Profile="インジニア",  
            salary="₹100,000",    
            email="test@example.com",
            status="Applied"
        )
        
        self.assertTrue(result)
        mock_server.sendmail.assert_called_once()


if __name__ == '__main__':
    unittest.main()