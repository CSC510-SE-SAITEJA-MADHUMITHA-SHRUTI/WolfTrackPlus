from flask import Blueprint, session, jsonify, render_template
from flask_login import login_required
from Controller.application_controller import Application

analytics_route = Blueprint("analytics_route", __name__)
application = Application()

@analytics_route.route("/salary-trends", methods=["GET"])
@login_required
def salary_trends():
    """
    Route to fetch salary trends for the logged-in user.
    :return: JSON containing company names and corresponding salaries
    """
    email = session["email"]
    salary_data = application.get_salary_by_company(email)  # DAO method
    formatted_data = [{"company": item[0], "salary": item[1]} for item in salary_data]
    return jsonify(formatted_data)

@analytics_route.route("/salary-graph", methods=["GET"])
@login_required
def salary_graph():
    """
    Route to render the salary graph page.
    """
    return render_template("analytics.html")
