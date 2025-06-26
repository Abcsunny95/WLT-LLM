import mysql.connector
import os
import re
import json
from datetime import datetime, timedelta
from typing import List, Dict, Union, Tuple

# ===========================
# Database Module
# ===========================
class DatabaseManager:
    def __init__(self, config):
        self.config = config
        self.connection = None

    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**self.config.DB_CONFIG)
            return self.connection.cursor(dictionary=True)
        except mysql.connector.Error as err:
            raise ConnectionError(f"Database connection failed: {err}")

    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()


    def execute_query(self, query: str) -> Dict:
        """Execute SQL query and return structured results"""
        cursor = self.connect()
        try:
            cursor.execute(query)

            # For SELECT queries, return results
            if cursor.description:
                results = cursor.fetchall()
                return {
                    "status": "success",
                    "type": "data",
                    "columns": [col[0] for col in cursor.description],
                    "data": results,
                    "rowcount": cursor.rowcount
                }
            # For other queries, return rowcount
            return {
                "status": "success",
                "type": "operation",
                "rowcount": cursor.rowcount,
                "message": f"Operation affected {cursor.rowcount} rows"
            }
        except mysql.connector.Error as err:
            return {
                "status": "error",
                "message": f"Database error: {err}",
                "sql": query
            }
        finally:
            cursor.close()
            self.close()

    def get_table_info(self) -> Dict:
        """Get database table metadata"""
        try:
            cursor = self.connect()
            cursor.execute("DESCRIBE employee_activities")
            return {
                "status": "success",
                "columns": [col[0] for col in cursor.description],
                "data": cursor.fetchall()
            }
        except mysql.connector.Error as err:
            return {"status": "error", "message": str(err)}
        finally:
            cursor.close()
            self.close()

    # Add to
    def initialize_database(self):
        """Create database schema and populate with synthetic data"""
        cursor = self.connect()
        try:
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS employee_activities
                           (
                               record_id
                               INT
                               AUTO_INCREMENT
                               PRIMARY
                               KEY,
                               employee_id
                               VARCHAR
                           (
                               20
                           ) NOT NULL,
                               full_name VARCHAR
                           (
                               100
                           ) NOT NULL,
                               week_number INT NOT NULL,
                               number_of_meetings INT DEFAULT 0,
                               total_sales_rmb DECIMAL
                           (
                               10,
                               2
                           ) DEFAULT 0.0,
                               hours_worked DECIMAL
                           (
                               5,
                               2
                           ) DEFAULT 0.0,
                               activities TEXT,
                               department VARCHAR
                           (
                               50
                           ),
                               hire_date DATE,
                               email_address VARCHAR
                           (
                               100
                           ),
                               job_title VARCHAR
                           (
                               100
                           ),
                               week_start_date DATE
                               )
                           """)

            # Generate synthetic data for 10 employees × 10 weeks
            departments = ["Sales", "Marketing", "Product Development", "Finance", "IT"]
            job_titles = ["Sales Manager", "Data Analyst", "Marketing Specialist",
                          "Product Manager", "Software Engineer", "Accountant"]

            for emp_id in range(1, 11):
                for week in range(1, 11):
                    cursor.execute(f"""
                    INSERT INTO employee_activities (
                        employee_id, full_name, week_number, number_of_meetings,
                        total_sales_rmb, hours_worked, activities, department,
                        hire_date, email_address, job_title, week_start_date
                    ) VALUES (
                        'E{emp_id:03d}', 
                        'Employee {emp_id}', 
                        {week},
                        {random.randint(5, 20)},
                        {random.uniform(1000, 50000):.2f},
                        {random.uniform(30.0, 50.0):.2f},
                        'Prepared sales reports and client meetings',
                        '{random.choice(departments)}',
                        DATE_SUB(NOW(), INTERVAL {random.randint(1, 5)} YEAR),
                        'employee{emp_id}@company.com',
                        '{random.choice(job_titles)}',
                        DATE_ADD('2024-01-01', INTERVAL {week - 1} WEEK)
                    )
                    """)
            self.connection.commit()
            return {"status": "success", "message": "Database initialized"}
        except mysql.connector.Error as err:
            return {"status": "error", "message": str(err)}