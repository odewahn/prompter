# This file contains the various transformations you can use

from markdownify import markdownify as md
import markdown
from bs4 import BeautifulSoup


def transformation_token_split(b, N=2000):
    res = []
    tokens = b.split()
    for i in range(0, len(tokens), N):
        res.append(" ".join(tokens[i : i + N]))
    return res


def transformation_clean_epub(b):
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
def transformation_html_heading_split(b, splits):
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
    return blocks


def transformation_html2md(b):
    out = md(b, heading_style="ATX")
    out = out.replace("xml version='1.0' encoding='utf-8'?", "")
    out = out.replace("\n\n", "\n")
    return out


def transformation_html2txt(b):
    soup = BeautifulSoup(b, "html.parser")
    return soup.prettify()


def transformation_newline_split(b):
    # split text text by newline and only return non-empty strings
    out = b.split("\n")
    out = list(filter(None, out))
    return out


def transformation_sentence_split(b):
    out = b.split(".")
    # Remove empty strings
    out = list(filter(None, out))
    # Trim the strings
    out = [x.strip() for x in out]
    # Add period to the end of each sentence
    out = [x + "." for x in out]
    return out
