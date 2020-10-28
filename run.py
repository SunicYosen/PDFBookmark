# -*- coding: utf-8 -*-

'''
Name:     run.py
Intro:    Entry of add bookmark
Author:   Sunic
'''

import os
from src.add_bookmark_wrapper import add_bookmark_wrapper
from src.level_dict import get_level_re

def run():
    pdf_file_path = input("Please input PDF file path:")
    if os.path.isfile(pdf_file_path):
        pass
    else:
        print("[-]: Error input PDF file path.")
        return
    
    bookmark_file = input("Please input Bookmark file path:")
    if os.path.isfile(pdf_file_path):
        pass
    else:
        print("[-]: Error input bookmark file path.")
        return

    pages_offset  = int(input("Please input offset number: "))

    level0_example = input("Please input level0 example: ")
    level1_example = input("Please input level1 example: ")
    level2_example = input("Please input level2 example: ")
    level0_re      = get_level_re("level0", level0_example)
    level1_re      = get_level_re("level1", level1_example)
    level2_re      = get_level_re("level2", level2_example)

    bookmark_file_p = open(bookmark_file, 'r')
    bookmark_text   = bookmark_file_p.readlines()
    add_bookmark_wrapper(bookmark_text, pages_offset, pdf_file_path, level0_re, level1_re, level2_re)

if __name__ == '__main__':
    run()
