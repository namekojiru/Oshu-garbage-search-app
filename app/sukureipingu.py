import requests
from bs4 import BeautifulSoup
from peewee import *
from translate import Translator

def honyaku(gengo,bunn):
    translator = Translator(from_lang = "ja", to_lang = gengo)
    bunn_en = translator.translate(bunn)
    bunn_en_list = bunn_en.split("/")

    if len(bunn_en_list) == 1:
        return bunn_en_list[0]
    else:
        return bunn_en_list[1]


db = SqliteDatabase('gomi.db')
class Oshu_gomi(Model):
    gomi = CharField()
    category = CharField()
    material = CharField(null = True)
    title = CharField()
    class Meta:
        database = db
class Oshu_gomi_en(Model):
    gomi_en = CharField()
    category_en = CharField()
    material_en = CharField(null = True)
    title_en  = CharField()
    class Meta:
        database = db
class Oshu_gomi_zh(Model):
    gomi_zh = CharField()
    category_zh = CharField()
    material_zh = CharField(null = True)
    title_zh  = CharField()
    class Meta:
        database = db
class Oshu_gomi_ko(Model):
    gomi_ko = CharField()
    category_ko = CharField()
    material_ko = CharField(null = True)
    title_ko  = CharField()
    class Meta:
        database = db
db.drop_tables([Oshu_gomi,Oshu_gomi_zh,])
db.create_tables([Oshu_gomi,Oshu_gomi_zh,])


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
        #item_en = honyaku("en",item)
        item_zh = honyaku("zh",item)
        #item_ko = honyaku("ko",item)
        #item_title_en = item_en[0]
        item_title_zh = item_zh[0]
        #item_title_ko = item_ko[0]
        category = row.find_all("td")[1].get_text()
        #category_en = honyaku("en",category)
        category_zh = honyaku("zh",category)
        #category_ko = honyaku("ko",category)
        material = row.find_all("td")[0].get_text()
        #material_en = honyaku("en",material)
        material_zh = honyaku("zh",material)
        #material_ko = honyaku("ko",material)

         
        a.append([item, category, material])
        if material == " ":
            b = Oshu_gomi(gomi=item,category=category,material=None,title=table_a_title).save()
            #b = Oshu_gomi_en(gomi_en=item_en,category_en=category_en,material_en=None,title_en=item_title_en).save()
            b = Oshu_gomi_zh(gomi_zh=item_zh,category_zh=category_zh,material_zh=None,title_zh=item_title_zh).save()
            #b = Oshu_gomi_ko(gomi_ko=item_ko,category_ko=category_ko,material_ko=None,title_ko=item_title_ko).save()
        else:
            b = Oshu_gomi(gomi=item,category=category,material=material,title=table_a_title).save()
            #b = Oshu_gomi_en(gomi_en=item_en,category_en=category_en,material_en=material_en,title_en=item_title_en).save()
            b = Oshu_gomi_zh(gomi_zh=item_zh,category_zh=category_zh,material_zh=material_zh,title_zh=item_title_zh).save()
            #b = Oshu_gomi_ko(gomi_ko=item_ko,category_ko=category_ko,material_ko=material_ko,title_ko=item_title_ko).save()


    gomi_list.append(a)
