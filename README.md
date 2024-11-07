

# Servidor de Chat en Python

Este código es un servidor de chat en Python que permite la conexión de múltiples clientes a través de sockets y realiza la gestión de usuarios en una base de datos MySQL. Este chat combina redes, hilos y gestión de base de datos para crear un ambiente de mensajería instantánea sencilla, ideal para pruebas locales o en redes pequeñas.

- **Concurrencia**: al usar threading, el servidor puede manejar múltiples conexiones simultáneas.
- **Comandos Especiales**: permite comandos para gestionar la sesión del cliente y funcionalidades específicas, como mensajes privados y públicos.
- **Base de Datos**: mantiene un registro de los usuarios y sus últimas conexiones para persistir datos y mejorar la experiencia del cliente.

## 1. Importaciones

- `socket`: para manejar la comunicación de red entre el servidor y los clientes.
- `threading`: para permitir la concurrencia, permitiendo que múltiples clientes se conecten y envíen mensajes al mismo tiempo.
- `mysql.connector`: para conectarse y realizar operaciones en la base de datos MySQL.
- `datetime`: para gestionar y registrar la fecha y hora de conexión de los usuarios.

## 2. Constantes de Configuración

- **IP**: dirección IP donde el servidor escuchará conexiones (configurada como 127.0.0.1 para localhost).
- **PUERTO**: puerto de red en el que el servidor escuchará conexiones entrantes (1234 en este caso).
- **BUFFER**: tamaño del buffer para los mensajes recibidos/enviados (1024).

## 3. Configuración de la Base de Datos

- `db_config`: contiene las credenciales de la base de datos, incluyendo el nombre de usuario, contraseña, host y nombre de la base de datos. Se usa para autenticar las conexiones a MySQL.

## 4. Conexión a la Base de Datos (`crear_conexion`)

- Crea y devuelve una conexión a la base de datos MySQL usando la configuración de `db_config`.

## 5. Manejo de Clientes (`manejar_cliente`)

Esta función se ejecuta en un hilo separado por cada cliente que se conecta y realiza lo siguiente:

- Solicita al cliente que introduzca un "nickname" (nombre de usuario).
- Verifica si el cliente ya está en la lista de clientes conectados (`clientes`) y le envía un mensaje de confirmación.
- Verifica la existencia del cliente en la base de datos y registra la conexión o actualiza la última conexión.
- Escucha continuamente los mensajes del cliente:
  - **Comandos** (inician con "/"): ejecutan acciones específicas usando `ejecutar_comando`.
  - **Mensajes privados** (inician con "#"): se envían a un usuario específico usando `enviar_privado`.
  - **Mensajes públicos**: se envían a todos los clientes conectados mediante `enviar_a_todos`.
- En caso de error o desconexión, el cliente se elimina de la lista de clientes y se cierra su conexión.

## 6. Verificación y Registro en la Base de Datos (`verificar_cliente`)

- Verifica si el "nickname" del cliente ya está en la base de datos:
  - Si el cliente existe, actualiza su última conexión.
  - Si es nuevo, lo registra con la fecha y hora actuales.

## 7. Ejecución de Comandos (`ejecutar_comando`)

Procesa comandos específicos ingresados por el cliente:

- `/listar`: envía al cliente una lista de los usuarios conectados.
- `/salir`: desconecta al cliente.
- `/username`: muestra el "nickname" del cliente.
- `/ayuda`: muestra una lista de comandos disponibles.
- `/hora`: envía la hora actual del servidor al cliente.

## 8. Enviar Mensajes Públicos (`enviar_a_todos`)

- Envía un mensaje a todos los clientes conectados excepto al que lo envió, útil para mensajes generales.

## 9. Enviar Mensajes Privados (`enviar_privado`)

- Envía un mensaje a un cliente específico, identificado por su "nickname". Si el destinatario no está conectado, se registra un mensaje en el servidor.

## 10. Inicialización del Servidor (`iniciar_servidor`)

- Crea un socket de servidor TCP, lo asocia a la IP y puerto configurados, y comienza a escuchar conexiones entrantes.
- Cada vez que un cliente se conecta, se lanza un hilo nuevo que ejecuta la función `manejar_cliente`, permitiendo gestionar múltiples clientes de forma concurrente.

## Requisitos para Configuración y Ejecución

- **Configurar la Base de Datos**: Debes tener una base de datos llamada `redes` con una tabla `clientes` que incluya las columnas `nickname` y `connected_at` para almacenar los nombres de usuario y la fecha/hora de conexión.
- **Ejecución del Servidor**:
  - Ejecuta el script en una máquina con Python instalado y una base de datos MySQL configurada con los parámetros indicados.
  - Al ejecutar el script, el servidor comenzará a escuchar en `127.0.0.1:1234`.
  - Los clientes pueden conectarse al servidor y comunicarse usando aplicaciones de socket TCP o scripts de cliente.
