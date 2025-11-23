import requests
import json
import os

# TODO: Move to environment variable in production
GEMINI_API_KEY = "AIzaSyAHVl69xyTacdv1lNWTKj761n7_1iMXtWY"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

def parse_search_query(query_text):
    """
    Uses Gemini to parse a natural language search query into structured filters.
    Returns a dictionary with:
    - refined_query: The core visual search term
    - negative_query: Terms to exclude
    - category: Inferred category
    - color: Inferred color
    - max_price: Inferred budget
    """
    if not query_text:
        return {}

    prompt = f"""
    You are an intelligent fashion search assistant. Parse the following user query into structured search filters.
    
    User Query: "{query_text}"
    
    Extract the following fields in JSON format:
    - refined_query: The main visual description of the item (e.g., "white sneakers", "floral dress"). Remove negative terms.
    - negative_query: Any terms the user explicitly wants to exclude (e.g., "leather", "red").
    - category: One of ['tops', 'bottoms', 'footwear', 'outerwear', 'bags', 'accessories']. Infer from the item type.
    - color: The primary color if mentioned.
    - max_price: If a price limit is mentioned (e.g., "under $500"), extract the number.
    
    Return ONLY the JSON object.
    """
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        response = requests.post(GEMINI_URL, json=payload, headers={'Content-Type': 'application/json'})
        response.raise_for_status()
        
        data = response.json()
        text_response = data['candidates'][0]['content']['parts'][0]['text']
        
        # Clean up code blocks if present
        if "```json" in text_response:
            text_response = text_response.split("```json")[1].split("```")[0]
        elif "```" in text_response:
            text_response = text_response.split("```")[1].split("```")[0]
            
        parsed_data = json.loads(text_response.strip())
        print(f"Gemini Parsed: {parsed_data}")
        return parsed_data
        
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        # Fallback: just use the raw text as the refined query
        return {"refined_query": query_text}
