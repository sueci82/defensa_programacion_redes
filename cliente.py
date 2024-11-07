import socket
import threading

# Configuracion del socket del cliente

IP = "127.0.0.1"
PUERTO = 1234
BUFFER = 1024

def iniciar_cliente():
    #crea el socket para el cliente
    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente_socket.connect((IP, PUERTO))

    #Le paso el nick al servidor
    nickname = input(f"{cliente_socket.recv(BUFFER).decode('utf-8')}")
    cliente_socket.send(nickname.encode('utf-8'))

    # Creo e inicializo hilos para enviar y recibir los mensajes

    threading.Thread(target=recibir_mensajes, args=(cliente_socket,)).start()
    threading.Thread(target=enviar_mensajes, args=(cliente_socket,)).start()

def recibir_mensajes(cliente_socket):
        while True:
            try:
                mensaje = cliente_socket.recv(BUFFER).decode('utf-8')
                if not mensaje:
                    break
                print(mensaje)
            except:
                print("Se cerro la conexión con el servidor")
                cliente_socket.close()
                break

def enviar_mensajes(cliente_socket):
    while True:
        mensaje = input()
        if mensaje.lower() == '/salir':
            cliente_socket.send(mensaje.encode('utf-8'))
            cliente_socket.close()
            break
        cliente_socket.send(mensaje.encode('utf-8'))

iniciar_cliente()