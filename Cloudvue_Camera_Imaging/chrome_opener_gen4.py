from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

import time

def open_in_chrome_gen4(selected_ips):
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument("--remote-debugging-port=9222")
    #chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("window-size=800x400")
    chrome_options.add_argument("--no-first-run")  # Suppress the initial tab
    chrome_options.add_argument("about:blank")  # Open an empty page instead of the default tab
    chrome_options.add_argument("--detach")

    # ✅ AUTO-INSTALL / AUTO-UPDATE CHROMEDRIVER
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    for ip in selected_ips:
        url = f"https://{ip}"
        print(f"Opening {url} in a new tab...")

        # Open new tab and switch to it
        driver.execute_script(f"window.open('{url}')")
        driver.switch_to.window(driver.window_handles[-1])

        wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds for elements

        # Define a mapping of firmware version prefixes to file paths
        firmware_paths = {
            "Illustra.Ess4.01.02": "/home/neal/PycharmProjects/Cloudvue_Camera_Imaging/Firmware/Illustra.Ess4.01.02.10.5982.tar.gz",
            "Illustra.Ess4.01.01": "/home/neal/PycharmProjects/Cloudvue_Camera_Imaging/Firmware/Illustra.Ess4.01.02.10.5982.tar.gz",
            "Illustra.SS004": "/home/neal/PycharmProjects/Cloudvue_Camera_Imaging/Firmware/Illustra.SS004.01.09.05.0008.tar.gz",
            "Illustra.SS008": "/home/neal/PycharmProjects/Cloudvue_Camera_Imaging/Firmware/Illustra.SS008.03.03.00.0002.tar.gz",
            "Illustra.SS009": "/home/neal/PycharmProjects/Cloudvue_Camera_Imaging/Firmware/Illustra.SS009.03.03.00.0002.tar.gz",
            "Illustra.SS018": "/home/neal/PycharmProjects/Cloudvue_Camera_Imaging/Firmware/Illustra.SS018.06.05.00.0005.tar.gz"
        }

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
            login_button = driver.find_element(By.ID, "lgn_button")


            username_field.send_keys("admin")
            password_field.send_keys("admin")
            login_button.click()
        except Exception as e:
            print(f"Login process failed for {url}: {e}")
            if len(driver.window_handles) > 0:
                driver.switch_to.window(driver.window_handles[-1])
            continue

        # Click accept
        try:
            time.sleep(1)
            accept_button = wait.until(ec.element_to_be_clickable((By.ID, "eulaMessage_1")))
            accept_button.click()
            print("Clicked 'Accept' button successfully.")
        except Exception as e:
            print(f"No 'Accept' button found or could not click on {url}: {e}")

        # Input Device IDs and Save
        try:
            time.sleep(1)
            dev_id_1 = wait.until(ec.presence_of_element_located((By.ID, "devId_1")))
            dev_id_2 = driver.find_element(By.ID, "devId_2")

            dev_id_1.send_keys("323232")
            dev_id_2.send_keys("323232")

            save_button = wait.until(
                ec.element_to_be_clickable((By.ID, "hostIdSave_2")))
            save_button.click()
            print("Device IDs entered and saved successfully.")
        except Exception as e:
            print(f"Skipping 'Input Device IDs and Save' step for {url}: {e}")
            time.sleep(2)

        # Set Standard Mode and Apply
        try:
            standard_mode_radio = wait.until(ec.element_to_be_clickable(
                (By.XPATH, "//input[@id='smode_0']")
            ))
            standard_mode_radio.click()

            apply_button = wait.until(ec.element_to_be_clickable(
                (By.ID, "secMode_1")
            ))
            apply_button.click()

            # WAIT FOR UI TO UNLOCK
            wait.until(ec.invisibility_of_element_located(
                (By.CLASS_NAME, "ui-widget-overlay")
            ))

        except Exception as e:
            print(f"Standard mode selection failed for {url}: {e}")


        # Enter passwords and Apply
        try:
            current_password = wait.until(ec.presence_of_element_located((By.ID, "cPwd")))
            current_password.send_keys("admin")

            new_password = driver.find_element(By.ID, "nPwd")
            confirm_new_password = driver.find_element(By.ID, "nPwdCpy")

            new_password.send_keys("323232")
            confirm_new_password.send_keys("323232")

            apply_button = wait.until(ec.element_to_be_clickable((By.ID, "secPwChange_1")))
            apply_button.click()
            print(f"'Apply' button clicked on {url}.")
        except Exception as e:
            print(f"Failed to enter passwords or click 'Apply' on {url}: {e}")

        # Handle Calibration prompt
        try:
            calibration_yes = wait.until(ec.element_to_be_clickable(
                (By.ID, "calibrationNotice_1")
            ))

            driver.execute_script("arguments[0].click();", calibration_yes)
            print("Calibration started (clicked Yes).")

            # Wait for overlay to disappear after calibration starts
            wait.until(ec.invisibility_of_element_located(
                (By.CLASS_NAME, "ui-widget-overlay")
            ))

        except Exception as e:
            print(f"No calibration prompt found or failed to click: {e}")

        # Click additional elements: Setup, System, About
        try:
            setup_button = wait.until(
                ec.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div/div[1]/label[3]")))

            actions = ActionChains(driver)
            actions.move_to_element(setup_button).perform()
            print("Hovered over the 'Setup' button.")

            setup_button.click()
            time.sleep(1)
            setup_button.click()
            print("'Setup' button clicked successfully.")
        except Exception as e:
            print(f"Failed to hover and click the 'Setup' button: {e}")

        try:
            time.sleep(2)
            system_link = wait.until(ec.element_to_be_clickable((By.ID, "AboutID_href")))
            system_link.click()

            time.sleep(1)
            about_item = wait.until(ec.element_to_be_clickable((By.ID, "AboutIDAbout")))
            about_item.click()
            print(f"'Setup', 'System', and 'About' were clicked on {url}.")
        except Exception as e:
            print(f"Failed to click additional elements on {url}: {e}")

        # Check Firmware Version and Upload if Matches

         # ---- FIRMWARE ----
        try:
            firmware_ver = wait.until(ec.presence_of_element_located((By.ID, "camFWVer"))).text
            print(f"{ip} firmware: {firmware_ver}")

            for prefix, path in firmware_paths.items():
                if firmware_ver.startswith(prefix):
                    wait.until(ec.element_to_be_clickable((By.ID, "AboutIDMaintenance"))).click()
                    wait.until(ec.presence_of_element_located(
                        (By.ID, "Isystem_infor_firmware_file"))
                    ).send_keys(path)
                    wait.until(ec.element_to_be_clickable(
                        (By.ID, "Isystem_infor_firmware"))
                    ).click()
                    break
        except Exception as e:
            print(f"Firmware handling failed for {ip}: {e}")


        time.sleep(5)

