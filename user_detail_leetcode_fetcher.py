import requests
import csv
import time
import os
from datetime import datetime

def fetch_leetcode_user_data(user_slug):
    """
    Fetch LeetCode user profile data using GraphQL API
    """
    url = "https://leetcode.com/graphql"
    
    # GraphQL query to fetch user data
    query = """
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
                acSubmissionNum {
                    difficulty
                    count
                }
                totalSubmissionNum {
                    difficulty
                    count
                }
            }
            badges {
                id
                displayName
                icon
                creationDate
            }
            activeBadge {
                displayName
                icon
            }
        }
    }
    """
    
    variables = {"username": user_slug}
    
    headers = {
        "Content-Type": "application/json",
        "Referer": f"https://leetcode.com/{user_slug}/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.post(
            url,
            json={"query": query, "variables": variables},
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get("data", {}).get("matchedUser") is None:
            print(f"  ⚠️  User '{user_slug}' not found!")
            return None
            
        return data["data"]["matchedUser"]
    
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Error fetching data for '{user_slug}': {e}")
        return None

def parse_user_data(user_data):
    """
    Parse user data into a flat dictionary for CSV
    """
    if not user_data:
        return {}
    
    profile = user_data.get("profile", {})
    submit_stats = user_data.get("submitStats", {})
    
    parsed = {
        "username": user_data.get("username", ""),
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
        "websites": "; ".join(profile.get("websites", [])) if profile.get("websites") else "",
        "skill_tags": "; ".join(profile.get("skillTags", [])) if profile.get("skillTags") else "",
    }
    
    # Add submission stats
    if submit_stats.get('acSubmissionNum'):
        for item in submit_stats['acSubmissionNum']:
            difficulty = item.get('difficulty', 'Unknown')
            count = item.get('count', 0)
            parsed[f"{difficulty.lower()}_solved"] = count
    
    if submit_stats.get('totalSubmissionNum'):
        for item in submit_stats['totalSubmissionNum']:
            difficulty = item.get('difficulty', 'Unknown')
            count = item.get('count', 0)
            parsed[f"{difficulty.lower()}_total_submissions"] = count
    
    # Add badges info
    badges = user_data.get("badges", [])
    parsed["total_badges"] = len(badges)
    parsed["badge_names"] = "; ".join([b.get("displayName", "") for b in badges[:10]])  # First 10 badges
    
    active_badge = user_data.get("activeBadge")
    if active_badge:
        parsed["active_badge"] = active_badge.get("displayName", "")
    else:
        parsed["active_badge"] = ""
    
    return parsed

def process_csv_file(input_filename):
    """
    Process input CSV file and fetch user data for all user_slugs
    """
    # Extract base filename without extension
    base_name = os.path.splitext(os.path.basename(input_filename))[0]
    output_filename = f"user_info_{base_name}.csv"
    
    try:
        # Read input CSV
        with open(input_filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        print(f"\n📊 Found {len(rows)} users in the CSV file")
        print(f"🎯 Will fetch data and save to: {output_filename}")
        print("="*70)
        
        # Collect all user data
        all_user_data = []
        
        for idx, row in enumerate(rows, 1):
            user_slug = row.get('user_slug', '').strip()
            
            if not user_slug:
                print(f"\n[{idx}/{len(rows)}] ⚠️  Empty user_slug, skipping...")
                continue
            
            print(f"\n[{idx}/{len(rows)}] 🔍 Fetching data for: {user_slug}")
            
            # Fetch user data
            user_data = fetch_leetcode_user_data(user_slug)
            
            if user_data:
                parsed_data = parse_user_data(user_data)
                # Merge original row data with fetched user data
                combined_data = {**row, **parsed_data}
                all_user_data.append(combined_data)
                print(f"  ✅ Successfully fetched data")
            else:
                # Still add the row with empty user info fields
                all_user_data.append(row)
                print(f"  ⚠️  Added row with missing user info")
            

        
        # Write to output CSV
        if all_user_data:
            # Get all unique fieldnames from all rows
            all_fieldnames = set()
            for data in all_user_data:
                all_fieldnames.update(data.keys())
            
            fieldnames = sorted(list(all_fieldnames))
            
            with open(output_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_user_data)
            
            print("\n" + "="*70)
            print(f"✅ SUCCESS! Data saved to: {output_filename}")
            print(f"📊 Total users processed: {len(all_user_data)}")
            print("="*70)
        else:
            print("\n❌ No data to save!")
            
    except FileNotFoundError:
        print(f"\n❌ Error: File '{input_filename}' not found!")
    except Exception as e:
        print(f"\n❌ Error processing file: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("="*70)
    print("LEETCODE BULK USER DATA FETCHER")
    print("="*70)
    
    # Get CSV filename from user
    csv_filename = input("\n📁 Enter the CSV filename (with .csv extension): ").strip()
    
    if not csv_filename:
        print("❌ Error: Filename cannot be empty!")
        return
    
    if not os.path.exists(csv_filename):
        print(f"❌ Error: File '{csv_filename}' does not exist!")
        return
    
    print(f"\n🚀 Starting to process: {csv_filename}")
    
    # Process the CSV file
    process_csv_file(csv_filename)

if __name__ == "__main__":
    main()