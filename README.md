# EmployeeApi

This repository contains a .NET 10 Web API project created from the `dotnet new webapi -n EmployeeApi` template and extended with SQLite support.

## What it contains

- `EmployeeApi.csproj` - .NET 10 Web API project file
- `Program.cs` - minimal Web API startup program with a sample `/weatherforecast` endpoint
- `appsettings.json` / `appsettings.Development.json` - JSON configuration files
- `Properties/launchSettings.json` - local launch profiles for development
- `bin/`, `obj/` - generated build artifacts (ignored by `.gitignore`)
- `EmployeeApi.http` - optional HTTP request file that may be used for local testing
- `export_project.py` and `interview_study_plan.md` - additional workspace files

## Commands used to create this project

The project was created using these commands from the repo root:

```powershell
# Create a new ASP.NET Core Web API project with .NET 10
dotnet new webapi -n EmployeeApi
```

This generated the Web API project, including `Program.cs`, default endpoints, launch settings, and the project file.

```powershell
# Add Entity Framework Core SQLite provider
dotnet add package Microsoft.EntityFrameworkCore.Sqlite
```

This installed SQLite database support for EF Core.

```powershell
# Add EF Core design tools for migrations and tooling support
dotnet add package Microsoft.EntityFrameworkCore.Design
```

This added the design-time tooling package used by EF Core migrations and scaffolding.

## Installed packages

The project includes these NuGet references:

- `Microsoft.AspNetCore.OpenApi` 10.0.8
- `Microsoft.EntityFrameworkCore.Sqlite` 10.0.8
- `Microsoft.EntityFrameworkCore.Design` 10.0.8

## Installation

1. Open a terminal in the repo root:

   ```powershell
   cd "C:\Users\marin\OneDrive\Documents\My Programs\dotnet-practice"
   ```

2. Restore packages:

   ```powershell
   dotnet restore
   ```

> The project was created with .NET 10 and already restored as part of `dotnet new webapi` and the added EF Core packages.

## Run the project

Start the API locally with:

```powershell
dotnet run
```

By default, the app will run on HTTPS and expose the generated OpenAPI document in development mode.

## What to expect

The current application includes one sample endpoint:

- `GET /weatherforecast` — returns a small array of weather forecast data

## Notes

- `bin/` and `obj/` are ignored by `.gitignore`
- `appsettings.Development.json` and `Properties/launchSettings.json` are local development files and are also ignored
- The project is configured for .NET 10 and SQLite-based Entity Framework Core support
