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

To scrape all the products from the Mercadona website, open [label](mercadona/scraping/mercadona_scraper.ipynb) and follow the written description and run code cells. Heres a preview of the script running and fetching categories and subcategories:
https://user-images.githubusercontent.com/62567171/225653414-f38e57ec-38df-484a-982d-3c37554cc137.mov

With the same command, after fetching the full list of categories and subcategories, the scrapper will start fetching all the information for every product.
https://user-images.githubusercontent.com/62567171/225653723-4e04dc71-e00b-41f1-9659-4dc28eb7fd31.mov

