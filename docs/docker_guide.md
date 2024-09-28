Hier ist der Inhalt für docs/docker_guide.md:
Copy# Docker Guide for Bundestag Mining Project

## Basic Commands

### Build Container
docker build -t bundestag-mining .

### Run Container
docker run -it -p 8050:8050 --name bundestag bundestag-mining

### View All Images
docker images

### View Running Containers
docker container ls

### View All Containers
docker container ls -a

## Management Commands

### Stop Container
docker stop <Container ID>

### Remove Container
docker rm <Container ID>

### Remove Image
docker image rm <Image ID>

## Updating Container

1. Stop and remove existing container
2. Remove existing image
3. Rebuild image:
docker build -t bundestag-mining . --no-cache
Copy4. Run new container

## Troubleshooting

- If "port already in use", stop the running container first.
- Ensure host IP is set in the app: `app.run_server(host="0.0.0.0", port=8050, debug=True)`