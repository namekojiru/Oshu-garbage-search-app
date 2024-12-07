import requests
from bs4 import BeautifulSoup
from peewee import *

db = SqliteDatabase('gomi.db')
class Oshu_gomi(Model):
    gomi = CharField()
    category = CharField()
    material = CharField(null = True)
    title = CharField()
    class Meta:
        database = db

def add_gomi(gomi,category,material,title):
    b = Oshu_gomi(gomi=gomi,category=category,material=material,title=title)
    b.save()

db.drop_tables([Oshu_gomi])
db.create_tables([Oshu_gomi])


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
        if material == " ":
            b = Oshu_gomi(gomi=item,category=category,material=None,title=table_a_title)
        else:
            b = Oshu_gomi(gomi=item,category=category,material=material,title=table_a_title)

        b.save()


    gomi_list.append(a)

for i in Oshu_gomi.select():
    print(i.material)