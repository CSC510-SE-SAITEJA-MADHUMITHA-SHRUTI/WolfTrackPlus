import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def s_email(
    company_name,
    location,
    job_Profile,
    salary,
    username,
    password,
    email,
    security_question,
    security_answer,
    notes,
    date_applied,
    status,
):
    """
    Send an email to notify the user.

    :param company_name: Company name of the application
    :param location: location of the application
    :param Job_Profile: Application job profile
    :param email: email of the user
    :return: returns one if the email was sent successfully returns zero if it was failed
    """
    sender_email = "wolftrackproject@gmail.com"
    receiver_email = email
    password = "dlafyfekdkmdfjdi"

    subject = "WolfTrack++ - Job Application Added"
    body = (
        f"WOLFTRACK++ APPLICATION\n\n"
        f"You have applied to {company_name} for the job profile - {job_Profile}.\n"
        f"Location: {location}\n"
        f"Salary: {salary}\n"
        f"Status: {status}\n\n"
        f"All the best for your application!\n"
        f"The WolfTrack++ Team."
    )
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email

    message.attach(MIMEText(body, "plain"))

    text = message.as_string()

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)

    return True

import pyotp

def send_otp_email(email, secret=None):
    """
    Generates an OTP and sends it to the user's email.
    :param email: Email address to send the OTP to.
    :param secret: (Optional) Unique secret for the user. If None, generates a new one.
    :return: True if the email was sent successfully, otherwise False.
    """
    # Generate OTP
    if secret is None:
        secret = pyotp.random_base32()  # Generate a new secret if not provided
    totp = pyotp.TOTP(secret)
    otp = totp.now()  # Generate the OTP

    # Prepare email details
    sender_email = "wolftrackproject@gmail.com"
    receiver_email = email
    password = "dlafyfekdkmdfjdi"
    subject = "Your WolfTrack++ Login OTP"
    body = (
        f"Hello,\n\n"
        f"Your OTP for logging into WolfTrack++ is: {otp}\n\n"
        f"This OTP is valid for 30 seconds.\n\n"
        f"Regards,\nThe WolfTrack++ Team"
    )

    # Create email message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    # Send the email
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print(f"OTP sent to {email}")
        return True, secret  # Return the secret for storing
    except Exception as e:
        print(f"Failed to send OTP email: {e}")
        return False, None



# New function to send registration email
def send_registration_email(name, email):
    """
    Send a registration email to the user.

    :param name: Name of the user
    :param email: Email address of the user
    :return: Returns True if the email was sent successfully, False otherwise
    """
    sender_email = "wolftrackproject@gmail.com"  # Replace with your email address
    receiver_email = email
    password = "dlafyfekdkmdfjdi"  # Replace with your email password

    subject = "Welcome to WolfTrack++ - Registration Successful"
    body = (
        f"Hello {name},\n\n"
        "Thank you for registering with WolfTrack!\n"
        "WolfTrack is a job application tracking system designed to help users efficiently manage and organize their job application process."
        "We are excited to have you on board.\n\n"
        "Best regards,\n"
        "WolfTrack"
    )

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email

    message.attach(MIMEText(body, "plain"))

    text = message.as_string()

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)

    return True

    


def status_change_email(application_id, email, status):

    sender_email = "wolftrackproject@gmail.com"
    receiver_email = email
    password = "dlafyfekdkmdfjdi"

    subject = "WolfTrack++ - Status Update"
    body = (
        "WOLFTRACK++ APPLICATION UPDATE \n\n"
        "The status has been changed to "
        + status
        + " for the job id - "
        + application_id
        + "\n\n"
        "Please reply back to this mail if you have any queries!\n"
        "The WolfTrack++ Team."
    )
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email

    message.attach(MIMEText(body, "plain"))

    text = message.as_string()

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)

    return True

def password_reset_email(email, code):

    sender_email = "wolftrackproject@gmail.com"
    receiver_email = email
    password = "dlafyfekdkmdfjdi"

    subject = "WolfTrack++ - Password Reset"
    body = (
        "WOLFTRACK++ PASSWORD RESET CODE \n\n"
        "The code to reset your password is: "
        + str(code)
        + "\n\n"
        + "Get back to the application and enter the code to reset your password"
        + "\n\n"
        "Please reply back to this mail if you have any queries!\n"
        "The WolfTrack++ Team."
    )
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email

    message.attach(MIMEText(body, "plain"))

    text = message.as_string()

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)

    return True

def successful_reset_email(email):

    sender_email = "wolftrackproject@gmail.com"
    receiver_email = email
    password = "dlafyfekdkmdfjdi"

    subject = "WolfTrack++ - Password has been reset"
    body = (
        "WOLFTRACK++ PASSWORD RESET DONE \n\n"
        "Your password has been successfully reset."
        + "\n\n"
        + "Now you can log in to your account using your new password."
        + "\n\n"
        "Please reply back to this mail if you have any queries!\n"
        "The WolfTrack++ Team."
    )
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email

    message.attach(MIMEText(body, "plain"))

    text = message.as_string()

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)

    return True


if __name__ == "__main__":
    status_change_email("1", "slabba@ncsu.edu", "In Review")
