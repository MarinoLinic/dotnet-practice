#!/usr/bin/env python3
"""
Project Exporter — converts a .NET project into a portable markdown file
Usage: python export_project.py <path_to_project>
Output: project_export.md in the current directory
"""

import os
import sys
from pathlib import Path
from datetime import datetime


def get_file_extension(filename):
    """Get file extension, determine language for syntax highlighting"""
    ext = Path(filename).suffix.lower()
    ext_map = {
        '.cs': 'csharp',
        '.json': 'json',
        '.xml': 'xml',
        '.csproj': 'xml',
        '.md': 'markdown',
        '.txt': 'text',
        '.sh': 'bash',
        '.sql': 'sql',
    }
    return ext_map.get(ext, 'text')


def should_include_file(filepath, filename):
    """Determine if a file should be included in export"""
    # Skip these directories
    skip_dirs = {
        'bin', 'obj', '.git', '.vs', 'node_modules',
        '.vscode', '.idea', 'packages'
    }
    
    # Skip these file patterns
    skip_patterns = {
        '.dll', '.exe', '.pdb', '.so', '.dylib',
        '.class', '.pyc', '.o', '.a', '.lib'
    }
    
    # Check if any part of the path is in skip_dirs
    parts = filepath.parts
    if any(part in skip_dirs for part in parts):
        return False
    
    # Check if file extension should be skipped
    if any(filename.endswith(pattern) for pattern in skip_patterns):
        return False
    
    # Skip hidden files (except .gitignore, .env files)
    if filename.startswith('.') and filename not in {'.gitignore', '.env', '.env.local'}:
        return False
    
    return True


def build_tree_structure(root_path, prefix="", is_last=True, max_depth=10, current_depth=0):
    """Build ASCII tree structure of the project"""
    if current_depth >= max_depth:
        return []
    
    lines = []
    root = Path(root_path)
    
    try:
        entries = sorted(root.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
    except PermissionError:
        return lines
    
    # Filter entries
    entries = [e for e in entries if should_include_file(e, e.name)]
    
    for i, entry in enumerate(entries):
        is_last_entry = (i == len(entries) - 1)
        current_prefix = "└── " if is_last_entry else "├── "
        
        if entry.is_dir():
            lines.append(f"{prefix}{current_prefix}{entry.name}/")
            
            # Recurse into directory
            next_prefix = prefix + ("    " if is_last_entry else "│   ")
            lines.extend(build_tree_structure(
                entry, 
                next_prefix, 
                is_last_entry,
                max_depth,
                current_depth + 1
            ))
        else:
            lines.append(f"{prefix}{current_prefix}{entry.name}")
    
    return lines


def read_file_content(filepath):
    """Read file content safely, handling encoding issues"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(filepath, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception:
            return "[Binary file or unreadable]"
    except Exception as e:
        return f"[Error reading file: {e}]"


def export_project(project_path):
    """Main export function"""
    project_path = Path(project_path)
    
    if not project_path.exists():
        print(f"Error: Path does not exist: {project_path}")
        sys.exit(1)
    
    if not project_path.is_dir():
        print(f"Error: Path is not a directory: {project_path}")
        sys.exit(1)
    
    # Find project name
    project_name = project_path.name
    csproj_files = list(project_path.glob("*.csproj"))
    if csproj_files:
        project_name = csproj_files[0].stem
    
    # Start markdown document
    md = []
    md.append(f"# {project_name} — Project Export")
    md.append(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    md.append("")
    md.append("This markdown file contains the complete project structure and all source files.")
    md.append("To reconstruct the project, create the folder structure and copy each code block into the corresponding file.")
    md.append("")
    
    # Project structure
    md.append("## Project Structure")
    md.append("")
    md.append("```")
    md.append(f"{project_name}/")
    tree_lines = build_tree_structure(project_path)
    md.extend(tree_lines)
    md.append("```")
    md.append("")
    
    # Collect all files
    all_files = []
    for root, dirs, files in os.walk(project_path):
        # Filter out directories
        dirs[:] = [d for d in dirs if d not in {
            'bin', 'obj', '.git', '.vs', 'node_modules', '.vscode', '.idea', 'packages'
        }]
        
        for filename in files:
            filepath = Path(root) / filename
            if should_include_file(filepath, filename):
                all_files.append(filepath)
    
    # Sort files by extension, then by name
    all_files.sort(key=lambda x: (x.suffix, x.name))
    
    if not all_files:
        print("Warning: No files found to export. Project might be empty or all files were filtered.")
        md.append("## Files")
        md.append("No source files found.")
    else:
        md.append("## Source Files")
        md.append("")
        
        # Group files by directory
        files_by_dir = {}
        for filepath in all_files:
            relative = filepath.relative_to(project_path)
            directory = str(relative.parent)
            if directory not in files_by_dir:
                files_by_dir[directory] = []
            files_by_dir[directory].append(filepath)
        
        # Output files grouped by directory
        for directory in sorted(files_by_dir.keys()):
            if directory == ".":
                md.append("### Root Directory")
            else:
                md.append(f"### {directory}/")
            
            md.append("")
            
            for filepath in sorted(files_by_dir[directory]):
                relative = filepath.relative_to(project_path)
                filename = filepath.name
                lang = get_file_extension(filename)
                
                md.append(f"#### {filename}")
                md.append("")
                md.append("```" + lang)
                
                content = read_file_content(filepath)
                md.append(content)
                
                md.append("```")
                md.append("")
    
    # Write to file
    output_file = Path.cwd() / "project_export.md"
    full_md = "\n".join(md)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_md)
    
    print(f"✓ Project exported successfully!")
    print(f"✓ File: {output_file}")
    print(f"✓ Files included: {len(all_files)}")
    print(f"✓ Size: {len(full_md) / 1024:.1f} KB")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python export_project.py <path_to_project>")
        print("")
        print("Example:")
        print("  python export_project.py ./EmployeeApi")
        print("  python export_project.py C:\\Users\\YourName\\EmployeeApi")
        sys.exit(1)
    
    project_path = sys.argv[1]
    export_project(project_path)
