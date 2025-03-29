import requests
import random

# URL from the curl request
url = "https://www.kroger.com/search?query=milk&searchType=default_search"

# Chrome-like headers
def generate_chrome_headers():
    # Recent Chrome User-Agent (Windows 10/11, update as needed)
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    ]
    
    # Randomly pick a User-Agent
    user_agent = random.choice(user_agents)
    
    # Common Accept-Language variations
    languages = [
        "en-US,en;q=0.9",
        "en-GB,en;q=0.9",
        "en-US,en;q=0.8,fr;q=0.7"
    ]
    
    headers = {
        "Host": "www.kroger.com",  # Extract from URL in a real scenario
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": random.choice(languages),
        "Accept-Encoding": "gzip, deflate, br",  # Chrome supports Brotli (br)
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",  # Indicates willingness to upgrade to HTTPj
        "Sec-Fetch-Site": "none",  # First request, no referrer yet
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document"
    }
    
    return headers

# Make the request



# Print the response

# Make the GET request
try:
    headers = generate_chrome_headers();
    response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)

    # Check if the request was successful
    response.raise_for_status()

    print("Status Code:", response.status_code)
    print("Response Headers:", response.headers)
    print("Content Snippet:", response.text[:200])  # First 200 chars
    # Save response to file
    with open("kroger_response.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print(f"Response saved to 'kroger_response.html' (Status Code: {response.status_code})")

except requests.exceptions.Timeout:
    print("Request timed out after 10 seconds")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")

