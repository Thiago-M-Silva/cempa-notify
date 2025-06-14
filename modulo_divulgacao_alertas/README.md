# Configuração envio de email

Para o envio de email funcionar corretamente, é necessário uma senha de app do gmail

Para isso, siga os seguintes passos:
- acesse https://myaccount.google.com
- busque por "senhas de app" na barra de pesquisa 
- gere sua senha de app, escrevendo o nome da aplicação no campo indicado
- crie um arquivo com o nome ".env" (apenas o que está entre aspas) nesta mesma pasta 
- adicione a senha gerada na seguinte linha, copie-a e cole-a, sem espacos, no arquivo gerado
    EMAIL_APP_PASSWORD=${app_password}
    EMAIL=${email}
- apos isso o sistema estará apto para enviar as notificações