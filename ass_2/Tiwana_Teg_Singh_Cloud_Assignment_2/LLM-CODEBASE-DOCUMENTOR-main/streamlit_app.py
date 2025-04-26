import streamlit as st
import os
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import utilities
from utils.env_loader import load_env_vars, get_api_keys, get_model_names, create_env_example
from utils.call_llm import LLMProvider_enum
from utils.github_api import RepoMetadata

# Import the flow
from flow import create_streamlit_flow
from nodes import SmartSearchRepo, FilterRepos, SelectRepository, RenderAndDownload

# Load environment variables
load_env_vars()

# 1. Page configuration (with a custom About menu item)
st.set_page_config(
    page_title="📖🤓 LLM Codebase Finder & Documentor",
    page_icon="🧐",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': (
            "### LLM Codebase Documentor\n"
            "A&nbsp;Streamlit app to auto-generate beginner-friendly tutorials from any GitHub repo.\n\n"
            "Built by **TEG SINGH TIWANA** for Cloud Assignment 2:\n"
            "[GitHub LLM Codebase Knowledge Building Summarizer](https://github.com/tej172/cloud_indv_assignments/tree/main/ass_2)"
        )
    }
)
# Initialize session state if not already done
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.search_results = []
    st.session_state.selected_repo = None
    st.session_state.filter_params = {
        "min_stars": 0,
        "min_forks": 0,
        "language": "",
        "sort_by": "stars",
        "updated_since": ""
    }
    st.session_state.shared_store = {}
    st.session_state.markdown_files = {}
    st.session_state.zip_path = None
    st.session_state.task_completed = False
    st.session_state.ui_view = "search"  # Possible values: search, results, tutorial
    
    # Get API keys from environment
    api_keys = get_api_keys()
    for key, value in api_keys.items():
        st.session_state[key] = value or ""
    
    # Get model names from environment
    model_names = get_model_names()
    for key, value in model_names.items():
        st.session_state[key] = value

# --- Sidebar ---
with st.sidebar:
    st.title("LLM Codebase Documentor")
    
    # Create tabs for different sidebar sections
    tab1, tab2, tab3 = st.tabs(["Search", "API Keys", "Model Settings"])
    
    with tab1:
        # Search input and type
        st.subheader("Repository Search")
        query_input = st.text_input(
            "Enter GitHub URL, local path, or natural language query:",
            placeholder="e.g., https://github.com/user/repo OR frameworks for UI prototyping"
        )
        
        # Filters (only shown for natural language search)
        st.subheader("Filters")
        min_stars = st.number_input("Minimum Stars", min_value=0, value=st.session_state.filter_params["min_stars"])
        min_forks = st.number_input("Minimum Forks", min_value=0, value=st.session_state.filter_params["min_forks"])
        language = st.selectbox(
            "Language", 
            ["", "Python", "JavaScript", "TypeScript", "Java", "Go", "Rust", "C++", "Ruby", "PHP"],
            index=0
        )
        sort_by = st.selectbox(
            "Sort By", 
            ["stars", "forks", "updated", "help-wanted-issues"],
            index=0
        )
        updated_since = st.date_input(
            "Updated Since", 
            value=None
        )
        
        # Update filter params in session state
        if st.button("Search", key="search_button"):
            # Update filter params
            st.session_state.filter_params = {
                "min_stars": min_stars,
                "min_forks": min_forks,
                "language": language,
                "sort_by": sort_by,
                "updated_since": updated_since.isoformat() if updated_since else ""
            }
            
            # Initialize shared store for the flow
            st.session_state.shared_store = {
                "query_input": query_input,
                "filter_params": st.session_state.filter_params,
                "github_token": st.session_state.github_token,
                "llm_provider": LLMProvider_enum(st.session_state.provider_selection),
                
                # Default parameters from original flow
                "include_patterns": {
                    "*.py", "*.js", "*.jsx", "*.ts", "*.tsx", "*.go", "*.java", "*.pyi", "*.pyx", 
                    "*.c", "*.cc", "*.cpp", "*.h", "*.md", "*.rst", "Dockerfile", 
                    "Makefile", "*.yaml", "*.yml", "*.ipynb", "*.html", "*.css", "*.scss",
                    "*.json", "*.txt", "*.csv", "*.xml", "*.proto", "*.sql", "*.sh",
                    "*.bat", "*.ps1", "*.rb", "*.php", "*.swift", "*.kotlin", "*.dart",
                    "*.pl", "*.asm", "*.asmx", "*.gohtml", "*.vue", "*.twig", "*.less", "*.md", "*.pdf"
                },
                "exclude_patterns": {
                    "*test*", "tests/*", "docs/*", "examples/*", "v1/*", 
                    "dist/*", "build/*", "experimental/*", "deprecated/*", 
                    "legacy/*", ".git/*", ".github/*", ".next/*", ".vscode/*", "obj/*", "bin/*", "node_modules/*", "*.log"
                },
                "max_file_size": 300000,
                "output_dir": "output"
            }
            
            # Create the flow
            flow = create_streamlit_flow()
            
            # Run the SmartSearchRepo and FilterRepos nodes
            with st.spinner("Processing query..."):
                # Set state to indicate we're waiting for results
                st.session_state.ui_view = "results"
                
                # Run the SmartSearch and FilterRepos nodes
                smart_search = SmartSearchRepo()
                filter_repos = FilterRepos()
                
                # Run nodes sequentially
                smart_search.run(st.session_state.shared_store)
                filter_repos.run(st.session_state.shared_store)
                
                # Update session state with search results
                if "search_results" in st.session_state.shared_store:
                    st.session_state.search_results = st.session_state.shared_store["search_results"]
                
                # If we have a selected_repo, run the full pipeline
                if "selected_repo" in st.session_state.shared_store:
                    st.session_state.selected_repo = st.session_state.shared_store["selected_repo"]
                    with st.spinner("Generating tutorial..."):
                        st.session_state.ui_view = "tutorial"
                        # Run the full flow
                        flow.run(st.session_state.shared_store)
                        
                        # Get the rendered Markdown files and ZIP path if available
                        if "markdown_files" in st.session_state.shared_store:
                            st.session_state.markdown_files = st.session_state.shared_store["markdown_files"]
                        if "zip_path" in st.session_state.shared_store:
                            st.session_state.zip_path = st.session_state.shared_store["zip_path"]
                        
                        st.session_state.task_completed = True
    
    with tab2:
        st.subheader("API Keys")
        
        # GitHub token
        github_token = st.text_input(
            "GitHub Token",
            value=st.session_state.github_token,
            type="password",
            help="Required for private repos or to avoid rate limits"
        )
        st.session_state.github_token = github_token
        
        # LLM API keys
        openai_api_key = st.text_input(
            "OpenAI API Key",
            value=st.session_state.openai_api_key,
            type="password"
        )
        st.session_state.openai_api_key = openai_api_key
        
        anthropic_api_key = st.text_input(
            "Anthropic API Key",
            value=st.session_state.anthropic_api_key,
            type="password"
        )
        st.session_state.anthropic_api_key = anthropic_api_key
        
        gemini_api_key = st.text_input(
            "Google Gemini API Key",
            value=st.session_state.gemini_api_key,
            type="password"
        )
        st.session_state.gemini_api_key = gemini_api_key
        
        # Save API keys to environment
        if st.button("Save API Keys"):
            os.environ["GITHUB_TOKEN"] = github_token
            os.environ["OPENAI_API_KEY"] = openai_api_key
            os.environ["ANTHROPIC_API_KEY"] = anthropic_api_key
            os.environ["GEMINI_API_KEY"] = gemini_api_key
            st.success("API keys saved to environment!")
    
    with tab3:
        st.subheader("Model Settings")
        
        # LLM Provider selection
        provider_selection = st.selectbox(
            "LLM Provider",
            options=[provider.value for provider in LLMProvider_enum],
            index=0
        )
        st.session_state.provider_selection = provider_selection
        
        # Model name based on provider
        if provider_selection == LLMProvider_enum.OPENAI.value:
            model_name = st.text_input(
                "OpenAI Model",
                value=st.session_state.openai_model
            )
            st.session_state.openai_model = model_name
            os.environ["OPENAI_MODEL"] = model_name
        
        elif provider_selection == LLMProvider_enum.ANTHROPIC.value:
            model_name = st.text_input(
                "Anthropic Model",
                value=st.session_state.anthropic_model
            )
            st.session_state.anthropic_model = model_name
            os.environ["ANTHROPIC_MODEL"] = model_name
        
        else:  # Gemini
            model_name = st.text_input(
                "Google Gemini Model",
                value=st.session_state.gemini_model
            )
            st.session_state.gemini_model = model_name
            os.environ["GEMINI_MODEL"] = model_name
            
        # Add save button for model settings
        if st.button("Save Model Settings"):
            # Save provider selection to session state
            st.session_state.provider_selection = provider_selection
            st.session_state.shared_store["llm_provider"] = LLMProvider_enum(provider_selection)
            
            # Save model name based on provider
            if provider_selection == LLMProvider_enum.OPENAI.value:
                os.environ["OPENAI_MODEL"] = model_name
                st.session_state.openai_model = model_name
            elif provider_selection == LLMProvider_enum.ANTHROPIC.value:
                os.environ["ANTHROPIC_MODEL"] = model_name
                st.session_state.anthropic_model = model_name
            else:  # Gemini
                os.environ["GEMINI_MODEL"] = model_name
                st.session_state.gemini_model = model_name
                
            st.success(f"Model settings saved! Provider: {provider_selection}, Model: {model_name}")

# --- Main Content ---
def display_repo_card(repo: RepoMetadata, index: int):
    """Display a repository card with details and select button."""
    col1, col2 = st.columns([1, 4])
    
    with col1:
        st.image("https://github.githubassets.com/favicons/favicon.png", width=50)
        st.button(f"Select", key=f"select_{index}", on_click=select_repository, args=(repo.url,))
    
    with col2:
        st.markdown(f"### [{repo.full_name}]({repo.url})")
        st.markdown(f"**Description:** {repo.description}")
        st.markdown(f"**Summary:** {repo.readme_summary}")
        st.markdown(f"**Language:** {repo.language} | **Stars:** {repo.stars} | **Forks:** {repo.forks}")

def select_repository(repo_url: str):
    """Handle repository selection from search results."""
    st.session_state.selected_repo = repo_url
    
    # Make sure we have the shared store initialized
    if not st.session_state.shared_store:
        st.session_state.shared_store = {}
    
    # Set the selected repository URL in the shared store
    st.session_state.shared_store["selected_repo"] = repo_url
    st.session_state.shared_store["repo_url"] = repo_url
    st.session_state.shared_store["local_dir"] = None
    
    # Make sure we have other necessary parameters in the shared store
    if "include_patterns" not in st.session_state.shared_store:
        st.session_state.shared_store["include_patterns"] = {
            "*.py", "*.js", "*.jsx", "*.ts", "*.tsx", "*.go", "*.java", "*.pyi", "*.pyx", 
            "*.c", "*.cc", "*.cpp", "*.h", "*.md", "*.rst", "Dockerfile", 
            "Makefile", "*.yaml", "*.yml", "*.ipynb", "*.html", "*.css", "*.scss",
            "*.json", "*.txt", "*.csv", "*.xml", "*.proto", "*.sql", "*.sh",
            "*.bat", "*.ps1", "*.rb", "*.php", "*.swift", "*.kotlin", "*.dart",
            "*.pl", "*.asm", "*.asmx", "*.gohtml", "*.vue", "*.twig", "*.less", ".md"
        }
    
    if "exclude_patterns" not in st.session_state.shared_store:
        st.session_state.shared_store["exclude_patterns"] = {
            "*test*", "tests/*", "docs/*", "examples/*", "v1/*", 
            "dist/*", "build/*", "experimental/*", "deprecated/*", 
            "legacy/*", ".git/*", ".github/*", ".next/*", ".vscode/*", "obj/*", "bin/*", "node_modules/*", "*.log"
        }
        
    if "max_file_size" not in st.session_state.shared_store:
        st.session_state.shared_store["max_file_size"] = 300000
        
    if "output_dir" not in st.session_state.shared_store:
        st.session_state.shared_store["output_dir"] = "output"
        
    if "github_token" not in st.session_state.shared_store:
        st.session_state.shared_store["github_token"] = st.session_state.github_token
        
    if "llm_provider" not in st.session_state.shared_store:
        st.session_state.shared_store["llm_provider"] = LLMProvider_enum(st.session_state.provider_selection)
    
    st.session_state.ui_view = "tutorial"
    
    # Create and run the flow
    flow = create_streamlit_flow()
    with st.spinner("Generating tutorial..."):
        # Run the full flow
        flow.run(st.session_state.shared_store)
        
        # Get the rendered Markdown files and ZIP path if available
        if "markdown_files" in st.session_state.shared_store:
            st.session_state.markdown_files = st.session_state.shared_store["markdown_files"]
        if "zip_path" in st.session_state.shared_store:
            st.session_state.zip_path = st.session_state.shared_store["zip_path"]
        
        st.session_state.task_completed = True

# Conditional display based on current view
if st.session_state.ui_view == "search":
    # Show welcome message and instructions
    st.title("Welcome to **GITHUB** Finder & Documentor📖🤓")
    st.markdown("""
    **Built by [TEG SINGH TIWANA](https://github.com/tej172)** for _Cloud Assignment 2_:  
    [GitHub LLM Codebase Knowledge Building Summarizer](https://github.com/tej172/cloud_indv_assignments/tree/main/ass_2)

    #### Welcome to **LLM Codebase Documentor**, your friendly assistant for auto-generating beginner-friendly tutorials from any codebase! 
    ###### This tool helps you understand codebases by generating detailed tutorials explaining core abstractions, relationships, and code organization.
    
    ### Getting Started
    1. In the **sidebar**, enter one of:
       - A **GitHub URL** (e.g. `https://github.com/user/repo`)
       - A **local folder path** on your machine
       - A **natural language** query (e.g. "frameworks for UI prototyping")
    2. If you chose natural language, adjust **advanced filters** (stars, forks, language, updated date).
    3. Click **Search** to fetch repositories or **Generate** to build the tutorial.
    
    ### Features
    - 🔍 **Smart Search** powered by GPT / Gemini / Claude for effortless keyword extraction  
    - 📂 **Local Path** support—point to any folder you've already cloned  
    - ⭐ **Advanced Filters**—stars, forks, issues, language, last‐updated  
    - 📄 **Markdown Preview**—click through `index.md` and each chapter in-app  
    - 📥 **Downloadable ZIP**—grab your entire tutorial with one click  

    > _Tip_: Make sure your **API keys** (GITHUB_TOKEN, OPENAI_API_KEY, GEMINI_API_KEY, etc.) are set in the sidebar or in your `.env` file.
    """)
    
elif st.session_state.ui_view == "results":
    # Show search results
    st.title("Search Results")
    
    if st.session_state.search_results:
        st.markdown(f"Found {len(st.session_state.search_results)} repositories matching your query.")
        for i, repo in enumerate(st.session_state.search_results):
            with st.container():
                display_repo_card(repo, i)
                st.markdown("---")
    else:
        st.info("No results found. Try different keywords or filters.")
        
elif st.session_state.ui_view == "tutorial":
    # Show the generated tutorial
    project_name = st.session_state.shared_store.get("project_name", "Repository")
    st.title(f"Tutorial for {project_name}")
    
    # Download button for ZIP if available
    if st.session_state.zip_path:
        with open(st.session_state.zip_path, "rb") as f:
            st.download_button(
                label="Download Tutorial ZIP",
                data=f,
                file_name=f"{project_name}_tutorial.zip",
                mime="application/zip"
            )
    
    # Display the Markdown files
    if st.session_state.markdown_files:
        # First show index.md if it exists
        if "index.md" in st.session_state.markdown_files:
            st.markdown(st.session_state.markdown_files["index.md"])
            st.markdown("---")
        
        # Then show all other files in order
        for filename in sorted([f for f in st.session_state.markdown_files if f != "index.md"]):
            with st.expander(f"{filename}", expanded=True):
                st.markdown(st.session_state.markdown_files[filename])
    else:
        st.info("Generating tutorial content... Please wait.")

# Footer
st.markdown("---")
st.markdown(
    "LLM Codebase Documentor NTU © 2025 | "
    "[View on GitHub](https://github.com/tej172/cloud_indv_assignments/tree/main/ass_2) |  "
    "Created by [**TEG SINGH TIWANA (U2122816B)**](https://github.com/tej172) | "
    "[Cloud Assignment 2 – GitHub LLM Codebase Knowledge Building Summarizer](https://github.com/tej172/cloud_indv_assignments/tree/main/ass_2)"
)

# Create .env.example file if it doesn't exist
if not os.path.exists(".env.example"):
    create_env_example() 