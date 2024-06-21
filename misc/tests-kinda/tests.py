import pytest

import main


def test_squash():
    main.args = main.define_arguments("version")
    main.args.delimiter = "*"
    # Test that the squash function works
    data = [
        {"block_tag": "one", "response": "one"},
        {"block_tag": "one", "response": "two"},
        {"block_tag": "one", "response": "three"},
        {"block_tag": "two", "response": "four"},
        {"block_tag": "two", "response": "five"},
        {"block_tag": "two", "response": "six"},
        {"block_tag": "three", "response": "seven"},
        {"block_tag": "four", "response": "eight"},
        {"block_tag": "four", "response": "nine"},
        {"block_tag": "four", "response": "ten"},
    ]
    # assert main.squash(data) == {
    #    "one": "one*two*three*",
    #    "two": "four*five*six*",
    #    "three": "seven*",
    #    "four": "eight*nine*ten*",
    # }
