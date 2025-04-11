# Maloca das iCoisas - Hands On Avançado

[Link](https://github.com/gabiel98/gabiel98-maloca-das-icoisas-avancado)

Projeto realizado no curso Maloca das iCoisas, módulo intermediário, pelo grupo 4 - Os Suricatos Cibernéticos.

## Big Picture

### Storytelling

![Big Picture](./big_picture.jpeg)

### Situação Hipotética A FAZER
1. **Paciente faz cirurgia**: O paciente passa pelo procedimento cirúrgico e é encaminhado para a sala de recuperação, onde começa o monitoramento.  
2. **Paciente é monitorado no hospital**: Sensores de movimento, temperatura, pressão arterial e batimentos cardíacos são fixados no corpo do paciente e conectados ao sistema.  
3. **Monitoramento contínuo no hospital**: Os sensores enviam dados em tempo real para a base de dados, e alertas são gerados caso algum parâmetro saia do padrão.  
4. **Paciente recebe alta e vai para casa**: O paciente recebe um dispositivo portátil de monitoramento contínuo, que mantém o envio de dados para os médicos.  
5. **Paciente passa mal em casa**: O sistema detecta alterações nos sinais vitais (ex: febre alta, pressão baixa) e gera um alerta automático.  
6. **Médico recebe notificação e toma providências**: O profissional analisa os dados do paciente remotamente e decide as ações necessárias.  
7. **Ambulância resgata o paciente**: O médico aciona uma ambulância, que recebe as informações do paciente e se dirige até sua residência.  
8. **Paciente retorna ao hospital**: O paciente é readmitido no hospital, onde passa por nova avaliação médica detalhada.  
9. **Acompanhamento do histórico do paciente**: O médico acessa os dados coletados pelo dispositivo para auxiliar no diagnóstico e no tratamento.  
<!--
1. Pessoa doente vai para o hospital, é atendida e admitida na internação;
2. Médicos colocam sensores de temperatura fixos no corpo da paciente;
3. Sensor de temperatura é conectado a uma base de dados alimentada em tempo real;
4. Quando a temperatua do paciente for ≥ 37.8 ºC, o sistema emite um alerta para os profissionais envolvidos;
5. O sistema registra o histórico da temperatura do paciente na base de dados;
6. O profissional verifica condição do paciente após alertas.
-->

## Equipe 

<div align="center">

![Organograma](./organograma.svg)

</div>

- **Product Owner**: Thaís Oliveira Almeida
- **Scrum Master**: Eduardo Henrique Freire Machado

### Equipe de Desenvolvimento 

- Eduardo Henrique Freire Machado;
- Gabriel Peixoto Menezes da Costa;
- Natália Ribeiro de Almada;

## Esquema de Conexão A FAZER

### Dispositivo do Paciente
![Esquema de Conexão](./simulacao_paciente.png) 

### Dispositivo do Médico A FAZER
![Esquema de Conexão](./simulacao_medico.png) 

### Requisitos

#### Hardware

- 1 ESP32;
- 1 Sensor DHT11;
- 2 Galaxy Watch 7;

#### Software

- Flask;
- Streamlit;
- Arduino IDE com as bibliotecas DHT e WiFi;
- Integração com Samsung Health SDK;

## Recursos A FAZER

- [Big Picture](https://www.canva.com/design/DAGX9015E_Y/igNJWoiv6dB_DmXLwmla8g/edit?utm_content=DAGX9015E_Y&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton)
- [Kanban](https://trello.com/invite/b/67f9814a70391e1f77704678/ATTI7b5a3cc73e9dc276db2bb33731acf766C5B92480/hands-on-maloca-avancado)
- [Documento de Requisitos Funcionais](https://docs.google.com/document/d/139STMAsBITp9Wc13MITmVtwTrKqo48Z1CFOeEzPEa9E/edit?usp=sharing)
- [Draft do Dashboard](https://docs.google.com/document/d/1C2ehc7o-pFcvJAB2sn8F75oxu_O5OohuYzn4Uq6_mu0/edit?usp=sharing)
- [Documento de Definição de Pronto]() A FAZER
- [Simulações]() A FAZER
- [Documento de Progresso]() A FAZER
- [Plano de Testes]() A FAZER
- [Pitch]() A FAZER
- [Esquema de Conexão]() A FAZER
- [Documento de Progresso]() A FAZER
