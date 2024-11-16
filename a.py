from peewee import *

db = SqliteDatabase('gomi.db')
class Oshu_gomi(Model):
    gomi = CharField()
    category = CharField()
    material = CharField()
    title = CharField()
    class Meta:
        database = db

title = []

for i in Oshu_gomi.select():
    if not i.title in title:
        title.append(i.title)


a = ""

while not (len(a) == 1 and a in title):
    a = str(input("文字"))

gomi_a = Oshu_gomi.filter(Oshu_gomi.title == a).execute()
for s in gomi_a:
    if s.material == None :
        print(f"{s.gomi}")
    else:
        print(f"{s.gomi}[{s.material}]")

