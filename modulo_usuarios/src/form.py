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
    <link rel="icon" href="/static/cempa_ico.png" type="image/png">
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
        input[type="email"] {
            width: 90%;
            padding: 8px;
            margin-top: 5px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }

        select {
            width: 90%;
            padding: 8px;
            margin-top: 5px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }

        .city-block {
            background: #e9ecef;
            border-radius: 6px;
            padding: 10px;
            margin-top: 10px;
            margin-bottom: 10px;
            position: relative;
        }

        .city-block strong {
            font-size: 1.1em;
        }

        .city-block .remove-btn {
            position: absolute;
            right: 10px;
            top: 10px;
            background: #dc3545;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 2px 8px;
            cursor: pointer;
        }

        .city-block .remove-btn:hover {
            background: #b52a37;
        }

        .checkbox-group label {
            display: inline-block;
            margin-right: 10px;
        }

        .error {
            color: red;
            font-size: 0.9em;
        }

        button[type="submit"] {
            margin-top: 20px;
            padding: 10px;
            background: #28a745;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }

        button[type="submit"]:hover {
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
        <p>Cadastre-se para receber alertas meteorológicos por e-mail diretamente do CEMPA.</p>
        <label for="nome">Nome:</label>
        <input type="text" id="nome" name="nome" required>
        <label for="email">Email:</label>
        <input type="email" id="email" name="email" required>
        <label for="cidadeSelect">Adicionar cidade:</label>
        <select id="cidadeSelect">
{city_options}        </select>
        <button type="button" id="addCityBtn">Adicionar cidade</button>
        <div class="help-text">Selecione uma cidade e clique em Adicionar. Para cada cidade, escolha os tipos de alerta desejados.</div>
        <div id="cityBlocks"></div>
        <div id="errorMsg" class="error"></div>
        <button type="submit">Enviar</button>
    </form>
    <script>
        const cityBlocks = {};
        document.getElementById('addCityBtn').addEventListener('click', function() {
            const select = document.getElementById('cidadeSelect');
            const city = select.value;
            if (!city || cityBlocks[city]) return;
            // Cria bloco
            const block = document.createElement('div');
            block.className = 'city-block';
            block.id = `block-${city}`;
            block.innerHTML = `
                <strong>${city}</strong>
                <div class="checkbox-group">
                    <label><input type="checkbox" value="Temperatura"> Temperatura</label>
                    <label><input type="checkbox" value="Umidade"> Umidade</label>
                </div>
                <button type="button" class="remove-btn" onclick="removeCityBlock('${city}')">Remover</button>
            `;
            document.getElementById('cityBlocks').appendChild(block);
            cityBlocks[city] = block;
        });
        window.removeCityBlock = function(city) {
            const block = cityBlocks[city];
            if (block) {
                block.remove();
                delete cityBlocks[city];
            }
        }
        document.getElementById('alertForm').addEventListener('submit', async function (e) {
            e.preventDefault();
            const nome = document.getElementById('nome').value.trim();
            const email = document.getElementById('email').value.trim();
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
            const blocks = document.querySelectorAll('.city-block');
            if (blocks.length === 0) {
                errorMsg.textContent = "Adicione pelo menos uma cidade.";
                return;
            }
            const cidades = [];
            const alert_types = [];
            let valid = true;
            blocks.forEach(block => {
                const city = block.querySelector('strong').textContent;
                const types = Array.from(block.querySelectorAll('input[type=checkbox]:checked')).map(cb => cb.value);
                if (types.length === 0) {
                    valid = false;
                }
                cidades.push(city);
                alert_types.push(types);
            });
            if (!valid) {
                errorMsg.textContent = "Selecione pelo menos um tipo de alerta para cada cidade.";
                return;
            }
            try {
                const currentUrl = window.location.origin;
                const res = await fetch(`${currentUrl}/users`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        username: nome,
                        email: email,
                        cities: cidades,
                        alert_types: alert_types
                    })
                });
                const data = await res.json();
                if (res.status === 201) {
                    alert('Usuário cadastrado com sucesso!');
                    document.getElementById('alertForm').reset();
                    document.getElementById('cityBlocks').innerHTML = '';
                    for (const key in cityBlocks) delete cityBlocks[key];
                } else {
                    errorMsg.textContent = 'Erro ao cadastrar usuário.';
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