import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog, QTextEdit, QScrollArea, QLineEdit, QStackedWidget, QMainWindow, QFrame
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
from backend_fixed import set_textbook_path, ChatBot, generate_reading_comprehension, grade_reading_comprehension_question, generate_cards, generate_fill_in_blanks, grade_fill_in_blank_question, textbookPath

class MainPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Navigation buttons at the top
        nav_layout = QHBoxLayout()
        nav_buttons = ['ChatBot', 'Reading', 'Flashcards', 'Fill it in']
        for btn_text in nav_buttons:
            btn = QPushButton(btn_text)
            btn.clicked.connect(lambda checked, text=btn_text: self.navigate(text))
            nav_layout.addWidget(btn)
        layout.addLayout(nav_layout)

        # Logo
        logo_label = QLabel()
        pixmap = QPixmap("logo-transparent.png")
        logo_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        layout.addWidget(logo_label, alignment=Qt.AlignCenter)

        # Upload Textbook button and path label
        upload_frame = QFrame()
        upload_layout = QVBoxLayout(upload_frame)
        upload_btn = QPushButton('Upload Textbook')
        upload_btn.clicked.connect(self.upload_textbook)
        upload_layout.addWidget(upload_btn)

        self.textbook_path_label = QLabel(self.get_textbook_path())
        self.textbook_path_label.setFixedHeight(20)
        upload_layout.addWidget(self.textbook_path_label)
        upload_layout.setAlignment(Qt.AlignBottom)
        
        layout.addWidget(upload_frame)

        # Add stretch to push content to the top
        layout.addStretch(1)

        self.setLayout(layout)

    def upload_textbook(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Textbook PDF", "", "PDF Files (*.pdf)")
        if file_path:
            set_textbook_path(file_path)
            self.textbook_path_label.setText(self.get_textbook_path())

    def get_textbook_path(self):
        return f"Textbook: {os.path.basename(textbookPath)}" if textbookPath else "No textbook uploaded"

    def navigate(self, page):
        index = ['ChatBot', 'Reading', 'Flashcards', 'Fill it in'].index(page) + 1
        self.stacked_widget.setCurrentIndex(index)

class BasePage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget

    def create_back_button(self):
        back_btn = QPushButton()
        back_btn.setIcon(QIcon.fromTheme("go-previous"))
        back_btn.setFixedSize(32, 32)
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        return back_btn

    def add_back_button(self, layout):
        back_btn = self.create_back_button()
        layout.addWidget(back_btn, alignment=Qt.AlignTop | Qt.AlignLeft)

class ChatBotPage(BasePage):
    def __init__(self, stacked_widget):
        super().__init__(stacked_widget)
        self.chatbot = ChatBot()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.add_back_button(layout)

        # Message history
        self.history_area = QTextEdit()
        self.history_area.setReadOnly(True)
        layout.addWidget(self.history_area)

        # User input
        input_layout = QHBoxLayout()
        self.input_box = QLineEdit()
        send_btn = QPushButton('Send')
        send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.input_box)
        input_layout.addWidget(send_btn)

        layout.addLayout(input_layout)
        self.setLayout(layout)

    def send_message(self):
        user_message = self.input_box.text()
        self.history_area.append(f"You: {user_message}")
        response = self.chatbot.message(user_message)
        self.history_area.append(f"AI: {response}")
        self.input_box.clear()

class ReadingPage(BasePage):
    def __init__(self, stacked_widget):
        super().__init__(stacked_widget)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.add_back_button(layout)

        # Generate button
        generate_btn = QPushButton('Generate Question')
        generate_btn.clicked.connect(self.generate_questions)
        layout.addWidget(generate_btn)

        # Story text box
        self.story_box = QTextEdit()
        self.story_box.setReadOnly(True)
        self.story_box.setLineWrapMode(QTextEdit.WidgetWidth)
        layout.addWidget(self.story_box)

        # Questions
        self.questions = []
        for _ in range(3):
            q_layout = QVBoxLayout()
            question_label = QLabel()
            question_label.setWordWrap(True)
            answer_box = QLineEdit()
            submit_btn = QPushButton('Submit')
            q_layout.addWidget(question_label)
            q_layout.addWidget(answer_box)
            q_layout.addWidget(submit_btn)
            layout.addLayout(q_layout)
            self.questions.append((question_label, answer_box, submit_btn))

        self.setLayout(layout)

    def generate_questions(self):
        story, q1, q2, q3 = generate_reading_comprehension()
        self.story_box.setText(story)
        for (label, answer_box, submit_btn), question in zip(self.questions, [q1, q2, q3]):
            label.setText(question)
            answer_box.clear()
            answer_box.setEnabled(True)
            answer_box.setStyleSheet("")
            submit_btn.clicked.connect(lambda checked, l=label, a=answer_box, q=question: self.check_answer(l, a, q))

    def check_answer(self, label, answer_box, question):
        user_answer = answer_box.text()
        if grade_reading_comprehension_question(self.story_box.toPlainText(), question, user_answer):
            answer_box.setStyleSheet("background-color: lightgreen;")
            answer_box.setEnabled(False)
        else:
            answer_box.setStyleSheet("background-color: lightcoral;")

class FlashcardsPage(BasePage):
    def __init__(self, stacked_widget):
        super().__init__(stacked_widget)
        self.flashcards = []
        self.current_index = 0
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.add_back_button(layout)

        # Flashcard panel
        self.flashcard_panel = QLabel()
        self.flashcard_panel.setAlignment(Qt.AlignCenter)
        self.flashcard_panel.setStyleSheet("border: 2px solid black; padding: 20px;")
        self.flashcard_panel.setWordWrap(True)
        self.flashcard_panel.mousePressEvent = self.flip_card
        layout.addWidget(self.flashcard_panel)

        # Navigation buttons
        nav_layout = QHBoxLayout()
        prev_btn = QPushButton('Previous')
        next_btn = QPushButton('Next')
        prev_btn.clicked.connect(self.prev_card)
        next_btn.clicked.connect(self.next_card)
        nav_layout.addWidget(prev_btn)
        nav_layout.addWidget(next_btn)
        layout.addLayout(nav_layout)

        # Generate button
        generate_btn = QPushButton('Generate Flashcards')
        generate_btn.clicked.connect(self.generate_flashcards)
        layout.addWidget(generate_btn)

        self.setLayout(layout)

    def generate_flashcards(self):
        self.flashcards = generate_cards(10)  # Generate 10 flashcards
        self.current_index = 0
        self.update_flashcard()

    def update_flashcard(self):
        if self.flashcards:
            card = self.flashcards[self.current_index]
            self.flashcard_panel.setText(card['English'])

    def flip_card(self, event):
        if self.flashcards:
            card = self.flashcards[self.current_index]
            current_text = self.flashcard_panel.text()
            self.flashcard_panel.setText(card['Foreign'] if current_text == card['English'] else card['English'])

    def prev_card(self):
        if self.flashcards:
            self.current_index = (self.current_index - 1) % len(self.flashcards)
            self.update_flashcard()

    def next_card(self):
        if self.flashcards:
            self.current_index = (self.current_index + 1) % len(self.flashcards)
            self.update_flashcard()

class FillInPage(BasePage):
    def __init__(self, stacked_widget):
        super().__init__(stacked_widget)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.add_back_button(layout)

        # Generate button
        generate_btn = QPushButton('Generate Questions')
        generate_btn.clicked.connect(self.generate_questions)
        layout.addWidget(generate_btn)

        # Questions
        self.questions = []
        for _ in range(3):
            q_layout = QVBoxLayout()
            sentence_label = QLabel()
            sentence_label.setWordWrap(True)
            answer_box = QLineEdit()
            submit_btn = QPushButton('Submit')
            q_layout.addWidget(sentence_label)
            q_layout.addWidget(answer_box)
            q_layout.addWidget(submit_btn)
            layout.addLayout(q_layout)
            self.questions.append((sentence_label, answer_box, submit_btn))

        self.setLayout(layout)

    def generate_questions(self):
        sentences = generate_fill_in_blanks(3)
        for (label, answer_box, submit_btn), sentence in zip(self.questions, sentences):
            label.setText(sentence)
            answer_box.clear()
            answer_box.setEnabled(True)
            answer_box.setStyleSheet("")
            submit_btn.clicked.connect(lambda checked, l=label, a=answer_box, s=sentence: self.check_answer(l, a, s))

    def check_answer(self, label, answer_box, sentence):
        user_answer = answer_box.text()
        if grade_fill_in_blank_question(sentence, user_answer):
            answer_box.setStyleSheet("background-color: lightgreen;")
            answer_box.setEnabled(False)
        else:
            answer_box.setStyleSheet("background-color: lightcoral;")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Lexiloom')
        self.setGeometry(100, 100, 800, 600)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Create and add pages
        main_page = MainPage(self.stacked_widget)
        chatbot_page = ChatBotPage(self.stacked_widget)
        reading_page = ReadingPage(self.stacked_widget)
        flashcards_page = FlashcardsPage(self.stacked_widget)
        fill_in_page = FillInPage(self.stacked_widget)

        self.stacked_widget.addWidget(main_page)
        self.stacked_widget.addWidget(chatbot_page)
        self.stacked_widget.addWidget(reading_page)
        self.stacked_widget.addWidget(flashcards_page)
        self.stacked_widget.addWidget(fill_in_page)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())