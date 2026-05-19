# .NET / ASP.NET Core Concepts — Interview Prep

Learn the core patterns and architecture concepts that power modern .NET APIs.

---

## 1. Middleware — The HTTP Request Pipeline

### What Is Middleware?

Every HTTP request passes through a **pipeline of middleware components**. Each component can:
- Read/modify the request
- Pass it to the next component
- Read/modify the response on the way back

**Order matters.** If you check authentication after logging, users won't be authenticated.

### The Pipeline Visualization

```
Request comes in
    ↓
[Logging Middleware]           ← logs request details
    ↓
[HTTPS Redirection Middleware] ← forces HTTPS
    ↓
[Routing Middleware]           ← figures out which controller
    ↓
[Authentication Middleware]    ← checks if user is logged in
    ↓
[Authorization Middleware]     ← checks if user has permission
    ↓
[Your Controller/Handler]      ← your actual business logic runs
    ↓
Response returns through middleware (in reverse)
    ↓
[Logging Middleware]           ← logs response
    ↓
Response sent to client
```

### Program.cs — Middleware Registration Order

```csharp
var builder = WebApplication.CreateBuilder(args);

var app = builder.Build();

// Order matters! These execute in order on request, reversed on response

app.UseHttpsRedirection();      // Force HTTPS (before routing)

app.UseRouting();               // Figure out which endpoint to call

app.UseAuthentication();        // Who are you? (before authorization)

app.UseAuthorization();         // Are you allowed? (after authentication)

app.MapControllers();           // Actually call the controller

app.Run();
```

**Critical:** Authentication must come before authorization. You can't check permissions if you don't know who the user is.

### Custom Middleware — Inline

```csharp
// Simple middleware that logs request duration
app.Use(async (context, next) =>
{
    var stopwatch = System.Diagnostics.Stopwatch.StartNew();
    
    // Logs before the request
    Console.WriteLine($"→ {context.Request.Method} {context.Request.Path}");
    
    // Pass to next middleware in pipeline
    await next.Invoke();
    
    // Logs after response
    stopwatch.Stop();
    Console.WriteLine($"← {context.Response.StatusCode} ({stopwatch.ElapsedMilliseconds}ms)");
});
```

### Custom Middleware — Class-Based (Reusable)

```csharp
public class LoggingMiddleware
{
    private readonly RequestDelegate _next;
    
    // RequestDelegate is the next middleware in pipeline
    public LoggingMiddleware(RequestDelegate next)
    {
        _next = next;
    }
    
    // Called for every request
    public async Task InvokeAsync(HttpContext context)
    {
        Console.WriteLine($"→ {context.Request.Method} {context.Request.Path}");
        
        // Call next middleware
        await _next(context);
        
        Console.WriteLine($"← {context.Response.StatusCode}");
    }
}

// Register in Program.cs (order matters!)
app.UseMiddleware<LoggingMiddleware>();
```

### Interview Question: "What is middleware?"

> "Middleware is a component in the ASP.NET Core pipeline that handles HTTP requests and responses. Every request passes through the middleware pipeline in order, each middleware can modify the request, then responses come back through in reverse. Order is critical — for example, authentication middleware must run before authorization middleware."

---

## 2. Dependency Injection (DI) — Core .NET Pattern

### What Is DI?

Instead of creating dependencies inside a class, you **receive them from outside** (injection). This decouples classes and makes testing easier.

### Without DI (Tightly Coupled)

```csharp
public class EmployeeService
{
    private readonly EmployeeRepository _repo;
    
    public EmployeeService()
    {
        // Service creates its own dependency — tightly coupled
        _repo = new EmployeeRepository();
    }
    
    public async Task<Employee> GetEmployeeAsync(int id)
    {
        return await _repo.GetByIdAsync(id);
    }
}

// Problem: Hard to test. Can't easily swap EmployeeRepository for a mock.
```

### With DI (Loosely Coupled)

```csharp
public interface IEmployeeRepository
{
    Task<Employee?> GetByIdAsync(int id);
}

public class EmployeeRepository : IEmployeeRepository
{
    private readonly AppDbContext _context;
    
    public EmployeeRepository(AppDbContext context)
    {
        _context = context;
    }
    
    public async Task<Employee?> GetByIdAsync(int id)
    {
        return await _context.Employees.FindAsync(id);
    }
}

public class EmployeeService
{
    private readonly IEmployeeRepository _repo;
    
    // DI: Repository injected by constructor
    public EmployeeService(IEmployeeRepository repo)
    {
        _repo = repo;
    }
    
    public async Task<Employee?> GetEmployeeAsync(int id)
    {
        return await _repo.GetByIdAsync(id);
    }
}

// In Program.cs — register dependencies
builder.Services.AddScoped<IEmployeeRepository, EmployeeRepository>();
builder.Services.AddScoped<IEmployeeService, EmployeeService>();

// In Controller
[ApiController]
[Route("api/[controller]")]
public class EmployeesController : ControllerBase
{
    private readonly IEmployeeService _service;
    
    // DI: Service injected automatically
    public EmployeesController(IEmployeeService service)
    {
        _service = service;
    }
    
    [HttpGet("{id}")]
    public async Task<ActionResult<Employee>> GetById(int id)
    {
        var emp = await _service.GetByIdAsync(id);
        return emp == null ? NotFound() : Ok(emp);
    }
}
```

### DI Lifetimes — When to Use Each

| Lifetime | Created | Use Case | Example |
|----------|---------|----------|---------|
| **Transient** | Every time requested | Stateless, lightweight | Email sender, logger |
| **Scoped** | Once per HTTP request | Stateful per request | DbContext, current user service |
| **Singleton** | Once for app lifetime | Shared, thread-safe | Configuration, cache |

```csharp
// Transient — new instance every time
builder.Services.AddTransient<IEmailService, EmailService>();

// Scoped — one per HTTP request (best for DbContext)
builder.Services.AddScoped<AppDbContext>();
builder.Services.AddScoped<IEmployeeService, EmployeeService>();

// Singleton — one for entire app
builder.Services.AddSingleton<IConfiguration>(builder.Configuration);
```

> **Critical:** DbContext should be **Scoped**, never Singleton. Each request gets its own instance.

### Interview Question: "Explain DI lifetimes"

> "Transient creates a new instance every time it's requested — use for stateless services. Scoped creates one instance per HTTP request — use for DbContext so each request has clean data. Singleton creates one instance for the entire app lifetime — use for configuration or caches that are thread-safe. DbContext is always Scoped because entity tracking and connection pooling expect per-request instances."

---

## 3. Entity Framework Core (EF Core) — ORM

### What Is EF Core?

An **Object-Relational Mapper** that maps database tables to C# classes. You work with objects instead of raw SQL.

### Models — Represent Database Tables

```csharp
public class Employee
{
    // Primary key
    public int Id { get; set; }
    
    // Required fields
    public string Name { get; set; } = null!;
    public decimal Salary { get; set; }
    
    // Timestamps
    public DateTime HiredAt { get; set; }
    
    // Foreign key
    public int DepartmentId { get; set; }
    
    // Navigation property (relationship)
    public Department Department { get; set; } = null!;
}

public class Department
{
    public int Id { get; set; }
    public string Name { get; set; } = null!;
    
    // One-to-many: One department has many employees
    public ICollection<Employee> Employees { get; set; } = [];
}
```

**Database equivalent:**
```sql
CREATE TABLE Departments (
    Id INT PRIMARY KEY AUTOINCREMENT,
    Name VARCHAR(100) NOT NULL
);

CREATE TABLE Employees (
    Id INT PRIMARY KEY AUTOINCREMENT,
    Name VARCHAR(100) NOT NULL,
    Salary DECIMAL(10,2),
    HiredAt DATETIME,
    DepartmentId INT FOREIGN KEY REFERENCES Departments(Id)
);
```

### DbContext — Database Connection

```csharp
public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) 
        : base(options) { }
    
    // DbSet<T> represents a table
    public DbSet<Employee> Employees { get; set; }
    public DbSet<Department> Departments { get; set; }
}
```

### Registering EF Core in Program.cs

```csharp
// Register with SQLite
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlite("Data Source=employees.db"));

// Or SQL Server
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlServer("Server=localhost;Database=EmployeeDb;..."));
```

### Querying with LINQ

```csharp
public class EmployeeRepository : IEmployeeRepository
{
    private readonly AppDbContext _context;
    
    public EmployeeRepository(AppDbContext context)
    {
        _context = context;
    }
    
    // Get by ID
    public async Task<Employee?> GetByIdAsync(int id)
    {
        return await _context.Employees
            .Include(e => e.Department)  // Eager load department
            .FirstOrDefaultAsync(e => e.Id == id);
    }
    
    // Get all
    public async Task<List<Employee>> GetAllAsync()
    {
        return await _context.Employees
            .Include(e => e.Department)  // Critical! Prevents N+1
            .OrderBy(e => e.Name)
            .ToListAsync();
    }
    
    // Filter
    public async Task<List<Employee>> GetByDepartmentAsync(int deptId)
    {
        return await _context.Employees
            .Where(e => e.DepartmentId == deptId)
            .OrderBy(e => e.Salary)
            .ToListAsync();
    }
    
    // Create
    public async Task<Employee> CreateAsync(Employee emp)
    {
        _context.Employees.Add(emp);
        await _context.SaveChangesAsync();
        return emp;
    }
    
    // Update
    public async Task UpdateAsync(Employee emp)
    {
        _context.Employees.Update(emp);
        await _context.SaveChangesAsync();
    }
    
    // Delete
    public async Task DeleteAsync(int id)
    {
        var emp = await _context.Employees.FindAsync(id);
        if (emp != null)
        {
            _context.Employees.Remove(emp);
            await _context.SaveChangesAsync();
        }
    }
}
```

### The N+1 Problem (Critical Interview Topic)

**Bad (N+1 queries):**
```csharp
var employees = await _context.Employees.ToListAsync();  // 1 query

foreach (var emp in employees)
{
    var dept = emp.Department.Name;  // 1 query per employee!
}
// Total: 1 + N queries (100 employees = 101 queries)
```

**Good (Single query with JOIN):**
```csharp
var employees = await _context.Employees
    .Include(e => e.Department)  // Eager load — SQL JOIN
    .ToListAsync();  // 1 query total

foreach (var emp in employees)
{
    var dept = emp.Department.Name;  // No more queries
}
// Total: 1 query
```

### Interview Question: "What is the N+1 problem?"

> "It happens when you load a collection of entities and then access a related entity on each one in a loop. You fire one query to get the collection, then one query per item to load the related data. With 100 employees, that's 101 queries. You fix it using Include() to load related data upfront in a single SQL JOIN."

---

## 4. LINQ — Language Integrated Query

LINQ lets you query collections and databases using SQL-like syntax.

### LINQ Query Methods

```csharp
var employees = new List<Employee> { /* ... */ };

// Where — filter rows
var highEarners = employees
    .Where(e => e.Salary > 3000)
    .ToList();

// Select — project/transform
var names = employees
    .Select(e => e.Name)
    .ToList();  // List<string>

// Select with transformation
var employeeDtos = employees
    .Select(e => new { e.Id, e.Name, DeptName = e.Department.Name })
    .ToList();

// OrderBy — sort ascending
var byName = employees
    .OrderBy(e => e.Name)
    .ToList();

// OrderByDescending — sort descending
var byHighestSalary = employees
    .OrderByDescending(e => e.Salary)
    .ToList();

// FirstOrDefault — get first or null
var first = employees.FirstOrDefault(e => e.Name == "Marino");
if (first == null) { /* not found */ }

// Any — check if any match
bool hasHighEarners = employees.Any(e => e.Salary > 5000);

// Count — count matches
int count = employees.Count(e => e.Salary > 3000);

// GroupBy — like SQL GROUP BY
var byDept = employees
    .GroupBy(e => e.DepartmentId)
    .Select(g => new
    {
        DeptId = g.Key,
        Count = g.Count(),
        AvgSalary = g.Average(e => e.Salary)
    })
    .ToList();
```

### LINQ vs SQL

**SQL:**
```sql
SELECT Name, Salary
FROM Employees
WHERE Salary > 3000
ORDER BY Salary DESC
LIMIT 10;
```

**LINQ (identical logic):**
```csharp
var result = employees
    .Where(e => e.Salary > 3000)
    .OrderByDescending(e => e.Salary)
    .Take(10)  // LIMIT equivalent
    .Select(e => new { e.Name, e.Salary })
    .ToList();
```

### LINQ with EF Core (Database Queries)

```csharp
// This runs ON the DATABASE, not in memory
var highEarners = await _context.Employees
    .Where(e => e.Salary > 3000)
    .OrderByDescending(e => e.Salary)
    .Include(e => e.Department)
    .ToListAsync();  // .ToListAsync() executes the query
```

> **Key difference:** When you call `.ToList()` or `.ToListAsync()`, the LINQ query is executed (either in-memory or against the database).

---

## 5. REST Conventions — HTTP Verbs & Status Codes

### HTTP Methods (Verbs)

| Method | Purpose | Idempotent? | Safe? | Example |
|--------|---------|------------|-------|---------|
| **GET** | Retrieve data | Yes | Yes | `GET /api/employees/1` |
| **POST** | Create new data | No | No | `POST /api/employees` with body |
| **PUT** | Replace entire resource | Yes | No | `PUT /api/employees/1` with body |
| **PATCH** | Partial update | No | No | `PATCH /api/employees/1` with partial body |
| **DELETE** | Remove data | Yes | No | `DELETE /api/employees/1` |

**Idempotent:** Calling multiple times = same result. GET/PUT/DELETE are idempotent.

### HTTP Status Codes

| Code | Meaning | Use Case |
|------|---------|----------|
| `200 OK` | Success | `GET /api/employees/1` returns the employee |
| `201 Created` | Created | `POST /api/employees` returns created employee + Location header |
| `204 No Content` | Success, no body | `DELETE /api/employees/1` (nothing to return) |
| `400 Bad Request` | Invalid input | Missing required field, invalid data |
| `404 Not Found` | Doesn't exist | `GET /api/employees/999` |
| `409 Conflict` | Duplicate/conflict | Trying to create with duplicate unique field |
| `500 Internal Error` | Server error | Unhandled exception |

### Controller — REST Example

```csharp
[ApiController]
[Route("api/[controller]")]
public class EmployeesController : ControllerBase
{
    private readonly IEmployeeService _service;
    
    public EmployeesController(IEmployeeService service) => _service = service;
    
    // GET /api/employees/{id}
    [HttpGet("{id}")]
    public async Task<ActionResult<EmployeeDto>> GetById(int id)
    {
        var emp = await _service.GetByIdAsync(id);
        return emp == null ? NotFound() : Ok(emp);  // 404 or 200
    }
    
    // POST /api/employees
    [HttpPost]
    public async Task<ActionResult<EmployeeDto>> Create(CreateEmployeeDto dto)
    {
        var created = await _service.CreateAsync(dto);
        // 201 + Location header pointing to GET /api/employees/{id}
        return CreatedAtAction(nameof(GetById), new { id = created.Id }, created);
    }
    
    // PUT /api/employees/{id}
    [HttpPut("{id}")]
    public async Task<IActionResult> Update(int id, UpdateEmployeeDto dto)
    {
        await _service.UpdateAsync(id, dto);
        return NoContent();  // 204
    }
    
    // DELETE /api/employees/{id}
    [HttpDelete("{id}")]
    public async Task<IActionResult> Delete(int id)
    {
        await _service.DeleteAsync(id);
        return NoContent();  // 204
    }
}
```

---

## 6. DTOs (Data Transfer Objects)

**Never expose your database models directly.** Use DTOs to separate API contracts from database models.

```csharp
// Database model (internal)
public class Employee
{
    public int Id { get; set; }
    public string Name { get; set; } = null!;
    public decimal Salary { get; set; }
    public DateTime HiredAt { get; set; }
    public int DepartmentId { get; set; }
    public Department Department { get; set; } = null!;
}

// DTOs (public API contracts)

// For creating (client sends this)
public class CreateEmployeeDto
{
    public string Name { get; set; } = null!;
    public decimal Salary { get; set; }
    public int DepartmentId { get; set; }
}

// For updating
public class UpdateEmployeeDto
{
    public string Name { get; set; } = null!;
    public decimal Salary { get; set; }
}

// For reading (API returns this)
public class EmployeeDto
{
    public int Id { get; set; }
    public string Name { get; set; } = null!;
    public decimal Salary { get; set; }
    public string DepartmentName { get; set; } = null!;
}

// Service maps DTOs to models
public class EmployeeService
{
    private readonly AppDbContext _context;
    
    public async Task<Employee> CreateAsync(CreateEmployeeDto dto)
    {
        var emp = new Employee
        {
            Name = dto.Name,
            Salary = dto.Salary,
            DepartmentId = dto.DepartmentId,
            HiredAt = DateTime.UtcNow
        };
        _context.Employees.Add(emp);
        await _context.SaveChangesAsync();
        return emp;
    }
    
    public async Task<EmployeeDto?> GetByIdAsync(int id)
    {
        var emp = await _context.Employees
            .Include(e => e.Department)
            .FirstOrDefaultAsync(e => e.Id == id);
        
        if (emp == null) return null;
        
        return new EmployeeDto
        {
            Id = emp.Id,
            Name = emp.Name,
            Salary = emp.Salary,
            DepartmentName = emp.Department.Name
        };
    }
}
```

---

## 7. Exception Handling with Async/Await

### Try/Catch/Finally Pattern

```csharp
public async Task<Employee> GetEmployeeAsync(int id)
{
    try
    {
        var emp = await _context.Employees.FindAsync(id);
        if (emp == null)
        {
            throw new KeyNotFoundException($"Employee {id} not found");
        }
        return emp;
    }
    catch (KeyNotFoundException ex)
    {
        // Handle expected error
        Console.WriteLine($"Error: {ex.Message}");
        throw;  // Re-throw if caller needs to handle
    }
    catch (Exception ex)
    {
        // Catch all others
        Console.WriteLine($"Unexpected error: {ex.Message}");
        throw;
    }
    finally
    {
        // Always runs (cleanup, logging)
        Console.WriteLine("GetEmployeeAsync completed");
    }
}
```

### Null-Coalescing with Exception

```csharp
public async Task UpdateAsync(int id, UpdateEmployeeDto dto)
{
    var emp = await _context.Employees.FindAsync(id)
        ?? throw new KeyNotFoundException($"Employee {id} not found");
    
    emp.Name = dto.Name;
    emp.Salary = dto.Salary;
    await _context.SaveChangesAsync();
}
```

### Controller Exception Handling

```csharp
[HttpGet("{id}")]
public async Task<ActionResult<EmployeeDto>> GetById(int id)
{
    try
    {
        var emp = await _service.GetByIdAsync(id);
        return emp == null ? NotFound() : Ok(emp);
    }
    catch (Exception ex)
    {
        // Log error, return 500
        Console.WriteLine(ex.Message);
        return StatusCode(500, "Internal server error");
    }
}
```

---

## Interview Questions — Practice These

### "What is middleware and why does order matter?"

> "Middleware is a component in the HTTP pipeline that every request passes through. Each middleware can modify the request, then responses come back through in reverse. Order is critical — authentication must come before authorization, because you can't check permissions without knowing who the user is."

### "Explain dependency injection."

> "DI is providing a class its dependencies from outside rather than having it create them. Instead of `new Repository()` inside a service, the service declares what it needs in the constructor and the DI container provides it. This decouples code and makes testing easier. Lifetimes matter: Transient for stateless services, Scoped for DbContext (one per request), Singleton for shared objects."

### "What is the N+1 problem and how do you fix it?"

> "It's loading a collection of entities and accessing related data in a loop. 100 employees = 101 queries (1 for employees, 1 per employee for department). You fix it with Include() to eager-load related data in a single SQL JOIN."

### "What's the difference between PUT and PATCH?"

> "PUT replaces the entire resource — send the complete object. PATCH updates specific fields — send only what changed. PUT is idempotent; PATCH typically isn't."

### "Why use DTOs instead of exposing models directly?"

> "Models are implementation details tied to your database. DTOs define your API contract. You can change models without breaking clients, and you can exclude sensitive fields (passwords, internal IDs) from responses."

---

## Summary — What You Need for Interview

1. ✅ **Middleware:** Request pipeline, order matters, custom middleware
2. ✅ **Dependency Injection:** Constructor injection, lifetimes (Transient/Scoped/Singleton)
3. ✅ **EF Core:** Models, DbContext, LINQ queries, Include() to prevent N+1
4. ✅ **LINQ:** Where, Select, OrderBy, FirstOrDefault, GroupBy, etc.
5. ✅ **REST:** HTTP methods, status codes, proper endpoint design
6. ✅ **DTOs:** Separate API contracts from database models
7. ✅ **Exception Handling:** Try/catch/finally with async, proper error codes

Next: Build the mini project to apply all these concepts.
