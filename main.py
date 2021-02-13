import requests # for making standard html requests
from bs4 import BeautifulSoup # magical tool for parsing html data
import time
import pandas as pd
from openpyxl import load_workbook
from datetime import date
from openpyxl import Workbook
import os
import json # for parsing data
from pandas import DataFrame as df # premier library for data organization



def request2BfSoupObj(root_url, url_path):
    page = requests.get("{}{}".format(root_url,url_path))
    print("\nRequesting Page URL: {}{}\n".format(root_url,url_path))
    if page.status_code == 200: print("\nRequest OK: Status code {}\n".format(page.status_code))
    else:
        print("\nError with the request:response: {}\n".format(page.status_code))
        raise ConnectionError("\nError with the request:response: {}\n".format(page.status_code))
        return 0
    page.encoding = 'ISO-885901'
    soup = BeautifulSoup(page.text, 'html.parser')      #using the html parser, easier to search in browser
    return soup

def productPrice(soup, product_title):
    #get main-container-inner
    productPriceTag = soup.body.find("div", class_="main-container-inner")
    #go to product-page-pricing
    productHighlight = productPriceTag.find("div", class_="product-page-pricing")
    # extract 'new-price' -> so-called reduced one in some cases
    productNewPrice = productHighlight.find("p", class_="product-new-price")

    # extract main price, it is the pos 0 in the list of contents
    mainNewPrice = productNewPrice.contents[0].strip()

    # extract the secondary price, it is under an <sup> tag
    secNewPrice = productNewPrice.sup.string

    # extract 'old-price' -> so-called unreduced one
    # careful how we treat it, it may exist => extract, it may not exist => None => ==new-price
    if (productHighlight.find("p", class_="product-old-price") is None):
        mainOldPrice = mainNewPrice
        secOldPrice  = secNewPrice
    else:
        productOldPrice = productHighlight.find("p", class_="product-old-price")
        mainOldPrice = productOldPrice.s.contents[0]
        secOldPrice  = productOldPrice.s.sup.string


    if (mainNewPrice is not None and secNewPrice is not None) and (mainOldPrice is not None and secOldPrice is not None):
        formatedProudctBasePrice    = "{},{}".format(mainOldPrice, secOldPrice)
        formatedProudctReducedPrice = "{},{}".format(mainNewPrice, secNewPrice)
        return formatedProudctBasePrice, formatedProudctReducedPrice
    else:
        raise ValueError("\nPrice could not be extracted for product {}\n".format(product_title))
        print(productHighlight)
        print(mainNewPrice, secNewPrice)
        print(mainOldPrice, secOldPrice)
        return 0

def readProductLists(fileList):
    productList = []
    try:
        with open(fileList, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if(line == ""):
                    continue
                productList.append(line)
            print(productList)
    except Exception as e:
        print(e)
    return productList

def format_title(title):
    #make sure that these chars are not in the title, else excel will error it out
    for ch in ['\\', '/', '*', '?' , ':' , '[' , ']']:
        if ch in title:
            title = title.replace(ch, ' ')
    if len(title) > 30:
        title = title[:30]
    return title

def main():
    #load the list of products
    #opening spreadsheet
    filename = "Prices.xlsx"
    today = date.today()
    today = today.strftime("%B %d, %Y")
    if not (os.path.exists(filename)):
        print("Creating a new excel file named : {}".format(filename))
        workbook = Workbook()
        sheet = workbook.active

        workbook.save(filename=filename)

    excel_file = load_workbook(filename=filename)

    productList = readProductLists("Products.txt")
    if len(productList) == 0:
        exit("Product list is empty. Exiting...")
    for eMagProduct in productList:
        soup = BeautifulSoup()
        emagRoot    = "https://www.emag.ro/"
        URL = emagRoot + eMagProduct


        try:
            soup = request2BfSoupObj(emagRoot, eMagProduct)
        except Exception as e:
            print(e)
            print("Bad request response. Next product!")
            continue
        try:
            title = soup.title.string
            basePrice, reducedPrice = productPrice(soup, title)
            print("URL                  : {}".format(URL))
            print("Product name         : {}\nProduct base price   : {}\nProduct reduced price: {}".format(title, basePrice, reducedPrice))
        except Exception as e:
            print(e)
            print("Continuing to next product")
            continue

        title = format_title(title)
        if title not in excel_file.sheetnames:
            excel_file.create_sheet(title)
            excel_file[title].append(['Date', 'Link', 'BasePrice', 'ReducedPrice', 'Email_recip'])
            excel_file.save(filename)
            excel_file = load_workbook(filename=filename)
        productSheet = excel_file[title]
        if productSheet['A{}'.format(productSheet.max_row)].value == today:
            print("Same day")
        else:
            productSheet.append([today, URL, basePrice, reducedPrice, "florin.firanescu@gmail.com"])
        time.sleep(2)
    excel_file.save(filename)

if __name__ == "__main__":
    main()