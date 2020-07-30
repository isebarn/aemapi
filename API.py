from flask import Flask, jsonify, request

from flask_cors import CORS, cross_origin
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
import os
from time import sleep

JOMAFA = "https://www.jomafa.com/busqueda?controller=search&s={}"
AMAZON = "https://www.amazon.es/s?k={}"
app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app, resources={r"*": {"origins": os.environ.get('WEB')}})

def jomafa(search):
  driver = webdriver.Remote(os.environ.get('BROWSER'), DesiredCapabilities.FIREFOX)

  search_term = search
  search_term = '+'.join(search.split(' '))

  driver.get(JOMAFA.format(search_term))
  items = driver.find_elements_by_xpath("//div[@class='products row products-grid']/div")

  results = []
  for item in items[0:10]:
    img = item.find_element_by_xpath(".//img")
    src = img.get_attribute("src")

    description_div = item.find_element_by_xpath(".//div[@class='product-description']")

    title_h3 = description_div.find_element_by_xpath(".//h3[@class='h3 product-title']")
    title = title_h3.text

    url_a = title_h3.find_element_by_xpath(".//a")
    url = url_a.get_attribute('href')

    price_span = description_div.find_element_by_xpath(".//span[@class='product-price']")
    price = price_span.text

    result = {}
    result['src'] = src
    result['title'] = title
    result['url'] = url
    result['price'] = price

    results.append(result)

  driver.close()

  return results

def amazon(search):
  driver = webdriver.Remote(os.environ.get('BROWSER'), DesiredCapabilities.FIREFOX)

  search_term = search
  #search_term = '+'.join(search.split(' '))

  driver.get(AMAZON.format(search_term))

  results = []
  for idx in range(1,11):
    try:
      item = driver.find_element_by_xpath("//div[@data-index='{}']".format(idx))

      img = item.find_element_by_xpath(".//img")
      src = img.get_attribute('src')

      title_a = item.find_element_by_xpath(".//h2/a[@href]")
      title = title_a.text
      url = title_a.get_attribute('href')

      price_span = item.find_element_by_xpath(".//span[@class='a-price']")
      price = price_span.text

      result = {}
      result['src'] = src
      result['title'] = title
      result['url'] = url
      result['price'] = price

      results.append(result)

    except Exception as e:
      pass
      
  driver.close()

  return results

@app.route('/jomafa')
def jomafa_endpoint():
  search = request.args.get('search', default = '', type = str)
  return jsonify(jomafa(search))

@app.route('/amazon')
def amazon_endpoint():
  search = request.args.get('search', default = '', type = str)
  return jsonify(amazon(search))

if __name__ == "__main__":
  search = "prensa hidraulica 12 toneladas"

  for x in amazon(search):
    print(x)



