import socket
import threading

# Configuración
IP = "127.0.0.1"
PUERTO = 1234
BUFFER = 1024

def iniciar_cliente():
    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente_socket.connect((IP, PUERTO))

    # Obtiene el nickname
    nickname = input(f"{cliente_socket.recv(BUFFER).decode('utf-8')}")
    cliente_socket.send(nickname.encode('utf-8'))

    # Inicia hilos de recepción y envío
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
            print("Se ha cerrado la comunicación.")
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
