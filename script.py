# Resources
# https://www.scrapingbee.com/blog/selenium-python/
# https://stackoverflow.com/questions/1066933/how-to-extract-top-level-domain-name-tld-from-url
# https://github.com/wkeeling/selenium-wire
# https://stackoverflow.com/questions/56705650/how-to-capture-network-traffic-with-selenium
# https://www.geeksforgeeks.org/packet-sniffing-using-scapy/



# Diagram
# ------> Browser launched
#       ------> Start capturing packets
#              ------> Connect to webpage
#                     Page is loaded
#              ------> Screenshot once page is loaded
#       ------> Stop capturing packets
# ------> Browser closed

# Sidenote:
# Not sure whats best to capture packets
# Researching it looks like tcpdump is better for live captures
# This command allows for user to run tcpdump without sudo: 
# sudo setcap cap_net_raw,cap_net_admin=eip $(which tcpdump)

# To consider:
# How does tcpdump work when we implement multithreading
# Need to do further research (we don't want to mix up the packets from different webpages)

import subprocess
import time
# import threading
import os
from selenium import webdriver
import tldextract
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

os.makedirs("networks", exist_ok=True)
os.makedirs("screenshots", exist_ok=True)

# Helper function to get the top level domain name
def get_domain_name(url):
    extracted = tldextract.extract(url)
    return extracted.domain

# Helper function to get the list of websites to be scraped
def fetch_websites():
    websites = []
    with open('websites.txt', 'r') as file:
        for line in file:
            websites.append(line.strip())
    return websites

def start_capturing(website):

    domain = get_domain_name(website)
    pcap_file = f"networks/{domain}.pcap"

    tcpdump_cmd = ["tcpdump", "-i", "any", "-w", pcap_file]
    
    try:
        # run tcpdump subprocess
        tcpdump_process = subprocess.Popen(tcpdump_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return tcpdump_process
    except Exception as e:
        print(f"Error starting tcpdump for {website}: {e}")
        return None

def stop_capturing(capture):
    # Check if process is still running
    if capture.poll() is None:
        capture.terminate()
        capture.wait()
        
    # # Stop packet capture
    # capture.terminate()
    # subprocess.run(["sudo", "killall", "tcpdump"])

def load_webpage(driver, website):
    
    try:
        # Visit the website
        driver.get(website)
        # Wait for the page to load by checking for the presence of the <body> tag
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print(f"Successfully loaded: {website}")
        
    except Exception as e:
        print(f"Error loading {website}: {e}")
        
def screenshot(driver, website):
    filename = get_domain_name(website)
    filename = f"screenshots/{filename}.png"
    driver.save_screenshot(filename)
    
def browser(website):
    
    options = Options()
    # For headless mode
    # options.add_argument("--headless")
    
    # Initialise driver
    driver = webdriver.Chrome(options=options)
    
    # Begin capturing packets
    capture = start_capturing(website)
    
    # Load the webpage
    load_webpage(driver, website)
    
    # Take a screenshot of the loaded page
    # Not sure how to determine if a page is fully loaded
    screenshot(driver, website)
    
    # Stop capturing packets
    stop_capturing(capture)
    
    # Quit the browser
    driver.quit()
    
if __name__ == "__main__":
    
    websites = fetch_websites()

    for website in websites:
        browser(website)

    # threads = []
    # for website in websites:
    #     t = threading.Thread(target=browser, args=(website,))
    #     threads.append(t)
    #     t.start()

    # for t in threads:
    #     t.join()