import os
import sys
import json  # Add json import at the top
import html
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from shared_config.config_parser import ConfigParser

current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.abspath(os.path.join(current_dir, '../../', 'config.csv'))

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
        import json
        import html
        
        # Começar com uma opção vazia
        options_html = '            <option value="">Selecione uma cidade</option>\n'
        
        # Ordenar as cidades pelo nome de exibição para melhor apresentação
        city_display_names = []
        city_configs = {}  # Armazenar configurações das cidades
        
        # Lista de chaves de temperatura mensal para verificar
        temp_keys = [
            'temp_max_jan', 'temp_max_feb', 'temp_max_mar', 'temp_max_apr',
            'temp_max_may', 'temp_max_jun', 'temp_max_jul', 'temp_max_aug',
            'temp_max_sep', 'temp_max_oct', 'temp_max_nov', 'temp_max_dec'
        ]
        
        for polygon_name, config in config_map.items():
            display_name = config.get('display_name')
            if display_name:
                city_display_names.append(display_name)
                # Armazenar configuração da cidade
                city_configs[display_name] = {
                    'has_temperature': True,  # Começa como True, será False se encontrar algum 0
                    'has_humidity': True  # Umidade sempre disponível
                }
                
                # Verificar se qualquer threshold mensal é 0
                for key in temp_keys:
                    if config.get(key, 0) == 0:
                        city_configs[display_name]['has_temperature'] = False
                        break
        
        # Ordenar alfabeticamente
        city_display_names.sort()
        
        # Gerar as opções HTML
        for display_name in city_display_names:
            # Use json.dumps to properly serialize the config and escape it for HTML
            config_json = html.escape(json.dumps(city_configs[display_name]))
            options_html += f'            <option value="{html.escape(display_name)}" data-config="{config_json}">{html.escape(display_name)}</option>\n'
        
        return options_html
    
    # Substitua na string HTML a parte estática das opções de cidades por dinâmica
    form_html = """
<!DOCTYPE html>
<html lang="pt-BR">

<head>
    <meta charset="UTF-8">
    <title>CEMPA - Cadastro Avisos</title>
    <link rel="icon" href="/static/cempa_ico.png" type="image/png">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        html, body {
            height: 100%;
            width: 100%;
            overflow-x: hidden;
        }

        body {
            font-family: Arial, sans-serif;
            background: #f2f2f2;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            min-height: 100vh;
            padding: 20px;
            margin: 0;
        }

        form {
            background: white;
            padding: 20px;
            width: 100%;
            max-width: 400px;
            margin: 0;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            max-height: 90vh;
            overflow-y: auto;
        }

        @media (max-width: 480px) {
            body {
                padding: 10px;
                min-height: 100vh;
                height: 100vh;
                overflow-y: auto;
            }
            
            form {
                padding: 20px;
                margin: 0;
                min-height: auto;
                max-height: calc(100vh - 20px);
                border-radius: 8px;
                max-width: 100%;
                overflow-y: auto;
            }

            input[type="text"],
            input[type="email"],
            select {
                width: 100%;
                font-size: 16px; /* Previne zoom em iOS */
                padding: 12px;
            }

            #addCityBtn {
                width: 100%;
                padding: 12px;
                font-size: 16px;
            }

            button[type="submit"] {
                width: 100%;
                padding: 12px;
                font-size: 16px;
            }

            .city-block {
                padding: 15px;
            }

            .city-block .remove-btn {
                padding: 8px 12px;
                font-size: 14px;
            }

            h2 {
                font-size: 1.5em;
                margin-bottom: 15px;
            }

            p {
                font-size: 1em;
                line-height: 1.4;
                margin-bottom: 15px;
            }

            label {
                font-size: 1em;
                margin-top: 12px;
            }

            .help-text {
                font-size: 0.9em;
                margin-top: 6px;
            }
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

        #addCityBtn {
            margin-top: 10px;
            padding: 10px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            width: 90%;
        }

        #addCityBtn:hover {
            background: #0056b3;
        }

        .help-text {
            font-size: 12px;
            color: #666;
            margin-top: 4px;
            font-style: italic;
        }

        .consent-checkbox {
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 4px solid #007bff;
        }

        .consent-checkbox label {
            display: flex;
            align-items: flex-start;
            gap: 10px;
            margin-top: 0;
            font-size: 14px;
            line-height: 1.4;
            cursor: pointer;
        }

        .consent-checkbox input[type="checkbox"] {
            width: auto;
            margin-top: 2px;
            flex-shrink: 0;
        }

        .consent-checkbox .consent-text {
            flex: 1;
        }

        @media (max-width: 480px) {
            .consent-checkbox {
                padding: 12px;
                margin-top: 15px;
            }

            .consent-checkbox label {
                font-size: 13px;
            }
        }

        .logo-container {
            text-align: center;
            margin-bottom: 20px;
        }

        .logo-container img {
            max-width: 280px;
            height: auto;
        }

        @media (max-width: 480px) {
            .logo-container {
                margin-bottom: 15px;
            }

            .logo-container img {
                max-width: 220px;
            }
        }
    </style>
</head>

<body>
    <form id="alertForm">
        <div class="logo-container">
            <img src="/static/cempa_horizontal.png" alt="CEMPA Logo">
        </div>
        <h2>Cadastro de avisos</h2>
        <p>
            Cadastre-se para receber avisos meteorológicos por e-mail diretamente do Centro de Excelência em Estudos, 
            Monitoramento e Previsões Ambientais do Cerrada/Universidade Federal de Goiás (CEMPA).
        </p>
        <label for="email">Email:</label>
        <input type="email" id="email" name="email" required>
        <div id="emailMsg" class="help-text"></div>
        <label for="nome">Nome:</label>
        <input type="text" id="nome" name="nome" required>
        <label for="cidadeSelect">Adicionar cidade:</label>
        <select id="cidadeSelect">
{city_options}        </select>
        <button type="button" id="addCityBtn">Adicionar cidade</button>
        <div class="help-text">Selecione uma cidade e clique em Adicionar. Para cada cidade, escolha os tipos de avisos desejados.</div>
        <div id="cityBlocks"></div>
        <div id="errorMsg" class="error"></div>
        
        <div class="consent-checkbox">
            <label>
                <input type="checkbox" id="consentCheckbox" required>
                <span class="consent-text">
                    Autorizo o Centro de Excelência em Estudos, Monitoramento e Previsões Ambientais do Cerrado (CEMPA) 
                    a enviar e-mails e notificações sobre alertas meteorológicos, novidades e comunicados pertinentes 
                    ao funcionamento do sistema de avisos. Posso cancelar este consentimento a qualquer momento.
                </span>
            </label>
        </div>
        
        <button type="submit">Enviar</button>
    </form>
    <script>
        const cityBlocks = {};
        let isEditing = false;

        // Função para criar um bloco de cidade
        function createCityBlock(city, selectedTypes = []) {
            if (cityBlocks[city]) return;
            
            const select = document.getElementById('cidadeSelect');
            const option = Array.from(select.options).find(opt => opt.value === city);
            if (!option) return;
            
            const config = JSON.parse(option.getAttribute('data-config'));
            
            // Cria bloco
            const block = document.createElement('div');
            block.className = 'city-block';
            block.id = `block-${city}`;
            
            // Gerar checkboxes baseado nas configurações da cidade
            let checkboxes = '';
            if (config.has_temperature) {
                const checked = selectedTypes.includes('Temperatura') ? 'checked' : '';
                checkboxes += `<label><input type="checkbox" value="Temperatura" ${checked}> Temperatura</label>`;
            }
            if (config.has_humidity) {
                const checked = selectedTypes.includes('Umidade') ? 'checked' : '';
                checkboxes += `<label><input type="checkbox" value="Umidade" ${checked}> Umidade</label>`;
            }
            
            block.innerHTML = `
                <strong>${city}</strong>
                <div class="checkbox-group">
                    ${checkboxes}
                </div>
                <button type="button" class="remove-btn" onclick="removeCityBlock('${city}')">Remover</button>
            `;
            document.getElementById('cityBlocks').appendChild(block);
            cityBlocks[city] = block;
        }

        // Função para preencher o formulário com os dados do usuário
        async function fillUserData(email) {
            // Limpar blocos existentes em qualquer caso
            document.getElementById('cityBlocks').innerHTML = '';
            for (const key in cityBlocks) delete cityBlocks[key];
            isEditing = false;
            
            try {
                const currentUrl = window.location.origin;
                const response = await fetch(`${currentUrl}/users/email?email=${encodeURIComponent(email)}`);
                
                if (response.status === 200) {
                    const userData = await response.json();
                    
                    // Preencher nome apenas se usuário for encontrado
                    document.getElementById('nome').value = userData.username;
                    
                    // Criar blocos para cada alerta
                    userData.alerts.forEach(alert => {
                        createCityBlock(alert.city, alert.types);
                    });
                    
                    // Marcar como edição
                    isEditing = true;
                    document.getElementById('emailMsg').textContent = 'Usuário encontrado. Você pode editar os avisos.';
                    document.getElementById('emailMsg').style.color = '#28a745';
                } else if (response.status === 404) {
                    // Limpar mensagem se o usuário não for encontrado
                    document.getElementById('emailMsg').textContent = 'Email não cadastrado. Preencha o formulário para se cadastrar.';
                    document.getElementById('emailMsg').style.color = '#666';
                }
            } catch (error) {
                console.error('Erro ao buscar usuário:', error);
                document.getElementById('emailMsg').textContent = 'Erro ao verificar email.';
                document.getElementById('emailMsg').style.color = '#dc3545';
            }
        }

        // Adicionar evento blur no campo de email
        document.getElementById('email').addEventListener('blur', function() {
            const email = this.value.trim();
            if (email && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
                fillUserData(email);
            }
        });

        // Modificar o evento de submit para lidar com edição
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
            
            // Verificar se o consentimento foi dado
            const consentCheckbox = document.getElementById('consentCheckbox');
            if (!consentCheckbox.checked) {
                errorMsg.textContent = "É necessário aceitar o consentimento para envio de e-mails.";
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
                errorMsg.textContent = "Selecione pelo menos um tipo de aviso para cada cidade ou remova-a.";
                return;
            }
            
            try {
                const currentUrl = window.location.origin;
                const alerts = cidades.map((city, index) => ({
                    city: city,
                    types: alert_types[index]
                }));
                
                const method = isEditing ? 'PUT' : 'POST';
                const url = isEditing ? 
                    `${currentUrl}/users` : 
                    `${currentUrl}/users`;
                
                const res = await fetch(url, {
                    method: method,
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        username: nome,
                        email: email,
                        alerts: alerts
                    })
                });
                
                const data = await res.json();
                if (res.status === 201 || res.status === 200) {
                    alert(isEditing ? 'Usuário atualizado com sucesso!' : 'Usuário cadastrado com sucesso!');
                    document.getElementById('alertForm').reset();
                    document.getElementById('cityBlocks').innerHTML = '';
                    document.getElementById('emailMsg').textContent = '';
                    for (const key in cityBlocks) delete cityBlocks[key];
                    isEditing = false;
                } else {
                    errorMsg.textContent = isEditing ? 'Erro ao atualizar usuário.' : 'Erro ao cadastrar usuário.';
                }
            } catch (err) {
                console.error(err);
                errorMsg.textContent = 'Erro na comunicação com o servidor.';
            }
        });

        // Manter o código existente do addCityBtn
        document.getElementById('addCityBtn').addEventListener('click', function() {
            const select = document.getElementById('cidadeSelect');
            const option = select.options[select.selectedIndex];
            const city = option.value;
            
            if (!city || cityBlocks[city]) return;
            
            createCityBlock(city);
        });

        window.removeCityBlock = function(city) {
            const block = cityBlocks[city];
            if (block) {
                block.remove();
                delete cityBlocks[city];
            }
        }
    </script>
</body>

</html>
    """
    
    # Substituir o marcador {city_options} pelo HTML gerado dinamicamente
    form_html = form_html.replace('{city_options}', generate_city_options.__func__())