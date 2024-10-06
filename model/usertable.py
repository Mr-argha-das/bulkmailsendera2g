from mongoengine import Document, StringField
from pydantic import BaseModel

class UserTable(Document):
    name = StringField(required = True)
    email = StringField(required=True)
    password = StringField(required=True)

class UserCreateModel(BaseModel):
    name: str
    email:str
    password:str
    
class LoginModel(BaseModel):
    email: str
    password: str