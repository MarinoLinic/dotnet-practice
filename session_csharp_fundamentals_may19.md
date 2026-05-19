# C# Syntax & .NET Concepts — Interview Prep

**You know JS and C++.** This document covers **only syntax differences and .NET-specific concepts** you need for the interview.

---

## C# Syntax Differences from JavaScript & C++

### 1. String Interpolation (Better than JS Template Literals)

**C# — Use `$"..."`:**
```csharp
string name = "Marino";
int age = 25;
Console.WriteLine($"Name: {name}, Age: {age}");
```

**vs JS template literals:**
```javascript
console.log(`Name: ${name}, Age: ${age}`);
```

**Difference:** C# uses `$` prefix, JS uses backticks. Otherwise identical concept.

---

### 2. Type System — Static Typing Like C++

**C# requires explicit types (like C++):**
```csharp
int age = 25;
string name = "Marino";
decimal salary = 2500.50m;  // m suffix for decimal (money)
bool isActive = true;
```

**Not like JavaScript:**
```javascript
let age = 25;  // no type needed
```

> **Key:** Use `decimal` for money, not `double`. `decimal` is precise; `double` isn't.

---

### 3. Null Handling — Nullable Types

**C# can be strict about null:**

```csharp
// Non-nullable — can't be null
string name = "Marino";
name = null;  // ERROR at compile time

// Nullable — can be null (add ?)
string? optionalName = null;  // OK
optionalName = "Marino";      // OK

// Null-coalescing operator ??
string result = optionalName ?? "Unknown";  // if null, use "Unknown"
```

**vs JS:**
```javascript
let name = "Marino";
name = null;  // always allowed
```

> **Remark:** C#'s nullable system prevents null reference bugs at compile time. This is a strength.

---

### 4. Properties — Not Just Fields

**C# uses properties (with get/set):**

```csharp
public class Employee
{
    // Field
    private int _age;
    
    // Property with backing field
    public int Age 
    { 
        get { return _age; }
        set { _age = value; }
    }
    
    // Auto-property (shorthand)
    public string Name { get; set; }
    
    // Read-only property
    public int Id { get; private set; }
}

// Usage
var emp = new Employee();
emp.Name = "Marino";  // calls setter
int name = emp.Name;  // calls getter
```

**vs JS/C++:**
```javascript
// JS — just fields
class Employee {
    constructor() {
        this.name = "Marino";
    }
}
```

> **Why:** Properties let you add logic (validation, logging) without changing the calling code. Important for interviews.

---

### 5. Access Modifiers — Similar to C++

```csharp
public class Employee       // accessible everywhere
{
    public string Name { get; set; }        // public
    protected int SalaryMultiplier { get; } // subclasses only
    private int _internalId;                // this class only
    internal string Department { get; }     // same assembly only
}
```

**vs C++:**
- Same names: `public`, `protected`, `private`
- C# adds `internal` (assembly-level visibility)

---

### 6. No Pointers — References Only

**C# does memory management for you:**

```csharp
var emp1 = new Employee { Name = "Marino" };
var emp2 = emp1;  // reference copy, not deep copy
emp2.Name = "Ana";
Console.WriteLine(emp1.Name);  // "Ana" (same object)
```

**vs C++:**
```cpp
Employee* emp1 = new Employee();
Employee* emp2 = emp1;  // pointer
```

> **No pointers in C#.** No `*`, no manual `delete`. Garbage collection handles it.

---

### 7. Collections — List<T> Instead of Vector/Array

**C# has strongly typed collections:**

```csharp
// List (dynamic array)
var employees = new List<Employee> { };
employees.Add(new Employee { Name = "Marino" });
employees.Remove(employees[0]);

// Dictionary (map)
var salaries = new Dictionary<string, decimal>
{
    { "Marino", 2500m },
    { "Ana", 3000m }
};
salaries["Marino"] = 2600m;

// Array (fixed size)
int[] numbers = new int[5];
numbers[0] = 10;
```

**vs JS:**
```javascript
let employees = [];  // just arrays for everything
let salaries = {};   // objects as maps
```

---

## .NET-Specific Concepts

### 1. Async/Await — Essential for APIs

**C# async/await is built-in:**

```csharp
public async Task<Employee> GetEmployeeAsync(int id)
{
    // Simulate async work (DB call, HTTP request)
    await Task.Delay(1000);
    return new Employee { Id = id, Name = "Marino" };
}

// Calling
var emp = await GetEmployeeAsync(1);  // must await, never .Result
```

**Key Rules:**
- Async methods return `Task` or `Task<T>`
- Always `await` async calls (never `.Result` or `.Wait()`)
- Async propagates up the call chain

> **Remark:** `.Result` blocks the thread — deadlock risk. Always `await`.

---

### 2. Dependency Injection (DI) — Core to .NET

**Injected in constructor:**

```csharp
public class EmployeeService
{
    private readonly IEmployeeRepository _repo;
    
    // DI: repository provided by constructor
    public EmployeeService(IEmployeeRepository repo)
    {
        _repo = repo;
    }
    
    public async Task<Employee> GetEmployeeAsync(int id)
    {
        return await _repo.GetByIdAsync(id);
    }
}

// Registration in Program.cs
builder.Services.AddScoped<IEmployeeService, EmployeeService>();
builder.Services.AddScoped<IEmployeeRepository, EmployeeRepository>();
```

**Lifetimes:**
- **Transient:** New instance every time
- **Scoped:** One per HTTP request (use for DbContext)
- **Singleton:** One for entire app lifetime

---

### 3. Entity Framework Core (EF Core) — ORM for Database

**Models map to database tables:**

```csharp
public class Employee
{
    public int Id { get; set; }
    public string Name { get; set; } = null!;
    public decimal Salary { get; set; }
    public DateTime HiredAt { get; set; }
    public int DepartmentId { get; set; }
    
    // Navigation property (relationship)
    public Department Department { get; set; } = null!;
}

public class Department
{
    public int Id { get; set; }
    public string Name { get; set; } = null!;
    public ICollection<Employee> Employees { get; set; } = [];
}
```

**DbContext (database connection):**

```csharp
public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) 
        : base(options) { }
    
    public DbSet<Employee> Employees { get; set; }
    public DbSet<Department> Departments { get; set; }
}
```

**Querying with LINQ:**

```csharp
// Get employee by id
var emp = await _context.Employees.FindAsync(1);

// Get all employees with their department
var emps = await _context.Employees
    .Include(e => e.Department)  // eager load (prevents N+1)
    .ToListAsync();

// Filter and sort
var activeSalaries = await _context.Employees
    .Where(e => e.HiredAt > DateTime.Now.AddYears(-5))
    .OrderBy(e => e.Name)
    .Select(e => new { e.Name, e.Salary })
    .ToListAsync();
```

> **Critical:** Always use `Include()` to load related data. Otherwise you get N+1 queries.

---

### 4. LINQ — SQL-like Querying in C#

**Core LINQ methods:**

```csharp
var employees = new List<Employee> { /* ... */ };

// Where (filter)
var seniors = employees.Where(e => e.Salary > 3000).ToList();

// Select (project)
var names = employees.Select(e => e.Name).ToList();

// OrderBy
var sorted = employees.OrderBy(e => e.Name).ToList();

// FirstOrDefault (get first or null)
var first = employees.FirstOrDefault(e => e.Name == "Marino");

// Any (check existence)
bool hasSeniors = employees.Any(e => e.Salary > 5000);

// GroupBy (like SQL GROUP BY)
var byDept = employees
    .GroupBy(e => e.DepartmentId)
    .Select(g => new { DeptId = g.Key, Count = g.Count() })
    .ToList();
```

---

### 5. REST API Conventions

**HTTP Status Codes:**
- `200 OK` — Success
- `201 Created` — Resource created
- `204 No Content` — Success, no body
- `400 Bad Request` — Invalid input
- `404 Not Found` — Resource doesn't exist
- `500 Internal Server Error` — Server error

**Example controller:**

```csharp
[ApiController]
[Route("api/[controller]")]
public class EmployeesController : ControllerBase
{
    private readonly IEmployeeService _service;
    
    public EmployeesController(IEmployeeService service) 
        => _service = service;
    
    [HttpGet("{id}")]
    public async Task<ActionResult<Employee>> GetById(int id)
    {
        var emp = await _service.GetByIdAsync(id);
        return emp == null ? NotFound() : Ok(emp);
    }
    
    [HttpPost]
    public async Task<ActionResult<Employee>> Create(CreateEmployeeDto dto)
    {
        var emp = await _service.CreateAsync(dto);
        return CreatedAtAction(nameof(GetById), new { id = emp.Id }, emp);
    }
}
```

---

### 6. DTOs (Data Transfer Objects)

**Don't expose your database models directly:**

```csharp
// DTO for creating employees
public class CreateEmployeeDto
{
    public string Name { get; set; } = null!;
    public decimal Salary { get; set; }
    public int DepartmentId { get; set; }
}

// DTO for updating
public class UpdateEmployeeDto
{
    public string Name { get; set; } = null!;
    public decimal Salary { get; set; }
}

// Service maps DTO to model
public async Task<Employee> CreateAsync(CreateEmployeeDto dto)
{
    var employee = new Employee
    {
        Name = dto.Name,
        Salary = dto.Salary,
        DepartmentId = dto.DepartmentId,
        HiredAt = DateTime.UtcNow
    };
    _context.Employees.Add(employee);
    await _context.SaveChangesAsync();
    return employee;
}
```

---

### 7. Interfaces — Crucial for DI

**Define contracts:**

```csharp
public interface IEmployeeService
{
    Task<Employee?> GetByIdAsync(int id);
    Task<List<Employee>> GetAllAsync();
    Task<Employee> CreateAsync(CreateEmployeeDto dto);
    Task UpdateAsync(int id, UpdateEmployeeDto dto);
    Task DeleteAsync(int id);
}

public class EmployeeService : IEmployeeService
{
    // implement all methods
}
```

**Why:** You inject the interface, not the class. Easy to swap implementations for testing.

---

## Key Differences Summary

| Concept | JavaScript | C++ | C# |
|---------|-----------|-----|-----|
| Typing | Dynamic | Static | Static |
| Null safety | Always nullable | Pointers/null | Nullable with `?` |
| Collections | Arrays + Objects | Vectors/Maps | List<T>, Dictionary<K,V> |
| Async | Promises/async-await | Callbacks/threads | async/await (built-in) |
| Memory | Garbage collection | Manual | Garbage collection |
| OOP | Prototype-based | Class-based | Class-based |
| Dependency Injection | Manual | Manual | Built-in DI container |

---

## What You Need to Know for Interview

1. ✅ **String interpolation:** `$"..."`
2. ✅ **Nullable types:** `string?`, `??` operator
3. ✅ **Properties:** get/set, auto-properties
4. ✅ **Async/await:** Always `await`, never `.Result`
5. ✅ **DI:** Constructor injection, lifetimes (Transient/Scoped/Singleton)
6. ✅ **EF Core:** DbSet, Include(), LINQ queries
7. ✅ **LINQ:** Where, Select, OrderBy, FirstOrDefault, GroupBy
8. ✅ **REST:** HTTP verbs, status codes
9. ✅ **DTOs:** Separate request/response models from database models
10. ✅ **Interfaces:** Implement contracts, inject abstractions

---

## Next Steps

Focus on the mini project (`EmployeeApi`) to apply these concepts. Everything above will appear in the actual code you write.
