import openai
import csv
from pypdf import PdfReader
import random


textbookPath = "data/the-navajo-verb-a-grammar-for-students-and-scholars.pdf"
textbookParsed = ""
openai.api_key = ""


# reader = PdfReader(textbookPath)
# for page in reader.pages:
#     text = page.extract_text()
#     textbookParsed+= text + "\n"

def read_csv_to_list(file_path):
    with open(file_path, 'r') as file:
        return file.read().splitlines()


def generateCards(num):
    vocab_list = read_csv_to_list("data/vocab.csv")

    list_cards = []
    randWord = random.choice(vocab_list)
    for i in range(num):
        if randWord not in list_cards:
            list_cards.append(randWord)
        randWord = random.choice(vocab_list)
    return list_cards

def translateCards(list_cards):
    system_prompt= f"""Given the following textbook, learn the language in the material. 
    \n {textbookParsed}\n
    Translate the provided vocabulary words into the language taught in the textbook. Output each translated word individually on a new line with no formatting.
    
    \n{list_cards}\n
    """

    system_prompt_temp= f"""
    Translate the provided vocabulary words into Latin. Output each translated word individually on a new line with no formatting.
    
    \n{list_cards}\n
    """


    messages = [{"role": "system", "content": system_prompt_temp}]
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.3,
        max_tokens=4096
    )
    return response.choices[0].message.content.strip().split("\n")


def read_csv_to_dict_list(file_path):
    result = []
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            if len(row) == 4:  # Ensure the row has 4 columns
                row_dict = {
                    "story": row[0],
                    "question1": row[1],
                    "question2": row[2],
                    "question3": row[3]
                }
                result.append(row_dict)
    return result

file_path = 'data/storyAndAnswers.csv'
parsed_data = read_csv_to_dict_list(file_path)
randStory = random.choice(parsed_data)

def readingComprehension():

    system_prompt= f"""Given the following textbook, learn the language in the material. 
    \n {textbookParsed}\n
    Translate the provided story and reading comprehension questions into the language taught in the textbook.
    Do so in the format:

    *Story*
    1. *Question 1*
    2. *Question 2*
    3. *Question 3*
    \n{randStory}\n
    """

    system_prompt_temp= f"""
    Translate the provided provided story and reading comprehension question into Latin. 
    Do so in the format:

    *Story*
    1. *Question 1*
    2. *Question 2*
    3. *Question 3*
    \n{randStory}\n
    """


    messages = [{"role": "system", "content": system_prompt_temp}]
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.3,
        max_tokens=4096
    )
    return response.choices[0].message.content.strip()

def gradeReadingComprehension(answers):
    system_prompt_temp= f"""
    Given the following story and reading questions
    \n{randStory}\n

    Identify if the answers to the questions are valid (once they are translated into English) and provide ONLY a Yes or No divided by a newline, no formatting based on the provided text
    \n{answers}\n
    """


    messages = [{"role": "system", "content": system_prompt_temp}]
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.3,
        max_tokens=4096
    )
    grades =  response.choices[0].message.content.strip().split("\n")
    grade_list = []
    for grade in grades:
        if grade == "Yes":
            grade_list.append(True)
        else:
            grade_list.append(False)
    return grade_list

def get_gpt4_response(prompt, context):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful language assistant."},
                {"role": "user", "content": context},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {str(e)}"

def chatbot(user_input):
    context = f"""You are a language assistant. Your primary role is to help users with language-related queries, such as grammar, vocabulary, translation, and language learning tips.
    """
    
    while True:
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("Language Assistant: Goodbye! Have a great day!")
            break
        
        response = get_gpt4_response(user_input, context)
        return response 


fill_blank_question = ""

def generatefillBlank():
    q_list = read_csv_to_list("data/fillblank.csv")
    list_questions = []
    random_question = random.choice(q_list)
    fill_blank_question = random_question

    system_prompt= f"""Given the following textbook, learn the language in the material. 
    \n {textbookParsed}\n
    Translate the provided questions into the language taught in the textbook, leaving all underscores untouched. Output each translated question individually on a new line with no formatting.
    
    \n{random_question}\n
    """

    system_prompt_temp= f"""
    Translate the provided questions into the Latin, leaving all underscores untouched. Output each translated question individually on a new line with no formatting.
    
    \n{random_question}\n
    """

    messages = [{"role": "system", "content": system_prompt_temp}]
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.3,
        max_tokens=4096
    )

    
    response_content = response.choices[0].message.content.strip().split("\n")
    response_text = "\n".join(response_content)

    return response.choices[0].message.content.strip().split("\n")

def gradeFillBlank(answer):

    system_prompt= f"""Given the following textbook, learn the language in the material. 
    \n {textbookParsed}\n
    Here is a fill in the blank question in the language you learned:
    
    \n{fill_blank_question}\n

    Now, given the following answer, please answer whether or not the answer reasonably answers the question in that language. Only answer with either an uppercase YES or NO.
    \n{answer}\n
    """

    system_prompt_temp= f"""
    Here is a fill in the blank question in Latin:
    
    \n{fill_blank_question}\n

    Now, given the following answer, please answer whether or not the answer reasonably answers the question in that language. Only answer with either an uppercase YES or NO.
    \n{answer}\n
    """

    messages = [{"role": "system", "content": system_prompt}]
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.3,
        max_tokens=4096
    )

    response_content = response.choices[0].message.content.strip().upper()
    if response_content == "YES":
        return True
    else:
         return False



