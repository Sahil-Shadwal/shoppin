import sys
sys.path.append('/Users/sahilshadwal/Desktop/pinterest/vibe-search-backend')

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vibesearch.settings')

import django
django.setup()

from search.gemini_utils import parse_search_query

# Test cases
test_queries = [
    "not white Nike Air Force",
    "black shoes without leather",
    "red dress no floral",
    "sneakers not red or blue",
    "blue jeans"  # No negation
]

print("🧪 Testing Negation Parsing\n")
print("=" * 60)

for query in test_queries:
    print(f"\n📝 Query: '{query}'")
    result = parse_search_query(query)
    print(f"   ✅ Refined: {result.get('refined_query', 'N/A')}")
    print(f"   ❌ Negative: {result.get('negative_query', 'N/A')}")
    print(f"   📁 Category: {result.get('category', 'N/A')}")
    print(f"   🎨 Color: {result.get('color', 'N/A')}")

print("\n" + "=" * 60)
print("\n✨ Test Complete!")
