from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time


def open_in_chrome(selected_ips):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("window-size=800x400")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_experimental_option("detach", True)

    # ✅ AUTO-INSTALL / AUTO-UPDATE CHROMEDRIVER
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    for ip in selected_ips:
        url = f"https://{ip}"
        print(f"Opening {url} in a new tab...")

        driver.execute_script(f"window.open('{url}')")
        driver.switch_to.window(driver.window_handles[-1])

        wait = WebDriverWait(driver, 15)

        firmware_paths = {
            "Illustra.Ess4.01.02.": "/home/neal/PycharmProjects/Cloudvue_Camera_Imaging/Firmware/Illustra.Ess4.01.02.13.6953.tar.gz",
            "Illustra.Ess4.01.01.": "/home/neal/PycharmProjects/Cloudvue_Camera_Imaging/Firmware/Illustra.Ess4.01.02.13.6953.tar.gz",
            "Illustra.SS004": "/home/neal/PycharmProjects/Cloudvue_Camera_Imaging/Firmware/Illustra.SS004.01.09.05.0008.tar.gz",
            "Illustra.SS008": "/home/neal/PycharmProjects/Cloudvue_Camera_Imaging/Firmware/Illustra.SS008.03.03.00.0002.tar.gz",
            "Illustra.SS009": "/home/neal/PycharmProjects/Cloudvue_Camera_Imaging/Firmware/Illustra.SS009.03.03.00.0002.tar.gz",
            "Illustra.SS018": "/home/neal/PycharmProjects/Cloudvue_Camera_Imaging/Firmware/Illustra.SS018.06.05.00.0005.tar.gz"
        }

        # ---- SECURITY WARNING ----
        try:
            wait.until(ec.element_to_be_clickable((By.ID, "details-button"))).click()
            wait.until(ec.element_to_be_clickable((By.ID, "proceed-link"))).click()
        except:
            pass

        # ---- LOGIN ----
        try:
            username = wait.until(ec.element_to_be_clickable((By.ID, "username")))
            password = wait.until(ec.element_to_be_clickable((By.ID, "password")))
            login_btn = wait.until(ec.element_to_be_clickable(
                (By.XPATH, "//span[contains(text(),'Log in')]")
            ))

            username.clear()
            username.send_keys("admin")
            password.clear()
            password.send_keys("admin")
            login_btn.click()
        except Exception as e:
            print(f"Login failed for {ip}: {e}")
            continue

        # ---- DEVICE IDs ----
        try:
            dev_id_1 = wait.until(ec.element_to_be_clickable((By.ID, "devId_1")))
            dev_id_2 = wait.until(ec.element_to_be_clickable((By.ID, "devId_2")))
            save_btn = wait.until(ec.element_to_be_clickable(
                (By.XPATH, "//span[contains(text(),'Save')]")
            ))

            dev_id_1.send_keys("323232")
            dev_id_2.send_keys("323232")
            save_btn.click()
        except:
            pass

        # ---- STANDARD MODE ----
        try:
            wait.until(ec.element_to_be_clickable((By.ID, "smode_0"))).click()
            wait.until(ec.element_to_be_clickable(
                (By.XPATH, "//span[contains(text(),'Apply')]")
            )).click()
        except:
            pass

        # ---- PASSWORD CHANGE ----
        try:
            cPwd = wait.until(ec.element_to_be_clickable((By.ID, "cPwd")))
            nPwd = wait.until(ec.element_to_be_clickable((By.ID, "nPwd")))
            nPwdCpy = wait.until(ec.element_to_be_clickable((By.ID, "nPwdCpy")))

            cPwd.send_keys("admin")
            nPwd.send_keys("323232")
            nPwdCpy.send_keys("323232")

            wait.until(ec.element_to_be_clickable((By.ID, "secPwChange_1"))).click()
        except:
            pass

        # ---- NAVIGATION ----
        try:
            setup = wait.until(ec.element_to_be_clickable(
                (By.XPATH, "/html/body/div[1]/div[2]/div/div[1]/label[3]")
            ))
            ActionChains(driver).move_to_element(setup).click().perform()

            wait.until(ec.element_to_be_clickable((By.ID, "AboutID_href"))).click()
            wait.until(ec.element_to_be_clickable((By.ID, "AboutIDAbout"))).click()
        except:
            pass

        time.sleep(8)

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


