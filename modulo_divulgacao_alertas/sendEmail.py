import smtplib
import email.message
from dotenv import load_dotenv
import os

def enviar_email(destinatarios):  
    corpo_email = """
    Alerta de temperatura acima de 35°C nas próximas 24 horas!
    """

    load_dotenv() 
    
    msg = email.message.Message()
    msg['Subject'] = "Alerta Meteorológico"
    msg['From'] = 'thiagoavatarnaruto@gmail.com'
    msg['To'] = ", ".join(destinatarios)

    password = os.getenv("EMAIL_APP_PASSWORD")
    print(password)

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
    "thiagobossun06@gmail.com",
    "thiagoavatarnaruto.marcos@yahoo.com",
    "thiagomarcos@discente.ufg.br"
]

enviar_email(destinatarios)
