from Utils import floatRepr

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
