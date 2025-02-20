# Quickstart

[Prompter](https://github.com/odewahn/prompter) is a development that provides both a REPL and a GUI that allows you to tool for apply prompt templates to content.

- block: chunks of text of any size. The goal of prompter is to get all blocks in a work to be smaller than the context window for LLM models
- group: sets of blocks that are created during actions like loading, transforming, or squashing other blocks. You can give a group a meaningfule name by supplying a `--group_tag` in the command that is creting it. Otherwise prompter will generate a random name for you.
- current group: the set of blocks that are the result of the most recent operation

Most prompter workflows look something like this:

- Load content into a SQLite database
- Convert the content into a format approriate for use with an LLM (e.g., epub => markdown)
- Break the content into smaller blocks that can fit within the context window of most LLMs (currently 8000 tokens). Most books or courses will be 200,000 tokens or more, so they require some degree of pre-processing.
- Apply prompt templates (both task and persona) and metadata the blocks and sending them to the LLM for completion
- Store and manage the results as new blocks

Commands in prompter have a basic syntax that consists of a command name and a set of arguments that follow typical command line format. For example, completing a prompt looks like this:

```
complete extract-key-points.task --persona=oreilly-short.txt --context=metadata.yaml
```

You can find full documentation for prompter at https://github.com/odewahn/prompter.

The following sections assume you have followed the instructions above and downloaded some content and prompts into a root directory.

## Installation and setup

Download and install prompter from the [releases page](https://github.com/odewahn/prompter/releases).

Next, create a working direcory. For the purposes of this walkthrough, let's assume all files are in a directory called `genai-tutorial`:

```
cd ~
mkdir genai-tutorial
cd genai-tutorial
code .
```

Within VSCode, open a terminal and type `prompter`. Your environment should look something like this:

![prompter in vscode](images/prompter-in-vscode.png)

## Summarizing an Essay

Let's start with a simple example -- summarizing an essay. The main things to understand about using prompter are:
