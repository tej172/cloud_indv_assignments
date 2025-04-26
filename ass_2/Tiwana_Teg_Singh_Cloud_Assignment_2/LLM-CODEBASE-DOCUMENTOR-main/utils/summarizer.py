from utils.call_llm import call_llm, LLMProvider_enum
import re

def summarize_readme(readme_text: str, max_length: int = 500, llm_provider=None) -> str:
    """
    Generate a concise summary of a repository README using LLM.
    
    Args:
        readme_text (str): README content as text
        max_length (int): Maximum length of the summary in characters
        llm_provider: LLM provider to use (default: None, which uses the default provider)
        
    Returns:
        str: Concise summary of the README
    """
    # Limit input length to prevent context overflow
    truncated_text = truncate_text(readme_text, 6000)  # Limit to ~6k chars
    
    prompt = f"""
    Provide a clear, concise summary of the following repository README.
    Focus on what the repository does, key features, and its purpose.
    Keep your response to about 2-3 sentences, under 100 words.
    
    README CONTENT:
    {truncated_text}
    
    YOUR SUMMARY:
    """
    
    try:
        # Use the specified provider if available, otherwise use default
        summary = call_llm(prompt, model=llm_provider if llm_provider else LLMProvider_enum.GOOGLE)
        # Ensure the summary doesn't exceed max_length
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
        return summary
    except Exception as e:
        print(f"Error summarizing README: {e}")
        # Fallback to manual extraction
        return extract_first_paragraph(truncated_text, max_length)

def truncate_text(text: str, max_chars: int) -> str:
    """
    Truncate text to maximum character limit while preserving complete sentences.
    
    Args:
        text (str): Text to truncate
        max_chars (int): Maximum number of characters
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_chars:
        return text
    
    # Find the last sentence boundary before max_chars
    truncated = text[:max_chars]
    last_period = truncated.rfind('.')
    last_question = truncated.rfind('?')
    last_exclamation = truncated.rfind('!')
    
    # Find the last sentence boundary
    last_sentence_end = max(last_period, last_question, last_exclamation)
    
    if last_sentence_end > 0:
        return text[:last_sentence_end + 1] + "..."
    else:
        # If no sentence boundary found, just truncate
        return truncated + "..."

def extract_first_paragraph(text: str, max_length: int = 500) -> str:
    """
    Extract the first paragraph from a text as a fallback summary method.
    
    Args:
        text (str): Text to extract from
        max_length (int): Maximum length of the extracted paragraph
        
    Returns:
        str: Extracted paragraph
    """
    # Remove Markdown formatting
    cleaned_text = re.sub(r'#+ ', '', text)
    cleaned_text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', cleaned_text)  # Replace links with text
    cleaned_text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', cleaned_text)  # Remove images
    
    # Split by double newlines (paragraph breaks)
    paragraphs = re.split(r'\n\s*\n', cleaned_text)
    
    # Find first non-empty paragraph
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if paragraph and len(paragraph) > 30:  # Ensure it's substantial
            if len(paragraph) > max_length:
                return paragraph[:max_length-3] + "..."
            return paragraph
    
    # Fallback to first 100 characters
    return cleaned_text[:min(max_length, len(cleaned_text))] 