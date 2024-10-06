import requests
from bs4 import BeautifulSoup

# スクレイピングでHTMLを取得
html_content = requests.get("https://www.city.oshu.iwate.jp/soshiki/5/1051/2/1/246.html")

# 取得したHTMLをBeautifulSoupで読み込み
soup = BeautifulSoup(html_content.content, "html.parser")

# tableタグを取得（0番目が「あ」）
table = soup.find_all("table")
table_a = table[0]

# captionタグから「あ」という文字を取得
table_a_title = table_a.find("caption").get_text()

# tableタグのthタグを取得
# 0番目が「品目」、2番めが「排出区分」
table_a_th = table_a.find_all("th")
table_a_th_hinmoku = table_a_th[0].get_text()
table_a_th_kubun = table_a_th[2].get_text()

# tableタグのtbodyタグを取得
table_a_tbody = table_a.find("tbody").find_all("tr")

# 空のリストを作成
gomi_list = []
gomi_list.append(table_a_title)

# tbodyの中身を取り出して、ほしい形のリストを作成
for row in table_a_tbody:
    item = row.find("th").get_text()
    category = row.find_all("td")[1].get_text()
    gomi_list.append([[table_a_th_hinmoku, item], [table_a_th_kubun, category]])

print(gomi_list)