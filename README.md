# Installation and Usage

See [https://odewahn.github.io/prompter/](https://odewahn.github.io/prompter/)

# To Do / Wishlist

## Short

- Improve documentation
  -- more examples
  -- how to run in docker

- UI improvements
  -- Jazz up the UI a bit / make it match the docs
  -- Add a "processing" UI state - maybe use the context to share data. Simple thing would be to poll an environment variable

- Additional functionality
  -- Compute embeddings for blocks and save them out
  -- Get something running as a webhook
  -- Get something deployed via cloud run
  -- use tiktoken to get token counts

## Medium

- Support for Anthropic
- Be able to do dimensionality reduction on the embeddings
- show rate limits somehow

## Longer

- A much deeper ability to compute and manage context. For example, use a cimplete command to create something that tcan then be used as context for another completion. Base it usely on unix file perms -- world, group, block.

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

I used this this tool, whih does all the steps in a nice package:

https://github.com/txoof/codesign

Note that I renamed it `pycodesign` when I downloaded it, even though it's called `pycodesign.py` when you download it from the repo.

```
cd dist
pycodesign ../pycodesign.ini
```

NB: Before you can notarize, you need to have a developer account with Apple and have set up the notarization process. This is a bit of a pain, but it's not too bad. You can find the instructions [here](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution).

First, set up the keychain stuff:

```
xcrun notarytool store-credentials ODEWAHN \
 --apple-id andrew@odewahn.com \
 --team-id 8R36RY2J2J
```

## Build for Docker

First, build the image:

```
docker build --no-cache  -t prompter -f Prompter.Dockerfile .
```

Then run it -- you can use environment variables to pass in the commands you want to run:

```
docker run -it --env-file .env prompter /bin/bash
```

## Retrieving the binary from the container

https://stackoverflow.com/questions/25292198/docker-how-can-i-copy-a-file-from-an-image-to-a-host

```
id=$(docker create prompter)
docker cp $id:/usr/local/bin/prompter ./dist/prompter.ubuntu
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

# Setting up the docs site

I use [mkdocs](https://www.mkdocs.org/) to build the documentation site. It's a static site generator that uses markdown files to create a site. The site is hosted on GitHub pages.

## Setup

First, create a new virtual environment:

```
python -m venv .docs-venv
```

Then activate it:

```
source .docs-venv/bin/activate
```

Then install the requirements:

```
pip install -r docs-requirements.txt
```

## Developing and publishing

To develop the site:

```
mkdocs serve -a localhost:8080
```

To publish the site:

```
mkdocs gh-deploy
```

## Markup notes

There were some conflicts between markdown formatting in VSCode and MKDocs material theme, especially for the `admonition` element. Use [PyMdown Extensions](https://facelessuser.github.io/pymdown-extensions/extensions/blocks/plugins/admonition/) to get the same formatting in VSCode and the site.

```
/// admonition | Some title
Some content
///
```
