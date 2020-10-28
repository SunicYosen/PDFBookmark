# -*- coding: utf-8 -*-

"""
Convert a Bookmark text or list to bookmark index dict
"""

import re

def split_page_num(bookmark):
    """
    split between title and page number
    """
    bookmark = bookmark.strip()
    bookmark_list = re.split(r'([-]?\d*$)', bookmark)

    if len(bookmark_list) > 1:
        return bookmark_list[0].rstrip(' .-'), int(bookmark_list[1] or 0)
    
    return bookmark_list[0], 0

def text_to_list(text):
    if  type(text) == list:
        return text
    else:
        return text.split('\n')

def is_in(title, level_exp):
    return bool(re.match(level_exp, title)) if level_exp else False

def check_level(title, level0_re, level1_re, level2_re, other=0):
    """
    Check the level of this title.
    """

    if is_in(title, level2_re):
        return 2

    elif is_in(title, level1_re):
        return 1

    elif is_in(title, level0_re):
        return 0

    return other

def _bookmark_dict_generator(bookmark_text, pages_offset=0, level0_re=None, level1_re=None, level2_re=None, other=0):
    current_level0 = None
    current_level1 = None
    page_num       = 0
    bookmark_dict  = {}

    bookmark_list  = text_to_list(bookmark_text)

    for index, bookmark in enumerate(bookmark_list):
        title, num = split_page_num(bookmark)

        page_num_temp = num + pages_offset - 1

        if page_num_temp > page_num:
            page_num = page_num_temp

        bookmark_dict[index] = {'title': title, 'page_num': page_num}

        level = check_level(title, level0_re, level1_re, level2_re, other)

        if level == 2:
            bookmark_dict[index]['parent'] = current_level1

        elif level == 1:
            bookmark_dict[index]['parent'] = current_level0
            current_level1 = index

        elif level == 0:
            current_level0 = index

    return bookmark_dict

def bookmark_dict_generator(bookmark_text, pages_offset=0, level0_re=None, level1_re=None, level2_re=None, other=0):
    """
    convert bookmark text to dict.
        :param: bookmark_text: unicode, the directory text, usually copy from a bookstore like amazon.
        :param: pages_offset: int, the offset of this book.
        :param: level0_re: unicode, the expression to find level0 title.
        :param: level1_re: unicode, the expression to find level1 title.
        :param: level2_re: unicode, the expression to find level2 title.
        :param: other    : int(0-2), three level can't match title, then this is the level.
        :return: the dict of directory, like {0:{'title':'A', 'page_num':1}, 1:{'title':'B', page_num:2, parent: 0} ......}
    """
    return _bookmark_dict_generator(bookmark_text, pages_offset, level0_re, level1_re, level2_re, other)
