from email.mime.multipart import MIMEMultipart
from fastapi import FastAPI, Request, Response
from fastapi import FastAPI, Form,  FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from fastapi.responses import RedirectResponse
import os
from model.shhetNameTable import ShetTableName, CreateShhetData
from model.usertable import UserCreateModel, LoginModel, UserTable
from model.maindata import MainData
import csv
from io import StringIO
import logging
from mongoengine import connect
connect(db="MailData", host="mongodb+srv://avbigbuddy:nZ4ATPTwJjzYnm20@cluster0.wplpkxz.mongodb.net/MailData")
from bson import ObjectId
import json
app = FastAPI()
app.add_middleware(
    CORSMiddleware,  # Add the middleware class here
    allow_origins=["*"],  # Allows all origins, replace with specific origins as needed
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

logging.basicConfig(filename='email_open_log.txt', level=logging.INFO)

@app.get("/track_open")
async def track_open(request: Request, email: str):
    # Log that the email has been opened
    logging.info(f"Email opened by: {email}, IP: {request.client.host}")
    findData = MainData.objects(email__icontains = email).first()
    findData.status = "Open"
    findData.save()
    # Serve a 1x1 transparent pixel
    with open("static/image.png", "rb") as image:
        return Response(content=image.read(), media_type="image/png")
    
    
@app.get("/download-csv/{tableid}")
async def download_csv(tableid: str):
    # Query all the data from MainData collection
    data = MainData.objects(tableid=tableid).all()

    # Create an in-memory string buffer for the CSV
    csv_buffer = StringIO()
    csv_writer = csv.writer(csv_buffer)

    # Write the header row to the CSV
    csv_writer.writerow(['Sr no', 'name', 'email', 'status'])

    # Write the data rows       
    for index, item in enumerate(data):
           csv_writer.writerow([ index+1, item.name, item.email, item.status])

    # Set the CSV string buffer's position to the beginning
    csv_buffer.seek(0)

    # Return the CSV file as a response
    return Response(
        content=csv_buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=data.csv"}
    )
# Set up Jinja2 templates


async def send_mail(recipient_email, recipient_name, sender_email, sender_password, message, subject, attachments: list[UploadFile] = File(...)):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    try:
        # Create a message object
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Personalize the HTML template with the recipient's name
        html_content = f"""
        <p>Hi {recipient_name},</p><br/>
        {message}
        <img src="http://139.59.89.17:8000/track_open?email={recipient_email}" alt="" width="100" height="100"/>
        """

        # Attach the personalized HTML body
        msg.attach(MIMEText(html_content, 'html'))
        print("==attachments===")
        print(attachments)
        # Attach a file if provided
        if attachments:
            for attachment in attachments:
                print(attachment.filename)
                print("==========")
                if hasattr(attachment, 'read'):  # File-like object (e.g., file uploaded via form)
                    attachment_content = await attachment.read()
                    filename = attachment.filename
                else:  # Regular file path
                    with open(attachment, 'rb') as f:
                        attachment_content = f.read()
                    filename = os.path.basename(attachment)

                # Create the attachment part
                part = MIMEBase('application', 'octet-stream')
                
                part.set_payload(attachment_content)
                encoders.encode_base64(part)

                # Add header with the correct filename
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{filename}"'
                )

                print(f"Attaching file: {filename}")
                msg.attach(part)
   
        # Set up the SMTP server and send the email
        
        server.starttls()  # Secure the connection
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        print(f"Email sent successfully to {recipient_name} ({recipient_email})")
    except Exception as e:
        print(f"Failed to send email to {recipient_name} ({recipient_email}). Error: {e}")
    finally:
        server.quit()

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

async def send_mail_html(email, name, username, password, message_file: UploadFile, subject):
    server = smtplib.SMTP("smtp.gmail.com", 587)  # Initialize the SMTP server

    try:
        # Create a message object
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = email
        msg['Subject'] = f'{subject}'
  
        with open('photonretouch mail template.text', 'r') as f:
            html_content = f.read()
        # Read the HTML template from the uploaded file
        # html_template = (await message_file.read()).decode('utf-8')

        # Personalize the HTML template by replacing {{name}} with the recipient’s name
        personalized_html = html_content.replace('{{name}}', name)
        personalized_html = f"""
        {personalized_html}
        <img src="http://139.59.89.17:8080/track_open?email={email}" alt="" width="100" height="100"/>
        """
        # Attach the personalized HTML body to the email
        msg.attach(MIMEText(personalized_html, 'html'))

        # Set up the server and send the email
        server.starttls()  # Secure the connection
        server.login(username, password)
        server.sendmail(username, email, msg.as_string())
        print(f"Email sent successfully to {name} ({email})")

    except Exception as e:
        print(f"Failed to send email to {name} ({email}). Error: {e}")

    finally:
        if server:
            server.quit()

# # Mock email sending function
# def send_mail(email: str, name: str):
#     print(f"Sending email to {name} at {email}")

@app.get("/home", response_class=HTMLResponse)
async def get_form(request: Request):
    # Render the HTML form page
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    # Render the HTML form page
    return templates.TemplateResponse("login.html", {"request": request})
@app.post("/submit-done", response_class=HTMLResponse)
async def get_form(request: Request):
    # Render the HTML form page
    return templates.TemplateResponse("submited.html", {"request": request})
@app.get("/table", response_class=HTMLResponse)
async def get_form(request: Request):
    # Render the HTML form page
    findSheet = ShetTableName.objects.all()
    tojson = findSheet.to_json()
    fromjson = json.loads(tojson)
    
    data = {
        "data":fromjson
    }
    return templates.TemplateResponse("table.html", {"request": request, **data})

@app.get("/html-bulk", response_class=HTMLResponse)
async def get_form(request: Request):
    # Render the HTML form page
    return templates.TemplateResponse("index2.html", {"request": request})

@app.post("/submit-form2/")
async def submit_form2(
    email: str = Form(...),
    password: str = Form(...),
    subject: str = Form(...),
    html: UploadFile = File(...),
    file: UploadFile = File(...),
    
):
    # Read the uploaded CSV file
    contents = await file.read()
    csv_string = contents.decode("utf-8")
    csv_reader = csv.reader(StringIO(csv_string))

    # Skip the header row
    header = next(csv_reader)

    # Process each recipient in the CSV file
    findDataTable = ShetTableName.objects(sheetname=file.filename).first()
    if findDataTable:
        for row in csv_reader:
            name = row[0]  # Assuming the first column is the name
            email2 = row[1]  # Assuming the second column is the email
    
            # Send the email using the send_mail_html function
            # Pass the uploaded HTML file (html) directly as the message_file
            await send_mail_html(email2, name, email, password, html, subject)
            saveData = MainData(tableid=str(ObjectId(findDataTable.id)), name=name, email=email2, status = "Sent")
            saveData.save()
    else:
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        saveTable= ShetTableName(sheetname=file.filename, date=current_date)
        # Skip the header row
        saveTable.save()
        header = next(csv_reader)
    # Process each recipient in the CSV file
        for row in csv_reader:
           name = row[0]  # Assuming the first column is the name
           email2= row[1]  # Assuming the second column is the email
           await send_mail_html(email2, name, email, password, html, subject)
           saveData = MainData(tableid=str(ObjectId(saveTable.id)), name=name, email=email2, status = "Sent")
           saveData.save()
        
        


    # Debug print the form data
    print(f"Email: {email}")
    print(f"Password: {password}")
    print(f"Subject: {subject}")

    return RedirectResponse(url="/submit-done")

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
from datetime import datetime
@app.post("/submit-form/")
async def submit_form(
    email: str = Form(...),
    password: str = Form(...),
    subject: str = Form(...),
    ckeditor_content: str = Form(...),
    file: UploadFile = File(...),
    files: list[UploadFile] = File(...)
):
    # Read the uploaded file (CSV)
    contents = await file.read()
    csv_string = contents.decode("utf-8")
    csv_reader = csv.reader(StringIO(csv_string))
    findDataTable = ShetTableName.objects(sheetname=file.filename).first()
    for file in files:
        print("===filename =",file.filename)
        
    if findDataTable:
        print("found")
        for row in csv_reader:
           name = row[0]  # Assuming the first column is the name
           email2= row[1]  # Assuming the second column is the email
           await send_mail(email2, name, email, password, ckeditor_content, subject, files)
           saveData = MainData(tableid=str(ObjectId(findDataTable.id)), name=name, email=email2, status = "Sent")
           saveData.save()
    else:
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        saveTable= ShetTableName(sheetname=file.filename, date=f"{current_date}")
        # Skip the header row
        saveTable.save()
        header = next(csv_reader)  
    # Process each recipient in the CSV file
        for row in csv_reader:
           name = row[0]  # Assuming the first column is the name
           email2= row[1]  # Assuming the second column is the email
           await send_mail(email2, name, email, password, ckeditor_content, subject, files)
           saveData = MainData(tableid=str(ObjectId(saveTable.id)), name=name, email=email2, status = "Sent")
           saveData.save()
           
        
      # Send the email to each recipient

    # Debug print the form data
    print(f"Email: {email}")
    print(f"Password: {password}")
    print(f"Subject: {subject}")
    print(f"CKEditor Content: {ckeditor_content}")

    return  RedirectResponse(url="/submit-done")


@app.post("/api/v1/login")
async def loginApi(body: LoginModel):
    findata = UserTable.objects(email=body.email).first()
    if findata :
        if findata.password == body.password:
             return RedirectResponse(url="/home")
        else:
            return {
                "message" : "Inccorect password",
                "status":False
            }
    else:
        return {
                "message" : "Inccorect email | password",
                "status":False
            }

@app.post("/api/v1/user-create")
async def userCreate(body: UserCreateModel):
    saveData = UserTable(**body.dict())
    saveData.save()
    return {
        "message": "User Created Succes",
        "status":True
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)