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

prompter uses Pyinstaller to create a single executable file. To install it, [download the latest release](https://github.com/oreillymedia/prompter/releases), unzip it, and then put it somewhere in your path. You will likely also need to [enable it to run on a mac by changing the permissions](https://iboysoft.com/howto/cannot-be-opened-because-it-is-from-an-unidentified-developer.html).

To test that it's working correctly, run:

```
./prompter/prompter/prompter version
```

Note that it's pretty slow to start. This is an artifact of the way Pyinstaller works when it builds a single file for distribution. Once it's running, it's pretty fast. I should probably make a REPL for it.

# Usage

prompter is meant to help you explore the vairous transformations and prompts required to transform large amounts of content (like, a book). Here's a pretty typical way you might start a new project:

- Create a directory to hold your content. For example, you might download an EPUB or some files there.
- Run `prompter init` to create a new database. This will create a SQLITE database called `prompter.db` in the current directory (unless you override the name with the `--db` option).
- Load the content into the database with `prompter load --fn=*.epub`. This will create a new group with blocks for each chapter in the EPUB.

At this point, you might need to poke around a bit in the data to figure out how it's structured. You can use the `dump` command to inspect the blocks. Once you have an idea of how it looks, you can use the various transformations to clean up the data and split it into smaller blocks that will fit into the LLM's context window, which is typically around 8192 tokens. For example, you might use the `html-h1-split` transformation to split the text into blocks based on the H1 tags in the HTML. Finally, you might also want to restrict the blocks you're working with to a subset of the data. You can use the `filter` command to do this. For example, you might only want to work with blocks that have more than 1000 tokens.

Next, you can start creating prompt templates. These should be Jinja templates that include the text of the prompt and any metadata you want to include. When you run the `prompt` command, you'll pass in the name of the template and the metadata file, and each block in the set you supply will be passed into the template in the `{{block}}` variable. The fully rendered prompt will be sent to the LLM for completion.

Finally, you can use the `dump` command to write the results to a file, or transfer them into other blocks or metadata.

Once you've found the right set of transformations and filters, you can script the whole process to automate the generation of prompts and responses and save it as a bash script.

Note that prompter isn't meant to be a production tool -- it's mostly for exploratoy work to figure out how to structure your data and what prompts are effective for whatever you're trying to do. Once you've figured that out, it's likely that you would want to condense those operations into a single program that you can run at scale.

# Command Reference

prompter has the following commands:

- `init` -- create a new sqlite database to store data
- `load` -- load a file or files into a new group with blocks
- `transform` -- create a new group of blocks by applying a transformation to the current group
- `filter` -- create a new group of blocks by applying a filter to the current group
- `blocks` -- list all blocks in the current group
- `groups` -- list all groups
- `set-group` -- set the current group
- `prompt` -- generate prompts from a set of blocks based on metadata and a template
- `prompts` -- list all prompts
- `transfer-prompts` -- convert prompts into blocks or metadata
- `version` - show the version of the software
- `set-api-key` - set the api key used for the LLM
- `dump` - write blocks or prompts to standard output
- `squash` - concatenates all prompts with the same block tag into a new block; useful when recombining prompts computed from segments of a total work.
- `speak` -- converts the selected blocks into MP3 files using the OpenAI TTS API

## `init`

Creates an empty database. If no db is provided, the default is `prompter.db`.

### Arguments

- `--db` (optional) The name of the database file. Default is `prompter.db`.

### Examples

```
prompter init --db=database.db
```

## `load`

Loads a file or files into a new group, each of which contains a set of blocks. For example, loading an EPUB will create one new group with and optional tag you specificy, and then individual blocks for each chapter in the manifest. `load` currently supports EPUB or text (markdown, html, text, etc).

### Arguments

- `--fn` (required) The name of the file to load.
- `--group_tag` (optional) The tag of the group to create

### Examples

Load all HTML files:

```
prompter load --fn=*.html
```

Loading an EPUB will create a group for each chapter and a block for each chapter:

```
prompter load --fn=example.epub
```

You can provide a tag for the group so you can reference it later, like this:

```
prompter load --fn=example.epub --group_tag=example
```

## `transform`

The `transform` command creates new groups of blocks by applying a transformation rule to the current group. The transformations are:

- `token-split` - Breaks text into chunks of 2000 tokens
- `clean-epub` - Simplifies the HTML of an EPUB
- `html-h1-split` - Breaks HTML into blocks based on H1 tags
- `html-h2-split` - Breaks HTML into blocks based on H2 tags
- `html2md` - Converts HTML to Markdown
- `html2txt` - Converts HTML to text
- `new-line-split` - Splits text into blocks based on new lines
- `sentence-split` - Splits text into blocks based on sentences

### Arguments

`--transformation` (required) The name of the transformation to run; you can run multiple transformations by providing a comma-separated list of transformations.
`--group_tag` (optional) The tag to use for the new group. (Only valid when there are is a single transformation.)

### Examples

Apply 3 transformations to the current group:

```
prompter transform --transformation="clean-epub, html-h1-split, html2md"
```

Name a group:

```
prompter transform --transformation="clean-epub" --group_tag=cleaned-up-files
```

## `filter`

The `filter` command creates a new group of blocks by applying a filter to the current group. The filter is a SQL WHERE clause that filters the blocks in the current group. The filtered group is then set to the current group.

### Arguments

- `--where` (required) A SQL WHERE clause to filter the blocks in the current group.
- `--order` (optional) A SQL ORDER BY clause to order the results.
- `--group_tag` (optional) The tag to use for the new group.

### Examples

Filter blocks whose tag name starts with "chapter":

```
prompter filter --where="block_tag like 'chapter%'"
```

Filter blocks with more than 1000 tokens:

```
prompter filter --where="token_count > 1000"
```

## `groups`

Lists all groups.

### Arguments

- `--where` (optional) A SQL WHERE clause to filter the results
- `--order` (optional) A SQL ORDER BY clause to order the results.

### Examples

Show all current groups:

```
prompter groups
```

Show all groups with more than 50 blocks:

```
prompter groups --where="block_count > 50"
```

## `set-group`

Sets the group to the provided group tag.

### Arguments

`--group_tag` (required) The group tag to set as the current group.

### Examples

```
prompter set-group --group_tag=example
```

## `blocks`

List all blocks in the current group:

### Arguments

- `--where` (optional) A SQL WHERE clause to filter the results. Running `promplab blocks` will show the columns available for filtering. These are currently `['block_id', 'block_tag', 'parent_block_id', 'group_id', 'group_tag', 'block', 'token_count']`
- `--order` (optional) A SQL ORDER BY clause to order the results.

### Examples

Show all blocks in the current group

```
prompter blocks
```

Show all blocks with more than 1000 characters:

```
prompter blocks --where="token_count > 1000"
```

Select all blocks that match a tag:

```
prompter blocks --where="block_tag like 'chapter%'"
```

## `dump`

Write blocks or prompts to standard output.

### Arguments

- `--source` (required) The source to dump. Options are `blocks` or `prompts`. Default is `blocks`.
- `--where` (optional) A SQL WHERE clause to filter the results. Running `promplab blocks` will show the columns available for filtering. These are currently `['block_id', 'block_tag', 'parent_block_id', 'group_id', 'group_tag', 'block', 'token_count']`
- `--order` (optional) A SQL ORDER BY clause to order the results.
- `--delimiter` (optional) The delimiter to use when joining the blocks. Default is a newline.
- `--dir` (optional) The directory to write the files to. Default is standard output.
- `--extension` (optional) The extension to use for the files. Default is `txt`.

### Examples

Dump all blocks to standard output:

```
prompter dump
```

Dump all blocks with more than 1000 characters:

```
dump --source=blocks --where="block_tag like 'part03%'"
```

Dump all blocks with a comma delimiter:

```
dump --source=blocks --delimiter=","
```

Save all blocks to a file:

```
dump  --dir="~/Desktop/test"
```

## `prompt`

Generate prompts from a set of blocks based on metadata and a template, and then used an LLM complection endpoint to generate completions.

### Arguments

- `--task` (required) -- the filename or URL of the jinja template for the task
- `--persona` (optional) -- the filename or URL of the jinja template for the persona
- `--where` (optional) A SQL WHERE clause to filter the blocks that will be used to create the prompts.
- `--order` (optional) A SQL ORDER BY clause to order the results.
- `--model` (optional) The name of the model to use in the format `provider:model`, where provider is `openai` or `groq`, and model is the name of the model. The default is `openai:gpt-4o`. You can find the names of the models for each provider by running `prompter models --provider=openai|groq`.
- `--prompt_tag` (optional) A tag to use for the prompt; this tag can be referred to later in queries.
- `--globals` (optional) A YAML file with global metadata values that can be used in the prompt template.

### Examples

You run the prompt against a block using the `prompt` command:

```
prompter prompt --fn=extract-key-points.jinja --model=gpt-3.5-turbo --prompt_tag="extract-key-points"
```

Prompt for a specific group:

```
prompter prompt --fn=summarize.jinja --where="block_tag like 'ch12%'"
```

Prompt and provide global metadata from a file:

```
prompter prompt --fn=extract-key-points.jinja --globals=metadata.yml
```

## `models`

Prints all models available for a provider.

### Arguments

- `--provider` (required) The name of the provider. Options are `openai` or `groq`.

### Examples

Print all models for OpenAI:

```
prompter models --provider=openai
```

## `prompts`

Prints all prompts to standard output.

### Arguments

- `--where` (optional) A SQL WHERE clause to filter the results. Running `promplab prompts` will show the columns available for filtering. These are currently `['prompt_id', 'block_id', 'prompt', 'response', 'model', 'prompt_tag', 'created_at']`
- `--order` (optional) A SQL ORDER BY clause to order the results.

### Examples

Print all prompts:

```
prompter prompts
```

Print all prompts with a specific tag:

```
prompter prompts --where="prompt_tag like 'ch12%'"
```

## `transfer-prompts`

Convert prompts into blocks or metadata. This is useful is you want to do later processing with a prompt.

### Arguments

- `--where` (optional) A SQL WHERE clause to filter the results. Running `promplab transfer-prompts` will show the columns available for filtering. These are currently `['prompt_id', 'block_id', 'prompt', 'response', 'model', 'prompt_tag', 'created_at']`
- `--order` (optional) A SQL ORDER BY clause to order the results.
- `--to` (required) The type of object to transfer the prompts to. Options are `blocks` or `metadata`.
- `--metadata_key` (optional) The key to use for the metadata. Only valid when `--to=metadata`.

### Examples

Transfer prompts to blocks:

```
prompter transfer-prompts --to=blocks
```

Transfer prompts to metadata:

```
prompter transfer-prompts --to=metadata --metadata_key=key-points
```

## `version`

Prints the version of the software.

### Examples

```
prompter version
```

## `set-api-key`

Sets the API key used for the LLM. This is required to use the `prompt` command. NB: This key is stored in plain text in a file called `~/.prompter`.

### Examples

```
prompter set-api-key
```

## `run`

Runs a script that contains a series of commands. This is useful for automating the process of generating prompts and responses. The script is treated as a Jinja template, so that you can also do some basic logic in the script. For example, you might want to only run a command if a certain condition is met.

```
{% if format == "book" %}
   # Load a book
   load --fn=source/*.html
   transform --transformation="html2md,token-split"
   filter --where="block_tag like '%-ch%'"
{% else %}
   # Loading {{format}}
   load --fn=source/*.md
   transform --transformation="token-split"
{% endif %}
```

### Arguments

- `--fn` (required) The name of the script file to run.
- `--globals` (optional) A YAML file with global metadata values that can be used in the script
- `--preview` (optional) Prints the rendered script to standard output only (does not execute it).

### Examples

```
prompter run --fn=script.prompter
```

The `script.prompter` file might look like this:

```
cd --dir=~/Desktop/content/test
init
load --fn=test.txt --group_tag="raw"
blocks --where="group_tag='raw'"
transform --transformation="sentence-split"
blocks --order=block_id
```

Here's an example of a script that uses global metadata and a preview:

```
run --fn=/Users/odewahn/Desktop/content/summaries/summarizer.jinja --globals=metadata.yaml --preview
```

## `squash`

Concatenates all prompts with the same block tag into a new block. This is useful when recombining prompts computed from segments of a total work. For example, if you have a book that you've split into chapters, and you've generated prompts for each chapter, you can use `squash` to recombine the prompts into a single block.

### Arguments

- `--where` (optional) A SQL WHERE clause to filter the results. Running `promplab prompts` will show the columns available for filtering. These are currently `['prompt_id', 'block_id', 'prompt', 'response', 'model', 'prompt_tag', 'created_at']`

### Examples

Squash all prompts:

```
squash --group_tag='condensed-chapter-blocks'
```

## `speak`

Uses the openai API to convert the selected blocks into MP3 files. This is useful if you want to listen to the responses instead of reading them. Note that this command requires an OpenAI API key to be set, as well as that you have [ffmpeg](https://ffmpeg.org/) installed on your system.

### Arguments

- `--voice` - one of the [voices from the OpenAI API](https://platform.openai.com/docs/guides/text-to-speech/voice-options).
- `--where` (optional) A SQL WHERE clause to filter the results. Running `promplab prompts` will show the columns available for filtering. These are currently `['prompt_id', 'block_id', 'prompt', 'response', 'model', 'prompt_tag', 'created_at']`

# Development

This section is a little light right now since this is a single person project. I should probably write some tests, for example....

## TO DO

- Add the persona prompt into the hash computation in prompter

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

## Building the binary

Go through all the rigamarole to build the binary.

First, set up the keychain stuff:

xcrun notarytool store-credentials ODEWAHN \
 --apple-id andrew@odewahn.com \
 --team-id 8R36RY2J2J

## To build:

```
pyinstaller --noconfirm --clean prompter.spec
```

To inspect the packaged contents, you can do this:

```
pyi-archive_viewer -l prompter > archive.csv
```

I found this helpful when trying to debug why the binary was so big.

## To package, sign, and notarize

This tool does all the steps in a nice package:

https://github.com/txoof/codesign

Note that I renamed it `pycodesign` when I downloaded it, even though it's called `pycodesign.py` when you download it from the repo.

```
cd dist
pycodesign ../pycodesign.ini
```

## Various blind alleys and notes!

I went through a lot of steps to finally get a pkg built. The big insight was most of this stuff only works is you use pyinstaller's `onefile` option, rather than the diectory. The startup time there is slower, but it seems worth the hassle to make an installable binary.

First, be sure you're set up to run pyinstaller by reading [Build an executable with pyinstaller](http://www.gregreda.com/2023/05/18/notes-on-using-pyinstaller-poetry-and-pyenv/). This is another good [tutorial on pyinstaller](https://www.devdungeon.com/content/pyinstaller-tutorial). It took a bit of finagling to make this work, so YMMV.

From the root directory, run the following command:

```

pyinstaller \
 --name=prompter \
 --add-data="sql:sql" \
 --hidden-import=prompt_toolkit \
 --noconfirm \
 --clean \
 main.py

```

To view the sizes of the included files, cd into the `dist/_internal` directory and run:

```
du -hs *
```

Originally, I compiled this using `--onefile` but found that it became incredibly slow to start up. Ths seems to be a common complaint about pyinstaller. I think it also has to do with a virus scanner, which has to scan each file in the package as it's unzipped every time. So, I started just directibuting the dist folder. It's less convenient and clear, but gives an acceptable startup time.

### Codesigning

https://haim.dev/posts/2020-08-08-python-macos-app/

https://github.com/pyinstaller/pyinstaller/issues/5154

https://pyinstaller.org/en/v4.7/feature-notes.html#macos-binary-code-signing

https://github.com/pyinstaller/pyinstaller/issues/7320

https://gist.github.com/txoof/0636835d3cc65245c6288b2374799c43

https://www.linkedin.com/pulse/looking-distribute-your-python-script-mac-users-jai-goyal-aotsc/

https://forums.developer.apple.com/forums/thread/735581

https://apple.stackexchange.com/questions/395763/how-to-code-sign-my-python-script-package-packaged-for-mac-using-pyinstaller-w

https://stackoverflow.com/questions/21736367/signing-code-for-os-x-application-bundle

https://stackoverflow.com/questions/68884906/pyinstaller-error-systemerror-codesign-failure-on-macos

Then this:

codesign -s Developer -v --force --deep --timestamp --entitlements entitlements.plist -o runtime "dist/prompter.app"

### Using codesigning in pyinstaller

See https://pyinstaller.org/en/v4.7/feature-notes.html#macos-binary-code-signing

### Create the build

First, if you've not done so already, get the [codesign identity](https://github.com/pyinstaller/pyinstaller/issues/7320):

```
security find-identity -v -p codesigning
```

This is the value used in `codesign_identity` in the spec file. Then run the build:

```
pyinstaller --noconfirm --clean prompter.spec
```

#### Sign the app

Then sign the app. [Unlock the keychain before you use codesign](https://stackoverflow.com/questions/11712322/error-the-timestamp-service-is-not-available-when-using-codesign-on-mac-os-x):

```
security unlock-keychain login.keychain
```

Then:

```
codesign -s Developer -v -vvv --force --deep --timestamp --entitlements=entitlements.plist -o runtime "dist/prompter"
```

```
codesign --timestamp -s Developer --deep --force --options runtime "dist/prompter/_internal/Python.framework"


```

For debugging, see:

https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution/resolving_common_notarization_issues#3087735

```
codesign -vvv --deep --strict dist/prompter
```

### Notarizing

```
ditto -c -k --keepParent "dist/prompter" dist/prompter.zip
```

```
xcrun notarytool submit dist/prompter.zip \
 --apple-id andrew@odewahn.com \
 --password vmbz-ccnv-diov-xhsr \
 --team-id 8R36RY2J2J \
 --wait
```

If it gives you an "invalid" message, you can check why with

xcrun notarytool log d8948805-2088-4f1d-a660-69ae74573a99 --apple-id YOUR_APPLE_ID --team-id=YOUR_TEAM_ID

### With pycodesign

First, set up the keychain stuff:

xcrun notarytool store-credentials ODEWAHN \
 --apple-id andrew@odewahn.com \
 --team-id 8R36RY2J2J

Do a fresh build

Change into `dis/prompter` directory

Run

```
pycodesign.py pycodesign.ini
```

The run this:

codesign --timestamp -s Developer --deep --force --options runtime "dist/prompter/\_internal/Python.framework"

xcrun notarytool log \
 --apple-id=andrew@odewahn.com \
 --team-id=8R36RY2J2J \
 f5617b4f-f93c-4254-a364-cbca7a93fe6e
