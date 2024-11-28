from flask import render_template, request
from flask_restful import Resource
from flask_login import login_required
from DAO.application_dao import application_dao


class Application(Resource):
    """
    This class is a controller for the application database. It inherits properties from flask_restful.Resource
    """

    def __init__(self):
        self.headers = {"Content-Type": "text/html"}
        self.application = application_dao()

    # @login_required
    def get(self, email, application_category):
        """
        Obtains stock information from the given url.

        :param url: URL of the product
        :return: a string indicating the stock information and a string indicating cost of the product
        """
        return self.application.get_application(email, application_category)
    
    def get_job_locations_for_applications(self, email):
        """
        Fetches all job application locations for a specific user.
        :param email: Email of the user
        :return: List of job application locations
        """
        return self.application.get_locations_for_application(email)
    
    def get_job_companies_for_applications(self, email):
        """
        Fetches all job application companies for a specific user.
        :param email: Email of the user
        :return: List of job application companies
        """
        return self.application.get_company_names_for_application(email)

    def get_resume(self, email):
        """
        Gets the resume for the specified user.

        Args:
            email (string): Email of the user

        Returns:
            bytes: The resume binary data if found, None otherwise
        """
        return self.application.get_resume(email)

    # @login_required
    def post(
        self,
        email,
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
        resume,
    ):
        """
        Obtains stock information from the given url.

        :param url: URL of the product
        :return: a string indicating the stock information and a string indicating cost of the product
        """
        # print(resume)
        return self.application.add_application(
            email,
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
            resume,
        )

    def change_status(self, status, application_id):
        return self.application.change_status(status, application_id)

    # @login_required
    def update(
        self,
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
    ):
        return self.application.update_application(
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
    
    def get_salary_trends(self, email):
        """
        Fetches salary trends for applications made by the given user.

        :param email: Email of the user
        :return: JSON containing company names and corresponding salaries
        """
        # Fetch salary data using the DAO
        salary_data = self.application.get_salary_by_company(email)

        # Format the result into a list of dictionaries
        formatted_data = [{"company": item[0], "salary": item[1]} for item in salary_data]

        return jsonify(formatted_data)



   # @login_required
def delete(self, application_id):
    return self.application.delete_application(application_id)

