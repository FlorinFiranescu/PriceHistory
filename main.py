import requests # for making standard html requests
from bs4 import BeautifulSoup # magical tool for parsing html data
import time
import pandas as pd
from openpyxl import load_workbook
from datetime import date
from openpyxl import Workbook
import os
import smtplib
from email.mime.text import MIMEText
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
                if (line == ""):
                    continue
                URL, perc, email_recips = line.split(',')
                recips = email_recips.split()
                tempProduct = product_class(URL, perc, recips)

                tempProduct.print_attrs()
                productList.append(tempProduct)
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


def getMinRowValue(Sheet, column):
    list_of_prices = []
    for cell in Sheet[column]:
        if cell.value == "ReducedPrice" or cell.value is None: continue
        value = floatRepr(cell.value)
        list_of_prices.append(value)
    return min(list_of_prices)

def format_title(title):
    #make sure that these chars are not in the title, else excel will error it out
    for ch in ['\\', '/', '*', '?' , ':' , '[' , ']']:
        if ch in title:
            title = title.replace(ch, ' ')
    if len(title) > 30:
        title = title[:30]
    return title

def email_nofifier(usr, pswd, recip, body, subject):
    #first customize the email
    user = usr
    password = pswd
    #sent_to is a list, we need it in a string format of recip1, recip2, etc...
    #subject = "Test email"
    email = MIMEText("{}".format(body))
    sender = usr
    recipients = recip
    email['Subject'] = subject
    email['From'] = sender
    email['To'] = ", ".join(recipients)


    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(user, password)
        server.sendmail(sender, recipients, email.as_string())
        server.close()

        print('Email sent!')
    except Exception as e:
        print("Something went wrong!")
        print(e)

def calculate_percDecrease(prev_price, actual_price):
    if(prev_price == 0 or actual_price == 0):
        raise ValueError("\nOne of the prices is null:\n{}\n{}\n".format(prev_price, actual_price))
    prev = float(prev_price)
    actual = float(actual_price)
    diff = prev - actual
    return (diff/actual)*100

def floatRepr(string):
    myString = string.replace('.', '')
    myString = myString.replace(',', '.')
    return float(myString)

class product_class:

    def __init__(self, URL, percentage, email_recips):
        self.URL = URL
        self.percentage = percentage
        self.email_recips = email_recips
        self.prev_price = ""
        self.actual_reducedPrice = ""
        self.actual_basePrice    = ""
        self.reduction = 0
        self.email_triggered = 0

    def print_attrs(self):
        print('URL: {}\nperc: {}\n emails: {}\n'.format(self.URL, self.percentage, self.email_recips))

    def getSubject(self):
        return "Florin here. Good news, one of you wish-list products has been reduced by {:.2f}%!".format(self.reduction)

    def getBody(self, title, URL):
        body    = '''
  Hello, the product entitled {} has been reduced by {:.2f}%.
This URL will get you directly to it: {}
The price when we first started to monitor it was   : {}
The current reduced price is                        : {}
Grab it as fast as you can, hope you will like it :)
PS: thank you for letting me help you

  Best regards,
    Florin F.
        '''.format(title, self.reduction, URL, self.prev_price, self.actual_reducedPrice)
        return body


    def calculatePercentage(self):
        #first format our prices
        prev_price = floatRepr(self.prev_price)
        actual_price = floatRepr(self.actual_reducedPrice)

        if(prev_price == 0 or actual_price == 0):
            raise ValueError("\nOne of the prices is null:\n{}\n{}\n".format(self.prev_price, self.actual_reducedPrice))
        diff = prev_price - actual_price
        self.reduction = (diff/actual_price)*100
        return self.reduction

def main():
    #load the list of products
    #opening spreadsheet
    excelName = "Prices.xlsx"
    today = date.today()
    today = today.strftime("%B %d, %Y")
    bot_user, bot_pswd = getCredentials()
    #email_nofifier(bot_user, bot_pswd, ["florin.firanescu@gmail.com"])
    #print(calculate_percDecrease(0, 89))
    #exit()
    if not (os.path.exists(excelName)):
        print("Creating a new excel file named : {}".format(excelName))
        workbook = Workbook()
        sheet = workbook.active

        workbook.save(filename=excelName)

    excel_file = load_workbook(filename=excelName)

    productList = readProductLists("Products.txt")

    if len(productList) == 0:
        exit("Product list is empty. Exiting...")
    for pageProduct in productList:
        soup = BeautifulSoup()
        pageRoot    = "https://www.emag.ro/"
        URL = pageRoot + pageProduct.URL


        try:
            soup = request2BfSoupObj(pageRoot, pageProduct.URL)
        except Exception as e:
            print(e)
            print("Bad request response. Next product!")
            continue
        try:
            title = soup.title.string
            basePrice, reducedPrice = productPrice(soup, title)
            pageProduct.actual_basePrice    = basePrice
            pageProduct.actual_reducedPrice = reducedPrice
            print("URL                  : {}".format(URL))
            print("Product name         : {}\nProduct base price   : {}\nProduct reduced price: {}".format(title, pageProduct.actual_basePrice, pageProduct.actual_reducedPrice))
        except Exception as e:
            print(e)
            print("Continuing to next product")
            continue
        true_title = title
        title = format_title(title)
        if title not in excel_file.sheetnames:
            excel_file.create_sheet(title)
            excel_file[title].append(['Date', 'Link', 'BasePrice', 'ReducedPrice', 'Email_recip', 'Email_notification'])
            excel_file.save(excelName)
            excel_file = load_workbook(filename=excelName)
        productSheet = excel_file[title]
        pageProduct.prev_price = productSheet['D2'].value
        print(true_title)
        if productSheet['A{}'.format(productSheet.max_row)].value == today:
            print("Same day")
        else:
            if (float(pageProduct.calculatePercentage()) > float(pageProduct.percentage)
                    and getMinRowValue(productSheet, 'D') > floatRepr(pageProduct.actual_reducedPrice)):
                email_nofifier(bot_user, bot_pswd, pageProduct.email_recips, pageProduct.getBody(true_title, URL), pageProduct.getSubject())
                pageProduct.email_triggered = 1
            recips =  ', '.join(pageProduct.email_recips)
            print(recips)
            productSheet.append([today, URL, pageProduct.actual_basePrice, pageProduct.actual_reducedPrice, recips, pageProduct.email_triggered ])
        time.sleep(2)
    excel_file.save(excelName)

if __name__ == "__main__":
    main()