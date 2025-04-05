output "medusa_backend_url" {
  value = aws_ecs_service.medusa_service.network_configuration[0].assign_public_ip
}
name: Deploy Medusa to AWS ECS

on:
  push:
    branches:
      - main  # Trigger the deployment when code is pushed to the main branch

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v2

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2

    - name: Log in to Amazon ECR
      uses: aws-actions/amazon-ecr-login@v1

    - name: Build Docker image
      run: |
        docker build -t ${{ secrets.ECR_REPOSITORY }} .
        docker tag ${{ secrets.ECR_REPOSITORY }}:latest ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-east-1.amazonaws.com/${{ secrets.ECR_REPOSITORY }}:latest

    - name: Push Docker image to ECR
      run: |
        docker push ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-east-1.amazonaws.com/${{ secrets.ECR_REPOSITORY }}:latest

    - name: Update ECS service
      uses: jakejarvis/ecs-deploy-action@v1
      with:
        cluster: medusa-cluster
        service: medusa-service
        task-definition: medusa-task
        container-name: medusa-backend
        container-image: ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-east-1.amazonaws.com/${{ secrets.ECR_REPOSITORY }}:latest
