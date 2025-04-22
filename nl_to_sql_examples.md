# Natural Language to SQL: Example Queries

This document provides examples of natural language queries and their SQL equivalents to help you effectively use the NL to SQL feature.

## Basic Queries

### Example 1: Simple Selection

**Natural Language:**
```
Show me the first 10 orders
```

**Generated SQL:**
```sql
SELECT TOP 10 *
FROM SUS_ORDER_TRANS_HDR
ORDER BY ORDER_HDR_ID
```

### Example 2: Filtering

**Natural Language:**
```
Find all orders with strength greater than 5
```

**Generated SQL:**
```sql
SELECT *
FROM NEW_ATTRIBUTES_TBL_HIST
WHERE ORDERSTRENGTH > 5
ORDER BY ORDERSTRENGTH DESC
```

### Example 3: Aggregation

**Natural Language:**
```
What is the average order strength by ingredient group?
```

**Generated SQL:**
```sql
SELECT 
    i.INGRD_GRP_NM AS 'Ingredient Group',
    AVG(h.ORDERSTRENGTH) AS 'Average Order Strength'
FROM 
    NEW_ATTRIBUTES_TBL_HIST h
    INNER JOIN SUS_INGRD_FMLY_GRP i ON i.INGRD_GRP_ID = h.INGRD_GRP_ID
GROUP BY 
    i.INGRD_GRP_NM
ORDER BY 
    'Average Order Strength' DESC
```

## Intermediate Queries

### Example 4: Multiple Tables

**Natural Language:**
```
Show me orders with their journal comments and ingredient groups
```

**Generated SQL:**
```sql
SELECT 
    h.ORDER_CD AS 'Order Number',
    i.INGRD_GRP_NM AS 'Ingredient Group',
    j.ORDER_JRNL_CMT_TXT AS 'Journal Comment',
    a.ORDERSTRENGTH AS 'Order Strength'
FROM 
    SUS_ORDER_TRANS_HDR h
    INNER JOIN SUS_ORDER_TRANS_DETL d ON h.ORDER_HDR_ID = d.ORDER_HDR_ID
    INNER JOIN SUS_ORDER_JRNL j ON j.ORDER_HDR_ID = d.ORDER_HDR_ID AND j.INGRD_GRP_ID = d.INGRD_GRP_ID
    INNER JOIN SUS_INGRD_FMLY_GRP i ON i.INGRD_GRP_ID = d.INGRD_GRP_ID
    INNER JOIN NEW_ATTRIBUTES_TBL_HIST a ON a.ORDERNUMBER = h.ORDER_CD AND a.INGRD_GRP_ID = i.INGRD_GRP_ID
ORDER BY 
    h.ORDER_CD DESC
```

### Example 5: Date Filtering

**Natural Language:**
```
Find orders from last month with high strength
```

**Generated SQL:**
```sql
SELECT 
    h.ORDER_CD AS 'Order Number',
    i.INGRD_GRP_NM AS 'Ingredient Group',
    a.ORDERSTRENGTH AS 'Order Strength',
    h.ORDER_DT AS 'Order Date'
FROM 
    SUS_ORDER_TRANS_HDR h
    INNER JOIN SUS_ORDER_TRANS_DETL d ON h.ORDER_HDR_ID = d.ORDER_HDR_ID
    INNER JOIN SUS_INGRD_FMLY_GRP i ON i.INGRD_GRP_ID = d.INGRD_GRP_ID
    INNER JOIN NEW_ATTRIBUTES_TBL_HIST a ON a.ORDERNUMBER = h.ORDER_CD AND a.INGRD_GRP_ID = i.INGRD_GRP_ID
WHERE 
    h.ORDER_DT >= DATEADD(MONTH, -1, GETDATE())
    AND a.ORDERSTRENGTH > 7
ORDER BY 
    a.ORDERSTRENGTH DESC
```

### Example 6: Advanced Aggregation

**Natural Language:**
```
What is the total order strength by month and ingredient group for the past year?
```

**Generated SQL:**
```sql
SELECT 
    YEAR(h.ORDER_DT) AS 'Year',
    MONTH(h.ORDER_DT) AS 'Month',
    i.INGRD_GRP_NM AS 'Ingredient Group',
    SUM(a.ORDERSTRENGTH) AS 'Total Order Strength',
    COUNT(h.ORDER_CD) AS 'Order Count'
FROM 
    SUS_ORDER_TRANS_HDR h
    INNER JOIN SUS_ORDER_TRANS_DETL d ON h.ORDER_HDR_ID = d.ORDER_HDR_ID
    INNER JOIN SUS_INGRD_FMLY_GRP i ON i.INGRD_GRP_ID = d.INGRD_GRP_ID
    INNER JOIN NEW_ATTRIBUTES_TBL_HIST a ON a.ORDERNUMBER = h.ORDER_CD AND a.INGRD_GRP_ID = i.INGRD_GRP_ID
WHERE 
    h.ORDER_DT >= DATEADD(YEAR, -1, GETDATE())
GROUP BY 
    YEAR(h.ORDER_DT),
    MONTH(h.ORDER_DT),
    i.INGRD_GRP_NM
ORDER BY 
    'Year' DESC,
    'Month' DESC,
    'Total Order Strength' DESC
```

## Advanced Queries

### Example 7: Complex Joins with Subqueries

**Natural Language:**
```
Find the top 5 ingredient groups by average order strength that have more than 10 orders
```

**Generated SQL:**
```sql
SELECT TOP 5
    i.INGRD_GRP_NM AS 'Ingredient Group',
    AVG(a.ORDERSTRENGTH) AS 'Average Strength',
    COUNT(h.ORDER_CD) AS 'Order Count'
FROM 
    SUS_INGRD_FMLY_GRP i
    INNER JOIN NEW_ATTRIBUTES_TBL_HIST a ON i.INGRD_GRP_ID = a.INGRD_GRP_ID
    INNER JOIN SUS_ORDER_TRANS_HDR h ON h.ORDER_CD = a.ORDERNUMBER
GROUP BY 
    i.INGRD_GRP_NM
HAVING 
    COUNT(h.ORDER_CD) > 10
ORDER BY 
    'Average Strength' DESC
```

### Example 8: Trend Analysis

**Natural Language:**
```
Show me how order strengths have trended over the last 12 periods
```

**Generated SQL:**
```sql
SELECT 
    a.ORDERNUMBER AS 'Order Number',
    i.INGRD_GRP_NM AS 'Ingredient Group',
    a.TREND_LAG1_STRNT AS 'Period 1',
    a.TREND_LAG2_STRNT AS 'Period 2',
    a.TREND_LAG3_STRNT AS 'Period 3',
    a.TREND_LAG4_STRNT AS 'Period 4',
    a.TREND_LAG5_STRNT AS 'Period 5',
    a.TREND_LAG6_STRNT AS 'Period 6',
    a.TREND_LAG7_STRNT AS 'Period 7',
    a.TREND_LAG8_STRNT AS 'Period 8',
    a.TREND_LAG9_STRNT AS 'Period 9',
    a.TREND_LAG10_STRNT AS 'Period 10',
    a.TREND_LAG11_STRNT AS 'Period 11',
    a.TREND_LAG12_STRNT AS 'Period 12'
FROM 
    NEW_ATTRIBUTES_TBL_HIST a
    INNER JOIN SUS_INGRD_FMLY_GRP i ON i.INGRD_GRP_ID = a.INGRD_GRP_ID
ORDER BY 
    a.ORDERNUMBER DESC
```

### Example 9: Pivot/Cross-Tab Analysis

**Natural Language:**
```
Create a pivot table showing the average strength by ingredient group and approval type
```

**Generated SQL:**
```sql
SELECT 
    i.INGRD_GRP_NM AS 'Ingredient Group',
    AVG(CASE WHEN k.ORDER_JRNL_TYP_TXT = 'First Approval' THEN a.ORDERSTRENGTH ELSE NULL END) AS 'First Approval Avg',
    AVG(CASE WHEN k.ORDER_JRNL_TYP_TXT = 'Second Approval' THEN a.ORDERSTRENGTH ELSE NULL END) AS 'Second Approval Avg',
    AVG(CASE WHEN k.ORDER_JRNL_TYP_TXT = 'Release' THEN a.ORDERSTRENGTH ELSE NULL END) AS 'Release Avg',
    AVG(CASE WHEN k.ORDER_JRNL_TYP_TXT = 'Comment' THEN a.ORDERSTRENGTH ELSE NULL END) AS 'Comment Avg',
    AVG(a.ORDERSTRENGTH) AS 'Overall Avg'
FROM 
    NEW_ATTRIBUTES_TBL_HIST a
    INNER JOIN SUS_INGRD_FMLY_GRP i ON i.INGRD_GRP_ID = a.INGRD_GRP_ID
    INNER JOIN SUS_ORDER_TRANS_HDR h ON h.ORDER_CD = a.ORDERNUMBER
    INNER JOIN SUS_ORDER_JRNL j ON j.ORDER_HDR_ID = h.ORDER_HDR_ID AND j.INGRD_GRP_ID = i.INGRD_GRP_ID
    INNER JOIN SUS_ORDER_JRNL_TYP k ON k.ORDER_JRNL_TYP_ID = j.ORDER_JRNL_TYP_ID
GROUP BY 
    i.INGRD_GRP_NM
ORDER BY 
    'Overall Avg' DESC
```

## Using the SQL Editor with Autocomplete

The SQL Editor includes intelligent autocomplete functionality that helps you write and edit queries more efficiently. This feature suggests tables, columns, and SQL keywords as you type.

### How to Use Autocomplete

1. **Start typing**: Begin typing a table name, column name, or SQL keyword
2. **View suggestions**: After typing at least 2 characters, a suggestion box appears with matching items
3. **Navigate suggestions**: Use the up and down arrow keys to move through the suggestions
4. **Select a suggestion**: Press Tab or Enter to select the highlighted suggestion, or click on it with your mouse
5. **Table-specific columns**: Type a table name followed by a period (e.g., `SUS_ORDER_TRANS_HDR.`) to see only columns from that table

### Keyboard Shortcuts

| Key(s) | Action |
|--------|--------|
| **Up/Down Arrow** | Navigate through suggestions |
| **Tab** | Select the highlighted suggestion (or first item if none highlighted) |
| **Enter** | Select the highlighted suggestion |
| **Escape** | Close the suggestion box |

### Suggestion Types

The autocomplete feature suggests:

1. **Tables**: All tables in the database
2. **Columns**: All columns across all tables
3. **Table-specific columns**: Only columns from a specific table when typing after `tablename.`
4. **SQL Keywords**: Common SQL keywords like SELECT, FROM, WHERE, JOIN, etc.

### Examples of Using Autocomplete

#### Example 1: General Suggestions

Start typing:
```sql
SEL
```

Suggestions appear:
- SELECT
- INNER JOIN
- SUS_ORDER_TRANS_DETL
- ...

#### Example 2: Table-Specific Columns

Start typing:
```sql
SELECT * FROM SUS_ORDER_TRANS_HDR h WHERE h.
```

Suggestions show only columns from SUS_ORDER_TRANS_HDR:
- ORDER_HDR_ID
- ORDER_CD
- ORDER_DT
- ...

#### Example 3: Refining Suggestions

Start typing:
```sql
SELECT i.INGRD
```

Suggestions narrow to matching columns:
- INGRD_GRP_ID
- INGRD_GRP_NM
- ...

### Tips for Using Autocomplete Effectively

1. **Use table aliases**: Assign short aliases to tables (e.g., `SUS_ORDER_TRANS_HDR h`) to make column access more concise
2. **Type the beginning of words**: Suggestions appear after typing at least 2 characters
3. **Use the keyboard**: The Tab key quickly inserts suggestions without disrupting your workflow
4. **Explore available columns**: Type a table name and period to explore what columns are available
5. **Learn common keywords**: The system suggests SQL keywords to help you structure your queries correctly

## Tips for Effective Natural Language Queries

1. **Be specific** about what data you want to see:
   - "Show orders from last month" is better than "Show recent orders"

2. **Use common words** for SQL operations:
   - "Find the average order strength" for AVG()
   - "Count the number of orders" for COUNT()
   - "Find orders with strength more than 5" for WHERE ORDERSTRENGTH > 5

3. **Include table relationships** if you know them:
   - "Show orders and their journal comments" indicates you want to join these tables

4. **Specify order** when relevant:
   - "Show orders with highest strength first" for ORDER BY ORDERSTRENGTH DESC

5. **Include time periods** clearly:
   - "Orders from last month" or "Orders in 2023"
   - "Trend over 12 periods"

6. **Mention column names** similar to how they appear in the database:
   - "order strength" for ORDERSTRENGTH
   - "journal comments" for ORDER_JRNL_CMT_TXT

7. **Remember** to review and potentially edit the generated SQL before execution! 