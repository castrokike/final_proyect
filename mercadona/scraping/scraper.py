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
import sys

from dotenv import load_dotenv
load_dotenv()



# Functions

def get_categories(zip, headless=False):

    """
    Scrape the Mercadona website to get a list of all the categories available based on the input postal code.

    Args:
        zip (str): The postal code used to find the nearest Mercadona store.
        headless (bool, optional): Whether to run the browser in headless mode, which means that the browser will not display a user interface. Defaults to False.

    Returns:
        list: A list of strings containing the name of each category available in the website.

    Raises:
        TimeoutException: If the browser is unable to find any required element in the page within the allotted time.
        NoSuchElementException: If the browser is unable to find the element that matches the specified selector.
        ElementClickInterceptedException: If the browser is unable to click on an element because another element is blocking it.
    """

    # Set options for headless (invisible) browsing
    options = Options()
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
        zip (str): The postal code of the location to browse. This is used to find the nearest Mercadona store.
        category (str): The name of the category to retrieve subcategories for.
        headless (bool, optional): If True, the function will run the web driver in headless mode, which means that the browser will not display a user interface. Defaults to True.

    Returns:
        list: A list containing a string with the name of every subcategory of the given category.
    
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
    Scrape product information from Mercadona website based on zip code, category, and subcategory.
    Returns a pandas DataFrame with a row per each product scraped and the total amount of products scraped.
    The product information includes the product name, type, volume, price per unit, price, unit, category, subcategory, URL, product code (from URL), and the collected timestamp. 

    Args:
        zip (str): The zip code for the Mercadona website to search in, it should be a string containing 5 digits.
        category (str): The category of products to search for.
        subcategory (str): The subcategory of products to search for.
        headless (bool, optional): Whether to run the Chrome webdriver in headless mode, which means the browser window will not be visible. Defaults to True.
        
    Returns:
        ret_df (pandas.DataFrame): A DataFrame with the following columns: 'product_name', 'product_type', 'volume', 'price_per_unit', 'price', 'unit', 'category', 'subcategory', 'url', 'product_code', 'timestamp'. Each row corresponds to a product scraped from the Mercadona website.
        product_count (int): The number of products scraped.
    """

    # Create a ChromeOptions object
    options = Options()

    # Add the headless argument if passed
    if headless:
        options.add_argument('--headless')

    # Specify the path to your web driver
    driver = webdriver.Chrome(options=options)

    # Navigate to the login page
    driver.get('https://www.mercadona.es/')

    # Enter the postal code and submit it
    postal_code = driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Código postal"]').send_keys(zip)
    submit_button = driver.find_element(By.CSS_SELECTOR, 'input.postal-code-form__button').click()

    # Wait until categories is clickable and click it, then wait for the product grid to be clickable and accept cookies
    categorias_link = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.LINK_TEXT, "Categorías"))).click()
    product_cell = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-test='product-cell']")))
    accept_button = driver.find_element(By.XPATH, "//button[contains(text(),'Aceptar todas')]").click()

    # Wait for the passed category and subcategory to be clickable and clicks them
    selected_category = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//label[text()='{category}']"))).click()
    selected_subcategory = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//button[text()='{subcategory}']"))).click()

    # Wait for the products to load and saves them
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

        # Wait for the description element to be present
        descripcion = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.private-product-detail__description')))

        # Give feedback to user by printing the current product being scraped
        print(f'\rScraping "{i+1}: {product_cells[i].text[0:15]}..." product...                                                                              ', end='')
        sys.stdout.flush()

        # Initialize the dictionary that will be appended to the list of already scraped product information (that will later be our DataFrame)
        info_prod={}

        # Scrapes data if available, when it is not, it saves "Not available"

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
        
        # Wait half of the time passed before going back to the product list
        time.sleep(wait/2)

        # Send the 'esc' key and the back command to exit the product info page. Do it until we are moved back to the product grid (URL contains "categories")
        while "categories" not in driver.current_url:
            driver.back()
            driver.find_element(By.CSS_SELECTOR, "body").send_keys(Keys.ESCAPE)
        
        # Wait the second half of the time passed before clicking the next product
        time.sleep(wait/2)

        # Click on the next "product-cell" element, if available
        if i < len(product_cells) - 1:
            next_product_cell = product_cells[i+1]
            next_product_cell.click()

            # Wait for the page to load
            WebDriverWait(driver, 10).until(EC.url_changes(current_url))

            # If an error is thrwon because of too many requests, exit the function by returning "Error" and closing the browser window.
            try:
                len(driver.find_element(By.XPATH, '//button[contains(text(), "Entendido")]').text) > 0
                driver.quit()
                return "error"

            # If this error is not displayed the code in the previous block will fail so we can continue scraping
            except:
                continue
        
    # Creates the Data Frame to return from the list of dictionaries created and closes the browser window
    ret_df = pd.DataFrame(list_of_dicts)
    driver.quit()
    
    return ret_df,product_count

def mercadona_full_scraper(cod_postal,retry=4, wait_min=0.3, wait_max=0.5, e_wait_min=3, e_wait_max=5, max_error_wait = 5, prod_wait=0, headless=False):

    """
    Scrape all available product information from the Mercadona website for a given zip code. 

    This function scrapes product information for all categories and subcategories in the specified zip code. It returns a pandas DataFrame with a row per each product scraped and the total amount of products scraped.
    The product information includes the product name, type, volume, price per unit, price, unit, category, subcategory, URL, product code (from URL), and the collected timestamp.

    Args:
        cod_postal (str): The zip code for the Mercadona website to search in. It is a string containing a 5 digit spanish zip code.
        retry (int, optional): The number of times to retry scraping a subcategory if an error occurs. Defaults to 4.
        wait_min (float, optional): The minimum amount of time to wait before each scrape, in seconds. Defaults to 0.3 (minutes).
        wait_max (float, optional): The maximum amount of time to wait before each scrape, in seconds. Defaults to 0.5 (minutes).
        e_wait_min (float, optional): The minimum amount of time to wait before retrying a failed scrape, in minutes. Defaults to 3.
        e_wait_max (float, optional): The maximum amount of time to wait before retrying a failed scrape, in minutes. Defaults to 5.
        max_error_wait (float, optional): The maximum amount of time to wait when an error occurs, in minutes. Defaults to 5. After every error, the random interval from which to pick a wait time increases, this parameter sets a max value.
        prod_wait (float, optional): The amount of time to wait for the page to load before scraping product information, in seconds. Defaults to 0.
        headless (bool, optional): Whether to run the Chrome webdriver in headless mode, which means the browser window will not be visible. Defaults to False.
        
    Returns:
        product_info (pandas.DataFrame): A pandas DataFrame with a row per each product scraped.
        missing_subcategories (pandas.DataFrame): A pandas DataFrame with a list of subcategories that failed to scrape.
    """
    
    # Record start time and current time as timestamp
    start_time=time.time()
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # Use timestamp to create unique session name
    session_name = f"Mercadona Scraping {timestamp}"

    # Print message indicating that categories are being retrieved
    print(f"\rGetting categories...                                                      ", end='')
    sys.stdout.flush()

    # Retrieve categories from Mercadona website for given postal code
    categories = get_categories(cod_postal, headless=headless)

    # Create empty DataFrame to store product information
    product_info = pd.DataFrame({})

    # Set error count to 0 and create empty list to store missing subcategories
    error_count = 0
    missing_subcats = []

    # Loop through each category
    for i in categories:

        # Print message indicating that subcategories for current category are being retrieved
        print(f'\rGetting subcategories for the "{i}" category...                                                      ', end='')
        sys.stdout.flush()

        # Retrieve subcategories for current category
        subcategories = get_subcategories(cod_postal, i, headless=headless)

        # Loop through each subcategory
        for x in subcategories:

            # Print message indicating that products for current subcategory are being retrieved
            print(f'\rGetting products for the "{x}" subcategory in the "{i}" category...                                                ')
            sys.stdout.flush()
            
            # Set number of retries to maximum number allowed
            retries = retry

            # Start the set number of retries to scrape the product information
            while retries > 0:
                try:

                    # Retrieve product information for current subcategory
                    products, product_count =  get_product_info(cod_postal, i, x, wait=prod_wait, headless=headless)

                    # Concatenate product information to previously retrieved information
                    product_info = pd.concat([product_info,products], ignore_index=True)

                    # Write product information to CSV file with unique session name in order to avoid losing information in case the scraping is interrupted.
                    product_info.to_csv(f'scraping_output/{session_name}.csv', index=False, mode='w', sep='~')

                    # Generate random wait time between specified minimum and maximum values
                    random_time = random.randint((wait_min*60*1000), (wait_max*60*1000)) /1000

                    # If random wait time is greater than specified maximum error wait time, generate random wait time within error range
                    if random_time > max_error_wait*60:
                        random_time = random.randint((((max_error_wait*60)-30)*1000), (((max_error_wait*60)+30)*1000)) /1000
                    
                    # Print message indicating successful retrieval of current subcategory's products
                    print(f"\n---------------\nTime:{round((time.time()-start_time)/60,2)}\nFinished '{x}' subcateogry succesfully. \n{product_count} products registered.\nWaiting {round(random_time/60,2)} minutes so that we don't get caught...\nCurrent size of data captured: {product_info.shape}\n---------------\n")
                    
                    # Wait for random wait time before moving on to next subcategory
                    time.sleep(random_time)
                    break

                # Error handling for failed product information retrieval
                except:

                    # Print the time at which the error occurred
                    print(f'\n\nTime: {round((time.time()-start_time)/60,2)}')

                    # Calculate a random amount of time to wait before retrying, based on the error count
                    random_time = random.randint((((e_wait_min*60)+(error_count*10))*1000), (((e_wait_max*60)+(error_count*10))*1000)) /1000
                    
                    # If the random time is greater than the maximum error wait time, cap it at the maximum
                    if random_time > max_error_wait*60:
                        random_time = random.randint((((max_error_wait*60)-30)*1000), (((max_error_wait*60)+30)*1000)) /1000
                    
                    # Increment the error count
                    error_count +=1

                    # If no more retries are left, add the subcategory to the list of missing subcategories and wait before breaking out of the for loop
                    if retries == 1:
                        print(f"!!! An error occurred in subcategory '{x}'... Again... Adding it to the list of missing subcategories...\Waiting {round(random_time/60,2)} minutes so that we don't get caught... ")
                        missed_subcat={}
                        missed_subcat["category"]=i
                        missed_subcat["subcategory"]=x
                        missing_subcats.append(missed_subcat)
                        time.sleep(random_time)
                        break

                    # Decrement the number of retries left and wait before retrying the current subcategory
                    retries -=1
                    print(f'!!! An error occurred in subcategory "{x}". Retrying in {round(random_time/60,2)} minutes...\n')
                    time.sleep(random_time)
    
    # Convert the list of missing subcategories to a DataFrame
    mising_subcategories = pd.DataFrame(missing_subcats)

    # Return the DataFrame containing all product information and the DataFrame containing missing subcategories
    return product_info, mising_subcategories