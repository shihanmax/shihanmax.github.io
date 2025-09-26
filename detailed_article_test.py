#!/usr/bin/env python3
"""
Detailed test script to examine the full structure of the entity relation extraction article.
"""

import requests
from bs4 import BeautifulSoup


def detailed_article_analysis():
    """Perform a detailed analysis of the article structure."""
    try:
        # Fetch the article
        url = "http://localhost:8081/2022/03/entity_relation_extraction"
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Failed to fetch article. Status code: {response.status_code}")
            return False
            
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the post-container
        post_container = soup.find('div', class_='post-container')
        if not post_container:
            print("ERROR: post-container not found!")
            return False
            
        print("SUCCESS: post-container found")
        
        # Check if the article content is inside the post-container
        article_content = post_container.find('div', id='article-content')
        if not article_content:
            print("ERROR: article-content not found inside post-container!")
            return False
            
        print("SUCCESS: article-content found inside post-container")
        
        # Get all headings in the article content
        headings = article_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        print(f"Total headings found in article: {len(headings)}")
        
        # Print all headings with their levels
        print("\nHeadings structure:")
        for i, heading in enumerate(headings):
            level = heading.name
            text = heading.get_text().strip()
            print(f"  {i+1}. {level}: {text}")
            
        # Check for images
        images = article_content.find_all('img')
        print(f"\nTotal images found: {len(images)}")
        for i, img in enumerate(images):
            src = img.get('src', 'No src attribute')
            alt = img.get('alt', 'No alt attribute')
            print(f"  {i+1}. src: {src}")
            print(f"      alt: {alt}")
            
        # Check for mathematical content
        math_content = str(article_content)
        display_math_count = math_content.count('$$')
        inline_math_count = math_content.count('$') - (display_math_count * 2)  # Each $$ contains two $ symbols
        print(f"\nMathematical content:")
        print(f"  Display math blocks: {display_math_count // 2}")  # Each block has opening and closing $$
        print(f"  Inline math expressions: {inline_math_count}")
        
        # Check the overall structure
        main_container = soup.find('main', class_='u-container')
        if not main_container:
            print("ERROR: u-container not found!")
            return False
            
        print("\nContainer structure verification:")
        print("SUCCESS: u-container found")
        
        # Check that post-container is inside u-container
        post_container_parent = post_container.find_parent('main', class_='u-container')
        if not post_container_parent:
            print("ERROR: post-container is not inside u-container!")
            return False
            
        print("SUCCESS: post-container is properly nested inside u-container")
        
        # Verify that all content is within the post-container
        # Get all text content elements
        content_elements = article_content.find_all(['p', 'div', 'span', 'img', 'table', 'ul', 'ol'])
        elements_outside = 0
        
        for element in content_elements:
            parent_container = element.find_parent('div', class_='post-container')
            if not parent_container:
                elements_outside += 1
                
        if elements_outside > 0:
            print(f"WARNING: {elements_outside} content elements found outside post-container")
        else:
            print("SUCCESS: All content elements are properly contained within post-container")
            
        print("\n=== DETAILED ARTICLE ANALYSIS COMPLETE ===")
        print(f"Article title: {soup.find('h1', class_='c-article__title').get_text().strip()}")
        print(f"Total headings: {len(headings)}")
        print(f"Total images: {len(images)}")
        print(f"Display math blocks: {display_math_count // 2}")
        print(f"Inline math expressions: {inline_math_count}")
        print("Container structure: Properly nested")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False


if __name__ == "__main__":
    print("Performing detailed analysis of entity relation extraction article...")
    detailed_article_analysis()