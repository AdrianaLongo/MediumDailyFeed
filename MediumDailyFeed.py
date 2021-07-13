import datetime
import email
import imaplib
import os
import re
from email.header import decode_header
from email.message import Message
from smtplib import SMTP_SSL, SMTP_SSL_PORT

imap = imaplib.IMAP4_SSL("imap.gmail.com")
smtp = SMTP_SSL("smtp.gmail.com")

my_mail = "myaddress@mymail.com"
password = "appPassword" # app password, not email password
pocket = "add@getpocket.com"

def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)

print('\nTry connection...\n')

try:
    imap.login(my_mail, password)
    print("Connected!\n")

    date = (datetime.date.today() - datetime.timedelta(1)).strftime("%d-%b-%Y")  
    imap.select("INBOX")
    status, unread = imap.search(None, ('UNSEEN'), '(SENTSINCE {0})'.format(date), 'FROM "Medium Daily Digest"')
    unread_number = len(unread[0].split())

    print("Unread from medium: " + str(unread_number) + "\n")

    read_list = []

    if unread_number > 0:
        for i in unread[0].split():
            res, msg = imap.fetch(i, "(RFC822)")
            for m in msg:
                if isinstance(m, tuple):
                    msg = email.message_from_bytes(m[1])

                    # Retrieve sender
                    sender, encoding = decode_header(msg.get("From"))[0]
                    if isinstance(sender, bytes):
                        sender = sender.decode("UTF-8")

                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            try:
                                body = part.get_payload(decode=True).decode()
                            except:
                                pass

                            if content_type == "text/html":
                                # Body has many links: we want to filter links to articles
                                urls = re.findall(r'https:\/\/medium.com\/@[a-z]+\/(?:[a-zA-Z0-9]+-)+(?:[a-zA-Z0-9]+)', body, re.DOTALL)

                                for r in urls:
                                    read_list.append(r)       

        read_list = list(dict.fromkeys(read_list)) # deletes duplicates

        print(str(len(read_list)) + " links found")

        for rl in read_list:
            # SEND MULTIPLES MAIL WITH LINKS TO POCKET
            smtp.set_debuglevel(1) # Show SMTP server interactions
            smtp.login(my_mail, password)
            url = '\n\n'+rl
            smtp.sendmail(my_mail, pocket, url)
            print(rl)
        
    else:
        print("No new mail from Medium")
    
    print("\nLogout")    
    imap.close()
except imaplib.IMAP4_SSL.error:
    print("Login failed or already logged out")