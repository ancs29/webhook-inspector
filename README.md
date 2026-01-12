
# Online Webhook Inspector

This webhook inspector is a developer tool designed to aid in debugging webhook integrations. It accepts incoming HTTP POST requests, validates their contents, and provides both API and web-based interfaces for inspecting webhook payloads, headers, and query parameters.

Link - http://webhook-inspector-alb-1832205148.eu-west-1.elb.amazonaws.com/
## Author

- Alex Staicu
- alexstaicu628@gmail.com
- 07949887549


## Tech Stack

- Backend: Python + FastAPI
- Frontend: Jinja2 + TailwindCSS
- Database: SQLAlchemy + PostgreSQL
- CI: PyTest + SQLite + GitHub Actions
- Deployment: Docker + GitHub Actions + AWS
## Features

- Captures webhook requests, decodes UTF-8 string and JSON format and raises exceptions if data is invalid.
- For valid webhooks, stores headers, body, and query parameters.
- Displays all webhooks in a table, in addition to a link to send webhooks to.
- Click on a row to view pretty printed JSON contents of each webhook.
- Global exception handler to raise unexpected errors.
- Well formatted Python code with docstrings.
- Unit tests covering backend with continuous integration using GitHub Actions.
## Design Intent

The design decisions of this project were made to demonstrate professional development practices.

### Key Decisions
- FastAPI was chosen as it is a simple, modern framework with a lack of boilerplate code, ideal for a relatively small portfolio piece. 
- Jinja2 and TailwindCSS were chosen to develop a fast front end solution. The focus of this project was primarily on the backend structure, testing, and deployment. 
- Cloud deployment is essential to the modern software industry, so to build experience I chose to Dockerise the app and deploy it using GitHub Actions and AWS. Fargate was chosen to provide an abstract interface instead of directly managing servers. PostgreSQL was chosen for its strong integration with AWS and its reliability and scalability.
- SQLAlchemy was used as an ORM to streamline the programming process by acting as an interface between Python and Postgres. Additionally, since it is database agnostic, it allows a separate SQLite database to be created for testing purposes only.
- The project uses PyTest and GitHub Actions to ensure CI by testing the backend routes automatically during every push.

### Trade-offs
- FastAPI has a smaller ecosystem than Django.
- SQLAlchemy adds a slight performance overhead.
- AWS RDS costs money if you extend past the limitations of the free tier.

### Other Design Considerations

- The modular structure of the backend separates concerns: main.py (routes), model.py (schema), db.py (configuration). Within main.py the routes are separated into API routes and HTML routes that return Jinja2 templates.
- JSON payloads are stored as text columns for simplicity and database agnosticity (**trade-off:** less efficient than Postgres JSONB data type).
- The receive route parses the payload to ensure it is in the correct format.
- AWS credentials stored as GitHub secrets.
- Runtime permissions come from an IAM role and not within the image itself.
- RDS in private subnet with security group restricting access to ECS only.
- Principle of least privilege: execution role limited to ECR pull and CloudWatch logging.
## Backend Routes

### API Routes

#### Create Webhook

```http
  POST /api/webhooks
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `request` | `Request` | HTTP request |
| `db` | `Session` | SQLAlchemy database session|


Decodes payload into UTF-8 and then into JSON, raising errors if either fails. If the payload is in a valid format, it is saved into the database along with the headers and query parameters. 

#### Get Webhooks

```http
  GET /api/webhooks
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `db` | `Session` | SQLAlchemy database session|


Queries all rows from the database and returns them all as a list of Python dictionaries.

```http
  GET /api/webhooks/{webhook_id}
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `webhook_id` | `int` | Database ID of webhook|
| `db` | `Session` | SQLAlchemy database session|


Queries the database for the webhook with that ID, and either returns the row as a Python dictionary or returns an error message if it can't find it. 

```http
  GET /
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `request` | `Request` | HTTP request |
| `db` | `Session` | SQLAlchemy database session|


Returns the home page of the website, containing a table displaying all webhooks in the database and 

```http
  GET /{webhook_id}
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `webhook_id` | `int` | Database ID of webhook|
| `request` | `Request` | HTTP request |
| `db` | `Session` | SQLAlchemy database session|


Returns a page displaying the pretty-printed body, headers and query parameters of the selected webhook.
## CI Pipeline

### PyTest Unit Tests

Four unit tests are included with the project, using a local SQLite database for testing:

- Test Receive and Get Webhooks - validates that the receive route accepts and stores JSON webhooks, that the get webhooks route returns the same webhook, and that parameters are serialised and deserialised correctly.
- Test Invalid JSON Webhook - validates that invalid JSON is rejected with a 400 error and that it is not saved in the database.
- Test Invalid UTF-8 Webhook - validates that invalid UTF-8 is rejected with a 400 error and that it is not saved in the database.
- Test Get Individual Webhook - validates that the GET individual webhook route retuns the correct webhook, and that the route does not return anything for a non-existent webhook ID.

### GitHub Actions
When new code is pushed:

- **1 -** tests.yml runs all four tests to ensure code is still healthy and functional.
- **2 -** If all the tests were passed, deploy.yml builds a new Docker and pushes it to AWS ECS automatically.

In addition the Docker can manually be built and tested in GitHub Actions with docker-test.yml in the event of any issues, but this is not done every time as it is generally time consuming and redundant.
## Deployment
The application is containerized with Docker and deployed to AWS ECS Fargate with the following infrastructure:

- **ECR (Elastic Container Registry):** Stores Docker images
- **ECS Fargate:** Runs containers serverless (to abstract away server management)
- **RDS PostgreSQL:** Database service
- **CloudWatch:** Automated logging

Upon passing the unit tests, GitHub Actions builds an image using the Dockerfile with Python 3.14-slim and all the dependencies from requirements.txt, and pushes it to its designated ECR. It then tells ECS Fargate to deploy the new image immediately.

**Security:** AWS credentials are stored as GitHub secrets. ECS tasks use IAM roles for ECR access and CloudWatch logging. Network security groups restrict database access to the application container only.
## Possible Enhancements

- Automated webhook table refreshing
- Search and filter functionality
- Password authentication
- Automatically generated curl command for users to send webhooks with