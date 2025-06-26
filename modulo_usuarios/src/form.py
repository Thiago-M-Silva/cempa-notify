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
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
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
                padding: 8px;
                min-height: 100vh;
                height: 100vh;
                overflow-y: auto;
                background: #f2f2f2;
            }
            
            form {
                padding: 16px;
                margin: 0;
                min-height: auto;
                max-height: calc(100vh - 16px);
                border-radius: 12px;
                max-width: 100%;
                overflow-y: auto;
                box-shadow: 0 2px 15px rgba(0, 0, 0, 0.15);
            }

            .logo-container {
                margin-bottom: 16px;
            }

            .logo-container img {
                max-width: 180px;
            }

            h2 {
                font-size: 1.3em;
                margin-bottom: 12px;
                text-align: center;
                color: #333;
            }

            p {
                font-size: 0.85em;
                line-height: 1.4;
                margin-bottom: 16px;
                text-align: justify;
                color: #555;
            }

            label {
                font-size: 0.9em;
                margin-top: 16px;
                font-weight: 500;
                color: #333;
            }

            input[type="text"],
            input[type="email"],
            select {
                width: 100%;
                font-size: 16px;
                padding: 14px 12px;
                margin-top: 6px;
                border-radius: 8px;
                border: 1px solid #ddd;
                background-color: #fafafa;
            }

            input[type="text"]:focus,
            input[type="email"]:focus,
            select:focus {
                outline: none;
                border-color: #007bff;
                background-color: white;
                box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.1);
            }

            #addCityBtn {
                width: 100%;
                padding: 14px;
                font-size: 16px;
                margin-top: 12px;
                border-radius: 8px;
                font-weight: 500;
            }

            button[type="submit"] {
                width: 100%;
                padding: 16px;
                font-size: 16px;
                margin-top: 20px;
                border-radius: 8px;
                font-weight: 500;
            }

            .city-block {
                padding: 16px;
                margin-top: 12px;
                margin-bottom: 12px;
                border-radius: 10px;
                background: #f8f9fa;
                border: 1px solid #e9ecef;
            }

            .city-block strong {
                font-size: 1.1em;
                display: block;
                margin-bottom: 12px;
                color: #333;
            }

            .city-block .remove-btn {
                padding: 8px 12px;
                font-size: 12px;
                border-radius: 6px;
                position: absolute;
                right: 12px;
                top: 12px;
            }

            .checkbox-group {
                margin: 12px 0;
            }

            .checkbox-group label {
                display: block;
                margin: 10px 0;
                font-size: 0.9em;
                padding: 8px 0;
            }

            .checkbox-group input[type="checkbox"] {
                margin-right: 8px;
                transform: scale(1.2);
            }

            .help-text {
                font-size: 0.8em;
                margin-top: 8px;
                color: #666;
                line-height: 1.3;
                font-style: italic;
            }

            #removeAllCitiesBtn {
                width: 100%;
                padding: 14px;
                font-size: 16px;
                border-radius: 8px;
                font-weight: 500;
            }

            #unsubscribeBtn {
                width: 100%;
                padding: 14px;
                font-size: 16px;
                border-radius: 8px;
                font-weight: 500;
            }

            .consent-checkbox {
                padding: 16px;
                margin-top: 20px;
                border-radius: 10px;
                background: #f8f9fa;
                border-left: 4px solid #007bff;
            }

            .consent-checkbox label {
                font-size: 0.8em;
                line-height: 1.4;
                margin-top: 0;
            }

            .consent-checkbox input[type="checkbox"] {
                transform: scale(1.2);
                margin-right: 10px;
            }

            .error {
                color: red;
                font-size: 0.9em;
                min-height: 0;
                margin: 0;
                padding: 0;
                display: none;
            }

            .error:not(:empty) {
                display: block;
                margin-top: 8px;
                padding: 10px;
                border-radius: 6px;
                background-color: #f8d7da;
                border: 1px solid #f5c6cb;
                color: #721c24;
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
            width: 100%;
            padding: 8px;
            margin-top: 5px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }

        select {
            width: 100%;
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
            width: 100%;
        }

        #addCityBtn:hover {
            background: #0056b3;
        }

        #removeAllCitiesBtn {
            background: #dc3545;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            cursor: pointer;
            font-size: 14px;
            width: 90%;
        }

        #removeAllCitiesBtn:hover {
            background: #b52a37;
        }

        #removeAllCitiesContainer {
            margin-top: 10px;
            text-align: center;
        }

        #unsubscribeContainer {
            margin-top: 15px;
            text-align: center;
        }

        #unsubscribeBtn {
            background: #dc3545;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 10px 20px;
            cursor: pointer;
            font-size: 14px;
            width: 100%;
        }

        #unsubscribeBtn:hover {
            background: #b52a37;
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

        button[type="submit"] {
            width: 100%;
            padding: 12px;
            font-size: 16px;
        }

        #removeAllCitiesBtn {
            width: 100%;
            padding: 12px;
            font-size: 16px;
        }

        .city-block {
        }

        /* Modal customizado */
        .custom-modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(2px);
        }

        .modal-content {
            background-color: white;
            margin: 15% auto;
            padding: 20px;
            border-radius: 8px;
            width: 90%;
            max-width: 400px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            animation: modalSlideIn 0.3s ease-out;
        }

        @keyframes modalSlideIn {
            from {
                opacity: 0;
                transform: translateY(-50px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .modal-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #333;
        }

        .modal-message {
            font-size: 14px;
            margin-bottom: 20px;
            color: #666;
            line-height: 1.4;
        }

        .modal-buttons {
            display: flex;
            gap: 10px;
            justify-content: center;
        }

        .modal-btn {
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            min-width: 80px;
        }

        .modal-btn-primary {
            background-color: #007bff;
            color: white;
        }

        .modal-btn-primary:hover {
            background-color: #0056b3;
        }

        .modal-btn-danger {
            background-color: #dc3545;
            color: white;
        }

        .modal-btn-danger:hover {
            background-color: #b52a37;
        }

        .modal-btn-secondary {
            background-color: #6c757d;
            color: white;
        }

        .modal-btn-secondary:hover {
            background-color: #545b62;
        }

        @media (max-width: 480px) {
            .modal-content {
                margin: 20% auto;
                width: 95%;
                padding: 25px 20px;
            }

            .modal-buttons {
                flex-direction: column;
            }

            .modal-btn {
                width: 100%;
                padding: 12px;
                font-size: 16px;
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
        <input type="email" id="email" name="email" autocomplete="email" required>
        <label for="nome">Nome:</label>
        <input type="text" id="nome" name="nome" autocomplete="name" required>
        <label for="cidadeSelect">Adicionar cidade:</label>
        <select id="cidadeSelect">
{city_options}        </select>
        <button type="button" id="addCityBtn">Adicionar cidade</button>
        <div class="help-text">Selecione uma cidade e clique em Adicionar. Para cada cidade, escolha os tipos de avisos desejados.</div>
        <div id="cityBlocks"></div>
        <div id="removeAllCitiesContainer" style="display: none; margin-top: 10px; text-align: center;">
            <button type="button" id="removeAllCitiesBtn" style="background: #dc3545; color: white; border: none; border-radius: 4px; padding: 8px 16px; cursor: pointer; font-size: 14px;">
                Remover todas as cidades
            </button>
        </div>
        <div id="errorMsg" class="error"></div>
        
        <div class="consent-checkbox">
            <label>
                <input type="checkbox" id="consentCheckbox" required>
                <span class="consent-text">
                    Autorizo o Centro de Excelência em Estudos, Monitoramento e Previsões Ambientais do Cerrado (CEMPA) 
                    a enviar e-mails e notificações sobre avisos meteorológicos, novidades e comunicados pertinentes 
                    ao funcionamento do sistema de avisos. Posso cancelar este consentimento a qualquer momento.
                </span>
            </label>
        </div>
        
        <button type="submit" id="submitBtn">Cadastrar</button>
        <div id="unsubscribeContainer" style="display: none; margin-top: 15px; text-align: center;">
            <button type="button" id="unsubscribeBtn" style="background: #dc3545; color: white; border: none; border-radius: 4px; padding: 10px 20px; cursor: pointer; font-size: 14px; width: 100%;">
                Descadastrar
            </button>
        </div>
    </form>

    <!-- Modal customizado -->
    <div id="customModal" class="custom-modal">
        <div class="modal-content">
            <div class="modal-title" id="modalTitle"></div>
            <div class="modal-message" id="modalMessage"></div>
            <div class="modal-buttons" id="modalButtons">
                <button class="modal-btn modal-btn-primary" id="modalOkBtn">OK</button>
            </div>
        </div>
    </div>

    <script>
        const cityBlocks = {};
        let isEditing = false;

        // Funções para o modal customizado
        function showModal(title, message, buttons = ['OK']) {
            const modal = document.getElementById('customModal');
            const modalTitle = document.getElementById('modalTitle');
            const modalMessage = document.getElementById('modalMessage');
            const modalButtons = document.getElementById('modalButtons');
            
            modalTitle.textContent = title;
            modalMessage.textContent = message;
            
            // Limpar botões existentes
            modalButtons.innerHTML = '';
            
            // Adicionar botões
            buttons.forEach((button, index) => {
                const btn = document.createElement('button');
                btn.textContent = button.text || button;
                btn.className = 'modal-btn';
                
                if (button.type === 'danger') {
                    btn.classList.add('modal-btn-danger');
                } else if (button.type === 'secondary') {
                    btn.classList.add('modal-btn-secondary');
                } else {
                    btn.classList.add('modal-btn-primary');
                }
                
                btn.onclick = () => {
                    hideModal();
                    if (button.onClick) button.onClick();
                };
                
                modalButtons.appendChild(btn);
            });
            
            modal.style.display = 'block';
        }
        
        function hideModal() {
            document.getElementById('customModal').style.display = 'none';
        }
        
        // Fechar modal ao clicar fora dele
        document.getElementById('customModal').addEventListener('click', function(e) {
            if (e.target === this) {
                hideModal();
            }
        });

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
            
            // Mostrar o botão de remover todas as cidades se houver pelo menos uma cidade
            updateRemoveAllButton();
        }

        // Função para atualizar a visibilidade do botão de remover todas as cidades
        function updateRemoveAllButton() {
            const removeAllContainer = document.getElementById('removeAllCitiesContainer');
            const cityBlocksCount = Object.keys(cityBlocks).length;
            
            if (cityBlocksCount > 0) {
                removeAllContainer.style.display = 'block';
            } else {
                removeAllContainer.style.display = 'none';
            }
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
                    
                    // Agrupar alertas por cidade
                    const cityAlerts = {};
                    userData.alerts.forEach(alert => {
                        if (!cityAlerts[alert.city]) {
                            cityAlerts[alert.city] = [];
                        }
                        // Cada alert.types é um array com um elemento, então usamos o primeiro
                        const alertType = alert.types[0];
                        if (!cityAlerts[alert.city].includes(alertType)) {
                            cityAlerts[alert.city].push(alertType);
                        }
                    });
                    
                    // Criar blocos para cada cidade com seus tipos agrupados
                    Object.keys(cityAlerts).forEach(city => {
                        createCityBlock(city, cityAlerts[city]);
                    });
                    
                    // Marcar como edição
                    isEditing = true;
                    // Alterar texto do botão principal e mostrar botão de descadastrar
                    document.getElementById('submitBtn').textContent = 'Atualizar';
                    document.getElementById('unsubscribeContainer').style.display = 'block';
                } else if (response.status === 404) {
                    // Alterar texto do botão principal e esconder botão de descadastrar
                    document.getElementById('submitBtn').textContent = 'Cadastrar';
                    document.getElementById('unsubscribeContainer').style.display = 'none';
                }
            } catch (error) {
                console.error('Erro ao buscar usuário:', error);
                document.getElementById('errorMsg').textContent = 'Erro ao verificar email.';
                document.getElementById('errorMsg').style.color = '#dc3545';
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
                    showModal(
                        'Sucesso!', 
                        isEditing ? 'Usuário atualizado com sucesso!' : 'Usuário cadastrado com sucesso!'
                    );
                    document.getElementById('alertForm').reset();
                    document.getElementById('cityBlocks').innerHTML = '';
                    document.getElementById('errorMsg').textContent = '';
                    for (const key in cityBlocks) delete cityBlocks[key];
                    isEditing = false;
                    updateRemoveAllButton();
                    document.getElementById('submitBtn').textContent = 'Cadastrar';
                    document.getElementById('unsubscribeContainer').style.display = 'none';
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

        // Adicionar evento para o botão de remover todas as cidades
        document.getElementById('removeAllCitiesBtn').addEventListener('click', function() {
            showModal(
                'Confirmar ação',
                'Tem certeza que deseja remover todas as cidades?',
                [
                    { text: 'Cancelar', type: 'secondary' },
                    { 
                        text: 'Remover', 
                        type: 'danger',
                        onClick: function() {
                            document.getElementById('cityBlocks').innerHTML = '';
                            for (const key in cityBlocks) delete cityBlocks[key];
                            updateRemoveAllButton();
                        }
                    }
                ]
            );
        });

        window.removeCityBlock = function(city) {
            const block = cityBlocks[city];
            if (block) {
                block.remove();
                delete cityBlocks[city];
                updateRemoveAllButton();
            }
        }

        // Função para obter parâmetros da URL
        function getUrlParameter(name) {
            name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
            var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
            var results = regex.exec(location.search);
            return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
        }

        // Verificar se há email na URL e preencher automaticamente
        document.addEventListener('DOMContentLoaded', function() {
            const emailFromUrl = getUrlParameter('email');
            if (emailFromUrl) {
                const emailField = document.getElementById('email');
                emailField.value = emailFromUrl;
                
                // Validar o email e buscar dados do usuário
                if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailFromUrl)) {
                    fillUserData(emailFromUrl);
                }
            }
        });

        // Adicionar evento para o botão de descadastrar
        document.getElementById('unsubscribeBtn').addEventListener('click', async function() {
            const email = document.getElementById('email').value.trim();
            if (!email) return;
            
            showModal(
                'Confirmar descadastro',
                'Tem certeza que deseja descadastrar este email?',
                [
                    { text: 'Cancelar', type: 'secondary' },
                    { 
                        text: 'Descadastrar', 
                        type: 'danger',
                        onClick: async function() {
                            try {
                                const currentUrl = window.location.origin;
                                const res = await fetch(`${currentUrl}/users/email?email=${encodeURIComponent(email)}`, {
                                    method: 'DELETE'
                                });
                                if (res.status === 200) {
                                    showModal('Sucesso!', 'Usuário descadastrado com sucesso.');
                                    document.getElementById('alertForm').reset();
                                    document.getElementById('cityBlocks').innerHTML = '';
                                    document.getElementById('errorMsg').textContent = '';
                                    for (const key in cityBlocks) delete cityBlocks[key];
                                    isEditing = false;
                                    updateRemoveAllButton();
                                    document.getElementById('submitBtn').textContent = 'Cadastrar';
                                    document.getElementById('unsubscribeContainer').style.display = 'none';
                                } else {
                                    showModal('Erro', 'Erro ao descadastrar usuário.');
                                }
                            } catch (err) {
                                showModal('Erro', 'Erro na comunicação com o servidor.');
                            }
                        }
                    }
                ]
            );
        });
    </script>
</body>

</html>
    """
    
    # Substituir o marcador {city_options} pelo HTML gerado dinamicamente
    form_html = form_html.replace('{city_options}', generate_city_options.__func__())