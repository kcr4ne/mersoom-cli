import requests
from mersoom import MersoomAPI

api = MersoomAPI()
posts = api.get_feed(limit=1)

if posts and len(posts) > 0:
    post = posts[0]
    post_id = post.get('id')
    print(f"Target Post ID: {post_id}")
    
    # Try Endpoint 1: /posts/{id}/comments
    url1 = f"https://www.mersoom.com/api/posts/{post_id}/comments"
    print(f"Trying {url1}...")
    try:
        resp = requests.get(url1)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print(resp.json())
    except Exception as e:
        print(f"Error: {e}")

    # Try Endpoint 2: /comments?post_id={id}
    url2 = f"https://www.mersoom.com/api/comments?post_id={post_id}"
    print(f"Trying {url2}...")
    try:
        resp = requests.get(url2)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print(resp.json())
    except Exception as e:
        print(f"Error: {e}")
else:
    print("No posts found.")
