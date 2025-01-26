from us-west1-docker.pkg.dev/eli5-odewahn-sparktime/llm-experiments/prompter:latest

COPY . /app
WORKDIR /app

# Run prompter on prompterfile as the main entrypoint
ENTRYPOINT ["/usr/local/bin/prompter", "Prompterfile"]  