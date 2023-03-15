# Import libraries
import chromedriver_autoinstaller
chromedriver_autoinstaller.install()
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Time imports
import random
import datetime
import time

# Other imports
import re as re
import pandas as pd
import os
import sys
import numpy as np

import pymysql
import sqlalchemy as alch
from getpass import getpass

from dotenv import load_dotenv
load_dotenv()

# Functions

def get_categories(zip, headless=False):
    """
    Get a list of all the categories available in Mercadona website based on the input postal code.

    Args:
    zip (str): The postal code used to find the nearest Mercadona store.

    Returns:
    list: A list of strings containing the name of each category available in the website.

    Raises:
    TimeoutException: If the browser is unable to find any required element in the page within the allotted time.
    NoSuchElementException: If the browser is unable to find the element that matches the specified selector.
    ElementClickInterceptedException: If the browser is unable to click on an element because another element is blocking it.
    """

    # Set options for headless (invisible) browsing
    options = Options()
    # add the headless argument if passed
    if headless:
        options.add_argument('--headless')

    # Start the driver with the options
    driver = webdriver.Chrome(options=options)

    # Navigate to the login page
    driver.get('https://www.mercadona.es/')

    # Enter the postal code and submit
    postal_code = driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Código postal"]').send_keys(zip)
    submit_button = driver.find_element(By.CSS_SELECTOR, 'input.postal-code-form__button').click()

    # Wait until categories is clickable and click it.
    categorias_link = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.LINK_TEXT, "Categorías"))).click()

    # Wait for the "product-cell" element to be clickable (grid of porducts)
    product_cell = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-test='product-cell']")))

    # Accept cookies
    accept_button = driver.find_element(By.XPATH, "//button[contains(text(),'Aceptar todas')]").click()

    # Find all the category links
    category_links = driver.find_elements(By.CSS_SELECTOR, "span[class='category-menu__header']")

    ret_list = []
    for i in category_links:
        ret_list.append(i.text)
    
    # Close the session
    driver.quit()

    return ret_list

def get_subcategories(zip, category, headless=True):
    """
    Retrieve the subcategories of a given category in the Mercadona website for a given postal code.

    Args:
        zip (str): The postal code of the location to browse.
        category (str): The name of the category to retrieve subcategories for.

    Returns:
        list: A list containing a string with the name of every subcategory of the given category.
    """
    
    # Set options for headless (invisible) browsing
    options = Options()

    # add the headless argument if passed
    if headless:
        options.add_argument('--headless')

    # Start the driver with the options
    driver = webdriver.Chrome(options=options)

    # Navigate to the login page
    driver.get('https://www.mercadona.es/')

    # Enter the postal code and submit, then wait for categories to be available and clicks it
    postal_code = driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Código postal"]').send_keys(zip)
    submit_button = driver.find_element(By.CSS_SELECTOR, 'input.postal-code-form__button').click()
    categorias_link = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.LINK_TEXT, "Categorías"))).click()

    # Wait for the "product-cell" element to be clickable (grid of porducts) and accepts cookies.
    product_cell = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-test='product-cell']")))
    accept_button = driver.find_element(By.XPATH, "//button[contains(text(),'Aceptar todas')]").click()

    # Wait for the target category to be clickable and clicks it
    selected_category = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//label[text()='{category}']"))).click()

    # Wait for the subcategories to load and save them
    subcategory_links = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".category-item__link")))

    ret_list = []
    for i in subcategory_links:
        ret_list.append(i.text)
    
    driver.quit()

    return ret_list

def get_product_info(zip, category, subcategory, wait=0, headless=False):
    """
    Get product information from the Mercadona website for a given zip code, category and subcategory.
    Returns a pandas DataFrame with a row per each product scraped and the total amount of products scraped.
    The product information includes the product name, type, volume, price per unit, price, unit, category, subcategory, URL, product code (from URL), and the collected timestamp. 

    Args:
        zip (str): The zip code for the Mercadona website to search in.
        category (str): The category of products to search for.
        subcategory (str): The subcategory of products to search for.
        headless (bool, optional): Whether to run the Chrome webdriver in headless mode. Defaults to True.
        
    Returns:
        ret_df: A pandas DataFrame with a row per each product scraped.
        product_count: An int representing the amount of products scraped.
    """
    # create a ChromeOptions object
    options = Options()

    # add the headless argument if passed
    if headless:
        options.add_argument('--headless')

    # specify the path to your web driver
    driver = webdriver.Chrome(options=options)

    # navigate to the login page
    driver.get('https://www.mercadona.es/')

    # enter the postal code and submit it
    postal_code = driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Código postal"]').send_keys(zip)
    submit_button = driver.find_element(By.CSS_SELECTOR, 'input.postal-code-form__button').click()

    # wait until categories is clickable and click it, then wait for the product grid to be clickable and accept cookies
    categorias_link = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.LINK_TEXT, "Categorías"))).click()
    product_cell = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-test='product-cell']")))
    accept_button = driver.find_element(By.XPATH, "//button[contains(text(),'Aceptar todas')]").click()

    # wait for the passed category and subcategory to be clickable and clicks them
    selected_category = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//label[text()='{category}']"))).click()
    selected_subcategory = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//button[text()='{subcategory}']"))).click()

    # wait for the products to load and saves them
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-cell")))
    product_cells = driver.find_elements(By.CSS_SELECTOR, "div[data-test='product-cell']")

    # Get the current URL of the page
    current_url = driver.current_url

    # Click on the frist "product-cell" element
    product_cells[0].click()

    # Initialize list of dictionaries (to be turned into a dataframe) and product counter for feedback
    list_of_dicts = []
    product_count = 0

    # Iterate over the "product-cell" elements (products)
    for i in range(len(product_cells)):
        # Scroll to the current product cell and wait for the "product-cell" element to be clickable
        driver.execute_script("arguments[0].scrollIntoView();", product_cells[i])
        product_cell = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-test='product-cell']")))

        # wait for the description element to be present
        descripcion = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.private-product-detail__description')))

        # Give feedback to user by printing the current product
        print(f'\rScraping "{i+1}: {product_cells[i].text[0:15]}..." product...                                                                              ', end='')
        sys.stdout.flush()

        # Initialize the dictionary that will be apended to the list (that will later be our DataFrame)
        info_prod={}

        # Scrapes data if available, when it is not it saves "Not available"
        # Product name
        try:
            info_prod["product"] = driver.find_element(By.CSS_SELECTOR, 'h1.title2-r.private-product-detail__description').text
        except:
            info_prod["product"] = "Not available"
        # Product_type
        try:
            info_prod["product_type"] = driver.find_element(By.CSS_SELECTOR, 'span.headline1-r:nth-child(1)').text
        except:
            info_prod["product_type"] = "Not available"
        # Product_volume
        try:
            info_prod["product_volume"] = driver.find_element(By.CSS_SELECTOR, 'span.headline1-r:nth-child(2)').text
        except:
            info_prod["product_volume"] = "Not available"
        # Price per unit (€ / L)
        try:
            info_prod["product_price_per_unit"] = driver.find_element(By.CSS_SELECTOR, 'span.headline1-r:nth-child(3)').text.replace("| ","")
        except:
            info_prod["product_price_per_unit"] = "Not available"
        # Product_price
        try:
            info_prod["product_price"] = float(driver.find_element(By.CSS_SELECTOR, 'p.product-price__unit-price.large-b').text.replace("€","").strip().replace(",","."))
        except:
            info_prod["product_price"] = "Not Available"
        # Product unit (e.g.: L)
        try:
            info_prod["product_unit"] = driver.find_element(By.CSS_SELECTOR, 'p.product-price__extra-price.title1-r').text.replace("/","").replace(".","")
        except:
            info_prod["product_unit"] = "Not Available"
        # Product category
        try:
            info_prod["product_category"] = driver.find_element(By.CSS_SELECTOR, 'span.subhead1-r').text.replace(" >","")
        except:
            info_prod["product_category"] = "Not Available"
        # Product Subcategory
        try:
            info_prod["product_subcategory"] = driver.find_element(By.CSS_SELECTOR, 'span.subhead1-sb').text
        except:
            info_prod["product_subcategory"] = "Not Available"
        # Url, Product code (from URL), and scraped time
        info_prod["product_url"] = driver.current_url
        info_prod["product_code"] = driver.current_url.split("/")[4]
        info_prod["collected_timestamp"] = datetime.datetime.now()

        # Appends the current row (product) to the list of dicts (will be turned to a DataFrame) and advances the counter
        list_of_dicts.append(info_prod)
        product_count += 1
        
        time.sleep(wait/2)

        # Send the 'esc' key and the back command to exit the product info page. Does it until we are moved back to the product grid (URL contains "categories")
        while "categories" not in driver.current_url:
            driver.back()
            driver.find_element(By.CSS_SELECTOR, "body").send_keys(Keys.ESCAPE)
        
        time.sleep(wait/2)

        # Click on the next "product-cell" element, if available
        if i < len(product_cells) - 1:
            next_product_cell = product_cells[i+1]
            next_product_cell.click()

            # Wait for the page to load
            WebDriverWait(driver, 10).until(EC.url_changes(current_url))

            # If we get an error for too many requests, exit the function by returning "Error" and closing the browser window.
            try:
                len(driver.find_element(By.XPATH, '//button[contains(text(), "Entendido")]').text) > 0
                driver.quit()
                return "error"

            except:
                continue
        
    # Creates the Data Frame to return from the list of dictionaries created and closes the browser window
    ret_df = pd.DataFrame(list_of_dicts)
    driver.quit()
    
    return ret_df,product_count

def mercadona_full_scraper(cod_postal,retry=4, wait_min=0.3, wait_max=0.5, e_wait_min=3, e_wait_max=5, max_error_wait = 5, prod_wait=0, headless=False):
    start_time=time.time()
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    session_name = f"Mercadona Scraping {timestamp}"
    print(f"\rGetting categories...                                                      ", end='')
    sys.stdout.flush()
    categories = get_categories(cod_postal, headless=headless)

    product_info = pd.DataFrame({})
    error_count = 0
    missing_subcats = []

    for i in categories:
        print(f'\rGetting subcategories for the "{i}" category...                                                      ', end='')
        sys.stdout.flush()
        subcategories = get_subcategories(cod_postal, i, headless=headless)
        for x in subcategories:
            print(f'\rGetting products for the "{x}" subcategory in the "{i}" category...                                                ')
            sys.stdout.flush()
            
            retries = retry
            while retries > 0:
                try:
                    products, product_count =  get_product_info(cod_postal, i, x, wait=prod_wait, headless=headless)
                    product_info = pd.concat([product_info,products], ignore_index=True)
                    product_info.to_csv(f'scraping_output/{session_name}.csv', index=False, mode='w', sep='~')
                    random_time = random.randint((wait_min*60*1000), (wait_max*60*1000)) /1000
                    if random_time > max_error_wait*60:
                        random_time = random.randint((((max_error_wait*60)-30)*1000), (((max_error_wait*60)+30)*1000)) /1000
                    print(f"\n---------------\nTime:{round((time.time()-start_time)/60,2)}\nFinished '{x}' subcateogry succesfully. \n{product_count} products registered.\nWaiting {round(random_time/60,2)} minutes so that we don't get caught...\nCurrent size of data captured: {product_info.shape}\n---------------\n")
                    time.sleep(random_time)
                    break

                except:
                    print(f'\n\nTime: {round((time.time()-start_time)/60,2)}')
                    random_time = random.randint((((e_wait_min*60)+(error_count*10))*1000), (((e_wait_max*60)+(error_count*10))*1000)) /1000
                    if random_time > max_error_wait*60:
                        random_time = random.randint((((max_error_wait*60)-30)*1000), (((max_error_wait*60)+30)*1000)) /1000
                    error_count +=1
                    if retries == 1:
                        print(f"!!! An error occurred in subcategory '{x}'... Again... Adding it to the list of missing subcategories...\Waiting {round(random_time/60,2)} minutes so that we don't get caught... ")
                        missed_subcat={}
                        missed_subcat["category"]=i
                        missed_subcat["subcategory"]=x
                        missing_subcats.append(missed_subcat)
                        time.sleep(random_time)
                        break
                    retries -=1
                    print(f'!!! An error occurred in subcategory "{x}". Retrying in {round(random_time/60,2)} minutes...\n')
                    time.sleep(random_time)
    
    mising_subcategories = pd.DataFrame(missing_subcats)

    return product_info, mising_subcategories