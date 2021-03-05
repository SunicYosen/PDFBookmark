# -*- coding: utf-8 -*-

"""
Add directory bookmarks to the pdf file.

Public:

- function: add_bookmark(path, bookmark_dict)

"""

from .pdf import PDF

def _add_bookmark(pdf, bookmark_dict):

    if not bookmark_dict:
        return None

    bookmark_num = max(bookmark_dict.keys())

    parent_dict  = {}
    max_page_num = pdf.writer.getNumPages() - 1

    for bookmark_index in range(bookmark_num + 1):
        value        = bookmark_dict[bookmark_index]
        title        = value.get('title', '')
        page_num     = min(value.get('page_num', 1) - 1, max_page_num)
        parent       = parent_dict.get(value.get('parent'))
        
        bookmark_ref = pdf.add_bookmark(title    = title,
                                        page_num = page_num,
                                        parent   = parent)

        parent_dict[bookmark_index] = bookmark_ref


def add_bookmark(pdf_path, bookmark_dict):
    """
    Add directory bookmarks to the pdf file.
        :param pdf_path: pdf file path.
        :param bookmark_dict: bookmarks dict, like {0:{'title':'A', 'page_num':1}, 1:{'title':'B', page_num:2, parent: 0} ......}
    """

    pdf = PDF(pdf_path)
    _add_bookmark(pdf, bookmark_dict)

    return pdf.save_pdf()

