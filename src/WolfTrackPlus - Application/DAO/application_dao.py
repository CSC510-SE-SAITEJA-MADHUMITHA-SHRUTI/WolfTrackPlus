from DAO.sql_helper import sql_helper
import base64

class application_dao:
    """
    This is the application_dao class."
    """

    def __init__(self):
        """
        This is the default constructor for the application_dao class.
        """
        self.__db = sql_helper()

    def add_application(
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
        resume=None
    ):
        """
        Adds an application with all the specified arguments into the database.

        Args:
            email (string): Email ID of the user for that application.
            company_name (string): Company to which the user is applying to.
            location (string): Location of the job posting.
            job_profile (string): Type of role.
            salary (int): Salary that the job offers.
            username (string): Login credentials for the application.
            password (string): Password for the application.
            security_question (string): Security question for the application.
            security_answer (string): Answer to the application's security questions.
            notes (string): Any notes that the user might want to add in regards to their application.
            date_applied (date): Takes in the date of application.
            status (string): Status of this application such as applied or pending.

        Returns:
            self: runs the SQL query to add an application into the database, and returns the execution status of the query.
        """
        userId = self.__db.run_query(
            "SELECT user_id FROM user WHERE email='" + email + "'"
        )[0][0]

        self.__db.run_query(
            "INSERT into company (company_name) values ('" + company_name + "');"
        )
        companyId = self.__db.run_query(
            "SELECT company_id FROM company WHERE company_name='" + company_name + "'"
        )[0][0]

        self.__db.run_query("INSERT INTO roles (role) values ('" + job_profile + "');")
        roleId = self.__db.run_query(
            "SELECT role_id FROM roles WHERE role='" + job_profile + "'"
        )[0][0]

        if resume:
           resume_data = base64.b64encode(resume).decode('utf-8')
           base_query = (
               "INSERT INTO application (user_id, company_id, role_id, application_date, job_description, "
               "salary, location, status, imortant_links, resume) VALUES ("
               + str(userId)
               + ", "
               + str(companyId)
               + ", "
               + str(roleId)
               + ", '"
               + date_applied
               + "', '"
               + job_profile
               + "', "
               + str(salary)
               + ", '"
               + location
               + "', '"
               + status
               + "', '"
               + notes
               + "', '"
               + resume_data
               + "');"
           )
        else:
            base_query = (
        "INSERT INTO application (user_id, company_id, role_id, application_date, "
        "job_description, salary, location, status, imortant_links, resume) VALUES ("
        + str(userId)
        + ", "
        + str(companyId)
        + ", "
        + str(roleId)
        + ", '"
        + date_applied
        + "', '"
        + job_profile
        + "', "
        + str(salary)
        + ", '"
        + location
        + "', '"
        + status
        + "', '"
        + notes
        + "', NULL"
        + ");"
    )
        return self.__db.run_query(base_query)

    def get_application(self, email, application_status):
        """
        Fetches an application based on keywords from the database.

        Args:
            email (string): email of the user who created the application in respect.
            application_status (string): Application status such as pending or applied.

        Returns:
            [tuple]: Returns the result of the SQL query that fetches the application from the database.
        """
        userId = self.__db.run_query(
            "SELECT user_id FROM user WHERE email='" + email + "'"
        )[0][0]

        sQuery = (
            "SELECT company_name, status, application_date, application_id, location, role, salary, imortant_links"
            + "  FROM application JOIN company ON company.company_id = application.company_id "
            + " JOIN roles ON roles.role_id = application.role_id "
            + "WHERE user_id="
            + str(userId)
        )

        if application_status != "":
            sQuery += f" and status = '{application_status}'"

        res = self.__db.run_query(sQuery)

        res = [list(i) for i in res]
        for i in res:
            i[2] = i[2][:10]

        print(res)
        return res

    def get_resume(self, email):
        """
        Fetches the resume for a user based on their email.
        
        Args:
            email (string): Email ID of the user
            
        Returns:
            bytes: The resume binary data if found, None otherwise
        """
        try:
            userId = self.__db.run_query(
                "SELECT user_id FROM user WHERE email='" + email + "'"
            )[0][0]

            query = (
                "SELECT resume "
                + "FROM application "
                + "WHERE user_id ="
                + '"'+str(userId)+'"'
                + " AND resume IS NOT NULL "
                + "LIMIT 1"
                )
            result = self.__db.run_query(query)
            
            if result and result[0][0]:
                resume_data = result[0][0]
                return base64.b64decode(resume_data)
            return None
            
        except Exception as e:
            print(f"Error fetching resume: {e}")
            return None


    def get_locations_for_application(self, email):
        """
        Fetches all job application locations for a specific user.
        :param email: Email of the user
        :return: List of job application locations
        """
        # Assuming you have a 'user_id' field in the 'application' table
        user_id = self.__db.run_query(
            "SELECT user_id FROM user WHERE email='" + email + "'"
        )[0][0]

        # Assuming 'location' is the field in your 'application' table
        query = f"SELECT DISTINCT location FROM application WHERE user_id = {user_id}"
        result = self.__db.run_query(query)

        # Extract the locations from the result
        locations = [row[0] for row in result]

        return locations
    

    def get_company_names_for_application(self, email):
        """
        Fetches all distinct company names for a specific user's job applications.
        :param email: Email of the user
        :return: List of distinct company names
        """
        # Assuming you have a 'user_id' field in the 'user' table
        user_id_query = f"SELECT user_id FROM user WHERE email = '{email}'"
        user_id = self.__db.run_query(user_id_query)[0][0]

        # Assuming 'company_name' is the field in your 'company' table
        query = (
        "SELECT DISTINCT company_name "
        "FROM application "
        "JOIN company ON company.company_id = application.company_id "
        f"WHERE user_id = {user_id}"
        )
        result = self.__db.run_query(query)

        # Extract the company names from the result
        company_names = [row[0] for row in result]

        return company_names


    def update_application(
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
        """
        Updates an application with all the specified arguments into the database.

        Args:
            email (string): Email ID of the user for that application.
            company_name (string): Company to which the user is applying to.
            location (string): Location of the job posting.
            job_profile (string): Type of role.
            salary (int): Salary that the job offers.
            username (string): Login credentials for the application.
            password (string): Password for the application.
            security_question (string): Security question for the application.
            security_answer (string): Answer to the application's security questions.
            notes (string): Any notes that the user might want to add in regards to their application.
            date_applied (date): Takes in the date of application.
            status (string): Status of this application such as applied or pending.

        Returns:
            self: runs the SQL query to update an application in the database, and returns the execution status of the query.
        """
        "test Commit"

        res = self.__db.run_query(
            "SELECT company_name,company.company_id, role, roles.role_id"
            + "  FROM application JOIN company ON company.company_id = application.company_id "
            + " JOIN roles ON roles.role_id = application.role_id "
            + "WHERE application_id="
            + str(application_id)
        )

        companyId = res[0][1]
        roleId = res[0][3]
        if res[0][0] != company_name:
            self.__db.run_query(
                "INSERT into company (company_name) values ('" + company_name + "');"
            )
            companyId = self.__db.run_query(
                "SELECT company_id FROM company WHERE company_name='"
                + company_name
                + "'"
            )[0][0]

        if res[0][2] != job_profile:
            self.__db.run_query(
                "INSERT INTO roles (role) values ('" + job_profile + "');"
            )
            roleId = self.__db.run_query(
                "SELECT role_id FROM roles WHERE role='" + job_profile + "'"
            )[0][0]

        sQuery = (
            f"Update application set company_id={companyId}, role_id={roleId}, job_description='{job_profile}', "
            + f"salary={salary}, location='{location}', status='{status}', imortant_links='{notes}' where application_id="
            + str(application_id)
        )
        return self.__db.run_query(sQuery)

    def change_status(self, application_id, status):
        """
        Changes the status of an existing application.

        Args:
            application_id (string): An identifier which can link to the required application.
            status (string): New status that the application should be changed into.

        Returns:
            bool: returns the status of the SQL query execution for changing application status.
        """
        res = self.__db.run_query(
            "UPDATE application SET status = '"
            + status
            + "' WHERE application_id="
            + str(application_id)
        )
        print(res)
        return res

    def delete_application(self, application_id):
        """
        Deletes an existing application.

        Args:
            application_id (string): An identifier which can link to the required application.

        Returns:
            bool: returns the status of the SQL query execution for deleting an application.
        """
        res = self.__db.run_query(
            "DELETE FROM application WHERE application_id=" + str(application_id)
        )
        return res
    
    def get_salary_by_company(self, email):
        query = """
            SELECT company.company_name, application.salary
            FROM application
            INNER JOIN company ON application.company_id = company.company_id
            INNER JOIN user ON application.user_id = user.user_id
            WHERE user.email = %s
        """
        result = self.__db.run_query(query, (email,))
        return result
