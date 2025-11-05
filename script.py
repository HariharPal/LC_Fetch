import json
import csv
import os

class LeetCodeSearch:
    def __init__(self):
        self.usernames = []
    
    def load_json(self, filename):
        """Load data from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.usernames = json.load(f)
            print(f"Loaded {len(self.usernames)} usernames from {filename}")
            return True
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return False
    
    def load_csv(self, filename):
        """Load data from CSV file"""
        try:
            self.usernames = []
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.usernames.append(row)
            print(f"Loaded {len(self.usernames)} usernames from {filename}")
            return True
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return False
    
    def search(self, query):
        """Search for usernames containing the query"""
        query = query.lower()
        matches = []
        
        for user in self.usernames:
            if query in user['username'].lower():
                matches.append(user)
        
        return matches
    
    def search_starts_with(self, query):
        """Search for usernames starting with query"""
        query = query.lower()
        matches = []
        
        for user in self.usernames:
            if user['username'].lower().startswith(query):
                matches.append(user)
        
        return matches
    
    def search_by_rank(self, min_rank, max_rank):
        """Search by rank range"""
        matches = []
        
        for user in self.usernames:
            try:
                rank = int(user.get('rank', 0))
                if min_rank <= rank <= max_rank:
                    matches.append(user)
            except:
                continue
        
        # Sort by rank
        matches.sort(key=lambda x: int(x.get('rank', 0)))
        return matches
    
    def display_results(self, matches, title="Search Results"):
        """Display search results"""
        print(f"\n{title}")
        print("=" * 60)
        
        if not matches:
            print("No matches found.")
            return
        
        print(f"Found {len(matches)} matches:")
        print(f"{'Rank':<8} {'Username':<30} {'Page':<8}")
        print("-" * 60)
        
        for user in matches[:20]:  # Show first 20
            rank = user.get('rank', 'N/A')
            username = user.get('username', '')[:29]
            page = user.get('page', 'N/A')
            print(f"{rank:<8} {username:<30} {page:<8}")
        
        if len(matches) > 20:
            print(f"\n... and {len(matches) - 20} more results")
    
    def export_results(self, matches, filename):
        """Export search results to file"""
        try:
            if filename.endswith('.json'):
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(matches, f, indent=2, ensure_ascii=False)
            elif filename.endswith('.csv'):
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    if matches:
                        writer = csv.DictWriter(f, fieldnames=matches[0].keys())
                        writer.writeheader()
                        writer.writerows(matches)
            else:
                # Text file
                with open(filename, 'w', encoding='utf-8') as f:
                    for user in matches:
                        f.write(f"{user.get('rank', 'N/A')}\t{user.get('username', '')}\t{user.get('page', 'N/A')}\n")
            
            print(f"Exported {len(matches)} results to {filename}")
        except Exception as e:
            print(f"Error exporting: {e}")

def main():
    searcher = LeetCodeSearch()
    
    # Try to find and load data file
    data_files = [f for f in os.listdir('.') if f.endswith(('.json', '.csv')) and 'leetcode' in f.lower()]
    
    if data_files:
        print("Found these data files:")
        for i, filename in enumerate(data_files):
            print(f"{i+1}. {filename}")
        
        try:
            choice = int(input(f"Choose file (1-{len(data_files)}): ")) - 1
            filename = data_files[choice]
        except:
            filename = data_files[0]  # Use first file as default
    else:
        filename = input("Enter your data filename (JSON or CSV): ")
    
    # Load the data
    if filename.endswith('.json'):
        success = searcher.load_json(filename)
    elif filename.endswith('.csv'):
        success = searcher.load_csv(filename)
    else:
        print("Unsupported file format!")
        return
    
    if not success:
        return
    
    # Interactive search
    while True:
        print("\n" + "="*50)
        print(f"LEETCODE USERNAME SEARCH ({len(searcher.usernames)} users loaded)")
        print("="*50)
        print("1. Search username (contains)")
        print("2. Search username (starts with)")
        print("3. Search by rank range")
        print("4. Show top 50 users")
        print("5. Show random 20 users")
        print("6. Export all data")
        print("7. Quit")
        
        choice = input("\nChoose option (1-7): ").strip()
        
        if choice == "1":
            query = input("Enter search term: ").strip()
            if query:
                matches = searcher.search(query)
                searcher.display_results(matches, f"Users containing '{query}'")
                
                if matches and input("\nExport results? (y/N): ").lower() == 'y':
                    export_file = input("Export filename: ").strip()
                    if export_file:
                        searcher.export_results(matches, export_file)
        
        elif choice == "2":
            query = input("Enter prefix: ").strip()
            if query:
                matches = searcher.search_starts_with(query)
                searcher.display_results(matches, f"Users starting with '{query}'")
                
                if matches and input("\nExport results? (y/N): ").lower() == 'y':
                    export_file = input("Export filename: ").strip()
                    if export_file:
                        searcher.export_results(matches, export_file)
        
        elif choice == "3":
            try:
                min_rank = int(input("Min rank: "))
                max_rank = int(input("Max rank: "))
                matches = searcher.search_by_rank(min_rank, max_rank)
                searcher.display_results(matches, f"Ranks {min_rank}-{max_rank}")
                
                if matches and input("\nExport results? (y/N): ").lower() == 'y':
                    export_file = input("Export filename: ").strip()
                    if export_file:
                        searcher.export_results(matches, export_file)
            except ValueError:
                print("Please enter valid numbers!")
        
        elif choice == "4":
            matches = searcher.search_by_rank(1, 50)
            searcher.display_results(matches, "Top 50 Users")
        
        elif choice == "5":
            import random
            sample = random.sample(searcher.usernames, min(20, len(searcher.usernames)))
            searcher.display_results(sample, "Random 20 Users")
        
        elif choice == "6":
            export_file = input("Export all data to filename: ").strip()
            if export_file:
                searcher.export_results(searcher.usernames, export_file)
        
        elif choice == "7":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()
