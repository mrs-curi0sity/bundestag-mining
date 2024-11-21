# Docker Guide for Bundestag Mining Project
## auf gcc deployen
1. clonen des projekts
2. builden
>  docker build -t gcr.io/bundestag-miner/bundestag-dashboard .

3. pushen
> docker push gcr.io/bundestag-miner/bundestag-dashboard

4. auf cloud run deployen
> gcloud run deploy bundestag-dashboard --image gcr.io/bundestag-miner/bundestag-dashboard --platform managed

## Basic Commands

### Build Container
docker build -t bundestag-mining .

### Run Container
docker run -it -p 8050:8050 --name bundestag bundestag-mining bzw

docker run -it -p 8050:8050 -v $(pwd):/app --name bundestag bundestag-mining


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


# 1. Stop and remove existing container
docker stop bundestag-dashboard
docker rm bundestag-dashboard

# 2. Rebuild image
docker build -t bundestag-dashboard . --no-cache

# 3.  Run new container
docker run -it -p 8050:8050 --name bundestag-dashboard bundestag-dashboard


## Troubleshooting

- If "port already in use", stop the running container first.:
docker rm bundestag

- Ensure host IP is set in the app: `app.run_server(host="0.0.0.0", port=8050, debug=True)`