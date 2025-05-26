import smtplib
import email.message
from dotenv import load_dotenv
import os

def enviar_email(destinatarios, corpo_email=None, email_remetente = ""):  
    load_dotenv() 
    
    msg = email.message.Message()
    msg['Subject'] = "Alerta Meteorológico"
    msg['From'] = email_remetente
    msg['To'] = ", ".join(destinatarios)

    password = os.getenv("EMAIL_APP_PASSWORD")

    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(corpo_email)

    s = smtplib.SMTP('smtp.gmail.com:587')
    s.starttls()
    s.login(msg['From'], password)
    s.sendmail(msg['From'], destinatarios, msg.as_string().encode('utf-8'))
    s.quit()
    print('Emails enviados com sucesso!')

# Exemplo de uso
destinatarios = [
]

enviar_email(destinatarios, "teste de envio de email", "Insira aqui o email do remetente")
