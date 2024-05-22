from argparse import ArgumentParser, BooleanOptionalAction
from rich.console import Console
from rich import print
from rich.table import Table
from dotenv import load_dotenv, find_dotenv
from ebooklib import epub
from ebooklib import ITEM_DOCUMENT as ebooklib_ITEM_DOCUMENT
from bs4 import BeautifulSoup
import sqlite3
import time
import shutil
import os
from jinja2 import Template
import sys
import openai
import hashlib
import logging
import glob
from transformations import *
import os
from pathlib import Path
from faker import Faker
import yaml
from prompt_toolkit import PromptSession
from shlex import split as shlex_split
from art import text2art
from sys import exit
from os import system, chdir


console = Console()
fake = Faker()
log = logging.getLogger("rich")

VERSION = "0.3.0"

ENV_FILENAME = ".promptlab"

ACTIONS = [
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
    "merge-prompts-into-block",
    "ls",
    "cd",
    "mkdir",
    "pwd",
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


# Check if the .promptlab file exists in the home directory
def load_env():
    home = str(Path.home())
    if not os.path.isfile(home + "/" + ENV_FILENAME):
        return False
    load_dotenv(home + "/" + ENV_FILENAME)
    console.log(f"Loaded API key from {home}/{ENV_FILENAME}")
    return True


# Write the API key to the .promptlab file in the home directory
def action_set_api_key():
    console.log("Setting API key")
    home = str(Path.home())
    # get user input for api key
    api_key = input("Enter your API key: ")
    # write the key to the .promptlab file
    console.log(f"Missing credentials in file {home}/{ENV_FILENAME}.")
    with open(home + "/" + ENV_FILENAME, "w") as f:
        f.write(f"API_KEY={api_key}")
    console.log(f"API key set successfully and saved in {home}/{ENV_FILENAME}")


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
    return load_file(fn, False)


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


# Used to get the where clause.  I'll add something about ssql injection here later
def apply_where_clause(sql):
    if args.where is not None:
        sql += " where " + args.where
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


# *****************************************************************************************
#  Metadata
# *****************************************************************************************


def read_metadata(fn):
    txt = load_user_file(fn)
    # parse the yml file into a dictionary
    metadata = yaml.safe_load(txt)
    return metadata


# Takes prompts and converts them to metadata under the supplied key
def action_transfer_prompts_to_metadata(prompt_tag, metadata_key):
    header, results = fetch_prompts()
    try:
        sql = load_system_file("sql/create_metadata.sql")
        conn = sqlite3.connect(args.db)
        conn.isolation_level = None
        c = conn.cursor()
        c.execute("BEGIN")
        for r in results:
            c.execute(sql, (r["block_id"], metadata_key, r["response"]))
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
def fetch_blocks(tag=None, latest=True, sort_by=None):
    sql = load_system_file("sql/v_current_blocks.sql")
    sql = apply_where_clause(sql)
    headers, results = fetch_from_db(sql, ())
    if sort_by is not None:
        results = sorted(results, key=lambda d: d[sort_by])
    else:
        results = sorted(results, key=lambda d: d[headers[0]])
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
        files = glob.glob(args.fn)
        idx = 0
        for f in files:
            txt = load_user_file(f)
            data.append({"block": txt, "tag": f, "parent_id": idx})
            idx += 1
    insert_blocks_in_new_group(data)


def action_transfer_prompts_to_blocks(prompt_tag):
    headers, results = fetch_prompts()
    # print_results("Prompts to transfer", headers, results)
    data = []
    for p in results:
        data.append(
            {"block": p["response"], "tag": p["block_tag"], "parent_id": p["parent_id"]}
        )
    insert_blocks_in_new_group(data)


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


def action_prompt(prompt_fn):
    openai.api_key = os.environ["API_KEY"]
    prompt = load_user_file(prompt_fn)
    metadata = {}
    if args.globals is not None:
        metadata = read_metadata(args.globals)
    template = Template(prompt)
    headers, blocks = fetch_blocks()
    # Apply the template to each block
    prompt_log_id, prompt_tag = create_prompt_log(prompt_fn, prompt)
    idx = 1
    for b in blocks:
        prompt_text = template.render(block=b["block"], **metadata)
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
            response = openai.ChatCompletion.create(
                model=args.model,
                messages=[{"role": "user", "content": prompt_text}],
                temperature=0.1,
                max_tokens=1000,
            )
            response_txt = str(response.choices[0].message.content)
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
    sql = apply_where_clause(sql)
    return fetch_from_db(sql, ())


def action_merge_prompts_into_block():
    sql = load_system_file("sql/v_current_prompts.sql")
    sql = apply_where_clause(sql)
    headers, results = fetch_from_db(sql, ())
    # merge the results into single string , grouping by the parent_block column
    merged_results = {}
    for r in results:
        if r["block_parent_id"] not in merged_results:
            merged_results[r["block_parent_id"]] = []
        merged_results[r["block_parent_id"]].append(r["response"])
    out = []
    tag = "merged_prompts"
    for k in merged_results.keys():
        new_block = get_delimiter().join(merged_results[k])
        out.append({"block": new_block, "tag": tag, "parent_id": int(k)})
    insert_blocks_in_new_group(out)


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
    sql = apply_where_clause(sql)
    headers, results = fetch_from_db(sql, ())
    results = sorted(results, key=lambda d: d[headers[0]])
    print_results("Prompt Logs", headers, results)


def action_prompts():
    sql = load_system_file("sql/v_current_prompts.sql")
    sql = apply_where_clause(sql)
    columns, results = fetch_from_db(sql, ())
    results = transform_by_key(
        results,
        {
            "response": lambda x: x[:40].replace("\n", " "),
            "elapsed_time_in_seconds": lambda x: f"{x:.2f}",
        },
    )
    print_results("Prompts", columns, results)
    console.print(f"\n{len(results)} prompts in total")
    console.print("The following fields available in --where clause:", columns)


def action_dump_blocks():
    headers, blocks = fetch_blocks()
    # Pull out the block element into it's own list
    out = [b["block"] for b in blocks]
    console.print(get_delimiter().join(out))


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
        "--db", help="The database file", required=False, default="promptlab.db"
    )
    # Arguments related to loading files
    parser.add_argument("--fn", help="Filename", required=False)
    # Arguments related to naming or fetching blocks, prompts, etc.
    parser.add_argument("--group_tag", help="Tag to filter on", required=False)
    parser.add_argument("--prompt_tag", help="Tag to filter on", required=False)
    parser.add_argument("--where", help="SQLITE where clause", required=False)
    # Arguments related to prompting
    parser.add_argument("--prompt", help="Prompt to use", required=False)
    parser.add_argument("--model", help="Model to use", required=False, default="gpt-4")
    parser.add_argument(
        "--fake",
        help="Generate fake prompt response data",
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
        default="metadata",
    )
    # Arguments related to tranferring data from prompts to metadata or blocks
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
    # arguments related to files and the current directory
    parser.add_argument("--dir", help="Directory name", required=False)

    if argString:
        return parser.parse_args(shlex_split(argString))
    else:
        return parser.parse_args()


# *****************************************************************************************


def process_command():
    if args.action == "init":
        action_init()
        return

    if args.action == "load":
        check_db(args.db)
        if args.fn is None:
            raise Exception("You must provide a --fn argument for the file to load")
        action_load()
        return

    if args.action == "transform":
        check_db(args.db)
        if args.transformation is None:
            raise Exception("You must provide a --transformation argument to use")
        transformations = args.transformation.split(",")
        if len(transformations) > 0 and args.group_tag is not None:
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
        console.log(args.fn)
        if args.fn is None:
            raise Exception("You must provide a --fn argument for the prompt")
        if load_env() is False:
            action_set_api_key()
            load_env()
        action_prompt(args.fn)
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
            action_transfer_prompts_to_metadata(args.prompt_tag, args.metadata_key)
        elif args.to == "blocks":
            action_transfer_prompts_to_blocks(args.prompt_tag)
        else:
            raise Exception("Unknown transfer target", args.to)

    if args.action == "filter":
        check_db(args.db)
        if args.where is None:
            raise Exception("You must provide a --where clause for the filter")
        action_filter()
        return

    if args.action == "merge-prompts-into-block":
        check_db(args.db)
        action_merge_prompts_into_block()
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


if __name__ == "__main__":

    if len(sys.argv) > 1:
        args = define_arguments()
        try:
            process_command()
        except Exception as e:
            console.log("[red]An error occurred on this request[/red]")
            console.log(" ".join(sys.argv))
            console.log(f"\nThe following error occurred:\n\n[red]{e}[/red]\n")
            sys.exit(1)
    else:
        Art = text2art("Promptlab")
        print(f"[green]{Art}")
        session = PromptSession()
        while True:
            argString = session.prompt("promptlab> ")
            # If the user just hits enter, skip parsing because it will exit the program
            if len(argString) == 0:
                continue
            if argString == "exit":
                break
            try:
                args = define_arguments(argString)
                process_command()
            except Exception as e:
                console.log("[red]An error occurred on this request[/red]")
                console.log(" ".join(sys.argv))
                console.log(f"\nThe following error occurred:\n\n[red]{e}[/red]\n")
