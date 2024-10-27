# For pyinstaller, we want to show something as quickly as possible
print("Loading transformations...")
from rich.console import Console

console = Console()

# Set up a loading message as the libraries are loaded
with console.status(f"[bold green]Loading required libraries...") as status:
    from markdownify import markdownify as md
    import markdown
    from bs4 import BeautifulSoup


# Dictionary to map transformation names to functions
TRANSFORMATIONS = {
    "token-split": lambda b, **kwargs: transformation_token_split(b, **kwargs),
    "clean-epub": lambda b, **kwargs: transformation_clean_epub(b, **kwargs),
    "html-h1-split": lambda b, **kwargs: transformation_html_heading_split(
        b, splits=["h1"], **kwargs
    ),
    "html-h2-split": lambda b, **kwargs: transformation_html_heading_split(
        b, splits=["h1", "h2"], **kwargs
    ),
    "html2md": lambda b, **kwargs: transformation_html2md(b, **kwargs),
    "html2txt": lambda b, **kwargs: transformation_html2txt(b, **kwargs),
    "new-line-split": lambda b, **kwargs: transformation_newline_split(b, **kwargs),
    "sentence-split": lambda b, **kwargs: transformation_sentence_split(b, **kwargs),
}


def transformation_token_split(b, **kwargs):
    N = kwargs.get("N", 1000)
    res = []
    tokens = b.split()
    for i in range(0, len(tokens), N):
        res.append(" ".join(tokens[i : i + N]))
    return res


def transformation_clean_epub(b, **kwargs):
    # Convert the raw block of epub html to markdown
    out = md(b, heading_style="ATX")
    out = out.replace("xml version='1.0' encoding='utf-8'?", "")
    out = out.replace("\n\n", "\n")
    # Use markdown to convert the markdown back to html
    out = markdown.markdown(out)
    # Read into beautiful soup
    soup = BeautifulSoup(out, "html.parser")
    # Pretty print the html
    out = soup.prettify(formatter="html")
    return out


#
# Split an HTML into blocks based on the h1 and h2 tags
#
def transformation_html_heading_split(b, **kwargs):
    splits = kwargs.get("splits", ["h1"])
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


def transformation_html2md(b, **kwargs):
    out = md(b, heading_style="ATX")
    out = out.replace("xml version='1.0' encoding='utf-8'?", "")
    out = out.replace("\n\n", "\n")
    return out


def transformation_html2txt(b, **kwargs):
    soup = BeautifulSoup(b, "html.parser")
    return soup.prettify()


def transformation_newline_split(b, **kwargs):
    # split text by newline and only return non-empty strings
    out = b.split("\n")
    out = list(filter(None, out))
    return out


def transformation_sentence_split(b, **kwargs):
    out = b.split(".")
    # Remove empty strings
    out = list(filter(None, out))
    # Trim the strings
    out = [x.strip() for x in out]
    # Add period to the end of each sentence
    out = [x + "." for x in out]
    return out
