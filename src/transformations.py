# For pyinstaller, we want to show something as quickly as possible
print("Loading transformations...")
from rich.console import Console

console = Console()

# Set up a loading message as the libraries are loaded
with console.status(f"[bold green]Loading required libraries...") as status:
    from markdownify import markdownify as md
    import markdown
    from bs4 import BeautifulSoup


def apply_transformation(transformation_name, b, **kwargs):
    # if b is string, apply the transformation
    if isinstance(b, str):
        return perform(transformation_name, b, **kwargs)
    # if b is list, apply the transformation to each element of the list
    elif isinstance(b, list):
        out = [x for item in b for x in perform(transformation_name, item, **kwargs)]
        return out
    elif transformation_name == "strip-attributes":
        return transformation_strip_attributes(b, **kwargs)
        raise ValueError(f"Unrecognized type: {type(b)}")


def perform(transformation_name, b, **kwargs):
    if transformation_name == "token-split":
        return transformation_token_split(b, **kwargs)
    elif transformation_name == "clean-epub":
        return transformation_clean_epub(b, **kwargs)
    elif transformation_name == "html-h1-split":
        return transformation_html_heading_split(b, splits=["h1"], **kwargs)
    elif transformation_name == "html-h2-split":
        return transformation_html_heading_split(b, splits=["h1", "h2"], **kwargs)
    elif transformation_name == "html-to-md":
        return transformation_html_to_md(b, **kwargs)
    elif transformation_name == "html-to-txt":
        return transformation_html_to_txt(b, **kwargs)
    elif transformation_name == "new-line-split":
        return transformation_newline_split(b, **kwargs)
    elif transformation_name == "sentence-split":
        return transformation_strip_attributes(b, **kwargs)
    elif transformation_name == "strip-attributes":
        return transformation_strip_attributes(b, **kwargs)
    elif transformation_name == "extract-headers":
        return transformation_extract_headers(b, **kwargs)
    else:
        raise ValueError(f"Unrecognized transformation: {transformation_name}")


def transformation_token_split(b, **kwargs):
    N = kwargs.get("n", 1000)
    OVERLAP = kwargs.get("overlap", 10)
    STEP = int(N * (1 - OVERLAP / 100))
    res = []
    tokens = b.split(" ")
    for i in range(0, len(tokens), STEP):
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


def transformation_strip_attributes(b, **kwargs):
    soup = BeautifulSoup(b, "html.parser")
    for tag in soup(["style", "script"]):
        tag.decompose()
    for tag in soup.find_all(True):  # True matches all tags
        tag.attrs = {key: value for key, value in tag.attrs.items() if key == "id"}
    return str(soup)


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


def transformation_html_to_md(b, **kwargs):
    out = md(b, heading_style="ATX")
    out = out.replace("xml version='1.0' encoding='utf-8'?", "")
    out = out.replace("\n\n", "\n")
    return out


def transformation_html_to_txt(b, **kwargs):
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


# Add a transformation that will pull out all headers in order, as well as the firs
# paragraph of each section
def transformation_extract_headers(b, **kwargs):
    soup = BeautifulSoup(b, "html.parser")
    out = ""
    for tag in soup.find_all(["h1", "h2", "h3", "h4"]):
        # intialize text with the full tag and its text
        out += repr(tag).replace("\n", " ") + "\n"
    return out
