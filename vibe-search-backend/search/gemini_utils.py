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
    - refined_query: The main visual description of the item WITHOUT any negation words. Extract only the positive attributes.
    - negative_query: Terms the user wants to EXCLUDE. Look for patterns like "not X", "no X", "without X", "except X".
    - category: One of ['tops', 'bottoms', 'footwear', 'outerwear', 'bags', 'accessories']. Infer from the item type.
    - color: The primary color if mentioned (only if it's a POSITIVE attribute, not excluded).
    - max_price: If a price limit is mentioned (e.g., "under $500"), extract the number.
    
    IMPORTANT EXAMPLES:
    - "not white Nike Air Force" → refined_query: "Nike Air Force", negative_query: "white", category: "footwear"
    - "black shoes without leather" → refined_query: "black shoes", negative_query: "leather", category: "footwear"
    - "red dress no floral" → refined_query: "red dress", negative_query: "floral", category: "tops"
    - "sneakers not red or blue" → refined_query: "sneakers", negative_query: "red blue", category: "footwear"
    
    Return ONLY the JSON object without any markdown formatting.
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
        # Fallback: Use regex to extract negations
        import re
        
        negative_terms = []
        cleaned_query = query_text
        
        # Pattern: "not X" or "no X" or "without X" or "except X" (single word only)
        pattern = r'\b(not|no|without|except)\s+(\w+)\b'
        matches = list(re.finditer(pattern, cleaned_query, re.IGNORECASE))
        
        for match in matches:
            # Extract the negated term (group 2)
            neg_term = match.group(2)
            negative_terms.append(neg_term)
            # Remove the entire negation phrase from the query
            cleaned_query = cleaned_query.replace(match.group(0), '', 1).strip()
        
        # Clean up extra spaces
        cleaned_query = re.sub(r'\s+', ' ', cleaned_query).strip()
        
        result = {
            "refined_query": cleaned_query if cleaned_query else query_text,
            "negative_query": ' '.join(negative_terms) if negative_terms else None
        }
        
        print(f"Fallback Parsed: refined='{result['refined_query']}', negative='{result.get('negative_query')}'")
        return result
