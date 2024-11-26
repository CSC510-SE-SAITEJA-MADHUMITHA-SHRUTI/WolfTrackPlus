import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, session
from your_flask_app import create_app  # Replace with your actual app module

class TestVerifyOtpRoute(unittest.TestCase):
    def setUp(self):
        # Create the app and configure it for testing
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SECRET_KEY"] = "test_secret_key"
        self.client = self.app.test_client()

    def test_valid_otp_flow(self):
        with self.client:
            # Set up a session with a valid OTP secret
            with self.client.session_transaction() as sess:
                sess["otp_secret"] = "JBSWY3DPEHPK3PXP"  # Example base32 secret

            # Mock pyotp.TOTP.verify to return True for valid OTP
            with patch("pyotp.TOTP.verify", return_value=True) as mock_verify:
                response = self.client.post("/verify_otp", data={"otp": "123456"})
                self.assertEqual(response.status_code, 302)
                self.assertIn("/auth", response.location)
                self.assertNotIn("otp_secret", session)  # Ensure secret is cleared
                mock_verify.assert_called_once_with("123456")

    def test_invalid_otp_flow(self):
        with self.client:
            # Set up a session with a valid OTP secret
            with self.client.session_transaction() as sess:
                sess["otp_secret"] = "JBSWY3DPEHPK3PXP"  # Example base32 secret

            # Mock pyotp.TOTP.verify to return False for invalid OTP
            with patch("pyotp.TOTP.verify", return_value=False) as mock_verify:
                response = self.client.post("/verify_otp", data={"otp": "654321"})
                self.assertEqual(response.status_code, 200)
                self.assertIn(b"Invalid OTP. Please try again.", response.data)
                mock_verify.assert_called_once_with("654321")

    def test_missing_otp_secret_in_session(self):
        with self.client:
            # Ensure session does not have `otp_secret`
            with self.client.session_transaction() as sess:
                sess.pop("otp_secret", None)

            response = self.client.post("/verify_otp", data={"otp": "123456"})
            self.assertEqual(response.status_code, 302)
            self.assertIn("/login", response.location)

    def test_get_request_renders_otp_page(self):
        with self.client:
            response = self.client.get("/verify_otp")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Enter OTP", response.data)  # Verify the OTP form renders

class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SECRET_KEY"] = "test_secret_key"
        self.client = self.app.test_client()

    def test_login(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Login", response.data)

    def test_auth_redirect_without_session(self):
        response = self.client.get('/auth', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Login", response.data)

    def test_auth_with_session(self):
        with self.client:
            with self.client.session_transaction() as session:
                session['email'] = 'test@example.com'

            response = self.client.get('/auth')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Home", response.data)

    def test_signup(self):
        response = self.client.post('/signup', data={
            'email': 'test@example.com',
            'password': 'password123',
            'name': 'John Doe',
            'location': 'New York',
            'gender': 'Male'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"success", response.data)

if __name__ == "__main__":
    unittest.main()
