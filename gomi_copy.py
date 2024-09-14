import requests
from bs4 import BeautifulSoup
import pickle

class Garbage:
    def Oshu_garbage(self):

        self.load_url = "https://www.city.oshu.iwate.jp/soshiki/5/1051/2/1/246.html"
        self.html = requests.get(self.load_url)
        self.soup = BeautifulSoup(self.html.content,"html.parser")
        self.gomi = self.soup.find(class_="wysiwyg")

        self.list = []
        self.body_list = []

        self.Oshu_process = {}
        for element in self.soup.find("thead"):
            self.list.append(element.text.split("\n"))
        for element in self.soup.find("tbody"):
            self.body_list.append(element.text.split("\n"))

        test = [[
            "あ",
            ["育苗箱", "収集しません"],
            ["衣装ケース", "燃えるごみ"],
            ],
        
            [
            "か",
            ["か","収集しません"],
            ["き","燃えるゴミ"],

            ],
        ["が"],
        ["さ"],
        ["ざ"],
        ["た"],
        ["だ"],
        ["な"],
        ["は"],
        ["ぱ"],
        ["ば"],
        ["ま"],
        ["や"],
        ["ら"],
        ["わ"],
        ]
        

        return test
        return self.list,self.body_list
    
a = Garbage()
print(a.Oshu_garbage())