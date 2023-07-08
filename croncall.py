import smtplib
import json
import pandas as pd
import imaplib
import os
import io
import pprint
import base64
import email
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import decode_header
import time
from extract import invextract


luser = 'demoacc8413@gmail.com'
lpass = 'polxonghdxqwleeq'


sServer = "imap.gmail.com"
nImap = imaplib.IMAP4_SSL(sServer)
nImap.login(luser,lpass)
nImap.select('INBOX')

nImap.recent()

type,data = nImap.search(None,'(UNSEEN)')
# type,data = nImap.search(None,'(UNSEEN)' ,'(SUBJECT "email test")')
mailIds = data[0]

idList = mailIds.split()

if idList == []:
    print('empty')
    pass
else:
    # print('check',idList)
    for num in data[0].split():
        type,data = nImap.fetch(num,'(RFC822)')
        rawEmail = data[0][1]
        rawEmailString = rawEmail.decode('utf-8')
        emailMessage = email.message_from_string(rawEmailString)
        euid = emailMessage.get('Message-ID')
        efrom = emailMessage['From']
        esub = emailMessage['Subject']
        for part in emailMessage.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            fileName = part.get_filename()
            if bool(fileName):
                # filePath = os.path.join('/document',fileName)
                filePath = os.path.join('/home/shashi/Documents/WorkingFolder/venv/afcons/rootfolder/mailtest',fileName)
                if not os.path.isfile(filePath):
                    fp = open(filePath, 'wb')
                    fp.write(part.get_payload(decode=True))
                    fp.close()

    nImap.close()

    time.sleep(10)

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(luser,lpass)
    receiveremail = efrom
    message = MIMEMultipart("mixed")
    message["Message-ID"] = euid
    message["Subject"] = esub
    message["From"] = efrom
    message["To"] = luser
    try:
        pdffile = filePath
        callfunc = invextract(pdffile)
        if callfunc:
            str_io = io.StringIO()
            df = pd.read_json(callfunc)
            df.to_html(buf=str_io)
            table_html = str_io.getvalue()

        # print(pdffile)
        # Create the plain-text and HTML version of your message
        text = """\
        Hi,
        How are you?
        Real Python has many great tutorials:
        www.realpython.com"""
        html = """\
        <html>
        <body>
            <p>{table_html}</p>
        </body>
        </html>
        """.format(table_html=table_html)

        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        message.attach(part1)
        message.attach(part2)

        # Create secure connection with server and send email
        s.sendmail(luser,efrom,message.as_string())
        os.remove(filePath)
    except NameError:
        # Create the plain-text and HTML version of your message
        text = """\
        Hi,
        there were no attachment"""
        html = """\
        <html>
        <body>
            <p>Hi,

            There were no attachment.
            </p>
        </body>
        </html>
        """

        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        message.attach(part1)
        message.attach(part2)

        # Create secure connection with server and send email
        s.sendmail(luser,efrom,message.as_string())

    # print(euid,efrom,esub)
