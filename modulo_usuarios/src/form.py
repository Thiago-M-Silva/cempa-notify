import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from shared_config.config_parser import ConfigParser

current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.abspath(os.path.join(current_dir, '../../', 'config_files.csv'))

config_parser = ConfigParser(config_path)
config_parser.parse()
config_map = config_parser.get_config_map()


"""
Formulario HTML para cadastro de usuários
"""

class Form:
    # Gerando as opções de cidades dinamicamente a partir do config_map
    @staticmethod
    def generate_city_options():
        options_html = ""
        
        # Ordenar as cidades pelo nome de exibição para melhor apresentação
        city_display_names = []
        
        for polygon_name, config in config_map.items():
            display_name = config.get('display_name')
            if display_name:
                city_display_names.append(display_name)
        
        # Ordenar alfabeticamente
        city_display_names.sort()
        
        # Gerar as opções HTML
        for display_name in city_display_names:
            options_html += f'            <option value="{display_name}">{display_name}</option>\n'
        
        return options_html
    
    # Substitua na string HTML a parte estática das opções de cidades por dinâmica
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

        select[multiple] {
            width: 90%;
            padding: 8px;
            margin-top: 5px;
            border: 1px solid #ccc;
            border-radius: 4px;
            background-color: white;
        }

        select[multiple] option {
            padding: 8px;
            margin: 2px 0;
        }

        select[multiple] option:checked {
            background-color: #28a745;
            color: white;
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

        .help-text {
            font-size: 12px;
            color: #666;
            margin-top: 4px;
            font-style: italic;
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
            <label><input type="checkbox" name="alerta" value="Umidade"> Umidade</label>
        </div>

        <label for="cidade">Cidades: </label>
        <select id="cidade" name="cidade" multiple size="5">
{city_options}
        </select>
        <p class="help-text">* Para selecionar múltiplas cidades, mantenha a tecla CTRL pressionada enquanto clica</p>

        <div id="errorMsg" class="error"></div>

        <button type="submit">Enviar</button>
    </form>

    <script>
        document.getElementById('alertForm').addEventListener('submit', async function (e) {
            e.preventDefault();
            const nome = document.getElementById('nome').value.trim();
            const email = document.getElementById('email').value.trim();
            const cidades = Array.from(document.getElementById('cidade').selectedOptions).map(opt => opt.value);
            const alertas = document.querySelectorAll('input[name="alerta"]:checked');
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

            if (alertas.length === 0) {
                errorMsg.textContent = "Selecione pelo menos um tipo de alerta.";
                return;
            }

            if (cidades.length === 0) {
                errorMsg.textContent = "Selecione pelo menos uma cidade.";
                return;
            }

            try {
                const alertasArray = Array.from(alertas).map(cb => cb.value);
                const res = await fetch('http://localhost:8081/users', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        username: nome,
                        email: email,
                        cities: cidades,  
                        alert_types: alertasArray
                    })
                });

                const data = await res.json();
                
                if (res.status === 201) { 
                    alert('Usuário cadastrado com sucesso!');
                    document.getElementById('alertForm').reset();
                } else {
                    errorMsg.textContent = 'Erro ao cadastrar usuário, usuário ';
                }
            } catch (err) {
                console.error(err); 
                errorMsg.textContent = 'Erro na comunicação com o servidor.';
            }
        });
    </script>

</body>

</html>
    """
    
    # Substituir o marcador {city_options} pelo HTML gerado dinamicamente
    form_html = form_html.replace('{city_options}', generate_city_options.__func__())