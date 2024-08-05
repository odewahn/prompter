from argparse import ArgumentParser, BooleanOptionalAction
from rich.console import Console
from rich import print
from rich.table import Table
from ebooklib import epub
from ebooklib import ITEM_DOCUMENT as ebooklib_ITEM_DOCUMENT
from bs4 import BeautifulSoup
import sqlite3
import time
import shutil
import os
from jinja2 import Template
import sys
import hashlib
import logging
import glob
from transformations import *
from completions_common import *
import os
from faker import Faker
import yaml
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from shlex import split as shlex_split
from art import text2art
from sys import exit
from os import system, chdir
import traceback
import json
import asyncio


console = Console()
fake = Faker()
log = logging.getLogger("rich")
args = None

VERSION = "0.3.0"


ACTIONS = [
    "auth",
    "init",
    "load",
    "transform",
    "filter",
    "groups",
    "blocks",
    "dump",
    "prompt",
    "prompts",
    "prompt-log",
    "transfer-prompts",
    "set-group",
    "version",
    "set-api-key",
    "squash",
    "ls",
    "cd",
    "mkdir",
    "pwd",
    "models",
    "run",
    "exit",
    "stats",
]
TRANSFORMATIONS = [
    "token-split",
    "clean-epub",
    "html-h1-split",
    "html-h2-split",
    "html2md",
    "html2txt",
    "new-line-split",
    "sentence-split",
]


# *****************************************************************************************
# Utiltiy functions
# *****************************************************************************************
# If the db exists; if not, print error and exit.  Otherwise sqlite silently create a new file.
def check_db(fn):
    if not os.path.isfile(fn):
        console.log(f"Database file {fn} does not exist.")
        console.log("Check the filename or run init to create a new database.")
        raise Exception(f"Database file {fn} does not exist.")


# Loads a file eirher from the current directory or from the directory
# in which the script was run, which is needed when pyinstaller loads external files
def load_file(fn, config=False):
    if config:
        # find filepath for where the script is actually running
        script_path = os.path.dirname(os.path.realpath(__file__))
        # Join the filename with the script path
        fn = os.path.join(script_path, fn)
    # Check if the file exists
    if not os.path.isfile(fn):
        raise Exception(f"File does not exist:{fn}")
    # Load and return the file
    with open(fn, "r") as f:
        data = f.read()
    return data


def load_system_file(fn):
    return load_file(fn, True)


def load_user_file(fn):
    return load_file(os.path.expanduser(fn), False)


def hash(txt):
    return str(hashlib.sha256(txt.encode("utf-8")).hexdigest())


def get_delimiter():
    d = args.delimiter
    d = d.replace(r"\n", "\n")
    return d


# Convert a * wildcard to a % for sqlite3
def convert_wildcard(s):
    return s.replace("*", "%")


def generate_slug(length):
    return fake.slug()


# Used to get the where clause.  I'll add something about sql injection here later
def apply_sql_clauses(sql, where=None, order=None):
    where_final = where if where is not None else args.where
    order_final = order if order is not None else args.order
    if where_final is not None:
        sql += " where " + where_final
    if order_final is not None:
        sql += " order by " + order_final
    return sql


# This function takes an array of dictionaries and then a set of transformations expressed as lambda functions
# It will iterate through the array and apply the transformation if they have matching key names.  For example:
#
# transform_by_key([{"text": "hello"}, {"text": "world"}], {"text": lambda x: x.upper()})
# will return [{"text": "HELLO"}, {"text": "WORLD"}]
#
def transform_by_key(data=[], transformations={}):
    transformed_data = []
    for d in data:
        row = {**d}
        for key, transformation in transformations.items():
            if key in row.keys():
                row[key] = transformation(row[key])
        transformed_data.append(row)
    return transformed_data


def fetch_from_db(sql, tuple):
    try:
        conn = sqlite3.connect(args.db)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(sql, tuple)
        results = c.fetchall()
        # get column names and store in a list
        column_names = [description[0] for description in c.description]
        # Unpack the sqlite row objects into a list of dictionaries
        # See this great article on this next line
        # https://nickgeorge.net/programming/python-sqlite3-extract-to-dictionary/
        unpacked = [{k: item[k] for k in item.keys()} for item in results]
        conn.close()
        return column_names, unpacked
    except Exception as e:
        console.log("[red]An error occurred on this request[/red]")
        console.log(" ".join(sys.argv))
        console.log("SQL used in this request is:\n\n", sql)
        console.log(f"\nThe following error occurred:\n\n[red]{e}[/red]\n")
        raise Exception("An error occurred on this request")


def print_results(title, column_names, results):
    table = Table(title=title, header_style="bold magenta")
    for cn in column_names:
        table.add_column(cn)
    for row in results:
        table.add_row(*[str(row[cn]) for cn in column_names])
    console.print(table)


# Take a command file used in the "run" option and render it using the metadata
def render_command_file():
    console.log("Rendering command file", args.fn)
    instructions = load_user_file(args.fn)
    metadata = {}
    if args.globals is not None:
        metadata = read_metadata(args.globals)
    # Render the template
    template = Template(instructions)
    instructions = template.render(**metadata)
    out = []
    for instruction in instructions.split("\n"):
        if len(instruction) > 0:
            out.append(instruction.strip())
    return out


# *****************************************************************************************
#  Metadata
# *****************************************************************************************


def read_metadata(fn):
    txt = load_user_file(fn)
    # parse the yml file into a dictionary
    metadata = yaml.safe_load(txt)
    return metadata


# Takes prompts and converts them to metadata under the supplied key
def action_transfer_prompts_to_metadata():
    header, results = fetch_prompts()
    try:
        sql = load_system_file("sql/create_metadata.sql")
        conn = sqlite3.connect(args.db)
        conn.isolation_level = None
        c = conn.cursor()
        c.execute("BEGIN")
        for r in results:
            c.execute(sql, (r["block_id"], args.metadata_key, r["response"]))
        conn.commit()
    except Exception as e:
        console.log("Unable to process request:", e)
        conn.rollback()
    finally:
        conn.close()


# *****************************************************************************************
#  Groups
# *****************************************************************************************


def create_group(c, tag=None):
    sql = load_system_file("sql/create_group.sql")
    tag = tag if tag is not None else generate_slug(3)
    arguments = " ".join(sys.argv)
    c.execute(sql, (arguments, tag))
    group_id = c.lastrowid
    return group_id


def get_current_group():
    headers, results = fetch_from_db(
        "select cg.id, g.tag group_tag from current_group cg join groups g on g.id = cg.id",
        (),
    )
    try:
        group_id = results[0]["id"]
        group_tag = results[0]["group_tag"]
    except:
        group_id = 0
        group_tag = ""
    return int(group_id), group_tag


def fetch_groups():
    sql = load_system_file("sql/fetch_groups.sql")
    headers, results = fetch_from_db(sql, ())
    return results


def set_group(c, group_id):
    c.execute("UPDATE current_group set id = ?", (group_id,))
    return group_id


def get_group_id_by_tag():
    headers, results = fetch_from_db(
        "select id from groups where tag = ?", (args.group_tag,)
    )
    try:
        return results[0]["id"]
    except:
        raise Exception("Group not found")


# *****************************************************************************************
#  Blocks
# *****************************************************************************************


def create_block(c, group_id, block, tag, parent_id):
    sql = load_system_file("sql/create_block.sql")
    token_count = len(block.split(" "))
    c.execute(sql, (group_id, block, tag, parent_id, token_count))
    block_id = c.lastrowid
    return block_id


# fetch blocks and apply where clause if it exists
# TODO: something arouns sql injection here. there is probbaly a python library
def fetch_blocks():
    sql = load_system_file("sql/v_current_blocks.sql")
    sql = apply_sql_clauses(sql)
    headers, results = fetch_from_db(sql, ())
    return headers, results


def insert_blocks_in_new_group(blocks):
    # If the load fails then we want to rollback the entire transaction
    try:
        conn = sqlite3.connect(args.db)
        conn.isolation_level = None
        c = conn.cursor()
        c.execute("BEGIN")
        group_id = create_group(c, args.group_tag)
        for b in blocks:
            create_block(c, group_id, b["block"], b["tag"], b["parent_id"])
        set_group(c, group_id)
        conn.commit()
    except Exception as e:
        console.log("Unable to process request:", e)
        conn.rollback()
    finally:
        conn.close()


# *****************************************************************************************
#  Prompts
# *****************************************************************************************


def create_prompt_response(
    prompt_log_id, block_id, prompt_text, response_txt, elapsed_time_in_seconds
):
    sql = load_system_file("sql/create_prompt_response.sql")
    conn = sqlite3.connect(args.db)
    c = conn.cursor()
    c.execute(
        sql,
        (
            prompt_log_id,
            block_id,
            hash(prompt_text),
            response_txt,
            elapsed_time_in_seconds,
        ),
    )
    # Unlike other group, this should alsways be committed directly
    conn.commit()
    conn.close()
    prompt_response_id = c.lastrowid
    return prompt_response_id


def create_prompt_log(prompt_fn, prompt):
    sql = load_system_file("sql/create_prompt_log.sql")
    conn = sqlite3.connect(args.db)
    c = conn.cursor()
    arguments = " ".join(sys.argv)
    tag = args.prompt_tag if args.prompt_tag is not None else generate_slug(3)
    c.execute(sql, (prompt_fn, prompt, arguments, tag))
    conn.commit()
    conn.close()
    prompt_log_id = c.lastrowid
    return prompt_log_id, tag


def response_already_exists(prompt_text):
    headers, result = fetch_from_db(
        "select * from prompt_responses where prompt_hash like ?", (hash(prompt_text),)
    )
    return len(result) > 0


def action_stats():
    sql = load_system_file("sql/prompt_stats.sql")
    headers, results = fetch_from_db(sql, ())
    results = transform_by_key(
        results,
        {
            "approximate_tokens_processed": lambda x: "{:,}".format(x),
            "elapsed_seconds": lambda x: f"{x:,.0f}",
        },
    )
    print_results("Prompt Stats", headers, results)


# *****************************************************************************************
# Action groups
# *****************************************************************************************


# Initialize the database by reading in the schema and creating the database
def action_init():
    # Back up the existing database
    try:
        now = time.strftime("%Y%m%d-%H%M%S")
        # copy the db to a backup file
        backup_fn = args.db + "." + now + ".bak"
        console.log("Backing up database to", backup_fn)
        shutil.copyfile(args.db, backup_fn)
        os.remove(args.db)
    except:
        pass
    # Initialize the new database
    conn = sqlite3.connect(args.db)
    c = conn.cursor()
    sql = load_system_file("sql/schema.sql")
    c.executescript(sql)
    conn.commit()
    conn.close()


# Loads a file into the database
def action_load():
    console.log("Loading file", args.fn)
    data = []
    # If the load fails then we want to rollback the entire transaction
    if args.fn.endswith(".epub"):
        book = epub.read_epub(args.fn, {"ignore_ncx": True})
        idx = 0
        for item in book.get_items():
            if item.get_type() == ebooklib_ITEM_DOCUMENT:
                html = item.get_content().decode("utf-8")
                data.append({"block": html, "tag": item.get_name(), "parent_id": 0})
                idx += 1
    else:
        files = sorted(glob.glob(os.path.expanduser(args.fn)))
        idx = 0
        for f in files:
            console.log("Loading file", f)
            txt = load_user_file(f)
            data.append({"block": txt, "tag": os.path.basename(f), "parent_id": idx})
            idx += 1
    insert_blocks_in_new_group(data)


def action_transfer_prompts_to_blocks():
    headers, results = fetch_prompts()
    print("Found headers", headers)
    data = []
    for p in results:
        data.append(
            {
                "block": p["response"],
                "tag": p["block_tag"],
                "parent_id": p["block_parent_id"],
            }
        )
    insert_blocks_in_new_group(data)


def action_squash():
    # See https://stackoverflow.com/questions/3926162/group-different-rows-in-one-by-combining-strings
    sql = load_system_file("sql/v_squash_current_prompts.sql")
    headers, results = fetch_from_db(sql, (get_delimiter(),))
    insert_blocks_in_new_group(results)


def action_transform(transformation):
    transformation = transformation.lower().strip()
    # Fetch the block or blocks to use
    headers, blocks = fetch_blocks()
    data = []
    for b in blocks:
        console.log("Processing block", b["block_tag"])
        # Apply the transformation to the block
        match transformation:
            case "token-split":
                result = transformation_token_split(b["block"])
            case "clean-epub":
                result = transformation_clean_epub(b["block"])
            case "html-h1-split":
                result = transformation_html_heading_split(b["block"], ["h1"])
            case "html-h2-split":
                result = transformation_html_heading_split(b["block"], ["h1", "h2"])
            case "html2md":
                result = transformation_html2md(b["block"])
            case "html2txt":
                result = transformation_html2txt(b["block"])
            case "new-line-split":
                result = transformation_newline_split(b["block"])
            case "sentence-split":
                result = transformation_sentence_split(b["block"])
            case _:
                raise Exception(f"Unknown transformation {args.transformation}")
        # If the result is a list, then create a block for each element
        if type(result) is list:
            for r in result:
                data.append(
                    {"block": r, "tag": b["block_tag"], "parent_id": b["block_id"]}
                )
        elif type(result) is str:
            data.append(
                {"block": result, "tag": b["block_tag"], "parent_id": b["block_id"]}
            )
        else:
            # Raise an error
            raise Exception(f"Result is not a list or string: {type(result)}")
    insert_blocks_in_new_group(data)


async def action_prompt():
    task_prompt = load_user_file(args.task)
    persona_prompt = load_user_file(args.persona) if args.persona is not None else ""
    metadata = {}
    if args.globals is not None:
        metadata = read_metadata(args.globals)
    template = Template(task_prompt)
    headers, blocks = fetch_blocks()
    # Load the tasks to be processed into a list
    tasks = []
    for b in blocks:
        prompt_text = template.render(block=b["block"], **metadata)
        if not response_already_exists(prompt_text):
            tasks.append({"block_id": b["block_id"], "prompt_text": prompt_text})
    # Call the completion service with the tasks using asyncio
    print(f"Processing {len(tasks)} blocks")
    start = time.time()
    results = await complete(args, tasks, persona_prompt)
    end = time.time()
    # Write results to the database
    prompt_log_id, prompt_tag = create_prompt_log(args.task, task_prompt)
    for r in results:
        # Save the response to the database
        create_prompt_response(
            prompt_log_id,
            r["block_id"],
            r["prompt_text"],
            r["prompt_response"],
            end - start,
        )
    console.log(
        f"\nPrompt response saved with id {prompt_log_id} and prompt_tag {prompt_tag}"
    )


def OLD_action_prompt():
    task_prompt = load_user_file(args.task)
    persona_prompt = load_user_file(args.persona) if args.persona is not None else ""
    metadata = {}
    if args.globals is not None:
        metadata = read_metadata(args.globals)
    template = Template(task_prompt)
    headers, blocks = fetch_blocks()
    # Apply the template to each block
    prompt_log_id, prompt_tag = create_prompt_log(args.task, task_prompt)
    idx = 1
    for b in blocks:
        prompt_text = template.render(block=b["block"], **metadata)
        # Check if we're only previwewing the prompt.  If so, print it andbreak the loop
        if args.preview:
            console.log(
                f"({idx}/{len(blocks)}) Previewing block",
                b["block_id"],
                b["block_tag"],
                b["block"][:40].replace("\n", " "),
            )
            print("\n\n", prompt_text, "\n\n")
            break
        if response_already_exists(prompt_text):
            console.log(
                f"({idx}/{len(blocks)}) Prompt already exists for",
                b["block_id"],
                b["block_tag"],
                b["block"][:40].replace("\n", " "),
            )
            idx += 1
            continue
        console.log(
            f"({idx}/{len(blocks)}) Prompting block",
            b["block_id"],
            b["block_tag"],
            b["block"][:40].replace("\n", " "),
        )
        start = time.time()
        response = "TBD"
        if args.fake:
            response_txt = fake.text(500)
        else:
            response_txt = complete(args, prompt_text, persona_prompt)
        idx += 1
        end = time.time()
        # Save the response to the database
        create_prompt_response(
            prompt_log_id, b["block_id"], prompt_text, response_txt, end - start
        )
        console.log(
            "Elapsed time", end - start, " -> ", response_txt[:40].replace("\n", " ")
        )
    console.log(
        f"\nPrompt response saved with id {prompt_log_id} and prompt_tag {prompt_tag}"
    )


def action_filter():
    console.log("Filtering blocks")
    # Fetch the block or blocks to use
    headers, blocks = fetch_blocks()
    # Open a new connection
    data = []
    for b in blocks:
        console.log("Processing block", b["block_tag"])
        data.append(
            {
                "block": b["block"],
                "tag": b["block_tag"],
                "parent_id": b["parent_block_id"],
            }
        )
    insert_blocks_in_new_group(data)


def fetch_prompts():
    sql = load_system_file("sql/v_current_prompts.sql")
    sql = apply_sql_clauses(sql)
    return fetch_from_db(sql, ())


# *****************************************************************************************
# Reporting functions -- these mostly just fetch data from the database and print it
# *****************************************************************************************
def action_blocks():
    columns, results = fetch_blocks()
    # add token count in the block column to the results

    # use lise comprehension to sum up the results["token_count"] to get the total tokens
    total_tokens = sum([r["token_count"] for r in results])

    # Transform the results to make them more readable
    results = transform_by_key(
        results,
        {
            "block": lambda x: x[:40].replace("\n", " "),
            "token_count": lambda x: "{:,}".format(x),
        },
    )
    print_results("Current Blocks", columns, results)
    console.print(f"\n{len(results)} blocks with {'{:,}'.format(total_tokens)} tokens.")
    console.print(f"Current group id = {get_current_group()}\n")
    console.print("The following fields available in --where clause:", columns)


def action_groups():
    sql = load_system_file("sql/fetch_groups.sql")
    headers, results = fetch_from_db(sql, ())
    print_results("Groups", headers, results)
    console.print(f"\n{len(results)} group(s) in total")
    console.print(f"Current group_id: {get_current_group()}\n")


def action_prompt_log():
    sql = load_system_file("sql/fetch_prompt_log.sql")
    sql = apply_sql_clauses(sql)
    headers, results = fetch_from_db(sql, ())
    results = sorted(results, key=lambda d: d[headers[0]])
    print_results("Prompt Logs", headers, results)


def action_prompts():
    sql = load_system_file("sql/v_current_prompts.sql")
    sql = apply_sql_clauses(sql)
    columns, results = fetch_from_db(sql, ())
    # Sum up the elapsed_time_in_seconds key
    total_time = sum([r["elapsed_time_in_seconds"] for r in results])
    results = transform_by_key(
        results,
        {
            "response": lambda x: x[:40].replace("\n", " "),
            "elapsed_time_in_seconds": lambda x: f"{x:.2f}",
        },
    )
    print_results("Prompts", columns, results)
    console.print(f"\n{len(results)} prompts in total")
    console.print(f"Total time: {total_time:.2f} seconds")
    console.print("The following fields available in --where clause:", columns)


def action_dump_blocks():
    headers, blocks = fetch_blocks()
    # Pull out the block element into it's own list
    if args.dir is None:
        out = [b["block"] for b in blocks]
        console.print(get_delimiter().join(out))
    else:
        for idx, b in enumerate(blocks):
            fn = f"{os.path.expanduser(args.dir)}/{b['block_tag']}.{idx:05d}.{args.extension}"
            with open(fn, "w") as f:
                f.write(b["block"])
                console.log("Wrote block to", fn)


def action_dump_prompts():
    headers, prompts = fetch_prompts()
    # Pull out the block element into it's own list
    out = [p["response"] for p in prompts]
    console.print(get_delimiter().join(out))


# *****************************************************************************************
# Define commandline arguments and flags
# *****************************************************************************************
def define_arguments(argString=None):

    parser = ArgumentParser(
        description="Mangage prommpts across long blocks of text", exit_on_error=False
    )
    parser.add_argument(
        "action",
        choices=ACTIONS,
        help="The action to perform ",
    )

    # Universal arguments
    parser.add_argument(
        "--db", help="The database file", required=False, default="prompter.db"
    )
    # Arguments related to loading files
    parser.add_argument("--fn", help="Filename", required=False)
    # Arguments related to naming or fetching blocks, prompts, etc.
    parser.add_argument("--group_tag", help="Tag to filter on", required=False)
    parser.add_argument("--prompt_tag", help="Tag to filter on", required=False)
    parser.add_argument("--where", help="SQLITE where clause", required=False)
    parser.add_argument("--order", help="SQLITE order by clause", required=False)
    # Arguments related to prompting
    parser.add_argument("--prompt", help="Prompt to use", required=False)
    parser.add_argument("--task", help="Filenaame of task template", required=False)
    parser.add_argument(
        "--persona", help="Filename of persona template", required=False
    )
    parser.add_argument(
        "--model", help="Model to use", required=False, default="gpt-4o"
    )
    parser.add_argument(
        "--provider", help="LLM service provider", required=False, default="openai"
    )
    parser.add_argument(
        "--fake",
        help="Generate fake prompt response data",
        required=False,
        default=False,
        action=BooleanOptionalAction,
    )
    parser.add_argument(
        "--preview",
        help="Preview the command",
        required=False,
        default=False,
        action=BooleanOptionalAction,
    )
    # Arguments related to transformation operations
    parser.add_argument(
        "--transformation",
        help=f"Transformation to use ({','.join(TRANSFORMATIONS)})",
        required=False,
    )
    # Arguments related to tranferring data from prompts to metadata or blocks
    parser.add_argument(
        "--to",
        help="Where to transfer prompts",
        choices=["metadata", "blocks"],
        required=False,
        default="blocks",
    )
    parser.add_argument(
        "--source",
        help="Source to dump from",
        choices=["blocks", "prompts"],
        required=False,
        default="blocks",
    )
    # Arguments related to metadata
    parser.add_argument(
        "--globals", help="Name of the file with global metadata", required=False
    )
    parser.add_argument(
        "--metadata_key",
        help="Name of metadata key; this will match the name in a prompt template",
        required=False,
    )
    # Arguments related to dumping data
    parser.add_argument(
        "--delimiter",
        help="Delimiter to use when dumping prompts",
        required=False,
        default="\n\n",
    )
    parser.add_argument(
        "--extension",
        help="Extension to use when saving dumped data",
        required=False,
        default="md",
    )
    # arguments related to files and the current directory
    parser.add_argument("--dir", help="Directory name", required=False)

    if argString:
        return parser.parse_args(shlex_split(argString))
    else:
        return parser.parse_args()


# *****************************************************************************************


async def process_command():
    if args.action == "init":
        action_init()
        return

    if args.action == "load":
        check_db(args.db)
        if args.fn is None:
            raise Exception("You must provide a --fn argument for the file to load")
        action_load()
        return

    if args.action == "auth":
        action_set_api_key()
        return

    if args.action == "transform":
        check_db(args.db)
        if args.transformation is None:
            raise Exception("You must provide a --transformation argument to use")
        transformations = args.transformation.split(",")
        if len(transformations) > 1 and args.group_tag is not None:
            raise Exception("You cannot use --group_tag with multiple transformations")
        for t in transformations:
            console.log("Applying transformation", t)
            action_transform(t)
        return

    if args.action == "blocks":
        check_db(args.db)
        action_blocks()
        return

    if args.action == "groups":
        check_db(args.db)
        action_groups()
        return

    if args.action == "dump":
        check_db(args.db)
        if args.source is None:
            raise Exception("You must provide a --source argument for the source")
        if args.source == "blocks":
            action_dump_blocks()
        elif args.source == "prompts":
            action_dump_prompts()
        return

    if args.action == "prompt":
        check_db(args.db)
        if args.task is None:
            raise Exception("You must provide a --task argument for the prompt")
        await action_prompt()
        return

    if args.action == "set-group":
        check_db(args.db)
        if args.group_tag is None:
            raise Exception("You must provide a --group_tag argument for the group")
        group_id = get_group_id_by_tag()
        conn = sqlite3.connect(args.db)
        c = conn.cursor()
        set_group(c, group_id)
        conn.commit()
        conn.close()
        console.log(f"Group set to {(group_id, args.group_tag)}")

    if args.action == "prompts":
        check_db(args.db)
        action_prompts()
        return

    if args.action == "prompt-log":
        check_db(args.db)
        action_prompt_log()
        return

    if args.action == "version":
        console.log("Version", VERSION)
        return

    if args.action == "set-api-key":
        action_set_api_key()
        return

    if args.action == "transfer-prompts":
        check_db(args.db)
        if args.to == "metadata" and args.metadata_key is None:
            raise Exception("You must provide a --metadata_key")
        if args.to == "metadata":
            action_transfer_prompts_to_metadata()
        elif args.to == "blocks":
            action_transfer_prompts_to_blocks()
        else:
            raise Exception("Unknown transfer target", args.to)

    if args.action == "filter":
        check_db(args.db)
        if args.where is None:
            raise Exception("You must provide a --where clause for the filter")
        action_filter()
        return

    if args.action == "squash":
        check_db(args.db)
        action_squash()
        return

    if args.action == "ls":
        num_files = len(glob.glob("*"))
        if num_files > 15:
            system("ls -l | more")
        else:
            system("ls -l")
        return

    if args.action == "cd":
        if not args.dir:
            raise Exception("You must provide a --dir=<directory>")
        path = os.path.expanduser(args.dir)
        chdir(path)
        return

    if args.action == "mkdir":
        if not args.dir:
            raise Exception("You must provide a --dir=<directory>")
        os.mkdir(args.dir)
        return

    if args.action == "pwd":
        print(os.getcwd())
        return

    if args.action == "models":
        models = action_models(args)
        console.log(models)
        return

    if args.action == "exit":
        console.log("Bye!")
        sys.exit(0)

    if args.action == "stats":
        check_db(args.db)
        action_stats()
        return


# accepts a command
async def run():
    commands = load_user_file(args.fn)
    # Load the metadata
    metadata = {}
    if args.globals is not None:
        metadata = read_metadata(args.globals)
    # Render the template
    template = Template(commands)
    commands = template.render(**metadata)
    # Print the commands
    console.log(commands)
    # Leave if we're just previewing
    if args.preview:
        return

    for command in commands.split("\n"):
        # skip lines that start with a #
        if command.strip().startswith("#") or len(command) == 0:
            continue
        args = define_arguments(command)
        await process_command()


async def main():
    global args
    if len(sys.argv) > 1:
        args = define_arguments()
        try:
            if args.action == "run":
                if args.fn is None:
                    raise Exception(
                        "You must provide a --fn argument for the file to run"
                    )
                instructions = render_command_file()
                for instruction in instructions:
                    print(instruction)
                    if instruction.strip().startswith("#"):
                        continue
                    args = define_arguments(instruction)
                    await process_command()
            else:
                await process_command()
        except Exception as e:
            console.log("[red]An error occurred on this request[/red]")
            console.log(" ".join(sys.argv))
            console.log(f"\nThe following error occurred:\n\n[red]{e}[/red]\n")
            print(traceback.format_exc())
            sys.exit(1)
    else:
        Art = text2art("prompter")
        print(f"[green]{Art}")
        session = PromptSession()
        while True:
            argString = await session.prompt_async(f"prompter> ")
            # If the user just hits enter, skip parsing because it will exit the program
            if len(argString) == 0:
                continue
            # In the command is a comment then exit
            if argString.strip().startswith("#"):
                print("Skipping comment")
                continue
            if argString == "exit":
                break
            try:
                args = define_arguments(argString)
                if args.action == "run":
                    if args.fn is None:
                        raise Exception(
                            "You must provide a --fn argument for the file to run"
                        )
                    instructions = render_command_file()
                    console.log(instructions)
                    # Leave if we're just previewing
                    if not args.preview:
                        for instruction in instructions:
                            if (
                                instruction.strip().startswith("#")
                                or len(instruction) == 0
                            ):
                                continue
                            args = define_arguments(instruction)
                            await process_command()
                else:
                    await process_command()
            except Exception as e:
                console.log("[red]An error occurred on this request[/red]")
                console.log(" ".join(sys.argv))
                console.log(f"\nThe following error occurred:\n\n[red]{e}[/red]\n")
                print(traceback.format_exc())


# *****************************************************************************************
# Main
# *****************************************************************************************
if __name__ == "__main__":
    os.chdir(os.path.expanduser("~/Desktop/cat-essay"))
    asyncio.run(main())
