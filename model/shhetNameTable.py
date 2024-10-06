from mongoengine import Document, StringField
from pydantic import BaseModel


class ShetTableName(Document):
    sheetname = StringField(required = True)
    
class CreateShhetData(BaseModel):
    sheetname: str
    