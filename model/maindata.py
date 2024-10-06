from mongoengine import Document, StringField
from pydantic import BaseModel


class MainData(Document):
    tableid = StringField(requried = True)
    name = StringField(required=True)
    email = StringField(required=True)
    status = StringField(required=True)