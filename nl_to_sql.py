import os
import pandas as pd
import google.generativeai as genai
import pyodbc
import logging
import json
import re
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("nl_to_sql.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("NLtoSQL")


def get_db_connection(server, database, username=None, password=None):
    """Create and return a database connection using Windows authentication"""
    try:
        # Use Windows authentication if username is None
        if username is None:
            conn_str = (
                f'DRIVER={{SQL Server}};'
                f'SERVER={server};'
                f'DATABASE={database};'
                f'Trusted_Connection=yes'
            )
        else:
            # Fallback to SQL authentication if username is provided
            conn_str = (
                f'DRIVER={{SQL Server}};'
                f'SERVER={server};'
                f'DATABASE={database};'
                f'UID={username};'
                f'PWD={password}'
            )
        return pyodbc.connect(conn_str)
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return None


def get_table_schema(server, database, username=None, password=None):
    """Retrieve schema information for the database - optimized version"""
    try:
        start_time = time.time()
        logger.info(f"Fetching schema information for {database} on {server}")
        
        conn = get_db_connection(server, database, username, password)
        if conn is None:
            return None

        cursor = conn.cursor()
        schema_data = {}

        # Optimized query to get table and column information in one go
        # Uses system catalog views for better performance
        query = """
        SELECT 
            s.name AS schema_name,
            t.name AS table_name,
            c.name AS column_name,
            ty.name AS data_type,
            c.max_length,
            c.is_nullable,
            (SELECT COUNT(*) FROM sys.foreign_keys fk 
             INNER JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
             WHERE fkc.parent_object_id = t.object_id) as has_relationships
        FROM 
            sys.tables t
            INNER JOIN sys.columns c ON t.object_id = c.object_id
            INNER JOIN sys.types ty ON c.user_type_id = ty.user_type_id
            INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
        WHERE
            t.is_ms_shipped = 0  -- Exclude system tables
        ORDER BY 
            has_relationships DESC, -- Tables with relationships first
            t.name, c.column_id
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        # Process the rows
        for row in rows:
            schema_name, table_name, column_name, data_type, max_length, is_nullable, _ = row
            
            # Skip system tables and temp tables
            if schema_name in ('sys', 'INFORMATION_SCHEMA') or table_name.startswith('#'):
                continue

            # Skip columns with 'sold_to' in their name
            if 'sold_to' in column_name.lower():
                continue

            full_table_name = f"{schema_name}.{table_name}"
            if full_table_name not in schema_data:
                schema_data[full_table_name] = []

            schema_data[full_table_name].append({
                "column_name": column_name,
                "data_type": data_type,
                "max_length": max_length,
                "is_nullable": bool(is_nullable)
            })

        conn.close()
        
        elapsed_time = time.time() - start_time
        logger.info(f"Schema information fetched in {elapsed_time:.2f} seconds")
        return schema_data
    except Exception as e:
        logger.error(f"Error getting schema information: {e}")
        return None


def get_foreign_keys(server, database, username=None, password=None):
    """Retrieve foreign key relationships for the database - optimized version"""
    try:
        start_time = time.time()
        logger.info(f"Fetching foreign key relationships for {database} on {server}")
        
        conn = get_db_connection(server, database, username, password)
        if conn is None:
            return None

        cursor = conn.cursor()
        fk_relationships = []

        # Optimized query with additional filters
        query = """
        SELECT 
            fk.name AS fk_name,
            ps.name AS parent_schema,
            tp.name AS parent_table,
            cp.name AS parent_column,
            rs.name AS referenced_schema,
            tr.name AS referenced_table,
            cr.name AS referenced_column
        FROM 
            sys.foreign_keys fk
            INNER JOIN sys.tables tp ON fk.parent_object_id = tp.object_id
            INNER JOIN sys.tables tr ON fk.referenced_object_id = tr.object_id
            INNER JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
            INNER JOIN sys.columns cp ON fkc.parent_column_id = cp.column_id AND fkc.parent_object_id = cp.object_id
            INNER JOIN sys.columns cr ON fkc.referenced_column_id = cr.column_id AND fkc.referenced_object_id = cr.object_id
            INNER JOIN sys.schemas ps ON tp.schema_id = ps.schema_id
            INNER JOIN sys.schemas rs ON tr.schema_id = rs.schema_id
        WHERE
            tp.is_ms_shipped = 0 AND  -- Exclude system tables
            tr.is_ms_shipped = 0      -- Exclude system tables
        ORDER BY 
            tp.name, tr.name
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        # Process the first 300 relationships to avoid excessive data
        for row in rows[:300]:
            fk_name, parent_schema, parent_table, parent_column, ref_schema, ref_table, ref_column = row

            # Skip relationships involving sold_to columns
            if 'sold_to' in parent_column.lower() or 'sold_to' in ref_column.lower():
                continue

            fk_relationships.append({
                "fk_name": fk_name,
                "parent_table": f"{parent_schema}.{parent_table}",
                "parent_column": parent_column,
                "referenced_table": f"{ref_schema}.{ref_table}",
                "referenced_column": ref_column
            })

        conn.close()
        
        elapsed_time = time.time() - start_time
        logger.info(f"Foreign key relationships fetched in {elapsed_time:.2f} seconds")
        return fk_relationships
    except Exception as e:
        logger.error(f"Error getting foreign key relationships: {e}")
        return None


def prepare_schema_context(server, database, username=None, password=None):
    """Prepare a context string that describes the database schema for the AI - optimized version"""
    start_time = time.time()
    schema_data = get_table_schema(server, database, username, password)
    
    if schema_data is None:
        return "Error: Could not retrieve schema information."

    # Only get foreign keys if we have schema data
    fk_relationships = get_foreign_keys(server, database, username, password)

    context = f"Database: {database}\n\n"
    context += "Tables and Columns:\n"

    # Limit the number of tables to include in the context (focus on tables with most columns or relationships)
    # Sort tables by number of columns to prioritize more complex tables
    sorted_tables = sorted(schema_data.items(), key=lambda x: len(x[1]), reverse=True)
    top_tables = sorted_tables[:50]  # Limit to top 50 tables
    
    for table_name, columns in top_tables:
        context += f"Table: {table_name}\n"
        # Limit columns per table to avoid excessive context
        for column in columns[:20]:  # Limit to top 20 columns per table
            nullable_str = "NULL" if column["is_nullable"] else "NOT NULL"
            context += f"  - {column['column_name']} ({column['data_type']}, {nullable_str})\n"
        if len(columns) > 20:
            context += f"  - ... and {len(columns) - 20} more columns\n"
        context += "\n"

    if fk_relationships:
        context += "Foreign Key Relationships:\n"
        # Limit the number of relationships to include
        for fk in fk_relationships[:100]:  # Limit to 100 relationships
            context += f"  - {fk['parent_table']}.{fk['parent_column']} -> {fk['referenced_table']}.{fk['referenced_column']}\n"
        if len(fk_relationships) > 100:
            context += f"  - ... and {len(fk_relationships) - 100} more relationships\n"

    elapsed_time = time.time() - start_time
    logger.info(f"Schema context prepared in {elapsed_time:.2f} seconds")
    return context


def nl_to_sql(natural_language_query, schema_context, api_key):
    """Convert natural language query to SQL using Gemini AI"""
    try:
        # Configure Gemini API
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')

        logger.info(f"Processing natural language query: {natural_language_query}")

        prompt = f"""
        As a SQL expert specializing in Microsoft SQL Server, your task is to convert the following natural language query into a valid SQL query.

        DATABASE SCHEMA INFORMATION:
        {schema_context}

        NATURAL LANGUAGE QUERY:
        {natural_language_query}

        GUIDELINES:
        1. Generate ONLY a valid Microsoft SQL Server query that answers the user's question.
        2. The query should be runnable as-is on SQL Server.
        3. Use appropriate JOINs where necessary based on the schema relationships.
        4. Use appropriate column names and tables as defined in the schema.
        5. Include clear column aliases for readability.
        6. Limit results to a reasonable number (e.g., TOP 100) if appropriate.
        7. Ensure the query follows best practices for performance.
        8. Add helpful comments before complex logic.
        9. IMPORTANT: Do NOT include any columns with 'sold_to' in their name in your query, regardless of context or necessity. These columns should be completely ignored.

        RESPONSE FORMAT:
        Return a JSON object with the following structure:
        {{
            "sql_query": "Your SQL query here",
            "explanation": "Brief explanation of the query and any assumptions made, explain in natural language do not include columns or tables names directly"
        }}

        Ensure your response is properly escaped JSON without any markdown formatting.
        """

        logger.info("Sending request to Gemini API")
        response = model.generate_content(prompt)
        logger.info("Received response from Gemini API")

        # Remove markdown formatting if present
        response_text = re.sub(r'```json\s*', '', response.text)
        response_text = re.sub(r'```', '', response_text)

        # Try to parse the response as JSON
        try:
            result = json.loads(response_text)
            logger.info("Successfully parsed JSON response")

            # Validate that the SQL query is present and non-empty
            if not result.get("sql_query"):
                logger.warning("SQL query is empty in the response")
                result["sql_query"] = "-- Could not generate a valid SQL query"

            return {
                "sql_query": result.get("sql_query", ""),
                "explanation": result.get("explanation", "")
            }
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}. Attempting to extract SQL with regex.")
            # If response is not valid JSON, try to extract SQL using regex
            sql_match = re.search(r'(?:```sql)?\s*(SELECT[\s\S]+?)(?:```|$)', response_text, re.IGNORECASE)
            if sql_match:
                sql_query = sql_match.group(1).strip()
                logger.info("Extracted SQL query using regex")
                return {
                    "sql_query": sql_query,
                    "explanation": "SQL query extracted from non-JSON response."
                }
            else:
                logger.error(f"Failed to parse AI response: {response_text}")
                return {
                    "sql_query": "",
                    "explanation": "Failed to parse AI response. Please try a different query."
                }

    except Exception as e:
        logger.error(f"Error in nl_to_sql: {e}", exc_info=True)
        return {
            "sql_query": "",
            "explanation": f"Error: {str(e)}"
        }


def execute_sql_query(server, database, username=None, password=None, sql_query=None):
    """Execute the SQL query and return results as a DataFrame"""
    try:
        conn = get_db_connection(server, database, username, password)
        if conn is None:
            return None

        # Try to execute the query and get results
        df = pd.read_sql(sql_query, conn)
        conn.close()

        return df
    except Exception as e:
        logger.error(f"Error executing SQL query: {e}")
        return None


def execute_query_with_user_feedback(server, database, username=None, password=None, natural_language_query=None, api_key=None):
    """Execute the entire NL-to-SQL pipeline and handle user feedback gracefully"""
    start_time = time.time()
    logger.info(f"Starting execution for query: {natural_language_query}")
    
    # Get schema context
    schema_context = prepare_schema_context(server, database, username, password)
    if "Error:" in schema_context:
        return {
            "success": False,
            "results": None,
            "message": "We couldn't connect to the database. Please try again later or contact support.",
            "summary": None
        }

    # Convert NL to SQL
    sql_result = nl_to_sql(natural_language_query, schema_context, api_key)
    sql_query = sql_result.get("sql_query", "")

    if not sql_query:
        return {
            "success": False,
            "results": None,
            "message": "We couldn't understand your question. Please try rephrasing it or being more specific.",
            "summary": None
        }

    # Execute the query
    results = execute_sql_query(server, database, username, password, sql_query)

    if results is None:
        # Query execution failed
        return {
            "success": False,
            "results": None,
            "message": "We couldn't find the information you requested. Please try a different question.",
            "summary": None,
            "sql_query": sql_query  # Include the SQL query even when execution fails
        }

    if len(results) == 0:
        # Query executed successfully but returned no records
        return {
            "success": True,
            "results": results,
            "message": "No records found matching your criteria. Please try a different search.",
            "summary": "No data found that matches your criteria.",
            "sql_query": sql_query  # Include the SQL query for empty results
        }

    # Generate summary for the results
    try:
        # Create a summary based on the data type and content
        columns = list(results.columns)
        row_count = len(results)

        # Create the final summary text
        summary = f"Found {row_count} records with {len(columns)} columns."

        # Add explanation if available
        if sql_result.get("explanation"):
            summary += f"\n\nThis shows: {sql_result.get('explanation')}"

    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        summary = f"Found {len(results)} records matching your query."

    elapsed_time = time.time() - start_time
    logger.info(f"Query execution completed in {elapsed_time:.2f} seconds")
    
    # Query executed successfully and returned records
    return {
        "success": True,
        "results": results,
        "message": f"Found {len(results)} records matching your query.",
        "summary": summary,
        "sql_query": sql_query  # Include the SQL query in the result
    }   