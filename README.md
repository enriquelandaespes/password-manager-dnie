# password-manager-dnie

Gestor de Contraseñas con DNI Electrónico (DNIe)

Un gestor de contraseñas de escritorio seguro que utiliza las capacidades criptográficas del DNI electrónico español para el cifrado y acceso a los datos. La aplicación está desarrollada en Python con una interfaz gráfica creada con Pygame.
—----------------------------------------------------------------------------------------------------------------------
Características Principales
—----------------------------------------------------------------------------------------------------------------------
Máxima Seguridad con DNIe: La clave que se utiliza para cifrar la clave de la base de datos se basa en la firma de DNI electrónico por lo que es necesario para poder acceder a la base de datos

Cifrado Fuerte: La base de datos está completamente cifrada utilizando el algoritmo AES-256 GCM.

Base de Datos Anónima con JSON: Los nombres de los archivos de la base de datos se generan a partir de un hash del número de serie del DNIe, evitando que se pueda identificar al usuario a partir de los archivos guardados.

Interfaz Gráfica Intuitiva: Una GUI sencilla y funcional creada con Pygame que permite realizar todas las operaciones del programa de forma sencilla.

Generador de Contraseñas Seguras: Incluye una herramienta para generar contraseñas aleatorias y robustas de longitud variable (15-25 caracteres).

Portapapeles Seguro: Al copiar una contraseña, esta se elimina automáticamente del portapapeles después de 30 segundos para mayor seguridad. Depende del sistema operativo se puede ver con el historial del portapapeles si está activo, es algo que no se puede cambiar a no ser que se cambie la configuración del propio sistema operativo.
—------------------------------------------------------------------------------------------------------------------
Funcionamiento de la Seguridad 
—------------------------------------------------------------------------------------------------------------------
Este gestor basa su seguridad en el dni por lo que se utilizará su firma, que es accesible únicamente si se posee del dni físico y se conoce su número pin. Para ello se utiliza una clave simétrica y un desafío que deberá ser firmado por el dni para obtener esta clave simétrica.

Número Desafío (C): La primera vez que se ejecuta, la aplicación crea un número aleatorio único de 64 bits, llamado C, que es común para la aplicación y cualquier usuario.

Firma Digital (S): Para acceder, cada usuario introduce el PIN del DNIe. El DNIe utiliza su clave privada para firmar el valor C, generando una firma digital única S. Esta firma es diferente para cada DNIe.

Derivación de Clave (K): La firma S se procesa con un hash SHA-256 para derivar una clave de cifrado simétrica, K, única para cada S, es decir, para cada DNIe.

Descifrado de la Clave Maestra (K_db): La clave K se utiliza para descifrar la clave maestra de la base de datos (K_db), que está almacenada en un archivo de texto.

Acceso a la Base de Datos: Finalmente, K_db se utiliza para descifrar la base de datos JSON principal que contiene todas las contraseñas del usuario.

Este conjunto de claves que se pueden obtener únicamente con el DNIe proporcionan seguridad, integridad y confidencialidad a la hora de gestionar las contraseñas.
—------------------------------------------------------------------------------------------------------------------------
Requisitos Previos 
—------------------------------------------------------------------------------------------------------------------------
Antes de ejecutar el programa, asegúrate de tener lo siguiente:

Python 3.9 o superior.

Las siguientes librerías de Python. 
pygame
pyscard
pyperclip
cryptography
python-pkcs11

Puedes instalarlas con pip:

pip install pygame pyscard pyperclip cryptography python-pkcs11

Software del DNI Electrónico: Es imprescindible tener instalados los drivers oficiales del DNIe en tu sistema. Puedes descargarlos desde la web oficial del Cuerpo Nacional de Policía en el enlace (15/10/2025):
https://www.dnielectronico.es/portaldnie/prf1_cons02.action?pag=ref_1101

El programa está configurado para usar la librería opensc-pkcs11.dll. Asegúrate de que la ruta en manejo_datos.py coincida con tu instalación.

—------------------------------------------------------------------------------------------------------------------
Instalación y Ejecución 
—------------------------------------------------------------------------------------------------------------------
Clona o descarga este repositorio en tu máquina.

Abre una terminal en la carpeta del proyecto (o adjunta la ruta correspondiente).

Instala las dependencias mencionadas en los requisitos previos.

Asegúrate de tener un lector de tarjetas conectado y el DNIe insertado.

Ejecuta el script principal:

python Inicio_Gestor.py

—------------------------------------------------------------------------------------------------------------------
Estructura del Proyecto 
—------------------------------------------------------------------------------------------------------------------
Inicio_Gestor.py: Punto de entrada de la aplicación. Muestra la pantalla de bienvenida y da paso al resto del programa.

detectar_dnie.py: Lógica de bajo nivel para detectar la presencia del lector y del DNIe verificando si hay un lector conectado y en este hay conectado un DNIe.

detectar_dnie_gui.py: Interfaz gráfica para el proceso de detección inicial. Aparece una pantalla de carga mientras se ejecuta la parte lógica.

verificar_dnie_gui.py: Interfaz gráfica que solicita el PIN del DNIe y gestiona la verificación.

manejo_datos.py: El núcleo de la aplicación, lo más importante. Gestiona toda la lógica criptográfica, la interacción con el DNIe y el manejo de la base de datos.

Interfaz_Contraseñas.py: La ventana principal donde se listan y gestionan las contraseñas.

Nombre_Contraseña.py: La ventana emergente para añadir o editar entradas.

generador_contraseñas.py: Utilidad para la generación de contraseñas seguras.

—------------------------------------------------------------------------------------------------------------------
Autores
—------------------------------------------------------------------------------------------------------------------
Enrique Landa

Ruben Sanz

