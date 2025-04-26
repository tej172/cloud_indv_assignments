from utils.call_llm import call_llm, LLMProvider_enum

def extract_keywords(query_input: str, llm_provider=None) -> list:
    """
    Extract search keywords from a natural language query using LLM.
    
    Args:
        query_input (str): Natural language query string
        llm_provider: LLM provider to use (default: None, which uses the default provider)
        
    Returns:
        list: List of extracted keywords for GitHub search
    """
    # prompt = f"""
    # Extract the most relevant search keywords from this natural language query to find GitHub repositories relevant to my natural text.
    # Return just a JSON array of strings, with no explanation.
    
    # Natural language query: "{query_input}"
    
    # Example output format:
    # ["keyword1", "keyword2", "keyword3"]
    # """
    
    #     prompt = f"""

    # You are a helpful and precise software research assistant specialized in codebase discovery and summarization. 
    # From the question below, list at most six concise keywords suitable for a GitHub repository search. 
    # Output in YAML list format only without any additional text.

    # Here are 3 guiding examples:

    # Question: 'Tool for real-time object detection in videos' → Keywords: [‘computer vision’, ‘object detection’, ‘real-time’, ‘deep learning’, ‘video analysis’]

    # Question: 'Simple backend server for user authentication' → Keywords: [‘backend’, ‘authentication’, ‘API’, ‘OAuth’, ‘JWT’]

    # Question: 'Lightweight Python library for financial time series forecasting' → Keywords: [‘Python’, ‘time series’, ‘forecasting’, ‘finance’, ‘machine learning’]

    # Task: Extract the most important technical or domain-relevant keywords to optimize GitHub search precision.

    # Rules:

    # Output only a pure YAML list.

    # Each keyword must be concise (1–3 words).

    # No repetition or synonyms.

    # No extra explanation outside the list.

    # Natural language query: "{query_input}"""

    prompt = f"""
    Rewrite my request from a natural language query into a simple 3-4 word query to find only relevant GitHub repositories to my natural text.
    Return just a JSON array of strings, with no explanation.
    
    Natural language query: "{query_input}"
    
    Example output format:
    ["keyword1", "keyword2", "keyword3"]
    """

    try:
        # Use the specified provider if available, otherwise use default
        response = call_llm(prompt, model=llm_provider if llm_provider else LLMProvider_enum.GOOGLE)
        # Simple parsing to extract array content
        if response.strip().startswith('[') and response.strip().endswith(']'):
            # Extract items between brackets and split by commas
            keywords_str = response.strip()[1:-1]
            # Split by commas and clean up each keyword
            keywords = [k.strip().strip('"\'') for k in keywords_str.split(',')]
            return keywords
        else:
            # Fallback: split the query into words, filter out common words
            simple_keywords = [word for word in query_input.split() 
                              if len(word) > 3 and word.lower() not in {
                                  'the', 'and', 'for', 'that', 'with', 'this', 'what', 'how'
                              }]
            return simple_keywords
    except Exception as e:
        print(f"Error extracting keywords: {e}")
        # Fallback to simple keyword extraction on failure
        return query_input.split()

def looks_like_url(text: str) -> bool:
    """
    Check if input text looks like a URL.
    
    Args:
        text (str): Input text to check
        
    Returns:
        bool: True if text appears to be a URL
    """
    return text.startswith(('http://', 'https://')) and 'github.com' in text.lower() 