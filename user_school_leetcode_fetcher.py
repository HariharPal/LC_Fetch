import requests
import csv
import concurrent.futures
import os
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ============================================================
# Create reusable session with retry and keep-alive
# ============================================================
def create_session():
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.headers.update({
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    })
    return session

# ============================================================
# Minimal GraphQL query (only username + school)
# ============================================================
QUERY = """
query getUserProfile($username: String!) {
    matchedUser(username: $username) {
        username
        profile {
            school
        }
    }
}
"""

# ============================================================
# Fetch data for a single user
# ============================================================
def fetch_user(session, user_slug):
    url = "https://leetcode.com/graphql"
    payload = {"query": QUERY, "variables": {"username": user_slug}}

    try:
        response = session.post(url, json=payload, timeout=8)
        response.raise_for_status()
        data = response.json().get("data", {}).get("matchedUser")

        if not data:
            print(f"⚠️ {user_slug} not found")
            return {"user_slug": user_slug, "username": "", "school": ""}

        return {
            "user_slug": user_slug,
            "username": data.get("username", ""),
            "school": data.get("profile", {}).get("school", "")
        }

    except Exception as e:
        print(f"❌ {user_slug} error: {e}")
        return {"user_slug": user_slug, "username": "", "school": ""}

# ============================================================
# Process all users from input CSV
# ============================================================
def process_csv(input_file):
    if not os.path.exists(input_file):
        print(f"❌ File '{input_file}' not found")
        return

    # Read user_slugs
    with open(input_file, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        user_slugs = [r.get("user_slug", "").strip() for r in reader if r.get("user_slug")]

    print(f"📊 Found {len(user_slugs)} users — fetching username & school...\n")

    session = create_session()
    results = []

    # Use threading for faster requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(fetch_user, session, slug): slug for slug in user_slugs}

        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            slug = futures[future]
            data = future.result()
            results.append(data)
            print(f"[{i}/{len(user_slugs)}] ✅ {slug}")


    # Write to output CSV
    if results:
        output_file = f"user_school_{os.path.splitext(os.path.basename(input_file))[0]}.csv"
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["user_slug", "username", "school"])
            writer.writeheader()
            writer.writerows(results)

        print(f"\n✅ Done! Saved to {output_file} ({len(results)} users)")
    else:
        print("❌ No data fetched")

# ============================================================
# Entry Point
# ============================================================
def main():
    print("=" * 60)
    print("⚡ LeetCode User School Fetcher (with user_slug)")
    print("=" * 60)
    file = input("Enter input CSV filename: ").strip()
    if file:
        process_csv(file)
    else:
        print("❌ Please enter a filename")

if __name__ == "__main__":
    main()
