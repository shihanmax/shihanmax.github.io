#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to add 'display' field to all posts based on filename format
"""

import os
import re
import frontmatter
from datetime import datetime

def is_date_based_filename(filename: str) -> bool:
    """Check if filename follows the date format YYYY-MM-DD-xxx.md"""
    return re.match(r'^\d{4}-\d{1,2}-\d{1,2}-', filename) is not None

def add_display_field_to_post(filepath: str):
    """Add display field to a post if it doesn't already exist"""
    try:
        # Load the post
        with open(filepath, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        # Check if display field already exists
        if 'display' in post.metadata:
            print(f"Skipping {filepath} - display field already exists")
            return False
        
        # Determine display value based on filename
        filename = os.path.basename(filepath)
        display_value = is_date_based_filename(filename)
        
        # Add display field
        post.metadata['display'] = display_value
        
        # Write back to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        
        print(f"Added display: {display_value} to {filepath}")
        return True
        
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def process_posts_directory(posts_dir: str):
    """Process all markdown files in the posts directory"""
    if not os.path.exists(posts_dir):
        print(f"Directory does not exist: {posts_dir}")
        return
    
    processed_count = 0
    error_count = 0
    
    # Process files in the main directory
    for filename in os.listdir(posts_dir):
        if filename.endswith('.md') and not filename.startswith('.'):
            filepath = os.path.join(posts_dir, filename)
            if add_display_field_to_post(filepath):
                processed_count += 1
            else:
                error_count += 1
    
    # Process files in subdirectories (like pack/)
    for root, dirs, files in os.walk(posts_dir):
        for dirname in dirs:
            if not dirname.startswith('.'):
                subdir_path = os.path.join(root, dirname)
                for filename in os.listdir(subdir_path):
                    if filename.endswith('.md') and not filename.startswith('.'):
                        filepath = os.path.join(subdir_path, filename)
                        if add_display_field_to_post(filepath):
                            processed_count += 1
                        else:
                            error_count += 1
    
    print(f"\nProcessing complete:")
    print(f"- Processed: {processed_count} files")
    print(f"- Errors: {error_count} files")

if __name__ == '__main__':
    # Get the blog root directory
    blog_root = os.path.dirname(os.path.abspath(__file__))
    posts_dir = os.path.join(blog_root, '_posts')
    
    print(f"Processing posts in: {posts_dir}")
    process_posts_directory(posts_dir)