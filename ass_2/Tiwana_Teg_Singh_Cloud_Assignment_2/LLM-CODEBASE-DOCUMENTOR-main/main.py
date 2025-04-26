import dotenv
import os
import argparse
# Import the function that creates the flow
from flow import create_tutorial_flow
from utils.call_llm import LLMProvider_enum

# Load environment variables from .env file
dotenv.load_dotenv()

# Default file patterns
DEFAULT_INCLUDE_PATTERNS = {
    "*.py", "*.js", "*.jsx", "*.ts", "*.tsx", "*.go", "*.java", "*.pyi", "*.pyx", 
    "*.c", "*.cc", "*.cpp", "*.h", "*.md", "*.rst", "Dockerfile", 
    "Makefile", "*.yaml", "*.yml", "*.ipynb", "*.html", "*.css", "*.scss",
    "*.json", "*.txt", "*.csv", "*.xml", "*.proto", "*.sql", "*.sh",
    "*.bat", "*.ps1", "*.rb", "*.php", "*.swift", "*.kotlin", "*.dart",
    "*.pl", "*.asm", "*.asmx", "*.gohtml", "*.vue", "*.twig", "*.less", ".md"
}

DEFAULT_EXCLUDE_PATTERNS = {
    "*test*", "tests/*", "docs/*", "examples/*", "v1/*", 
    "dist/*", "build/*", "experimental/*", "deprecated/*", 
    "legacy/*", ".git/*", ".github/*", ".next/*", ".vscode/*", "obj/*", "bin/*", "node_modules/*", "*.log"
}

# --- Main Fn ---
def main():
    parser = argparse.ArgumentParser(description="Use this script to analyze a GitHub repository or local codebase and generate a structured, " \
                                                "AI-friendly tutorial. Ideal for experimenting with LLMs and building a SaaS code-search or " \
                                                "doc generation tool.")
    
    # Create mutually exclusive group for source
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--repo", help="If GITHUB dir is online: Specify the URL of a public GitHub repository "
                                            "(i.e. https://github.com/[user]/[project]). This will fetch code using the GitHub REST API.")
    
    source_group.add_argument("--dir", help="If GITHUB dir is pulled locally to local folder dir: Provide a local directory path to analyze " \
                                            "code on your machine instead of pulling from GitHub.")

    # Added argument for LLM provider
    # Note: LLMProvider_enum is an Enum class that contains the available LLM providers
    # The choices are the values of the enum members: 
    # LLMProvider_enum('anthropic-claude'),  LLMProvider_enum('google-gemini') & 'openai-gpt': LLMProvider_enum('openai-gpt') /or/
    # LLMProvider_enum.ANTHROPIC , LLMProvider_enum.GOOGLE & openai: LLMProvider_enum.OPENAI
    parser.add_argument("--model", type=str, choices=[e.value for e in LLMProvider_enum], 
                        default=LLMProvider_enum.GOOGLE.value, help="LLM provider to use: " \
                        "'anthropic-claude', 'google-gemini', or 'openai-gpt'. Choose based " \
                        "on your access/API tokens, model preference and task requirements. Default is 'google-gemini'.")
    
    # Optional arguments    
    parser.add_argument("-n", "--name", help="Optional: Define a custom project name for output purposes. " \
                                            "If omitted, the name is inferred from the repo URL or folder name.")
    
    parser.add_argument("-t", "--token", help="Optional: Your GitHub Personal Access Token for authenticated API access. " \
                                            "Required if accessing private repositories or hitting rate limits. " \
                                            "If not provided, it checks the GITHUB_TOKEN environment variable.")
    
    parser.add_argument("-o", "--output", default="output", help="Base output directory for all generated documentation "
                                                                "and results (default is './output').")
    
    parser.add_argument("-i", "--include", nargs="+", help="List of file patterns to include during analysis (e.g., '*.py', '*.js'). " \
                                                            "Useful if you're building a WebGPT-based documentation generator or " \
                                                            "doing language-specific LLM tasks on specific file tupes. Defaults to common code files if not specified.")
    
    parser.add_argument("-e", "--exclude", nargs="+", help="List of file or directory patterns to ignore (e.g., 'tests/*', 'docs/*'). " \
                                                            "Helps exclude irrelevant or noisy files from analysis. Exclude file patterns "
                                                            "(e.g. 'tests/*' 'docs/*'). Defaults to test/build directories if not specified.")
    
    parser.add_argument("-s", "--max-size", type=int, default=300000, help="Ignore files larger than this size (in bytes). " \
                                                            "Default is 300,000 (~300KB). This prevents feeding overly large files into the LLM, " \
                                                            "which may affect generation quality or exceed context limits. Maximum file size "
                                                            "in bytes (default: 300,000 (300000), about 300KB).")

    args = parser.parse_args()

    # Get GitHub token from argument or environment variable if using repo
    github_token = None
    if args.repo:
        github_token = args.token or os.environ.get('GITHUB_TOKEN')
        if not github_token:
            print("Warning: No GitHub token provided. You might hit rate limits for public repositories.")

    # Initialize the shared dictionary with inputs
    shared = {
        "repo_url": args.repo,
        "local_dir": args.dir,
        "project_name": args.name, # Can be None, FetchRepo will derive it
        "github_token": github_token,
        "output_dir": args.output, # Base directory for output tut
        "model_used": args.model, # LLM provider to use as string
        "llm_provider": LLMProvider_enum(args.model), # LLM provider enum version, usable in call_llm()


        # Add include/exclude patterns and max file size
        "include_patterns": set(args.include) if args.include else DEFAULT_INCLUDE_PATTERNS,
        "exclude_patterns": set(args.exclude) if args.exclude else DEFAULT_EXCLUDE_PATTERNS,
        "max_file_size": args.max_size,

        # Outputs will be populated by the nodes
        "files": [],
        "abstractions": [],
        "relationships": {},
        "chapter_order": [],
        "chapters": [],
        "final_output_dir": None
    }

    print(f"Starting tutorial generation for: {args.repo or args.dir}")

    # Create the flow instance
    tutorial_flow = create_tutorial_flow()

    # Run the flow
    tutorial_flow.run(shared)
    
if __name__ == "__main__":
    main()