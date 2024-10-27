# For pyinstaller, we want to show something as quickly as possible
print("Loading transformations...")
from rich.console import Console

console = Console()

# Set up a loading message as the libraries are loaded
with console.status(f"[bold green]Loading required libraries...") as status:
    from markdownify import markdownify as md
    import markdown
    from bs4 import BeautifulSoup


def transformation_token_split(args, b):
    res = []
    tokens = b.split()
    for i in range(0, len(tokens), args.N):
        res.append(" ".join(tokens[i : i + args.N]))
    return res


def transformation_clean_epub(args, b):
    # Convert the raw block of epub html to markdown
    out = md(b, heading_style="ATX")
    out = out.replace("xml version='1.0' encoding='utf-8'?", "")
    out = out.replace("\n\n", "\n")
    # Use markdown to conver the markdown to back html
    out = markdown.markdown(out)
    # Read into beautiful soup
    soup = BeautifulSoup(out, "html.parser")
    # Prettiy print the html
    out = soup.prettify(formatter="html")
    return out


#
# Split an HTML into blocks based on the h1 and h2 tags
#
def transformation_html_heading_split(args, b, splits):
    # Construct a BeautifulSoup out of the raw HTML
    soup = BeautifulSoup(b, "html.parser")
    blocks = []
    s = ""
    tag = soup.find("h1")  # Find the first tag
    while tag:
        if tag.name is not None:
            s += repr(tag).replace("\n", " ")
        else:
            s += "\n\n"
        tag = tag.nextSibling
        if tag is not None and tag.name in splits:
            blocks.append(s.replace("'\n'", "\n"))
            s = ""
    # Now append the last block, which is everything that comes after the last h2 tag
    blocks.append(s.replace("'\n'", "\n"))
    return blocks


def transformation_html2md(args, b):
    out = md(b, heading_style="ATX")
    out = out.replace("xml version='1.0' encoding='utf-8'?", "")
    out = out.replace("\n\n", "\n")
    return out


def transformation_html2txt(args, b):
    soup = BeautifulSoup(b, "html.parser")
    return soup.prettify()


def transformation_newline_split(args, b):
    # split text text by newline and only return non-empty strings
    out = b.split("\n")
    out = list(filter(None, out))
    return out


def transformation_sentence_split(args, b):
    out = b.split(".")
    # Remove empty strings
    out = list(filter(None, out))
    # Trim the strings
    out = [x.strip() for x in out]
    # Add period to the end of each sentence
    out = [x + "." for x in out]
    return out


# Dictionary to map transformation names to functions
TRANSFORMATIONS = {
    "token-split": transformation_token_split,
    "clean-epub": transformation_clean_epub,
    "html-h1-split": lambda args, b: transformation_html_heading_split(args, b, ["h1"]),
    "html-h2-split": lambda args, b: transformation_html_heading_split(
        args, b, ["h1", "h2"]
    ),
    "html2md": transformation_html2md,
    "html2txt": transformation_html2txt,
    "new-line-split": transformation_newline_split,
    "sentence-split": transformation_sentence_split,
}
