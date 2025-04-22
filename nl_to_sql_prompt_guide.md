# Natural Language to SQL: Prompt Engineering Guide

This document explains the prompt engineering techniques used in the NL to SQL feature to help developers understand how the system works and how to improve or customize it.

## Prompt Structure Analysis

The core of the NL to SQL feature is the carefully engineered prompt that guides the Gemini AI model. Below is a detailed breakdown of the prompt structure and the reasoning behind each component:

```
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

RESPONSE FORMAT:
Return a JSON object with the following structure:
{
    "sql_query": "Your SQL query here",
    "explanation": "Brief explanation of the query and any assumptions made"
}

Ensure your response is properly escaped JSON without any markdown formatting.
```

## Prompt Components Explained

### 1. Role Definition

```
As a SQL expert specializing in Microsoft SQL Server, your task is to convert the following natural language query into a valid SQL query.
```

**Purpose**: This establishes the AI's role as a SQL expert with specific Microsoft SQL Server knowledge, not just a generic SQL generator. This is critical because SQL Server has dialect-specific syntax that differs from MySQL, PostgreSQL, etc.

**Benefits**:
- Focused expertise on a specific SQL dialect
- Contextual understanding of the task
- Sets clear expectations for the response

### 2. Schema Context Section

```
DATABASE SCHEMA INFORMATION:
{schema_context}
```

**Purpose**: Provides the AI with complete information about the database structure, which is essential for generating accurate SQL queries.

**Format**:
The schema context follows a specific format that balances human readability with structured information:

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

**Benefits**:
- Provides table names for FROM clauses
- Shows column names for SELECT statements
- Indicates data types for proper filtering
- Maps relationships for join conditions
- Shows nullable status for handling NULL values

### 3. User Query Section

```
NATURAL LANGUAGE QUERY:
{natural_language_query}
```

**Purpose**: Clearly identifies the user's question, separated from the schema information and other instructions.

**Benefits**:
- Isolates the specific request the AI needs to address
- Makes it easier for the AI to identify the key elements of the question
- Provides a clear reference point when explanations are generated

### 4. Guidelines Section

```
GUIDELINES:
1. Generate ONLY a valid Microsoft SQL Server query that answers the user's question.
2. The query should be runnable as-is on SQL Server.
...
```

**Purpose**: Provides specific constraints and best practices for the generated SQL query.

**Key Guidelines Analysis**:

- **#1 & #2**: Ensures the output is valid, executable SQL Server code
- **#3**: Encourages relationship-aware queries using the foreign key information
- **#4**: Forces the use of actual schema elements rather than guessing
- **#5**: Improves readability with proper column naming
- **#6**: Prevents accidental return of enormous result sets
- **#7**: Encourages performance considerations like proper indexing
- **#8**: Makes complex queries more understandable with comments

**Benefits**:
- Constrains the AI output to useful, valid SQL
- Encourages best practices
- Prevents common SQL generation issues like column name mismatches

### 5. Response Format Section

```
RESPONSE FORMAT:
Return a JSON object with the following structure:
{
    "sql_query": "Your SQL query here",
    "explanation": "Brief explanation of the query and any assumptions made"
}
```

**Purpose**: Forces a structured, machine-readable response that can be easily parsed by the application code.

**Benefits**:
- Enables reliable extraction of just the SQL query
- Provides explanatory text separately from the executable code
- Facilitates error handling with a predictable response format
- Makes fallback regex extraction more reliable when JSON parsing fails

## Schema Context Optimization

The schema context is carefully optimized for token efficiency while maintaining clarity:

1. **Tabular Format**: Information is presented in a hierarchical, indented format that is both human-readable and compact
2. **Essential Information Only**: Only includes necessary metadata (data types, nullability) without exhaustive properties
3. **Relationship Focus**: Emphasizes table relationships which are critical for generating proper JOINs
4. **Abbreviated Syntax**: Uses shortened notation like "NULL/NOT NULL" rather than verbose descriptions

## Error Handling Strategies

The prompt includes several elements designed to reduce error rates:

1. **Clear Boundaries**: Distinct sections separated by headers prevent confusion between schema information and query instructions
2. **Explicit Format**: The JSON response format is explicitly shown with the exact field names to use
3. **SQL Server Specificity**: The prompt repeatedly emphasizes SQL Server to prevent the generation of incompatible syntax
4. **No Markdown**: Explicitly requests no markdown formatting to reduce parsing issues

## Fallback Mechanisms

Despite the carefully engineered prompt, the system includes fallback parsing strategies:

1. **JSON Parsing**: Primary approach for extracting structured information
2. **Regex Extraction**: Secondary approach that looks for SQL patterns when JSON parsing fails
3. **Error Messages**: Informative errors when neither approach succeeds

## Customization Options

The prompt can be customized for different scenarios:

### For Complex Schemas
Add more detailed relationship descriptions:
```
Table relationships and common join conditions:
[table1] JOIN [table2] ON [table1].[column] = [table2].[column] (purpose: link orders to details)
```

### For Performance Focus
Add index information:
```
Indexed columns:
Table: [table_name]
  - [column_name] (indexed: primary key)
  - [column_name] (indexed: yes)
```

### For Different SQL Dialects
Simply change the role and specific instructions:
```
As a PostgreSQL expert...
```

## Testing and Refinement

The prompt has been refined through testing with various query types:
- Simple selection queries
- Filtering and sorting
- Aggregation queries
- Multi-table joins
- Date-based filtering
- Subqueries and complex conditions

Each test helped refine the guidelines and schema format to improve accuracy and usability.

## Conclusion

Effective prompt engineering is the key to successful natural language to SQL conversion. The system's prompt balances:
- Comprehensive schema information
- Clear instructions
- Structured response format
- Error prevention strategies

This approach maximizes the AI's ability to generate accurate, useful SQL from natural language while minimizing errors and response parsing issues. 