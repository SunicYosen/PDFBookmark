# -*- coding: utf-8 -*-

"""
The main GUI model of project.
"""
import os
import sys
import webbrowser

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QErrorMessage

from gui.main_ui import Ui_PDFBookMark
from gui.tree_widget import TreeWidget
from pdf.bookmark import add_bookmark
from src.level_dict import level_dict
from src.bookmark_dict_generator import text_to_list, split_page_num, check_level
from src.level_dict import get_level_re

def dynamic_base_class(instance, cls_name, new_class, **kwargs):
    instance.__class__ = type(cls_name, (new_class, instance.__class__), kwargs)
    return instance

class WindowDragMixin(object):
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_drag = True
            self.m_DragPosition = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, QMouseEvent):
        if QMouseEvent.buttons() and Qt.LeftButton:
            self.move(QMouseEvent.globalPos() - self.m_DragPosition)
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_drag = False


class ControlButtonMixin(object):
    def set_control_button(self, min_button, exit_button):
        min_button.clicked.connect(self.showMinimized)
        exit_button.clicked.connect(self.close)


class MainWindow(QtWidgets.QMainWindow, Ui_PDFBookMark, ControlButtonMixin):
    def __init__(self, app, trans):
        super(MainWindow, self).__init__()
        self.app = app
        self.trans = trans
        self.setupUi(self)
        self.version = 'v1.0'
        self.setWindowTitle(u'PDF Bookmark %s' % self.version)
        self.setWindowIcon(QtGui.QIcon('icons/bookmark.svg'))
        self.error_message = QErrorMessage()
        self.bookmark_tree_widget = dynamic_base_class(self.bookmark_tree_widget, 'TreeWidget', TreeWidget)
        self.bookmark_tree_widget.init_connect(parents=[self, self.bookmark_tree_widget])
        self.add_page_num_box.setMinimum(-1000)
        self._set_connect()
        self._set_action()
        self._set_level_edit_unwritable()

    def _set_connect(self):
        self.open_button.clicked.connect(self.open_pdf_file_dialog)
        self.bookmark_open_button.clicked.connect(self.open_bookmark_file_dialog)
        self.export_button.clicked.connect(self.write_tree_to_pdf)
        self.refresh_bt.clicked.connect(self.refresh_tree_widget)
        self.open_bt.clicked.connect(self.expand_tree_widget)
        self.close_bt.clicked.connect(self.collapses_tree_widget)
        self.bookmark_save_bt.clicked.connect(self.save_bookmark)
        self.bookmark_text_edit.textChanged.connect(self.to_tree_widget)

        self.level0_box.clicked.connect(self._change_level0_writable)
        self.level1_box.clicked.connect(self._change_level1_writable)
        self.level2_box.clicked.connect(self._change_level2_writable)

        self.add_page_num_to_selected_button.clicked.connect(self._add_selected_page_num)
        self.add_page_num_to_all_button.clicked.connect(self._add_all_page_num)

    def _set_action(self):
        self.home_page_action.triggered.connect(self._open_home_page)
        self.help_action.triggered.connect(self._open_help_page)
        self.english_action.triggered.connect(self.to_english)
        self.chinese_action.triggered.connect(self.to_chinese)

    def _set_level_edit_unwritable(self):
        self.level0_edit.setEnabled(False)
        self.level1_edit.setEnabled(False)
        self.level2_edit.setEnabled(False)

    def _level_button_clicked(self, level_str):
        context_menu = QtWidgets.QMenu()
        for k, v in level_dict.get(level_str).items():
            context_menu.addAction(k, lambda v=v: self._insert_to_editor(level_str, v))
        context_menu.exec_(QtGui.QCursor.pos())

    def _insert_to_editor(self, level_str, text):
        editor = getattr(self, level_str + '_edit')
        if editor.isEnabled():
            editor.insert(text)

    def _change_level0_writable(self):
        self.level0_edit.setEnabled(True if self.level0_box.isChecked() else False)

    def _change_level1_writable(self):
        self.level1_edit.setEnabled(True if self.level1_box.isChecked() else False)

    def _change_level2_writable(self):
        self.level2_edit.setEnabled(True if self.level2_box.isChecked() else False)

    def _add_page_num_to_item(self, item):
        current_num = int(item.text(1))
        add_num = self.add_page_num_box.value()
        self.bookmark_tree_widget.set_page_num(item, max(current_num + add_num, 0))

    def _add_selected_page_num(self):
        selected_items = self.bookmark_tree_widget.selectedItems()
        for item in selected_items:
            self._add_page_num_to_item(item)

    def _add_all_page_num(self):
        for item in self.bookmark_tree_widget.all_items:
            self._add_page_num_to_item(item)

    @staticmethod
    def _open_home_page():
        webbrowser.open('https://github.com/sunicyosen', new=1)

    @staticmethod
    def _open_help_page():
        webbrowser.open('https://github.com/sunicyosen', new=1)

    def to_english(self):
        self.trans.load("./language/en")
        self.app.installTranslator(self.trans)
        self.retranslateUi(self)

    def to_chinese(self):
        self.app.removeTranslator(self.trans)
        self.retranslateUi(self)

    def _get_args(self):
        self.pdf_file_path      = self.pdf_path_edit.text()
        self.bookmark_file_path = self.bookmark_path_edit.text()
        self.offset         = int(self.add_page_num_box.value())
        self.bookmark_text  = self.bookmark_text_edit.toPlainText()
        self.level0_example = self.level0_edit.text() if self.level0_box.isChecked() else None
        self.level1_example = self.level1_edit.text() if self.level1_box.isChecked() else None
        self.level2_example = self.level2_edit.text() if self.level2_box.isChecked() else None
        self.level0_re      = get_level_re('level0', self.level0_example)
        self.level1_re      = get_level_re('level1', self.level1_example)
        self.level2_re      = get_level_re('level2', self.level2_example)

    @property
    def pdf_path(self):
        return self.pdf_path_edit.text()

    def open_pdf_file_dialog(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, u'Select PDF File', filter="PDF (*.pdf)")
        self.pdf_path_edit.setText(filename)

    def open_bookmark_file_dialog(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, u'Select Bookmark File')
        self.bookmark_path_edit.setText(filename)
        self.set_bookmark_text_edit_text_by_file(filename)
    
    def set_bookmark_text_edit_text_by_file(self, filename):
        if os.path.isfile(filename):
            bookmark_file = open(filename, 'r', encoding='utf-8')
            bookmark_text = bookmark_file.read()
            self.bookmark_text_edit.setPlainText(bookmark_text)
            bookmark_file.close()
        else:
            self.statusbar.showMessage(u"[-]: %s Bookmark file doesn't exists" % self.pdf_path, 3000)

    def tree_to_dict(self):
        return self.bookmark_tree_widget.tree_to_dict()

    def refresh_tree_widget(self):
        self.to_tree_widget()

    def expand_tree_widget(self):
        self.bookmark_tree_widget.expand_all_items()

    def collapses_tree_widget(self):
        self.bookmark_tree_widget.collapses_all_items()

    def save_bookmark(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, u'Select A New File to Save Bookmark')
        if os.path.isfile(filename):
            bookmark_file = open(filename, 'w+')
            self.bookmark_tree_widget.save_tree_widget_to_file(bookmark_file)
            bookmark_file.close()
            self.statusbar.showMessage(u"[+]: %s Bookmark Write Finished！" % filename, 3000)

        else:
            self.statusbar.showMessage(u"[-]: %s file does not exists！" % filename, 3000)

    def to_tree_widget(self):
        self.bookmark_tree_widget.clear()
        self._get_args()
        bookmark_list = text_to_list(self.bookmark_text)

        last_num = 0
        level0_parent_item = None
        level1_parent_item = None

        for book_mark in bookmark_list:
            title, num = split_page_num(book_mark)
            bm_level   = check_level(title, self.level0_re, self.level1_re, self.level2_re)
            page_num   = num + self.offset - 1
            page_num   = max(page_num, last_num)
            last_num   = page_num

            if bm_level == 2:
                qtree_item = QtWidgets.QTreeWidgetItem([str(title), str(page_num)])
                level1_parent_item.addChild(qtree_item)

            elif bm_level == 1:
                qtree_item = QtWidgets.QTreeWidgetItem([str(title), str(page_num)])
                level0_parent_item.addChild(qtree_item)
                level1_parent_item = qtree_item

            else:
                qtree_item = QtWidgets.QTreeWidgetItem([str(title), str(page_num)])
                self.bookmark_tree_widget.addTopLevelItem(qtree_item)
                level0_parent_item = qtree_item

    def write_tree_to_pdf(self):
        if os.path.isfile(self.pdf_path):
            try:
                new_path = self.dict_to_pdf(self.pdf_path, self.tree_to_dict())
                self.statusbar.showMessage(u"[+]: %s Finished！" % new_path, 3000)
            except PermissionError:
                self.error_message.showMessage(u"[-]: Permission denied！")
        else:
            self.statusbar.showMessage(u"[-]: %s PDF file doesn't exists" % self.pdf_path, 3000)

    @staticmethod
    def dict_to_pdf(pdf_path, index_dict):
        return add_bookmark(pdf_path, index_dict)

def run():
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QtWidgets.QApplication(sys.argv)
    trans = QtCore.QTranslator()
    app.installTranslator(trans)
    window = MainWindow(app, trans)
    window.show()
    sys.exit(app.exec_())

sys._excepthook = sys.excepthook

def exception_hook(exctype, value, traceback):
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)
sys.excepthook = exception_hook

if __name__ == '__main__':
    run()