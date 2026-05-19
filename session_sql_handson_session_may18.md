# SQL Hands-On Learning Session — May 18, 2026

## Overview
Learning SQL from scratch by building real tables with data, then querying them. Interview prep for .NET/C#/SQL junior position on May 20 at 13:00.

---

## Initial Setup

### Project Context
- Using `EmployeeApi` project (ASP.NET Core Web API, already bootstrapped with EF Core SQLite packages)
- Tonight's focus: SQL from zero (5 hours allocated)
- Study plan: Hands-on practice, then read the theory later

### Getting SQLite Running on Windows

**Problem:** `sqlite3` command not recognized in PowerShell.

**Solution:** Download precompiled binary
1. Go to https://www.sqlite.org/download.html
2. Under "Precompiled Binaries for Windows", download `sqlite-tools-win-x64-*.zip`
3. Unzip to `C:\sqlite\` (or any simple path)
4. Run from project folder:
   ```powershell
   C:\sqlite\sqlite3.exe practice.db
   ```

**Result:** SQLite 3.53.1 shell opens with prompt `sqlite>`

---

## Creating the Database Schema

### Table 1: `customers`

```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    city TEXT
);
```

**Breakdown:**
- `id`: Unique identifier for each customer. `PRIMARY KEY` = main identifier, no duplicates allowed. `AUTOINCREMENT` = database auto-assigns next number (1, 2, 3...).
- `name`: Text field. `NOT NULL` = mandatory, can't be blank.
- `email`: Text field. Optional (can be NULL).
- `city`: Text field. Optional.

### Table 2: `orders`

```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    total DECIMAL(10,2),
    status TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
```

**Breakdown:**
- `id`: Unique order identifier.
- `customer_id`: Links to the `customers` table. Must reference an actual customer id.
- `total`: `DECIMAL(10,2)` = number with up to 10 digits total, 2 after decimal. Good for money (prevents floating-point errors).
- `status`: Text ('completed', 'pending', etc.).
- **`FOREIGN KEY (customer_id) REFERENCES customers(id)`**: The database enforces referential integrity — you cannot create an order for a customer that doesn't exist. This prevents orphaned data.

---

## Understanding FOREIGN KEY Constraint

### Why It Matters

**Without constraint (bad):**
```sql
INSERT INTO orders (customer_id, total, status) VALUES
(99, 500.00, 'completed');  -- customer 99 doesn't exist, but INSERT succeeds anyway
```
Result: Orphaned order. Your code tries to fetch customer 99, gets NULL. Bugs.

**With constraint (good):**
```sql
INSERT INTO orders (customer_id, total, status) VALUES
(99, 500.00, 'completed');  -- SQLite checks if customer 99 exists → NO → INSERT FAILS
```
Result: Database protects itself. Consistency guaranteed.

### Key Point: Referential Integrity
The database enforces rules, not just your code. This is why relational databases are powerful.

---

## Inserting Sample Data

### Customers (4 total)

```sql
INSERT INTO customers (name, email, city) VALUES
('Marino', 'marino@email.com', 'Zagreb'),
('Ana', 'ana@email.com', 'Split'),
('Ivan', 'ivan@email.com', 'Zagreb'),
('Petra', 'petra@email.com', 'Rijeka');
```

**IDs assigned automatically:** 1, 2, 3, 4

### Orders (5 total)

```sql
INSERT INTO orders (customer_id, total, status) VALUES
(1, 250.00, 'completed'),
(1, 100.00, 'completed'),
(2, 450.00, 'completed'),
(2, 80.00, 'pending'),
(3, 999.00, 'completed');
```

**Order breakdown:**
- Marino (id=1): 2 orders
- Ana (id=2): 2 orders
- Ivan (id=3): 1 order
- Petra (id=4): **0 orders** ← Intentional, used later for LEFT JOIN examples

---

## SQL Case Sensitivity

**SQL keywords are case-insensitive:**
```sql
-- All equivalent:
CREATE TABLE customers (...)
create table customers (...)
CrEaTe TaBlE customers (...)
```

**Convention:** Capitalize SQL keywords (CREATE, TABLE, SELECT, WHERE, etc.), lowercase user-defined names (table names, column names). Makes code easier to read.

```sql
-- Standard style
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);
```

---

## Why This Matters for Interview

This is **real database structure**, not theory. Your EmployeeApi project will mirror this:
- `Employees` table (like `customers`)
- `Departments` table (like `customers`)
- Linking tables with FOREIGN KEYs

When you write SQL queries against this database, you're learning the exact patterns you'll use in your .NET project with Entity Framework Core.

---

## INSERT INTO Syntax Deep Dive

### Basic Structure

```sql
INSERT INTO customers (name, email, city) VALUES ('Marino', 'marino@email.com', 'Zagreb');
```

**Breakdown:**

1. **`INSERT INTO customers`** — "Add a new row to the `customers` table"
2. **`(name, email, city)`** — "I'm providing values for these specific columns" (NOT id, because it auto-increments)
3. **`VALUES (...)`** — "Here are the actual values for those columns"

**Key Rule:** Column order in the statement must match VALUES order. The database doesn't care what that order is — you define it.

### Why Specify Columns?

- **Explicit:** No ambiguity about which value goes where
- **Flexible:** Can skip optional columns (they'll be NULL)
- **Safe:** Protects against column order changes in the future
- **Professional:** This is how real code does it

### Can You Reorder Columns?

**Yes!** Example:

```sql
INSERT INTO customers (city, name, email) VALUES ('Zagreb', 'Marino', 'marino@email.com');
```

SQLite matches by position. You can skip columns too:

```sql
INSERT INTO customers (email, name) VALUES ('marino@email.com', 'Marino');
-- city will be NULL
```

### Multi-Row Insert (What We Did)

```sql
INSERT INTO customers (name, email, city) VALUES
('Marino', 'marino@email.com', 'Zagreb'),
('Ana', 'ana@email.com', 'Split'),
('Ivan', 'ivan@email.com', 'Zagreb'),
('Petra', 'petra@email.com', 'Rijeka');
```

Each line is a separate row, separated by commas. Faster and cleaner than 4 separate INSERT statements.

---

## Basic SELECT Queries with WHERE

### Verified Data

Ran `SELECT * FROM customers;` — all 4 customers present with auto-generated ids (1-4).

### WHERE Clause — Filtering Rows

WHERE lets you filter which rows you get back.

#### Basic Equality

```sql
SELECT * FROM customers WHERE city = 'Zagreb';
-- Returns: Marino (id=1) and Ivan (id=3) — 2 rows
```

```sql
SELECT * FROM customers WHERE name = 'Ana';
-- Returns: Ana (id=2) — 1 row
```

#### NOT Equal

```sql
SELECT * FROM customers WHERE city != 'Zagreb';
-- Returns: Ana (Split) and Petra (Rijeka) — 2 rows
-- Alternative: WHERE NOT city = 'Zagreb'
```

#### LIKE — Pattern Matching

```sql
SELECT * FROM customers WHERE email LIKE '%a%';
-- Returns: All customers with 'a' in their email — case insensitive
-- % = "any characters", _ = "exactly one character"
```

---

## Queries Against Orders Table

### See All Orders

```sql
SELECT * FROM orders;
-- Returns all 5 orders
```

Data recap:
- Order 1: customer_id=1, total=250.00, status='completed'
- Order 2: customer_id=1, total=100.00, status='completed'
- Order 3: customer_id=2, total=450.00, status='completed'
- Order 4: customer_id=2, total=80.00, status='pending'
- Order 5: customer_id=3, total=999.00, status='completed'

### Filter by Status

```sql
SELECT * FROM orders WHERE status = 'completed';
-- Returns: Orders 1, 2, 3, 5 — 4 rows
```

### Filter by Number (No Quotes!)

```sql
SELECT * FROM orders WHERE total > 100;
-- Returns: Orders 1, 3, 5 — 3 rows
-- Note: No quotes around 100 — it's a number, not text
```

### Filter by Customer

```sql
SELECT * FROM orders WHERE customer_id = 1;
-- Returns: Orders 1 and 2 (both from Marino) — 2 rows
```

### AND — Both Conditions Must Be True

```sql
SELECT * FROM orders WHERE status = 'pending' AND total < 100;
-- Returns: Order 4 (pending AND total=80.00 which is < 100) — 1 row
```

### OR — At Least One Condition Is True

```sql
SELECT * FROM orders WHERE status = 'pending' OR total > 400;
-- Returns: Order 4 (pending) and Order 3 (total=450 > 400) — 2 rows
```

---

## Key Concepts So Far

1. **Columns are flexible:** You define the order when inserting
2. **WHERE filters rows:** Based on conditions you specify
3. **Data types matter:** Text in quotes (`'Zagreb'`), numbers without (`250.00`)
4. **NULL is handled:** Skip a column in INSERT, it becomes NULL
5. **Pattern matching:** LIKE with `%` and `_`
6. **Logical operators:** AND (both true), OR (at least one true), NOT (opposite)

---

## Aggregate Functions — Summaries Instead of Details

Aggregate functions collapse many rows into **one result** (or one per group).

### COUNT — How Many Rows?

```sql
SELECT COUNT(*) FROM orders;
-- Returns: 5 (total number of orders)

SELECT COUNT(*) FROM orders WHERE status = 'completed';
-- Returns: 4 (completed orders only)

SELECT COUNT(customer_id) FROM orders;
-- Returns: 5 (count non-NULL values in customer_id column)
```

### SUM — Add Up a Column

```sql
SELECT SUM(total) FROM orders;
-- Returns: 1879 (250 + 100 + 450 + 80 + 999)

SELECT SUM(total) FROM orders WHERE customer_id = 1;
-- Returns: 350 (only Marino's orders)
```

### AVG — Average Value

```sql
SELECT AVG(total) FROM orders;
-- Returns: 375.8 (1879 / 5)
```

### MIN, MAX — Smallest and Largest

```sql
SELECT MIN(total), MAX(total) FROM orders;
-- Returns: 80, 999
```

---

## GROUP BY — Split Data Into Groups

GROUP BY groups rows and applies aggregate functions to each group.

### Basic Example: Total Spent Per Customer

```sql
SELECT customer_id, SUM(total) FROM orders GROUP BY customer_id;
```

**Result:**
| customer_id | SUM(total) |
|-------------|-----------|
| 1           | 350       |
| 2           | 530       |
| 3           | 999       |

(Customer 4/Petra doesn't appear — no orders)

### Count Orders Per Customer

```sql
SELECT customer_id, COUNT(*) FROM orders GROUP BY customer_id;
```

| customer_id | COUNT(*) |
|-------------|---------|
| 1           | 2       |
| 2           | 2       |
| 3           | 1       |

### Average Order Value Per Customer

```sql
SELECT customer_id, AVG(total) FROM orders GROUP BY customer_id;
```

### Min and Max Per Customer

```sql
SELECT customer_id, MIN(total), MAX(total) FROM orders GROUP BY customer_id;
```

### Group by Status

```sql
SELECT status, COUNT(*) FROM orders GROUP BY status;
```

| status      | COUNT(*) |
|------------|---------|
| completed  | 4       |
| pending    | 1       |

---

## HAVING — Filter Groups (Not Rows)

WHERE filters **individual rows** before grouping. HAVING filters **groups** after grouping.

### WHERE (Before Grouping)

```sql
SELECT customer_id, COUNT(*) FROM orders 
WHERE total > 100 
GROUP BY customer_id;
```

Process:
1. Filter rows: Keep only orders with total > 100
2. Group those filtered rows by customer_id
3. Count each group

### HAVING (After Grouping)

```sql
SELECT customer_id, SUM(total) FROM orders 
GROUP BY customer_id 
HAVING SUM(total) > 500;
```

Process:
1. Group all orders by customer_id
2. Calculate SUM(total) for each group
3. Filter groups: Show only those with SUM > 500

**Result:** customer_id 2 (530) and customer_id 3 (999)

### More HAVING Examples

```sql
SELECT customer_id, COUNT(*) FROM orders 
GROUP BY customer_id 
HAVING COUNT(*) > 1;
-- Show customers with more than 1 order (customer_id 1 and 2)
```

```sql
SELECT status, AVG(total) FROM orders 
GROUP BY status 
HAVING AVG(total) > 200;
-- Show statuses with average order value > 200
```

**Key Rule:** You can't use HAVING without GROUP BY. You can use WHERE without GROUP BY.

---

## JOINs — Connecting Multiple Tables

### Why JOINs Matter

You have related data in separate tables (customers, orders). JOINs combine them based on a linking column (the FOREIGN KEY).

Example: "Show me customer names with their orders"
- Customer data is in `customers` table
- Order data is in `orders` table
- They link via `customer_id` (FOREIGN KEY in orders → PRIMARY KEY in customers)

---

### The JOIN Formula (Memorize This)

```sql
SELECT [columns]
FROM [table1]
[JOIN_TYPE] JOIN [table2] ON [table1.id] = [table2.foreign_key_id];
```

**Real example:**

```sql
SELECT customers.customer_name, orders.product_name
FROM customers
LEFT JOIN orders ON customers.customer_id = orders.customer_id;
```

**Structure breakdown:**
- `FROM customers` — Start with the main table (left table)
- `LEFT JOIN orders` — Add the other table (right table)
- `ON customers.customer_id = orders.customer_id` — How they link (primary key = foreign key)

---

### INNER JOIN — Only Matching Rows

```sql
SELECT customers.customer_name, orders.product_name
FROM customers
INNER JOIN orders ON customers.customer_id = orders.customer_id;
```

**Logic:**
- Returns only rows where a match exists in both tables
- If a customer has no orders, they're excluded
- If an order has no matching customer, it's excluded

**Result:** 5 rows (Alice, Alice, Bob, Carol, Emily — no Luffy)

**When to use:** "Show me customers who have orders"

---

### LEFT JOIN — All Left Table + Matching Right Table

```sql
SELECT customers.customer_name, orders.product_name
FROM customers
LEFT JOIN orders ON customers.customer_id = orders.customer_id;
```

**Logic:**
- Returns ALL rows from the left table (customers)
- Adds matching rows from the right table (orders)
- If no match, fills right table columns with NULL

**Result:** 6 rows (Alice, Alice, Bob, Carol, Emily, Luffy with NULL product_name)

**When to use:** "Show me all customers with their orders, even if they haven't ordered"

**Most common JOIN type in real work.**

---

### RIGHT JOIN — All Right Table + Matching Left Table

```sql
SELECT customers.customer_name, orders.product_name
FROM customers
RIGHT JOIN orders ON customers.customer_id = orders.customer_id;
```

**Logic:**
- Returns ALL rows from the right table (orders)
- Adds matching rows from the left table (customers)
- If no match, fills left table columns with NULL

**Note:** Rarely used in practice. You can usually flip the tables and use LEFT JOIN instead.

---

### FULL OUTER JOIN — All Rows from Both Tables

```sql
SELECT customers.customer_name, orders.product_name
FROM customers
FULL OUTER JOIN orders ON customers.customer_id = orders.customer_id;
```

**Logic:**
- Returns ALL rows from both tables
- Matches where possible, NULL where not

**Note:** SQLite doesn't support FULL OUTER JOIN natively. Use UNION instead (advanced).

---

### CROSS JOIN — Cartesian Product

```sql
SELECT customers.customer_name, orders.product_name
FROM customers
CROSS JOIN orders;
```

**Logic:**
- Combines every row from left table with every row from right table
- No ON clause needed
- Result: (# left rows) × (# right rows) combinations

**Example:** 6 customers × 5 orders = 30 rows (often useless)

---

### JOIN Quick Reference

| JOIN Type | Keeps | Use When | Example |
|-----------|-------|----------|---------|
| **INNER** | Only matches | "customers who have orders" | `INNER JOIN orders ON ...` |
| **LEFT** | All left + matches | "all customers with their orders" | `LEFT JOIN orders ON ...` |
| **RIGHT** | All right + matches | "all orders with their customers" | `RIGHT JOIN orders ON ...` |
| **FULL OUTER** | All rows both tables | "all customers and all orders" | `FULL OUTER JOIN orders ON ...` |
| **CROSS** | Every combination | Rare, generating all combinations | `CROSS JOIN orders` |

---

## Combining JOINs with Aggregate Functions and GROUP BY

### Example: Customer names with order count and total spent

```sql
SELECT customers.customer_name, COUNT(orders.order_id) as order_count, SUM(orders.total) as total_spent
FROM customers
LEFT JOIN orders ON customers.customer_id = orders.customer_id
GROUP BY customers.customer_id;
```

**Result:**

| customer_name | order_count | total_spent |
|---------------|------------|------------|
| Alice Smith   | 2          | 1250.00    |
| Bob Johnson   | 1          | 800.00     |
| Carol Williams| 1          | 1500.00    |
| David Brown   | 0          | NULL       |
| Emily Davis   | 1          | 950.00     |
| Luffy         | 0          | NULL       |

**Flow:**
1. LEFT JOIN keeps all customers
2. GROUP BY groups them
3. Aggregate functions count and sum their orders

---

## Parentheses — When and Why

### 1. Function Arguments (REQUIRED)

```sql
SELECT COUNT(*) FROM orders;
SELECT SUM(total) FROM orders;
SELECT AVG(price) FROM products;
SELECT MAX(quantity) FROM orders;
```

Parentheses are **mandatory** for functions to work.

---

### 2. Math Expressions (Optional but Clear)

```sql
SELECT (quantity * price) as total FROM orders;
SELECT quantity * price FROM orders;  -- Same result, less clear
```

Parentheses clarify order of operations. Both work, but parentheses are more readable.

---

### 3. Grouping Conditions (Optional but Recommended)

```sql
-- Ambiguous:
SELECT * FROM orders 
WHERE status = 'pending' OR status = 'completed' AND total > 100;

-- Clear:
SELECT * FROM orders 
WHERE (status = 'pending') OR (status = 'completed' AND total > 100);
```

Parentheses clarify which conditions go together with AND/OR.

---

### 4. Subqueries (REQUIRED)

```sql
SELECT * FROM (
  SELECT customer_id, SUM(total) as total_spent 
  FROM orders 
  GROUP BY customer_id
) as customer_totals;
```

Inner query must be in parentheses.

---

### Where Parentheses Do NOT Go

❌ **Selecting multiple columns — WRONG:**

```sql
SELECT (customer_name, product_name) FROM customers;
```

✅ **Correct:**

```sql
SELECT customer_name, product_name FROM customers;
```

---

### Parentheses Summary

| Use Case | Example | Required? |
|----------|---------|-----------|
| Function arguments | `COUNT(*)`, `SUM(total)` | ✅ Yes |
| Math expressions | `(price * qty)` | ❌ No (but good for clarity) |
| Grouping conditions | `(status = 'A') AND (total > 100)` | ❌ No (but recommended) |
| Subqueries | `FROM (SELECT ...)` | ✅ Yes |
| **Column lists** | `SELECT (col1, col2)` | ❌ **NO — WRONG** |

---

## BETWEEN — Range Filtering

BETWEEN filters values within a range (inclusive on both ends).

### Basic Syntax

```sql
SELECT * FROM orders WHERE total BETWEEN 100 AND 500;
```

**Logic:**
- Returns rows where `total` is >= 100 AND <= 500 (inclusive)
- Equivalent to: `WHERE total >= 100 AND total <= 500`

**Example results:** Orders with total 100.00, 250.00, 450.00 (within range)

### NOT BETWEEN

```sql
SELECT * FROM orders WHERE total NOT BETWEEN 100 AND 500;
```

Returns orders outside the range (80.00, 999.00).

### Works with Text Too

```sql
SELECT * FROM customers WHERE name BETWEEN 'A' AND 'M';
```

Returns names starting with A-L (alphabetically).

---

## Aliases with AS — Renaming Columns and Tables

AS renames columns or tables in the output. Useful for clarity and combining data.

### Column Aliases

```sql
SELECT 
  customers.name AS customer_name,
  orders.total AS order_amount,
  orders.status AS order_status
FROM customers
LEFT JOIN orders ON customers.id = orders.customer_id;
```

**Without aliases:** Column headers are `name`, `total`, `status`

**With aliases (AS):** Column headers become `customer_name`, `order_amount`, `order_status`

Clearer for reading and exporting data!

### Table Aliases

Shortens table names in queries, especially useful in JOINs:

```sql
SELECT c.name, o.total
FROM customers AS c
LEFT JOIN orders AS o ON c.id = o.customer_id;
```

Instead of `customers.name`, write `c.name`. Saves typing.

### Aggregate Function with Alias

```sql
SELECT 
  customer_id, 
  COUNT(*) AS order_count, 
  SUM(total) AS total_spent
FROM orders
GROUP BY customer_id;
```

| customer_id | order_count | total_spent |
|-------------|------------|------------|
| 1           | 2          | 350.00     |
| 2           | 2          | 530.00     |
| 3           | 1          | 999.00     |

---

## Composite Keys — Multiple Columns as Primary Key

A composite key uses **multiple columns together** to uniquely identify a row.

### Creating a Table with Composite Key

```sql
CREATE TABLE enrollments (
    student_id INTEGER,
    course_id INTEGER,
    semester TEXT,
    grade TEXT,
    PRIMARY KEY (student_id, course_id, semester)
);
```

**The composite key is:** `PRIMARY KEY (student_id, course_id, semester)`

Multiple columns in parentheses, separated by commas.

### What the Data Looks Like

```sql
INSERT INTO enrollments (student_id, course_id, semester, grade) VALUES
(1, 101, 'Fall2024', 'A'),
(1, 102, 'Fall2024', 'B'),
(1, 101, 'Spring2025', 'A+'),
(2, 101, 'Fall2024', 'B+'),
(2, 102, 'Fall2024', 'A');
```

**Result:**

| student_id | course_id | semester    | grade |
|------------|-----------|-------------|-------|
| 1          | 101       | Fall2024    | A     |
| 1          | 102       | Fall2024    | B     |
| 1          | 101       | Spring2025  | A+    |
| 2          | 101       | Fall2024    | B+    |
| 2          | 102       | Fall2024    | A     |

**Why it works:**
- Student 1 appears in rows 1, 2, 3 — that's OK (different course or semester)
- Course 101 appears in rows 1, 3, 4 — that's OK (different student or semester)
- BUT no row has the same `(student_id, course_id, semester)` combination twice ✅

### What Violates the Composite Key?

```sql
INSERT INTO enrollments (student_id, course_id, semester, grade) VALUES
(1, 101, 'Fall2024', 'B');  -- ERROR! (1, 101, Fall2024) already exists
```

SQLite rejects it. The combination must be unique.

### Single vs Composite Primary Key

**Single Primary Key:**
```sql
CREATE TABLE students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
);
```

One column uniquely identifies a row.

**Composite Primary Key:**
```sql
CREATE TABLE enrollments (
    student_id INTEGER,
    course_id INTEGER,
    semester TEXT,
    PRIMARY KEY (student_id, course_id, semester)
);
```

Multiple columns together uniquely identify a row. No AUTOINCREMENT (you provide the values).

### Interview Answer

> "A composite key is a primary key made of multiple columns. Used when no single column is unique by itself, but a combination of columns is. For example, in an enrollments table, (student_id, course_id, semester) together uniquely identify a student's grade in a specific course during a semester."

---

## Normalization — How to Design Tables Properly

Normalization avoids data duplication and inconsistency. There are 3 main levels: 1NF, 2NF, 3NF.

### 1NF (First Normal Form) — Atomic Values

**Rule:** Each cell contains only ONE value, not a list.

**Bad (violates 1NF):**

```
orders table:
order_id | customer_name | products
---------|---------------|------------------
1        | Marino        | Laptop, Mouse, Keyboard
2        | Ana           | Monitor, Keyboard
```

The `products` column has multiple values in one cell. Hard to query ("give me all orders with Laptop").

**Good (follows 1NF):**

```
orders table:
order_id | customer_name | product
---------|---------------|----------
1        | Marino        | Laptop
1        | Marino        | Mouse
1        | Marino        | Keyboard
2        | Ana           | Monitor
2        | Ana           | Keyboard
```

Each row has ONE product. Easy to query.

---

### 2NF (Second Normal Form) — No Partial Dependencies

**Rule:** If you have a composite primary key, all non-key columns must depend on the **ENTIRE** key, not just part of it.

**Bad (violates 2NF):**

```sql
CREATE TABLE order_items (
    order_id INTEGER,
    item_number INTEGER,
    product_name TEXT,
    product_price DECIMAL,
    quantity INTEGER,
    PRIMARY KEY (order_id, item_number)
);
```

**Data:**

| order_id | item_number | product_name | product_price | quantity |
|----------|-------------|--------------|---------------|----------|
| 1        | 1           | Laptop       | 999.00        | 1        |
| 1        | 2           | Mouse        | 25.00         | 2        |
| 2        | 1           | Laptop       | 999.00        | 1        |

**Problem:**
- `product_price` depends on `product_name`, NOT on the entire key `(order_id, item_number)`
- You repeat "Laptop = 999.00" in rows 1 and 3
- If Laptop's price changes, you update it in multiple places → **data inconsistency**

This is a **partial dependency** (depends on only part of the key).

**Good (follows 2NF):**

Split into two tables:

```sql
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT,
    product_price DECIMAL
);

CREATE TABLE order_items (
    order_id INTEGER,
    item_number INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    PRIMARY KEY (order_id, item_number),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
```

**products:**

| product_id | product_name | product_price |
|------------|--------------|---------------|
| 1          | Laptop       | 999.00        |
| 2          | Mouse        | 25.00         |

**order_items:**

| order_id | item_number | product_id | quantity |
|----------|-------------|------------|----------|
| 1        | 1           | 1          | 1        |
| 1        | 2           | 2          | 2        |
| 2        | 1           | 1          | 1        |

**Now:**
- `product_id` depends on the entire key `(order_id, item_number)` ✅
- `product_price` is in products table, not order_items ✅
- Change Laptop's price once → updates everywhere ✅

---

### 3NF (Third Normal Form) — No Non-Key Dependencies

**Rule:** Non-key columns should depend ONLY on the primary key, not on other non-key columns.

**Bad (violates 3NF):**

```sql
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT,
    city TEXT,
    country TEXT
);
```

**Data:**

| customer_id | customer_name | city   | country |
|------------|---------------|--------|---------|
| 1          | Marino        | Zagreb | Croatia |
| 2          | Ana           | Split  | Croatia |
| 3          | Ivan          | Zagreb | Croatia |

**Problem:**
- `country` depends on `city`, NOT directly on `customer_id`
- Zagreb appears twice with "Croatia" repeated
- If Zagreb changes countries, you update it in multiple places → **data inconsistency**

This is a **non-key dependency** (one non-key column depends on another non-key column).

**Good (follows 3NF):**

Split into two tables:

```sql
CREATE TABLE cities (
    city_id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT,
    country TEXT
);

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT,
    city_id INTEGER,
    FOREIGN KEY (city_id) REFERENCES cities(city_id)
);
```

**cities:**

| city_id | city   | country |
|---------|--------|---------|
| 1       | Zagreb | Croatia |
| 2       | Split  | Croatia |
| 3       | Rijeka | Croatia |

**customers:**

| customer_id | customer_name | city_id |
|------------|---------------|---------|
| 1          | Marino        | 1       |
| 2          | Ana           | 2       |
| 3          | Ivan          | 1       |

**Now:**
- `customer_name` depends on `customer_id` ✅
- `city_id` depends on `customer_id` ✅
- `country` is in cities table, not customers ✅
- Change Zagreb's country once → updates everywhere ✅

---

## Normalization Quick Reference

| Level | Rule | Solves |
|-------|------|--------|
| **1NF** | Atomic values (one value per cell) | Lists in cells (e.g., "Laptop, Mouse") |
| **2NF** | Non-key columns depend on ENTIRE key | Partial dependencies in composite keys |
| **3NF** | Non-key columns depend ONLY on PK | Non-key columns depending on other non-key columns |

**Simple Memory Aid:**
- **2NF:** "Non-key columns depend on the ENTIRE key" (for composite keys)
- **3NF:** "Non-key columns depend ONLY on the primary key, not on other non-key columns"

---

## Interview Answers for Normalization

**"What's a composite key?"**
> "A primary key made of multiple columns. Used when no single column is unique by itself, but a combination of columns is. For example, in an enrollments table, (student_id, course_id, semester) together uniquely identify a student's enrollment."

**"Explain 2NF and 3NF."**
> "2NF removes **partial dependencies**. If you have a composite key, all non-key columns must depend on the entire key, not just part of it. For example, product_price shouldn't be in order_items — it depends only on the product, not the entire key.
>
> 3NF removes **non-key dependencies**. Non-key columns should depend only on the primary key, not on other non-key columns. For example, country shouldn't be in customers — it depends on city, not customer_id.
>
> In both cases, you split into separate tables and use FOREIGN KEYs to link them. This avoids data duplication."

**"Why is normalization important?"**
> "It prevents data inconsistency and redundancy. If you repeat data in multiple places, updating it becomes error-prone. With normalization, you update in one place and it reflects everywhere through foreign keys."

---

---

## ORDER BY — Sort Results

ORDER BY sorts your results in ascending or descending order.

### Basic Syntax

```sql
SELECT * FROM orders ORDER BY total ASC;
```

- `ASC` = ascending (smallest to largest) — DEFAULT
- `DESC` = descending (largest to smallest)

### Example: Lowest to Highest Spending

```sql
SELECT * FROM orders ORDER BY total ASC;
```

**Result (sorted by total, lowest first):**

| order_id | customer_id | total  | status      |
|----------|-------------|--------|------------|
| 4        | 2           | 80.00  | pending    |
| 2        | 1           | 100.00 | completed  |
| 1        | 1           | 250.00 | completed  |
| 3        | 2           | 450.00 | completed  |
| 5        | 3           | 999.00 | completed  |

### Example: Highest to Lowest Spending

```sql
SELECT * FROM orders ORDER BY total DESC;
```

Same table, reversed order (999, 450, 250, 100, 80).

### Sort by Multiple Columns

```sql
SELECT * FROM orders ORDER BY status ASC, total DESC;
```

**Logic:** First sort by status alphabetically ('completed', then 'pending'), then within each status sort by total (high to low).

**Result:**

| order_id | customer_id | total  | status      |
|----------|-------------|--------|------------|
| 5        | 3           | 999.00 | completed  |
| 3        | 2           | 450.00 | completed  |
| 1        | 1           | 250.00 | completed  |
| 2        | 1           | 100.00 | completed  |
| 4        | 2           | 80.00  | pending    |

---

## DISTINCT — Remove Duplicates

DISTINCT removes duplicate rows from results. Useful for finding unique values.

### Basic Syntax

```sql
SELECT DISTINCT city FROM customers;
```

**Without DISTINCT:**

| city   |
|--------|
| Zagreb |
| Split  |
| Zagreb |
| Rijeka |

(4 rows, "Zagreb" appears twice)

**With DISTINCT:**

| city   |
|--------|
| Zagreb |
| Split  |
| Rijeka |

(3 rows, duplicate "Zagreb" removed)

### DISTINCT with Multiple Columns

```sql
SELECT DISTINCT customer_id, status FROM orders;
```

Returns unique combinations of (customer_id, status).

**Example result:**

| customer_id | status      |
|-------------|------------|
| 1           | completed  |
| 2           | completed  |
| 2           | pending    |
| 3           | completed  |

---

## LIMIT — Get First N Rows

LIMIT restricts how many rows you get back. Useful for testing queries and pagination.

### Basic Syntax

```sql
SELECT * FROM orders LIMIT 3;
```

Returns only the first 3 rows.

### LIMIT with ORDER BY — Top N

```sql
SELECT * FROM orders ORDER BY total DESC LIMIT 3;
```

**Get the 3 orders with highest spending:**

| order_id | customer_id | total  | status     |
|----------|-------------|--------|------------|
| 5        | 3           | 999.00 | completed  |
| 3        | 2           | 450.00 | completed  |
| 1        | 1           | 250.00 | completed  |

### LIMIT with OFFSET — Skip Rows

```sql
SELECT * FROM orders ORDER BY total DESC LIMIT 3 OFFSET 2;
```

Skip first 2 rows, then get 3. So you get rows 3, 4, 5.

**Result:**

| order_id | customer_id | total  | status     |
|----------|-------------|--------|------------|
| 1        | 1           | 250.00 | completed  |
| 2        | 1           | 100.00 | completed  |
| 4        | 2           | 80.00  | pending    |

(Useful for pagination: page 1 = LIMIT 10 OFFSET 0, page 2 = LIMIT 10 OFFSET 10, etc.)

---

## Practice: Combine Everything

### Task 1: Get top 2 customers by total spending

```sql
SELECT customer_id, SUM(total) as total_spent
FROM orders
GROUP BY customer_id
ORDER BY total_spent DESC
LIMIT 2;
```

**Expected result:**

| customer_id | total_spent |
|-------------|------------|
| 3           | 999.00     |
| 2           | 530.00     |

### Task 2: Get all customers and their cities, no duplicates

```sql
SELECT DISTINCT c.name, c.city
FROM customers c
ORDER BY c.city ASC;
```

### Task 3: Get customers with pending orders, ordered by spending

```sql
SELECT customer_id, SUM(total) as total_pending
FROM orders
WHERE status = 'pending'
GROUP BY customer_id
ORDER BY total_pending DESC;
```

---

## Interview Summary — Complete SQL Roadmap

Everything your friend said you'd be asked:

| Topic | Status | Key Concepts |
|-------|--------|--------------|
| **JOINs** | ✅ | INNER, LEFT, RIGHT, FULL OUTER, CROSS; ON clause; FK linking |
| **WHERE clause** | ✅ | Filters rows; AND, OR, NOT, LIKE, BETWEEN, comparison operators |
| **BETWEEN** | ✅ | Range filtering (inclusive); works with text too |
| **Aliases (AS)** | ✅ | Rename columns and tables for clarity |
| **FK (Foreign Keys)** | ✅ | FOREIGN KEY constraint; referential integrity; prevents orphaned data |
| **Composites** | ✅ | Composite PRIMARY KEY; multiple columns together as unique identifier |
| **Normalization** | ✅ | 1NF (atomic values), 2NF (no partial deps), 3NF (no non-key deps) |

**Additional SQL skills covered:**
- SELECT, FROM
- Aggregate functions: COUNT, SUM, AVG, MIN, MAX
- GROUP BY, HAVING
- ORDER BY (ASC, DESC, multiple columns)
- DISTINCT
- LIMIT, OFFSET
- Parentheses (functions, math, conditions, subqueries)

---

## Key Formulas to Memorize

**SELECT with WHERE:**
```sql
SELECT columns FROM table WHERE condition;
```

**JOINs (core formula):**
```sql
SELECT columns 
FROM table1 
[INNER|LEFT|RIGHT|FULL] JOIN table2 ON table1.id = table2.fk_id;
```

**GROUP BY with aggregate:**
```sql
SELECT column, COUNT(*) as count
FROM table
GROUP BY column
HAVING COUNT(*) > 1;
```

**ORDER BY and LIMIT:**
```sql
SELECT columns FROM table ORDER BY column DESC LIMIT 10;
```

---

## Next Steps

1. ✅ **Verify data:** Done — saw all customers and orders
2. ✅ **Basic SELECT queries:** Done — WHERE, AND, OR, LIKE
3. ✅ **Aggregate functions:** Done — COUNT, SUM, AVG, MIN, MAX
4. ✅ **GROUP BY and HAVING:** Done — grouping and filtering groups
5. ✅ **JOINs:** Done — INNER, LEFT, RIGHT, FULL OUTER, CROSS
6. ✅ **BETWEEN and Aliases:** Done — range filtering and column/table renaming
7. ✅ **Composite Keys:** Done — multiple columns as PK
8. ✅ **Normalization:** Done — 1NF, 2NF, 3NF concepts
9. ✅ **ORDER BY, DISTINCT, LIMIT:** Done — sorting, uniqueness, limiting results
10. **C# Fundamentals:** Next major topic (39+ hours remaining)

---

## Study Plan Context

**Tonight (May 18, 20:15 → 01:00):** SQL from zero
- 15 min: What is SQL?
- 30 min: Basic SELECT queries
- 45 min: Aggregate functions & GROUP BY
- 1.5 hours: JOINs (most important!)
- 30 min: Keys & Relationships

**Day 1 Morning (May 19, 09:00 → 13:00):** C# fundamentals

**Day 1 Afternoon (May 19, 14:00 → 18:00):** .NET / ASP.NET Core concepts

**Day 1 Evening (May 19, 19:00 → 23:00):** Mini project (building the EmployeeApi)

**Day 2 Morning (May 20, 08:00 → 12:00):** Final revision + verbal answers

**Interview:** May 20 at 13:00 (~41 hours from start)

---

## Notes

- Junior position (0–1 years experience) — they want reasoning and understanding, not perfection
- SQL *will* be asked (explicitly in job requirements, confirmed by friend)
- Hands-on approach: Learn by doing, read theory later
- Mini project covers: DI, EF Core, LINQ, REST API, async/await, DTOs, exception handling, SOLID

