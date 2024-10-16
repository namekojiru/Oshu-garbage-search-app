from peewee import *
import datetime
db = SqliteDatabase('rirekis.db')


class Rireki(Model):
    gomi = CharField()
    time = DateTimeField()

    class Meta:
        database = db

def add_rireki(gomi):
    dt_now = datetime.datetime.now()
    a = Rireki(gomi = gomi, time = dt_now)
    a.save()
#db.drop_tables([Rireki])
#db.create_tables([Rireki])
if input("追加するか") == "y":
    gomi = input("ゴミ")
    add_rireki(gomi)
for i in Rireki.select():
    print(i.gomi,i.time)