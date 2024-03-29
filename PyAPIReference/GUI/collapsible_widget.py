import sys
from PyQt5.QtWidgets import QFrame, QWidget, QVBoxLayout, QLabel, QPushButton, QApplication, QMainWindow, QMenu, QAction, QCheckBox, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QCursor

if __name__ == "__main__":
    import collapsible_widget_resources
else:
    import GUI.collapsible_widget_resources

if __name__ == "__main__":
    raise RuntimeError("collapsible_widget.py requires get_widgets_from_layout from extra.py which is outside this folder, you can't run this script as main")
else:
    from extra import get_widgets_from_layout 

VERTICAL_ARROW_PATH = ":/vertical_arrow_collapsible.png"
HORIZONTAL_ARROW_PATH = ":/horizontal_arrow_collapsible.png"


class CollapseButton(QWidget):
    def __init__(self, title: str="", color: str=None, is_collapsed: bool=True, parent: QWidget=None):
        super().__init__(parent=parent)

        self.parent = parent

        self.setLayout(QHBoxLayout())

        self.button = QPushButton(title)
        self.layout().addWidget(self.button)
        self.update_arrow()

        self.setStyleSheet(
        f"""  
        QPushButton {{
            text-align: left; 
            padding: 3px 5px 3px 5px; 
            color: {color};
        }}
        """)

    def update_arrow(self, is_collapsed: bool=True):
        if is_collapsed:
            self.button.setIcon(QIcon(HORIZONTAL_ARROW_PATH))
        elif not is_collapsed:
            self.button.setIcon(QIcon(VERTICAL_ARROW_PATH))


class CheckBoxCollapseButton(CollapseButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.checkbox = QCheckBox()
        self.checkbox.stateChanged.connect(self.checkbox_state_changed)
        self.checkbox.setFixedSize(30, 30)
        self.checkbox.setChecked(True)
        self.checkbox.setToolTip("Include in Markdown?")

        self.layout().addWidget(self.checkbox)

    def checkbox_state_changed(self, state):
        if state == 0: # Means not checked
            self.parent.disable_all_checkboxes()
        elif state == 2: # Means checked
            pass


class CollapsibleWidget(QWidget):
    def __init__(self, 
        THEME, 
        current_theme, 
        title: str=None, 
        color=None, 
        collapse_button: QWidget=CollapseButton, 
        parent: QWidget=None
    ):
        super().__init__(parent=parent)
        
        self.parent = parent

        self.THEME = THEME
        self.current_theme = current_theme
        self.title = title

        self.is_collapsed = True

        if color is None:
            color = self.THEME[self.current_theme]["font_color"]
        
        self.title_frame = collapse_button(title, color, self.is_collapsed, parent=self)
        self.title_frame.button.clicked.connect(self.toggle_collapsed)

        self.title_frame.setContextMenuPolicy(Qt.CustomContextMenu)
        self.title_frame.customContextMenuRequested.connect(self.context_menu)
    
        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)    

        self.layout().addWidget(self.title_frame, Qt.AlignTop)
        self.layout().addWidget(self.init_content())

    def context_menu(self):
        menu = QMenu(self.parent)
        fold_action = QAction("Fold")
        fold_action.triggered.connect(self.collapse)
        
        unfold_action = QAction("Unfold")
        unfold_action.triggered.connect(self.uncollapse)

        fold_all_action = QAction("Fold all")
        fold_all_action.triggered.connect(lambda ignore: self.fold_all())
        
        unfold_all_action = QAction("Unfold all")
        unfold_all_action.triggered.connect(lambda ignore: self.unfold_all())

        # print_tree_action = QAction("Print tree")
        # print_tree_action.triggered.connect(lambda ignore: print(self.tree_to_dict()))
           
        menu.addAction(fold_action)
        menu.addAction(unfold_action)
           
        menu.addAction(fold_all_action)
        menu.addAction(unfold_all_action)

        # menu.addAction(print_tree_action)

        menu.exec_(QCursor.pos())

    def fold_all(self):
        for widget in get_widgets_from_layout(self.content_layout):
            if isinstance(widget, CollapsibleWidget):
                widget.collapse()

    def unfold_all(self):
        for widget in get_widgets_from_layout(self.content_layout):
            if isinstance(widget, CollapsibleWidget):
                widget.uncollapse()

        self.uncollapse()

    def init_content(self):
        self.content = QWidget()
        self.content_layout = QVBoxLayout()

        self.content.setLayout(self.content_layout)
        self.content.setVisible(not self.is_collapsed)

        return self.content

    def addWidget(self, widget: QWidget):
        widget.setContentsMargins(10, 0, 0, 0) # To representate indentation
        self.content_layout.addWidget(widget)
   
    def toggle_collapsed(self):
        self.content.setVisible(self.is_collapsed)
        self.is_collapsed = not self.is_collapsed
        self.title_frame.update_arrow(self.is_collapsed)

    def collapse(self):
        self.is_collapsed = True

        self.content.setVisible(False)
        self.title_frame.update_arrow(self.is_collapsed)

    def uncollapse(self):
        self.is_collapsed = False

        self.content.setVisible(True)
        self.title_frame.update_arrow(self.is_collapsed)

    def disable_all_checkboxes(self):
        """This function will disable all child collapsible objects checkboxes if CollapseButton == CheckBoxCollapseButton
        """

        for widget in get_widgets_from_layout(self.content_layout):
            if isinstance(widget, CollapsibleWidget):
                if isinstance(widget.title_frame, CheckBoxCollapseButton):
                    widget.title_frame.checkbox.setChecked(False)

    def disable_checkbox(self):
        self.title_frame.checkbox.setChecked(False)

    def enable_checkbox(self):
        self.title_frame.checkbox.setChecked(True)

    def tree_to_dict(self, collapsible_widget=None, include_title: bool=True):
        """This will convert the tree of collapsible widgets into a dictionary.
        """
        if collapsible_widget is None:
            collapsible_widget = self
        
        layout = collapsible_widget.content_layout

        content = {}

        collapsible_widgets_with_checkbox_counter = 0
        widgets = get_widgets_from_layout(layout) # widgets on collapsible widgets layout

        for widget in widgets:
            if isinstance(widget, CollapsibleWidget):
                if isinstance(widget.title_frame, CheckBoxCollapseButton):
                    collapsible_widgets_with_checkbox_counter += 1
                    if not widget.title_frame.checkbox.checkState():
                        content[widget.title] = False
                        continue

                    content[widget.title] = self.tree_to_dict(widget, include_title=False)

        
        if collapsible_widgets_with_checkbox_counter == 0 and isinstance(collapsible_widget.title_frame, CheckBoxCollapseButton):
            content = bool(collapsible_widget.title_frame.checkbox.checkState())

        return {self.title: content} if include_title else content

