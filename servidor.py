import socket
import threading
import mysql.connector
from datetime import datetime 

# Configuracion del socket del servidor

IP = "127.0.0.1"
PUERTO = 1234
BUFFER = 1024

# Configuracion de la base de datos

db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'redes' #ACA VA EL NOMBRE DE TU BASE DE DATOS
}

# Declarar una lista de clientes CONECTADOS

clientes = []
# clientes = [    cliente = [username, socket_cliente]      ]
# funcion para crear la conexion de la base de datos

def crear_conexion():
    return mysql.connector.connect(**db_config)

# Funcion que va a manejar la comunicacion con el cliente
# o sea, va a recibir los mensajes y responder segun el mensaje
# y también va a verificar si el cliente existe o no, y agregarlo
# o no según corresponda a la base de datos y/o a la lista de clientes conectados

def manejar_cliente(cliente_socket):
    conn = crear_conexion()
    cursor = conn.cursor()
    print("Cliente conectado.")

    cliente_socket.send("Ingrese su nickname: ".encode('utf-8'))
    nickname = cliente_socket.recv(BUFFER).decode('utf-8')

    # Verificar si el cliente ya está en la lista de conectados
    if not any(nick == nickname for nick, _ in clientes):
        clientes.append((nickname, cliente_socket))
        cliente_socket.send('Su usuario fue agregado a la lista de conectados.'.encode('utf-8'))
    else:
        cliente_socket.send('Su usuario ya forma parte de la lista de conectados.'.encode('utf-8'))

    # Actualizar o insertar el cliente en la base de datos

    EstaRegistrado = verificacion_cliente(nickname, cursor, conn)
    cliente_socket.send(EstaRegistrado.encode('utf-8'))

    # Ejecuto el bucle infinito para empezar a atender los mensajes/consultas de los clientes
    while True:
        try: #Intenta hacer esto

            #intento recibir mensajes
            mensaje = cliente_socket.recv(BUFFER).decode('utf-8')
            
            #si no hay ningun mensaje, termino de atender al cliente (finaliza el bucle infinito)
            if not mensaje:
                break
            print(f"mensaje recibido: {mensaje}")

            if mensaje.startswith("/"):
                ejecutar_comando(mensaje, cliente_socket, nickname)
            elif mensaje.startswith("#"):
                destino_nick, mensaje_privado = mensaje[1:].split(" ", 1)
                enviar_privado(destino_nick, mensaje_privado, nickname) # nickname = nick del remitente 
            else:
                enviar_a_todos(f"{nickname}: {mensaje}", cliente_socket)
        except: #Si ocurre un error, informalo
                print("Error en la comunicacion con el cliente.")
                break
        
    clientes.remove((nickname, cliente_socket))
    cliente_socket.close()
    conn.close()
    print(f"Conexion cerrada con {nickname}.")

# FUNCION PARA LOS COMANDOS

def ejecutar_comando(mensaje, cliente_socket, nickname):
    if mensaje == '/listar':
        cliente_socket.send("\nUsuarios conectados:\n".encode('utf-8'))
        for nick, _ in clientes:
            cliente_socket.send(f"- {nick}\n".encode('utf-8'))
    elif mensaje == '/salir':
        cliente_socket.send("Desconectando...".encode('utf-8'))
        clientes.remove((nickname, cliente_socket))
        cliente_socket.close()
    elif mensaje == "/username":
        cliente_socket.send(f"Tu nickname es: {nickname}".encode('utf-8'))
    elif mensaje == '/hora':
        hora_actual = datetime.now().strftime("%H:%M:%S")
        cliente_socket.send(f"La hora actual es: {hora_actual}".encode('utf-8'))
    elif mensaje == "/ayuda":
        cliente_socket.send((
            "Comandos disponibles:\n"
            "/listar - Muestra los usuarios conectados\n"
            "/salir - Desconecta al cliente del servidor\n"
            "/username - Muestra tu nickname\n"
            "/hora - Muestra la hora actual\n"
            "/ayuda - Muestra esta lista de comandos\n"
        ).encode('utf-8'))
    else:
        cliente_socket.send("Comando no reconocido. Usa /ayuda para ver los comandos existentes.".encode('utf-8'))

# FUNCION PARA ENVIAR MENSAJE A TODOS

def enviar_a_todos(mensaje, emisor_socket):
    for nickname, cliente_socket in clientes:
        if cliente_socket != emisor_socket:
            cliente_socket.send(mensaje.encode('utf-8'))

# FUNCION PARA ENVIAR MENSAJES PRIVADOS

def enviar_privado(destino_nick, mensaje_privado, remitente):
    for nickname, cliente_socket in clientes:
        if nickname == destino_nick:
            cliente_socket.send(f"MSG Privado de {remitente}: {mensaje_privado}".encode('utf-8'))

# FUNCION para verificar si el cliente ya existia en la base de datos

def verificacion_cliente(nickname, cursor, conn):
    # SELECCIONAME EL NICKNAME DE LA TABLA CLIENTES SI NICKNAME ES IGUAL AL NICKNAME QUE TE PASO
    sql = "SELECT nickname FROM clientes WHERE nickname = (%s)"
    cursor.execute(sql, (nickname,))
    resultado = cursor.fetchone()

    print("Resultado de verificación:", resultado)

    if resultado:
        # Si el cliente existe, actualizamos la ultima conexion
        sql_update = "UPDATE clientes SET connected_at = %s WHERE nickname = %s"
        cursor.execute(sql_update, (datetime.now(), nickname))
        conn.commit()
        return f"Bienvenido de nuevo, {nickname}. Ultima conexión actualizada."
    else:
        sql_insert = "INSERT INTO clientes (nickname) VALUES (%s)"
        cursor.execute(sql_insert, (nickname,))
        conn.commit()
        return f"Bienvenido, {nickname}. Has sido registrado."
    


# CREAMOS LA FUNCION PARA INICIAR EL SERVIDOR Y CREAR EL SOCKET

def iniciar_servidor():
    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor_socket.bind((IP, PUERTO))
    servidor_socket.listen(5)
    print(f"Servidor escuchando en {IP}, {PUERTO}")

    while True:
        # En un bucle infinito, acepto la conexion con los clientes
        cliente_socket, _ = servidor_socket.accept()
        threading.Thread(target=manejar_cliente, args=(cliente_socket,)).start()
        # Se crea un hilo que va a ejecutar esta funcion (primer paramatro) y le va a pasar
        # como parametro el cliente (segundo parametro)

iniciar_servidor()