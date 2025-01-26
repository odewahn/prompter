Build the image:

docker build -t cloud_run_test -f CloudRun.Dockerfile .

Tag it...

```
docker tag cloud_run_test us-west1-docker.pkg.dev/eli5-odewahn-sparktime/llm-experiments/cloud_run_test
```

Push it...

```
docker push us-west1-docker.pkg.dev/eli5-odewahn-sparktime/llm-experiments/cloud_run_test:latest
```
