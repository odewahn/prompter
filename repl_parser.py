import argparse


def create_parser():
    parser = argparse.ArgumentParser(description="Prompter repl")
    subparsers = parser.add_subparsers(dest="command")

    # Adding a command to create a new database
    use_parser = subparsers.add_parser("use", help="Use a new database")
    use_parser.add_argument("db_name", type=str, help="Database name to use")

    # Adding a command to load files into a BlockGroup
    load_parser = subparsers.add_parser("load", help="Load files into a BlockGroup")
    load_parser.add_argument("files", nargs="+", help="List of files to load")
    load_parser.add_argument("--group_tag", help="Tag for the BlockGroup", required=False, default="default")
    exit_parser = subparsers.add_parser("exit", help="Exit the repl")

    return parser
