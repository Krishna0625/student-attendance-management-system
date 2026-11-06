from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Open Google Chrome
driver = webdriver.Chrome()

try:
    # Open Student Management login page
    driver.get("http://localhost:5002")

    wait = WebDriverWait(driver, 10)

    # Find username and password fields
    username = wait.until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    password = driver.find_element(By.NAME, "password")

    # Enter faculty login details
    username.send_keys("admin")
    password.send_keys("admin123")

    # Click login button
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    # Wait for dashboard
    wait.until(EC.url_contains("dashboard"))

    print("Login test passed!")
    print("Dashboard URL:", driver.current_url)

except Exception as e:
    print("Login test failed:", e)

finally:
    driver.quit()
