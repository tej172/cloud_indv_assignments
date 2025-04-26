# LLM Codebase Documentor

A tool that helps developers understand codebases by generating detailed tutorials explaining core abstractions, relationships, and code organization.

## Features

1. **CLI Interface**: Generate tutorials from GitHub URLs or local directories using command-line arguments
2. **Web Interface**: User-friendly Streamlit UI for repository search and tutorial generation
3. **Smart GitHub Search**: Natural language query processing to find relevant repositories
4. **Advanced Filtering**: Sort and filter repositories by stars, forks, language, and more
5. **Customizable LLM Providers**: Support for OpenAI, Anthropic Claude, and Google Gemini

## Installation

1. Clone the repository:
   ```bash
   git clone
   cd LLM-CODEBASE-DOCUMENTOR
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables by creating a `.env` file (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```
   
4. Edit the `.env` file to add your API keys:
   ```
   GITHUB_TOKEN=your_github_token_here
   OPENAI_API_KEY=your_openai_key_here
   ANTHROPIC_API_KEY=your_anthropic_key_here
   GEMINI_API_KEY=your_gemini_key_here
   ```

## Usage

### Command Line Interface

Generate a tutorial for a GitHub repository:
```bash
python main.py --repo https://github.com/username/repository
```

Generate a tutorial for a local directory:
```bash
python main.py --dir /path/to/local/codebase
```

Additional options:
```
--model [anthropic-claude|google-gemini|openai-gpt]  # Choose LLM provider
--name PROJECT_NAME                                  # Custom project name
--token GITHUB_TOKEN                                 # GitHub token (if not in .env)
--output OUTPUT_DIR                                  # Output directory
--include "*.py" "*.js"                              # File patterns to include
--exclude "tests/*" "docs/*"                         # File patterns to exclude
--max-size SIZE_BYTES                                # Maximum file size
```

### Web Interface

Start the Streamlit web app:
```bash
streamlit run streamlit_app.py
```

Then open your browser at http://localhost:8501 to access the web interface.

## How It Works

1. **Repository Crawling**: Fetches code from GitHub or local directory
2. **Abstraction Identification**: Analyzes code to identify key abstractions
3. **Relationship Analysis**: Determines how abstractions interact
4. **Chapter Generation**: Creates beginner-friendly tutorials for each abstraction
5. **Tutorial Assembly**: Combines chapters with a diagram in structured Markdown

## LLM Providers

The tool supports three LLM providers:
- **Google Gemini** (default): Uses Google's Gemini 2.5 Pro model or any other Gemini models supported via API calls
- **Anthropic Claude**: Uses Claude 3.7 Sonnet model or any other Anthropic models supported via API calls
- **OpenAI GPT**: Uses GPT-4o-mini model or any other OpenAI models supported via API calls

## Credits

This project uses PocketFlow library, a minimalist LLM framework for agent-based workflows. 