# BACKEND DE TERMINALES - LENGUAJE DE PROGRAMACIÓN Y LIBRERÍAS UTILIZADAS

Para el desarrollo del backend de terminales del presente trabajo, se ha seleccionado el lenguaje de programación Python. Esta elección se fundamenta en su simplicidad, su amplia adopción en el ecosistema de desarrollo web y la disponibilidad de librerías modernas que permiten construir APIs robustas con poco código. Python permite un desarrollo ágil, reduciendo significativamente el tiempo de implementación sin sacrificar la calidad del resultado.

Una de las principales razones para su adopción en este componente es la disponibilidad del framework FastAPI, que permite construir servicios web de alto rendimiento con validación automática de datos y generación de documentación interactiva. A diferencia de otros frameworks más verbosos, FastAPI aprovecha las anotaciones de tipo de Python moderno para reducir el código necesario y detectar errores en tiempo de desarrollo. En el contexto de este proyecto, esto resulta conveniente ya que el servicio de terminales actúa como proveedor de datos para el backend principal, por lo que la claridad y confiabilidad de su interfaz son esenciales.

Además, Python cuenta con SQLAlchemy como ORM (Object-Relational Mapper) de referencia, lo que permite interactuar con la base de datos PostgreSQL de forma segura y expresiva, sin necesidad de escribir SQL manualmente. Esto garantiza que el acceso a datos sea consistente en todo el servicio y facilita el mantenimiento a futuro.

## Librerías a utilizar

Para el desarrollo del prototipo del presente trabajo se utilizaron varias librerías, las más importantes son FastAPI, SQLAlchemy, Pydantic, psycopg2 y pydantic-settings. En el anexo A del trabajo se presenta una breve descripción de cada una de las librerías utilizadas.

---

# PROTOTIPO DEL BACKEND DE TERMINALES

En esta sección se describe cómo se estructuró e implementó el backend de terminales del sistema, incluyendo la organización del código, el modelo de datos y los aspectos más relevantes de cada componente.

El servicio sigue una arquitectura en capas sencilla, separando las responsabilidades entre modelos (estructura de la base de datos), esquemas (validación de datos de entrada y salida), rutas (controladores HTTP) y configuración. Esta separación facilita el mantenimiento y la evolución independiente de cada parte.

## Punto de entrada de la aplicación

La aplicación se inicializa en el módulo `app/main.py`. En este punto se crea la instancia principal de FastAPI, se crean automáticamente las tablas en la base de datos si no existen, y se registran los dos grupos de rutas del servicio.

```python
app = FastAPI(
    title="API Terminales de Buses",
    description="Backend for bus terminal ticket management",
    version="1.0.0",
)

app.include_router(bus_ticket_router)
app.include_router(terminal_router)
```
Figura 1, código del punto de entrada de la aplicación.

La creación automática de tablas se realiza mediante `Base.metadata.create_all(bind=engine)`, que al arrancar el servidor compara el estado del modelo con el de la base de datos y genera las estructuras necesarias si no existen.

## Configuración y conexión a la base de datos

La configuración del servicio se centraliza en `app/config.py` utilizando la librería pydantic-settings. Esto permite definir variables de entorno con un valor por defecto y cargarlas automáticamente desde un archivo `.env`, manteniendo los datos sensibles fuera del código fuente.

```python
class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:1234@localhost:5432/terminales"

    class Config:
        env_file = ".env"
```
Figura 2, código de configuración de variables de entorno.

La conexión a la base de datos se gestiona en `app/database.py` mediante SQLAlchemy. Se crea un motor de conexión y una fábrica de sesiones, y se expone una función `get_db()` que los endpoints utilizan como dependencia para obtener una sesión activa y cerrarla correctamente al finalizar cada petición.

## Arquitectura

El proyecto sigue una estructura de directorios clara y bien definida:

```
backend-terminales/
├── app/
│   ├── config.py       → Variables de entorno y configuración
│   ├── database.py     → Conexión a la base de datos
│   ├── main.py         → Punto de entrada de la aplicación
│   ├── models/
│   │   └── ticket.py   → Modelo de base de datos (BusTicket)
│   ├── schemas/
│   │   └── ticket.py   → Esquemas de validación (Pydantic)
│   └── routes/
│       └── ticket.py   → Controladores HTTP y lógica de rutas
├── .env
└── requirements.txt
```
Figura 3, esquema de la arquitectura del servicio de terminales.

Base de datos: PostgreSQL con SQLAlchemy como ORM, usando UUIDs generados automáticamente como claves primarias.

## Modelo de Datos

### Pasaje de Ómnibus (pasajes)

La tabla `pasajes` es la única entidad del sistema y almacena los datos de cada boleto de ómnibus emitido. Cada registro representa un pasaje vendido, incluyendo información sobre el pasajero, el vehículo y el recorrido.

| Campo               | Tipo     | Descripción                                       |
|---------------------|----------|---------------------------------------------------|
| uuid                | String   | Identificador único generado automáticamente      |
| postal_code         | String   | Código postal de la terminal de origen            |
| bus_terminal_name   | String   | Nombre de la terminal de ómnibus                  |
| ticket              | String   | Código único del boleto (indexado)                |
| dni                 | String   | Documento de identidad del pasajero               |
| name                | String   | Nombre completo del pasajero                      |
| bus_license_plate   | String   | Patente del colectivo                             |
| enterprise          | String   | Empresa de transporte                             |
| start_date          | DateTime | Fecha y hora de inicio del viaje                  |
| end_date            | DateTime | Fecha y hora de fin del viaje                     |
| trip_city           | JSON     | Lista de ciudades del recorrido con fechas        |

Figura 4, campos de la tabla pasajes en la base de datos.

El campo `trip_city` almacena en formato JSON una lista de objetos, donde cada uno contiene el nombre de la ciudad, la fecha de llegada y el orden en el itinerario. Este diseño permite representar viajes con múltiples escalas sin necesidad de una tabla adicional.

## Esquemas de validación

Los esquemas Pydantic definen la estructura esperada de los datos tanto en la entrada (peticiones) como en la salida (respuestas) de la API. Esto garantiza que los datos sean validados automáticamente antes de procesarse.

Los principales esquemas son:

- **TripCity**: representa una parada del recorrido, con nombre de ciudad, fechas y orden.
- **BusTicketCreate**: datos requeridos para registrar un nuevo pasaje.
- **BusTicketResponse**: datos devueltos al consultar un pasaje, incluye el `uuid` generado.
- **TerminalItem**: representa una terminal con su `uuid` y nombre, usado para listar terminales.
- **TerminalBusTicketsResponse**: respuesta al consultar los viajes de una terminal en un rango de fechas, incluye el nombre de la terminal y una lista de viajes.

## Organización de rutas

Las rutas se organizan en dos grupos bien diferenciados, registrados en `app/routes/ticket.py`:

**Bus Tickets** (`/bus_tickets`): agrupa los endpoints para la gestión de pasajes individuales. Permite consultar un pasaje por su código de boleto y registrar nuevos pasajes.

**Terminal** (`/terminal`): agrupa los endpoints orientados a la consulta de datos por terminal. Permite listar todas las terminales conocidas, verificar la existencia de una terminal o de un viaje, y obtener los viajes de una terminal en un rango de fechas.

No se aplica autenticación en ninguna de las rutas, ya que este servicio opera como proveedor de datos interno dentro del sistema y se asume que solo es accesible desde la red interna del proyecto.

## Endpoints

### Health check

**GET /**

Endpoint de verificación de estado del servidor. Permite comprobar que el servicio está en funcionamiento. Devuelve `{"status": "ok"}`.

### Bus Tickets (`/bus_tickets`)

**GET /bus_tickets/{ticket}**

Consulta los datos de un pasaje por su código de boleto. Si el código no existe, devuelve un error 404. Este endpoint es el que consume el backend principal para obtener los datos de un boleto al momento de que un usuario se registra en un viaje.

**POST /bus_tickets/**

Registra un nuevo pasaje en el sistema. Valida que no exista previamente un registro con el mismo código de boleto; si ya existe, devuelve un error 409 (conflicto). Devuelve el pasaje creado con su `uuid` generado.

### Terminal (`/terminal`)

**GET /terminal/**

Lista todas las terminales de ómnibus conocidas en el sistema. Internamente agrupa los pasajes por nombre de terminal y devuelve una lista con el nombre y un `uuid` representativo de cada una. Este endpoint es utilizado por el backend principal para mostrar al usuario las terminales disponibles.

**GET /terminal/exist/?uuid={uuid}**

Verifica si existe en el sistema un registro con el `uuid` indicado. Devuelve `{"exist": true}` o `{"exist": false}`. El backend principal lo utiliza para validar que una terminal exista antes de crear registros internos asociados a ella.

**GET /terminal/trip/exist/?uuid={uuid}&license_plate={patente}&start_date={fecha}**

Verifica si existe un pasaje con el `uuid` y la patente indicados, cuyo viaje se superponga con el día calendario de la fecha proporcionada. Es utilizado por el backend principal para validar que un viaje programado exista antes de enviar notificaciones de demora a los pasajeros.

**GET /terminal/trip/?uuid={uuid}&start_date={inicio}&end_date={fin}**

Devuelve todos los pasajes asociados a la terminal identificada por el `uuid` dado, cuyos viajes se superpongan con el rango de fechas indicado. La respuesta incluye el nombre de la terminal y una lista con la patente, empresa, y fechas de cada viaje. Este endpoint es utilizado por el microservicio de OCR (a través del backend principal) para determinar qué colectivos se esperan en una terminal en un momento determinado.

## Integración con el resto del sistema

Este servicio actúa como el sistema upstream de terminales dentro de la arquitectura general. El backend principal lo consume de forma transparente a través de su variable de entorno `EXTERNAL_TERMINAL_UPSTREAM_URL`, que apunta a la dirección donde corre este servicio.

Las integraciones concretas son tres:

1. **Consulta de boletos**: cuando un usuario se registra en un viaje desde la aplicación, el backend principal llama a `GET /bus_tickets/{ticket}` para obtener los datos del pasaje (patente, empresa, ciudades del recorrido) y verificar que el boleto existe.

2. **Verificación de terminales**: cuando un super administrador crea una terminal interna, el backend principal llama a `GET /terminal/exist/` para comprobar que la terminal referenciada existe en este sistema antes de crear el registro interno.

3. **Verificación de viajes para notificaciones de demora**: cuando un administrador quiere enviar una notificación de demora, el backend principal llama a `GET /terminal/trip/exist/` para confirmar que el viaje programado existe y que la patente y fecha son correctas.

---

# ANEXO A

A continuación, se presenta una breve descripción de algunas de las librerías más importantes que se han utilizado para llevar a cabo el desarrollo del backend de terminales del presente trabajo.

## FastAPI

FastAPI es un framework web de código abierto para Python, orientado al desarrollo de APIs RESTful modernas de alto rendimiento. Es una de las librerías más populares del ecosistema Python cuando se trata de construir servicios HTTP. FastAPI es el framework principal para el manejo de rutas, validación de datos y peticiones HTTP en este servicio. Permite definir endpoints de forma declarativa utilizando anotaciones de tipo de Python, generar documentación interactiva automáticamente con Swagger UI, y manejar errores de forma coherente. Sus principales beneficios son: su altísima velocidad de ejecución, la validación automática de datos de entrada y salida mediante Pydantic, la generación de documentación sin configuración adicional, y su soporte nativo para programación asíncrona.

## SQLAlchemy

SQLAlchemy es una librería de código abierto para Python que implementa el patrón ORM (Object-Relational Mapper) y también ofrece acceso directo a SQL. Es una de las herramientas más consolidadas del ecosistema Python para la interacción con bases de datos relacionales. SQLAlchemy es la librería principal para el acceso a la base de datos PostgreSQL en este servicio. Permite mapear clases de Python a tablas relacionales, ejecutar consultas de lectura, escritura, actualización y eliminación, y gestionar la conexión a la base de datos de forma segura mediante el patrón de sesión. Algunos de sus beneficios son: la reducción del código repetitivo para acceso a datos, soporte para múltiples motores de base de datos, y una integración fluida con el ecosistema de Python.

## Pydantic

Pydantic es una librería de código abierto para Python orientada a la validación de datos y la gestión de configuraciones mediante anotaciones de tipo. Es la herramienta estándar de validación de datos en el ecosistema FastAPI. Pydantic es la librería utilizada para definir los esquemas de entrada y salida de la API, garantizando que los datos recibidos y enviados cumplan siempre con la estructura esperada. Cuando un cliente envía datos incorrectos, Pydantic rechaza la petición automáticamente con un mensaje de error descriptivo sin necesidad de código de validación adicional. Sus principales ventajas son: la validación automática sin código extra, la serialización y deserialización de datos, y la integración nativa con FastAPI.

## psycopg2-binary

psycopg2 es el adaptador de base de datos PostgreSQL más utilizado en el ecosistema Python. Es la librería que permite a SQLAlchemy comunicarse con PostgreSQL de forma nativa. psycopg2-binary es la versión precompilada del adaptador, que simplifica la instalación al no requerir dependencias del sistema operativo. En este servicio actúa como el puente entre SQLAlchemy y PostgreSQL, gestionando las conexiones, las transacciones y la ejecución de sentencias SQL a bajo nivel. Su principal ventaja es ser el estándar de facto para conectar Python con PostgreSQL, con soporte completo para las características avanzadas de la base de datos.

## pydantic-settings

pydantic-settings es una extensión de Pydantic orientada a la gestión de configuraciones de aplicaciones. Permite definir las variables de entorno de la aplicación como un modelo Pydantic tipado, cargándolas automáticamente desde el entorno del sistema operativo o desde un archivo `.env`. En este servicio se utiliza para centralizar la configuración (principalmente la URL de la base de datos) en una única clase `Settings`, evitando referencias dispersas a variables de entorno a lo largo del código. Sus ventajas son: la validación automática de las variables de configuración al arrancar la aplicación, la separación clara entre código y configuración, y la compatibilidad con los estándares de la metodología Twelve-Factor App.

## python-dotenv

python-dotenv es una librería de código abierto para Python que permite cargar variables de entorno desde un archivo `.env`. Es una de las herramientas más utilizadas para gestionar la configuración de aplicaciones en distintos entornos de desarrollo. python-dotenv se utiliza para simplificar la configuración del servicio en entornos de desarrollo, permitiendo definir en un único archivo todas las variables del sistema (como la cadena de conexión a la base de datos) sin necesidad de definirlas manualmente en el entorno del sistema operativo. Sus beneficios son: la separación clara entre código y configuración, y la facilidad para manejar múltiples entornos sin modificar el código.

---

# ANEXO B

A continuación, se presenta una breve descripción de algunos conceptos y estándares técnicos fundamentales que se han empleado a lo largo del desarrollo del backend de terminales del presente trabajo.

## ORM (Object-Relational Mapper)

Un ORM, cuyas siglas corresponden a Object-Relational Mapper, es una técnica de programación que permite interactuar con una base de datos relacional utilizando objetos del lenguaje de programación en lugar de sentencias SQL directas. El ORM se encarga de traducir automáticamente las operaciones sobre objetos (crear, leer, actualizar, eliminar) en las consultas SQL correspondientes. En este servicio, SQLAlchemy cumple el rol de ORM: la clase `BusTicket` de Python está mapeada directamente a la tabla `pasajes` de PostgreSQL, y todas las operaciones de base de datos se realizan mediante métodos sobre esa clase. Las principales ventajas de este enfoque son: la reducción del código repetitivo, la independencia del motor de base de datos, y la detección temprana de errores gracias al sistema de tipos.

## UUID (Identificador Único Universal)

Un UUID, cuyas siglas corresponden a Universally Unique Identifier, es un número de 128 bits generado de forma que su probabilidad de colisión con cualquier otro UUID generado en cualquier momento y lugar sea prácticamente nula. Es el estándar más utilizado para identificar recursos de forma única en sistemas distribuidos. En este servicio, cada pasaje almacenado en la base de datos recibe un UUID generado automáticamente como clave primaria. Esto permite que los registros sean identificados de forma segura incluso en escenarios donde múltiples instancias del servicio estén operando simultáneamente, y facilita la referenciación cruzada desde otros servicios del sistema (como el backend principal) sin riesgo de ambigüedad.

## JSON (JavaScript Object Notation)

JSON, cuyas siglas corresponden a JavaScript Object Notation, es un formato de intercambio de datos ligero y legible por humanos basado en la sintaxis de objetos de JavaScript. Es el formato estándar para la comunicación entre servicios web modernos y la representación de datos semiestructurados. En este servicio, JSON cumple dos funciones: por un lado, es el formato de todas las respuestas de la API (siguiendo la convención RESTful); por otro, es el tipo de dato utilizado para almacenar el campo `trip_city` de cada pasaje en la base de datos PostgreSQL, lo que permite representar el itinerario completo del viaje (con múltiples ciudades y fechas) en un único campo sin necesidad de una tabla separada.

## API RESTful

REST, cuyas siglas corresponden a Representational State Transfer, es un estilo arquitectónico para el diseño de sistemas distribuidos. Una API se considera RESTful cuando sigue un conjunto de restricciones fundamentales: arquitectura cliente-servidor, comunicación sin estado (cada petición contiene toda la información necesaria para procesarse), uso de recursos identificados mediante URLs y aprovechamiento de los métodos del protocolo HTTP. En este servicio, toda la interfaz está diseñada siguiendo este estilo. Cada recurso del dominio (pasajes, terminales, viajes) se expone con su propia URL, y las operaciones se realizan utilizando los métodos HTTP correspondientes (GET para consultar, POST para crear). Las respuestas se devuelven siempre en formato JSON, estableciendo contratos de comunicación claros para los demás servicios del sistema que consumen esta API.

## Variables de entorno (.env)

Las variables de entorno son valores de configuración definidos fuera del código fuente de una aplicación, que el sistema operativo o un archivo de configuración ponen a disposición del proceso en tiempo de ejecución. El uso de variables de entorno es una práctica recomendada por la metodología Twelve-Factor App para separar la configuración del código, evitando que datos sensibles queden expuestos en el repositorio. En este servicio, las variables de entorno se utilizan para centralizar la cadena de conexión a la base de datos PostgreSQL. Este valor se define en un archivo `.env` que no se incluye en el control de versiones, y es cargado automáticamente al inicio de la aplicación mediante pydantic-settings y python-dotenv. Esto permite operar con distintas configuraciones en desarrollo y producción sin modificar una sola línea de código.
