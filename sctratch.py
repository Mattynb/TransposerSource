# Import the library Selenium
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
  
# Make browser open in background
options = webdriver.ChromeOptions()
  
# Create the webdriver object
browser = webdriver.Chrome(
    executable_path="C:\chromedriver_win32\chromedriver.exe", 
  options=options)
  
# Obtain the Google Map URL
url = "https://www.google.com/maps/search/condominiums/@40.7936903,-74.0277896,14z/data=!3m1!4b1"
  
# Initialize variables and declare it 0
i = 0
  
# Create a loop for obtaining data from URLs

# Open the Google Map URL
browser.get(url)
  
# Obtain the title of that place
title = browser.find_element_by_class_name("x3AX1-LfntMc-header-title-title")
print(i+1, "-", title.text)
  
# Obtain the address of that place
address = browser.find_elements_by_class_name("CsEnBe")[0]
print("Address: ", address.text)
print("\n")