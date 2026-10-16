import sys

from PyQt6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QRadioButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


PRIORITIES = ["Low", "Medium", "High"]
DEFAULT_PRIORITY = "Medium"


class TaskManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Task Manager")
        self.resize(520, 640)

        # Все созданные задачи хранятся в обычном списке
        self.tasks = []

        self.create_widgets()
        self.create_layouts()
        self.connect_signals()

        self.clear_form()

    def create_widgets(self):
        self.title_label = QLabel("Task")
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Название задачи")

        self.description_label = QLabel("Description")
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Описание задачи")
        self.description_input.setFixedHeight(100)

        # Радиокнопки: можно выбрать только один приоритет
        self.priority_buttons = {}
        self.priority_group = QButtonGroup(self)

        for priority in PRIORITIES:
            button = QRadioButton(priority)
            self.priority_buttons[priority] = button
            self.priority_group.addButton(button)

        # Чекбоксы: настройки не зависят друг от друга
        self.important_checkbox = QCheckBox("Important")
        self.notification_checkbox = QCheckBox("Send notification")
        self.favorite_checkbox = QCheckBox("Add to favorites")

        self.create_button = QPushButton("Create task")
        self.clear_button = QPushButton("Clear")
        self.delete_last_button = QPushButton("Delete last task")

        self.filter_label = QLabel("Filter")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All"] + PRIORITIES)

        self.tasks_output = QTextEdit()
        self.tasks_output.setReadOnly(True)

        self.counter_label = QLabel()
        self.status_label = QLabel()

    def create_layouts(self):
        # QMainWindow сам управляет своей структурой, поэтому layout
        # ставим не на окно, а на центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Название и описание удобно выровнять сеткой
        form_layout = QGridLayout()
        form_layout.addWidget(self.title_label, 0, 0)
        form_layout.addWidget(self.title_input, 0, 1)
        form_layout.addWidget(self.description_label, 1, 0)
        form_layout.addWidget(self.description_input, 1, 1)
        main_layout.addLayout(form_layout)

        priority_box = QGroupBox("Priority")
        priority_layout = QHBoxLayout()
        for priority in PRIORITIES:
            priority_layout.addWidget(self.priority_buttons[priority])
        priority_box.setLayout(priority_layout)
        main_layout.addWidget(priority_box)

        options_box = QGroupBox("Options")
        options_layout = QVBoxLayout()
        options_layout.addWidget(self.important_checkbox)
        options_layout.addWidget(self.notification_checkbox)
        options_layout.addWidget(self.favorite_checkbox)
        options_box.setLayout(options_layout)
        main_layout.addWidget(options_box)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.create_button)
        buttons_layout.addWidget(self.clear_button)
        buttons_layout.addWidget(self.delete_last_button)
        main_layout.addLayout(buttons_layout)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(self.filter_label)
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addStretch()
        main_layout.addLayout(filter_layout)

        main_layout.addWidget(self.tasks_output)
        main_layout.addWidget(self.counter_label)
        main_layout.addWidget(self.status_label)

    def connect_signals(self):
        self.create_button.clicked.connect(self.create_task)
        self.clear_button.clicked.connect(self.clear_form)
        self.delete_last_button.clicked.connect(self.delete_last_task)
        self.filter_combo.currentTextChanged.connect(self.show_tasks)

    def get_selected_priority(self):
        for priority, button in self.priority_buttons.items():
            if button.isChecked():
                return priority

        return DEFAULT_PRIORITY

    def create_task(self):
        title = self.title_input.text().strip()

        if not title:
            self.set_status("Enter task title")
            return

        task = {
            "title": title,
            "description": self.description_input.toPlainText().strip(),
            "priority": self.get_selected_priority(),
            "important": self.important_checkbox.isChecked(),
            "notification": self.notification_checkbox.isChecked(),
            "favorite": self.favorite_checkbox.isChecked(),
        }

        self.tasks.append(task)

        print("Task created:")
        print(self.format_task(task))
        print()

        self.clear_form()
        self.show_tasks()
        self.set_status("Task created")

    def delete_last_task(self):
        if not self.tasks:
            self.set_status("No tasks to delete")
            return

        self.tasks.pop()

        self.show_tasks()
        self.set_status("Last task deleted")

    def clear_form(self):
        self.title_input.clear()
        self.description_input.clear()
        self.priority_buttons[DEFAULT_PRIORITY].setChecked(True)
        self.important_checkbox.setChecked(False)
        self.notification_checkbox.setChecked(False)
        self.favorite_checkbox.setChecked(False)

        self.title_input.setFocus()
        self.set_status("Ready")
        self.show_tasks()

    def format_task(self, task):
        options = []

        if task["important"]:
            options.append("Important")
        if task["notification"]:
            options.append("Send notification")
        if task["favorite"]:
            options.append("Add to favorites")

        lines = [
            f"Title: {task['title']}",
            f"Description: {task['description'] or '-'}",
            f"Priority: {task['priority']}",
            f"Options: {', '.join(options) if options else '-'}",
        ]

        return "\n".join(lines)

    def show_tasks(self):
        selected_filter = self.filter_combo.currentText()

        blocks = []

        for number, task in enumerate(self.tasks, start=1):
            if selected_filter != "All" and task["priority"] != selected_filter:
                continue

            blocks.append(f"#{number}\n{self.format_task(task)}")

        self.tasks_output.setPlainText("\n\n".join(blocks))
        self.counter_label.setText(f"Created tasks: {len(self.tasks)}")

    def set_status(self, text):
        self.status_label.setText(f"Status: {text}")


def main():
    app = QApplication(sys.argv)

    window = TaskManagerWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
