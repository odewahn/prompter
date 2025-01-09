- Change "browse" to "workshop" to rename the web editor

# Documentation organization

## Data management

"use": handle_use_command,
"load": handle_load_command,
"blocks": handle_blocks_command,
"groups": handle_groups_command,
"checkout": handle_set_group,

"select": this doesn't exist yet, but maybe it should replace all where clauses
"squash" -- should this be a subset of transform?

## Environment management

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

## Scripting with `run`

"run": handle_run_command,

Allows you to run a sequence of commands in a file. Use this to automate tasks. A script file is processed in two passes. The first pass is a Jinja template rendering pass. The second pass is a command execution pass. This allows you to use Jinja templating in your script files.

## The rendering pass

In the first pass (the rendering pass), you can use any environment variables that are set in the prompter environment as part of the command template. For example, you might have a script file that looks like this:

```
load {{SOURCE}}/cat-essay.txt
transform new-line-split
```

Assuming you have set a `SOURCE` environment variable, the `{{SOURCE}}` will be replaced with the value of the `SOURCE` environment variable during the rendering pass. You can see the rendered script by using the `--preview` option.

Use `{%raw%}...{%endraw%}` to prevent Jinja from processing block variables during the first pass of the template rendering. This is useful when you want to use Jinja templating in a block that will be processed later. For example:

```
write --fn="{{DEST}}/test-{%raw%}{{block_tag.split('.')[0]}}{%endraw%}-{{position}}.md"
```

## The command pass

In the render phase, each individual command is executed. You can use either environment variables or block-level variables (for example, the `block_tag` or `position`).

## Core features

"transform": handle_transform_command,
"complete": handle_complete_command,
"write": handle_write_command

(Be sure the use `{%raw%}...{%endraw%}` to prevent Jinja from processing block variables if you're using a jinja template in the `--fn` argument.)

## Navigating filesystem

"cd": handle_cd_command,
"ls": handle_ls_command,
"pwd": handle_pwd_command,

## Utility functions

"speak": handle_speak_command,
"browse" -- rename this to workshop?
"history": handle_history_command,

## Misc

"exit": handle_exit_command,
"version": handle_version_command,
"help": handle_help_command,
