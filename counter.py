import os
from pathlib import Path
import pathspec  # for handling .gitignore patterns
import sys


def get_gitignore_spec(project_path):
    """Load .gitignore patterns and create a PathSpec matcher"""
    gitignore_path = Path(project_path) / '.gitignore'
    if not gitignore_path.exists():
        return None

    with open(gitignore_path, 'r') as f:
        spec = pathspec.PathSpec.from_lines(
            pathspec.patterns.GitWildMatchPattern,
            f.readlines()
        )
    return spec


def count_lines_in_project(project_path, file_type=None):
    """
    Count lines in Django project files, excluding .venv and .gitignore patterns.

    Args:
        project_path (str): Path to Django project root directory
        file_type (str): Specific file type to count ('py', 'html', 'css', 'js', or None for all)

    Returns:
        dict: Dictionary containing line counts by file type and total count
    """
    # File extensions to count
    extensions = {
        '.py': 'Python',
        '.html': 'HTML',
        '.css': 'CSS',
        '.js': 'JavaScript'
    }

    # Filter extensions based on file_type parameter
    if file_type:
        file_type = '.' + file_type.lower()
        if file_type in extensions:
            filtered_extensions = {file_type: extensions[file_type]}
            extensions = filtered_extensions
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    # Initialize counters
    counts = {ext_name: 0 for ext_name in extensions.values()}
    counts['Total'] = 0
    file_counts = {ext_name: 0 for ext_name in extensions.values()}

    # Convert to Path object and get absolute path for proper gitignore matching
    project_path = Path(project_path).resolve()

    # Load gitignore patterns
    gitignore_spec = get_gitignore_spec(project_path)

    def should_skip_path(path):
        """Check if path should be skipped"""
        rel_path = str(Path(path).relative_to(project_path))
        if '.venv' in Path(path).parts:
            return True
        if gitignore_spec and gitignore_spec.match_file(rel_path):
            return True
        return False

    # Walk through project directory
    for root, dirs, files in os.walk(project_path):
        if should_skip_path(root):
            dirs.clear()
            continue

        files = [f for f in files if not should_skip_path(Path(root) / f)]

        for file in files:
            file_path = Path(root) / file
            ext = file_path.suffix.lower()

            if ext in extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = sum(1 for line in f if line.strip())
                        file_type = extensions[ext]
                        counts[file_type] += lines
                        counts['Total'] += lines
                        file_counts[file_type] += 1
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    return counts, file_counts


def format_report(counts, file_counts):
    """Format the counting results into a readable report"""
    report = "Django Project Line Count Report\n"
    report += "=" * 30 + "\n\n"

    for file_type in counts:
        if file_type != 'Total':
            report += f"{file_type}:\n"
            report += f"  Files: {file_counts[file_type]}\n"
            report += f"  Lines: {counts[file_type]:,}\n\n"

    report += f"Total Lines: {counts['Total']:,}\n"
    return report


def main():
    project_path = os.getcwd()
    file_type = None

    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['py_only', 'html_only', 'css_only', 'js_only']:
            file_type = sys.argv[1].split('_')[0]

    try:
        counts, file_counts = count_lines_in_project(project_path, file_type)
        report = format_report(counts, file_counts)
        print(report)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()