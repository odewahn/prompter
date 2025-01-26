# prompter

prompter is a utility for managing common activities when processing large amounts of text with an LLM. It lets you:

- Load text from files or EPUBs into a database
- Transform text using a variety of transformations. For example, convert an EPUB to markdown, split a long block into smaller blocks, or split a block into sentences. A lot of this work is required to fit the text into the LLM's token limit.
- Filter out blocks of text. For example, you might only want to process one chapter in a book.
- Apply templated prompts to your blocks and send them to an LLM. You can use metadata in your prompts to make them more dynamic. For example, you might have a metadata file with keys like `title`, `author`, and `topic`. You can include these keys in your prompt templates.

prompter helps you massage text into smaller blocks that can be fed into an LLM using a [Jinja](https://jinja.palletsprojects.com/) template. This template contains the text of your prompt, along with variables that get passed in from the block. For example, you might have a template like this with three variables -- a topic, a title, an author, and a block of text:

```
You are a technical instructional designer who is reviewing
a book about {{topic}} called {{title}} by {{author}}.  Your job is to
summarize the key points in each section.  Here is some text in
markdown format for you to use summarize:

{{block}}
```

You supply the metadata in a YAML file, like this:

```yml
title: Fooing the Bar
topic: Python Programming
author: A. N. Other
```

When you run the `prompt` command in prompter, a block of text and the metadata is passed into the template:

```jinja
You are a technical instructional designer who is reviewing
a book about Python Programming called Fooing the Bar by A. N. Other.
Your job is to summarize the key points in each section.  Here is
some text in markdown format for you to use summarize:

<BLOCK OF TEXT>
```

This fully rendered text is sent to an LLM for completion. The process is repeated for the other blocks of content until all the sections you select are processed. You can then convert these resposes into new blocks or metadata, or just dump them out an save them in a file.

You can run it in an interactive mode or as a script. To run it interactively, run `prompter` with no arguments. You then enter commands at the prompt as if you were using the CLI.

![prompter interactive](misc/prompter-repl.png)

Finally, prompter can be used as part of a script to automate the process of generating prompts and responses. For example, here's an example of how tou might summarize the full contents of a book:

```bash
# Make sure the bash script exits if any command fails
set -e
# Create a new database
prompter init
# Load the epub
prompter load --fn=book.epub
# Apply a filter to only work on chapter
prompter filter --where="block_tag like 'ch%'"
# Clean up the extraneous HTML, split the text into sections, and convert to markdown
prompter transform --transformation="clean-epub, html-h1-split, html2md"
# Only work on sections with more than 1000 tokens
prompter filter --where="token_count > 1000" --group_tag=key-sections
# Apply the summarization template using the metadata in metadata.yml
prompter prompt --fn=summarize.jinja --globals=metadata.yml
# Write the results to a file
prompter dump --source=prompts > key-points.md
```

# Installation

# Usage

# Development

This section is a little light right now since this is a single person project. I should probably write some tests, for example....

## Set up the environment

```
python -m venv .venv
```

To activate:

```
source .venv/bin/activate
```

To deactivate:

```
deactivate
```

## Install the requirements

```
pip install -r requirements.txt
```

I've noticed that sometimes `pyinstaller` doesn't pick up these packages unless you also run them in the global environment where Python is installed, rather than in the virtual environment. I'm not sure why this is, but it's something to keep in mind.

NB: MAKE SURE YOU INCLUDE PYINSTALLER IN THE REQUIREMENTS FILE! OTHERWISE, WHEN YOU BUILD A BINARY, IT WILL INCLUDE ALL THE PACKAGES IN THE GLOBAL ENVIRONMENT, WHICH IS NOT WHAT YOU WANT.

## Frontend

## Build for OSx

```
pyinstaller --noconfirm --clean prompter.spec
```

### To package, sign, and notarize

Before you can notarize, you need to have a developer account with Apple and have set up the notarization process. This is a bit of a pain, but it's not too bad. You can find the instructions [here](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution).

First, set up the keychain stuff:

xcrun notarytool store-credentials ODEWAHN \
 --apple-id andrew@odewahn.com \
 --team-id 8R36RY2J2J

Then you can codesign the app. I used this this tool, whih does all the steps in a nice package:

https://github.com/txoof/codesign

Note that I renamed it `pycodesign` when I downloaded it, even though it's called `pycodesign.py` when you download it from the repo.

```
cd dist
pycodesign ../pycodesign.ini
```

## Build for Docker

First, build the image:

```
docker build -t prompter -f Prompter.Dockerfile .
```

Then run it -- you can use environment variables to pass in the commands you want to run:

```
docker run -it --env-file .env prompter /bin/bash
```

## Retrieving the binary from the container

https://stackoverflow.com/questions/25292198/docker-how-can-i-copy-a-file-from-an-image-to-a-host

```
id=$(docker create prompter)
docker cp $id:/usr/local/bin/prompter .
docker rm $id
```

This makes afile that you can then put somewhere so that it can be copied onto a machine.

## Setting up google cloud run

### Setup

```
gcloud auth configure-docker     us-west1-docker.pkg.dev
```

```
 gcloud projects add-iam-policy-binding eli5-odewahn-sparktime \
       --member='user:odewahn@oreilly.com' \
       --role='roles/artifactregistry.reader'

#       --role='roles/artifactregistry.writer' \
```

NB: In google artifact registry, create a repository called `llm-experiments` before you can push to it. You then push images based on a local name to the registry.

### Pushing to Google Artifact Registry

Create an image:

```
docker build -t prompter -f Prompter.Dockerfile .
```

Tag it:

```
docker tag prompter us-west1-docker.pkg.dev/eli5-odewahn-sparktime/llm-experiments/prompter
```

Push it:

```
docker push us-west1-docker.pkg.dev/eli5-odewahn-sparktime/llm-experiments/prompter:latest
```

### Setting up Google Cloud Run

Set up the job in the console
Create a Volume and a volume mount for the job (I mapped it to the `/output` directory)
