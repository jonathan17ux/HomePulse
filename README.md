# HomePulse

HomePulse is a centralized monitoring web application for personal
home networks and homelabs.

The project is being developed for CSCA 5028 Applications of Software
Architecture for Big Data.

## Current MVP

The current HomePulse version includes:

* Flask web application
* User input and echo functionality
* External REST API data collection
* Separate data collector process
* SQLite persistent storage
* SQLAlchemy ORM
* Database schema migrations
* REST API for collected observations
* Health-check endpoint
* Unit tests
* Integration tests

## Architecture

The current data flow is:

External REST API -> Data Collector -> Database -> Web Application -> User

Future versions will add:

* Data analyzer
* RabbitMQ event messaging
* Application metrics
* Alerts
* Simulated device and security data
* Expanded dashboards

## Local Setup

Create and activate a Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create/update the database:

```bash
flask --app src.app db upgrade
```

Run the web application:

```bash
flask --app src.app run --debug
```

Run one data collection cycle:

```bash
python -m src.collector
```

Run tests:

```bash
python -m pytest -v
```

## Endpoints

* `/` - HomePulse dashboard
* `/echo_user_input` - Module 2 user input functionality
* `/health` - application health check
* `/api/observations` - REST API for collected observations

## Database

HomePulse currently uses SQLite during local development.

The application supports the `DATABASE_URL` environment variable so
a production SQL database can be used later without redesigning the
application.

