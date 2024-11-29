import pymysql
import traceback
import os


class sql_helper:
    """
    This class contains the necessary supporting funtions to perform SQL related operations.
    """

    def __init__(self):
        """
        Default constructor for class sql_helper
        """
        self.connection_obj = None

    def connect_database(self):
        """
        This function connects to the database on AWS, and authenticates the user.
        """
        try:
            self.connection_obj = pymysql.connect(
                # host="http://database-1.cjzkwewltsjb.us-east-2.rds.amazonaws.com",
                host="wolftrackplus.cz0o608agr58.us-east-1.rds.amazonaws.com",
                port=3306,
                user="admin",
                password="SEfall2024",
                db="wolftrack_se",
                autocommit=True,
            )
        except pymysql.Error as e:
            # Handle the exception
            print("Error: Could not connect to the database")
            print("Error Details:", str(e))
            traceback.print_exc()  # Print detailed error information
        # except:
        #     pass
            # Need to import error handling class

    def disconnect_database(self):
        """
        This function closes the database connection once done with it.
        """
        try:
            self.connection_obj.close()
        except:
            pass
            # Need to import error handling class

    def run_query(self, query, params=None):
        self.connect_database()
        try:
            tempCursor = self.connection_obj.cursor()
            if params:
                tempCursor.execute(query, params)
            else:
                tempCursor.execute(query)
            output = tempCursor.fetchall()
            return output
        except Exception as e:
            print(f"Error executing query: {e}")
            return None
        finally:
            self.disconnect_database()
