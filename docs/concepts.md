# Quickstart: Making summaries with prompter

[Prompter](https://github.com/odewahn/prompter) is a tool for automating the process of applying prompt templates to blocks of content. It provides a REPL that allows you to:

- Load content into a local SQLite database
- Convert the content into a format approriate for use with an LLM (e.g., epub => markdown)
- Break the content into smaller blocks that can fit within the context window of most LLMs (currently 8000 tokens). Most books or courses will be 200,000 tokens or more, so they require som degree of preprocessinf.
- Apply prompt templates (both task and persona) and metadata the blocks and sending them to the LLM for completion
- Store and manage the LLM output

Commands in prompter have a basic syntax that consists of a command name and a set of arguments that follow typical command line format. For example, completing a prompt looks like this:

```
prompt --task=../prompts/tasks/extract-key-points.txt --persona=../prompts/tasks/oreilly-short.txt --global=../metadata.yaml
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

## Some fundamental concepts

Let's start with a simple example -- summarizing an essay. The main things to understand about using prompter are:

- block -- chunks of text of any size. The goal of prompter is to get all blocks in a work to be smaller than the context window for LLM models
- group -- sets of blocks that are created during actions like loading, transforming, or squashing other blocks. You can give a group a meaningfule name by supplying a `--group_tag` in the command that is creting it. Otherwise prompter will generate a random name for you.
- current group -- the set of blocks that are the result of the most recent operation
- prompt -- a templated task (and persona) that are applied to a block and sent to an LLM for completion.
  -- prompt responses -- This output returned when a prompt is sent to the LLM. These can be used to create new blocks, which enables you to chain commands together to create more complex workflows.

```
cd ~/genai-tutorial
git clone git@github.com:odewahn/cat-essay.git
```

Start prompter:

```
prompter
```

First, create a database:

```
init
```

Next, load in the essay:

```
load --fn=cat-essay.txt
```

This will create a new group (a set of content named with a `group_tag`) with 1 block (a chunk of text). Run the `blocks` command to see the blocks:

```
blocks
                                                        Current Blocks
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ block_id ┃ block_tag     ┃ parent_block_id ┃ group_id ┃ group_tag           ┃ block                          ┃ token_count ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ 1        │ cat-essay.txt │ 0               │ 1        │ table-read-state-of │ Man's best friend has          │ 354         │
│          │               │                 │          │                     │ historically been              │             │
└──────────┴───────────────┴─────────────────┴──────────┴─────────────────────┴────────────────────────────────┴─────────────┘

1 blocks with 354 tokens.
Current group id = (1, 'table-read-state-of')
```

You can see the content with the `dump` command:

```
dump
```

Now let's split this into separate paragraphs, which is done with the `transform` command:

```
transform --transformation=new-line-split
```

Now rerun the `blocks` command, ordering it by block_id:

```
blocks --order=block_id
                                                        Current Blocks
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ block_id ┃ block_tag     ┃ parent_block_id ┃ group_id ┃ group_tag           ┃ block                          ┃ token_count ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ 2        │ cat-essay.txt │ 1               │ 2        │ turn-reduce-medical │ Man's best friend has          │ 65          │
│          │               │                 │          │                     │ historically been              │             │
│ 3        │ cat-essay.txt │ 1               │ 2        │ turn-reduce-medical │ Cats are good companions. They │ 72          │
│          │               │                 │          │                     │ will snug                      │             │
│ 4        │ cat-essay.txt │ 1               │ 2        │ turn-reduce-medical │ Cats are also civilized        │ 86          │
│          │               │                 │          │                     │ housemates. Unli               │             │
│ 5        │ cat-essay.txt │ 1               │ 2        │ turn-reduce-medical │ Cats are easy to care for.     │ 76          │
│          │               │                 │          │                     │ They don’t ha                  │             │
│ 6        │ cat-essay.txt │ 1               │ 2        │ turn-reduce-medical │ Cats are low maintenance,      │ 59          │
│          │               │                 │          │                     │ civilized comp                 │             │
└──────────┴───────────────┴─────────────────┴──────────┴─────────────────────┴────────────────────────────────┴─────────────┘

5 blocks with 358 tokens.
Current group id = (2, 'turn-reduce-medical')
```

Notice that we now have a new group with five blocks that are each a paragraph from the original essay. You can see the content of a block with the `dump` command:

```
dump --where="block_id=3"

Cats are good companions. They will snuggle up and ask to be petted or scratched under the chin, and who can resist a purring cat? If they're not feeling affectionate, cats are generally quite playful; they love to chase balls and feathers — or just about anything dangling from a string. And when they’re tired from chasing laser pointers, cats will curl up in your lap to nap. Cats are loyal housemates.
```

Now we're ready to try to do some prompting:

```
prompt --task=summarize.jinja
[20:13:48] (1/5) Prompting block 4 cat-essay.txt Cats are also civilized    main.py:536
           housemates. Unli
[20:13:50] Elapsed time 2.2171173095703125  ->  Cats are polite and         main.py:554
           civilized housemates
           (2/5) Prompting block 5 cat-essay.txt Cats are easy to care for. main.py:536
           They don’t ha
[20:13:51] Elapsed time 0.7761921882629395  ->  Cats are low-maintenance    main.py:554
           pets that exerc
           (3/5) Prompting block 3 cat-essay.txt Cats are good companions.  main.py:536
           They will snug
           Elapsed time 0.6047070026397705  ->  Cats make excellent         main.py:554
           companions due to th
           (4/5) Prompting block 6 cat-essay.txt Cats are low maintenance,  main.py:536
           civilized comp
[20:13:52] Elapsed time 0.981417179107666  ->  Cats are ideal house pets    main.py:554
           due to their l
           (5/5) Prompting block 2 cat-essay.txt Man's best friend has      main.py:536
           historically been
[20:13:53] Elapsed time 0.642535924911499  ->  While dogs are traditionally main.py:554
           seen as man
                                                                            main.py:557
           Prompt response saved with id 1 and prompt_tag
           that-probably-trade
```

Run the `prompts` command to see the prompts that were created:

```
prompts
```

To see the actual reults from all the prompts, use the `dump` command:

```
dump --source=prompts --order=prompt_id
```

Now take all the prompts and squash them back into a single block. This time we'll supply our own group name so that we can refer to it later if we want:

```
squash --group_tag=summary
```

Then run the `blocks` command to see the new group:

```
blocks
                                                     Current Blocks
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ block_id ┃ block_tag     ┃ parent_block_id ┃ group_id ┃ group_tag ┃ block                               ┃ token_count ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ 7        │ cat-essay.txt │ 1               │ 3        │ summary   │ Cats are polite and civilized       │ 110         │
│          │               │                 │          │           │ housemates                          │             │
└──────────┴───────────────┴─────────────────┴──────────┴───────────┴─────────────────────────────────────┴─────────────┘

1 blocks with 110 tokens.
Current group id = (3, 'summary')
```

Since we now have a new block, we can consolidate things even further by asking the LLM to resummarize the squashed summaries:

```
prompt --task=summarize.jinja
[20:25:02] (1/1) Prompting block 7 cat-essay.txt Cats are polite and civilized housemates                     main.py:536
[20:25:03] Elapsed time 1.1071386337280273  ->  Cats are ideal house pets due to their l                      main.py:554
                                                                                                              main.py:557
           Prompt response saved with id 2 and prompt_tag fly-art-tell-threat
```

This time, we only have one prompt, so we can just transfer it directly back as single block:

```
transfer-prompts --to=blocks --group_tag=final
```

And, finally, we can see the results of the new prompt with the `dump` command:

```
dump

Cats are ideal house pets due to their low maintenance, civilized behavior, suitability for small living spaces, and affectionate companionship.
```

Great! Now we have the "recipe" for creating a summary for the content. Now we can put it all into a single script that can be run in one step. check out the file `summarize.prompter`, which has all the commands in one place:

```bash
init
load --fn=cat-essay.txt
transform --transformation=new-line-split
prompt --task=summarize.jinja --model=gpt-3.5-turbo
squash --group_tag=summarized-chunks --order=group_id
prompt --task=summarize.jinja
transfer-prompts --to=blocks --group_tag=final
dump
```

Note that there are a few new prompter options in this script, such as they ability to change the model you use when submitting a prompt. The full list of options can be found in the prompter documentation.

To run this, we can use the `run` command:

```
run --fn=summarize.prompter
```

Finally, try adding this to the final prompt to see a different persona and run the script again:

```
 --persona=pirate.txt
```

Rerunning the script (you should be able to just up-arrow) gives you this result:

```
Arrr, cats be excellent house pets, me hearties, for they be good companions, civilized members of the household, and easy to care for, makin' 'em a popular choice fer many a landlubber.
```

# Using `fetcher` to download content from the platform

[Fetcher](https://github.com/odewahn/fetcher) is a tool for downloading content from the O'Reilly learning platform. You provide the content identifier you want to download. Fetcher creates a directory based on the identfier and work title, and then downloads the source text into it. You need a JWT to be able to get full content. You can see the additional capabilities of fetcher at https://github.com/odewahn/fetcher.

To install it on OSX, doubleclick the fetcher package file from https://drive.google.com/drive/u/0/folders/15UZ9jfqb9bepiN4uNrSIZnJsiVXjNWX0.

## Startup

Open a terminal

```
cd ~/genai-tutorial
fetcher
```

It will take a minute for fetcher to start...

## Set up authentication

Run the following command once the REPL starts:

```
auth
```

You will be prompted to enter a JWT. If you don't have one, you can still use fetcher, but you will only get content previews. Note that this will create a configuration file called in your home directory called `.fetcher`. You should keep the content of this file private.

## Download content

You pull content using the `init` command:

```
init --identifier=9781492092384
```

Fetcher will create a direcory based on the identifier and title slug, and start downloading the content into it:

```
- 9781492092384-data-mesh
-- README.md
-- metadata.yml
-- source
   -- ...
   -- 00009-ch01-1-data-mesh-in-a-nutshell.html
   -- 00010-ch02-2-principle-of-domain-ownership.html
   -- 00011-ch03-3-principle-of-data-as-a-product.html
   -- 00012-ch04-4-principle-of-the-self-serve-data-platform.html
   -- ...
```

The `metadata.yml` file contains the a subset of the product metadata:

```
authors: Dehghani, Zhamak
content_format: book
description: <marketing description>
duration_seconds: null
format: book
identifier: '9781492092384'
issued: '2022-03-09'
publishers: O'Reilly Media, Inc.
title: Data Mesh
topics: Data Mesh
virtual_pages: 569
```

The `source` directory contains the text of each element in the project. Note that the file type depends on the type of content: books will have `html` data, while courses will be in `markdown` format.

# Prompt Templates

Once you have content downloaded, you can start defining the kinds of prompts you want to perform with it. Prompts are defined using the [jinja templating language](https://jinja.palletsprojects.com/en/3.1.x/templates/).

## Setup

You'll need a directory to store the prompt templates and automation scripts. Download this into the root your working directory:

```
cd ~/genai-tutorial
git clone https://github.com/odewahn/prompts
```

You will then have a directory that looks like this:

```
- prompts
  - tasks
    - extract-key-points.txt
    - ...
  - personas
    - oreilly-short.txt
  - scripts
    - summarizer.jinja
```

Here is a description of the contents for each folder:

## `tasks`

The `tasks` folder contains templates for the common tasks you want an LLM to perform. For example, things like extracting key points, writing a narrative summary, or creating a narrative summary.

For example, here is the contents of the `extract-key-points.txt` task:

```md
Here is a selection from a book called {{title}}:

---

{{block}}

---

Produce a bullet-point summary of the selection from {{title}}.
```

The task, as well as any metadata such as `{{title}}` and `{{block}}` elements is supplied to `prompter` as described below. The `{{block}}` element is a special, reserved word and is used to supply a block of text extracted from the content you downloaded from `fetcher`. In general, a chapter (much less an entire book) is far too long to fit within the context window of most models. `prompter` is a tool for helping manage this problem by giving you many ways to break contento into smaller blocks and do prompting with it.

## `personas`

The `personas` directory contains prompts related to the tone of voice and approach the LLM should use when it's performing the task. (This is sometimes also called the system prompt.) For example, you might want than LLM to sound like a helpful tutor, or perhaps a pirate.

Here is the sample of the `oreilly-short.txt` persona:

```md
Imagine you are an expert in a technical field, tasked with explaining a complex topic to a smart novice. Whether speaking or writing, your tone should be informal, helpful, and friendly, yet rigorously thorough. Emphasize clarity and engagement, ensuring that your explanation is accessible while maintaining depth. Your goal is to create a seamless experience where concepts take center stage, guiding the audience through the information with organized structure and eliminating unnecessary details. Consider the audience's potential prior knowledge and approach the explanation as if addressing an intelligent novice.
```

You supply the persona as an option to `prompter` as described below.

## `scripts`

prompter provides two ways to work with content: a REPL mode and a script mode. The section below will uses the REPL where you enter commands that are run one step at a time. However, much like a scripting language, you can also store commands in a file and then run them all at once. This enables you to scale the production of content once you've figured out how the original content should be formatted and chunked and decided on your prompts.

# Using Prompter with Fetcher content

This section describes how to use prompter with content downloaded from the O'Reilly learning platform using fetcher. The goal is to show how to use prompter to create summaries of technical content.

## Navigating to the content repo

Once prompter starts, type `pwd` to see your current location in the filesystem:

```
prompter> pwd
/Users/odewahn/genai-tutorial
```

Use `ls` to see the contents of the directory:

```
prompter> ls
total 0
drwxr-xr-x  6 odewahn  staff  192 Jun 27 10:56 9781492092384-data-mesh
drwxr-xr-x  6 odewahn  staff  192 Jun 27 10:55 prompts
```

Use `cd --dir=<direcotory>` to change into the directory you downloaded with `fetcher`:

```
prompter> cd --dir=9781492092384-data-mesh
prompter> ls
total 24
-rw-------   1 odewahn  staff   121 Jun 27 10:56 README.md
-rw-------   1 odewahn  staff   285 Jun 27 10:56 init.promptlab
-rw-r--r--   1 odewahn  staff  1500 Jun 27 10:56 metadata.yaml
drwxr-xr-x  35 odewahn  staff  1120 Jun 27 10:58 source
```

# Run the script to produce the summaries

Run the script to create the summaries using this command:

```
run --fn=../prompts/scripts/summarizer-ch01-ch02.jinja --global=metadat
a.yaml
```

This will churn for a few minutes, but it's only doing two chapters, so it won't take too long.

_NOTE_: A full book might take 15-20 minutes as prompter works now, although that time could be improved by paralellizing the requests. You can use [Caffine](https://www.caffeine-app.net/) to prevent your Mac from falling asleep while this is happenening.

Once it's complete, note the new markdown files in the root of the content directory. Also, note that you now what a file called `prompter.db` in your directory. This is a sqlite database that has all the blocks and content from the

# Create the summary in Atlas

- Create a new Atlas project at https://atlas.oreilly.com/
- Clone it locally
- Add the new file
- Configure the project
- Build

# Self-paced prompter demo

This section describes how to use prompter in more depth, and walks through many of the the commands in the main script one by one. The goal of this section is to explain the underlying concepts required to create new scripts for different types of works. For example, if you wanted to make a glossary for a book, study questions, or other types of content.

## Create a new database

Running this command will create a new database and back up the existing copy:

```
init
```

## Loading the content

Use the following command to load all the HTML files in the source directory:

```
load --fn=source/*.html
```

Here's a sample of the output:

```bash
prompter> load --fn=source/*.html
[17:03:22] Loading file source/*.html                                                                             main.py:417
    Loading file source/00000-cover-cover.html                                                             main.py:432
    Loading file source/00001-dedication01-praise-for-data-mesh.html                                       main.py:432
    Loading file source/00002-titlepage01-data-mesh.html                                                   main.py:432
    Loading file source/00003-copyright-page01-data-mesh.html                                              main.py:432
    Loading file source/00008-part01-i-what-is-data-mesh.html                                              main.py:432
    Loading file source/00009-ch01-1-data-mesh-in-a-nutshell.html                                          main.py:432
    Loading file source/00010-ch02-2-principle-of-domain-ownership.html                                    main.py:432
    ...
```

Run the `blocks` command to see blocks that were just created:

```
prompter> blocks
                                                       Current Blocks
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ block_id ┃ block_tag              ┃ parent_block_id ┃ group_id ┃ group_tag        ┃ block                   ┃ token_count ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ 1        │ 00000-cover-cover.html │ 0               │ 1        │ director-himself │ <div                    │ 7           │
│          │                        │                 │          │                  │ id="sbo-rt-content"><f… │             │
│          │                        │                 │          │                  │ data-ty                 │             │
│ 2        │ 00001-dedication01-pr… │ 1               │ 1        │ director-himself │ <div                    │ 593         │
│          │                        │                 │          │                  │ id="sbo-rt-content"><s… │             │
│          │                        │                 │          │                  │ class=                  │             │
|                      ..........                                                                                           |
│          │                        │                 │          │                  │ class=                  │             │
│ 32       │ 00031-colophon02-colo… │ 31              │ 1        │ director-himself │ <div                    │ 180         │
│          │                        │                 │          │                  │ id="sbo-rt-content"><s… │             │
│          │                        │                 │          │                  │ data-t                  │             │
└──────────┴────────────────────────┴─────────────────┴──────────┴──────────────────┴─────────────────────────┴─────────────┘

32 blocks with 131,892 tokens.
Current group id = (1, 'director-himself')

The following fields available in --where clause:
['block_id', 'block_tag', 'parent_block_id', 'group_id', 'group_tag', 'block', 'token_count']

```

Note that each block has a unique field called `block_tag` that is based off the original filename. You can use this name to refer to specific block or group of blocks.

You can view the contents of a block using the `dump` command with a `--where` clause to select the one you want to view:

```html
prompter> dump --where="block_id=32"
<div id="sbo-rt-content">
  <section
    data-type="colophon"
    epub:type="colophon"
    class="abouttheauthor"
    data-pdf-bookmark="About 
the Author"
  >
    <div class="colophon" id="idm45614675385984">
      <h1>About the Author</h1>
      <p>
        <strong>Zhamak Dehghani</strong> is a director of technology at
        Thoughtworks, focusing on distributed systems and data architecture in
        the enterprise. She’s a member of multiple technology advisory boards
        including Thoughtworks. Zhamak is an advocate for the decentralization
        of all things, including architecture, data, and ultimately power. She
        is the founder of data mesh.
      </p>
    </div>
  </section>
</div>
```

The `--where` clause can be any sqlite where clause for the columns 'block_id', 'block_tag', 'parent_block_id', 'group_id', 'group_tag', 'block', 'token_count'. When you look at the full output of the blocks command, you'll see 32 files, many of which (like a cover or index) are not things you want to send to an LLM. You could use the `--where` clause to just get the chapters:

```
blocks --where="block_tag like '%-ch%'"
```

## Creating new groups using transformations

The content downloaded from the platform contains a bunch of HTML markup that we don't want to send to the LLM. You can use the `transform` command to convert it to markdown:

```
transform --transformation=html2md
```

Rerun the blocks command just for the colophon:

```
prompter> blocks --where="block_tag like '%colo%'"
Current Blocks
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ block_id ┃ block_tag ┃ parent_block_id ┃ group_id ┃ group_tag ┃ block ┃ token_count ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ 63 │ 00030-colophon01-abou… │ 31 │ 2 │ me-wait-kind-gas │ # About the Author │ 55 │
│ │ │ │ │ │ **Zhamak Dehghani** │ │
│ 64 │ 00031-colophon02-colo… │ 32 │ 2 │ me-wait-kind-gas │ # Colophon The animal │ 175 │
│ │ │ │ │ │ on the cover of │ │
└──────────┴────────────────────────┴─────────────────┴──────────┴──────────────────┴─────────────────────────┴─────────────┘

2 blocks with 230 tokens.
Current group id = (2, 'me-wait-kind-gas')

The following fields available in --where clause:
['block_id', 'block_tag', 'parent_block_id', 'group_id', 'group_tag', 'block', 'token_count']

```

Here's the result of the conversion:

```

prompter> dump --where="block_tag like '%colophon01%'"

# About the Author

**Zhamak Dehghani** is a director of technology at Thoughtworks, focusing on distributed systems and data architecture in the
enterprise. She’s a member of multiple technology advisory boards including Thoughtworks. Zhamak is an advocate for the
decentralization of all things, including architecture, data, and ultimately power. She is the founder of data mesh.

```

A few things to note:

- the colophon now has a block_id of 63
- the current group id (shown at the end of the output of the blocks command) is now 2
- the group_tag has changed from `director-himself` to `me-wait-kind-gas`
- the HTML markup has been converted to markdown, which is a cleaner format to send to an LLM

The reason the group_id and block_id changed is that transformation in `prompter` do not update data -- it only adds new results. Each transformation creates a new group containing the corresponding blocks. The `groups` command will shows the groups different groups:

```
prompter> groups
                        Groups
┏━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ id ┃ group_tag        ┃ block_count ┃ prompt_count ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ 1  │ director-himself │ 32          │ 0            │
│ 2  │ me-wait-kind-gas │ 32          │ 0            │
└────┴──────────────────┴─────────────┴──────────────┘

2 group(s) in total
Current group_id: (2, 'me-wait-kind-gas')
```

You can provide a `--group_tag` when doing transformations to name them yourself; otherwise, `prompter` will generate a random name for you.

As a last example of transformation, this command will split the current blocks into new blocks of 2000 characters with a group tag of `chunked`:

```
transform --transformation=token-split --group_tag=chunked
```
