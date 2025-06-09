import smtplib
import email.message
from dotenv import load_dotenv
import os

class EmailSender:
    def __init__(self):
        load_dotenv()
        self.email_remetente = os.getenv("EMAIL_APP_PASSWORD")
        self.password = os.getenv("EMAIL")
        
    def enviar_email(self, destinatarios, corpo_email=None, assunto="Alerta Meteorológico"):  
        msg = email.message.Message()
        msg['Subject'] = assunto
        msg['From'] = self.email_remetente
        msg['To'] = ", ".join(destinatarios)

        msg.add_header('Content-Type', 'text/html')
        msg.set_payload(corpo_email)

        s = smtplib.SMTP('smtp.gmail.com:587')
        s.starttls()
        s.login(msg['From'], self.password)
        s.sendmail(msg['From'], destinatarios, msg.as_string().encode('utf-8'))
        s.quit()
        print('Emails enviados com sucesso!')
