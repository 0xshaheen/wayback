import requests
import json
import re
import sys
import os
import time

# Banner
def print_banner():
    banner = """
    ============================================
         Wayback Machine Subdomain Finder
    ============================================
    Author: 0xShaheen
    Facebook: https://facebook.com/0xshaheen
    Twitter:  https://x.com/0xshaheen
    Github:   https://github.com/0xshaheen
    LinkedIn: https://www.linkedin.com/in/0xshaheen
    Medium:   https://medium.com/@0xshaheen
    ============================================
    """
    print(banner)

# Function to fetch subdomains from Wayback Machine
def fetch_wayback_subdomains(domain):
    url = f"http://web.archive.org/cdx/search/cdx?url=*.{domain}/*&output=json&collapse=urlkey"
    headers = {"User-Agent": "Mozilla/5.0"}

    retries = 3
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            if response.text.strip() == "":
                print(f"[!] Empty response from Wayback Machine for {domain}.")
                return
            
            data = response.json()
            if not data or len(data) <= 1:
                print(f"[!] No data found for {domain}.")
                return

            # Extract subdomains matching *.domain.com
            subdomain_pattern = re.compile(rf"([a-zA-Z0-9._-]+\.)?{re.escape(domain)}")
            subdomains = sorted(set(
                match.group(0) for entry in data[1:] if len(entry) > 2
                for match in [subdomain_pattern.search(entry[2])] if match
            ))

            if subdomains:
                output_file = f"wayback_subs_{domain}.txt"
                with open(output_file, "w") as f:
                    f.write("\n".join(subdomains))
                print(f"[+] {len(subdomains)} subdomains for {domain} saved to {output_file}")
            else:
                print(f"[!] No matching subdomains found for {domain}.")
            return
        
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to fetch data for {domain}: {e}")
            time.sleep(2)
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON decoding error for {domain}: {e}")
            return
        except Exception as e:
            print(f"[ERROR] Unexpected error for {domain}: {e}")
            return

    print(f"[ERROR] All retries failed for {domain}.")

# Validate domain format
def validate_domain(domain):
    pattern = r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$"
    if not re.match(pattern, domain):
        print(f"[ERROR] Invalid domain format: {domain}")
        sys.exit(1)

# Main function
def main():
    print_banner()

    if len(sys.argv) < 2:
        domain_or_file = input("Enter a domain (e.g., domain.com) or a file containing domains: ").strip()
    else:
        domain_or_file = sys.argv[1].strip()

    if os.path.isfile(domain_or_file):
        with open(domain_or_file, "r") as file:
            domains = [line.strip() for line in file if line.strip()]
        
        print(f"[+] Found {len(domains)} domains in {domain_or_file}. Fetching subdomains...\n")
        for domain in domains:
            validate_domain(domain)
            fetch_wayback_subdomains(domain)
    else:
        validate_domain(domain_or_file)
        fetch_wayback_subdomains(domain_or_file)

if __name__ == "__main__":
    main()
