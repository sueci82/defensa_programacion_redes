import socket
import threading
import mysql.connector
from datetime import datetime

# Configuración
IP = "127.0.0.1"
PUERTO = 1234
BUFFER = 1024

# Base de datos
db_config = {
    'user': '27293176855',
    'password': '',
    'host': 'localhost',
    'database': 'redes'
}

# Lista de clientes
clientes = []

def crear_conexion():
    return mysql.connector.connect(**db_config)

def manejar_cliente(cliente_socket):
    conn = crear_conexion()
    cursor = conn.cursor()

    print("Cliente conectado.")
    cliente_socket.send("Ingresa tu nickname: ".encode('utf-8'))
    nickname = cliente_socket.recv(BUFFER).decode('utf-8')

    # Verificar si el cliente ya está en la lista
    if not any(nick == nickname for nick, _ in clientes):
        clientes.append((nickname, cliente_socket))
        cliente_socket.send('El cliente fue agregado a la lista'.encode('utf-8'))
    else:
        cliente_socket.send('Ya estás en la lista, continuando...'.encode('utf-8'))

    # Actualizar o insertar en la BBDD
    cliente_socket.send(verificar_cliente(nickname, cursor, conn).encode('utf-8'))

    while True:
        try:
            mensaje = cliente_socket.recv(BUFFER).decode('utf-8')
            if not mensaje:
                break

            print(f"mensaje recibido: {mensaje}")

            if mensaje.startswith("/"):
                ejecutar_comando(mensaje, cliente_socket, nickname)
            elif mensaje.startswith("#"):
                destino_nick, mensaje_privado = mensaje[1:].split(" ", 1)
                enviar_privado(destino_nick, mensaje_privado, nickname)
            else:
                enviar_a_todos(f"{nickname}: {mensaje}", cliente_socket)
        except:
            print("Error en la comunicacion")
            break

    clientes.remove((nickname, cliente_socket))
    cliente_socket.close()
    conn.close()
    print("Conexion cerrada.")

def verificar_cliente(nickname, cursor, conn):
    sql = "SELECT nickname FROM clientes WHERE nickname = (%s)"
    cursor.execute(sql, (nickname,))
    resultado = cursor.fetchone()
    
    if resultado:
        # Si el cliente ya existe, actualizamos la última conexión
        sql_update = "UPDATE clientes SET connected_at = %s WHERE nickname = %s"
        cursor.execute(sql_update, (datetime.now(), nickname))
        conn.commit()
        return f"Bienvenido de nuevo, {nickname}. Última conexión actualizada."
    else:
        # Insertamos el nuevo cliente
        sql_insert = "INSERT INTO clientes (nickname, connected_at) VALUES (%s, %s)"
        cursor.execute(sql_insert, (nickname, datetime.now()))
        conn.commit()
        return f"Bienvenido, {nickname}. Has sido registrado."

def ejecutar_comando(comando, cliente_socket, nickname):
    if comando == "/listar":
        cliente_socket.send("Usuarios conectados:\n".encode('utf-8'))
        for nick, _ in clientes:
            cliente_socket.send(f"- {nick}\n".encode('utf-8'))
    elif comando == "/salir":
        cliente_socket.send("Desconectando...".encode('utf-8'))
        clientes.remove((nickname, cliente_socket))
        cliente_socket.close()
    elif comando == "/username":
        cliente_socket.send(f"Tu nickname es: {nickname}".encode('utf-8'))
    elif comando == "/ayuda":
        cliente_socket.send((
            "Comandos disponibles:\n"
            "/listar - Muestra los usuarios conectados\n"
            "/salir - Desconecta del servidor\n"
            "/username - Muestra tu nickname\n"
            "/hora - Muestra la hora actual del servidor\n"
            "/ayuda - Muestra esta lista de comandos\n"
        ).encode('utf-8'))
    elif comando == "/hora":
        hora_actual = datetime.now().strftime("%H:%M:%S")
        cliente_socket.send(f"La hora actual es: {hora_actual}".encode('utf-8'))
    else:
        cliente_socket.send("Comando no reconocido. Usa /ayuda para ver los comandos disponibles.".encode('utf-8'))

def enviar_a_todos(mensaje, emisor_socket):
    for nickname, cliente_socket in clientes:
        if cliente_socket != emisor_socket:  # Excluir el cliente que envió el mensaje
            cliente_socket.send(mensaje.encode('utf-8'))

def enviar_privado(destino_nick, mensaje, remitente):
    for nickname, cliente_socket in clientes:
        if nickname == destino_nick:
            cliente_socket.send(f"Privado de {remitente}: {mensaje}".encode('utf-8'))
            return
    print(f"Cliente {destino_nick} no encontrado")

def iniciar_servidor():
    sv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sv_socket.bind((IP, PUERTO))
    sv_socket.listen(5)
    print(f"Servidor escuchando en {IP}, {PUERTO}")

    while True:
        cliente_socket, _ = sv_socket.accept()
        threading.Thread(target=manejar_cliente, args=(cliente_socket,)).start()

iniciar_servidor()

