# -*- coding: utf-8 -*-

"""
The add bookmark api for a pdf file.

public:
- class: Pdf(path)
"""

import os
from typing import Iterator
from PyPDF4 import PdfFileWriter, PdfFileReader, utils

class PDF(object):
    """
    Add bookmarks to a pdf file.

    Usage:

    >>> from pdf import PDF

    # read a exist pdf file:
    >>> p = PDF('/home/sun/test.pdf')

    # add a bookmark:
    >>> b0 = p.add_bookmark('First bookmark', 1)

    # add a child bookmark to b0:
    >>> p.add_bookmark('Child bookmark', 2, parent=b0)

    # save pdf:
    >>> p.save_pdf()

    # the new pdf file will save to save directory with '1_new.pdf'

    """
    def __init__(self, path, path_new=None):
        self.path     = path
        self.path_new = path_new

        self.reader       = PdfFileReader(open(path, "rb"), strict=False)
        self.org_outlines = self.reader.getOutlines()

        self.writer       = PdfFileWriter()
        self.writer.appendPagesFromReader(self.reader)
        self.writer.addMetadata({k: v for k, v in self.reader.getDocumentInfo().items()
                                 if isinstance(v, (utils.string_type, utils.bytes_type))})

    @property
    def _new_path(self):
        if self.path_new:
            return self.path_new
        else:
            name, ext     = os.path.splitext(self.path)
            self.path_new = name + '_new' + ext
            return self.path_new

    def add_bookmark(self, title, page_num, parent=None, color=None, bold=False, italic=False, fit='/Fit', *args):
        """
        Add a bookmark to pdf file with title and page num.
        If it's a child bookmark, add a parent argument.

        :Args

        title:    str, the bookmark title.
        page_num: int, the page num this bookmark refer to.
        parent:   IndirectObject(the addBookmark() return object), the parent of this bookmark, the default is None.
        color:    param tuple color: Color of the bookmark as a red, green, blue tuple from 0.0 to 1.0
        bold:     param bool bold: Bookmark is bold
        italic:   param bool italic: Bookmark is italic
        fit:      param str fit: The fit of the destination page.
                '/Fit'	    No additional arguments, Default
                '/XYZ'	    [left] [top] [zoomFactor]
                '/FitH'	    [top]
                '/FitV'	    [left]
                '/FitR'	    [left] [bottom] [right] [top]
                '/FitB'	    No additional arguments
                '/FitBH'	[top]
                '/FitBV'	[left]
        """
        return self.writer.addBookmark(title, page_num, parent=parent, color=color, bold=bold, italic=italic, fit=fit, *args)

    def save_pdf(self):
        """
         save the writer to a pdf file with name 'name_new.pdf' 
        """
        
        if os.path.exists(self._new_path):
            os.remove(self._new_path)

        with open(self._new_path, 'wb') as out:
            self.writer.write(out)

        return self._new_path
