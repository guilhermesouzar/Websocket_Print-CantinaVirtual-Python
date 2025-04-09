import os
import json
import asyncio
import websockets
import win32print
import win32api
import win32con
import sys

# Determina o diretório do executável
if getattr(sys, 'frozen', False):
    # Se o código está rodando em um executável gerado pelo PyInstaller
    application_path = os.path.dirname(sys.executable)
else:
    # Se o código está rodando em um script Python normal
    application_path = os.path.dirname(os.path.abspath(__file__))

# Caminho do arquivo de configuração
CONFIG_PATH = os.path.join(application_path, 'config.json')

# Função para ler o arquivo de configuração
def ler_configuracao():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as file:
            return json.load(file)
    return None

# Função para escrever no arquivo de configuração
def escrever_configuracao(printer_name, printer_size):
    config = {"printer_name": printer_name, "printer_size": printer_size}
    with open(CONFIG_PATH, 'w') as file:
        json.dump(config, file, indent=2)

# Função para listar impressoras disponíveis
def listar_impressoras():
    return win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)

# Função para escolher a impressora e o tamanho do papel
def escolher_impressora():
    impressoras = listar_impressoras()
    print("Impressoras disponíveis:")
    for i, impressora in enumerate(impressoras):
        print(f"{i + 1}. {impressora[2]}")

    escolha = int(input("Digite o número da impressora que deseja usar: ")) - 1
    if 0 <= escolha < len(impressoras):
        printer_name = impressoras[escolha][2]
    else:
        print("Impressora inválida.")
        exit(1)

    # Escolha do tamanho do papel
    printer_size = input("Escolha o tamanho da impressora (80mm ou 48mm): ").strip().lower()
    while printer_size not in ["80mm", "48mm"]:
        print("Tamanho inválido. Escolha entre 80mm ou 48mm.")
        printer_size = input("Escolha o tamanho da impressora (80mm ou 48mm): ").strip().lower()

    return printer_name, printer_size

# Função para enviar comandos ESC/POS para a impressora
def imprimir_pedido(pedido, printer_name, printer_size):
    try:
        hprinter = win32print.OpenPrinter(printer_name)
        hprinter_info = win32print.GetPrinter(hprinter, 2)
        pdc = win32print.OpenPrinter(printer_name)

        try:
            # Junta todos os comandos antes de enviar para a impressora
            commands = b"".join([
                b'\x1B\x40',  # Inicializa a impressora
                b'\x1B\x21\x10',  # Define o tamanho do texto
                b'\x1B\x61\x01',
                f"{pedido['aluno']}\n".encode('utf-8'),
            ])

            if 'turma' in pedido and pedido['turma']:
                commands += f" {pedido['turma']}\n".encode('utf-8')

            commands += b'--------------------\n\n'

            if isinstance(pedido['detalhes'], list):
                for item in pedido['detalhes']:
                    commands += b'\x1B\x61\x00'
                    commands += f"{item['quantidade']} {item['nome']}\n".encode('utf-8')

            commands += b'\x1B\x61\x01'
            commands += b'--------------------\n'

            if 'observacoes' in pedido and pedido['observacoes']:
                commands += f"Obs: {pedido['observacoes']}\n".encode('utf-8')

            if 'dataAgendado' in pedido and pedido['dataAgendado']:
                commands += f"Data Agendada: {pedido['dataAgendado']}\n".encode('utf-8')

            if 'tipoDaEntrega' in pedido and pedido['tipoDaEntrega']:
                commands += f"Entrega: {pedido['tipoDaEntrega']}\n".encode('utf-8')

            commands += f"Total: R$ {pedido['valorTotalPedido']}\n".encode('utf-8')
            commands += f"Data: {pedido['dataRealizado']}\n".encode('utf-8')

            # Espaçamento personalizável de acordo com o tamanho da impressora
            if printer_size == "80mm":
                commands += b'\n\n\n\n\n\n'  # 6 linhas para 80mm
            elif printer_size == "48mm":
                commands += b'\n\n'  # 2 linhas para 48mm

            # Adiciona um espaço extra antes do corte para evitar cortes prematuros
            commands += b'\x1B\x69'  # Comando de corte


            # Envia tudo de uma vez
            win32print.StartDocPrinter(hprinter, 1, ("Pedido", None, "RAW"))
            win32print.StartPagePrinter(hprinter)
            win32print.WritePrinter(hprinter, commands)
            win32print.EndPagePrinter(hprinter)
            win32print.EndDocPrinter(hprinter)

            print("Pedido impresso com sucesso.")
            return True
        finally:
            win32print.ClosePrinter(hprinter)
    except Exception as e:
        print(f"Erro ao imprimir: {e}")
        return False

# Função principal do servidor WebSocket
async def servidor_websocket(websocket):
    print("Cliente conectado")

    async for message in websocket:
        print(f"Recebido: {message}")

        # Processa a mensagem e imprime
        pedido = json.loads(message)
        sucesso = imprimir_pedido(pedido, config["printer_name"], config["printer_size"])

        # Envia uma confirmação de sucesso ao cliente WebSocket
        if sucesso:
            await websocket.send(json.dumps({"success": True, "message": "Pedido impresso com sucesso"}))
        else:
            await websocket.send(json.dumps({"success": False, "message": "Erro ao imprimir"}))

    print("Cliente desconectado")

# Inicia o servidor
async def iniciar_servidor():
    global config
    config = ler_configuracao()

    if config:
        print(f"Usando impressora: {config['printer_name']} ({config['printer_size']}) da configuração.")
    else:
        printer_name, printer_size = escolher_impressora()
        escrever_configuracao(printer_name, printer_size)
        config = {"printer_name": printer_name, "printer_size": printer_size}

    async with websockets.serve(servidor_websocket, "localhost", 8989):
        print("Servidor WebSocket rodando na porta 8989")
        await asyncio.Future()  # Executa indefinidamente

# Executa o servidor
if __name__ == "__main__":
    asyncio.run(iniciar_servidor())