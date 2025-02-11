# Resources
# https://www.scrapingbee.com/blog/selenium-python/

# ------> Browser launched
#       ------> Start capturing packets
#              ------> Connect to webpage
#                     Page is loaded
#              ------> Screenshot once page is loaded
#       ------> Stop capturing packets
# ------> Browser closed

# Sidenote:
# Not sure if its better to
# Researching it looks like tcpdump is better for live captures

# To consider:
# Multithreading
# 

import subprocess
import time
import threading
from selenium import webdriver
import tldextract

# Helper function to get the top level domain name
def get_domain_name(url):
    extracted = tldextract.extract(url)
    return extracted.domain

# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager

def fetch_websites():
    websites = []
    with open('websites.txt', 'r') as file:
        for line in file:
            websites.append(line.strip())

    return websites

def browser(website):
    
    # # For headless mode
    # options = Options()
    # options.add_argument("--headless")
    # service = Service(ChromeDriverManager().install())
    # driver = webdriver.Chrome(service=service, options=options)
    
    # Initialise Selenium WebDriver
    driver = webdriver.Chrome()
    
    # Begin capturing packets
    capture = start_capturing(website)
    
    # Connect to webpage
    load_webpage(driver, website)
    
    # Take a screenshot of the loaded page
    screenshot(driver, website)
    
    # Stop capturing packets
    stop_capturing(capture)
    
    # Quit the browser
    driver.quit()

def start_capturing(website):

    res = get_domain_name(website)
    pcap_file = f"{res}.pcap"

    # Start packet capture before launching the browser (running tcpdump in the background)
    tcpdump_cmd = ["sudo", "tcpdump", "-i", "any", "-w", pcap_file]
    tcpdump_process = subprocess.Popen(tcpdump_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return tcpdump_process

def stop_capturing(capture):
    if capture.poll() is None:  # Check if process is still running
        capture.terminate()
        capture.wait()
    # # Stop packet capture
    # capture.terminate()
    # subprocess.run(["sudo", "killall", "tcpdump"])  # Ensure tcpdump stops completely

def load_webpage(driver, website):
    
    try:
        # Visit the website
        driver.get(website)

        # Allow time for page to load
        time.sleep(3)
        
    except Exception as e:
        print(f"Error loading {website}: {e}")
        
def screenshot(driver, website):
    filename = get_domain_name(website)
    filename = f"{filename}.png"
    driver.save_screenshot(filename)
    
if __name__ == "__main__":
    
    websites = fetch_websites()

    threads = []
    for website in websites:
        t = threading.Thread(target=browser, args=(website,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()