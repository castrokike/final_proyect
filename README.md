# Mercadona Price Tracker
![Mercadona logo](media/Logo_Mercadona_(color-300-alpha).png)
#### IronHack Final Project
### Andrés Castro

The Mercadona Price Tracker is a Python-based web scraper that allows users to track the prices of products sold by the Spanish supermarket chain, Mercadona. This project consists of two main parts: scraping all the products in the Mercadona website and extracting the user's order history to visualize price changes per product.

## Features
 - Scrapes all products from the Mercadona website along with their details (name, price, category, subcategory, etc.).
 - Extracts the user's order history from the Mercadona website, which includes the list of products ordered along with their corresponding price and quantity.
    - Assigns product codes to the products in the user's order history by matching them with the codes of the scraped products.
    - Calculates the price per unit for each product in the user's order history.
 - Visualizes the price changes per product over time.


## Usage

### Scraping Products

To scrape all the products from the Mercadona website, open [mercadona_scraper.ipynb](mercadona/scraping/mercadona_scraper.ipynb) and follow the written description and run code cells. Heres a preview of the script running and fetching categories and subcategories:

https://user-images.githubusercontent.com/62567171/225653414-f38e57ec-38df-484a-982d-3c37554cc137.mov

With the same command, after fetching the full list of categories and subcategories, the scrapper will start fetching all the information for every product.

https://user-images.githubusercontent.com/62567171/225653723-4e04dc71-e00b-41f1-9659-4dc28eb7fd31.mov

This will create a CSV file containing all the products and their details in the [scraping_output](mercadona/scraping/scraping_output) directory.

### Extracting User Order History
To extract the user's order history from the Mercadona website, open [mercadona_order_history.ipynb](mercadona/order_history/mercadona_order_history.ipynb) and follow the written description and run code cells. Since this process contains sensible user information, we won't show a video preview. 

This jupyter notebook will create a CSV file containing the user's order history in the [order_history/outputs](mercadona/order_history/outputs) directory.

### Uploading to SQL and process
To upload all the collected information to SQL to generate the price variations, open [uploading_to_sql.ipynb](sql/uploading_to_sql.ipynb) and follow the written description and run code cells. This will upload both sets of data (order history and scraped product information) to SQL and then query both tables to generate the percentage of price increase per product.