# Google Cloud Console Deployment Guide

This guide outlines the steps to deploy updated code to Google Cloud Run using the Google Cloud Console.

## Prerequisites

- A Google Cloud Platform account with an active project
- Git repository with your project code
- Docker installed on your local machine
- Google Cloud SDK (gcloud) installed and configured

## Deployment Steps

1. **Update and Pull Code**

   First, ensure your local repository is up to date:

   ```
   git pull
   ```

   If you encounter authentication issues, make sure you're using a personal access token instead of a password.

2. **Build Docker Image**

   Build your Docker image with the updated code:

   ```
   docker build -t gcr.io/bundestag-miner/btm .
   ```

   Replace `[PROJECT-ID]` with your Google Cloud project ID and `[IMAGE-NAME]` with your desired image name.

3. **Push Docker Image to Google Container Registry**

   Push the built image to Google Container Registry:

   ```
   docker push gcr.io/bundestag-miner/btm
   ```

4. **Deploy to Google Cloud Run**

   Deploy your updated image to Google Cloud Run:

   ```
   gcloud run deploy bundestag-dashboard --image gcr.io/bundestag-miner/btm --platform managed
   ```

   Replace `[SERVICE-NAME]` with your Cloud Run service name.

5. **Configuration**

   - If prompted, enable necessary APIs for your project.
   - Choose a region for your deployment when asked.
   - Decide whether to allow unauthenticated invocations to your service.

6. **Verify Deployment**

   After successful deployment, you'll receive a Service URL. Visit this URL to verify your updated application is running correctly.

## Notes

- Ensure your `Dockerfile` is optimized for production use.
- Consider using environment variables for sensitive information.
- Regularly clean up unused images and revisions to manage costs.

By following these steps, you can efficiently deploy your updated code to Google Cloud Run using the Google Cloud Console.
