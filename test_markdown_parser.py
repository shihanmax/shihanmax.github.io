#!/usr/bin/env python3
"""
Unit tests for the MarkdownParser class
"""

import os
import sys
import unittest
from typing import List

# Add the parent directory to the path so we can import the utils module
sys.path.insert(0, os.path.dirname(__file__))

from utils.markdown_parser import MarkdownParser
from utils.toc_parser import TOCItem


class TestMarkdownParser(unittest.TestCase):
    """Test cases for the MarkdownParser class"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.parser = MarkdownParser()

    def test_basic_markdown_rendering(self):
        """Test basic markdown rendering functionality"""
        content = ("# Hello World\n\nThis is a **bold** text "
                   "and this is *italic*.")
        
        result = self.parser.render(content)
        # We'll check for key elements rather than exact match due to 
        # potential whitespace differences
        self.assertIn('Hello World', result)
        self.assertIn('<strong>bold</strong>', result)
        self.assertIn('<em>italic</em>', result)

    def test_code_block_rendering(self):
        """Test code block rendering with syntax highlighting"""
        content = """```python
def hello():
    print("Hello, World!")
```"""
        
        result = self.parser.render(content)
        self.assertIn('class="highlight"', result)
        # Code is wrapped in span tags with classes, so check for parts of the code
        self.assertIn('Hello, World!', result)

    def test_table_rendering(self):
        """Test table rendering with responsive wrapper"""
        content = """| Name | Age |
|------|-----|
| John | 30  |
| Jane | 25  |"""
        
        result = self.parser.render(content)
        self.assertIn('<div class="table-responsive">', result)
        self.assertIn('<table class="table">', result)
        self.assertIn('John', result)
        self.assertIn('Jane', result)

    def test_math_formula_preservation(self):
        """Test that math formulas are preserved correctly"""
        content = ("This is an inline formula $E = mc^2$ and a block "
                   "formula $$F = ma$$")
        
        result = self.parser.render(content)
        # The math formulas should be preserved in the output
        self.assertIn('$E = mc^2$', result)
        self.assertIn('$$F = ma$$', result)

    def test_image_responsive_class(self):
        """Test that images get responsive class added"""
        content = "![Alt text](image.jpg)"
        
        result = self.parser.render(content)
        self.assertIn('class="img-responsive"', result)

    def test_jekyll_highlight_tag_conversion(self):
        """Test conversion of Jekyll highlight tags to code blocks"""
        content = """{% highlight python %}
def test():
    return True
{% endhighlight %}"""
        
        result = self.parser.render(content)
        self.assertIn('class="highlight"', result)
        # Code is wrapped in span tags with classes
        # With syntax highlighting, "True" becomes "<span class="kc">True</span>"
        self.assertIn('True', result)

    def test_toc_generation(self):
        """Test table of contents generation"""
        content = """# Introduction
# Main Content
## Subsection
# Conclusion"""
        
        toc = self.parser.get_toc(content)
        # The TOC extension generates HTML with ul/li elements
        self.assertIn('<ul>', toc)
        self.assertIn('Introduction', toc)
        self.assertIn('Main Content', toc)
        self.assertIn('Conclusion', toc)

    def test_summary_extraction(self):
        """Test summary extraction functionality"""
        content = ("# Title\nThis is a short article with some content "
                   "that should be extracted as a summary.")
        
        summary = self.parser.extract_summary(content, 50)
        # 50 + ... = 53, so <= 55 is reasonable
        self.assertTrue(len(summary) <= 55)
        self.assertIn('This is a short article', summary)

    def test_toc_parsing_from_markdown(self):
        """Test parsing TOC from markdown content"""
        content = """# Introduction
Some content here.

## Background
More content.

# Main Topic
## Subsection 1
### Sub-subsection
## Subsection 2

# Conclusion"""
        
        toc_items: List[TOCItem] = self.parser.parse_toc_from_markdown(content)
        self.assertEqual(len(toc_items), 3)  # Three top-level headings
        self.assertEqual(toc_items[0].title, 'Introduction')
        self.assertEqual(toc_items[1].title, 'Main Topic')
        self.assertEqual(toc_items[2].title, 'Conclusion')
        
        # Check that Main Topic has children
        main_topic = toc_items[1]
        self.assertIsNotNone(main_topic.children)
        if main_topic.children is not None:
            self.assertEqual(len(main_topic.children), 2)  # Two subsections
            self.assertEqual(main_topic.children[0].title, 'Subsection 1')
            self.assertEqual(main_topic.children[1].title, 'Subsection 2')
            
            # Check that Subsection 1 has a child
            subsection_1 = main_topic.children[0]
            self.assertIsNotNone(subsection_1.children)
            if subsection_1.children is not None:
                self.assertEqual(len(subsection_1.children), 1)
                self.assertEqual(
                    subsection_1.children[0].title, 
                    'Sub-subsection'
                )

    def test_toc_html_generation(self):
        """Test TOC HTML generation"""
        content = """# Introduction
## Background
# Main Topic"""
        
        toc_html = self.parser.generate_toc_html(content)
        self.assertIn('<ul class="toc-list">', toc_html)
        self.assertIn('Introduction', toc_html)
        self.assertIn('Background', toc_html)
        self.assertIn('Main Topic', toc_html)
        self.assertIn('href="#', toc_html)  # Check for anchor links

    def test_toc_json_generation(self):
        """Test TOC JSON generation"""
        content = """# Introduction
## Background
# Main Topic"""
        
        toc_json = self.parser.generate_toc_json(content)
        self.assertIsInstance(toc_json, list)
        self.assertEqual(len(toc_json), 2)  # Two top-level items
        self.assertEqual(toc_json[0]['title'], 'Introduction')
        self.assertEqual(toc_json[1]['title'], 'Main Topic')
        
        # Check children
        intro_children = toc_json[0]['children']
        self.assertEqual(len(intro_children), 1)
        self.assertEqual(intro_children[0]['title'], 'Background')

    def test_toc_summary(self):
        """Test TOC summary information"""
        content = """# Introduction
## Background
## Another Subsection
# Main Topic
### Deep Subsection
# Conclusion"""
        
        summary = self.parser.get_toc_summary(content)
        self.assertIn('total_items', summary)
        self.assertIn('max_level', summary)
        self.assertIn('has_content', summary)
        
        # Should have multiple items
        self.assertTrue(summary['total_items'] >= 5)
        self.assertEqual(summary['max_level'], 3)  # H3 is level 3
        self.assertTrue(summary['has_content'])

    def test_empty_content_handling(self):
        """Test handling of empty content"""
        result = self.parser.render("")
        self.assertEqual(result, "")
        
        toc = self.parser.get_toc("")
        self.assertEqual(toc, "")
        
        summary = self.parser.extract_summary("")
        self.assertEqual(summary, "")
        
        toc_items = self.parser.parse_toc_from_markdown("")
        self.assertEqual(toc_items, [])

    def test_complex_markdown_content(self):
        """Test rendering of complex markdown content"""
        content = """# Complex Article

This is a paragraph with **bold text** and *italic text*.

## Code Example

```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))
```

## Table Example

| Language | Creator | Year |
|----------|---------|------|
| Python   | Guido   | 1991 |
| JavaScript | Brendan | 1995 |

## Mathematical Formulas

Inline formula: $E = mc^2$

Block formula:
$$
\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}
$$

![Python Logo](python.png)

> This is a blockquote that should be rendered properly.
"""
        
        result = self.parser.render(content)
        
        # Check for key elements
        self.assertIn('Complex Article', result)
        self.assertIn('<strong>bold text</strong>', result)
        self.assertIn('<em>italic text</em>', result)
        self.assertIn('class="highlight"', result)  # Code block
        self.assertIn('<div class="table-responsive">', result)  # Table
        self.assertIn('$E = mc^2$', result)  # Math formula
        self.assertIn('class="img-responsive"', result)  # Image
        self.assertIn('<blockquote>', result)  # Blockquote


if __name__ == '__main__':
    print("Running MarkdownParser tests...")
    unittest.main(verbosity=2)