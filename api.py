from flask import Flask
from ProductsScrapper import scrape_products
from ProductDetailsScrapper import scrape_product_details

app = Flask(__name__)


@app.route('/scrapeProducts', methods=['GET'])
def get_scrape_products():
    # Search text scrap:
    # https://www.amazon.com/s?k=laptop+bag&page=2
    # http://127.0.0.1:5000//scrapeProducts?url=https://www.amazon.com/s?rh=n%3A16225009011%26page=2
    # http://127.0.0.1:5000//scrapeProducts?url=https://www.amazon.com/s?rh=n:21179674011%26page=2
    response = scrape_products()
    return response


@app.route('/scrapeProductDetails', methods=['GET'])
def get_scrape_product_details():
    # http://127.0.0.1:5000//scrapeProductDetails?url=https://www.amazon.com/dp/B06XJ9CYB2/
    response = scrape_product_details()
    return response


if __name__ == '__main__':
    app.run(debug=True)
