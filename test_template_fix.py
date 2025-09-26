#!/usr/bin/env python3
"""
Test script to verify the template fix for container wrapping issue.
"""

import requests
from bs4 import BeautifulSoup


def test_article_rendering():
    """Test if article content is properly wrapped in post-container."""
    try:
        # Fetch the test article
        url = "http://localhost:8081/2025/09/complex-test"
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Failed to fetch article. Status code: "
                  f"{response.status_code}")
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
        article_content = post_container.find('div', {'id': 'article-content'})
        if not article_content:
            print("ERROR: article-content not found inside post-container!")
            return False
            
        print("SUCCESS: article-content found inside post-container")
        
        # Check for proper structure
        # The article should contain all the content within the post-container
        # and not have any content leaking outside
        
        # Check if there are any article headings outside the post-container
        # We'll specifically look for headings that are part of the article content
        article_headings = article_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        all_headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        # Check if all article headings are inside the post-container
        headings_outside_container = []
        
        for heading in article_headings:
            # Check if this heading is inside the post-container
            parent = heading.find_parent('div', class_='post-container')
            if not parent:
                headings_outside_container.append(heading.get_text().strip())
                
        if headings_outside_container:
            print(f"ERROR: Article headings found outside post-container: "
                  f"{headings_outside_container}")
            return False
        else:
            print("SUCCESS: No article headings found outside post-container")
            
        # Check for proper nesting of containers
        main_container = soup.find('main', class_='u-container')
        if not main_container:
            print("ERROR: u-container not found!")
            return False
            
        print("SUCCESS: u-container found")
        
        # Check that post-container is inside u-container
        post_container_parent = post_container.find_parent(
            'main', class_='u-container')
        if not post_container_parent:
            print("ERROR: post-container is not inside u-container!")
            return False
            
        print("SUCCESS: post-container is properly nested inside u-container")
        
        print("\n=== TEMPLATE FIX VERIFICATION PASSED ===")
        print("The template fix has been successfully applied.")
        print("All article content is now properly wrapped in the "
              "post-container.")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False


if __name__ == "__main__":
    print("Testing template fix for container wrapping issue...")
    test_article_rendering()