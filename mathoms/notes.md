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

## Scripting

"run": handle_run_command,
"history": handle_history_command,

## Core features

"transform": handle_transform_command,
"complete": handle_complete_command,
"write": handle_write_command,

## Navigating filesystem

"cd": handle_cd_command,
"ls": handle_ls_command,

## Utility functions

"speak": handle_speak_command,
"browse" -- rename this to workshop?

## Misc

"exit": handle_exit_command,
"version": handle_version_command,
"help": handle_help_command,
