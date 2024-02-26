from flask import jsonify, request
import requests
from bs4 import BeautifulSoup
import re
from Constants import HEADERS
import time
from urllib.parse import unquote


def scrape_products():
    # url = 'https://www.amazon.com/s?rh=n:21179674011&page=3'
    url = unquote(request.args.get('url'))
    if not url:
        return jsonify({'error': 'URL parameter is missing.'}), 400

    print("captured url: ", url, request)
    html = requests.get(url, headers=HEADERS)
    time.sleep(5)  # Adjust the sleep duration as needed
    soup = BeautifulSoup(html.text, 'html.parser')

    # Use regular expression to extract the node ID
    parent_category_id = ''
    pattern = r"rh=n:(\d+)"
    match = re.search(pattern, url)
    if match:
        parent_category_id = match.group(1)

    # Products
    products = []
    product_elements = soup.find_all('div', class_='s-asin')
    print("product: ", product_elements)

    for product_element in product_elements:
        # Find product_id
        product_id = product_element['data-asin']

        # Check if product with same product_id already exists
        if any(product['product_id'] == product_id for product in products):
            continue

        # Find title
        title_element = product_element.select_one(
            '.a-color-base.a-text-normal')
        title = title_element.text.strip() if title_element else ''

        # Find thumbnail
        thumbnail_element = product_element.find('img', class_='s-image')
        thumbnail = thumbnail_element['src'] if thumbnail_element else ''

        # Find price
        price_element = product_element.find('span', class_='a-offscreen')
        price = price_element.text.strip() if price_element else ''

        # Find rating
        rating_text = ''
        total_ratings = 0
        rating_element = product_element.select_one('.a-icon-alt')
        rating_text = rating_element.text.strip() if rating_element else ''
        total_ratings_element = product_element.select_one(
            'span.a-size-base.s-underline-text')
        print("total_ratings_element: ", total_ratings_element)
        total_ratings = total_ratings_element.text.strip() if total_ratings_element else ''

        # Extract numeric value from total_ratings
        total_ratings = re.sub('[^0-9]', '', total_ratings)
        rating = {
            'rating': rating_text,
            'total_ratings': total_ratings,
        }

        if (product_id == '' or thumbnail == '' or price == '' or title == ''):
            continue

        product = {
            'product_id': product_id,
            'title': title,
            'thumbnail': thumbnail,
            'price': price,
            'rating': rating,
        }
        products.append(product)

    data = {
        'message': 'Products scraped successfully',
        'link': url,
        'parent_category_id': parent_category_id,
        'product_results': products,
        # 'html': soup.prettify(),
    }
    return jsonify(data)
    return soup.prettify()
