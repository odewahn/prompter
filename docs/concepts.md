# Understanding Prompter

Prompter is a tool for applying Large Language Model (LLM) prompts to content at scale. It provides both a command-line REPL interface and a GUI for managing the workflow of:

1. Loading content from various sources
2. Processing that content into LLM-friendly chunks
3. Applying prompts systematically
4. Managing and storing the results

## Core Concepts

Before diving in, it's important to understand these key concepts:

### Blocks
A block is a chunk of text that can be processed by an LLM. Blocks are the fundamental unit in Prompter:
- They must fit within an LLM's context window (typically 8K tokens)
- Can be in various formats (HTML, Markdown, plain text)
- Have metadata like IDs and tags for tracking

### Groups
Groups are collections of related blocks:
- Created when you load, transform, or combine blocks
- Have a unique tag for identification (auto-generated or user-specified)
- Only one group is "active" at a time (the current group)

### Workflow
A typical Prompter workflow follows these steps:

1. **Load** content into the SQLite database
2. **Transform** content into LLM-friendly format (e.g., HTML → Markdown)
3. **Split** content into appropriate block sizes
4. **Apply** prompts (tasks + personas) to blocks
5. **Manage** the results as new blocks

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
