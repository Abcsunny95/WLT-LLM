# import logging
# from typing import Dict
#
# class QueryProcessor:
#     def __init__(self, db_manager, llm_processor):
#         self.db_manager = db_manager
#         self.llm_processor = llm_processor
#         self.logger = logging.getLogger(__name__)
#         self.logger.setLevel(logging.INFO)
#
#     def process_query(self, natural_language_query: str) -> Dict:
#         """Process natural language query end-to-end"""
#         # Special handling for knowledge-based queries
#         if self.is_knowledge_query(natural_language_query):
#             summary = self.llm_processor.handle_knowledge_query(
#                 natural_language_query,
#                 self.db_manager
#             )
#             return {
#                 "status": "success",
#                 "type": "knowledge",
#                 "summary": summary
#             }
#
#         # Standard query processing
#         try:
#             sql_query = self.llm_processor.generate_sql(natural_language_query)
#         except Exception as e:
#             return {
#                 "status": "error",
#                 "message": f"SQL generation failed: {str(e)}"
#             }
#
#         # Execute SQL
#         db_results = self.db_manager.execute_query(sql_query)
#
#         # Handle database errors
#         if db_results.get("status") == "error":
#             return {
#                 "status": "error",
#                 "message": db_results["message"]
#             }
#
#         # Generate summary
#         summary = self.llm_processor.generate_summary(natural_language_query, db_results)
#
#         return {
#             "status": "success",
#             "sql": sql_query,
#             "data": db_results.get("data", []),  # Ensure data is included
#             "summary": summary,
#             "rowcount": db_results.get("rowcount", 0)
#         }
#
#     def is_knowledge_query(self, query: str) -> bool:
#         """Check if query requires external knowledge"""
#         keywords = ["recession", "industry", "economic", "knowledge", "capabilit"]
#         return any(kw in query.lower() for kw in keywords)

import logging
from typing import Dict, List


class QueryProcessor:
    def __init__(self, db_manager, llm_processor):
        self.db_manager = db_manager
        self.llm_processor = llm_processor
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Configure logging handler
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def process_query(self, natural_language_query: str) -> Dict:
        """Process natural language query end-to-end"""
        self.logger.info(f"Processing query: {natural_language_query}")

        try:
            # Special handling for knowledge-based queries
            if self.is_knowledge_query(natural_language_query):
                self.logger.info("Identified as knowledge query")
                return self.handle_knowledge_query(natural_language_query)

            # Standard query processing
            return self.handle_standard_query(natural_language_query)

        except Exception as e:
            self.logger.error(f"Unexpected error processing query: {str(e)}")
            return {
                "status": "error",
                "message": f"System error: {str(e)}"
            }

    def handle_knowledge_query(self, query: str) -> Dict:
        """Process knowledge-based queries"""
        try:
            summary = self.llm_processor.handle_knowledge_query(
                query,
                self.db_manager
            )
            return {
                "status": "success",
                "type": "knowledge",
                "summary": summary
            }
        except Exception as e:
            self.logger.error(f"Knowledge query handling failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Knowledge processing error: {str(e)}"
            }

    def handle_standard_query(self, query: str) -> Dict:
        """Process standard database queries"""
        try:
            # Generate SQL query
            sql_query = self.llm_processor.generate_sql(query)
            self.logger.info(f"Generated SQL: {sql_query}")
        except Exception as e:
            self.logger.error(f"SQL generation failed: {str(e)}")
            return {
                "status": "error",
                "message": f"SQL generation failed: {str(e)}"
            }

        # Execute SQL
        db_results = self.db_manager.execute_query(sql_query)

        # Handle database errors
        if db_results.get("status") == "error":
            error_msg = db_results.get("message", "Unknown database error")
            self.logger.error(f"Database error: {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "sql": sql_query
            }

        # Generate summary
        try:
            summary = self.llm_processor.generate_summary(query, db_results)
        except Exception as e:
            self.logger.warning(f"Summary generation failed: {str(e)}")
            summary = "Could not generate summary - showing raw results"

        # Prepare result
        return {
            "status": "success",
            "sql": sql_query,
            "data": db_results.get("data", []),
            "summary": summary,
            "rowcount": db_results.get("rowcount", 0)
        }

    # In QueryProcessor.py - add to is_knowledge_query()
    def is_knowledge_query(self, query: str) -> bool:
        keywords = ["recession", "industry", "economic", "knowledge",
                    "capabilit", "external", "event", "period", "hired during"]
        return any(kw in query.lower() for kw in keywords)