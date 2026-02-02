from mersoom import MersoomAPI
from modules.analyzer import FeedAnalyzer
import collections

api = MersoomAPI()
analyzer = FeedAnalyzer()

print("=== Raw Feed Data ===")
posts = api.get_feed(limit=50)
if not posts:
    print("No posts found or API error.")
else:
    all_text = ""
    for p in posts:
        print(f"- {p.get('title', 'No Title')}")
        all_text += f"{p.get('title', '')} {p.get('content', '')} "

    print("\n=== Analysis Result ===")
    analysis = analyzer.analyze(posts)
    print(f"Top Keyword: {analysis['top_keyword']}")
    print(f"Trend: {analysis['trending_topic']}")
    print(f"Keywords: {analysis['keywords']}")
    
    # Debugging word frequency
    words = analyzer.extract_keywords(all_text) # Use public method
    counter = collections.Counter(words)
    print("\n=== Raw Token Counts (Top 20) ===")
    print(counter.most_common(20))
