from peewee import *
from datetime import date

db = SqliteDatabase('rirekis.db')


class Rireki(Model):
    gomi = CharField()

    class Meta:
        database = db

a = Rireki(gomi = "a")
a.save()

db.create_tables([Rireki])