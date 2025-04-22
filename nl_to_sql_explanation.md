# Natural Language to SQL: Technical Documentation

## Overview

The Natural Language to SQL feature allows users to query SQL Server databases using everyday language rather than writing SQL code directly. This document explains the technical implementation of this feature, detailing how it translates natural language queries into valid SQL Server queries, executes them, and presents the results.

## Architecture

The feature is implemented across several components:

1. **nl_to_sql.py**: Core module that handles schema analysis, query conversion, and execution
2. **app.py**: Integration with the Streamlit UI and user interaction flow
3. **Google Gemini AI**: External service used for natural language understanding and SQL generation
4. **SQL Editor with Autocomplete**: In-browser JavaScript that provides real-time column and table suggestions

## Detailed Process Flow

### 1. Database Schema Analysis

When a user connects to a database, the system automatically analyzes its structure:

```
Initial Connection → Schema Extraction → Relationship Mapping → Context Building
```

#### Key Functions:

- `get_table_schema()`: Queries SQL Server system tables to extract table and column metadata
- `get_foreign_keys()`: Identifies relationships between tables by analyzing foreign key constraints
- `prepare_schema_context()`: Formats the extracted schema into a structured context for the AI

#### Schema Context Format:

```
Database: [database_name]

Tables and Columns:
Table: [table_name]
  - [column_name] ([data_type], [NULL/NOT NULL])
  ...

Foreign Key Relationships:
  - [parent_table].[parent_column] -> [referenced_table].[referenced_column]
  ...
```

This schema context provides the AI with critical information about:
- Available tables and their structure
- Data types for each column (helping with appropriate filtering and joining)
- Relationships between tables (enabling complex query generation)
- Nullable properties (important for handling missing data cases)

### 2. Natural Language Query Processing

When a user submits a natural language question:

```
User Query → API Preparation → Gemini AI Processing → Response Parsing → SQL Extraction
```

#### Key Function:

- `nl_to_sql()`: Constructs a prompt with the schema context and user query, sends it to the Gemini AI, and processes the response

#### Prompt Structure:

The prompt follows a carefully designed template that includes:
1. Task definition for the AI
2. Complete database schema context
3. User's natural language query
4. Specific guidelines for SQL generation
5. Expected response format

#### Response Handling:

The function attempts to parse the AI's response as JSON with two fields:
- `sql_query`: The generated SQL Server query
- `explanation`: A human-readable explanation of what the query does

If JSON parsing fails (which can happen with some AI responses), a regex fallback mechanism attempts to extract the SQL query directly from the text.

### 3. SQL Query Editing with Intelligent Suggestions

After SQL generation, the system provides a user-friendly SQL editor with intelligent suggestions:

```
Generated SQL → Interactive Editor → Real-time Suggestions → User Modifications
```

#### Key Features:

- **Context-Aware Suggestions**: As the user types, the system suggests relevant table and column names
- **Table-Specific Filtering**: When typing after a table name and period (e.g., "table."), suggestions are filtered to only show columns from that table
- **SQL Keyword Support**: Common SQL keywords (SELECT, FROM, WHERE, etc.) are included in suggestions
- **Keyboard Navigation**: Users can navigate suggestions using arrow keys and select with Tab or Enter
- **Immediate Application**: Selected suggestions are immediately inserted at the cursor position

#### Implementation:

- The schema information is parsed and transformed into a format usable by JavaScript
- A dynamic suggestion box is created and positioned near the cursor
- Event listeners track the current word being typed
- Regular expressions detect whether suggestions should be table-specific or general
- Suggestions are filtered based on the current input and context

### 4. SQL Query Execution

After a SQL query is generated and potentially edited by the user:

```
SQL Query → Connection Establishment → Query Execution → Results Formatting
```

#### Key Function:

- `execute_sql_query()`: Establishes a database connection, executes the SQL query, and returns results as a pandas DataFrame

### 5. Error Handling

The system implements comprehensive error handling at each stage:

- **Connection errors**: If database connections fail, meaningful error messages are displayed
- **Schema extraction errors**: If schema information can't be retrieved, the process fails gracefully
- **AI parsing errors**: If the AI response can't be parsed, alternative extraction methods are attempted
- **Query execution errors**: If the generated SQL fails to execute, error details are logged and displayed
- **Suggestion errors**: If autocomplete fails, the editor gracefully degrades to standard text editing

## Implementation Details

### Schema Analysis Optimization

The schema analysis is optimized to handle large databases by:
1. Using efficient SQL Server system queries rather than multiple individual metadata requests
2. Caching schema information in the session state to avoid repeated analysis
3. Structuring schema data into a format that minimizes the token count for the AI prompt

### Prompt Engineering

The prompt is carefully engineered to:
1. Provide clear boundaries between schema data and the user's query
2. Give explicit guidelines to ensure SQL Server compatibility
3. Request appropriately formatted and structured responses
4. Include examples of good SQL practices like column aliasing and result limiting

### SQL Editor with Autocomplete

The SQL editor with autocomplete is implemented using:
1. **Client-side JavaScript**: Dynamic DOM manipulation provides real-time suggestions
2. **Schema Data Transformation**: Server-side processing makes database schema available to the client
3. **Event Handling**: Input, keydown, and blur events manage the suggestion workflow
4. **Context Detection**: Pattern matching determines when to show table-specific columns
5. **Keyboard Navigation**: Arrow keys, Tab, and Enter support for keyboard-centric usage

The autocomplete feature significantly improves the user experience by:
- Reducing the need for users to memorize table and column names
- Preventing syntax errors from typos in table or column names
- Enabling faster query editing with fewer keystrokes
- Supporting both keyboard and mouse interactions

### Security Considerations

While this feature provides significant usability benefits, it also implements several security measures:

1. User credentials are never exposed in the UI or passed to the AI
2. Generated SQL is displayed to the user before execution, allowing review
3. The user can modify any generated SQL before execution
4. All database interactions use parameterized connections
5. Query results are processed through pandas to minimize direct database interaction
6. Schema information is transformed into a safe format before being passed to client-side JavaScript

## Using the API Responsibly

The NL to SQL feature relies on Gemini AI, which is rate-limited and incurs costs. To use this feature responsibly:

1. The AI is configured to use the more efficient "gemini-2.0-flash" model instead of larger models
2. Schema information is condensed to reduce token usage
3. Responses are focused specifically on SQL generation without unnecessary explanations
4. The system maintains a single session rather than creating new connections for each interaction

## Limitations

The current implementation has some limitations:

1. Complex queries involving advanced SQL features may not always be generated correctly
2. The AI may occasionally generate syntax that is not fully compatible with SQL Server
3. Very large databases with complex schemas may exceed the AI's context window
4. The system cannot guarantee that generated queries will be optimized for performance
5. Natural language ambiguity can sometimes lead to queries that don't match user intent
6. The autocomplete suggestions may not work in all browsers or with all Streamlit versions

## Future Enhancements

Potential improvements to consider:
1. Query performance analysis and optimization suggestions
2. Schema caching to reduce database load with frequent connections
3. History tracking of successful queries for user reference
4. Fine-tuning the model with SQL Server-specific examples
5. Adding visualizations for query results
6. Enhanced syntax highlighting in the SQL editor
7. Expanded autocomplete to include table aliases and subquery variables
8. Saving favorite or frequently used queries 