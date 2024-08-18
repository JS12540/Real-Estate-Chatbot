import pandas as pd
import pandasql as psql
from logger import logger

def execute_query_on_csv(query):
    """
    Reads an Excel file, executes the given SQL query on it, and returns the results as a Markdown table.
    """

    logger.info(f"Executing query: {query}")
    # Load the Excel file into a pandas DataFrame
    df = pd.read_excel(r"Dataset/Inventory sheet.xlsx")
    
    # Create a local variable dictionary to pass to pandasql
    local_vars = {'df': df}
    
    # Execute the SQL query using pandasql, passing in the DataFrame explicitly
    result_df = psql.sqldf(query, local_vars)
    
    # Convert the result to a Markdown table format
    result_markdown = result_df.to_markdown(index=False)

    logger.info("Query execution completed successfully.")
    
    return result_markdown
