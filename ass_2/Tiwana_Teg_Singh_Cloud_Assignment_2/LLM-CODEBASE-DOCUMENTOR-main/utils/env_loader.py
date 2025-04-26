import os
import dotenv
import logging
from typing import Dict, Any, Optional

def load_env_vars(env_file_path: str = ".env") -> Dict[str, str]:
    """
    Load environment variables from .env file.
    
    Args:
        env_file_path (str): Path to the .env file
        
    Returns:
        Dict[str, str]: Dictionary of environment variables
    """
    # Check if file exists
    if not os.path.exists(env_file_path):
        logging.warning(f".env file not found at {env_file_path}")
        return {}
    
    # Load the .env file
    dotenv.load_dotenv(env_file_path)
    
    # Return a dictionary of the loaded variables
    env_vars = {}
    try:
        with open(env_file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                try:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip().strip('"\'')
                except ValueError:
                    # Skip lines that don't have key=value format
                    continue
    except Exception as e:
        logging.error(f"Error reading .env file: {e}")
    
    return env_vars

def get_api_keys() -> Dict[str, Optional[str]]:
    """
    Get API keys from environment variables.
    
    Returns:
        Dict[str, Optional[str]]: Dictionary of API keys
    """
    return {
        "github_token": os.environ.get("GITHUB_TOKEN"),
        "openai_api_key": os.environ.get("OPENAI_API_KEY"),
        "anthropic_api_key": os.environ.get("ANTHROPIC_API_KEY"),
        "gemini_api_key": os.environ.get("GEMINI_API_KEY")
    }

def get_model_names() -> Dict[str, str]:
    """
    Get model names from environment variables.
    
    Returns:
        Dict[str, str]: Dictionary of model names
    """
    return {
        "openai_model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        "anthropic_model": os.environ.get("ANTHROPIC_MODEL", "claude-3-7-sonnet-latest"),
        "gemini_model": os.environ.get("GEMINI_MODEL", "gemini-2.5-pro-exp-03-25")
    }

def create_env_example() -> None:
    """
    Create a .env.example file with placeholders.
    """
    example_content = """# API Keys
GITHUB_TOKEN=your_github_token_here
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GEMINI_API_KEY=your_gemini_key_here

# Model Names
GEMINI_MODEL=gemini-2.5-pro-exp-03-25
OPENAI_MODEL=gpt-4o-mini
ANTHROPIC_MODEL=claude-3-7-sonnet-latest
"""
    
    try:
        with open(".env.example", 'w') as f:
            f.write(example_content)
        print("Created .env.example file")
    except Exception as e:
        print(f"Error creating .env.example file: {e}")

if __name__ == "__main__":
    # Test the environment loading
    env_vars = load_env_vars()
    print("Loaded environment variables:", list(env_vars.keys()))
    
    api_keys = get_api_keys()
    print("API Keys available:", [k for k, v in api_keys.items() if v])
    
    # Create example .env file
    create_env_example() 