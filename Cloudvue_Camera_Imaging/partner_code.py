import subprocess
import time
import pyautogui
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def ping_and_reopen(selected_ips, partner_code_value):
    driver = None
    driver_path = "/home/neal/PycharmProjects/Cloudvue_Camera_Imaging/chromedriver-linux64/chromedriver"

    try:
        # Set up the Chrome driver once
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-first-run")

        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        wait = WebDriverWait(driver, 10)

        for ip in selected_ips:
            print(f"Starting to ping {ip}...")

            try:
                result = subprocess.run(
                    ["ping", "-c", "1", ip],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                output = result.stdout + result.stderr

                if "unreachable" in output.lower() or "bytes of data" not in output:
                    print(f"{ip} is unreachable. Skipping...")
                    continue

                if "time=" in output or "ms" in output:
                    print(f"{ip} is reachable. Opening in a new tab...")

                    # Open a new tab
                    driver.execute_script("window.open('');")
                    driver.switch_to.window(driver.window_handles[-1])  # Switch to the new tab

                    url = f"https://{ip}"
                    print(f"Opening {url}...")
                    driver.get(url)

                    # Bypass security warning
                    try:
                        advanced_button = wait.until(ec.element_to_be_clickable((By.ID, "details-button")))
                        advanced_button.click()

                        proceed_link = wait.until(ec.element_to_be_clickable((By.ID, "proceed-link")))
                        proceed_link.click()
                    except Exception as e:
                        print(f"Could not proceed on {url}: {e}")

                    # Enter credentials and login
                    try:
                        username_field = wait.until(ec.presence_of_element_located((By.ID, "username")))
                        password_field = driver.find_element(By.ID, "password")
                        login_button = wait.until(ec.element_to_be_clickable(
                            (By.XPATH, "//span[contains(@class, 'ui-button-text') and text()='Log in']")))

                        username_field.send_keys("admin")
                        password_field.send_keys("323232")
                        login_button.click()
                    except Exception as e:
                        print(f"Login process failed for {url}: {e}")
                        continue

                    # Click the "Setup" button
                    try:
                        setup_button = wait.until(ec.element_to_be_clickable(
                            (By.CSS_SELECTOR, "label[for='doSetup']")))
                        setup_button.click()
                        setup_button.click()
                        print("Clicked the Setup button.")
                    except Exception as e:
                        print(f"Could not click the Setup button: {e}")

                    # Click the "System" link
                    try:
                        system_link = wait.until(ec.element_to_be_clickable(
                            (By.CSS_SELECTOR, "a#AboutID_href")))
                        system_link.click()
                        print("Clicked the System link.")
                    except Exception as e:
                        print(f"Could not click the System link: {e}")

                    # Click the "Cloudvue" tab
                    try:
                        cloudvue_tab = wait.until(ec.element_to_be_clickable(
                            (By.CSS_SELECTOR, "li[aria-labelledby='smartVue'] a#smartVue")))
                        cloudvue_tab.click()
                        print("Clicked the Cloudvue tab.")
                    except Exception as e:
                        print(f"Could not click the Cloudvue tab: {e}")

                    # Enter the partner code
                    try:
                        partner_input = wait.until(ec.presence_of_element_located((By.ID, "sv_partner")))
                        partner_input.clear()
                        partner_input.send_keys(partner_code_value)
                        print(f"Entered partner code: {partner_code_value}")

                        # Locate and click the "Apply" button
                        apply_button = wait.until(ec.element_to_be_clickable((By.ID, "SmartVueEnable")))
                        apply_button.click()
                        print("Clicked the Apply button.")
                    except Exception as e:
                        print(f"Could not complete the Apply process: {e}")

                    # Handle modal dialog if required
                    try:
                        pyautogui.typewrite("323232")
                        time.sleep(1)
                        ok_button = wait.until(ec.element_to_be_clickable((By.ID, "secWarn_0")))
                        ok_button.click()
                        print("Clicked the 'OK' button.")
                    except Exception as e:
                        print(f"Could not click the 'OK' button: {e}")
                        pyautogui.press('enter')
                        time.sleep(1)

                        time.sleep(4)

            except Exception as e:
                print(f"Error processing {ip}: {e}")

            time.sleep(2)

    finally:
        if driver:
            driver.quit()  # Close the browser


