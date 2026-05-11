# Sentiment Analysis app

This builds a sentiment analysis app. User can send request via an REST API to predict sentiment of text. 

It deploys a sentiment model leveraging a cloud based serverless cloud architecture. The following tools are used:

- google cloud artifact registry (container registry)
- google cloud cloud storage (bucket: data and model storage)
- google cloud AIM (Access Identity Management): mangement role and 
- google cloud run : serverless cloud compute autoscaling
- github action for ci/cd
- docker container


# Call API

To call the API, use the following json format:
```angular2html

body = {
    text: "The meal service was not very good and we didn't get water"
}
```

Call with curl:

```angular2html
curl -m 310 -X POST https://ur_for_app/sentiment_analysis_model_app_cloud_fun \
-H "Authorization: bearer $(gcloud auth print-identity-token)" \
-H "Content-Type: application/json" \
-d '{text: "The meal service was not very good and we didn't get water"}'
```

# Test API locally when developing

The Flask app can be locally tested using:

- authenticate first
```angular2html
gcloud auth login --update-adc
```

- run application from terminal
```angular2html
python main.py
```
To see if the api is running you can use url = 'http://127.0.0.1:8000/ and you should see the following message:
'Sentiment Analysis Model'.

You can then run the rest_client.py script

# Setting up the cloud infrastructure

Below we show how set up the cloud infrastructure to create an REST API service deploying a model that we previously trained. This involves setting up a cloud storage bucket to store model files (joblib, pickle or other) and data. We package the code into a container image stored on google artifact. We can then deploy the image using cloud run service.

Set the following env variable in your terminal before running the commands:

- PROJECT_ID: google project ID
- REGION: region used in the project e.g. us-central1
- IMAGE: container image for the app
- REPOSITORY: location of the container registry stored in artifact registry
- GITHUB_USERNAME: the user name for your github account
- GITHUB_REPOSITORY: the github repo used in the ci/cd pipeline


You can get the project ID this way:

```
gcloud config get-value project
```

# Build app container image with docker

- authenticate first
```angular2html
gcloud auth login --update-adc
```

First, you need to make sure you have an image built for the container. I do this locally using docker. Follow the instructions below:

```
docker build -t flask_app .

docker build --no-cache -t flask_app .
docker image list #checking built images
docker ps #checking containers running
```
if you want to remove an sepcifc image and remove cash before recreating the image:

```angular2html
docker rmi -f <image_id>
docker builder prune
```
Once built we can bash inside a specific docker image by doing this:

```
docker run -it flask_app bash
```

To run the container locally with the app code, you need to pass env variables and the google cloud credentionsl

```angular2html
docker run -it -p 8000:8000 flask_app

docker run -p 8000:8000 \
           -v /home/benoit/.config/gcloud/application_default_credentials.json:/tmp/application_default_credentials.json \
           -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/application_default_credentials.json \
            flask_app:latest

docker run -p 8000:8000 \
           -v /Users/benoitparmentier/.config/gcloud/application_default_credentials.json:/tmp/application_default_credentials.json \
           -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/application_default_credentials.json \
            flask_app:latest

Bash inside of running container called 'serene_benz'

docker exec -ti serene_benz bash


```
#When using docker, check if it is running using
http://localhost:8000/

## To deploy with cloud run and artifact registry

Deploy the function from the command line with gcloud.

https://medium.com/@ThatJenPerson/getting-started-with-artifact-registry-deploying-to-cloud-run-7aa9f2c65d07
https://medium.com/codex/how-to-store-docker-images-in-google-artifact-registry-499feb23bd80

```angular2html

gcloud artifacts repositories create sentiment-analysis-model \
    --repository-format=docker \
    --location=$REGION \
    --project=$PROJECT_ID \
    --description="api sentiment-analysis-model"
```
Authenticate before pushing an image:
```angular2html
gcloud auth configure-docker \
    $REGION-docker.pkg.dev
```
Note that the full name of a artifact repo is the following:
REGION-docker.pkg.dev/$PROJECT-ID/$REPOSITORY

REGION: the region used in the project and used for the registry to store the image
IMAGE = 'sentiment_app_model'
PROJECT-ID = the project ID used for this app
REPOSITORY = 'sentiment-analysis-model' #artifact registry repo

First build a local image with a tag name (here latest). Then add a tag to push into the google artifact registry repository. Tags are human-readable 
aliases for the full image name ( eg. ab83c9ac75fd...).

The last step is to push the image to the repo and then list all images present in gcloud container registry.

```angular2html
docker build --tag sentiment_app_model:latest .
docker tag  sentiment_app_model:latest $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/sentiment_app_model:latest
docker push $REGION-docker.pkg.dev/$PROJECT_ID$/$REPOSITORY/sentiment_app_model:latest
gcloud artifacts docker images list $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY --include-tags
```
https://docs.docker.com/engine/reference/commandline/tag/


Let's now deploy the service using google cloud run. We need to indicate where the image is located in the artifact repo and configure the serverless compute. Note that we are able to scale down to zero. This means that the service will start only when the API is hit (a request comes in). We keep the resources low to lower (512Mi and one cpu) the cost.

```
gcloud run deploy SERVICE --image \
REPO-LOCATION-docker.pkg.dev/$PROJECT-ID/$IMAGE \
[--platform managed --region $REGION]

gcloud run deploy sentiment-api \
  --image=$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE:latest \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --min-instances=0 \
  --max-instances=1 \
  --concurrency=1 \
  --memory=512Mi \
  --cpu=1
```

Note that port 8080 is required not 8000.

You can check the service is running using the google cloud console GUI or send a request directly:

```
curl -X POST https://sentiment-api-blablabla.$REGION.run.app/ \
  -H "Content-Type: application/json" \
  -d '{"text": "The meal service was not very good and we didn'\''t get water"}'
```

#https://medium.com/fullstackai/how-to-deploy-a-simple-flask-app-on-cloud-run-with-cloud-endpoint-e10088170eb7
#https://medium.com/google-cloud/deploy-a-python-flask-server-using-google-cloud-run-d47f728cc864


TO DO
- use uv instead of pip
- Right now you load from a bucket every time. Don’t do that inside the request.

# Access and service account for cloud run and github action

We need to set up access and coordination among different google services. This will require several service accounts:

- cloud-run-sa: cloud run account with roles to access artifact registry and cloud storage.
- github-actions-sa: used to manage access by github. 

Since github is an external application/service, this is a bit more complex to setup. There are two options:
- export github actions service account keys and store them as secret in the  github.
- use workforce/workload identity federation to generate a temporay token to give github actions access to google cloud resources when uring the ci/cd pipeline. We show both ways but I opted for the Workload Identiy Federation since this is better practice and avoids cloud key leakage.

Let's first create the github action service account:

```
gcloud iam service-accounts create github-actions-sa \
  --display-name="GitHub Actions SA"
```

*** Enable required APIs to authenticate***


**Let grant required roles for github service account**

- Allows to deploy images in cloud run using github actions

```
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"
```

- Allows to push container images to registry:

```
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"
```

- Allows the service account to act as / impersonate other service accounts. This is useful to use cloud run:

```
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

**Export key for service account**

We can export the json key for later usage or to store in the relevant github repo for the ci-cd pipleline.

```
gcloud iam service-accounts keys create key.json \
  --iam-account=github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com
```

Add secrets to GitHub
Go to your repo → Settings → Secrets and variables → Actions and add:

GCP_SA_KEY → paste contents of key.json
GCP_PROJECT_ID → your GCP project ID (e.g. mlops-blabla)

## **Using Workload Identity Federation instead of key**

I use Workload Identity Federation instead of a JSON key for better security. It avoids storing a long-lived credential in GitHub Secrets.


### 1. Let's enable the necessary apis/services from gcloud:

```
gcloud services enable \
iamcredentials.googleapis.com \
cloudresourcemanager.googleapis.com \
sts.googleapis.com \
--project $PROJECT_ID
```

Together, these three APIs are the foundation for keyless GitHub Actions authentication to GCP:

GitHub OIDC token → STS (exchange) → short-lived GCP token → impersonate service account (IAM Credentials) → deploy

- iamcredentials.googleapis.com — IAM Service Account Credentials API
Allows generating short-lived credentials (tokens) for service accounts. This is the core API that powers Workload Identity Federation, which lets GitHub Actions authenticate to GCP without storing a long-lived JSON key file.

- cloudresourcemanager.googleapis.com — Cloud Resource Manager API
Allows querying and managing GCP project metadata and IAM policies. It's needed so tools (like GitHub Actions or gcloud) can read/validate project-level IAM bindings — including the ones set by the commands you showed earlier.

- sts.googleapis.com — Security Token Service API
Exchanges external credentials (like a GitHub OIDC token) for short-lived GCP tokens. This is the other half of Workload Identity Federation — GitHub presents its OIDC token to STS, which hands back a GCP-compatible token.

### 2. create cloud run sa

If not done before:

```
gcloud iam service-accounts create "cloud-run-sa" \
  --project=$PROJECT_ID \
  --display-name="Cloud Run Runtime SA"
```
### 3. Create a Workload Identity Pool

```
gcloud iam workload-identity-pools create "github-pool" \
  --location="global" \
  --display-name="GitHub Actions Pool" \
  --project $PROJECT_ID
```

### 4. Create the Service Account (if you haven't already)

```
gcloud iam service-accounts create github-actions-sa \
  --display-name="GitHub Actions SA" \
  --project $PROJECT_ID
```

### 5. Grant the SA the roles it needs

```
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

### 6. Create a Provider inside the pool

```
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.actor=assertion.actor" \
  --attribute-condition="assertion.repository==GITHUB_USERNAME/GITHUB_REPO" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --project=$PROJECT_ID
```

### 7. Allow GitHub Actions (for your specific repo) to impersonate the SA

Github-actions-sa needs permission to act as cloud-run-sa when deploying. Let's add this policy binding:

```
gcloud iam service-accounts add-iam-policy-binding \
  github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')/locations/global/workloadIdentityPools/github-pool/attribute.repository/$REPO" \
  --project $PROJECT_ID
```
  
### 8. Print the values you'll need for GitHub vars

```
echo "WIF_PROVIDER:"

gcloud iam workload-identity-pools providers describe github-provider \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --project $PROJECT_ID \
  --format="value(name)"

echo "WIF_SA:"
echo "github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com"

```

### 9. Run github ci-cd pipeline

After setting up and configuring the permissions, you can now run the .yml containing the ci-cd githubactions pipeline.