import requests
import csv
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ======================================
# Create reusable session with retry mechanism
# ======================================
def create_session():
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.headers.update({
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    })
    return session

# GraphQL query
QUERY = """
query getUserProfile($username: String!) {
    matchedUser(username: $username) {
        username
        profile {
            realName
            userAvatar
            birthday
            ranking
            reputation
            websites
            countryName
            company
            school
            skillTags
            aboutMe
            starRating
        }
        submitStats {
            acSubmissionNum { difficulty count }
            totalSubmissionNum { difficulty count }
        }
        badges { id displayName icon creationDate }
        activeBadge { displayName icon }
    }
}
"""

# ======================================
# Fetch user data
# ======================================
def fetch_user_data(session, user_slug):
    url = "https://leetcode.com/graphql"
    payload = {"query": QUERY, "variables": {"username": user_slug}}

    try:
        print(f"\n🔍 Fetching data for: {user_slug}")
        print(f"🌐 Profile URL: https://leetcode.com/u/{user_slug}")
        
        response = session.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json().get("data", {}).get("matchedUser")

        if not data:
            print(f"❌ User '{user_slug}' not found!")
            return None

        print(f"✅ Successfully fetched data for {user_slug}")
        return data

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

# ======================================
# Parse user data into flat dictionary
# ======================================
def parse_user_data(user):
    profile = user.get("profile", {})
    submit_stats = user.get("submitStats", {})

    parsed = {
        "username": user.get("username", ""),
        "real_name": profile.get("realName", ""),
        "country": profile.get("countryName", ""),
        "company": profile.get("company", ""),
        "school_college": profile.get("school", ""),
        "ranking": profile.get("ranking", ""),
        "reputation": profile.get("reputation", ""),
        "star_rating": profile.get("starRating", ""),
        "about_me": profile.get("aboutMe", ""),
        "birthday": profile.get("birthday", ""),
        "avatar": profile.get("userAvatar", ""),
        "websites": "; ".join(profile.get("websites", []) or []),
        "skill_tags": "; ".join(profile.get("skillTags", []) or []),
    }

    # Add solved counts
    for item in submit_stats.get("acSubmissionNum", []):
        difficulty = item["difficulty"].lower()
        parsed[f"{difficulty}_solved"] = item["count"]
    
    # Add total submission counts
    for item in submit_stats.get("totalSubmissionNum", []):
        difficulty = item["difficulty"].lower()
        parsed[f"{difficulty}_total_submissions"] = item["count"]

    # Add badge information
    badges = user.get("badges", [])
    parsed["total_badges"] = len(badges)
    parsed["badge_names"] = "; ".join(b.get("displayName", "") for b in badges[:10])
    
    active_badge = user.get("activeBadge")
    parsed["active_badge"] = active_badge.get("displayName", "") if active_badge else ""

    return parsed

# ======================================
# Display user data
# ======================================
def display_user_data(parsed_data):
    print("\n" + "="*70)
    print(f"📋 USER PROFILE: {parsed_data.get('username', 'N/A')}")
    print("="*70)
    
    print("\n👤 BASIC INFORMATION:")
    print(f"  Username: {parsed_data.get('username', 'N/A')}")
    print(f"  Real Name: {parsed_data.get('real_name', 'N/A')}")
    print(f"  Country: {parsed_data.get('country', 'N/A')}")
    print(f"  Company: {parsed_data.get('company', 'N/A')}")
    print(f"  School/College: {parsed_data.get('school_college', 'N/A')}")
    
    print("\n⭐ STATS:")
    print(f"  Ranking: {parsed_data.get('ranking', 'N/A')}")
    print(f"  Reputation: {parsed_data.get('reputation', 'N/A')}")
    print(f"  Star Rating: {parsed_data.get('star_rating', 'N/A')}")
    
    print("\n📊 PROBLEMS SOLVED:")
    print(f"  Easy: {parsed_data.get('easy_solved', 0)}")
    print(f"  Medium: {parsed_data.get('medium_solved', 0)}")
    print(f"  Hard: {parsed_data.get('hard_solved', 0)}")
    print(f"  Total: {parsed_data.get('all_solved', 0)}")
    
    print("\n🏆 BADGES:")
    print(f"  Total Badges: {parsed_data.get('total_badges', 0)}")
    print(f"  Active Badge: {parsed_data.get('active_badge', 'None')}")
    
    if parsed_data.get('about_me'):
        about = parsed_data.get('about_me', '')
        preview = about[:150] + "..." if len(about) > 150 else about
        print(f"\n💬 ABOUT:")
        print(f"  {preview}")
    
    print("\n" + "="*70)

# ======================================
# Save to CSV
# ======================================
def save_to_csv(parsed_data, filename=None):
    if not filename:
        username = parsed_data.get('username', 'user')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"leetcode_{username}_{timestamp}.csv"
    
    try:
        fieldnames = sorted(parsed_data.keys())
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(parsed_data)
        
        print(f"\n💾 Data saved to: {filename}")
        return filename
    
    except Exception as e:
        print(f"\n❌ Error saving to CSV: {e}")
        return None

# ======================================
# Main function
# ======================================
def main():
    print("="*70)
    print("⚡ LEETCODE USER DATA FETCHER")
    print("="*70)
    
    # Get user_slug from input
    user_slug = input("\n📝 Enter LeetCode user_slug: ").strip()
    
    if not user_slug:
        print("❌ User slug cannot be empty!")
        return
    
    # Create session
    session = create_session()
    
    # Fetch user data
    user_data = fetch_user_data(session, user_slug)
    
    if not user_data:
        return
    
    # Parse the data
    parsed_data = parse_user_data(user_data)
    
    # Display the data
    display_user_data(parsed_data)
    
    # Ask to save CSV
    save_choice = input("\n💾 Save to CSV? (y/n): ").strip().lower()
    
    if save_choice == 'y':
        custom_name = input("Enter filename (press Enter for auto-generated name): ").strip()
        
        if custom_name and not custom_name.endswith('.csv'):
            custom_name += '.csv'
        
        filename = save_to_csv(parsed_data, custom_name if custom_name else None)
        
        if filename:
            print(f"✅ Success! Check the file: {filename}")

# ======================================
# Entry Point
# ======================================
if __name__ == "__main__":
    main()