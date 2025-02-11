from selenium import webdriver
 
# Initialise instance of the chrome driver (browser)
driver = webdriver.Chrome()

# Visit the website (should be a list)
driver.get("https://www.google.com")

# output
# print(driver.page_source)

# Shut down the browser
driver.quit()