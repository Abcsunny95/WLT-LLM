from DatabaseManager import DatabaseManager
from LLMProcessor import LLMProcessor
from QueryProcessor import QueryProcessor
from employee_config import Config
import json
import decimal
import re


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super().default(o)


def run_benchmark(queries, output_file):
    config = Config()
    db_manager = DatabaseManager(config)
    llm_processor = LLMProcessor("MiniMaxAI/MiniMax-M1-80k")
    llm_processor.set_config(config)
    query_processor = QueryProcessor(db_manager, llm_processor)

    results = []
    for query in queries:
        try:
            clean_query = re.sub(r"^\d+\.\s*", "", query)
            clean_query = clean_query.replace("'", "").replace('"', '')

            result = query_processor.process_query(clean_query)
            record = {
                "query": clean_query,
                "status": result.get("status", "unknown")
            }

            if result["status"] == "error":
                record["error"] = result.get("message", "Unknown error")
            else:
                record.update({
                    "sql": result.get("sql", ""),
                    "data": result.get("data", []),
                    "summary": result.get("summary", "")
                })

            results.append(record)

        except Exception as e:
            results.append({
                "query": query,
                "error": str(e),
                "status": "error"
            })

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, cls=DecimalEncoder)


if __name__ == "__main__":
    example_queries = [
        # All 20 queries listed in your doc
    ]

    print("Running Benchmark 1...")
    run_benchmark(example_queries, "benchmark1_results.json")
    print("Benchmark 1 complete. Results saved to benchmark1_results.json")