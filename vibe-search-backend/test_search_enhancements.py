import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_search_enhancements():
    print("Testing Search Enhancements...")
    
    # 1. Test Text Search with Max Price
    print("\n1. Testing Text Search with Max Price...")
    payload = {
        "query": "shoes",
        "max_price": 100,
        "top_k": 5
    }
    try:
        response = requests.post(f"{BASE_URL}/search/text/", json=payload)
        if response.status_code == 200:
            data = response.json()
            matches = data.get('matches', [])
            print(f"Found {len(matches)} matches.")
            for m in matches:
                price = m.get('price')
                print(f"- {m['title']} (${price})")
                if price and float(price) > 100:
                    print("  FAIL: Price > 100")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

    # 2. Test Text Search with Negative Query
    print("\n2. Testing Text Search with Negative Query (shoes NOT red)...")
    payload = {
        "query": "shoes",
        "negative_query": "red",
        "top_k": 5
    }
    try:
        response = requests.post(f"{BASE_URL}/search/text/", json=payload)
        if response.status_code == 200:
            data = response.json()
            matches = data.get('matches', [])
            print(f"Found {len(matches)} matches.")
            for m in matches:
                print(f"- {m['title']}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_search_enhancements()
