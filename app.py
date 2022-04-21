# doing necessary imports

from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo
import  pandas as pd
from sentiment import SentimentalAnalysis

app = Flask(__name__)
class Formatting_html:
    def __init__(self):
        pass

        # dictionary to gather data


    def get_main_html(self,base_url,search_string):
        search_url = f"{base_url}/search?q={search_string}"
        with uReq(search_url) as url:
            page = url.read()
        return bs(page,"html.parser")

    def get_product_links(self,flipkart_base_url,bigBoxes):
        temp = []
        for box in bigBoxes:
            try:
                temp.append((box.div.div.div.a.img['alt'],
                             flipkart_base_url + box.div.div.div.a["href"]))
            except:
                pass
        return temp

    def get_prod_HTML(self, productLink):
        prod_page = requests.get(productLink)
        return bs(prod_page.text, "html.parser")

    def get_final_data(self, commentbox=None, prodName=None, prod_price=None):
        '''
        this will append data gathered from comment box into data dictionary
        '''
        # append product name
        self.data["Product"].append(prodName)
        self.data["Price (INR)"].append(prod_price)
        try:
            # append Name of customer if exists else append default
            self.data["Name"].append(commentbox.div.div. \
                                     find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text)
        except:
            self.data["Name"].append('No Name')

        try:
            # append Rating by customer if exists else append default
            self.data["Rating"].append(commentbox.div.div.div.div.text)
        except:
            self.data["Rating"].append('No Rating')

        try:
            # append Heading of comment by customer if exists else append default
            self.data["Comment Heading"].append(commentbox.div.div.div.p.text)
        except:
            self.data["Comment Heading"].append('No Comment Heading')

        try:
            # append comments of customer if exists else append default
            comtag = commentbox.div.div.find_all('div', {'class': ''})
            self.data["Comment"].append(comtag[0].div.text)
        except:
            self.data["Comment"].append('')

    def get_data_dict(self):
        '''
        returns collected data in dictionary
        '''
        return self.data

@app.route('/',methods=['POST','GET'])
def index():
    if request.method == 'POST':
        searchString = request.form['content'].replace(" ","")
        sentiments = SentimentalAnalysis()

        try:
            dbConn = pymongo.MongoClient("mongodb://localhost:27017/")
            db = dbConn['userReviews']
            reviews = list(db[searchString].find({}))

            if len(list(reviews))  > 0:
                return render_template('results.html',reviews=reviews)
            else:

                base_url = "https://www.flipkart.com"
                get_data = Formatting_html()

                flipkart_html = get_data.get_main_html(base_url, searchString)
                bigboxes = flipkart_html.find_all("div", {"class": "_1AtVbE col-12-12"})
                table = db[searchString]
                reviews = []

                product_links = get_data.get_product_links(base_url,bigboxes)
                for prodName, productLink in product_links[:4]:
                    prod_links = get_data.get_prod_HTML(productLink)
                    # for prod_HTML in prod_links:

                    comment_boxes = prod_links.find_all('div', {'class': '_16PBlm'})  # _3nrCtb


                    prod_price = prod_links.find_all('div', {"class": "_30jeq3 _16Jk6d"})[0].text
                    prod_price = float((prod_price.replace("₹", "")).replace(",", ""))
                    # iterate over comment boxes to extract required data
                    for commentbox in comment_boxes:
                                # prpare final data
                        Product = prodName
                        Price_INR = prod_price
                        try:
                                    # append Name of customer if exists else append default
                            Name = commentbox.div.div. \
                                find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
                        except:
                            Name = 'No Name'

                        try:
                                    # append Rating by customer if exists else append default
                            Rating = commentbox.div.div.div.div.text
                        except:
                            Rating = 'No Rating'

                        try:
                                    # append Heading of comment by customer if exists else append default
                             Comment_Heading = commentbox.div.div.div.p.text
                        except:
                             Comment_Heading = 'No Comment Heading'

                        try:
                                    # append comments of customer if exists else append default
                             comtag = commentbox.div.div.find_all('div', {'class': ''})
                             Comment = comtag[0].div.text
                             if len(Comment) > 0:
                                 sentiment_reviews = sentiments.analyse_data(Comment)
                             else:
                                 pass

                        except:
                              Comment = ""






                        mydict = {"Product": searchString, "product price":Price_INR, "Name": Name, "Rating": Rating, "CommentHead": Comment_Heading,
                                      "Comment": Comment,"Sentiment":sentiment_reviews}
                        x = table.insert_one(mydict)
                        reviews.append(mydict)
                    return render_template('results.html', reviews=reviews)
        except:
            return 'something is wrong'

    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(port=8000,debug=True)