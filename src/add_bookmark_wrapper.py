'''
Name:     add_bookmark_wrapper.py
Intro:    The wrapper of add_bookmarks
Author:   Sunic
'''
import re
from pdf.bookmark import add_bookmark
from src.bookmark_dict_generator import bookmark_dict_generator

def add_bookmark_wrapper(bookmark_text, pages_offset, pdf_file_path, level0_re=None, level1_re=None, level2_re=None, other=0):
    bookmark_dict = bookmark_dict_generator(bookmark_text, pages_offset, level0_re, level1_re, level2_re, other)
    print(bookmark_dict)
    return add_bookmark(pdf_file_path, bookmark_dict)
