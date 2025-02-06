# Examples

Here are a few samples.

## Create a summary from an epub

### Tasks

There are two key tasks: summarizing an individual block and then summarizing the summary. Here's the prompt to summarize the block, which is saved in a file called `task-summarize-block.md`:

```jinja
Summarize the following block of text:

{{content}}

Do this in 250 words or fewer using markdown fomatting.  Focus on adding bullet lists.
```

Here's the prompt to summarize the summary, which is saved in a file called `task-summarize-summary.md`:

```jinja
This is a summary of a chapter that was constucted from overlapping chunks of text from a longer work:

{{content}}

Summarize it into 250 words or fewer.
```

### Prompterfile

Here's the full program in a `Prompterfile`:

```sh
load test.epub
transform clean-epub html-to-md transform token-split --n=5000
complete summarize-block.task
squash
complete cleanup-summary.task
retag summary-{{block_tag}}.md
write
```

## Get the gist of a book using chapter headers
