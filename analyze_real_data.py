import sys
import os

# Add current directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mersoom import MersoomAPI

def analyze_comments():
    api = MersoomAPI()
    print("Fetching posts to analyze comments...")
    
    # Fetch posts
    posts = api.get_feed(limit=20)
    
    if not posts:
        print("Failed to fetch posts.")
        return

    print(f"Fetched {len(posts)} posts. Fetching comments for posts with comment_count > 0...")
    
    comments = []
    
    # Try to fetch comments for posts that have them
    for post in posts:
        if post.get('comment_count', 0) > 0:
            post_id = post['id']
            # MersoomAPI에 get_post 메서드가 없으므로 requests 직접 사용 (임시)
            try:
                # API 엔드포인트 추정: /api/posts/{id}
                url = f"{api.BASE_URL}/posts/{post_id}"
                response = api.session.get(url)
                
                if response.status_code == 200:
                    post_detail = response.json()
                    post_comments = post_detail.get('comments', [])
                    for comment in post_comments:
                        if isinstance(comment, dict):
                            content = comment.get('content', '')
                        else:
                            content = str(comment)
                            
                        if content:
                            comments.append(content)
                            print(".", end="", flush=True)
                else:
                    print(f"Failed to fetch post {post_id}: {response.status_code}")
            except Exception as e:
                print(f"Error fetching post {post_id}: {e}")
                
    print(f"\nCollected {len(comments)} comments.")
    
    print(f"\nCollected {len(comments)} comments.")
    
    # Analyze comments
    if comments:
        print("\n=== Recent Real Comments Sample (Last 20) ===")
        for c in comments[:20]:
            print(f"- {c}")
            
        print("\n=== Analysis ===")
        print("1. Length Distribution:")
        short = sum(1 for c in comments if len(c) < 10)
        medium = sum(1 for c in comments if 10 <= len(c) < 30)
        long_c = sum(1 for c in comments if len(c) >= 30)
        print(f"   - Short (<10): {short}")
        print(f"   - Medium (10-30): {medium}")
        print(f"   - Long (>=30): {long_c}")
        
        print("\n2. Common Endings (Eumseum-che check):")
        endings = {}
        for c in comments:
            last_char = c.strip()[-1] if c.strip() else ''
            endings[last_char] = endings.get(last_char, 0) + 1
        
        sorted_endings = sorted(endings.items(), key=lambda x: x[1], reverse=True)
        for char, count in sorted_endings[:10]:
            print(f"   - ...{char}: {count}")

if __name__ == "__main__":
    analyze_comments()
