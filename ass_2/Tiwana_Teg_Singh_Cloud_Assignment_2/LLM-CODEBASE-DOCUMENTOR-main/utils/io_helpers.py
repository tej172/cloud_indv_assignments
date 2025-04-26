import os
import zipfile
import tempfile
from typing import Optional
import shutil
import datetime

def zip_output_folder(folder_path: str, output_zip_path: Optional[str] = None) -> str:
    """
    Create a ZIP archive of the output folder.
    
    Args:
        folder_path (str): Path to the folder to zip
        output_zip_path (str, optional): Path for the output ZIP file.
                                         If None, a temporary file is created.
    
    Returns:
        str: Path to the created ZIP file
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder not found: {folder_path}")
    
    if not output_zip_path:
        # Generate a default filename based on the folder name and timestamp
        folder_name = os.path.basename(folder_path)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_zip_path = os.path.join(
            tempfile.gettempdir(), 
            f"{folder_name}_{timestamp}.zip"
        )
    
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk through all files in the directory
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Calculate path relative to the folder root for the archive
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)
    
    return output_zip_path

def load_env_vars(env_file_path: str) -> None:
    """
    Load environment variables from .env file if dotenv module is available.
    Fallback to manual loading if not.
    
    Args:
        env_file_path (str): Path to the .env file
    """
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file_path)
    except ImportError:
        print("python-dotenv not found, using manual .env loading")
        # Manual loading of .env as fallback
        try:
            with open(env_file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip().strip('"\'')
        except Exception as e:
            print(f"Error loading .env file: {e}")

def read_markdown_file(file_path: str) -> str:
    """
    Read a Markdown file and return its content as a string.
    
    Args:
        file_path (str): Path to the Markdown file
    
    Returns:
        str: Content of the Markdown file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def read_all_markdown_files(directory: str) -> dict:
    """
    Read all Markdown files in a directory.
    
    Args:
        directory (str): Path to the directory
    
    Returns:
        dict: Dictionary with filenames as keys and content as values
    """
    result = {}
    try:
        for filename in os.listdir(directory):
            if filename.endswith('.md'):
                file_path = os.path.join(directory, filename)
                result[filename] = read_markdown_file(file_path)
    except Exception as e:
        print(f"Error reading directory: {e}")
    
    return result

if __name__ == "__main__":
    # Test zipping a directory
    test_dir = "."
    zip_path = zip_output_folder(test_dir)
    print(f"Created ZIP file: {zip_path}") 