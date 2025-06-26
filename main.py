import os
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
from employee_config import Config
from DatabaseManager import DatabaseManager
from LLMProcessor import LLMProcessor
from QueryProcessor import QueryProcessor
from UserInterface import UserInterface
from DatabaseInitializer import DatabaseInitializer
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)


def main():
    print("Initializing system...")
    config = Config()

    # Initialize database if not already done
    db_initializer = DatabaseInitializer(config)
    # Note: In production, we would check if the database exists and is populated, but for simplicity, we initialize every time for now.
    # Alternatively, we can have a command-line flag or a config setting to avoid re-initializing every time.
    db_initializer.initialize_database()

    # Initialize database manager
    db_manager = DatabaseManager(config)
    print("Database manager initialized.")

    # Initialize LLM processor - SPECIFY MODEL NAME EXPLICITLY
    print("Loading language model (this may take a minute)...")
    start_time = time.time()
    # llm_processor = LLMProcessor("MiniMaxAI/MiniMax-M1-80k")
    llm_processor = LLMProcessor("gpt2-medium")
    llm_processor.set_config(config)

    load_time = time.time() - start_time
    print(f"Language model loaded in {load_time:.2f} seconds.")

    # Initialize query processor
    query_processor = QueryProcessor(db_manager, llm_processor)
    print("Query processor initialized.")

    # Initialize user interface
    ui = UserInterface()
    print("System ready.")

    # Get user queries
    queries = ui.get_user_queries()
    if not queries:
        print("No queries provided. Exiting.")
        return

    # Process each query
    print(f"\nProcessing {len(queries)} queries...")
    for i, query in enumerate(queries, start=1):
        try:
            # Process query and get results
            result_data = query_processor.process_query(query)
            result = {
                'query': query,
                'status': 'success',
                'data': result_data
            }
        except Exception as e:
            result = {
                'query': query,
                'status': 'error',
                'error': str(e)
            }

        # Pass structured result to UI
        ui.display_results(result)


if __name__ == "__main__":
    main()