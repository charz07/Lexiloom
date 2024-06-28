import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QFileDialog, QTextEdit, QLineEdit, QStackedWidget, QSizePolicy)
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap
from PyQt5.QtCore import Qt
from backend import generateCards, translateCards, readingComprehension, gradeReadingComprehension, chatbot, generatefillBlank, gradeFillBlank

# Define fonts
TITLE_FONT = QFont("Verdana", 24, QFont.Bold)
BUTTON_FONT = QFont("Arial", 12)
TEXT_FONT = QFont("Sans Serif", 11)
FLASHCARD_FONT = QFont("Georgia", 18)

class LexiLoom(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LexiLoom")
        self.setGeometry(100, 100, 800, 600)
        self.setup_ui()

    def setup_ui(self):
        # Set up purple theme
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(61, 11, 95))  # Dark purple
        palette.setColor(QPalette.Button, QColor(255, 105, 180))  # Hot pink
        palette.setColor(QPalette.ButtonText, Qt.black)
        palette.setColor(QPalette.WindowText, Qt.white)
        self.setPalette(palette)

        # Main layout
        main_layout = QVBoxLayout()

        #logo
        logo = QLabel()
        pixmap = QPixmap("full_logo_transparent.png")
        desired_width = 400  # Adjust this value to make the logo larger or smaller
        desired_height = 400  # Adjust this value to make the logo larger or smaller
        scaled_pixmap = pixmap.scaled(desired_width, desired_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo.setPixmap(scaled_pixmap)
        logo.setAlignment(Qt.AlignCenter)
        logo.setFixedSize(desired_width, desired_height)  # This ensures the label is the same size as the scaled pixmap

        # Create a wrapper layout to center the logo
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
        self.chatbot_button.setFont(BUTTON_FONT)
        self.flashcard_button = QPushButton("Flashcards")
        self.flashcard_button.setFont(BUTTON_FONT)
        self.fill_blank_button = QPushButton("Fill in the Blank")
        self.fill_blank_button.setFont(BUTTON_FONT)
        self.reading_comp_button = QPushButton("Reading Comprehension")
        self.reading_comp_button.setFont(BUTTON_FONT)

        for button in [self.chatbot_button, self.flashcard_button, self.fill_blank_button, self.reading_comp_button]:
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
        file_name, _ = QFileDialog.getOpenFileName(self, "Open PDF File", "", "PDF Files (*.pdf)")
        if file_name:
            print(f"File uploaded: {file_name}")
            # Here you would process the PDF file
            
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
        #self.chat_display.setFont(TEXT_FONT)
        self.chat_display.append(f"You: {user_message}")
        self.input_field.clear()
        
        # Here you would integrate with your chatbot backend
        bot_response = chatbot(user_message)
        self.chat_display.append(f"Bot: {bot_response}")

class FlashcardWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.cards = generateCards(10)  # Generate 10 cards, adjust as needed
        self.translated_cards = translateCards(self.cards)
        self.current_card_index = 0
        
        self.card_display = QLabel()
        self.card_display.setFont(FLASHCARD_FONT)
        self.card_display.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.card_display)

        self.flip_button = QPushButton("Flip")
        self.flip_button.setFont(FLASHCARD_FONT)
        self.flip_button.clicked.connect(self.flip_card)
        layout.addWidget(self.flip_button)

        self.next_button = QPushButton("Next Card")
        self.next_button.setFont(FLASHCARD_FONT)
        self.next_button.clicked.connect(self.next_card)
        layout.addWidget(self.next_button)

        self.setLayout(layout)

        self.is_front = True
        self.show_card()  # Show the first card

    def show_card(self):
        if self.current_card_index < len(self.cards):
            current_card_front = self.cards[self.current_card_index]
            current_card_back = self.translated_cards[self.current_card_index]
            if self.is_front:
                self.card_display.setText(current_card_front)
            else:
                # Here you might want to implement a way to show the "back" of the card
                # For now, we'll just show "Back of card"
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

class FillBlankWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        question  = generatefillBlank()
        
        self.question_label = QLabel(f"Fill in the blank: {question}")
        layout.addWidget(self.question_label)

        self.answer_input = QLineEdit()
        layout.addWidget(self.answer_input)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.check_answer)
        layout.addWidget(self.submit_button)

        self.result_label = QLabel("")
        layout.addWidget(self.result_label)

        self.setLayout(layout)

    def check_answer(self):
        answer = self.answer_input.text()
        # Here you would check the answer against the correct one
        self.result_label.setText(str(gradeFillBlank(answer)))

class ReadingCompWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        self.text = readingComprehension()

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

    def check_answer(self):
        answer = self.answer_input.text()
        # Here you would evaluate the answer
        self.result_label.setText(str(gradeReadingComprehension(answer)))

def main():
    app = QApplication(sys.argv)
    lexiloom = LexiLoom()
    lexiloom.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
