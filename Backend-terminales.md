# TERMINALS BACKEND - PROGRAMMING LANGUAGE AND LIBRARIES USED

For the development of the terminals backend of this work, the Python programming language was selected. This choice is based on its simplicity, its wide adoption in the web development ecosystem and the availability of modern libraries that make it possible to build robust APIs with little code. Python enables agile development, significantly reducing implementation time without sacrificing the quality of the result.

One of the main reasons for adopting it in this component is the availability of the FastAPI framework, which makes it possible to build high-performance web services with automatic data validation and generation of interactive documentation. Unlike other, more verbose frameworks, FastAPI takes advantage of modern Python type annotations to reduce the code needed and detect errors at development time. In the context of this project, this is convenient because the terminals service acts as a data provider for the main backend, so the clarity and reliability of its interface are essential.

In addition, Python has SQLAlchemy as its reference ORM (Object-Relational Mapper), which makes it possible to interact with the PostgreSQL database in a safe and expressive way, without having to write SQL by hand. This ensures that data access is consistent across the whole service and makes future maintenance easier.

## Libraries to be used

Several libraries were used to develop the prototype of this work; the most important ones are FastAPI, SQLAlchemy, Pydantic, psycopg2 and pydantic-settings. Appendix A of the work gives a brief description of each of the libraries used.

---

# TERMINALS BACKEND PROTOTYPE

This section describes how the system's terminals backend was structured and implemented, including the code organization, the data model and the most relevant aspects of each component.

The service follows a simple layered architecture, separating responsibilities between models (database structure), schemas (input and output data validation), routes (HTTP controllers) and configuration. This separation makes maintenance and the independent evolution of each part easier.

## Application entry point

The application is initialized in the `app/main.py` module. Here the main FastAPI instance is created, the database tables are created automatically if they do not exist, and the service's two route groups are registered.

```python
app = FastAPI(
    title="Bus Terminals API",
    description="Backend for bus terminal ticket management",
    version="1.0.0",
)

app.include_router(bus_ticket_router)
app.include_router(terminal_router)
```
Figure 1, application entry point code.

Automatic table creation is done with `Base.metadata.create_all(bind=engine)`, which, when the server starts, compares the state of the model with that of the database and generates the necessary structures if they do not exist.

## Configuration and database connection

The service configuration is centralized in `app/config.py` using the pydantic-settings library. This makes it possible to define environment variables with a default value and load them automatically from a `.env` file, keeping sensitive data out of the source code.

```python
class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:1234@localhost:5432/terminales"

    class Config:
        env_file = ".env"
```
Figure 2, environment variable configuration code.

The database connection is managed in `app/database.py` with SQLAlchemy. A connection engine and a session factory are created, and a `get_db()` function is exposed, which the endpoints use as a dependency to obtain an active session and close it correctly at the end of each request.

## Architecture

The project follows a clear and well-defined directory structure:

```
backend-terminales/
├── app/
│   ├── config.py       → Environment variables and configuration
│   ├── database.py     → Database connection
│   ├── main.py         → Application entry point
│   ├── models/
│   │   └── ticket.py   → Database model (BusTicket)
│   ├── schemas/
│   │   └── ticket.py   → Validation schemas (Pydantic)
│   └── routes/
│       └── ticket.py   → HTTP controllers and route logic
├── .env
└── requirements.txt
```
Figure 3, architecture diagram of the terminals service.

Database: PostgreSQL with SQLAlchemy as ORM, using automatically generated UUIDs as primary keys.

## Data Model

### Bus Ticket (bus_tickets)

The `bus_tickets` table is the only entity of the system and stores the data of each bus ticket issued. Each record represents a ticket sold, including information about the passenger, the vehicle and the route.

| Field               | Type     | Description                                       |
|---------------------|----------|---------------------------------------------------|
| uuid                | String   | Automatically generated unique identifier         |
| postal_code         | String   | Postal code of the origin terminal                |
| bus_terminal_name   | String   | Name of the bus terminal                          |
| ticket              | String   | Unique ticket code (indexed)                      |
| dni                 | String   | Passenger's national ID document                  |
| name                | String   | Passenger's full name                             |
| bus_license_plate   | String   | Bus license plate                                 |
| enterprise          | String   | Transport company                                 |
| start_date          | DateTime | Trip start date and time                          |
| end_date            | DateTime | Trip end date and time                            |
| trip_city           | JSON     | List of route cities with dates                   |

Figure 4, fields of the bus_tickets table in the database.

The `trip_city` field stores a list of objects in JSON format, where each one contains the city name, the arrival date and its order in the itinerary. This design makes it possible to represent trips with multiple stops without needing an additional table.

## Validation schemas

The Pydantic schemas define the expected structure of the data both in the input (requests) and in the output (responses) of the API. This ensures that data is validated automatically before being processed.

The main schemas are:

- **TripCity**: represents a stop on the route, with city name, dates and order.
- **BusTicketCreate**: data required to register a new bus ticket.
- **BusTicketResponse**: data returned when querying a bus ticket, includes the generated `uuid`.
- **TerminalItem**: represents a terminal with its `uuid` and name, used to list terminals.
- **TerminalBusTicketsResponse**: response when querying a terminal's trips in a date range, includes the terminal name and a list of trips.

## Route organization

Routes are organized into two clearly differentiated groups, registered in `app/routes/ticket.py`:

**Bus Tickets** (`/bus_tickets`): groups the endpoints for managing individual bus tickets. It allows querying a bus ticket by its ticket code and registering new bus tickets.

**Terminal** (`/terminal`): groups the endpoints oriented to querying data by terminal. It allows listing all known terminals, checking whether a terminal or a trip exists, and getting a terminal's trips in a date range.

No authentication is applied on any of the routes, since this service operates as an internal data provider within the system and is assumed to be reachable only from the project's internal network.

## Endpoints

### Health check

**GET /health**

Server status check endpoint. It makes it possible to verify that the service is up. It returns `OK` (plain text) with status 200.

**GET /** redirects to `/health`.

### Bus Tickets (`/bus_tickets`)

**GET /bus_tickets/{ticket}**

Queries the data of a bus ticket by its ticket code. If the code does not exist, it returns a 404 error. This is the endpoint the main backend consumes to get a ticket's data when a user registers for a trip.

**POST /bus_tickets/**

Registers a new bus ticket in the system. It validates that no record with the same ticket code already exists; if it does, it returns a 409 (conflict) error. It returns the created bus ticket with its generated `uuid`.

### Terminal (`/terminal`)

**GET /terminal/**

Lists all the bus terminals known to the system. Internally it groups the bus tickets by terminal name and returns a list with the name and a representative `uuid` for each one. The main backend uses this endpoint to show the user the available terminals.

**GET /terminal/exist/?uuid={uuid}**

Checks whether a record with the given `uuid` exists in the system. It returns `{"exist": true}` or `{"exist": false}`. The main backend uses it to validate that a terminal exists before creating internal records associated with it.

**GET /terminal/trip/exist/?uuid={uuid}&license_plate={license_plate}&start_date={date}**

Checks whether there is a bus ticket with the given `uuid` and license plate whose trip overlaps the calendar day of the given date. The main backend uses it to validate that a scheduled trip exists before sending delay notifications to passengers.

**GET /terminal/trip/?uuid={uuid}&start_date={start}&end_date={end}**

Returns all bus tickets associated with the terminal identified by the given `uuid` whose trips overlap the given date range. The response includes the terminal name and a list with the license plate, company and dates of each trip. The OCR microservice uses this endpoint (through the main backend) to determine which buses are expected at a terminal at a given time.

## Integration with the rest of the system

This service acts as the upstream terminals system within the overall architecture. The main backend consumes it transparently through its `EXTERNAL_TERMINAL_UPSTREAM_URL` environment variable, which points to the address where this service runs.

There are three concrete integrations:

1. **Ticket lookup**: when a user registers for a trip from the application, the main backend calls `GET /bus_tickets/{ticket}` to get the bus ticket data (license plate, company, route cities) and verify that the ticket exists.

2. **Terminal verification**: when a super administrator creates an internal terminal, the main backend calls `GET /terminal/exist/` to check that the referenced terminal exists in this system before creating the internal record.

3. **Trip verification for delay notifications**: when an administrator wants to send a delay notification, the main backend calls `GET /terminal/trip/exist/` to confirm that the scheduled trip exists and that the license plate and date are correct.

---

# APPENDIX A

Below is a brief description of some of the most important libraries used to develop the terminals backend of this work.

## FastAPI

FastAPI is an open-source web framework for Python, aimed at developing modern, high-performance RESTful APIs. It is one of the most popular libraries in the Python ecosystem for building HTTP services. FastAPI is the main framework for routing, data validation and HTTP requests in this service. It makes it possible to define endpoints declaratively using Python type annotations, automatically generate interactive documentation with Swagger UI, and handle errors consistently. Its main benefits are: its very high execution speed, automatic validation of input and output data through Pydantic, documentation generation with no additional configuration, and its native support for asynchronous programming.

## SQLAlchemy

SQLAlchemy is an open-source Python library that implements the ORM (Object-Relational Mapper) pattern and also offers direct SQL access. It is one of the most established tools in the Python ecosystem for interacting with relational databases. SQLAlchemy is the main library for accessing the PostgreSQL database in this service. It makes it possible to map Python classes to relational tables, run read, write, update and delete queries, and manage the database connection safely through the session pattern. Some of its benefits are: less repetitive data-access code, support for multiple database engines, and smooth integration with the Python ecosystem.

## Pydantic

Pydantic is an open-source Python library for data validation and settings management using type annotations. It is the standard data validation tool in the FastAPI ecosystem. Pydantic is the library used to define the API's input and output schemas, ensuring that the data received and sent always matches the expected structure. When a client sends incorrect data, Pydantic rejects the request automatically with a descriptive error message, with no additional validation code needed. Its main advantages are: automatic validation with no extra code, data serialization and deserialization, and native integration with FastAPI.

## psycopg2-binary

psycopg2 is the most widely used PostgreSQL database adapter in the Python ecosystem. It is the library that lets SQLAlchemy communicate natively with PostgreSQL. psycopg2-binary is the precompiled version of the adapter, which simplifies installation by not requiring operating system dependencies. In this service it acts as the bridge between SQLAlchemy and PostgreSQL, managing connections, transactions and low-level execution of SQL statements. Its main advantage is being the de facto standard for connecting Python to PostgreSQL, with full support for the database's advanced features.

## pydantic-settings

pydantic-settings is a Pydantic extension aimed at application settings management. It makes it possible to define the application's environment variables as a typed Pydantic model, loading them automatically from the operating system environment or from a `.env` file. In this service it is used to centralize the configuration (mainly the database URL) in a single `Settings` class, avoiding scattered references to environment variables throughout the code. Its advantages are: automatic validation of configuration variables when the application starts, a clear separation between code and configuration, and compatibility with the Twelve-Factor App methodology.

## python-dotenv

python-dotenv is an open-source Python library that loads environment variables from a `.env` file. It is one of the most widely used tools for managing application configuration across different development environments. python-dotenv is used to simplify the service's configuration in development environments, making it possible to define all the system's variables (such as the database connection string) in a single file without having to set them manually in the operating system environment. Its benefits are: a clear separation between code and configuration, and the ease of handling multiple environments without modifying the code.

---

# APPENDIX B

Below is a brief description of some fundamental technical concepts and standards used throughout the development of the terminals backend of this work.

## ORM (Object-Relational Mapper)

An ORM, short for Object-Relational Mapper, is a programming technique that makes it possible to interact with a relational database using objects of the programming language instead of direct SQL statements. The ORM takes care of automatically translating operations on objects (create, read, update, delete) into the corresponding SQL queries. In this service, SQLAlchemy plays the role of ORM: the Python `BusTicket` class is mapped directly to the PostgreSQL `bus_tickets` table, and all database operations are performed through methods on that class. The main advantages of this approach are: less repetitive code, independence from the database engine, and early error detection thanks to the type system.

## UUID (Universally Unique Identifier)

A UUID, short for Universally Unique Identifier, is a 128-bit number generated so that its probability of colliding with any other UUID generated at any time and place is practically zero. It is the most widely used standard for uniquely identifying resources in distributed systems. In this service, each bus ticket stored in the database receives an automatically generated UUID as its primary key. This allows records to be identified safely even in scenarios where multiple instances of the service are running simultaneously, and makes cross-referencing from other services of the system (such as the main backend) possible without any risk of ambiguity.

## JSON (JavaScript Object Notation)

JSON, short for JavaScript Object Notation, is a lightweight, human-readable data interchange format based on JavaScript object syntax. It is the standard format for communication between modern web services and for representing semi-structured data. In this service, JSON fulfills two functions: on one hand, it is the format of all API responses (following the RESTful convention); on the other, it is the data type used to store the `trip_city` field of each bus ticket in the PostgreSQL database, which makes it possible to represent the full trip itinerary (with multiple cities and dates) in a single field without needing a separate table.

## RESTful API

REST, short for Representational State Transfer, is an architectural style for designing distributed systems. An API is considered RESTful when it follows a set of fundamental constraints: client-server architecture, stateless communication (each request contains all the information needed to process it), use of resources identified by URLs and use of the HTTP protocol methods. In this service, the entire interface is designed following this style. Each domain resource (bus tickets, terminals, trips) is exposed with its own URL, and operations are performed using the corresponding HTTP methods (GET to query, POST to create). Responses are always returned in JSON format, establishing clear communication contracts for the other services of the system that consume this API.

## Environment variables (.env)

Environment variables are configuration values defined outside an application's source code, which the operating system or a configuration file makes available to the process at runtime. Using environment variables is a practice recommended by the Twelve-Factor App methodology to separate configuration from code, preventing sensitive data from being exposed in the repository. In this service, environment variables are used to centralize the PostgreSQL database connection string. This value is defined in a `.env` file that is not included in version control, and is loaded automatically when the application starts through pydantic-settings and python-dotenv. This makes it possible to run with different configurations in development and production without changing a single line of code.
