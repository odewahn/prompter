import argparse


def create_parser():
    parser = argparse.ArgumentParser(description="Prompter repl")
    subparsers = parser.add_subparsers(dest="command")

    # Adding a command to create a new database
    use_parser = subparsers.add_parser("use", help="Use a new database")
    use_parser.add_argument("db_name", type=str, help="Database name to use")

    # Adding a command to exit the repl
    exit_parser = subparsers.add_parser("exit", help="Exit the repl")

    return parser
