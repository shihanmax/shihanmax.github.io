import sys
sys.path.append("..")

from utils.markdown_parser import MarkdownParser


with open("/Users/shihanmax/Documents/code/blog/_posts/2022-03-06-entity_relation_extraction.md") as frd:
    html = MarkdownParser().render(frd.read())
    
    
with open("test.html", "w") as fwr:
    fwr.write(html)
