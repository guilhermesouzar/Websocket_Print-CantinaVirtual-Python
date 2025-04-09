# Impressão Instantânea de Pedidos via WebSocket

## Visão Geral

Este projeto implementa um **servidor WebSocket local** em Python, desenvolvido para integrar com a aplicação web **Cantina Virtual**, permitindo a **impressão instantânea de pedidos** diretamente em uma impressora térmica.
O objetivo é garantir agilidade no atendimento de cantinas escolares, automatizando o processo de venda no balcão e de pedidos agendados conforme os clientes fazem suas as solicitações presencial e online.

## Funcionalidades

- Inicialização automática de um servidor WebSocket local
- Comunicação em tempo real entre navegador e impressora via WebSocket
- Compatibilidade com impressoras térmicas de 80mm ou 48mm com e sem guilhotina
- Geração de comandos ESC/POS para impressão formatada
- Armazenamento e reutilização da impressora escolhida em config.JSON
- Manipulação de mensagens JSON com dados dos pedidos
- Confirmação automática de sucesso ou erro na impressão via WebSocket

## Tecnologias Utilizadas

- **Python 3.10+**
- **asyncio** e **websockets** para servidor assíncrono
- **win32print** e **win32api** para comunicação com impressoras no Windows
- **ESC/POS** para comandos de impressão
- **PyInstaller** (opcional) para empacotar como executável standalone

## Exemplo de Fluxo

1. O servidor é iniciado e aguarda conexões na porta 8989.
2. A aplicação web envia via WebSocket um JSON com os dados do pedido.
3. O servidor interpreta o JSON e envia os comandos para a impressora.
4. O cliente WebSocket recebe a confirmação de sucesso ou falha.
   
https://github.com/user-attachments/assets/072fd503-1812-4dc9-9488-172a882ac097

## Motivação
Este projeto surgiu a partir da necessidade de melhorar a eficiência no atendimento de cantinas escolares utilizando o Cantina Virtual, permitindo que os atendentes imprimam um recibo para que os alunos retirem os produtos comprados, também possibilitando a impressão direta dos pedidos recebidos por agendamento.
Trata-se de uma aplicação prática e real, com impacto direto no dia a dia de escolas que utilizam o Cantina Virtual.
