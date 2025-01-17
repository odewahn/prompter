# Command Reference

## Core Features

### use
**Description:** Use a new database.
- **Arguments:**
  - `db_name` (required): Database name to use.
- **Example:**
  ```
  use my_database
  ```

### load
**Description:** Load a file or files as a new group.
- **Arguments:**
  - `files` (required): List of files to load.
  - `--tag` (optional): Tag to use for the group.
- **Example:**
  ```
  load file1.txt file2.txt --tag=my_group
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
- **Example:**
  ```
  transform clean-epub --tag=cleaned --where="block_tag like 'ch%'"
  ```

### complete
**Description:** Complete a block using OpenAI.
- **Arguments:**
  - `task` (required): Filename of the task template.
  - `--tag` (optional): Tag to use for the group.
  - `--persona` (optional): Filename of the persona template.
  - `--metadata` (optional): Metadata file (default: DEFAULT_METADATA_FN).
  - `--model` (optional): Model to use (default: OPENAI_DEFAULT_MODEL).
  - `--temperature` (optional): Temperature to use (default: OPENAI_DEFAULT_TEMPERATURE).
  - `--where` (optional): Where clause for the blocks.
- **Example:**
  ```
  complete my_task.jinja --tag=my_group --model=gpt-3.5-turbo
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
  - `tag` (required): Tag to use for the group.
- **Example:**
  ```
  checkout my_group
  ```

### squash
**Description:** Squash the current group into a new group by tag.
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

### run
**Description:** Run a file.
- **Arguments:**
  - `fn` (required): File or URL to run.
- **Example:**
  ```
  run script.prompter
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
