import mysql.connector
from datetime import datetime, timedelta
import random


class DatabaseInitializer:
    def __init__(self, config):
        self.config = config.DB_CONFIG
        self.connection = None

    def connect(self):
        self.connection = mysql.connector.connect(**self.config)
        return self.connection.cursor()

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def initialize_database(self):
        cursor = self.connect()

        cursor.execute("CREATE DATABASE IF NOT EXISTS employee_activity_tracking")
        cursor.execute("USE employee_activity_tracking")
        cursor.execute("DROP TABLE IF EXISTS employee_activities")

        create_table_query = """
                             CREATE TABLE employee_activities \
                             ( \
                                 record_id          INT AUTO_INCREMENT PRIMARY KEY, \
                                 employee_id        VARCHAR(20)  NOT NULL, \
                                 full_name          VARCHAR(100) NOT NULL, \
                                 week_number        INT          NOT NULL, \
                                 number_of_meetings INT            DEFAULT 0, \
                                 total_sales_rmb    DECIMAL(10, 2) DEFAULT 0.0, \
                                 hours_worked       DECIMAL(5, 2)  DEFAULT 0.0, \
                                 activities         TEXT, \
                                 department         VARCHAR(50), \
                                 hire_date          DATE, \
                                 email_address      VARCHAR(100), \
                                 job_title          VARCHAR(100), \
                                 week_start_date    DATE
                             ) \
                             """
        cursor.execute(create_table_query)

        # Create Business Development department data
        departments = ["Sales", "Marketing", "Product Development", "Finance", "IT", "Business Development"]
        job_titles = ["Sales Manager", "Data Analyst", "Marketing Specialist", "Product Manager",
                      "Software Engineer", "Financial Analyst", "Business Development Manager"]

        base_date = datetime(2024, 8, 1)
        employees = [
            # Add employees for Business Development department
            {"id": "E011", "name": "John Smith", "department": "Business Development",
             "job_title": "Business Development Manager", "email": "john.smith@example.com",
             "hire_date": "2020-05-15"},
            {"id": "E012", "name": "Emily Johnson", "department": "Business Development",
             "job_title": "Business Development Associate", "email": "emily.j@example.com",
             "hire_date": "2021-03-22"}
        ]

        # Insert data for each employee and week
        for week in range(1, 11):
            week_start = base_date + timedelta(weeks=week - 1)
            for emp in employees:
                meetings = random.randint(5, 20)
                sales = random.uniform(1000.0, 50000.0)
                hours = random.uniform(30.0, 50.0)

                # Add recession-period hires
                if emp["name"] == "John Smith":
                    activities = "Faced challenges with customer retention; proposed new partnership program"
                else:
                    activities = "Conducted market analysis and identified new business opportunities"

                insert_query = """
                               INSERT INTO employee_activities (employee_id, full_name, week_number, number_of_meetings, \
                                                                total_sales_rmb, \
                                                                hours_worked, activities, department, hire_date, \
                                                                email_address, job_title, week_start_date) \
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
                               """
                values = (
                    emp["id"], emp["name"], week, meetings, sales, hours, activities,
                    emp["department"], emp["hire_date"], emp["email"], emp["job_title"], week_start
                )
                cursor.execute(insert_query, values)

        self.connection.commit()
        cursor.close()
        self.close()
        print("Database initialized with synthetic data including Business Development department")