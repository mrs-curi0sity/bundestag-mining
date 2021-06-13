#### docker
# show all images
> docker images

# show running container
> docker container ls # the same as docker ps?

# show all container, no matter what status
> docker container ls -a

# build container with image name bundestag-mining
> docker build -t bundestag-mining .

# run with container name: bundestag, image name: bundestag-mining
> docker run -it -p 8050:8050 --name bundestag bundestag-mining 
Be aware that port tunnelling only works when host IP is set like this: app.run_server(host="0.0.0.0",  port=8050, debug=True)

# wenn  "port already in use" dann erst
> docker stop 

# stop container
> docker stop <Container ID> 
> docker stop 71c721a3b85e

# show status of all container
> docker ps -a

# delete container (that can be seen with docker ps -a)
> docker rm <Container ID>
> docker rm 79a693d2e8ed

# delete image (that can be seen with docker images)
> docker image rm f697521385f4


#### update container locally (not sure if all of these steps are necessary. especially rm steps)
> docker stop <Container ID>
> docker rm <Container ID>
> docker image rm <Image ID>
> docker build -t bundestag-mining .
> docker run -it -p 8051:8051 --name btm-20210613 bundestag-mining

# evtl einfacher
> docker build -t abc . --no-cache

#### update container on aws
# 1. rebuild
> docker build -t abc . --no-cache

# 2. list all images. hier kann man REPOSITORY und TAG sehen
> docker images

# 3. tag image with ECR
> docker tag <REPOSITORY>:<TAG> 388550693512.dkr.ecr.eu-central-1.amazonaws.com/bundestag-mining-ecr
> docker tag bundestag-mining:latest 388550693512.dkr.ecr.eu-central-1.amazonaws.com/bundestag-mining-ecr

# 4. login to aws (generell wenn "denied: Your authorization token has expired. Reauthenticate and try again.")
> aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.<region>.amazonaws.com
> aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 388550693512.dkr.ecr.eu-central-1.amazonaws.com

# 5. push to ecr 
> docker push 388550693512.dkr.ecr.eu-central-1.amazonaws.com/bundestag-mining-ecr
kann unter asw console > ecr > repositories gecheckt werden

# 6. update ecs service 
> aws ecs update-service --cluster bundestag-mining-cluster --service bundestag-mining-ecs-service --force-new-deployment
kann uner aws console > ecs > clusters > [cluster name] > deployments gecheckt werden

# 7. find out public IP
aws console > ecs > clusters > [cluster name] > tasks > [task name]

# 8. falls sich port geändert hat, unter details => security group port 8050 frei geben
unter cluster => [Cluster name] => [SErvice name] => Details
=> ssecurity group => inbound group => edit inbound rules
=> custom tcp rule mit 8050 hinzu fügen


#### check website status on aws
# find out IP
AWS console => ECS => Clusters => Tasks
http://18.193.46.74:8050/
