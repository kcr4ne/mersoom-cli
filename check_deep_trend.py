import time
from mersoom import MersoomAPI

def check_feed_and_latency():
    api = MersoomAPI()
    
    print("Fetching Feed (20)...")
    start = time.time()
    posts = api.get_feed(limit=20)
    print(f"Feed Fetch: {time.time() - start:.2f}s")
    
    if not posts:
        print("No posts.")
        return

    # Check structure
    print(f"Sample Post Keys: {posts[0].keys()}")
    if 'comments' in posts[0]:
        print(f"Comments in feed: Yes (Count: {len(posts[0]['comments'])})")
    else:
        print("Comments in feed: No")

    # Measure Comment Fetch Latency
    print("\nFetching comments for 5 posts...")
    start = time.time()
    for i, post in enumerate(posts[:5]):
        _ = api.get_comments(post['id'])
        print(f".", end="", flush=True)
    duration = time.time() - start
    print(f"\nTime for 5 posts: {duration:.2f}s (Avg: {duration/5:.2f}s/req)")
    print(f"Estimated for 20 posts: {duration * 4:.2f}s")

if __name__ == "__main__":
    check_feed_and_latency()
