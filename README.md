# password-manager-dnie


Gestor de Contraseñas con DNI Electrónico (DNIe)
Un gestor de contraseñas de escritorio seguro que utiliza las capacidades criptográficas del DNI electrónico español para el cifrado y acceso a los datos. La aplicación está desarrollada en Python con una interfaz gráfica creada con Pygame.

Características Principales
Máxima Seguridad con DNIe: La clave maestra de la base de datos se deriva de una firma digital única generada por el DNIe, lo que requiere la posesión física de la tarjeta y el conocimiento del PIN.

Cifrado Fuerte: La base de datos de contraseñas está completamente cifrada utilizando el algoritmo AES-256 en modo GCM, que garantiza confidencialidad y autenticidad.

Archivos de Datos Anónimos: Los nombres de los archivos de la base de datos se generan a partir de un hash del número de serie del DNIe, evitando que se pueda identificar al usuario a partir de los archivos guardados.

Interfaz Gráfica Intuitiva: Una GUI sencilla y funcional creada con Pygame que permite gestionar las contraseñas de forma visual.

Generador de Contraseñas Seguras: Incluye una herramienta para generar contraseñas aleatorias y robustas de longitud variable (15-25 caracteres).

Portapapeles Seguro: Al copiar una contraseña, esta se elimina automáticamente del portapapeles después de 30 segundos para mayor seguridad.

Funcionamiento de la Seguridad 🔐
Este gestor no utiliza una contraseña maestra tradicional. En su lugar, implementa un sistema de seguridad basado en la criptografía de clave pública del DNIe.

Valor Desafío (C): La primera vez que se ejecuta, la aplicación crea un número aleatorio único de 64 bits, llamado C, que es común para la aplicación.

Firma Digital (S): Para acceder, el usuario introduce su PIN. El DNIe utiliza su clave privada para "firmar" el valor C, generando una firma digital única S. Esta firma es diferente para cada DNIe.

Derivación de Clave (K): La firma S se procesa con un hash SHA-256 para derivar una clave de cifrado simétrica, K.

Descifrado de la Clave Maestra (K_db): La clave K se utiliza para descifrar la clave maestra de la base de datos (K_db), que está almacenada en un archivo.

Acceso a la Base de Datos: Finalmente, K_db se utiliza para descifrar la base de datos principal que contiene todas las contraseñas del usuario.

Este método garantiza que solo la persona que posea el DNIe físico y conozca el PIN correcto pueda generar la firma S necesaria para descifrar los datos.

Requisitos Previos 📋
Antes de ejecutar el programa, asegúrate de tener lo siguiente:

Python 3.9 o superior.

Las siguientes librerías de Python. Puedes instalarlas con pip:

Bash

pip install pygame pyscard pyperclip cryptography python-pkcs11
Software del DNI Electrónico: Es imprescindible tener instalados los drivers oficiales del DNIe en tu sistema.

Puedes descargarlos desde la web oficial del Cuerpo Nacional de Policía.

El programa está configurado para usar la librería opensc-pkcs11.dll. Asegúrate de que la ruta en manejo_datos.py coincida con tu instalación si es necesario.

Instalación y Ejecución 🚀
Clona o descarga este repositorio en tu máquina local.

Abre una terminal en la carpeta del proyecto.

Instala las dependencias mencionadas en los requisitos previos.

Asegúrate de tener un lector de DNIe conectado y el DNIe insertado.

Ejecuta el script principal:

Bash

python Inicio_Gestor.py
Estructura del Proyecto 📂
Inicio_Gestor.py: Punto de entrada de la aplicación. Muestra la pantalla de bienvenida.

detectar_dnie.py: Lógica de bajo nivel para detectar la presencia de un lector y una tarjeta.

detectar_dnie_gui.py: Interfaz gráfica para el proceso de detección inicial.

verificar_dnie_gui.py: Interfaz gráfica que solicita el PIN y gestiona la verificación.

manejo_datos.py: El núcleo de la aplicación. Gestiona toda la lógica criptográfica, la interacción con el DNIe y el manejo de la base de datos.

Interfaz_Contraseñas.py: La ventana principal donde se listan y gestionan las contraseñas.

Nombre_Contraseña.py: La ventana emergente para añadir o editar entradas.

generador_contraseñas.py: Utilidad para la generación de contraseñas seguras.

Autores
Enrique Landa

Ruben Sanz
