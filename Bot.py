from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-notifications")
browser = webdriver.Chrome(options = chrome_options)

try:
    browser.get("https://kautz-collioni-concept.streamlit.app")

    WebDriverWait(browser, 15).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    recovery_button = WebDriverWait(browser, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Yes, get this app back up!')]"))
    )

    recovery_button.click()

    WebDriverWait(browser, 5).until(
        EC.invisibility_of_element_located((By.XPATH, "//button[contains(text(), 'Yes, get this app back up!')]"))
    )

except TimeoutException:
    print("Tempo limite excedido: elemento não encontrado ou página lenta!")
finally:
    browser.quit()