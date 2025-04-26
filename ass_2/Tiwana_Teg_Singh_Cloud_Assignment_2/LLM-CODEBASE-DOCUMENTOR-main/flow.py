from pocketflow import Flow

# Import all node classes from nodes.py
from nodes import (
    FetchRepo,
    IdentifyAbstractions,
    AnalyzeRelationships,
    OrderChapters,
    WriteChapters,
    CombineTutorial,
    # New nodes for Streamlit UI
    SmartSearchRepo,
    FilterRepos,
    SelectRepository,
    RenderAndDownload
)



def create_tutorial_flow():
    """Creates and returns the codebase tutorial generation flow."""

    # Instantiate nodes
    fetch_repo = FetchRepo()
    identify_abstractions = IdentifyAbstractions(max_retries=3, wait=10)
    analyze_relationships = AnalyzeRelationships(max_retries=3, wait=10)
    order_chapters = OrderChapters(max_retries=3, wait=10)
    write_chapters = WriteChapters(max_retries=3, wait=10) # This is a BatchNode
    combine_tutorial = CombineTutorial()

    # Connect nodes in sequence based on the design
    fetch_repo >> identify_abstractions
    identify_abstractions >> analyze_relationships
    analyze_relationships >> order_chapters
    order_chapters >> write_chapters
    write_chapters >> combine_tutorial

    # Create the flow starting with FetchRepo
    tutorial_flow = Flow(start=fetch_repo)

    return tutorial_flow, fetch_repo, combine_tutorial

def create_streamlit_flow():
    """Creates and returns the Streamlit UI flow with search and filtering."""
    
    # Create the original tutorial flow and get the first and last nodes
    tutorial_flow, fetch_repo, combine_tutorial = create_tutorial_flow()
    
    # Instantiate new UI nodes
    smart_search = SmartSearchRepo()
    filter_repos = FilterRepos()
    select_repo = SelectRepository()
    render_download = RenderAndDownload()
    
    # Connect the UI nodes
    smart_search >> filter_repos
    filter_repos >> select_repo
    
    # Connect the select_repo node to the FetchRepo node
    select_repo >> fetch_repo
    
    # Add the render and download node after CombineTutorial
    combine_tutorial >> render_download
    
    # Create the full UI flow
    ui_flow = Flow(start=smart_search)
    
    return ui_flow