import openai
import csv
from pypdf import PdfReader
import random
from groq import Groq

# Global variables
textbookParsed = ""  # Stores the parsed content of the textbook
textbookPath = "data/Hawaiian (1).pdf"    # Stores the path to the textbook file
vocabPath = "data/vocab.csv"  # Path to vocabulary CSV file
storyPath = "data/storyAndAnswers.csv"  # Path to story and questions CSV file
blanksPath = "data/fillblank.csv"  # Path to fill-in-the-blanks CSV file

# Initialize Groq client with API key
groq_client = Groq(api_key="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")

def set_textbook_path(path):
    """
    Sets the textbook path and parses its content.
    
    Args:
    path (str): Path to the textbook PDF file.
    
    Returns:
    str: Parsed content of the textbook.
    """
    global textbookPath, textbookParsed
    textbookPath = path
    reader = PdfReader(path)
    textbookParsed = "\n".join(page.extract_text() for page in reader.pages)
    return textbookParsed

def prompt_ai(system_prompt, user_prompt):
    """
    Sends a prompt to the AI and returns the response.
    
    Args:
    system_prompt (str): Instructions for the AI's behavior.
    user_prompt (str): The actual query or task for the AI.
    
    Returns:
    str: The AI's response.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    response = groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=messages,
        temperature=0.0,
        max_tokens=4096
    )
    return response.choices[0].message.content.strip()

def translate(text_to_translate):
    """
    Translates given text into the language of the textbook.
    
    Args:
    text_to_translate (str): Text to be translated.
    
    Returns:
    str: Translated text.
    """
    textbook_content = set_textbook_path(textbookPath)
    system_prompt = f"You are a translation AI tool. Use the textbook attached below to help translate any texts given to you into the textbook's target language. As a translation AI, only provide translations of texts and nothing else. Use identical formatting as the text provided. Purely translate, and don't even say things like 'here's the translated text:'. If given texts contain punctuation, blank spaces, or new lines, keep them identical in the translations.\n\nTEXTBOOK:\n\n{textbook_content}"
    return prompt_ai(system_prompt, text_to_translate)

def translate_to_english(text_to_translate):
    """
    Translates given text to English.
    
    Args:
    text_to_translate (str): Text to be translated to English.
    
    Returns:
    str: English translation of the input text.
    """
    system_prompt = "You are a translator. Translate the given text to English."
    return prompt_ai(system_prompt, text_to_translate)

def generate_cards(number):
    """
    Generates vocabulary cards.
    
    Args:
    number (int): Number of vocabulary cards to generate.
    
    Returns:
    list: List of dictionaries, each containing an English word and its foreign language translation.
    """
    with open(vocabPath, 'r') as file:
        vocab_list = list(csv.reader(file))
    
    selected_vocab = random.sample(vocab_list, number)
    vocab_string = "\n".join([word[0] for word in selected_vocab])
    translated_vocab = translate(vocab_string).split("\n")
    
    return [{"English": eng, "Foreign": for_} for eng, for_ in zip([word[0] for word in selected_vocab], translated_vocab)]

def generate_fill_in_blanks(number):
    """
    Generates fill-in-the-blank questions.
    
    Args:
    number (int): Number of fill-in-the-blank questions to generate.
    
    Returns:
    list: List of translated fill-in-the-blank questions.
    """
    with open(blanksPath, 'r') as file:
        blanks_list = list(csv.reader(file))
    
    selected_blanks = random.sample(blanks_list, number)
    blanks_string = "\n".join([blank[0] for blank in selected_blanks])
    translated_blanks = translate(blanks_string).split("\n")
    
    return translated_blanks

def grade_fill_in_blank_question(sentence, answer):
    """
    Grades a fill-in-the-blank question.
    
    Args:
    sentence (str): The fill-in-the-blank sentence.
    answer (str): The user's answer.
    
    Returns:
    bool: True if the answer is correct, False otherwise.
    """
    prompt = f"Given the fill-in-the-blank sentence '{sentence}', is '{answer}' the correct word to fill in the blank? Respond with YES or NO."
    response = prompt_ai("You are a language teacher grading fill-in-the-blank questions.", prompt)
    return "YES" in response.upper()

def generate_reading_comprehension():
    """
    Generates a reading comprehension exercise.
    
    Returns:
    tuple: Contains the translated story and three translated questions.
    """
    with open(storyPath, 'r') as file:
        stories = list(csv.reader(file))
    
    selected_story = random.choice(stories)
    translated_story = translate(selected_story[0])
    translated_questions = [translate(q) for q in selected_story[1:4]]
    
    return (translated_story, *translated_questions)

def grade_reading_comprehension_question(story, question, answer):
    """
    Grades a reading comprehension question.
    
    Args:
    story (str): The reading comprehension passage.
    question (str): The question about the passage.
    answer (str): The user's answer to the question.
    
    Returns:
    bool: True if the answer is correct, False otherwise.
    """
    prompt = f"Given the story:\n{story}\n\nAnd the question:\n{question}\n\nIs the answer '{answer}' correct? Respond with YES or NO."
    response = prompt_ai("You are a language teacher grading reading comprehension questions.", prompt)
    return "YES" in response.upper()

class ChatBot:
    """
    A chatbot class for interactive language learning.
    """
    def __init__(self):
        """
        Initializes the ChatBot with an empty message history.
        """
        self.message_history = []
    
    def message(self, message):
        """
        Processes a user message and returns the AI's response.
        
        Args:
        message (str): The user's message.
        
        Returns:
        str: The AI's response to the user's message.
        """
        system_prompt = f"You are a teacher of the language described in the following textbook. Assist the user in learning this language:\n\n{textbookParsed}"
        self.message_history.append({"role": "user", "content": message})
        
        messages = [{"role": "system", "content": system_prompt}] + self.message_history
        
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages,
            temperature=0.0,
            max_tokens=4096
        )
        
        ai_response = response.choices[0].message.content.strip()
        self.message_history.append({"role": "assistant", "content": ai_response})
        return ai_response