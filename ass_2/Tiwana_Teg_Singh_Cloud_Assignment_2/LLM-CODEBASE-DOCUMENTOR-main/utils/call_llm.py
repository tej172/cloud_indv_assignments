from google import genai
from anthropic import Anthropic
from openai import OpenAI
from dotenv import load_dotenv
import os
import logging
import json
from datetime import datetime
from enum import Enum

# Load environment variables from .env file
load_dotenv()  # Loads from .env file

class LLMProvider_enum(str, Enum):
    ANTHROPIC = 'anthropic-claude'
    GOOGLE = 'google-gemini'
    OPENAI = 'openai-gpt'

# Configure logging
log_directory = os.getenv("LOG_DIR", "logs")
os.makedirs(log_directory, exist_ok=True)
log_file = os.path.join(log_directory, f"llm_calls_{datetime.now().strftime('%Y%m%d')}.log")

# Set up logger
logger = logging.getLogger("llm_logger")
logger.setLevel(logging.INFO)
logger.propagate = False  # Prevent propagation to root logger
file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Simple cache configuration
cache_file = "llm_cache.json"

# By default, we Google Gemini 2.5 pro gievn recent high bench marks
def call_llm(prompt: str, use_cache: bool = True, model: str=LLMProvider_enum.GOOGLE) -> str:
    print(f"Calling LLM with model: {model}")
    
    # Log the prompt
    logger.info(f"PROMPT: {prompt}")
    
    # Check cache if enabled
    if use_cache:
        # Load cache from disk
        cache = {}
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cache = json.load(f)
                logger.warning(f"Loaded and Using cache")
            except:
                logger.warning(f"Failed to load cache, starting with empty cache")
        
        # Return from cache if exists
        if prompt in cache:
            logger.info(f"RESPONSE: {cache[prompt]}")
            return cache[prompt]
        

    # If not in cache, call the LLM
    # Call the LLM if not in cache or cache disabled
    if(model==LLMProvider_enum.GOOGLE):
        # Use Google Gemini
        
        # client = genai.Client(
        #     vertexai=True, 
        #     # TODO: change to your own project id and location
        #     project=os.getenv("GEMINI_PROJECT_ID", "llm-code-explainer"),
        #     location=os.getenv("GEMINI_LOCATION", "us-central1")
        # )
        # 
        client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY"),
        )
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-pro-exp-03-25")
        response = client.models.generate_content(
            model=model,
            contents=[prompt]
        )
        response_text = response.text
    elif(model==LLMProvider_enum.ANTHROPIC):
        # Use Anthropic Claude
        client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        response = client.messages.create(
            # Use Anthropic Claude 3.7 Sonnet Extended Thinking
            model=os.environ.get("ANTHROPIC_MODEL", "claude-3-7-sonnet-20250219"), 
            max_tokens=15000, #If have extra api budget, can increase this to 21000
            thinking={
                "type": "enabled", 
                "budget_tokens": 10000 # If have extra api budget, can increase this to 20000
            },
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        response_text = response.content[1].text
    else: # Assume OpenAI
        # Use the default LLM, which is OpenAI (Use OpenAI o1/4o/gpt-4o-mini) depedning on the model & api budget
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "o4-mini"),
            messages=[{"role": "user", "content": prompt}],
            response_format={
                "type": "text"
            },
            reasoning_effort="medium",
            store=False
        )
        response_text = response.choices[0].message.content

    # Log the response
    logger.info(f"RESPONSE: {response_text}")
    
    # Update cache if enabled
    if use_cache:
        # Load cache again to avoid overwrites
        cache = {}
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cache = json.load(f)
            except:
                pass
        
        # Add to cache and save
        cache[prompt] = response_text
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache, f)
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    return response_text

if __name__ == "__main__":
    test_prompt = "Hello, how are you? What is the exact model are you using?"
    test_prompt2 = "Hello, how bug is your model that are you using?"
    
    # First call - should hit the API and return vals
    print("Making call 1...")
    # LLMProvider_enum('anthropic-claude'),  LLMProvider_enum('google-gemini') & 'openai-gpt': LLMProvider_enum('openai-gpt') /or/
    # LLMProvider_enum.ANTHROPIC , LLMProvider_enum.GOOGLE & openai: LLMProvider_enum.OPENAI
    response1 = call_llm(test_prompt, use_cache=False, model=LLMProvider_enum('openai-gpt'))
    print(f"Response: {response1}\n======================")

    # Second call - should hit the cache and return vals
    print("Making call 2...")
    response1 = call_llm(test_prompt, use_cache=True, model=LLMProvider_enum.GOOGLE)
    print(f"Response: {response1}")
    
