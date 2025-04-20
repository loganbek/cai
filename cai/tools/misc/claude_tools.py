"""
Text editor tools module for viewing and modifying files.

Provides utilities for file operations such as viewing file contents,
replacing text, creating files, inserting text, and undoing edits.
"""

from cai.tools.common import run_command  # pylint: disable=E0401


def view(path: str, view_range: list = None) -> str:
    """
    View the contents of a file or list the contents of a directory.

    Args:
        path (str): The path to the file or directory to view.
        view_range (list, optional): An array of two integers specifying
            the start and end line numbers to view. Line numbers are 1-indexed,
            and -1 for the end line means read to the end of the file.
            This parameter only applies when viewing files, not directories.

    Returns:
        str: The contents of the file or directory listing.
    """
    if view_range:
        start_line, end_line = view_range
        if end_line == -1:
            command = f"sed -n '{start_line},$ p' {path}"
        else:
            command = f"sed -n '{start_line},{end_line}p' {path}"
    else:
        # Check if path is a directory
        is_dir_command = f"[ -d {path} ] && echo 'directory' || echo 'file'"
        path_type = run_command(is_dir_command).strip()
        
        if path_type == "directory":
            command = f"ls -la {path}"
        else:
            command = f"cat {path}"
    
    return run_command(command)


def str_replace(path: str, old_str: str, new_str: str) -> str:
    """
    Replace a specific string in a file with a new string.

    Args:
        path (str): The path to the file to modify.
        old_str (str): The text to replace (must match exactly,
            including whitespace and indentation).
        new_str (str): The new text to insert in place of the old text.

    Returns:
        str: A message indicating the result of the operation.
    """
    try:
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        if old_str not in content:
            return f"Error: The string to replace was not found in {path}"
        
        new_content = content.replace(old_str, new_str)
        
        with open(path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        # Return both success message and the modified content
        return f"Successfully replaced text in {path}\n\nModified content:\n{new_content}"
    except Exception as e:
        return f"Error replacing text in {path}: {str(e)}"


def create(path: str, file_text: str) -> str:
    """
    Create a new file with specified content.

    Args:
        path (str): The path where the new file should be created.
        file_text (str): The content to write to the new file.

    Returns:
        str: A message indicating the result of the operation.
    """
    try:
        with open(path, 'w', encoding='utf-8') as file:
            file.write(file_text)
        
        # Return success message and the content that was written
        return f"Successfully created file at {path}\n\nFile content:\n{file_text}"
    except Exception as e:
        return f"Error creating file at {path}: {str(e)}"


def insert(path: str, insert_line: int, new_str: str) -> str:
    """
    Insert text at a specific location in a file.

    Args:
        path (str): The path to the file to modify.
        insert_line (int): The line number after which to insert the text
            (0 for beginning of file).
        new_str (str): The text to insert.

    Returns:
        str: A message indicating the result of the operation.
    """
    try:
        with open(path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Make a backup of the original content
        with open(f"{path}.bak", 'w', encoding='utf-8') as backup:
            backup.writelines(lines)
        
        if insert_line == 0:
            lines.insert(0, new_str)
        else:
            if insert_line > len(lines):
                return f"Error: Line {insert_line} exceeds file length of {len(lines)}"
            
            lines.insert(insert_line, new_str)
        
        with open(path, 'w', encoding='utf-8') as file:
            file.writelines(lines)
        
        # Return success message and the modified content
        return f"Successfully inserted text at line {insert_line} in {path}\n\nModified content:\n{''.join(lines)}"
    except Exception as e:
        return f"Error inserting text in {path}: {str(e)}"


def undo_edit(path: str) -> str:
    """
    Revert the last edit made to a file.

    Args:
        path (str): The path to the file whose last edit should be undone.

    Returns:
        str: A message indicating the result of the operation.
    """
    backup_path = f"{path}.bak"
    try:
        # Check if backup file exists
        backup_exists = run_command(f"[ -f {backup_path} ] && echo 'exists'").strip()
        
        if backup_exists != "exists":
            return f"Error: No backup file found for {path}"
        
        # Restore from backup
        with open(backup_path, 'r', encoding='utf-8') as backup:
            content = backup.read()
        
        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        # Remove the backup file
        run_command(f"rm {backup_path}")
        
        # Return success message and the restored content
        return f"Successfully undid the last edit to {path}\n\nRestored content:\n{content}"
    except Exception as e:
        return f"Error undoing edit to {path}: {str(e)}"


