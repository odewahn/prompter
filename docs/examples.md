# Examples

## Summarize an EPUB

Here is an example of how you might make a summary of an EPUB book. It works by:

- splitting each chapter into overlapping blocks of text
- summarizing each block using a template
- squasing the summaries into a single summary
- using another prompt to clean up the summary

Here's the full program in a `Prompterfile`:

```sh
load test.epub
select "block_tag like 'chapter%'"
transform clean-epub html-to-md token-split --n=5000
complete summarize-block.task
squash
complete cleanup-summary.task
retag summary-{{block_tag}}.md
write
```

Here is the first task, which summarizes a single block of text:

/// note | `summarize-block.task`
Summarize the following block of text:

{{content}}

Do this in 250 words or fewer using markdown fomatting. Focus on adding bullet lists.
///

Here is the second task, which cleans up the "squashed" summaries of all the blocks:

/// note | `task-summarize-summary.md`
This is a summary of a chapter that was constucted from overlapping chunks of text from a longer work:

{{content}}

Summarize it into 250 words or fewer.
///

## Make an audio file of GitHub trending repos

This example use the [mshibanami/GitHubTrendingRSS](https://github.com/mshibanami/GitHubTrendingRSS) project to convert an RSS feed (in this case, RSS 2.0) of GitHub trending projects into an audio file. Here's how it works:

- `load` the feed from the "All Languages" feed on [GitHub Trending RSS](https://mshibanami.github.io/GitHubTrendingRSS/)
- `transform` the feed into json using the `feed-to-abridged-json` command (there are several ways to summarize the feed data)
- `complete` a prompt that converts the json into a markdown file
- `speak` to make the audio file

Here's an example of the output of the `feed-to-abridged-json` command when run on the feed:

```json
[
    {
        "title": "langgenius/dify",
        "link": "https://github.com/langgenius/dify",
        "summary": "<p>Dify is an open-source LLM app development platform. Dify's intuitive interface combines AI workflow, RAG pipeline, agent capabilities, model management, observability features and more, letting you quickly go from prototype to production.</p><hr /><p><img alt=\"cover-v5-optimized\" src=\"https://github.com/langgenius/dify/assets/13230914/f9e19af5-61ba-4119-b926-d10c4c06ebab\" /></p> \n<p align=\"center\"> \ud83d\udccc <a href=\"https://dify.ai/blog/introducing-dify-workflow-file-upload-a-demo-on-ai-podcast\">Introducing Dify Workflow File Upload: Recreate Google NotebookLM Podcast</a> </p> \n<p align=\"center\"> <a href=\"https://cloud.dify.ai\">Dify Cloud</a> \u00b7 <a href=\"https://docs.dify.ai/getting-started/install-self-hosted\">Self-hosting</a> \u00b7 <a href=\"https://docs.dify.ai\">Documentation</a> \u00b7 <a href=\"https://udify.app/chat/22L1zSxg6yW1cWQg\">Enterprise inquiry</a> </p> \n<p align=\"center\"> <a href=\"https://dify.ai\" target=\"_blank\"> <img alt=\"Static Badge\" src=\"https://img.shields.io/badge/Product-F04438"
    },
    ...
]
```

Here's the `Prompterfile`:

```sh
load https://mshibanami.github.io/GitHubTrendingRSS/weekly/all.xml
transform feed-to-abridged-json
complete summarize-trending-repos.task
speak
```

Here's the `summarize-trending-repos.task` task:

/// note | `summarize-trending-repos.task`
The prompt goes here
///

## Using Jinja in a Prompterfile

```sh
load data/source/*.html
select "block_tag like '%-ch%'"
transform strip-attributes extract-headers
complete task-summarize-block.txt
retag gist
squash --tag=squashed
{% for duration in ['30-seconds', '2-minutes'] %}
   checkout squashed
   # Set an environment variable to set context that can be used in the prompt
   set DURATION {{duration}}
   complete task-get-the-gist-duration.txt --context=data/metadata.yaml --model=gpt-4o
   retag gist-{{duration}}
   speak --speed=1.2
{% endfor %}
```

## Using `retag` to change filenames
