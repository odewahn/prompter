# Command Reference

## Core Features

### use

**Description:** Use a new database.

- **Arguments:**
  - `db_name` (required): Database name to use.
- **Example:**
  ```
  use my_database.db
  ```

### load

**Description:** Load a file or files as a new group.

- **Arguments:**
  - `files` (required): List of files or URLs to load.
  - `--tag` (optional): Tag to use for the group.
- **Example:**
  ```
  load file1.txt *.md http://example.com --tag=my_group
  ```

### transform

**Description:** Transform a block using specified transformations.

- **Arguments:**
  - `transformation` (required): Transformations to apply. Available transformations are:
    - `token-split`: Breaks text into overlapping chunks of 1000 tokens overlapping by 10%.
    - `clean-epub`: Simplifies the HTML of an EPUB.
    - `html-h1-split`: Breaks HTML into blocks based on H1 tags.
    - `html-h2-split`: Breaks HTML into blocks based on H1 and H2 tags.
    - `html-to-md`: Converts HTML to Markdown.
    - `html-to-txt`: Converts HTML to plain text.
    - `new-line-split`: Splits text into blocks based on new lines.
    - `sentence-split`: Splits text into blocks based on sentences.
  - `--tag` (optional): Tag to use for the group.
  - `--where` (optional): Where clause for the blocks.
  - `--n` (optional): Number of tokens to split (default: 1000).
  - `--overlap` (optional): Overlap percentage (as an integer) for token-split (default: 10).
- **Example:**
  ```
  transform clean-epub --tag=cleaned --where="block_tag like 'ch%'"
  ```

### complete

**Description:** Complete a block using OpenAI.

- **Arguments:**
  - `task` (required): Filename or URL of the task template.
  - `--persona` (optional): Filename or URL of the persona template.
  - `--metadata` (optional): Metadata file (default: DEFAULT_METADATA_FN).
  - `--tag` (optional): Tag to use for the group.
  - `--model` (optional): Model to use (default: OPENAI_DEFAULT_MODEL).
  - `--temperature` (optional): Temperature to use (default: OPENAI_DEFAULT_TEMPERATURE).
  - `--where` (optional): Where clause for the blocks.
- **Example:**
  ```
  complete summarize.jinja --tag=summary --model=gpt-4o --temperature=0.3
  ```

### run

**Description:** Run a file.

- **Arguments:**
  - `fn` (required): File or URL to run.
- **Example:**
  ```
  run script.prompter
  ```

## Data Management

### blocks

**Description:** List all blocks.

- **Arguments:**
  - `--where` (optional): Where clause for the blocks.
- **Example:**
  ```
  blocks --where="block_tag like 'ch%'"
  ```

### groups

**Description:** List all groups.

- **Arguments:**
  - `--where` (optional): Where clause for the group.
- **Example:**
  ```
  groups --where="group_tag like 'my_group%'"
  ```

### checkout

**Description:** Checkout a group.

- **Arguments:**
  - `tag` (required): Tag to checkout. This can be:
    - _tag_: the name of the group to checkout
    - `latest`: checkout the latest group
    - `first`: checkout the first group
    - `next`: checkout the next group
    - `previous`: checkout the previous group
- **Example:**
  ```
  checkout my_group
  ```

### squash

**Description:** Squash the current group into a new group by tag. Use this to combine blocks into a single block.

- **Arguments:**
  - `--delimiter` (optional): Delimiter to use (default: "\n").
  - `--tag` (optional): Tag for the new group.
- **Example:**
  ```
  squash --delimiter="\n\n" --tag=squashed_group
  ```

### write

**Description:** Write the current group to a file.

- **Arguments:**
  - `--fn` (optional): Filename pattern (jinja2) to write to (default: "{{block_tag}}").
  - `--where` (optional): Where clause for the blocks.
- **Examples:**
  Write each block to a file named after its tag:
  ```
  write --fn="output/{{block_tag}}.txt"
  ```

## Environment Management

### set

**Description:** Set an environment variable.

- **Arguments:**
  - `key` (required): Key to set.
  - `value` (required): Value to set.
- **Example:**
  ```
  set SOURCE https://example.com
  ```

### unset

**Description:** Remove an environment variable.

- **Arguments:**
  - `key` (required): Key to remove.
- **Example:**
  ```
  unset SOURCE
  ```

#### Usage Notes

Environments set in the bash environment that start with "PROMPTER\_" will be available in the prompter environment. (Note that the "PROMPTER\_" prefix will be stripped off.) For example, an environment variable created with `export PROMPTER_ENV=dev` automantically becomes available in the prompter environment as `ENV=dev`. You can use this freature to pass environment variables into prompter when it starts.

"env": handle_env_command,
"set": handle_set_command,
"unset": handle_unset_command,

For example, you might use environment variables to set a source URL for the location of your task and persona prompts. When the script is run, the environment variables are replaced with their values. For example:

```
set SOURCE https://example.com
```

And then you can do something like this:

```
complete {{SOURCE}}/summarize.md --persona={{SOURCE}}/persona.md
```

## Utility Functions

### speak

**Description:** Convert the current block to audio files.

- **Arguments:**
  - `--fn` (optional): Filename pattern (jinja2) to write to (default: "{{block_tag.split('.') | first}}-{{ '%04d' % position}}.mp3").
  - `--where` (optional): Where clause for the blocks.
  - `--voice` (optional): Voice to use (default: "alloy").
  - `--preview` (optional): Preview the filenames.
- **Example:**
  ```
  speak --fn="audio/{{block_tag}}.mp3" --voice=alloy
  ```

## Misc

### version

**Description:** Print the version of the application.

- **Example:**
  ```
  version
  ```

### exit

**Description:** Exit the REPL (Read-Eval-Print Loop).

- **Example:**
  ```
  exit
  ```
