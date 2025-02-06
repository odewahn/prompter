# prompter

prompter is a utility for managing common activities when processing large amounts of text with an LLM. It lets you:

- Load text from files or EPUBs into a database
- Transform text using a variety of transformations. For example, convert an EPUB to markdown, split a long block into smaller blocks, or split a block into sentences. A lot of this work is required to fit the text into the LLM's token limit.
- Filter out blocks of text. For example, you might only want to process one chapter in a book.
- Apply templated prompts to your blocks and send them to an LLM. You can use context in your prompts to make them more dynamic. For example, you might have a context file with keys like `title`, `author`, and `topic`. You can include these keys in your prompt templates.

prompter helps you massage text into smaller blocks that can be fed into an LLM using a [Jinja](https://jinja.palletsprojects.com/) template. This template contains the text of your prompt, along with variables that get passed in from the block. For example, you might have a template like this with three variables -- a topic, a title, an author, and a block of text:

```
You are a technical instructional designer who is reviewing
a book about {{topic}} called {{title}} by {{author}}.  Your job is to
summarize the key points in each section.  Here is some text in
markdown format for you to use summarize:

{{block}}
```

You supply the context in a YAML file, like this:

```yml
title: Fooing the Bar
topic: Python Programming
author: A. N. Other
```

When you run the `prompt` command in prompter, a block of text and the context is passed into the template:

```jinja
You are a technical instructional designer who is reviewing
a book about Python Programming called Fooing the Bar by A. N. Other.
Your job is to summarize the key points in each section.  Here is
some text in markdown format for you to use summarize:

<BLOCK OF TEXT>
```

This fully rendered text is sent to an LLM for completion. The process is repeated for the other blocks of content until all the sections you select are processed. You can then convert these resposes into new blocks or context, or just dump them out an save them in a file.

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
# Apply the summarization template using the context in context.yml
prompter prompt --fn=summarize.jinja --globals=context.yml
# Write the results to a file
prompter dump --source=prompts > key-points.md
```
