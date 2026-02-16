import subprocess
import time
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from webdriver_manager.chrome import ChromeDriverManager

# ------------------------------------------
#   GLOBAL DRIVER CACHE (persistent windows)
# ------------------------------------------
drivers = {}   # {"192.168.1.10": <webdriver.Chrome>}


def get_persistent_driver(ip):
    """
    Return an existing Chrome window for this IP,
    or launch a new one and save it.
    """
    if ip in drivers:
        return drivers[ip]

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--window-size=800,400")
    chrome_options.add_experimental_option("detach", True)  # Do not close window

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    drivers[ip] = driver
    return driver


def process_single_camera(ip, partner_code_value):
    """Handles ONE camera in a persistent browser window."""
    print(f"[{ip}] Thread started.")

    try:
        driver = get_persistent_driver(ip)
        wait = WebDriverWait(driver, 10)

        # -------- PING --------
        print(f"[{ip}] Pinging...")
        result = subprocess.run(["ping", "-c", "1", ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if "unreachable" in result.stdout.lower():
            print(f"[{ip}] Unreachable. Skipping.")
            return

        # -------- OPEN URL --------
        url = f"https://{ip}"
        print(f"[{ip}] Opening {url}")
        driver.get(url)

        # -------- SECURITY WARNING --------
        try:
            advanced = wait.until(ec.element_to_be_clickable((By.ID, "details-button")))
            advanced.click()
            proceed = wait.until(ec.element_to_be_clickable((By.ID, "proceed-link")))
            proceed.click()
        except:
            pass

        # -------- LOGIN --------
        try:
            username_field = wait.until(ec.presence_of_element_located((By.ID, "username")))
            password_field = driver.find_element(By.ID, "password")
            login_button = wait.until(
                ec.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Log in')]"))
            )

            username_field.send_keys("admin")
            password_field.send_keys("323232")
            login_button.click()
        except Exception as e:
            print(f"[{ip}] Login failed: {e}")
            return

        time.sleep(3)

        # -------- SETUP --------
        try:
            setup = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, "label[for='doSetup']")))
            setup.click()
            print(f"[{ip}] Setup clicked.")
        except Exception as e:
            print(f"[{ip}] Setup click failed: {e}")

        # -------- SYSTEM --------
        try:
            system_link = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, "a#AboutID_href")))
            system_link.click()
        except:
            pass

        # -------- CLOUDVUE TAB --------
        try:
            cloudvue_tab = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, "a#smartVue")))
            cloudvue_tab.click()
        except Exception as e:
            print(f"[{ip}] Cloudvue tab failed: {e}")

        # -------- PARTNER CODE --------
        try:
            partner_input = wait.until(ec.presence_of_element_located((By.ID, "sv_partner")))
            partner_input.clear()
            partner_input.send_keys(partner_code_value)

            apply_button = wait.until(ec.element_to_be_clickable((By.ID, "SmartVueEnable")))
            apply_button.click()
        except Exception as e:
            print(f"[{ip}] Partner code apply failed: {e}")

        # -------- POPUP PASSWORD (HTML input) --------
        try:
            popup_password = wait.until(ec.presence_of_element_located((By.ID, "password")))
            popup_password.clear()
            popup_password.send_keys("323232")

            ok_button = wait.until(ec.element_to_be_clickable((By.ID, "secWarn_0")))
            ok_button.click()
            print(f"[{ip}] Popup password submitted.")
        except Exception as e:
            print(f"[{ip}] Popup password failed: {e}")

        print(f"[{ip}] DONE.")

    finally:
        print(f"[{ip}] Thread complete.")
        # persistent chrome window stays open


def ping_and_reopen(selected_ips, partner_code_value):
    """Starts multiple threads — one per IP, staggered by 5 seconds."""
    threads = []

    for index, ip in enumerate(selected_ips):
        t = threading.Thread(
            target=process_single_camera,
            args=(ip, partner_code_value)
        )
        t.start()
        threads.append(t)

        print(f"[{ip}] Thread launched.")

        # Wait 5 seconds before launching next thread
        if index < len(selected_ips) - 1:
            time.sleep(5)

    print("All threads started.")



