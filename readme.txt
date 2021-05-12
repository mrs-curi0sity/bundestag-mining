#### docker
# show all images
> docker images

# show running container
> docker container ls

# build container
> docker build -t bundestag-mining .

# run with container name: bundestag, image name: bundestag-mining
> docker run -it -p 8050:8050 --name bundestag bundestag-mining 
Be aware that port tunnelling only works when host IP is set like this: app.run_server(host="0.0.0.0",  port=8050, debug=True)

# stop container
> docker stop bundestag

# show status of all container
> docker ps -a

# delete container
> docker rm 