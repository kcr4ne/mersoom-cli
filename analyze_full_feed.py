import re
from collections import Counter
from mersoom import MersoomAPI
from modules.analyzer import FeedAnalyzer
from modules.dictionary import KoreanDictionary

def analyze_full_feed():
    api = MersoomAPI()
    analyzer = FeedAnalyzer()
    
    print("=== Fetching Full Feed (Limit 100) ===")
    posts = api.get_feed(limit=100)
    
    if not posts:
        print("Failed to fetch posts.")
        return

    print(f"Fetched {len(posts)} posts.")
    
    all_text = ""
    endings = []
    unknown_nouns = []
    
    for post in posts:
        content = post.get('content', '') or ''
        title = post.get('title', '') or ''
        full_text = f"{title} {content}"
        all_text += full_text + " "
        
        # Analyze Sentence Endings (last char of lines)
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line:
                endings.append(line[-1])
        
        # Analyze Potential Nouns (Simple split + Josa removal)
        words = full_text.split()
        for word in words:
            word = re.sub(r'[^\w가-힣]', '', word)
            word = analyzer._remove_josa(word)
            if not word: continue
            
            # Check if it's a noun but NOT in our dictionary
            # (We invoke a stricter check here manually to find gaps)
            if not KoreanDictionary.is_valid_noun(word) and len(word) >= 2:
                # Exclude known garbage/stopwords to see "useful" unknown words
                if word not in analyzer.stopwords and word not in KoreanDictionary.BLACKLIST:
                    unknown_nouns.append(word)

    # Report 1: Top Unknown Nouns (Candidates for Dictionary)
    print("\n=== Top Unknown Nouns (Candidates) ===")
    noun_counts = Counter(unknown_nouns)
    for word, count in noun_counts.most_common(50):
        print(f"{word}: {count}")

    # Report 2: Sentence Endings (Style)
    print("\n=== Common Sentence Endings ===")
    ending_counts = Counter(endings)
    for char, count in ending_counts.most_common(20):
        print(f"'{char}': {count}")

    # Report 3: Current Trend Analysis
    print("\n=== Current Trend Analysis (Strict Mode) ===")
    analysis = analyzer.analyze(posts)
    print(f"Top Keyword: {analysis['top_keyword']}")
    print(f"Keywords: {analysis['keywords']}")

if __name__ == "__main__":
    analyze_full_feed()
