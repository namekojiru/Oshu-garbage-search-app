import requests
from bs4 import BeautifulSoup
class Garbage:
    def Oshu_garbage(self):

        self.load_url = "https://www.city.oshu.iwate.jp/soshiki/5/1051/2/1/246.html"
        self.html = requests.get(self.load_url)
        self.soup = BeautifulSoup(self.html.content,"html.parser")
        self.gomi = self.soup.find(class_="table-wrapelper")
        self.list = []

        self.Oshu_process = {}
        for element in self.soup.find_all("tr"):

            self.list.append(element.text)
        for kesu in self.list:
            if "\xa0" in kesu.split("\n")[2]:
                self.Oshu_process[kesu.split("\n")[1]]=kesu.split("\n")[3]
            else:
                self.Oshu_process[kesu.split("\n")[1]+'('+kesu.split("\n")[2]+')']=kesu.split("\n")[3]
        del self.Oshu_process['品目(材質・素材)']

        return self.Oshu_process
    
a = Garbage()
a.Oshu_garbage()