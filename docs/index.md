# Prompter

Prompter is a tool for developing content transformations with LLMs. It let's you create scripts that automate workflows, ike this:

```bash
load test.epub
transform html-to-md token-split --n=5000
complete summarize-block.task
squash
complete cleanup-summary.task
write
```

It also has an IDE to help create and test your scripts and prompts:

![Prompter](images/browser.png)

With prompter you can:

- Load text from files or EPUBs into a database
- Transform text using a variety of transformations. For example, convert an EPUB to markdown, split a long block into smaller blocks, or split a block into sentences. A lot of this work is required to fit the text into the LLM's token limit.
- Filter out blocks of text. For example, you might only want to process one chapter in a book.
- Apply templated prompts to your blocks and send them to an LLM. You can use context in your prompts to make them more dynamic. For example, you might have a context file with keys like `title`, `author`, and `topic`. You can include these keys in your prompt templates.
- Create scripts so that you can automate your workflows for new content
