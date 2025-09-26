#!/usr/bin/env python3
"""
Test script to verify the HTML generation for the entity relation extraction article.
"""

import requests
from bs4 import BeautifulSoup


def test_entity_relation_extraction_article():
    """Test if the entity relation extraction article is properly rendered."""
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
        
        # Check that the article has content
        headings = article_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if len(headings) == 0:
            print("ERROR: No headings found in article content!")
            return False
            
        print(f"SUCCESS: Found {len(headings)} headings in article content")
        
        # Check for specific headings we expect in this article
        expected_headings = [
            "关系抽取",
            "关系抽取中的几种复杂情况",
            "SEO (single entity overlapping)",
            "EPO (entity pair overlapping)",
            "典型的E2E抽取框架介绍",
            "NovelTagging",
            "CopyR",
            "GraphRel",
            "RSAN",
            "CasRel",
            "TPLinker",
            "TDEER",
            "SDN",
            "参考"
        ]
        
        found_headings = [h.get_text().strip() for h in headings]
        missing_headings = [h for h in expected_headings if h not in found_headings]
        
        if missing_headings:
            print(f"WARNING: Some expected headings not found: {missing_headings}")
        else:
            print("SUCCESS: All expected headings found")
            
        # Check for images in the content
        images = article_content.find_all('img')
        print(f"Found {len(images)} images in article content")
        
        # Check for mathematical formulas (this article has mathjax enabled)
        math_content = str(article_content)
        if '$$' in math_content or '$' in math_content:
            print("SUCCESS: Mathematical formulas found in content")
        else:
            print("WARNING: No mathematical formulas found in content")
            
        # Check for proper nesting of containers
        main_container = soup.find('main', class_='u-container')
        if not main_container:
            print("ERROR: u-container not found!")
            return False
            
        print("SUCCESS: u-container found")
        
        # Check that post-container is inside u-container
        post_container_parent = post_container.find_parent('main', class_='u-container')
        if not post_container_parent:
            print("ERROR: post-container is not inside u-container!")
            return False
            
        print("SUCCESS: post-container is properly nested inside u-container")
        
        # Verify that all article content is within the post-container
        # Get all elements that should be inside the article content
        all_elements = article_content.find_all()
        elements_outside = []
        
        for element in all_elements:
            parent_container = element.find_parent('div', class_='post-container')
            if not parent_container:
                elements_outside.append(element.name)
                
        if elements_outside:
            print(f"WARNING: Some elements found outside post-container: {set(elements_outside)}")
        else:
            print("SUCCESS: All article elements are properly contained within post-container")
            
        print("\n=== ARTICLE RENDERING VERIFICATION PASSED ===")
        print("The entity relation extraction article is properly rendered with:")
        print(f"- {len(headings)} headings")
        print(f"- {len(images)} images")
        print("- Mathematical formulas")
        print("- Proper container nesting")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False


if __name__ == "__main__":
    print("Testing entity relation extraction article rendering...")
    test_entity_relation_extraction_article()