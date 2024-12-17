# Prompter

Prompter is a utility designed to make it easy to create scripts and managing templated prompts with OpenAI. It let's you:

- Load files (currently, text file or EPUB) into a SQLite database
- Transform the files into blocks of content
  - Tokenize the content
  - Clean up EPUB files
  - Split the content based on HTML tags
  - Convert HTML to Markdown or plain text
  - Split the content based on new lines or sentences
- Apply those blocks of content to a template and complete with an LLM
- Write the completed blocks to a file
- Convert the blocks to audio files
- View the blocks in a web browser
- Create scripts to automate the process so that you can easily apply the same transformations and completions to different source files

## Usage

The following commands are available:

### use

**Description:** Use a new database.

**Arguments:**

- `db_name` (required): Database name to use.

**Example:**

```
use my_database
```

### load

**Description:** Load a file or files as a new group.

**Arguments:**

- `files` (required): List of files to load.
- `--tag` (optional): Tag to use for the group.

**Example:**

```
load file1.txt file2.txt --tag=my_group
```

### transform

**Description:** Transform a block using specified transformations.

**Arguments:**

- `transformation` (required): Transformations to apply. Available transformations are:
  - `token-split`: Breaks text into overlapping chunks of 1000 tokens overlapping by 10%(default, can be changed with `--n` and `--overlap`, where `overlap` is a integer percentage).
  - `clean-epub`: Simplifies the HTML of an EPUB.
  - `html-h1-split`: Breaks HTML into blocks based on H1 tags.
  - `html-h2-split`: Breaks HTML into blocks based on H1 and H2 tags.
  - `html-to-md`: Converts HTML to Markdown.
  - `html-to-txt`: Converts HTML to plain text.
  - `new-line-split`: Splits text into blocks based on new lines.
  - `sentence-split`: Splits text into blocks based on sentences.
- `--tag` (optional): Tag to use for the group.
- `--where` (optional): Where clause for the blocks.
- `--N` (optional): Number of tokens to split (default: 1000).

**Example:**

```
transform clean-epub --tag=cleaned --where="block_tag like 'ch%'"
```

### complete

**Description:** Complete a block using OpenAI.

**Arguments:**

- `task` (required): Filename of the task template.
- `--tag` (optional): Tag to use for the group.
- `--persona` (optional): Filename of the persona template.
- `--metadata` (optional): Metadata file (default: DEFAULT_METADATA_FN).
- `--model` (optional): Model to use (default: OPENAI_DEFAULT_MODEL).
- `--temperature` (optional): Temperature to use (default: OPENAI_DEFAULT_TEMPERATURE).
- `--where` (optional): Where clause for the blocks.

**Example:**

```
complete my_task.jinja --tag=my_group --model=gpt-3.5-turbo
```

### groups

**Description:** List all groups.

**Arguments:**

- `--where` (optional): Where clause for the group.

**Example:**

```
groups --where="group_tag like 'my_group%'"
```

### checkout

**Description:** Checkout a group.

**Arguments:**

- `tag` (required): Tag to use for the group.

**Example:**

```
checkout my_group
```

### blocks

**Description:** List all blocks.

**Arguments:**

- `--where` (optional): Where clause for the blocks.

**Example:**

```
blocks --where="block_tag like 'ch%'"
```

### squash

**Description:** Squash the current group into a new group by tag.

**Arguments:**

- `--delimiter` (optional): Delimiter to use (default: "\n").
- `--tag` (optional): Tag for the new group.

**Example:**

```
squash --delimiter="\n\n" --tag=squashed_group
```

### write

**Description:** Write the current group to a file. You can use a Jinja template as the filename and use the information in the blocks to customize the filename more.

**Arguments:**

- `--fn` (optional): Filename pattern (jinja2) to write to (default: "{{block_tag}}"). You can use block attributes like `block_tag`, `position`, or any other metadata available in the block to customize the filename.
- `--where` (optional): Where clause for the blocks.

**Examples:**

Write each block to a file named after its tag:

```
write --fn="output/{{block_tag}}.txt"
```

Include the block's position in the filename:

```
write --fn="output/{{block_tag}}-{{position}}.txt"
```

Use a custom prefix and include the creation date:

```
write --fn="output/custom-prefix-{{created_at.strftime('%Y%m%d')}}-{{block_tag}}.txt"
```

### speak

**Description:** Convert the current block to audio files.

**Arguments:**

- `--fn` (optional): Filename pattern (jinja2) to write to (default: "{{block_tag.split('.') | first}}-{{ '%04d' % position}}.mp3").
- `--where` (optional): Where clause for the blocks.
- `--voice` (optional): Voice to use (default: "alloy").
- `--preview` (optional): Preview the filenames.

**Example:**

```
speak --fn="audio/{{block_tag}}.mp3" --voice=alloy
```

### run

**Description:** Run a file.

**Arguments:**

- `fn` (required): File or URL to run.

**Example:**

```
run script.prompter
```

### web

**Description:** Open a web browser to view data.

**Example:**

```
web
```

### cd

**Description:** Change the working directory.

**Arguments:**

- `path` (required): Path to change to.

**Example:**

```
cd /path/to/directory
```

### ls

**Description:** List directories in the current directory.

**Example:**

```
ls
```

### help

**Description:** Get help.

**Example:**

```
help
```

### version

**Description:** Print the version of the application.

**Example:**

```
version
```

### exit

**Description:** Exit the REPL (Read-Eval-Print Loop).

**Example:**

```
exit
```
