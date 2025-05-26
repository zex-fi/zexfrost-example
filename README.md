# Application Name

This repository contains a distributed application with Node.js services running in Docker containers and a Python client.

## Prerequisites

- [Docker](https://www.docker.com/get-started) and Docker Compose
- [Python](https://www.python.org/downloads/) 3.12

## Getting Started

Follow these steps to run the application:

### 1. Start the Node.js Services

First, start the Node.js services using Docker Compose:

```bash
docker compose up
```

This command will:
- Build the necessary Docker images (if they don't exist)
- Create and start the containers defined in your docker-compose.yml
- Display logs from all services in the terminal

To run the services in detached mode (in the background), use:

```bash
docker compose up -d
```

### 2. Run the Python Client

After the Node.js services are up and running, start the Python client from the root folder of the project:

```bash
python -m src.client.main
```

Make sure you're in the root directory of the project when running this command.

## Stopping the Application

To stop the Docker containers, press `Ctrl+C` if running in the foreground, or run:

```bash
docker compose down
```

## Troubleshooting

If you encounter any issues:

1. Make sure all Docker containers are running properly with `docker ps`
2. Check the logs of specific services with `docker logs <container_name>`
3. Ensure you're running the Python client from the correct directory

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.