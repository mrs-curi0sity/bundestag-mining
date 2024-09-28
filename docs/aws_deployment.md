# AWS Deployment Guide for Bundestag Mining Project

## Updating Container on AWS

1. Rebuild the Docker image locally:
docker build -t bundestag-mining . --no-cache

2. List all images to get REPOSITORY and TAG:
docker images

3. Tag image for ECR:
docker tag bundestag-mining:latest 388550693512.dkr.ecr.eu-central-1.amazonaws.com/bundestag-mining-ecr

4. Login to AWS ECR:
aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 388550693512.dkr.ecr.eu-central-1.amazonaws.com

5. Push to ECR:
docker push 388550693512.dkr.ecr.eu-central-1.amazonaws.com/bundestag-mining-ecr

6. Update ECS service:
aws ecs update-service --cluster bundestag-mining-cluster --service bundestag-mining-ecs-service --force-new-deployment

7. Find public IP:
AWS Console > ECS > Clusters > [cluster name] > Tasks > [task name]

8. If port changed, update security group:
- AWS Console > ECS > Clusters > [Cluster name] > [Service name] > Details
- Security group > Inbound rules > Edit
- Add custom TCP rule for port 8050

## Checking Website Status

1. Find IP address:
AWS Console > ECS > Clusters > Tasks

2. Access website:
http://[IP_ADDRESS]:8050/

## Troubleshooting

If you encounter "denied: Your authorization token has expired", re-authenticate with AWS ECR (step 4 above).