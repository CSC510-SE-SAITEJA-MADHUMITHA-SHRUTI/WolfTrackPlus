from datetime import datetime
import json
from sqlite3 import IntegrityError
from flask import Blueprint, flash, session,jsonify,redirect
from flask import Flask, render_template, url_for, request, send_file
from flask_login import login_required, logout_user, login_manager
from werkzeug.utils import redirect
from Controller.user_controller import User
from Controller.application_controller import Application
from Controller.password_reset_controller import PasswordReset
from Controller.email_framework import s_email, send_otp_email , status_change_email, password_reset_email, successful_reset_email, send_registration_email
from Controller.geocoding_helper import get_location_coordinates
from collections import Counter
import requests
import random
import io
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
import os
from datetime import datetime  
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import pandas as pd
import pyotp 
from Controller.user_controller import User
from Controller.email_framework import password_reset_email  # Adjust the module name as needed
from Controller.email_framework import successful_reset_email 
from Controller.email_framework import send_registration_email  # Adjust as necessary
from Controller.email_framework import status_change_email

project_root = Path(__file__).parent.parent

CREDENTIALS_PATH = os.path.join(project_root, 'credentials', 'calendar_cred.json')

SCOPES = ['https://www.googleapis.com/auth/calendar.events']


api_key = '68188bd34eea4250107ae82ee6d61054'
app_id = '394232b1'
adzuna_api_url = 'https://api.adzuna.com/v1/api/jobs/us/search/1'
search_params = {
    'app_id': app_id,
    'app_key': api_key,
    'what': 'software engineer',  # Modify the search parameters
    'where': 'united states',      # Modify the location
    'content-type': 'application/json',
    'results_per_page': 40
}

home_route = Blueprint("home_route", __name__)

user = User()
application = Application()
password_reset = PasswordReset()
# login = login_manager.LoginManager(application)


def fetch_upcoming_events_temp():
    response = requests.get(adzuna_api_url, params=search_params)
    upcoming_events_temp = []
    if response.status_code == 200:
        job_listings = response.json()
        for job in job_listings['results']:
            dic = {}
            dic["title"] = job['title']
            dic["company"] = job['company']['display_name']
            dic["location"] = job['location']['display_name']
            date = job['created']
            year, month, day = datetime.strptime(
                date, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d").split('-')
            combined_date = f"{year}-{month}-{day}"
            dic["date_created"] = combined_date
            salary_max = job.get('salary_max', 'N/A')
            dic["salary"] = "$" + str(salary_max)
            dic['job_url'] = job['redirect_url']
            upcoming_events_temp.append(dic)
    return upcoming_events_temp


@home_route.route("/", methods=["GET"])
def home():
    return redirect("/auth")
@home_route.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html", loginError="")

@home_route.route("/forgot", methods=["GET", "POST"])
def forgot():
    return render_template("forgot.html", loginError="")


@home_route.route("/auth", methods=["GET"])
def auth():
    """
    Redirects to home page after authentication, intercepts the get method.
    """
    if "email" in session:
        data = user.get_auth_user_dao(session["email"])
        data["wishlist"] = application.get(session["email"], "")

        all_job_locations = application.get_job_locations_for_applications(session["email"])
        all_companies = application.get_job_companies_for_applications(session["email"])
        print("all_job_locations",all_job_locations)
        print("all_companies",all_companies)

        # data["wishlist"] is a list of lists, where i[2] is the application_date
        dates = [i[2] for i in data["wishlist"]]
        months = []
        for date_str in dates:
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                month_str = date_obj.strftime('%Y-%m')
                months.append(month_str)
            except ValueError as e:
                print(f"Error parsing date '{date_str}': {e}")

        # Count applications per month
        month_counts = Counter(months)

        # Prepare data for the chart (sorted chronologically)
        sorted_months = sorted(month_counts.keys())
        application_data = [{
            'month': month,
            'application_count': month_counts[month]
        } for month in sorted_months]

        print("Application Data:  ", application_data )

        # Fetch coordinates for each location
        coordinates_list = []
        for location in all_job_locations:
            coordinates = get_location_coordinates(location)
            if coordinates:
                coordinates_list.append(coordinates)

        print("coordinates_list",coordinates_list)

       
        upcoming_events = fetch_upcoming_events_temp()
        return render_template(
            "home.html",
            data=data,
            upcoming_events=upcoming_events,
            all_job_locations=json.dumps(all_job_locations),
            coordinates_list=json.dumps(coordinates_list),
            all_companies=json.dumps(all_companies),
            application_data=application_data
        )
    else:
        return redirect("/login")


@home_route.route("/forgotPassword", methods=["POST"])
def forgotPassword():
    """
    When encountering the /forgotPassword url, this is function is called. it intercepts post requests.
    if received a post request, it checks if the email is valid.
    If the email is valid then the user receives a code page is redirected login page.
    """
    session["email"] = request.form["username"]
    result = user.get_user_existence(session["email"])
    if result == 0:
        error = "Email does not exist. Please enter a valid email."
        return render_template("forgot.html", forgotError=error)
    else:
        code = random.randint(1111, 9999)
        res = password_reset.upsert(session["email"], code)
        password_reset_email(session["email"], code)
        return render_template("forgot.html", codeSent="yes", email=session["email"])


@home_route.route("/passwordReset", methods=["POST"])
def passwordReset():
    email = request.form.get("username")
    code = request.form.get("resetCode")
    newPassword = request.form.get("newPassword")
    actual_code = password_reset.get_code(email)

    if actual_code is None:
        error = "Some error occurred. Please try again."
        return redirect('/login', loginError=error)

    if int(actual_code) == int(code):
        if newPassword is None:
            error = "Enter a valid password"
            return render_template("forgot.html", codeSent="yes", email=session["email"], forgotError=error)
        else:
            successful_reset_email(email)
            password_reset.update_password(email, newPassword)
            return render_template("login.html", successMessage="Your password has been successfully reset.")
    else:
        error = "Incorrect code"
        return render_template("forgot.html", codeSent="yes", email=session["email"], forgotError=error)





@home_route.route("/loginUser", methods=["POST"])
def login_user():
    """
    Handles login, generates OTP, and sends it to the user's email.
    """
    email = request.form["username"]  # User's email
    password = request.form["password"]  # User's password

    # Validate user credentials (replace this with your database query)
    user_data = user.get(email, password)  # Assuming `user.get` fetches user info
    if user_data == 0:
        return render_template("login.html", loginError="Email does not exist. Please enter a valid email.")
    elif user_data == 2:
        return render_template("login.html", loginError="Incorrect password.")

    # Generate and send OTP
    success, secret = send_otp_email(email)
    if not success:
        return render_template("login.html", loginError="Failed to send OTP. Please try again.")

    # Store secret and other details in the session
    session["otp_secret"] = secret
    session["email"] = email
    session["otp_verified"] = False

    # Redirect to the OTP verification page
    return redirect("/verify_otp")


# from flask import request, session, redirect, render_template
# import pyotp
import logging

@home_route.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    """
    Verifies the OTP entered by the user.
    """
    if request.method == "POST":
        otp = request.form["otp"]  # OTP entered by the user
        secret = session.get("otp_secret")  # Retrieve the secret from the session

        print(f"OTP Secret: {secret}")  # Debug
        if secret:
            totp = pyotp.TOTP(secret)
            print(f"Expected OTP: {totp.now()}")  # Debug
            if totp.verify(otp, valid_window=1):  # Allow a 30-sec offset
                session["otp_verified"] = True  # Mark the OTP as verified
                return redirect("/auth")  # Redirect to the authenticated page
        return render_template("verify_otp.html", error="Invalid OTP. Please try again.")

    # Render the OTP input page for GET requests
    return render_template("verify_otp.html")






@home_route.route("/signup", methods=["POST"])
def signup():
    name = request.form["name"]
    session["email"] = request.form["email"]
    password = request.form["password"]
    gender = request.form["gender"]
    location = request.form["location"]

    try:
        # Attempt to create a new user
        result = user.post(name, session["email"], password, gender, location)

        # Check if user creation was successful
        if result == 0:
            raise IntegrityError(f"A user with the email '{session['email']}' already exists. Please choose a different email.")

        # Send registration email only if user creation is successful
        registration_email_result = send_registration_email(name, session["email"])

        # Check if email sending was successful
        if not registration_email_result:
            raise Exception("Failed to send registration email.")

        # Render the success message or redirect to another page if needed
        success_message = "User created successfully!"
        return render_template("login.html", successMessage=success_message)

    except IntegrityError as e:
        # Handle the IntegrityError specifically for duplicate entry
        error = f"A user with the email '{session['email']}' already exists. Please choose a different email."
        return render_template("login.html", emailError=error)

    except Exception as e:
        # Handle other exceptions
        error = "An error occurred. A user with same username exists. Please choose a different email."
        return render_template("login.html", emailError=error)
 
    


@home_route.route("/view", methods=["GET"])
# @login_required
def view():
    """
    This intercepts the /view URL get request. Displays the Page details for a application in a specific category.
    It reads the query parameters given when passing in the URL
    :return:
    """
    application_category = request.args.get("show").upper()

    result_data = application.get(session["email"], application_category)

    #("result_data ", result_data)
    # base.html data
    data = user.get_auth_user_dao(session["email"])
    data["wishlist"] = application.get(session["email"], "")
    upcoming_events = fetch_upcoming_events_temp()
    return render_template(
        "view_list.html", data=data, result_data=result_data, upcoming_events=upcoming_events
    )



def parse_date(date_str):
    """Parse date that can be either a year or a full date."""
    try:
        # Check if the input is a single year
        if len(date_str) == 4 and date_str.isdigit():
            # If so, return January 1st of that year
            return datetime.strptime(f"{date_str}-01-01", '%Y-%m-%d')
        else:
            # Otherwise, try to parse as a full date
            return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        # Return current date as fallback instead of error string
        return datetime.now()


@home_route.route("/add_new_application", methods=["GET", "POST"])
# @login_required
def add_new_application():
    """
    This intercepts the add new application post request .
    It reads all the application details from the form contents during the post operation and creates a new application For the user .

    :return:
    """

    company_name = request.form["companyName"]
    location = request.form["location"]
    job_profile = request.form["jobProfile"]
    salary = request.form["salary"]
    username = request.form["username"]
    password = request.form["password"]
    security_question = request.form["securityQuestion"]
    security_answer = request.form["securityAnswer"]
    notes = request.form["notes"]
    date_applied = request.form["dateApplied"]
    status = request.form["status"]
    #print("status", status)

    resume_content = None
    if 'resume' in request.files:
        resume_file = request.files['resume']
        if resume_file and resume_file.filename.endswith('.pdf'):
            resume_content = resume_file.read()
            print("Resume content length:", len(resume_content))  # Debug
    # print('-----')
    # print('-----')
    # print('-----')
    # print(date_applied)
    # print('-----')
    # print('-----')
    # print('-----')
    result = application.post(
        session["email"],
        company_name,
        location,
        job_profile,
        salary,
        username,
        password,
        security_question,
        security_answer,
        notes,
        date_applied,
        status,
        resume_content
    )
    if result == 0:
        error = "This job application could not be stored in the database. Please try again."
        return render_template("home.html", jobAddError=error)
    data = {}
    try:
        print(f'Date applied value: {date_applied}')
        
        parsed_date = parse_date(date_applied)
        formatted_date = parsed_date.strftime('%Y-%m-%d')
        
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
        creds = flow.run_local_server(port=0)
        
        service = build('calendar', 'v3', credentials=creds)
        
        event = {
            'summary': f'Job Application: {company_name} - {job_profile}',
            'description': f'''
                Company: {company_name}
                Position: {job_profile}
                Location: {location}
                Status: {status}
                Notes: {notes}
            ''',
            'start': {
                'date': formatted_date,  
                'timeZone': 'UTC',
            },
            'end': {
                'date': formatted_date,  
                'timeZone': 'UTC',
            }
        }
        
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        print(f'Calendar event created: {created_event.get("htmlLink")}')
        
    except Exception as e:
        print(f"Failed to create calendar event: {str(e)}")
        import traceback
        traceback.print_exc()  
        pass


    s_email(
        company_name,
        location,
        job_profile,
        salary,
        username,
        password,
        session["email"],
        security_question,
        security_answer,
        notes,
        date_applied,
        status,
    )
    return redirect("/auth")

@home_route.route('/download_resume')
def download_resume():
    try:
        resume_data = application.get_resume(session["email"])
        
        if resume_data:
            file_stream = io.BytesIO(resume_data)
            file_stream.seek(0)
            
            return send_file(
                file_stream,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'resume.pdf'
            )
        else:
            return "No resume found", 404
            
    except Exception as e:
        print(f"Error in download_resume: {e}")
        return f"Error: {str(e)}", 500
    
@home_route.route('/download_applications')
def download_applications():
    try:
        columns = ["Company Name", "Status", "Application Date", "Application ID", "Location", "Role", "Salary", "Imortant Links"]
        application_data = application.get(session["email"], "")
        
        df = pd.DataFrame(application_data, columns=columns)
        
        file_stream = io.BytesIO()
        df.to_excel(file_stream, index=False, engine='openpyxl')
        file_stream.seek(0)

        return send_file(
            file_stream,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='applications.xlsx'
        )
            
    except Exception as e:
        print(f"Error in download_applications: {e}")
        return f"Error: {str(e)}", 500


@home_route.route("/change_status_application", methods=["POST"])
# @login_required
def change_status_application():
    """
    It intercepts the change status application post request.
    It takes in the new status from the form content for the specific application ID and changes it to that status.
    :return:
    """
    status = request.form["status_change"]
    application_id = request.form["application_id"]
    #print("status", status)
    result = application.change_status(application_id, status)
    if result == 0:
        error = "This job application could not be stored in the database. Please try again."
        return render_template("home.html", jobAddError=error)
    data = {}
    status_change_email(application_id, session["email"], status)
    return redirect("/auth")


@home_route.route("/delete_application", methods=["POST"])
# @login_required
def delete_application():
    """
    This intercepts the delete application post request it takes in the application ID and delete it from the database for the user
    :return:
    """
    application_id = request.form["application_id"]
    result = application.delete(application_id)
    if result == 0:
        error = "This job application could not be stored in the database. Please try again."
        return render_template("home.html", jobAddError=error)
    data = {}
    return redirect("/auth")


@home_route.route("/edit_application", methods=["POST"])
# @login_required
def edit_application():
    """
    This intercepts the edit application post request.
    It takes in the new details of the application for the given application ID and the user and modify the contents of the application in the database
    :return:
    """
    company_name = request.form["companyName"]
    location = request.form["location"]
    job_profile = request.form["jobProfile"]
    salary = request.form["salary"]
    username = request.form["username"]
    password = request.form["password"]
    security_question = request.form["securityQuestion"]
    security_answer = request.form["securityAnswer"]
    notes = request.form["notes"]
    date_applied = request.form["dateApplied"]
    status = request.form["status"]
    application_id = request.form["application_id"]
    #print("status", status)
    result = application.update(
        company_name,
        location,
        job_profile,
        salary,
        username,
        password,
        security_question,
        security_answer,
        notes,
        date_applied,
        status,
        application_id,
    )
    if result == 0:
        error = "This job application could not be stored in the database. Please try again."
        return render_template("home.html", jobAddError=error)
    data = {}
    return redirect("/auth")


@home_route.route("/edit_profile", methods=["POST"])
# @login_required
def edit_profile():
    """
    This intercepts the edit profile post request.
    It takes in the new profile details of the user and edits in the user database
    :return:
    """
    name = request.form["name"]
    gender = request.form["gender"]
    location = request.form["location"]
    user_id = request.form["user_id"]
    result = user.edit_profile(user_id, name, gender, location)
    if result == 0:
        error = "This user not found in the database. Please try again."
        return render_template("home.html", jobAddError=error)
    data = {}
    return redirect("/auth")


@home_route.route("/logout", methods=["GET"])
# @login_required
def logout():
    """
    Logs out the user when encountered with the logout URL get request and navigate back to the login URL
    :return:
    """

    if "email" in session:
        session.pop("email", None)
    # logout_user()
    return redirect("/login")

@home_route.route("/analytics/salary-trends", methods=["GET"])
#@login_required
def salary_trends():
    try:
        email = session.get("email")
        if not email:
            return jsonify({"error": "User not logged in"}), 403

        salary_data = application.get_salary_by_company(email)  # DAO method

        if not salary_data:
            return jsonify({"error": "No salary data found"}), 404

        # Format the result into a list of dictionaries
        formatted_data = [{"company": item[0], "salary": item[1]} for item in salary_data]

        return jsonify(formatted_data)

    except Exception as e:
        print(f"Error in salary_trends: {e}")
        return jsonify({"error": "Internal server error"}), 500

@home_route.route("/analytics/salary-graph", methods=["GET"])
#@login_required  # Protects the route for logged-in users
def salary_graph():
    """
    Route to render the salary graph page.
    """
    return render_template("analytics.html")




# if __name__ == '__main__':
#     app.run(debug=True)
