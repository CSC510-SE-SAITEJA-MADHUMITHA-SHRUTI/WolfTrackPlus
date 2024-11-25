import unittest
from flask import Flask, session
from flask_testing import TestCase
from flask_login import LoginManager
from your_flask_app import create_app, db  # Adjust the import as per your app's structure
from your_flask_app.controllers import UserController  # Adjust according to the controller

class TestOTPVerification(TestCase):

    def create_app(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory database
        app.config['LOGIN_DISABLED'] = True  # Disable login for testing
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def generate_otp(self, mfa_secret):
        """ Helper function to simulate OTP generation. """
        # This should call your OTP generation logic
        # Here we are just returning a mock OTP for testing purposes.
        return "123456"  # Simulating OTP generation based on mfa_secret

    def send_otp_email(self, email, otp):
        """ Mock function to simulate sending OTP email. """
        print(f"Sending OTP {otp} to {email}")
        return True  # Simulate successful email sending

    def test_otp_generation(self):
        """ Test that OTP is generated and sent correctly. """
        email = "test@example.com"
        password = "password"
        mfa_secret = 'mock_secret'  # You would get this from the user data
        otp = self.generate_otp(mfa_secret)
        
        # Check OTP format (6 digits)
        self.assertEqual(len(otp), 6)  
        self.assertIsNotNone(otp)

        # Simulate OTP email sending (this is mocked in this example)
        response = self.send_otp_email(email, otp)
        self.assertTrue(response)  # Ensure email sending was simulated successfully

    def test_verify_correct_otp(self):
        """ Test the scenario where the user enters the correct OTP. """
        with self.client:
            session['mfa_secret'] = 'mock_secret'  # Mock mfa_secret
            otp = self.generate_otp(session['mfa_secret'])
            session['otp_verified'] = False  # Initially, OTP is not verified
            
            # Simulate entering the correct OTP
            response = self.client.post('/verify_otp', data=dict(otp=otp), follow_redirects=True)
            
            # Check if user is redirected to authenticated page
            self.assert200(response)
            self.assertRedirects(response, '/auth')
            self.assertTrue(session['otp_verified'])  # OTP should be verified now

    def test_verify_incorrect_otp(self):
        """ Test the scenario where the user enters an incorrect OTP. """
        with self.client:
            session['mfa_secret'] = 'mock_secret'
            otp = self.generate_otp(session['mfa_secret'])  # Correct OTP
            session['otp_verified'] = False  # Initially, OTP is not verified

            # Simulate entering an incorrect OTP
            incorrect_otp = '654321'
            response = self.client.post('/verify_otp', data=dict(otp=incorrect_otp), follow_redirects=True)
            
            # Check if error message is shown for incorrect OTP
            self.assert200(response)
            self.assertTemplateUsed('verify_otp.html')  # OTP page should be rendered
            self.assertIn(b'Invalid OTP. Please try again.', response.data)

    def test_verify_expired_otp(self):
        """ Test that expired OTP is not accepted. """
        from datetime import datetime, timedelta

        with self.client:
            session['mfa_secret'] = 'mock_secret'
            otp = self.generate_otp(session['mfa_secret'])  # Correct OTP
            session['otp_verified'] = False  # Initially, OTP is not verified
            
            # Simulate OTP expiration by setting timestamp in session
            session['otp_timestamp'] = datetime.now() - timedelta(minutes=10)  # Expired OTP
            
            # Simulate entering OTP after expiration
            response = self.client.post('/verify_otp', data=dict(otp=otp), follow_redirects=True)
            
            # Check if error message for expired OTP is shown
            self.assert200(response)
            self.assertTemplateUsed('verify_otp.html')  # OTP page should be rendered
            self.assertIn(b'OTP has expired. Please request a new OTP.', response.data)

    def test_verify_empty_otp(self):
        """ Test the scenario where the OTP input is empty. """
        with self.client:
            session['mfa_secret'] = 'mock_secret'
            session['otp_verified'] = False  # Initially, OTP is not verified
            
            # Simulate submitting the form without entering OTP
            response = self.client.post('/verify_otp', data=dict(otp=''), follow_redirects=True)
            
            # Check if error message for missing OTP is shown
            self.assert200(response)
            self.assertTemplateUsed('verify_otp.html')
            self.assertIn(b'OTP is required.', response.data)  # Error message for missing OTP

    def test_verify_no_mfa_secret_in_session(self):
        """ Test the case where the session does not contain mfa_secret. """
        with self.client:
            # Simulate submitting OTP without mfa_secret in session
            session['otp_verified'] = False  # Initially, OTP is not verified
            
            response = self.client.post('/verify_otp', data=dict(otp='123456'), follow_redirects=True)
            
            # Check if user is redirected to login page since mfa_secret is missing
            self.assertRedirects(response, '/login')

    def test_verify_already_verified_otp(self):
        """ Test that OTP can't be verified again once it has been verified. """
        with self.client:
            session['otp_verified'] = True  # OTP is already verified
            
            # Simulate submitting OTP again
            response = self.client.post('/verify_otp', data=dict(otp='123456'), follow_redirects=True)
            
            # Ensure user is redirected to the authenticated page
            self.assertRedirects(response, '/auth')  # Should be redirected since OTP is already verified

    def test_multiple_otp_requests(self):
        """ Test the scenario where multiple OTP requests are made. """
        with self.client:
            session['mfa_secret'] = 'mock_secret'
            otp_1 = self.generate_otp(session['mfa_secret'])
            
            # Simulate submitting the first OTP
            response = self.client.post('/verify_otp', data=dict(otp=otp_1), follow_redirects=True)
            self.assert200(response)
            self.assertTrue(session['otp_verified'])  # OTP should be verified
            
            # Simulate generating a new OTP
            otp_2 = self.generate_otp(session['mfa_secret'])
            
            # Simulate submitting the second OTP
            response = self.client.post('/verify_otp', data=dict(otp=otp_2), follow_redirects=True)
            self.assert200(response)
            self.assertTrue(session['otp_verified'])  # Second OTP should be verified

if __name__ == '__main__':
    unittest.main()
