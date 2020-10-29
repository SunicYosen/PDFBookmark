
from functools import partial

from PyQt5.QtWidgets import QTreeWidget, QMenu, QTreeWidgetItemIterator
from PyQt5.QtCore import pyqtSlot, Qt, QPoint

class MixinContextMenu(object):
    def __init__(self, parents=None):
        self._init_context_menu()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self._base_pos = self.pos()
        self.parents = parents

    def _init_context_menu(self):
        self.context_menu = QMenu()

    @property
    def base_pos(self):
        """
        If this class is inherited by a child widget,
        you should set instance.base_pos = parent.pos()
        """
        if self.parents:
            self._base_pos = QPoint()
            for p in self.parents:
                self._base_pos += p.pos()
        return self._base_pos

    @base_pos.setter
    def base_pos(self, value):
        self._base_pos = value

    def _show_context_menu(self, pos):
        if self.currentItem():
            self.context_menu.exec_(self.viewport().mapToGlobal(pos))

    def add_action(self, name, handler, menu=None):
        menu = menu or self.context_menu
        action = menu.addAction(name)
        action.triggered.connect(handler)

    def add_menu(self, name, menu=None):
        menu = menu or self.context_menu
        child_menu = menu.addMenu(name)
        child_menu.add_action = partial(self.add_action, menu=menu)
        child_menu.add_menu = partial(self.add_menu, menu=menu)
        return child_menu


class TreeWidget(MixinContextMenu):
    def init_connect(self, parents=None):
        super(TreeWidget, self).__init__(parents)
        self.itemPressed.connect(self.close_editor)
        self.itemDoubleClicked.connect(self.item_double_clicked)
        self.add_action('删除', self.item_remove_current)
        self.last_item = None
        self.last_column = None

    # TODO: Fix page num when drop item
    def dropEvent(self, event):
        """
        """
        # self.current_item.setText('')
        super(TreeWidget, self).dropEvent(event)

    @property
    def current_item(self):
        return self.currentItem()

    @property
    def all_items(self):
        it = QTreeWidgetItemIterator(self)
        while it.value():
            yield it.value()
            it += 1

    def _set_all_items(self, items):
        self.clear()
        self.addTopLevelItems(items)

    def expand_all_items(self):
        iterator = QTreeWidgetItemIterator(self)
        while iterator.value():
            item = iterator.value()
            item.setExpanded(True)
            iterator.__iadd__(1)

    def collapses_all_items(self):
        iterator = QTreeWidgetItemIterator(self)
        while iterator.value():
            item = iterator.value()
            item.setExpanded(False)
            iterator.__iadd__(1)

    def set_items(self, items):
        self._set_all_items(items)

    def close_editor(self, *args):
        if None not in (self.last_item, self.last_column):
            self.closePersistentEditor(self.last_item, self.last_column)

    def item_clicked(self, item):
        self.closePersistentEditor(item, self.currentColumn())

    def item_double_clicked(self, item):
        current_column = self.currentColumn()
        if self.last_item == item:
            if self.last_column == current_column:
                self.closePersistentEditor(item, current_column)
                return
            else:
                self.closePersistentEditor(item, self.last_column)

        self.openPersistentEditor(item, current_column)
        self.last_item = item
        self.last_column = current_column

    def remove_item(self, item):
        parent = item.parent()
        if parent:
            parent.removeChild(item)
        else:
            self.takeTopLevelItem(self.indexOfTopLevelItem(item))

    def item_remove_current(self):
        selecteds = self.selectedItems()
        for item in selecteds:
            self.remove_item(item)

    def children(self, item):
        child_items = []
        for i in range(item.childCount()):
            child_item = item.child(i)
            if not hasattr(child_item, '__hash__'):
                child_item.__hash__ = lambda: child_item.id
            child_items.append((child_item, self.children(child_item)))
        return child_items

    def qtree_to_list(self):
        items = []

        for top_index in range(self.topLevelItemCount()):
            item = self.topLevelItem(top_index)
            items.append((item, self.children(item)))

        return items

    def children_to_list(self, children, parent_index):
        children_list = []
        counter       = parent_index

        for child in children:
            counter += 1
            top_item, children_items = child
            children_list.append({'title': top_item.text(0), 'page_num': int(top_item.text(1)), 'parent': parent_index})
            grand_children_list, counter = self.children_to_list(children_items, counter)
            children_list.extend(grand_children_list)

        return children_list, counter

    def tree_to_dict(self):
        qtrees_list = self.qtree_to_list()
        count = 0
        bookmark_dict = {}
        for sub_tree in qtrees_list:
            level0_item, children_items = sub_tree
            bookmark_dict[count] = {'title': level0_item.text(0), 'page_num': int(level0_item.text(1))}

            children_list, counter_temp = self.children_to_list(children_items, count)

            for child_item in children_list:
                count += 1
                bookmark_dict[count] = child_item

            count += 1
        return bookmark_dict

    def save_tree_widget_to_file(self, file_ptr):
        iterator = QTreeWidgetItemIterator(self)
        while iterator.value():
            item = iterator.value()
            item_cols = item.columnCount()
            for i in range(item_cols):
                text = item.text(i)
                if i == item_cols - 1:
                    file_ptr.write(text + '\n')
                else:
                    file_ptr.write(text + " ")
                    
            iterator.__iadd__(1)

    @staticmethod
    def set_page_num(item, num):
        item.setText(1, str(num))

    def from_dict(self, bookmark_dict):
        pass