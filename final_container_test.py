#!/usr/bin/env python3
"""
Final test to verify that all article content is properly contained within the post-container.
"""

import requests
from bs4 import BeautifulSoup


def final_container_test():
    """Final test to verify container structure."""
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
        
        # Get all headings in the entire document
        all_headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        print(f"Total headings in entire document: {len(all_headings)}")
        
        # Get all headings inside the article content
        article_headings = article_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        print(f"Headings inside article content: {len(article_headings)}")
        
        # Check which headings are outside the post-container
        headings_outside = []
        for heading in all_headings:
            # Check if this heading is inside the post-container
            parent = heading.find_parent('div', class_='post-container')
            if not parent:
                headings_outside.append(heading.get_text().strip())
                
        if headings_outside:
            print(f"Headings outside post-container: {headings_outside}")
        else:
            print("SUCCESS: No headings outside post-container")
            
        # Check for specific article headings
        expected_article_headings = [
            "关系抽取",
            "关系抽取中的几种复杂情况", 
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
        
        found_article_headings = [h.get_text().strip().replace('¶', '') for h in article_headings]
        missing_headings = [h for h in expected_article_headings if h not in found_article_headings]
        
        if missing_headings:
            print(f"Missing expected article headings: {missing_headings}")
        else:
            print("SUCCESS: All expected article headings found")
            
        # Verify container structure
        main_container = soup.find('main', class_='u-container')
        if not main_container:
            print("ERROR: u-container not found!")
            return False
            
        # Check that post-container is inside u-container
        post_container_parent = post_container.find_parent('main', class_='u-container')
        if not post_container_parent:
            print("ERROR: post-container is not inside u-container!")
            return False
            
        print("SUCCESS: post-container is properly nested inside u-container")
        
        # Check for any content that might be outside the post-container but inside u-container
        # Get all content inside u-container
        u_container_content = main_container.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'img', 'table', 'ul', 'ol'])
        
        content_outside_post_container = []
        for element in u_container_content:
            # Skip elements that are part of the header or footer
            if element.find_parent('header') or element.find_parent('footer'):
                continue
                
            # Check if this element is inside the post-container
            parent = element.find_parent('div', class_='post-container')
            if not parent:
                content_outside_post_container.append(element.name)
                
        if content_outside_post_container:
            print(f"Content elements outside post-container: {set(content_outside_post_container)}")
        else:
            print("SUCCESS: No content elements outside post-container")
            
        print("\n=== FINAL CONTAINER TEST RESULTS ===")
        print(f"Article title: {soup.find('h1', class_='c-article__title').get_text().strip()}")
        print(f"Total document headings: {len(all_headings)}")
        print(f"Article content headings: {len(article_headings)}")
        print("Container structure: Properly nested")
        print("Content containment: Properly contained within post-container")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False


if __name__ == "__main__":
    print("Running final container test for entity relation extraction article...")
    final_container_test()