# .NET / C# / SQL Interview Study Plan
**Interview: May 20 at 13:00 | Time remaining: ~41 hours**
Junior position (0–1 years experience) — they want reasoning and understanding, not perfection.

---

# SCHEDULE OVERVIEW

| Block | Time | Focus |
|---|---|---|
| Tonight | May 18, 20:15 → 01:00 | SQL from zero |
| Day 1 Morning | May 19, 09:00 → 13:00 | C# fundamentals |
| Day 1 Afternoon | May 19, 14:00 → 18:00 | .NET / ASP.NET Core concepts |
| Day 1 Evening | May 19, 19:00 → 23:00 | Mini project |
| Day 2 Morning | May 20, 08:00 → 12:00 | Final revision + verbal answers |

---

# TONIGHT — SQL FROM ZERO (5 hours)

SQL **will** be asked. It's explicitly in the job requirements, and your friend confirmed it. Don't skip this.

---

## 1. What Is SQL? (15 min)

SQL (Structured Query Language) is how you talk to a relational database.
A relational database stores data in **tables** (like Excel sheets) with **rows** (records) and **columns** (fields).

```
customers table:
| id | name    | email              | city    |
|----|---------|-------------------|---------|
| 1  | Marino  | marino@email.com  | Zagreb  |
| 2  | Ana     | ana@email.com     | Split   |
| 3  | Ivan    | ivan@email.com    | Zagreb  |
```

---

## 2. Basic SELECT Queries (30 min)

```sql
-- Get everything from a table
SELECT * FROM customers;

-- Get specific columns
SELECT name, email FROM customers;

-- Give columns an alias (rename in results)
SELECT name AS customer_name, email AS contact FROM customers;

-- Filter rows with WHERE
SELECT * FROM customers WHERE city = 'Zagreb';

-- Multiple conditions
SELECT * FROM customers WHERE city = 'Zagreb' AND name = 'Marino';
SELECT * FROM customers WHERE city = 'Zagreb' OR city = 'Split';

-- NOT
SELECT * FROM customers WHERE NOT city = 'Zagreb';

-- BETWEEN (inclusive — includes both endpoints)
SELECT * FROM orders WHERE total BETWEEN 100 AND 500;
SELECT * FROM orders WHERE created_at BETWEEN '2024-01-01' AND '2024-12-31';

-- IN — match against a list
SELECT * FROM customers WHERE city IN ('Zagreb', 'Split', 'Rijeka');

-- LIKE — pattern matching
SELECT * FROM customers WHERE name LIKE 'M%';    -- starts with M
SELECT * FROM customers WHERE name LIKE '%ic';   -- ends with ic
SELECT * FROM customers WHERE name LIKE '%rin%'; -- contains rin

-- NULL — NEVER use = NULL, always IS NULL
SELECT * FROM customers WHERE phone IS NULL;
SELECT * FROM customers WHERE phone IS NOT NULL;

-- ORDER BY
SELECT * FROM customers ORDER BY name ASC;   -- A to Z
SELECT * FROM customers ORDER BY name DESC;  -- Z to A

-- LIMIT — only return first N rows
SELECT * FROM customers ORDER BY id DESC LIMIT 10;
```

---

## 3. Aggregate Functions & GROUP BY (45 min)

Aggregate functions collapse many rows into one result.

```sql
-- COUNT — how many rows
SELECT COUNT(*) FROM orders;
SELECT COUNT(*) FROM orders WHERE status = 'completed';

-- SUM, AVG, MIN, MAX
SELECT SUM(total) FROM orders;
SELECT AVG(total) FROM orders;
SELECT MIN(total), MAX(total) FROM orders;

-- GROUP BY — split rows into groups, aggregate each group
-- "How many orders does each customer have?"
SELECT customer_id, COUNT(*) AS order_count
FROM orders
GROUP BY customer_id;

-- "Total spent per customer"
SELECT customer_id, SUM(total) AS total_spent
FROM orders
GROUP BY customer_id;

-- HAVING — filter AFTER grouping (WHERE filters BEFORE grouping)
-- "Only show customers who spent more than 1000 total"
SELECT customer_id, SUM(total) AS total_spent
FROM orders
GROUP BY customer_id
HAVING SUM(total) > 1000;

-- ORDER of clauses — you must follow this order:
-- SELECT → FROM → WHERE → GROUP BY → HAVING → ORDER BY → LIMIT
SELECT customer_id, SUM(total) AS total_spent
FROM orders
WHERE status = 'completed'     -- filter rows first
GROUP BY customer_id           -- then group
HAVING SUM(total) > 500        -- then filter groups
ORDER BY total_spent DESC      -- then sort
LIMIT 5;                       -- then limit
```

---

## 4. JOINs — The Most Important SQL Concept (1.5 hours)

JOINs combine rows from two tables based on a related column.

```
customers:                    orders:
| id | name    |             | id | customer_id | total |
|----|---------|             |----|-------------|-------|
| 1  | Marino  |             | 1  | 1           | 250   |
| 2  | Ana     |             | 2  | 1           | 100   |
| 3  | Ivan    |             | 3  | 2           | 450   |
                             | 4  | 99          | 50    | ← customer 99 doesn't exist
```

### INNER JOIN — only rows with a match on BOTH sides
```sql
SELECT customers.name, orders.total
FROM customers
INNER JOIN orders ON customers.id = orders.customer_id;

-- Result:
-- | name   | total |
-- |--------|-------|
-- | Marino | 250   |
-- | Marino | 100   |
-- | Ana    | 450   |
-- Ivan doesn't appear (no orders), order 4 doesn't appear (no matching customer)
```

### LEFT JOIN — all rows from left table, NULL if no match on right
```sql
SELECT customers.name, orders.total
FROM customers
LEFT JOIN orders ON customers.id = orders.customer_id;

-- Result:
-- | name   | total |
-- |--------|-------|
-- | Marino | 250   |
-- | Marino | 100   |
-- | Ana    | 450   |
-- | Ivan   | NULL  | ← Ivan is included, but total is NULL (no orders)
```

### RIGHT JOIN — all rows from right table, NULL if no match on left
```sql
-- Less common. Same as LEFT JOIN with tables swapped.
SELECT customers.name, orders.total
FROM customers
RIGHT JOIN orders ON customers.id = orders.customer_id;

-- Result:
-- | name   | total |
-- |--------|-------|
-- | Marino | 250   |
-- | Marino | 100   |
-- | Ana    | 450   |
-- | NULL   | 50    | ← order 4 included, but customer name is NULL
```

### Using aliases to keep JOIN queries readable
```sql
-- Instead of writing the full table name every time, alias them
SELECT c.name, o.total, o.created_at
FROM customers c
INNER JOIN orders o ON c.id = o.customer_id
WHERE o.total > 100
ORDER BY o.total DESC;
```

### Multiple JOINs
```sql
-- Three tables: customers, orders, products (through order_items)
SELECT c.name, p.name AS product, oi.quantity
FROM customers c
INNER JOIN orders o ON c.id = o.customer_id
INNER JOIN order_items oi ON o.id = oi.order_id
INNER JOIN products p ON oi.product_id = p.id;
```

---

## 5. Keys & Relationships (30 min)

```sql
-- PRIMARY KEY — uniquely identifies each row, auto-increments usually
CREATE TABLE customers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE
);

-- FOREIGN KEY — links to another table's primary key
CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    total DECIMAL(10, 2),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
    -- This prevents orphan orders (customer must exist)
);

-- COMPOSITE KEY — primary key made of TWO columns
-- Used when neither column alone is unique, but the COMBINATION is
CREATE TABLE order_items (
    order_id INT,
    product_id INT,
    quantity INT,
    PRIMARY KEY (order_id, product_id)  -- composite PK
);
```

**When to explain composite keys in interview:**
> "A composite key is when we use multiple columns together as the primary key. For example, in an order_items table, the same order can have multiple products, and the same product can appear in many orders — but each order can only have each product once. So the combination of order_id + product_id uniquely identifies each row."

---

## 6. Normalization (30 min)

Normalization is the process of organizing data to **reduce redundancy** and **prevent anomalies**.

### 1NF — No repeating groups, all values must be atomic (single value)
```
BAD — phones column stores multiple values:
| id | name   | phones          |
|----|--------|-----------------|
| 1  | Marino | 091123, 099456  |  ← two values in one cell, can't query properly

GOOD — separate table:
customers: | id | name   |
           | 1  | Marino |

customer_phones: | customer_id | phone  |
                 | 1           | 091123 |
                 | 1           | 099456 |
```

### 2NF — No partial dependencies (every column must depend on the WHOLE primary key)
```
BAD — product_name depends only on product_id, not the whole composite key:
order_items: | order_id | product_id | quantity | product_name |
             | 1        | 5          | 2        | Laptop       |
             | 2        | 5          | 1        | Laptop       |  ← repeated!

GOOD — move product_name to its own table:
order_items: | order_id | product_id | quantity |
products:    | id       | name       |
```

### 3NF — No transitive dependencies (non-key column depending on another non-key column)
```
BAD — dept_name depends on dept_id, not on employee id:
employees: | id | name   | dept_id | dept_name   |
           | 1  | Marino | 10      | Engineering |
           | 2  | Ana    | 10      | Engineering |  ← repeated, inconsistency risk!

GOOD — separate departments:
employees:   | id | name   | dept_id |
departments: | id | name              |
             | 10 | Engineering       |
```

---

## 7. Subqueries & Transactions (30 min)

```sql
-- Subquery — a query inside a query
-- "Find employees earning more than the average salary"
SELECT name, salary
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);

-- "Find customers who have placed at least one order"
SELECT name FROM customers
WHERE id IN (SELECT DISTINCT customer_id FROM orders);

-- EXISTS — often faster than IN for large tables
SELECT name FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.customer_id = c.id
);

-- TRANSACTION — group of operations that must ALL succeed or ALL fail
-- Classic example: bank transfer
BEGIN TRANSACTION;
    UPDATE accounts SET balance = balance - 500 WHERE id = 1;  -- deduct from sender
    UPDATE accounts SET balance = balance + 500 WHERE id = 2;  -- add to receiver
COMMIT;   -- apply both changes

-- If something goes wrong:
ROLLBACK;  -- undo everything, neither change applies
```

---

# DAY 1 MORNING — C# FUNDAMENTALS (9:00 → 13:00)

---

## 1. Types & Variables (30 min)

```csharp
// Value types — stored directly
int age = 25;
double price = 19.99;
decimal money = 3500.50m;  // m suffix for decimal — use for money, not double
bool isActive = true;
char letter = 'A';

// Reference types — stored as a reference to memory
string name = "Marino";
int[] numbers = { 1, 2, 3, 4, 5 };

// var — compiler figures out the type (still strongly typed, NOT like JavaScript's var)
var message = "Hello";   // compiler knows this is string
var count = 42;           // compiler knows this is int

// const — value can never change
const double Pi = 3.14159;

// Nullable types — the ? allows null
string? middleName = null;   // can be null
int? optionalAge = null;     // normally int can't be null, ? allows it

// Null coalescing — provide a default if null
string display = middleName ?? "No middle name";

// String interpolation
string greeting = $"Hello, {name}! You are {age} years old.";
```

---

## 2. Control Flow (20 min)

```csharp
// if / else if / else
if (age >= 18)
{
    Console.WriteLine("Adult");
}
else if (age >= 13)
{
    Console.WriteLine("Teenager");
}
else
{
    Console.WriteLine("Child");
}

// switch expression (modern C# style)
string category = age switch
{
    >= 18 => "Adult",
    >= 13 => "Teenager",
    _ => "Child"   // _ is the default case
};

// for loop
for (int i = 0; i < 10; i++)
{
    Console.WriteLine(i);
}

// foreach — iterating collections (you'll use this constantly)
var names = new List<string> { "Marino", "Ana", "Ivan" };
foreach (var name in names)
{
    Console.WriteLine(name);
}

// while
int count = 0;
while (count < 5)
{
    count++;
}
```

---

## 3. Classes, Properties & Constructors (45 min)

```csharp
public class Employee
{
    // Properties — preferred over public fields
    // { get; set; } = can read and write from outside
    public int Id { get; set; }
    public string Name { get; set; }

    // private set = readable outside, only writable inside this class
    public decimal Salary { get; private set; }

    // Constructor — runs when you do new Employee(...)
    public Employee(int id, string name, decimal salary)
    {
        Id = id;
        Name = name;
        Salary = salary;
    }

    // Method
    public void GiveRaise(decimal amount)
    {
        if (amount <= 0) throw new ArgumentException("Raise must be positive");
        Salary += amount;
    }

    // Method that returns a value
    public string GetDisplayName()
    {
        return $"{Name} (ID: {Id})";
    }

    // Expression-bodied method (shorthand for single-line methods)
    public bool IsHighEarner() => Salary > 10000;
}

// Using the class
var emp = new Employee(1, "Marino", 3000m);
emp.GiveRaise(500m);
Console.WriteLine(emp.GetDisplayName());  // "Marino (ID: 1)"
Console.WriteLine(emp.Salary);            // 3500

// Object initializer syntax (when no required constructor params)
var emp2 = new Employee { Id = 2, Name = "Ana" };
```

---

## 4. Interfaces & Inheritance (45 min)

```csharp
// INTERFACE — a contract. "If you implement me, you MUST have these members."
// Interfaces have no implementation, just signatures.
public interface IOrderService
{
    Task<List<Order>> GetAllAsync();
    Task<Order?> GetByIdAsync(int id);
    Task<Order> CreateAsync(CreateOrderDto dto);
    Task DeleteAsync(int id);
}

// IMPLEMENTING an interface
public class OrderService : IOrderService
{
    // Must implement ALL methods from the interface
    public async Task<List<Order>> GetAllAsync()
    {
        // actual implementation here
        return await _dbContext.Orders.ToListAsync();
    }
    // ... etc
}

// WHY THIS MATTERS: You can inject IOrderService, not OrderService.
// This means you can swap OrderService for a FakeOrderService in tests.

// INHERITANCE — child class gets everything from parent
public class Animal
{
    public string Name { get; set; }
    public virtual string Speak() => "...";  // virtual = CAN be overridden
}

public class Dog : Animal  // Dog inherits from Animal
{
    public override string Speak() => "Woof";  // override replaces parent's version
    public void Fetch() => Console.WriteLine("Fetching!");  // Dog-only method
}

public class Cat : Animal
{
    public override string Speak() => "Meow";
}

// abstract class — can't be instantiated directly, MUST be inherited
public abstract class Shape
{
    public abstract double Area();  // abstract = MUST be overridden
    public void Print() => Console.WriteLine($"Area: {Area()}");  // normal method
}

public class Circle : Shape
{
    public double Radius { get; set; }
    public override double Area() => Math.PI * Radius * Radius;
}
```

---

## 5. Collections & LINQ (1 hour)

```csharp
// List<T> — resizable array
var names = new List<string> { "Marino", "Ana", "Ivan" };
names.Add("Petra");
names.Remove("Ana");
names.Count;          // 3
names[0];             // "Marino" — index access

// Dictionary<TKey, TValue> — key/value pairs, like a lookup table
var ages = new Dictionary<string, int>
{
    { "Marino", 25 },
    { "Ana", 30 }
};
ages["Ivan"] = 22;          // add
int marinoAge = ages["Marino"]; // get
ages.ContainsKey("Ana");    // true

// ==== LINQ ====
// LINQ lets you query collections with SQL-like operations
// Think of it as SQL for C# objects

var employees = new List<Employee>
{
    new Employee(1, "Marino", 3000m),
    new Employee(2, "Ana", 5000m),
    new Employee(3, "Ivan", 4000m),
    new Employee(4, "Petra", 7000m),
};

// WHERE — filter (like SQL WHERE)
var highEarners = employees.Where(e => e.Salary > 4000).ToList();
// Result: Ana (5000), Petra (7000)

// SELECT — transform/project (like SQL SELECT specific columns)
var names2 = employees.Select(e => e.Name).ToList();
// Result: ["Marino", "Ana", "Ivan", "Petra"]

// SELECT into a new anonymous object
var summary = employees.Select(e => new { e.Name, e.Salary }).ToList();

// ORDER BY
var sorted = employees.OrderBy(e => e.Salary).ToList();        // ascending
var sortedDesc = employees.OrderByDescending(e => e.Salary).ToList(); // descending

// FIRST / SINGLE
var first = employees.FirstOrDefault(e => e.Name == "Marino");
// Returns the Employee or NULL if not found — safe to use

var single = employees.SingleOrDefault(e => e.Id == 1);
// Returns one or null — THROWS EXCEPTION if more than one match

// COUNT, SUM, AVG, MIN, MAX
int count = employees.Count(e => e.Salary > 3000);
decimal total = employees.Sum(e => e.Salary);
decimal average = employees.Average(e => e.Salary);
decimal max = employees.Max(e => e.Salary);

// ANY / ALL — returns bool
bool anyHighEarner = employees.Any(e => e.Salary > 10000);  // false
bool allPaid = employees.All(e => e.Salary > 0);            // true

// GROUP BY
var byDepartment = employees
    .GroupBy(e => e.Department)
    .Select(g => new
    {
        Department = g.Key,
        Count = g.Count(),
        AvgSalary = g.Average(e => e.Salary)
    })
    .ToList();

// TAKE / SKIP — pagination
var page1 = employees.OrderBy(e => e.Id).Take(10).ToList();       // first 10
var page2 = employees.OrderBy(e => e.Id).Skip(10).Take(10).ToList(); // next 10

// Chaining multiple LINQ methods
var result = employees
    .Where(e => e.Salary > 3000)
    .OrderByDescending(e => e.Salary)
    .Select(e => new { e.Name, e.Salary })
    .Take(5)
    .ToList();
```

---

## 6. async / await (30 min)

```csharp
// SYNCHRONOUS — blocks the thread, nothing else can run while waiting
public string GetDataFromDatabase()
{
    Thread.Sleep(3000);  // entire app freezes for 3 seconds
    return "data";
}

// ASYNCHRONOUS — non-blocking, other requests can be handled while waiting
public async Task<string> GetDataFromDatabaseAsync()
{
    await Task.Delay(3000);  // waits without freezing the thread
    return "data";
}

// Task<T> is a promise to return T in the future
// Task (without <T>) is a promise to complete, like void
// async void — only for event handlers, never use otherwise

// Always await async methods — never do this:
var data = _service.GetDataAsync().Result;  // DEADLOCK RISK! Blocks the thread.

// Do this:
var data = await _service.GetDataAsync();  // correct

// Async methods should be async all the way up the call chain
public async Task<IActionResult> GetOrders()           // controller
{
    var orders = await _orderService.GetAllAsync();    // service
    return Ok(orders);
}

public async Task<List<Order>> GetAllAsync()           // service
{
    return await _dbContext.Orders.ToListAsync();      // EF Core
}
```

---

## 7. Exception Handling (20 min)

```csharp
try
{
    var result = int.Parse("abc");  // throws FormatException
    var order = GetOrderById(0);    // might throw our custom exception
}
catch (FormatException ex)
{
    // Handle specific exception type
    Console.WriteLine($"Invalid format: {ex.Message}");
}
catch (NotFoundException ex)
{
    // Handle another specific type
    Console.WriteLine($"Not found: {ex.Message}");
}
catch (Exception ex)
{
    // Catch-all — catches anything not caught above
    Console.WriteLine($"Unexpected error: {ex.Message}");
    throw;  // re-throw to let it bubble up (don't swallow errors silently)
}
finally
{
    // Always runs, even if an exception occurred
    // Good for cleanup: closing files, releasing connections
    Console.WriteLine("Cleanup done");
}

// Custom exception
public class NotFoundException : Exception
{
    public NotFoundException(string message) : base(message) {}
}

// Throwing exceptions
public Order GetOrderById(int id)
{
    var order = _dbContext.Orders.Find(id);
    if (order == null) throw new NotFoundException($"Order {id} not found");
    return order;
}
```

---

# DAY 1 AFTERNOON — .NET / ASP.NET CORE (14:00 → 18:00)

---

## 1. Dependency Injection — Know This Cold (1.5 hours)

### The Problem
```csharp
// BAD — tightly coupled. OrderController is glued to OrderService.
// Can't test OrderController without a real OrderService.
// Can't swap OrderService for a different implementation.
public class OrderController
{
    private OrderService _service = new OrderService();  // hardcoded
}
```

### The Solution
```csharp
// GOOD — depends on the interface, not the implementation
public class OrderController : ControllerBase
{
    private readonly IOrderService _service;

    // DI container sees this constructor and injects IOrderService automatically
    public OrderController(IOrderService service)
    {
        _service = service;
    }
}
```

### Registration in Program.cs
```csharp
// You tell .NET: "when someone asks for IOrderService, give them OrderService"
builder.Services.AddScoped<IOrderService, OrderService>();
builder.Services.AddTransient<IEmailService, EmailService>();
builder.Services.AddSingleton<ICacheService, CacheService>();
```

### The Three Lifetimes — Memorize This

| Lifetime | When is a new instance created? | Use for |
|---|---|---|
| `AddTransient` | Every single time it's requested | Lightweight, stateless operations |
| `AddScoped` | Once per HTTP request | DB contexts, business services |
| `AddSingleton` | Once, lives for app lifetime | Config readers, caches, shared state |

```csharp
// Scoped example — same instance within one HTTP request
// ServiceA and ServiceB get the SAME DbContext within one request
builder.Services.AddScoped<AppDbContext>();
builder.Services.AddScoped<IOrderService, OrderService>();    // OrderService uses DbContext
builder.Services.AddScoped<IEmailService, EmailService>();   // EmailService uses DbContext
// Both services share the same DbContext instance for this request
```

**Interview answer for "What is DI?":**
> "Dependency Injection is a way to provide a class with its dependencies from the outside rather than having the class create them itself. Instead of writing `new OrderService()` inside a controller, the controller declares what it needs in the constructor, and the DI container provides it. This makes code loosely coupled, easier to test because you can inject mocks, and easier to swap implementations."

---

## 2. Middleware (45 min)

Middleware is a pipeline — every HTTP request passes through each middleware in order.

```csharp
// Program.cs — ORDER MATTERS
app.UseExceptionHandler("/error");  // 1st — catch any unhandled exception
app.UseHttpsRedirection();          // 2nd — redirect HTTP to HTTPS
app.UseAuthentication();            // 3rd — who are you? (reads JWT/cookie)
app.UseAuthorization();             // 4th — what can you do? (must come AFTER auth)
app.MapControllers();               // 5th — route to the right controller

// Custom middleware
public class RequestLoggingMiddleware
{
    private readonly RequestDelegate _next;  // represents the next middleware

    public RequestLoggingMiddleware(RequestDelegate next)
    {
        _next = next;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        // Code here runs BEFORE the request hits the controller
        Console.WriteLine($"→ {context.Request.Method} {context.Request.Path}");

        await _next(context);  // pass request to next middleware

        // Code here runs AFTER the response comes back
        Console.WriteLine($"← {context.Response.StatusCode}");
    }
}

// Register in Program.cs
app.UseMiddleware<RequestLoggingMiddleware>();
```

**Interview answer:**
> "Middleware is a pipeline of components that every HTTP request passes through before reaching the controller, and every response passes through on the way back. Each middleware can inspect or modify the request and response. Order matters — for example, authentication must come before authorization, and exception handling should be first so it can catch errors from everything else."

---

## 3. Filters (30 min)

Filters are like middleware but operate specifically within the MVC layer — they have access to controller/action context.

```csharp
// Most common: Action Filter — runs before/after controller action
public class ValidateModelAttribute : ActionFilterAttribute
{
    public override void OnActionExecuting(ActionExecutingContext context)
    {
        if (!context.ModelState.IsValid)
        {
            context.Result = new BadRequestObjectResult(context.ModelState);
            // Setting context.Result short-circuits — controller action never runs
        }
    }
}

// Usage — apply to a specific action or whole controller
[HttpPost]
[ValidateModel]
public async Task<IActionResult> Create(CreateOrderDto dto)
{
    // If we get here, model is valid
    var order = await _service.CreateAsync(dto);
    return CreatedAtAction(nameof(GetById), new { id = order.Id }, order);
}

// Exception filter — handle exceptions from controllers
public class GlobalExceptionFilter : IExceptionFilter
{
    private readonly ILogger _logger;
    public GlobalExceptionFilter(ILogger<GlobalExceptionFilter> logger) => _logger = logger;

    public void OnException(ExceptionContext context)
    {
        _logger.LogError(context.Exception, "Unhandled exception");

        context.Result = context.Exception switch
        {
            NotFoundException => new NotFoundObjectResult(context.Exception.Message),
            _ => new ObjectResult("Internal server error") { StatusCode = 500 }
        };
        context.ExceptionHandled = true;
    }
}
```

---

## 4. Entity Framework Core (1.5 hours)

EF Core is an ORM (Object-Relational Mapper) — it lets you work with the database using C# objects instead of writing SQL by hand.

### Setup
```csharp
// Models
public class Customer
{
    public int Id { get; set; }
    public string Name { get; set; }
    public string Email { get; set; }
    public List<Order> Orders { get; set; } = new();  // navigation property
}

public class Order
{
    public int Id { get; set; }
    public decimal Total { get; set; }
    public DateTime CreatedAt { get; set; }
    public int CustomerId { get; set; }            // foreign key
    public Customer Customer { get; set; }          // navigation property
}

// DbContext — your gateway to the database
public class AppDbContext : DbContext
{
    public DbSet<Customer> Customers { get; set; }
    public DbSet<Order> Orders { get; set; }

    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) {}

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        // Configure relationships with Fluent API
        modelBuilder.Entity<Order>()
            .HasOne(o => o.Customer)        // Order has one Customer
            .WithMany(c => c.Orders)        // Customer has many Orders
            .HasForeignKey(o => o.CustomerId);

        // Seed data (optional)
        modelBuilder.Entity<Customer>().HasData(
            new Customer { Id = 1, Name = "Marino", Email = "marino@email.com" }
        );
    }
}

// Register in Program.cs
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlite("Data Source=app.db"));  // SQLite for easy setup
```

### CRUD Operations
```csharp
public class OrderService : IOrderService
{
    private readonly AppDbContext _context;
    public OrderService(AppDbContext context) => _context = context;

    // READ ALL — with eager loading
    public async Task<List<Order>> GetAllAsync()
    {
        return await _context.Orders
            .Include(o => o.Customer)   // load related Customer in same query (JOIN)
            .OrderByDescending(o => o.CreatedAt)
            .ToListAsync();
    }

    // READ ONE
    public async Task<Order?> GetByIdAsync(int id)
    {
        return await _context.Orders
            .Include(o => o.Customer)
            .FirstOrDefaultAsync(o => o.Id == id);
    }

    // CREATE
    public async Task<Order> CreateAsync(CreateOrderDto dto)
    {
        var order = new Order
        {
            CustomerId = dto.CustomerId,
            Total = dto.Total,
            CreatedAt = DateTime.UtcNow
        };
        _context.Orders.Add(order);
        await _context.SaveChangesAsync();  // commits to database
        return order;
    }

    // UPDATE
    public async Task UpdateAsync(int id, UpdateOrderDto dto)
    {
        var order = await _context.Orders.FindAsync(id);
        if (order == null) throw new NotFoundException($"Order {id} not found");

        order.Total = dto.Total;  // EF Core tracks this change automatically
        await _context.SaveChangesAsync();
    }

    // DELETE
    public async Task DeleteAsync(int id)
    {
        var order = await _context.Orders.FindAsync(id);
        if (order == null) throw new NotFoundException($"Order {id} not found");

        _context.Orders.Remove(order);
        await _context.SaveChangesAsync();
    }
}
```

### The N+1 Problem — Classic Interview Trap

```csharp
// BAD — N+1 queries: 1 for all orders + 1 DB query per order for customer
var orders = await _context.Orders.ToListAsync();  // 1 query
foreach (var order in orders)
{
    Console.WriteLine(order.Customer.Name);  // 1 QUERY PER ITERATION — disaster!
}
// If you have 100 orders = 101 database queries!

// GOOD — 1 query with JOIN
var orders = await _context.Orders
    .Include(o => o.Customer)  // single JOIN query
    .ToListAsync();
// 100 orders = 1 database query
```

### Migrations
```bash
# Create a migration (generates SQL to create/alter tables)
dotnet ef migrations add InitialCreate

# Apply migrations to the database
dotnet ef database update

# See what SQL will be run
dotnet ef migrations script
```

---

## 5. REST API Controller (45 min)

```csharp
[ApiController]
[Route("api/[controller]")]  // → api/orders
public class OrdersController : ControllerBase
{
    private readonly IOrderService _service;

    public OrdersController(IOrderService service)
    {
        _service = service;  // injected by DI
    }

    // GET api/orders
    [HttpGet]
    public async Task<IActionResult> GetAll()
    {
        var orders = await _service.GetAllAsync();
        return Ok(orders);  // 200 OK
    }

    // GET api/orders/5
    [HttpGet("{id}")]
    public async Task<IActionResult> GetById(int id)
    {
        var order = await _service.GetByIdAsync(id);
        if (order == null) return NotFound();  // 404
        return Ok(order);  // 200
    }

    // POST api/orders
    [HttpPost]
    public async Task<IActionResult> Create(CreateOrderDto dto)
    {
        var created = await _service.CreateAsync(dto);
        // 201 Created, with Location header pointing to the new resource
        return CreatedAtAction(nameof(GetById), new { id = created.Id }, created);
    }

    // PUT api/orders/5
    [HttpPut("{id}")]
    public async Task<IActionResult> Update(int id, UpdateOrderDto dto)
    {
        await _service.UpdateAsync(id, dto);
        return NoContent();  // 204 — success, no body
    }

    // DELETE api/orders/5
    [HttpDelete("{id}")]
    public async Task<IActionResult> Delete(int id)
    {
        await _service.DeleteAsync(id);
        return NoContent();  // 204
    }
}

// DTOs — Data Transfer Objects
// Never expose your DB models directly — use DTOs to control what goes in/out
public class CreateOrderDto
{
    public int CustomerId { get; set; }
    public decimal Total { get; set; }
}

public class UpdateOrderDto
{
    public decimal Total { get; set; }
}
```

### HTTP Status Codes to Know
| Code | Meaning | When |
|---|---|---|
| 200 OK | Success | GET, PUT with body |
| 201 Created | Resource created | POST |
| 204 No Content | Success, no body | PUT, DELETE |
| 400 Bad Request | Invalid input | Validation failed |
| 401 Unauthorized | Not authenticated | No/invalid token |
| 403 Forbidden | Authenticated but not allowed | Valid token, wrong role |
| 404 Not Found | Resource doesn't exist | ID not in database |
| 500 Internal Server Error | Server crashed | Unhandled exception |

---

# DAY 1 EVENING — MINI PROJECT (19:00 → 23:00)

## The Project: Simple Employee API

A REST API for managing employees. Covers every concept in one place.

### Why SQLite?
No installation needed. One file = your entire database. Perfect for learning.

### Setup
```bash
# Create new project
dotnet new webapi -n EmployeeApi
cd EmployeeApi

# Add EF Core with SQLite
dotnet add package Microsoft.EntityFrameworkCore.Sqlite
dotnet add package Microsoft.EntityFrameworkCore.Design
dotnet tool install --global dotnet-ef
```

### Project Structure
```
EmployeeApi/
├── Models/
│   ├── Employee.cs
│   └── Department.cs
├── DTOs/
│   ├── CreateEmployeeDto.cs
│   └── UpdateEmployeeDto.cs
├── Interfaces/
│   └── IEmployeeService.cs
├── Services/
│   └── EmployeeService.cs
├── Data/
│   └── AppDbContext.cs
├── Controllers/
│   └── EmployeesController.cs
└── Program.cs
```

### Step 1 — Models
```csharp
// Models/Department.cs
public class Department
{
    public int Id { get; set; }
    public string Name { get; set; }
    public List<Employee> Employees { get; set; } = new();
}

// Models/Employee.cs
public class Employee
{
    public int Id { get; set; }
    public string Name { get; set; }
    public string Email { get; set; }
    public decimal Salary { get; set; }
    public int DepartmentId { get; set; }
    public Department Department { get; set; }
    public DateTime HiredAt { get; set; }
}
```

### Step 2 — DTOs
```csharp
// DTOs/CreateEmployeeDto.cs
public class CreateEmployeeDto
{
    public string Name { get; set; }
    public string Email { get; set; }
    public decimal Salary { get; set; }
    public int DepartmentId { get; set; }
}

// DTOs/UpdateEmployeeDto.cs
public class UpdateEmployeeDto
{
    public string Name { get; set; }
    public decimal Salary { get; set; }
}
```

### Step 3 — DbContext
```csharp
// Data/AppDbContext.cs
public class AppDbContext : DbContext
{
    public DbSet<Employee> Employees { get; set; }
    public DbSet<Department> Departments { get; set; }

    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) {}

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Employee>()
            .HasOne(e => e.Department)
            .WithMany(d => d.Employees)
            .HasForeignKey(e => e.DepartmentId);

        // Seed data — so you have something to test with immediately
        modelBuilder.Entity<Department>().HasData(
            new Department { Id = 1, Name = "Engineering" },
            new Department { Id = 2, Name = "Marketing" }
        );

        modelBuilder.Entity<Employee>().HasData(
            new Employee { Id = 1, Name = "Marino", Email = "marino@co.com", Salary = 4000, DepartmentId = 1, HiredAt = DateTime.UtcNow },
            new Employee { Id = 2, Name = "Ana", Email = "ana@co.com", Salary = 5000, DepartmentId = 1, HiredAt = DateTime.UtcNow },
            new Employee { Id = 3, Name = "Ivan", Email = "ivan@co.com", Salary = 3500, DepartmentId = 2, HiredAt = DateTime.UtcNow }
        );
    }
}
```

### Step 4 — Interface & Service
```csharp
// Interfaces/IEmployeeService.cs
public interface IEmployeeService
{
    Task<List<Employee>> GetAllAsync();
    Task<Employee?> GetByIdAsync(int id);
    Task<List<Employee>> GetByDepartmentAsync(int departmentId);
    Task<Employee> CreateAsync(CreateEmployeeDto dto);
    Task UpdateAsync(int id, UpdateEmployeeDto dto);
    Task DeleteAsync(int id);
}

// Services/EmployeeService.cs
public class EmployeeService : IEmployeeService
{
    private readonly AppDbContext _context;
    public EmployeeService(AppDbContext context) => _context = context;

    public async Task<List<Employee>> GetAllAsync()
    {
        return await _context.Employees
            .Include(e => e.Department)
            .OrderBy(e => e.Name)
            .ToListAsync();
    }

    public async Task<Employee?> GetByIdAsync(int id)
    {
        return await _context.Employees
            .Include(e => e.Department)
            .FirstOrDefaultAsync(e => e.Id == id);
    }

    public async Task<List<Employee>> GetByDepartmentAsync(int departmentId)
    {
        return await _context.Employees
            .Include(e => e.Department)
            .Where(e => e.DepartmentId == departmentId)
            .ToListAsync();
    }

    public async Task<Employee> CreateAsync(CreateEmployeeDto dto)
    {
        var employee = new Employee
        {
            Name = dto.Name,
            Email = dto.Email,
            Salary = dto.Salary,
            DepartmentId = dto.DepartmentId,
            HiredAt = DateTime.UtcNow
        };
        _context.Employees.Add(employee);
        await _context.SaveChangesAsync();
        return employee;
    }

    public async Task UpdateAsync(int id, UpdateEmployeeDto dto)
    {
        var employee = await _context.Employees.FindAsync(id)
            ?? throw new KeyNotFoundException($"Employee {id} not found");
        employee.Name = dto.Name;
        employee.Salary = dto.Salary;
        await _context.SaveChangesAsync();
    }

    public async Task DeleteAsync(int id)
    {
        var employee = await _context.Employees.FindAsync(id)
            ?? throw new KeyNotFoundException($"Employee {id} not found");
        _context.Employees.Remove(employee);
        await _context.SaveChangesAsync();
    }
}
```

### Step 5 — Controller
```csharp
// Controllers/EmployeesController.cs
[ApiController]
[Route("api/[controller]")]
public class EmployeesController : ControllerBase
{
    private readonly IEmployeeService _service;
    public EmployeesController(IEmployeeService service) => _service = service;

    [HttpGet]
    public async Task<IActionResult> GetAll()
        => Ok(await _service.GetAllAsync());

    [HttpGet("{id}")]
    public async Task<IActionResult> GetById(int id)
    {
        var employee = await _service.GetByIdAsync(id);
        return employee == null ? NotFound() : Ok(employee);
    }

    [HttpGet("department/{departmentId}")]
    public async Task<IActionResult> GetByDepartment(int departmentId)
        => Ok(await _service.GetByDepartmentAsync(departmentId));

    [HttpPost]
    public async Task<IActionResult> Create(CreateEmployeeDto dto)
    {
        var created = await _service.CreateAsync(dto);
        return CreatedAtAction(nameof(GetById), new { id = created.Id }, created);
    }

    [HttpPut("{id}")]
    public async Task<IActionResult> Update(int id, UpdateEmployeeDto dto)
    {
        await _service.UpdateAsync(id, dto);
        return NoContent();
    }

    [HttpDelete("{id}")]
    public async Task<IActionResult> Delete(int id)
    {
        await _service.DeleteAsync(id);
        return NoContent();
    }
}
```

### Step 6 — Program.cs
```csharp
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Register DbContext with SQLite
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlite("Data Source=employees.db"));

// Register services — dependency injection
builder.Services.AddScoped<IEmployeeService, EmployeeService>();

var app = builder.Build();

// Auto-create and migrate DB on startup
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    db.Database.Migrate();
}

app.UseSwagger();
app.UseSwaggerUI();   // Visit https://localhost:PORT/swagger to test your API visually!
app.UseHttpsRedirection();
app.UseAuthorization();
app.MapControllers();
app.Run();
```

### Step 7 — Run it
```bash
# Create migration
dotnet ef migrations add InitialCreate

# Run the app
dotnet run

# Open browser to the Swagger URL shown in console
# e.g. https://localhost:7001/swagger
# Test all your endpoints there with no extra tools needed
```

### What This Project Covers
- ✅ Interfaces (IEmployeeService)
- ✅ Dependency Injection (constructor injection throughout)
- ✅ Scoped lifetime (DbContext, EmployeeService)
- ✅ Entity Framework Core with SQLite
- ✅ Include() for eager loading (no N+1)
- ✅ LINQ (Where, OrderBy, FirstOrDefault, Include)
- ✅ REST API with all HTTP verbs
- ✅ Proper status codes (200, 201, 204, 404)
- ✅ DTOs (CreateEmployeeDto, UpdateEmployeeDto)
- ✅ async/await throughout
- ✅ Exception handling

---

# DAY 2 MORNING — FINAL REVISION (08:00 → 12:00)

---

## SOLID Principles — Know the Explanation, Not Just the Name

**S — Single Responsibility**
One class does one job. `EmployeeService` handles employee business logic. `EmailService` sends emails. Don't mix them.

**O — Open/Closed**
Classes should be open for extension but closed for modification. Instead of adding `if (type == "email")` to an existing class, create a new class that extends it.

**L — Liskov Substitution**
A subclass should be usable anywhere its parent is expected without breaking anything. If `Animal` has a `Speak()` method, any `Dog` or `Cat` subclass should work wherever `Animal` is expected.

**I — Interface Segregation**
Don't force a class to implement methods it doesn't need. Split a large `IFullService` interface into smaller `IReadService` and `IWriteService` if some classes only need one.

**D — Dependency Inversion**
Depend on abstractions, not concretions. Inject `IEmployeeService`, not `EmployeeService`. This is literally what DI does.

---

## Keywords — Quick Reference

```csharp
partial   // split one class across multiple files
static    // belongs to the type, not instances. MathHelper.Add() not new MathHelper().Add()
abstract  // class can't be instantiated, method must be overridden
sealed    // class cannot be inherited
readonly  // field can only be set in constructor, then never changes
virtual   // method CAN be overridden by child class
override  // replaces parent's virtual method
new       // hides parent's method (different from override — avoid this)
```

---

## Verbal Answers — Practice These Out Loud

**"What is dependency injection?"**
> "It's a way to provide a class with its dependencies from the outside rather than having the class create them itself. Instead of writing `new OrderService()` inside a controller, the controller declares what it needs in the constructor and the DI container provides it. This makes code loosely coupled and easy to test."

**"What's the difference between Scoped, Transient, and Singleton?"**
> "Transient creates a new instance every time it's requested. Scoped creates one instance per HTTP request — all services within the same request share the same instance. Singleton creates one instance for the entire application lifetime. For database contexts you typically use Scoped."

**"What is middleware?"**
> "Middleware is a pipeline of components that every HTTP request passes through before reaching a controller, and every response passes through on the way back. Each component can read or modify the request or response. Order matters — for example, authentication must come before authorization."

**"What is the N+1 problem?"**
> "It happens when you load a list of entities and then access a related entity on each one in a loop, causing one database query per item on top of the initial query. With 100 orders you'd fire 101 queries. You fix it by using Include() in EF Core to load related data upfront in a single JOIN."

**"Explain LINQ in one sentence."**
> "LINQ lets you query and transform in-memory collections using methods like Where, Select, and OrderBy — essentially SQL-like operations on C# objects."

**"What is normalization?"**
> "It's the process of organizing database tables to reduce redundancy and prevent data anomalies. 1NF means each cell has one value. 2NF means every column depends on the whole primary key. 3NF means no column depends on another non-key column."

---

## Scenario Questions — Think Out Loud

**"The API is suddenly slow. How do you debug?"**
> Start by checking for N+1 queries — that's the most common cause. Check if there are missing database indexes on frequently queried columns. Look at application logs for slow queries. If it's a specific endpoint, profile what SQL EF Core is generating using logging. Then check external dependencies — maybe a third party API or service is slow.

**"A bug is reported in production. What do you do?"**
> First, check the logs to understand what happened. Then try to reproduce it locally. Don't push a fix directly to production — create a hotfix branch, fix, test, then deploy. Communicate status to stakeholders while working.

**"How would you handle a feature multiple developers work on?"**
> Use Git feature branches — each developer works on their own branch. Open a pull request when done, have at least one code review, then merge to the main branch. Use feature flags if the feature needs to be deployed but not yet activated.

---

## Priority Order If You Run Out of Time

1. ✅ DI + lifetimes (Transient/Scoped/Singleton)
2. ✅ EF Core basics + N+1 problem + Include()
3. ✅ SQL JOINs (INNER, LEFT) + GROUP BY + HAVING
4. ✅ SQL normalization (1NF, 2NF, 3NF)
5. ✅ Middleware — what it is and why order matters
6. ✅ LINQ core methods (Where, Select, FirstOrDefault, Any, Include)
7. ✅ REST conventions + status codes
8. ✅ async/await — always await, never .Result
9. ✅ SOLID (just the verbal explanations)
10. ⬇️ Filters (nice to know, lower priority)
11. ⬇️ Keywords like partial/static (your friend said he doesn't care much)

---

*Remember: this is a 0–1 year junior role. They want to see that you understand concepts and can reason. Tie everything back to the mini project. Good luck! 💪*
