import mysql.connector
import os
import re
import json
import requests
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Union, Tuple

# ===========================
# Configuration Module
# ===========================
class Config:
    MINIMAX_API_KEY= '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'  # Your Hugging Face token
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'mdsany$95',
        'database': 'employee_activity_tracking'
    }

    MAX_RESULT_ROWS = 100  # For qualitative summaries
    RECESSION_PERIODS = [
        {'start': '2018-01-01', 'end': '2019-12-31', 'name': 'Global Economic Slowdown'},
        {'start': '2020-01-01', 'end': '2022-12-31', 'name': 'COVID-19 Recession'},
        {'start': '2022-07-01', 'end': '2023-06-01', 'name': 'Tech Industry Downturn'}
    ]
    # In knowledge base initialization
    knowledge_base = {
        # ... existing data ...
        "economic_events": [
            {"period": "2008-2010", "event": "Global recession"},
            {"period": "2020-Q2", "event": "Industry downturn"}
        ]
    }

    # Update to match actual table structure
    @staticmethod
    def get_db_schema() -> str:
        return """
        Table: employee_activities
        - record_id (INT): Primary key
        - employee_id (VARCHAR): Unique employee identifier
        - full_name (VARCHAR): Employee's full name
        - week_number (INT): Week number (1-10)
        - number_of_meetings (INT): Meetings attended
        - total_sales_rmb (DECIMAL): Total sales in RMB
        - hours_worked (DECIMAL): Hours worked
        - activities (TEXT): Work activities description
        - department (VARCHAR): Department name
        - hire_date (DATE): Date hired
        - email_address (VARCHAR): Email address
        - job_title (VARCHAR): Job title
        """

    @staticmethod
    def get_query_examples() -> str:
        return """
        Query Type Examples:
        1. Point Query: 
           "What did John do from weeks 3-7?" 
           → SELECT * FROM employee_activities 
              WHERE full_name = 'John' AND week_number BETWEEN 3 AND 7

        2. Aggregation Query: 
           "How many employees does the company have?" 
           → SELECT COUNT(DISTINCT employee_id) FROM employee_activities

        3. Knowledge Query: 
           "Which employees were hired during a recession?" 
           → Requires comparing hire_date with recession periods

        4. Reasoning Query: 
           "Who faced challenges with customer retention?" 
           → SELECT * FROM employee_activities 
              WHERE activities LIKE '%customer retention%' 
              OR activities LIKE '%customer churn%'

        5. Match-based Query: 
           "List IT department employees" 
           → SELECT * FROM employee_activities 
              WHERE department = 'IT'

        6. Comparison Query: 
           "Compare hours worked by Wei Zhang and Tao Huang in week 1" 
           → SELECT full_name, hours_worked 
              FROM employee_activities 
              WHERE full_name IN ('Wei Zhang', 'Tao Huang') 
              AND week_number = 1

        7. Ranking Query: 
           "Top 3 employees by hours worked in last 4 weeks" 
           → SELECT full_name, SUM(hours_worked) AS total_hours 
              FROM employee_activities 
              WHERE week_number > 6 
              GROUP BY full_name 
              ORDER BY total_hours DESC 
              LIMIT 3
        """