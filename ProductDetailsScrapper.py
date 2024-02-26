from flask import jsonify, request
import requests
from bs4 import BeautifulSoup
import re
from Constants import HEADERS
import time


def scrape_product_details():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL parameter is missing.'}), 400
    # try:
    #     response = requests.get(url, headers=HEADERS)
    #     response.raise_for_status()  # Check for any HTTP errors

    #     # Parse the HTML content with BeautifulSoup
    #     soup = BeautifulSoup(response.content, "html.parser")
    #     print("test", soup.prettify())
    #     user_input = input("Enter text to add to the input field: ")
    #     data = {
    #         "amzn": "TZQK7rGXCU07Pu0XV1YGiw==",
    #         "amzn-r": "/dp/B07G3ZNK4Y/",
    #         "field-keywords": user_input  # Replace with the text you want to add to the input field
    #     }
    #     response2 = requests.post(url, headers=HEADERS, data=data)
    #     response2.raise_for_status()  # Check for any HTTP errors
    #     soup2 = BeautifulSoup(response2.content, "html.parser")
    #     return soup2.prettify()

    #     # # Find the text input field by its ID, name, class, XPath, or other attributes
    #     # # For example, if the text input field has the ID 'captchacharacters', you can do the following:
    #     # text_input_field = soup.find("input", {"id": "captchacharacters"})

    #     # # Set the value of the text input field to 'ECYCCR'
    #     # print("test", soup.prettify())
    #     # if text_input_field:
    #     #     text_input_field.attrs['value'] = user_input

    #     # continue_shopping_button = soup.find("button", {"class": "a-button-text"})

    #     # if continue_shopping_button:
    #     #     # Send a new HTTP GET request to the action URL to continue shopping
    #     #     response = requests.get("/errors/validateCaptcha", headers=HEADERS)
    #     #     response.raise_for_status()  # Check for any HTTP errors
    #     #     soup = BeautifulSoup(response.content, "html.parser")
    #     #     return soup.prettify()

    #     # Optionally, you can parse the new page content to continue interacting with the website.


    #     # Optionally, you can extract the updated HTML content after setting the value
    #     return soup.prettify()

    #     # Now you can use the updated_html for further processing or POST it back to the server if needed
    #     # For example, you can use requests.post() to submit the updated form.

    # except requests.exceptions.RequestException as e:
    #     print(f"Error accessing the page: {e}")

    # except Exception as e:
    #     print(f"Error parsing the HTML: {e}")

    html = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(html.text, 'html.parser')
    # print("captured HTML: ", soup.prettify())  # Print the parsed HTML structure for debugging

    # Find title
    title_element = soup.find('span', {'id': 'productTitle'})
    title = title_element.text.strip() if title_element else ''

    # Find ASIN
    asin = None
    asin_th = soup.find('th', text=re.compile(r'ASIN', re.IGNORECASE))
    if asin_th:
        asin_td = asin_th.find_next_sibling(
            'td', class_='a-size-base prodDetAttrValue')
        asin = asin_td.text.strip() if asin_td else ''

    # Find Dimensions
    dimensions = None
    dimensions_th = soup.find(
        'th', text=re.compile(r'Dimensions', re.IGNORECASE))
    if dimensions_th:
        dimensions_td = dimensions_th.find_next_sibling(
            'td', class_='a-size-base prodDetAttrValue')
        dimensions = dimensions_td.text.strip() if dimensions_td else ''

    # Find Weight
    weight = ""
    weight_th = soup.find('th', text=re.compile(r'Weight', re.IGNORECASE))
    if weight_th:
        weight_td = weight_th.find_next_sibling(
            'td', class_='a-size-base prodDetAttrValue')
        weight = weight_td.text.strip() if weight_td else ''

    # Find Category Inheritance
    parent_categories = []
    links = soup.find_all('a', {'class': 'a-link-normal a-color-tertiary'})
    if links:
        for link in links:
            name = link.text.strip()
            href = link['href']
            category_id = href.split('node=')[-1]
            full_link = 'https://www.amazon.com' + href
            category = {
                'name': name,
                'link': full_link,
                'category_id': category_id
            }
            parent_categories.append(category)

    # Find Brand
    brand_tr = soup.find('tr', {'class': 'a-spacing-small po-brand'})
    brand = brand_tr.find(
        'span', {'class': 'a-size-base po-break-word'}).text.strip() if brand_tr else ''

    # Find subtitle
    subtitle_element = soup.find('div', id_='bylineInfo')
    if subtitle_element:
        subtitle_text = subtitle_element.text.strip()
        subtitle_link = subtitle_element.find('a')['href']
    else:
        subtitle_text = None
        subtitle_link = None
    subtitle = {
        'text': subtitle_text,
        'link': subtitle_link
    }

    # Find price
    price = ""
    price_element = soup.find('span', {'id': 'price_inside_buybox'})
    if price_element:
        price = price_element.text.strip()
    else:
        price_element = soup.find('span', class_='priceToPay')
        if price_element:
            price_text_element = price_element.findChild(
                'span', class_='a-offscreen')
            price = price_text_element.text.strip() if price_text_element else ''

    # Find rating
    rating = None
    rating_element = soup.find(
        'i', {'class': 'cm-cr-review-stars-spacing-big'})
    if rating_element:
        rating_text = rating_element.span.text.strip() if rating_element else None
        if rating_text:
            rating_arr = re.findall(r'(\d+(\.\d+)?)', rating_text)
            rating = float(rating_arr[0][0]) if rating_arr else None
    else:
        rating = None

    # Find ratings_total
    ratings_total = 0
    ratings_total_element = soup.find(
        "div", {'class': 'averageStarRatingNumerical'})
    if ratings_total_element:
        ratings_total_child = ratings_total_element.find(
            "span", {'class': 'a-size-base'})
        ratings_total_text = ratings_total_child.text.strip() if ratings_total_child else ''
        ratings_total = int(''.join(filter(str.isdigit, ratings_total_text)))

    # Find images
    imagesArr = re.findall('"hiRes":"(.+?)"', html.text)
    images = [{"link": link} for link in imagesArr]

    # Find main_image
    main_image = images[0]['link'] if images else ""

    # Find attributes
    attributes = []
    attributes_table = soup.find('table', class_='a-normal a-spacing-micro')
    if attributes_table:
        attributes_trs = attributes_table.find_all('tr')
        if attributes_trs:
            for attributes_tr in attributes_trs:
                attributes_td = attributes_tr.find_all('td')
                if len(attributes_td) == 2:
                    name_element = attributes_td[0].find(
                        'span', class_='a-size-base a-text-bold')
                    name = name_element.text.strip() if name_element else None

                    value_element = attributes_td[1].find(
                        'span', class_='a-size-base po-break-word')
                    if value_element:
                        value = value_element.text.strip() if value_element else None
                    else:
                        value_element = attributes_td[1].find(
                            'span', class_='a-truncate-full a-offscreen')
                        value = value_element.text.strip() if value_element else None
                    attributes.append({'name': name, 'value': value})

    # Find feature_bullets
    feature_bullets = []
    feature_bullets_element = soup.find('div', id='featurebullets_feature_div')
    if feature_bullets_element:
        feature_bullets_ul = feature_bullets_element.find(
            'ul', class_='a-unordered-list')
        feature_bullets = [li_element_li.text.strip()
                           for li_element_li in feature_bullets_ul.find_all('li')]

    # Find description
    description_element = soup.find('div', {'id': 'productDescription'})
    description = description_element.text.strip() if description_element else ''

    # Validate response
    isValid = price != '' and asin != '' and main_image != '' and title != ''

    data = {
        'message': 'product details scraped successfully',
        "product_id": asin,
        'title': title,
        'description': description,
        'link': url,
        'price': price,
        "main_image": main_image,
        'images': images,
        'rating': rating,
        "ratings_total": ratings_total,
        'parent_categories': parent_categories,
        'brand': brand,
        "dimensions": dimensions,
        "weight": weight,
        "attributes": attributes,
        "subtitle": subtitle,
        "feature_bullets": feature_bullets,
        "isValid": isValid,
    }
    return jsonify(data)
    # return soup.prettify()
