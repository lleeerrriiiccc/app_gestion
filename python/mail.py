import smtplib
from email.mime.multipart import MIMEMultipart, MIMEBase
from email.mime.text import MIMEText
from email import encoders
import database as db
import os
import dotenv
dotenv.load_dotenv()  # Carga las variables de entorno desde el archivo .env


FROM = 'financierosu@gmail.com'
sender_address = FROM
sender_pass = os.getenv('MAILPASSWD')

def buil_fact_reminder_mail(invoice_id):
    data = db.get_invoice(invoice_id)
    print(data)
    subject = f'Recordatorio de factura pendiente - {data["fecha"]}'
    content = f"""
    <html>
        <body>
            <p>Hola {data['cliente']},</p>
            <p>Este es un recordatorio de que tienes una factura pendiente con fecha de vencimiento el {data['fecha']}.</p>
            <p>Por favor, asegúrate de realizar el pago antes de la fecha de vencimiento para evitar cargos adicionales.</p>
            <p>Gracias por tu atención.</p>
        </body>
    </html>
    """
    return subject, content, data['ubicacion_factura']

def send_mail(subject, content, receiver, attachments=None):
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver
    message['Subject'] = subject
    message['X-Priority'] = '1'
    message['Importance'] = 'High'
    message.attach(MIMEText(content, 'html'))

    if attachments:
        for file_path in attachments:
            with open(file_path, "rb") as attachment:
                msg_attachment = MIMEBase('application', 'octet-stream')
                msg_attachment.set_payload(attachment.read())
            encoders.encode_base64(msg_attachment)
            msg_attachment.add_header('Content-Disposition', f'attachment; filename= {os.path.basename(file_path)}')
            message.attach(msg_attachment)

    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    session.login(sender_address, sender_pass)
    session.sendmail(sender_address, receiver, message.as_string())
    session.quit()

