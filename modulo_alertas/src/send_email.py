import smtplib
import email.message
from dotenv import load_dotenv
import os
import sys
from pathlib import Path

class EmailSender:
    def __init__(self):
        # Look for .env file in the current and parent directories
        env_path = Path('.env')
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
        else:
            # Try parent directory
            parent_env_path = Path('../.env')
            if parent_env_path.exists():
                load_dotenv(dotenv_path=parent_env_path)
            else:
                print("ERRO: Arquivo .env não encontrado!", file=sys.stderr)
                sys.exit(1)
        
        # Get environment variables
        self.email_remetente = os.getenv("EMAIL")
        self.password = os.getenv("EMAIL_APP_PASSWORD")
        
        # Check if environment variables are set and not empty
        if not self.email_remetente or self.email_remetente == "" or not self.password or self.password == "":
            print("ERRO: Variáveis de ambiente EMAIL e/ou EMAIL_APP_PASSWORD não definidas ou vazias!", file=sys.stderr)
            print("Configure estas variáveis no arquivo .env", file=sys.stderr)
            sys.exit(1)  # Exit with error code
        
    def send(self, destinatarios, corpo_email=None, assunto="Alerta Meteorológico"):
        """
        Envia um email para uma lista de destinatários.
        
        Args:
            destinatarios (list): Lista de emails dos destinatários
            corpo_email (str, optional): Corpo do email. Se None, usa o template padrão
            assunto (str, optional): Assunto do email. Defaults to "Alerta Meteorológico"
            
        Returns:
            bool: True se o email foi enviado com sucesso, False caso contrário
        """
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