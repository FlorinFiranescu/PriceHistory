# PriceHistoryScrapper
This is a Python app that is able to extract the prices (base & reduced) of a product from an inputed link
Products.txt can be seen as a comma separated value file, on position one the link is expected, on 2 the percentage and on 3 the list of emails (separated by blank spaces)
The file will output/append the prices from the current day in an excel file. 
For each product, a new spreadsheet will be created.
Also, when the price of a product drops down by a certain percent, a notification will be sent through email.
The purpose of this app is to save the history of certain products in order to analyse how the prices are varying. Charts will be enabled in order to see how the prices vary. 
