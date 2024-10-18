from mongoengine import Document, StringField
from pydantic import BaseModel


class ShetTableName(Document):
    sheetname = StringField(required = True)
    date = StringField(Required=False)
    
class CreateShhetData(BaseModel):
    sheetname: str
    