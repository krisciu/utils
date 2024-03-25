import os
import sys
import fnmatch

def load_gitignore_patterns(directory, root_directory):
    """Load .gitignore patterns from the given directory, adjusting for rooted patterns."""
    patterns = []  # Patterns applicable to this directory and its subdirectories
    gitignore_path = os.path.join(directory, '.gitignore')
    if os.path.isfile(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as file:
            for line in file:
                stripped_line = line.strip()
                if stripped_line and not stripped_line.startswith('#'):
                    if stripped_line.startswith('/'):
                        relative_path = os.path.relpath(directory, root_directory).replace('\\', '/')
                        pattern = stripped_line.lstrip('/') if relative_path == '.' else os.path.join(relative_path, stripped_line.lstrip('/'))
                    else:
                        pattern = os.path.join(directory, stripped_line).replace('\\', '/')
                    patterns.append(pattern)
    return patterns

def is_ignored(path, patterns, root_directory):
    """Check if the given path matches any of the ignore patterns, considering root directory."""
    for pattern in patterns:
        pattern = os.path.join(root_directory, pattern).replace('\\', '/')
        if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(path + '/', pattern):
            return True
    return False

def concatenate_files(root_directory, output_filename):
    concatenated_contents = ""
    # Ignore .git globally and any package-lock.json files
    global_ignore_patterns = [os.path.join(root_directory, '.git'), "**/package-lock.json"]

    for root, dirs, files in os.walk(root_directory, topdown=True):
        local_ignore_patterns = global_ignore_patterns + load_gitignore_patterns(root, root_directory)
        
        dirs[:] = [d for d in dirs if not is_ignored(os.path.join(root, d), local_ignore_patterns, root_directory)]

        for file in files:
            file_path = os.path.join(root, file)
            if is_ignored(file_path, local_ignore_patterns, root_directory):
                continue

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                relative_path = os.path.relpath(file_path, root_directory)
                concatenated_contents += f"\n\n---\nFile: {relative_path}\n---\n{content}"

    with open(output_filename, 'w', encoding='utf-8') as output_file:
        output_file.write(concatenated_contents)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <directory> <output_filename>")
    else:
        root_directory = sys.argv[1]
        output_filename = sys.argv[2]
        concatenate_files(root_directory, output_filename)
        print(f"All files in {root_directory}, respecting .gitignore rules, excluding .git, and ignoring package-lock.json, have been concatenated into {output_filename}.")
