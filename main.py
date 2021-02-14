import requests # for making standard html requests
from bs4 import BeautifulSoup # magical tool for parsing html data
import time
import pandas as pd
from openpyxl import load_workbook
from datetime import date
from openpyxl import Workbook
import os
import smtplib
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
def getCredentials():
    try:
        with open("credentials.auth", 'r') as creds:
            string = creds.readlines()
        usr = string[0].strip()
        pswd = string[1].strip()
        return usr, pswd
    except Exception as e:
        print("Exception during geting the credentials:")
        print(e)


def format_title(title):
    #make sure that these chars are not in the title, else excel will error it out
    for ch in ['\\', '/', '*', '?' , ':' , '[' , ']']:
        if ch in title:
            title = title.replace(ch, ' ')
    if len(title) > 30:
        title = title[:30]
    return title

def email_nofifier(usr, pswd, recieps):
    #first customize the email
    user = usr
    password = pswd
    sent_from = usr
    #sent_to is a list, we need it in a string format of recip1, recip2, etc...
    sent_to = ", ".join(recieps)
    subject = "Test email"
    body = "Ello'"
    email_text = """\
Subject: {}

{}""".format(subject, body)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(user, password)
        server.sendmail(sent_from, sent_to, email_text)
        server.close()

        print('Email sent!')
    except Exception as e:
        print("Something went wrong!")
        print(e)


def main():
    #load the list of products
    #opening spreadsheet
    excelName = "Prices.xlsx"
    today = date.today()
    today = today.strftime("%B %d, %Y")
    bot_user, bot_pswd = getCredentials()
    #email_nofifier(bot_user, bot_pswd, ["florin.firanescu@gmail.com"])

    if not (os.path.exists(excelName)):
        print("Creating a new excel file named : {}".format(excelName))
        workbook = Workbook()
        sheet = workbook.active

        workbook.save(filename=excelName)

    excel_file = load_workbook(filename=excelName)

    productList = readProductLists("Products.txt")
    #exit
    #exit()
    if len(productList) == 0:
        exit("Product list is empty. Exiting...")
    for pageProduct in productList:
        soup = BeautifulSoup()
        pageRoot    = "https://www.emag.ro/"
        URL = pageRoot + pageProduct


        try:
            soup = request2BfSoupObj(pageRoot, pageProduct)
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
            excel_file.save(excelName)
            excel_file = load_workbook(filename=excelName)
        productSheet = excel_file[title]
        if productSheet['A{}'.format(productSheet.max_row)].value == today:
            print("Same day")
        else:
            productSheet.append([today, URL, basePrice, reducedPrice, "florin.firanescu@gmail.com"])
        time.sleep(2)
    excel_file.save(excelName)

if __name__ == "__main__":
    main()