import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QFileDialog, QTextEdit, QLineEdit, QStackedWidget, QSizePolicy, QSpinBox, QFrame)
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap
from PyQt5.QtCore import Qt
from backend import setTextBookPath, generateCards, selectStory, translateCards, readingComprehension, gradeReadingComprehension, chatbot, generatefillBlank, gradeFillBlank

# Define fonts
TITLE_FONT = QFont("Roboto", 24, QFont.Bold)
BUTTON_FONT = QFont("Roboto", 12)
TEXT_FONT = QFont("Roboto", 11)
FLASHCARD_FONT = QFont("Roboto", 18)
TEXTBOOK = ""

# Define colors
PRIMARY_COLOR = "#5D3FD3"  # Blue-purple shade
SECONDARY_COLOR = "#5c3f78"  # Light lavender
TEXT_COLOR = "#000000"  # Dark gray
BACKGROUND_COLOR = "#FFFFFF"  # White

class LexiLoom(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LexiLoom")
        self.setGeometry(100, 100, 800, 600)
        self.setFixedSize(800, 600)
        self.setup_ui()

    def setup_ui(self):
        # Set up theme
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {BACKGROUND_COLOR};
            }}
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {QColor(PRIMARY_COLOR).lighter(110).name()};
            }}
            QLabel, QTextEdit, QLineEdit {{
                color: {TEXT_COLOR};
            }}
            QTextEdit, QLineEdit {{
                border: 1px solid {PRIMARY_COLOR};
                border-radius: 5px;
                padding: 5px;
            }}
        """)

        # Main layout
        main_layout = QVBoxLayout()

        # Logo
        logo = QLabel()
        pixmap = QPixmap("logo-transparent.png")
        desired_width = 300
        desired_height = 300
        scaled_pixmap = pixmap.scaled(desired_width, desired_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo.setPixmap(scaled_pixmap)
        logo.setAlignment(Qt.AlignCenter)
        logo.setFixedSize(desired_width, desired_height)

        logo_layout = QHBoxLayout()
        logo_layout.addStretch()
        logo_layout.addWidget(logo)
        logo_layout.addStretch()

        main_layout.addLayout(logo_layout)

        # File input button
        self.file_button = QPushButton("Upload Linguistics File (.pdf)")
        self.file_button.setFont(BUTTON_FONT)
        self.file_button.clicked.connect(self.upload_file)
        main_layout.addWidget(self.file_button)

        # Function buttons
        button_layout = QHBoxLayout()
        self.chatbot_button = QPushButton("Assistance Chatbot")
        self.flashcard_button = QPushButton("Flashcards")
        self.fill_blank_button = QPushButton("Fill in the Blank")
        self.reading_comp_button = QPushButton("Reading Comprehension")

        for button in [self.chatbot_button, self.flashcard_button, self.fill_blank_button, self.reading_comp_button]:
            button.setFont(BUTTON_FONT)
            button.setEnabled(False)
            button_layout.addWidget(button)

        main_layout.addLayout(button_layout)

        # Create stacked widget for different pages
        self.stacked_widget = QStackedWidget()
        
        # Create pages
        self.main_page = QWidget()
        self.main_page.setLayout(main_layout)
        self.chatbot_page = ChatbotWidget()
        self.flashcard_page = FlashcardWidget()
        self.fill_blank_page = FillBlankWidget()
        self.reading_comp_page = ReadingCompWidget()

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.main_page)
        self.stacked_widget.addWidget(self.chatbot_page)
        self.stacked_widget.addWidget(self.flashcard_page)
        self.stacked_widget.addWidget(self.fill_blank_page)
        self.stacked_widget.addWidget(self.reading_comp_page)

        # Set central widget
        self.setCentralWidget(self.stacked_widget)

        # Connect buttons
        self.chatbot_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.chatbot_page))
        self.flashcard_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.flashcard_page))
        self.fill_blank_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.fill_blank_page))
        self.reading_comp_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.reading_comp_page))

        # Add return buttons to each page
        for page in [self.chatbot_page, self.flashcard_page, self.fill_blank_page, self.reading_comp_page]:
            return_button = QPushButton("Return to Main Menu")
            return_button.setFont(BUTTON_FONT)
            return_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.main_page))
            page.layout().addWidget(return_button)

    def upload_file(self):
        global TEXTBOOK
        file_name, _ = QFileDialog.getOpenFileName(self, "Open PDF File", "", "PDF Files (*.pdf)")
        if file_name:
            print(f"File uploaded: {file_name}")
            # Here you would process the PDF file
            TEXTBOOK = setTextBookPath(file_name)
            for button in [self.chatbot_button, self.flashcard_button, self.fill_blank_button, self.reading_comp_button]:
                button.setEnabled(True)

class ChatbotWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        self.input_field = QLineEdit()
        self.input_field.returnPressed.connect(self.send_message)
        layout.addWidget(self.input_field)

        self.setLayout(layout)

    def send_message(self):
        user_message = self.input_field.text()
        self.chat_display.append(f"You: {user_message}")
        self.input_field.clear()
        
        bot_response = chatbot(TEXTBOOK,user_message)
        self.chat_display.append(f"Bot: {bot_response}")

class FlashcardWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        # Add input for number of flashcards
        self.num_cards_layout = QHBoxLayout()
        self.num_cards_label = QLabel("Number of flashcards:")
        self.num_cards_input = QSpinBox()
        self.num_cards_input.setRange(1, 100)
        self.num_cards_input.setValue(10)
        self.generate_button = QPushButton("Generate")
        self.generate_button.clicked.connect(self.generate_cards)
        
        self.num_cards_layout.addWidget(self.num_cards_label)
        self.num_cards_layout.addWidget(self.num_cards_input)
        self.num_cards_layout.addWidget(self.generate_button)
        layout.addLayout(self.num_cards_layout)

        self.card_display = QLabel()
        self.card_display.setText("Click generate to begin")
        self.card_display.setFont(FLASHCARD_FONT)
        self.card_display.setAlignment(Qt.AlignCenter)
        self.card_display.setStyleSheet(f"""
            background-color: {SECONDARY_COLOR};
            border-radius: 10px;
            padding: 20px;
        """)
        layout.addWidget(self.card_display)

        button_layout = QHBoxLayout()
        self.flip_button = QPushButton("Flip")
        self.next_button = QPushButton("Next Card")
        self.reset_button = QPushButton("Reset")

        for button in [self.flip_button, self.next_button, self.reset_button]:
            button.setFont(BUTTON_FONT)
            button_layout.addWidget(button)

        self.flip_button.clicked.connect(self.flip_card)
        self.next_button.clicked.connect(self.next_card)
        self.reset_button.clicked.connect(self.reset_cards)

        layout.addLayout(button_layout)

        self.setLayout(layout)


    def generate_cards(self):
        print("generatecards")
        num_cards = self.num_cards_input.value()
        self.cards = generateCards(num_cards)
        self.translated_cards = translateCards(TEXTBOOK,self.cards)
        self.current_card_index = 0
        self.is_front = True
        self.show_card()

    def show_card(self):
        if self.current_card_index < len(self.cards):
            current_card_front = self.cards[self.current_card_index]
            current_card_back = self.translated_cards[self.current_card_index]
            if self.is_front:
                self.card_display.setText(current_card_front)
            else:
                self.card_display.setText(current_card_back)
        else:
            self.card_display.setText("No more cards")
            self.flip_button.setEnabled(False)
            self.next_button.setEnabled(False)

    def flip_card(self):
        self.is_front = not self.is_front
        self.show_card()

    def next_card(self):
        self.current_card_index += 1
        self.is_front = True
        self.show_card()

    def reset_cards(self):
        self.current_card_index = 0
        self.is_front = True
        self.flip_button.setEnabled(True)
        self.next_button.setEnabled(True)
        self.show_card()

class FillBlankWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Add generate button
        self.generate_button = QPushButton("Generate New Question")
        self.generate_button.setFont(BUTTON_FONT)
        self.generate_button.clicked.connect(self.generate_new_question)
        layout.addWidget(self.generate_button)

        self.question = "Press Generate"
        
        self.question_label = QLabel(f"Fill in the blank: {self.question}")
        self.question_label.setWordWrap(True)
        layout.addWidget(self.question_label)

        self.answer_input = QLineEdit()
        layout.addWidget(self.answer_input)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.check_answer)
        layout.addWidget(self.submit_button)
    
        self.result_label = QLabel("")
        layout.addWidget(self.result_label)

        self.setLayout(layout)

    def generate_new_question(self):
        self.question = generatefillBlank(TEXTBOOK)
        self.question_label.setText(f"Fill in the blank: {self.question}")
        self.answer_input.clear()
        self.result_label.clear()

    def check_answer(self):
        answer = self.answer_input.text()
        self.result_label.setText(str(gradeFillBlank(TEXTBOOK, self.question, answer)))
        self.result_label.setWordWrap(True)

class ReadingCompWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        # Add generate button
        self.generate_button = QPushButton("Generate New Passage")
        self.generate_button.setFont(BUTTON_FONT)
        self.generate_button.clicked.connect(self.generate_new_passage)
        layout.addWidget(self.generate_button)

        self.story = selectStory()
        self.text = "Press Generate"

        self.passage = QTextEdit()
        self.passage.setReadOnly(True)
        self.passage.setText(f"Read the following passage and answer the questions below. \n\n{self.text}")
        layout.addWidget(self.passage)

        self.question_label = QLabel("Answers to questions:")
        layout.addWidget(self.question_label)

        self.answer_input = QLineEdit()
        layout.addWidget(self.answer_input)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.check_answer)
        layout.addWidget(self.submit_button)

        self.result_label = QLabel("")
        layout.addWidget(self.result_label)

        self.setLayout(layout)
    
    def generate_new_passage(self):
        self.story = selectStory()
        self.text = readingComprehension(TEXTBOOK, self.story)
        self.passage.setText(f"Read the following passage and answer the questions below:\n\n{self.text}")
        self.answer_input.clear()
        self.result_label.clear()
    
    def check_answer(self):
        answer = self.answer_input.text()
        self.result_label.setText(str(gradeReadingComprehension(TEXTBOOK, self.story, answer)))

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Use Fusion style for a more modern look
    lexiloom = LexiLoom()
    lexiloom.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
