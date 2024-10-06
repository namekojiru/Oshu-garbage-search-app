import requests
from bs4 import BeautifulSoup
import pickle

# スクレイピングでHTMLを取得
html_content = requests.get("https://www.city.oshu.iwate.jp/soshiki/5/1051/2/1/246.html")

# 取得したHTMLをBeautifulSoupで読み込み
soup = BeautifulSoup(html_content.content, "html.parser")

# tableタグを取得
table = soup.find_all("table")

# 空のリストを作成
gomi_list = []

for i in table:
    table_a = i

    # captionタグから最初の文字を取得
    table_a_title = table_a.find("caption").get_text()



    # tableタグのtbodyタグを取得
    table_a_tbody = table_a.find("tbody").find_all("tr")

    a = []

    a.append(table_a_title)


    # tbodyの中身を取り出して、ほしい形のリストを作成
    for row in table_a_tbody:
        item = row.find("th").get_text()
        category = row.find_all("td")[1].get_text()
        material= row.find_all("td")[0].get_text()
         
        a.append([item, category, material])

    gomi_list.append(a)


with open("linklist.txt", mode="wb") as f:
    pickle.dump(gomi_list,f)
for i in gomi_list:
    for f in i:
        if "か" in f[0]:
            if type(f) != str:
                print(f[2])
