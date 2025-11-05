from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import json

class LeetCodeContestScraper:
    def __init__(self, contest_name: str, headless: bool = False):
        self.contest_name = contest_name
        self.base_url = f"https://leetcode.com/contest/api/ranking/{contest_name}/"
        
        # Setup Chrome options
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def login_manual(self):
        """Open LeetCode for manual login"""
        print("\n" + "="*70)
        print("🔐 MANUAL LOGIN REQUIRED")
        print("="*70)
        print("\n1. A browser window will open")
        print("2. Please log in to your LeetCode account")
        print("3. After logging in, press Enter here to continue\n")
        
        self.driver.get("https://leetcode.com/accounts/login/")
        input("Press Enter after you've logged in... ")
        print("✅ Login confirmed!\n")
    
    def fetch_page_data(self, page: int, region: str = "global_v2") -> dict:
        """Fetch page data using browser"""
        url = f"{self.base_url}?pagination={page}&region={region}"
        
        try:
            self.driver.get(url)
            
            # Get the page source (it's JSON)
            body = self.driver.find_element(By.TAG_NAME, "body").text
            data = json.loads(body)
            return data
            
        except json.JSONDecodeError:
            print(f"⚠️  Page {page}: Not valid JSON")
            return None
        except Exception as e:
            print(f"❌ Page {page}: {e}")
            return None
    
    def parse_ranking_data(self, data: dict) -> list:
        """Parse ranking data into list of dictionaries"""
        if not data or 'total_rank' not in data:
            return []
        
        rankings = []
        for user in data['total_rank']:
            user_data = {
                'rank': user.get('rank'),
                'username': user.get('username'),
                'user_slug': user.get('user_slug'),
                'country_code': user.get('country_code'),
                'country_name': user.get('country_name'),
                'score': user.get('score'),
                'finish_time': user.get('finish_time'),
                'data_region': user.get('data_region'),
                'contest_id': user.get('contest_id')
            }
            
            # Add submission details
            submissions = user.get('submissions', {})
            for problem_id, sub_info in submissions.items():
                user_data[f'problem_{problem_id}_date'] = sub_info.get('date')
                user_data[f'problem_{problem_id}_fail_count'] = sub_info.get('fail_count')
                user_data[f'problem_{problem_id}_lang'] = sub_info.get('lang')
                user_data[f'problem_{problem_id}_submission_id'] = sub_info.get('submission_id')
            
            rankings.append(user_data)
        
        return rankings
    
    def scrape_pages(self, min_page: int, max_page: int, region: str = "global_v2", delay: float = 0.05) -> pd.DataFrame:
        """Scrape multiple pages"""
        all_rankings = []
        
        print(f"\n{'='*70}")
        print(f"🚀 Scraping pages {min_page} to {max_page} for '{self.contest_name}'")
        print(f"{'='*70}\n")
        
        for page in range(min_page, max_page + 1):
            print(f"📄 Page {page:3d}...", end=" ", flush=True)
            
            data = self.fetch_page_data(page, region)
            
            if data:
                rankings = self.parse_ranking_data(data)
                if rankings:
                    all_rankings.extend(rankings)
                    print(f"✅ {len(rankings)} users")
                else:
                    print(f"⚠️  No users")
            else:
                print("❌ Failed")
            
            # Delay between requests
            if page < max_page:
                time.sleep(delay)
        
        if not all_rankings:
            print("\n❌ No data collected!")
            return pd.DataFrame()
        
        df = pd.DataFrame(all_rankings)
        print(f"\n{'='*70}")
        print(f"✅ Collected {len(df)} total users")
        print(f"{'='*70}\n")
        return df
    
    def save_to_csv(self, df: pd.DataFrame, min_page: int, max_page: int):
        """Save to CSV"""
        filename = f"leetcode_{self.contest_name}_page_{min_page}_to_{max_page}.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"💾 Saved to: {filename}\n")
        return filename
    
    def close(self):
        """Close browser"""
        self.driver.quit()


def main():
    print("\n" + "="*70)
    print("  LEETCODE CONTEST SCRAPER (Selenium)")
    print("="*70)
    
    contest_name = input("\n📌 Contest name (e.g., 'biweekly-contest-167'): ").strip()
    if not contest_name:
        print("❌ Contest name required!")
        return
    
    min_page = int(input("📌 Start page: "))
    max_page = int(input("📌 End page: "))
    region = input("📌 Region (default 'global_v2'): ").strip() or "global_v2"
    
    headless = input("📌 Run in headless mode? (y/n, default n): ").strip().lower() == 'y'
    
    scraper = None
    try:
        scraper = LeetCodeContestScraper(contest_name, headless=headless)
        
        # Manual login
        scraper.login_manual()
        
        # Scrape data
        df = scraper.scrape_pages(min_page, max_page, region, delay=0)
        
        if not df.empty:
            scraper.save_to_csv(df, min_page, max_page)
            
            print("="*70)
            print("📊 PREVIEW:")
            print("="*70)
            print(df.head())
            print(f"\n📈 Total rows: {len(df)}")
            print(f"📋 Total columns: {len(df.columns)}")
            print("\n✅ Scraping complete!")
        else:
            print("❌ No data collected")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    finally:
        if scraper:
            scraper.close()


if __name__ == "__main__":
    main()