from peewee import SqliteDatabase, Model, CharField, IntegerField, BooleanField
from db_connection import db


class Apartment(Model):
    external_id = CharField()
    add_url = CharField()
    title = CharField()
    price = IntegerField()
    agency_lent = BooleanField(default=True)
    image_url = CharField()
    region = CharField()

    class Meta:
        database = db


db.create_tables([Apartment])