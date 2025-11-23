"""
File operations for agent code generation.
"""
import os
from pathlib import Path
from typing import List


def read(path: str) -> str:
    """
    Read file contents.

    Args:
        path: File path to read

    Returns:
        File contents as string
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""
    except Exception as e:
        raise IOError(f"Failed to read {path}: {str(e)}")


def write(path: str, content: str) -> None:
    """
    Write content to a file, creating directories as needed.

    Args:
        path: File path to write
        content: Content to write
    """
    try:
        # Create parent directories if they don't exist
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        raise IOError(f"Failed to write {path}: {str(e)}")


def list_files(root: str) -> List[str]:
    """
    List all files recursively from a root directory.

    Args:
        root: Root directory path

    Returns:
        List of file paths relative to root
    """
    if not os.path.exists(root):
        return []

    files = []
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(filepath, root)
            files.append(rel_path)

    return files


def file_exists(path: str) -> bool:
    """Check if a file exists"""
    return os.path.isfile(path)


def create_directory(path: str) -> None:
    """Create a directory and all parent directories"""
    Path(path).mkdir(parents=True, exist_ok=True)
