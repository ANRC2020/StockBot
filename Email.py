import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import mimetypes

def email():
    host_address = 'stock.trader.report@gmail.com'
    send_to_addresses = 'siddiquiabbas22@gmail.com, ravirahul660@gmail.com'

    fileToSend = "ActivityLog.txt"

    msg = MIMEMultipart()
    msg['From'] = host_address
    fp = open(fileToSend, "rb")
    attachment = MIMEBase('txt','txt')
    attachment.set_payload(fp.read())
    fp.close()
    attachment.add_header("Content-Disposition", "attachment", filename=fileToSend)
    msg.attach(attachment)

    server = smtplib.SMTP(host = 'smtp.gmail.com', port = 587)
    server.starttls()
    server.login('stock.trader.report@gmail.com', 'qwert#12345')

    # for email in send_to_addresses:
    msg['To'] = send_to_addresses
    server.send_message(msg)

    server.quit()