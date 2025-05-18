# Documentação Técnica CEMPA
## 1. Introdução
### 1.1. Objetivo do Documento
Este documento possui o objetivo de esclarecer e registrar informações pertinentes sobre o projeto proposto bem como sua proposta, design, tecnologias, objetivos e escopo do projeto, contribuindo para com a clareza do entendimento do mesmo e para também em futuras manutenções ou melhorias.
### 1.2. Escopo do Projeto
O projeto se trata de um sistema de envio de notificações climáticas, com o objetivo de gerar avisos perante a condições incomuns que sejam de interesse público ou privado, contribuindo para amenizar eventuais problemas assim como para auxiliar no planejamento das atividades de seus usuários.
O sistema é composto por 3 módulos com responsabilidades únicas, mas que trabalharão em conjunto para gerar e enviar os alertas aos usuários interessados, são eles:
Módulo de Gerenciamento de Usuários: módulo responsável por permitir o cadastro de usuários, assim como suas preferências por alertas.
Módulo de Geração de Alertas: módulo responsável por coletar e interpretar os dados do CEMPA e gerar os alertas caso encontre condições necessárias para a emissão do alerta
Módulo de Divulgação de Alertas: módulo de emissão dos alertas gerados para os usuários interessados.
		Dessa forma, a intenção do squad é entregar um mvp do sistema e sua documentação visando facilitar sua manutenção e adição de novas funcionalidades, sendo que o mvp se trata de uma versão inicial do sistema, mas com os alertas limitados à temperatura e umidade do ar abrangendo apenas a cidade de Goiânia, desta forma os alertas das demais variáveis meteorológicas e o envio para outras cidades de Goiás ficarão de se implementados em atualizações futuras.	
### 1.3. Definições, Siglas e Abreviações
### 1.4. Referências (normas, sites, artigos usados)
## 2. Visão Geral do Sistema
### 2.1. Descrição do Problema
O cliente possui deficiência ao divulgar suas previsões climáticas, sendo que seus principais meios de comunicação possui baixo alcance, dessa forma as previsões realizadas são acessíveis apenas para um pequeno número de pessoas que deverão ativamente acompanhar as atualizações realizadas pelo cliente, sendo que, ainda assim as informações atualizadas podem não suprir as necessidades do demandante.
### 2.2. Impacto do Problema
Dessa maneira, o problema é impactante quanto à baixa personalização da comunicação e, principalmente quanto a sua ineficiência em situações críticas, onde o CEMPA poderia ter uma atuação mais decisiva ao contribuir com a mitigação de danos causados por eventos climáticos.
### 2.3. Proposta de Solução
Diante da problemática apresentada, chegamos à conclusão que um sistema de alertas por subscrição (em que o cliente interessado possa se inscrever para receber alertas climáticos de seu interesse) possa amenizar esse problema facilitando a distribuição das previsões formuladas pelo CEMPA para seus clientes sem que estes precisem procurar os canais do instituto de maneira ativa.
### 2.4. Público-Alvo e Stakeholders
Este projeto possui como público alvo os clientes e usuários dos serviços prestados pelo CEMPA, por exemplo: 
Órgãos públicos 
Órgãos ambientais
Defesa civil
Agricultores
População civil
		E os stakeholders do projeto incluem:
CEMPA
SECTI
UFG
Governo Estadual
### 2.5. Limitações e Premissas


## 3. Requisitos
### 3.1. Requisitos Funcionais
		Módulo de controle de usuários:
O sistema deve cadastrar usuários recolhendo informações sobre nome, email, cidade e alerta desejado pelos usuários.
O sistema deve garantir que há apenas um usuário cadastrado por email
O sistema deve armazenar as informações dos usuários cadastrados em um banco de dados
O sistema deve armazenar informações para log, como data e horário de cadastro de cada usuário
		Módulo de Geração de Alertas:
O sistema deve receber informações climáticas geradas pelo CEMPA.
O sistema deve interpretar essa informações buscando identificar dados acima da média das normais disponibilizadas no site do INMEP (https://portal.inmet.gov.br/normais ).
O sistema deverá gerar alertas diários, se houver condições necessárias.
		Módulo de Envio de Alertas:
O sistema deve enviar os alertas gerados para o email dos usuários cadastrados.
O sistema deve realizar envios diariamente se houver alertas gerados, caso contrário, não haverá envio.
### 3.2. Requisitos Não Funcionais
Módulo de Controle de Usuários
O sistema deve validar entradas para evitar injeções SQL ou scripts maliciosos.
Os dados de usuários (nome, email, cidade, alerta) devem ser trafegados exclusivamente por conexões seguras (HTTPS).
Informações sensíveis como email devem ser protegidas com acesso restrito e armazenadas de forma segura.
A API de cadastro deve seguir um padrão RESTful com documentação compatível com Swagger/OpenAPI.
O código deve estar estruturado para permitir testes unitários e de integração com cobertura mínima de 80%.
Cada cadastro de usuário deve ser logado com data e hora do registro.
As atualizações e exclusões também devem ser rastreadas nos logs.
O banco de dados deve garantir a unicidade do email via constraint no nível da tabela.
Os dados devem estar disponíveis mesmo após reinício do sistema (persistência física no volume).
 Módulo de Geração de Alertas
O sistema deve processar dados climáticos recebidos em até 10 segundos após o recebimento.
A verificação diária de dados anômalos deve ocorrer no máximo 5 minutos após a coleta.
A comunicação com o CEMPA deve ocorrer por meio de endpoints autenticados ou canais confiáveis (ex: SFTP, APIs REST protegidas).
Todos os dados de entrada devem ser validados antes do processamento.
O processamento de dados deve ser desacoplado por tipo de dado (chuva, temperatura, umidade, etc.) para facilitar ajustes modulares.
O sistema deve permitir a substituição do algoritmo de interpretação sem impactar o restante da arquitetura.
Cada alerta gerado deve conter uma referência clara ao conjunto de dados que o originou.
Logs de geração devem conter horário, tipo de evento climático e gravidade.
Módulo de Envio de Alertas
O envio de alertas deve ser concluído em até 5 minutos após a geração do alerta.
O sistema deve ser capaz de enviar mensagens para até 10.000 usuários com desempenho aceitável (com escalonamento se necessário).
O envio de emails deve utilizar servidores autenticados via SMTP com credenciais armazenadas em variáveis de ambiente.
Informações de email dos usuários não devem ser expostas nos logs.
As mensagens devem ser formatadas em HTML e texto simples (multiformato), com clareza e objetividade.
O sistema deve permitir personalização do conteúdo do alerta conforme o tipo de evento.
Cada envio de alerta deve ser registrado com: horário, email destinatário, e tipo de alerta enviado.



### 3.3. Regras de Negócio
Restrições específicas do domínio.


## 4. Arquitetura do Sistema
### 4.1. Visão Geral da Arquitetura
### 4.2. Tecnologias e Ferramentas Utilizadas
O sistema é feito na linguagem Python com o framework Flask, para a criação de API e acesso ao banco de dados PostgreSQL com a extensão SQLAlchemy. O projeto está alocado em um ambiente Docker que faz o suporte às tecnologias necessárias para a execução do projeto.
### 4.3. Padrões de Projeto e Boas Práticas
### 4.4. Diagrama de Componentes (UML)


## 5. Modelagem e Diagramas
### 5.1. Diagrama de Casos de Uso (atores e funcionalidades)
### 5.2. Diagrama de Atividades (fluxos internos)
### 5.3. Diagrama de Sequência (interação entre módulos)
### 5.4. Diagrama de Classes (entidades e atributos)
### 5.5. Diagrama BPMN


## 6. Banco de Dados
### 6.1. Modelo Entidade-Relacionamento (ER)
### 6.2. Descrição das Tabelas
### 6.3. Estratégias de Backup e Recuperação


## 7. Integrações Externas
### 7.1. APIs utilizadas
### 7.2. Webhooks, serviços de terceiros
### 7.3. Estratégias de autenticação e segurança


## 8. Estratégia de Testes
### 8.1. Plano de Testes
### 8.2. Casos de Teste
### 8.3. Ferramentas de Teste (ex: JUnit, Postman)


## 9. Deploy e Ambiente
### 9.1. Ambiente de Desenvolvimento
### 9.2. Ambiente de Homologação
### 9.3. Ambiente de Produção
### 9.4. Scripts de Deploy (Docker, Kubernetes, etc)


## 10. Anexos
### 10.1 Protótipos de tela
### 10.2 Wireframes
### 10.3 Outros documentos complementares


## 11. Histórico de Alterações
Versão
Data
Autor
Descrição
