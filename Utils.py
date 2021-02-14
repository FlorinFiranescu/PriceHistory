def calculate_percDecrease(prev_price, actual_price):
    if(prev_price == 0 or actual_price == 0):
        raise ValueError("\nOne of the prices is null:\n{}\n{}\n".format(prev_price, actual_price))
    prev = float(prev_price)
    actual = float(actual_price)
    diff = prev - actual
    return (diff/actual)*100

def getMinRowValue(Sheet, column):
    list_of_prices = []
    for cell in Sheet[column]:
        if cell.value == "ReducedPrice" or cell.value is None: continue
        value = floatRepr(cell.value)
        list_of_prices.append(value)
    return min(list_of_prices)

def floatRepr(string):
    myString = string.replace('.', '')
    myString = myString.replace(',', '.')
    return float(myString)

def formatTitle(title):
    #make sure that these chars are not in the title, else excel will error it out
    for ch in ['\\', '/', '*', '?' , ':' , '[' , ']']:
        if ch in title:
            title = title.replace(ch, ' ')
    if len(title) > 30:
        title = title[:30]
    return title

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
