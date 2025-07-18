class Form:
    form_html = """
    <!DOCTYPE html>
    <html lang="pt-BR">

    <head>
        <meta charset="UTF-8">
        <title>Cadastro Alertas CEMPA</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f2f2f2;
                padding: 40px;
            }

            form {
                background: white;
                padding: 20px;
                max-width: 400px;
                margin: auto;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }

            label {
                display: block;
                margin-top: 15px;
            }
            
            p {
                font-size: small;
            }

            input[type="text"],
            input[type="email"],
            select {
                width: 90%;
                padding: 8px;
                margin-top: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }

            .checkbox-group {
                margin-top: 10px;
            }

            .checkbox-group label {
                display: inline-block;
                margin-right: 10px;
            }

            .error {
                color: red;
                font-size: 0.9em;
            }

            button {
                margin-top: 20px;
                padding: 10px;
                background: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }

            button:hover {
                background: #218838;
            }
        </style>
    </head>

    <body>

        <form id="alertForm">
            <h2>Cadastro Alertas CEMPA</h2>

            <p>
                Cadastre-se para receber alertas meteorológicos por e-mail diretamente do CEMPA.
            </p>

            <label for="nome">Nome:</label>
            <input type="text" id="nome" name="nome" required>

            <label for="email">Email:</label>
            <input type="email" id="email" name="email" required>

            <label>Alerta:</label>
            <div class="checkbox-group">
                <label><input type="checkbox" name="alerta" value="Temperatura"> Temperatura</label>
                <label><input type="checkbox" name="alerta" value="Humidade"> Humidade</label>
            </div>

            <label for="cidade">Cidade:</label>
            <select id="cidade" name="cidade">
                <option value="Goiânia">Goiânia</option>
            </select>

            <div id="errorMsg" class="error"></div>

            <button type="submit">Enviar</button>
        </form>

        <script>
            document.getElementById('alertForm').addEventListener('submit', function (e) {
                e.preventDefault();
                const nome = document.getElementById('nome').value.trim();
                const email = document.getElementById('email').value.trim();
                const checkboxes = document.querySelectorAll('input[name="alerta"]:checked');
                const errorMsg = document.getElementById('errorMsg');
                errorMsg.textContent = "";

                if (!nome) {
                    errorMsg.textContent = "Nome é obrigatório.";
                    return;
                }

                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(email)) {
                    errorMsg.textContent = "Insira um email válido.";
                    return;
                }

                if (checkboxes.length === 0) {
                    errorMsg.textContent = "Selecione pelo menos um tipo de alerta.";
                    return;
                }

                if (!nome || !email || alertas.length === 0) {
            errorMsg.textContent = "Preencha todos os campos corretamente.";
            return;
        }

        try {
            const res = fetch('/users', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: nome,
                email: email,
                city: cidade,
                alert: alertas.join(', ')
            })
            });

            const json = res.json();
            if (res.ok) {
            alert('Usuário cadastrado com sucesso!');
            document.getElementById('alertForm').reset();
            } else {
            errorMsg.textContent = json.error || 'Erro ao cadastrar usuário.';
            }

        } catch (err) {
            errorMsg.textContent = 'Erro na comunicação com o servidor.';
        }
        });

                alert("Formulário enviado com sucesso!");
                
            });
        </script>

    </body>

    </html>
    """