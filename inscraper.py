"""
InScraper
Author: stuxweet

A Python script to scrape public profile information from the People section of a LinkedIn company page.
Uses Selenium WebDriver and Chrome.
Saves scraped profiles to 'linkedin_profiles.csv'.

Usage:
    python inscraper.py "https://www.linkedin.com/company/<COMPANY-NAME>/people/"

"""

import os
import sys
import time
import random
import keyboard
import threading

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC

stop_requested = False

# Monitor for 'q' to stop the script
def monitor_keypress():
    global stop_requested
    keyboard.wait('q') 
    stop_requested = True
    print("\n[!] User interruption requested. Exiting...")

# Abort the script / close the browser
def abort_script(driver):
    driver.quit()
    os._exit(0)  # exit the script

linkedin_login_url = "https://www.linkedin.com/login"

"""
As of March 17, 2025, starting from Chrome 136, it is no longer possible to use the default Chrome profile for debugging. 
This means that to persist a login, you must create a separate profile.
See: https://developer.chrome.com/blog/remote-debugging-port
"""
def setup_chrome_profile():
    chrome_profile_dir = os.path.abspath(r".\inscraperChromeProfile")

    if not os.path.exists(chrome_profile_dir):
        try:
            os.makedirs(chrome_profile_dir, exist_ok=True)
        except Exception as e:
            print(f"[!] Error creating profile: {e}")
            return None

    return chrome_profile_dir

# sets up the Chrome WebDriver with the specified profile directory.
def setup_chromedriver(profile_dir, headless=True):
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={profile_dir}")
    options.add_argument("profile-directory=Default")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")

    if headless:
        options.add_argument("--headless=new")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    return driver

# checks if the user is currently logged into LinkedIn
def is_logged_in(driver):
    driver.get("https://www.linkedin.com/feed/")  # URL to check login status
    time.sleep(5)
    return "feed" in driver.current_url

# prompts the user to log in manually via the opened browser window
def prompt_user_login(driver):
    print("[*] Please log in to LinkedIn in the window that opened.")
    driver.get(linkedin_login_url)
    input("[*] After finishing the login, press ENTER here in the terminal to continue...")

    if is_logged_in(driver):
        print("[+] Login successfully detected!")
        return True
    else:
        print("[!] Login not detected. Please check if you logged in correctly.")
        return False

# Scrapes all profiles from the given LinkedIn "People" page
def scrape_profiles(driver, url):
    print(f"[*] Accessing: {url}")
    driver.get(url)  # URL to scrape profiles from, given as an argument by the user
    time.sleep(5)  # wait for the page to load

    if "login" in driver.current_url:  # check if the user is logged in
        print("[!] ERROR: Not logged in to LinkedIn!")
        return False

    print("[*] Starting scraping...")
    # Wait for the page to load completely
    time.sleep(5)

    print("[*] Loading all available profiles...")

    print("[*] Press 'q' at any time to interrupt.")

    # Scroll and click the button until no more profiles are loaded
    last_count = -1
    retries = 0
    max_retries = 3  # maximum number of retries to find the "Load more" button
    while retries < max_retries:
        try:
            wait = WebDriverWait(driver, 10)
            more_button = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                "button.scaffold-finite-scroll__load-button"
            )))  # find the "Load more" button
            driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", more_button)  # scroll to the button
            time.sleep(1.5)
            more_button.click()

            time.sleep(random.uniform(3, 5))  # prevent being detected as a bot

            profiles = driver.find_elements(
                By.CSS_SELECTOR, 'li.org-people-profile-card__profile-card-spacing')  # find all profiles
            current_count = len(profiles)

            if stop_requested: # check if 'q' was pressed
                abort_script(driver)
            
            print(f"[+] Profiles loaded so far: {current_count}", end='\r')  # print the number of loaded profiles

            if current_count > last_count:
                last_count = current_count
                retries = 0
            else:
                retries += 1

        except:
            print(f"\n[!] 'Load more' button not found or not clickable. There may be no more profiles to load.")
            break

    # Check again all profiles after scrolling
    profiles = driver.find_elements(
        By.CSS_SELECTOR, 'li.org-people-profile-card__profile-card-spacing')
    print(f"[+] Total profiles found: {len(profiles)}")

    error_count = 0
    with open('linkedin_profiles.csv', 'w', encoding='utf-8') as file:
        file.write("Link;Name;Description\n")  # CSV header
        print("[*] Saving profiles to 'linkedin_profiles.csv'...")

        # iterate through all found profiles
        # and save their data to CSV     
        for idx, profile in enumerate(profiles, 1):
            if stop_requested:
                abort_script(driver)
            try:
                time.sleep(random.uniform(1, 3))
                # capture profile link, name, and description
                # using CSS selectors
                # ***these selectors may change over time, so they may need to be updated***
                link = profile.find_element(
                    By.CSS_SELECTOR, "a[data-test-app-aware-link]").get_attribute("href").split('?')[0]
                name = profile.find_element(
                    By.CSS_SELECTOR, ".artdeco-entity-lockup__title .lt-line-clamp--single-line").text
                desc = profile.find_element(
                    By.CSS_SELECTOR, ".artdeco-entity-lockup__subtitle .lt-line-clamp--multi-line").text
                file.write(f"{link};{name};{desc}\n")  # save profile data to CSV
                print(f"[+] Processed profile {idx}/{len(profiles)}", end='\r')  # print progress
            except:
                print(f"\n[!] Error processing profile {idx}: private or incomplete data.")
                error_count += 1

    print(f"\n[✓] Profiles processed: {len(profiles) - error_count}")
    # print error count
    # profiles with errors are not saved to CSV
    # errors can be caused by private profiles, missing elements, etc (most likely due to private profiles).
    print(f"[!] With errors: {error_count}")
    return True

if __name__ == "__main__":
    # print usage if number of arguments is different than 2
    if len(sys.argv) != 2:
        print('[!] Usage: python inscraper.py "https://www.linkedin.com/company/<COMPANY-NAME>/people/"')
        sys.exit(1)

    url = sys.argv[1] # URL to scrape profiles from, given as an argument by the user
    profile_dir = setup_chrome_profile() # create or get the Chrome profile directory
    if not profile_dir: # if profile directory could not be created
        sys.exit(1)

    driver = setup_chromedriver(profile_dir, headless=True) # set up the Chrome WebDriver with the specified profile directory
    if not is_logged_in(driver): # check if the user is logged in
        driver.quit()
        print("[*] Not logged in, opening window for login...")
        driver = setup_chromedriver(profile_dir, headless=False)
        if not prompt_user_login(driver):
            driver.quit()
            print("[!] Login failed or expired.")
            sys.exit(1)
        driver.quit()
        # Restart the driver in headless mode after login
        print("[*] Restarting in headless mode...")
        driver = setup_chromedriver(profile_dir, headless=True)

    threading.Thread(target=monitor_keypress, daemon=True).start() # start monitoring for 'q' keypress

    # Start scraping profiles from the URL
    try:
        if not scrape_profiles(driver, url):
            print("[!] Failed to process scraping.")
    finally:
        driver.quit()
        print("[*] Browser closed.")
