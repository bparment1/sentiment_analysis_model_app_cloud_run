# Sentiment Analysis app

This app provides a REST api to predict text sentiments.

To call the API, use the following json format:
```angular2html

body = {
    text: "The meal service was not very good and we didn't get water"
}
```


Call with curl:

```angular2html
curl -m 310 -X POST https://us-east1-mlops-494715.cloudfunctions.net/sentiment_analysis_model_app_cloud_fun \
-H "Authorization: bearer $(gcloud auth print-identity-token)" \
-H "Content-Type: application/json" \
-d '{text: "The meal service was not very good and we didn't get water"}'
```

## Test function

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

## Using docker

- authenticate first
```angular2html
gcloud auth login --update-adc
```

First, you need to make sure you have an image built fo the container. 
Build de container this way:

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
    --location=us-east1 \
    --project=mlops-494715 \
    --description="api sentiment-analysis-model"
```
Authenticate before pushing an image:
```angular2html
gcloud auth configure-docker \
    us-east1-docker.pkg.dev
```
Note that the full name of a artifact repo is the following:
LOCATION-docker.pkg.dev/PROJECT-ID/REPOSITORY

You can then use the following path 'us-east1-docker.pkg.dev/mlops-494715/sentiment-analysis-model'

LOCATION = 'us-east1'
IMAGE = 'sentiment_app_model'
PROJECT-ID = 'mlops-494715'
REPOSITORY = 'sentiment-analysis-model' #artifact repo

First build a local image with a tag name (here latest). Then add a tag to push into the artifact registry repository. Tags are human-readable 
aliases for the full image name ( eg. ab83c9ac75fd...).

 The last step is to push 
the image to the repo and list all image present in gcloud.

```angular2html
docker build --tag sentiment_app_model:latest .
docker tag  sentiment_app_model:latest us-east1-docker.pkg.dev/mlops-494715/sentiment-analysis-model/sentiment_app_model:latest
docker push us-east1-docker.pkg.dev/mlops-494715/sentiment-analysis-model/sentiment_app_model:latest
gcloud artifacts docker images list us-east1-docker.pkg.dev/mlops-494715/sentiment-analysis-model --include-tags
```
https://docs.docker.com/engine/reference/commandline/tag/


```
gcloud run deploy SERVICE --image \
REPO-LOCATION-docker.pkg.dev/PROJECT-ID/IMAGE \
[--platform managed --region RUN-REGION]

gcloud run deploy sentiment-api \
  --image=us-east1-docker.pkg.dev/mlops-494715/sentiment-analysis-model/sentiment_app_model:latest \
  --region=us-east1 \
  --platform=managed \
  --allow-unauthenticated \
  --min-instances=0 \
  --max-instances=1 \
  --concurrency=1 \
  --memory=1Gi \
  --cpu=1

  gcloud run deploy sentiment-api \
  --image=us-east1-docker.pkg.dev/mlops-494715/sentiment-analysis-model/sentiment_app_model:latest \
  --region=us-east1 \
  --platform=managed \
  --allow-unauthenticated \
  --min-instances=0 \
  --max-instances=1 \
  --concurrency=1 \
  --memory=512Mi \
  --cpu=1
```


```
curl -X POST https://sentiment-api-blablabla.us-east1.run.app/ \
  -H "Content-Type: application/json" \
  -d '{"text": "The meal service was not very good and we didn'\''t get water"}'
```

#https://medium.com/fullstackai/how-to-deploy-a-simple-flask-app-on-cloud-run-with-cloud-endpoint-e10088170eb7
#https://medium.com/google-cloud/deploy-a-python-flask-server-using-google-cloud-run-d47f728cc864


TO DO
- use uv instead of pip
- Right now you load from a bucket every time. Don’t do that inside the request.

Instead:

Load once at startup

- add multiple models
- add mlflow tracking
- use docker compose instead of other commands



gcloud iam service-accounts create github-actions-sa \
  --display-name="GitHub Actions SA"

# Grant required roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# Export key
gcloud iam service-accounts keys create key.json \
  --iam-account=github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com
2

3. Add secrets to GitHub
Go to your repo → Settings → Secrets and variables → Actions and add:

GCP_SA_KEY → paste contents of key.json
GCP_PROJECT_ID → your GCP project ID (e.g. mlops-494715)

Pro tip — use Workload Identity Federation instead of a JSON key for better security. It avoids storing a long-lived credential in GitHub Secrets. Let me know if you want that version too.

```
export PROJECT_ID=mlops-494715
export REPO=your-github-username/your-repo-name   # e.g. bparment1/sentiment-analysis-model-app-cloud-run
export YOUR_GITHUB_USERNAME
export YOUR_REPO #github repo used 

# 1. Enable required APIs
gcloud services enable iamcredentials.googleapis.com \
  cloudresourcemanager.googleapis.com \
  sts.googleapis.com \
  --project $PROJECT_ID

#2. create cloud run sa
gcloud iam service-accounts create "cloud-run-sa" \
  --project=$PROJECT_ID \
  --display-name="Cloud Run Runtime SA"

# 2. Create a Workload Identity Pool
gcloud iam workload-identity-pools create "github-pool" \
  --location="global" \
  --display-name="GitHub Actions Pool" \
  --project $PROJECT_ID

# 4. Create the Service Account (if you haven't already)
gcloud iam service-accounts create github-actions-sa \
  --display-name="GitHub Actions SA" \
  --project $PROJECT_ID

# 5. Grant the SA the roles it needs
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# 3. Create a Provider inside the pool
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.actor=assertion.actor" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --project $PROJECT_ID

gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.actor=assertion.actor" \
  --attribute-condition="assertion.repository=='YOUR_GITHUB_USERNAME/YOUR_REPO'" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --project=$PROJECT_ID

gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.actor=assertion.actor" \
  --attribute-condition="assertion.repository=='bparment1/sentiment-analysis-model-app-cloud-run'" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --project=$PROJECT_ID

gcloud iam workload-identity-pools providers update-oidc "github-provider" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --attribute-condition="assertion.repository=='bparment1/sentiment_analysis_model_app_cloud_run'" \
  --project=$PROJECT_ID

# 6. Allow GitHub Actions (for your specific repo) to impersonate the SA

gcloud iam service-accounts add-iam-policy-binding \
  github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')/locations/global/workloadIdentityPools/github-pool/attribute.repository/$REPO" \
  --project $PROJECT_ID



# 7. Print the values you'll need for GitHub vars
echo "WIF_PROVIDER:"
gcloud iam workload-identity-pools providers describe github-provider \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --project $PROJECT_ID \
  --format="value(name)"

echo "WIF_SA:"
echo "github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com"



#8 Add impersonification

This is the exact error I mentioned earlier — github-actions-sa needs permission to act as cloud-run-sa when deploying. Run this:
gcloud iam service-accounts add-iam-policy-binding \
  cloud-run-sa@$PROJECT_ID.iam.gserviceaccount.com \
  --member="serviceAccount:github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser" \
  --project=$PROJECT_ID

export REPO="bparment1/sentiment_analysis_model_app_cloud_run"

I fixed this error

gcloud iam workload-identity-pools providers update-oidc "github-provider" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --attribute-condition="assertion.repository=='bparment1/sentiment_analysis_model_app_cloud_run'" \
  --project=$PROJECT_ID

gcloud iam service-accounts add-iam-policy-binding \
  github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')/locations/global/workloadIdentityPools/github-pool/attribute.repository/$REPO" \
  --project=$PROJECT_ID
```