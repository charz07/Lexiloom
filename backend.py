import openai
import csv
from pypdf import PdfReader
import random
from groq import Groq

textbookParsed = ""
groq_client = Groq(api_key="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")

def setTextBookPath(path):
    global textbookPath, textbookParsed
    textbookPath = path
    reader = PdfReader(path)
    for page in reader.pages:
        text = page.extract_text()
        textbookParsed+= text + "\n"

    return textbookParsed



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

def translateCards(textbookParsed, list_cards):

    system_prompt= f"""Given the following textbook, learn the language in the material. 
    \n {textbookParsed}\n
    Translate the provided vocabulary words into the language in the textbook. 
    Output each translated word and ONLY the translated word by itself to a new line, no formatting.
    Do not include any labels, just have the list of words by itself.
    """

    messages = [{"role": "system", "content": system_prompt},{"role":"user", "content":str(list_cards)}]
    response = groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=messages,
        temperature=0.0,
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


def selectStory():
    file_path = 'data/storyAndAnswers.csv'
    parsed_data = read_csv_to_dict_list(file_path)
    randStory = random.choice(parsed_data)
    return randStory

def readingComprehension(textbookParsed, story):
    print("->"+textbookParsed +"<-")
    system_prompt= f"""Given the following textbook, learn the language in the material. 
    \n {textbookParsed}\n
    Translate the provided story and reading comprehension questions into the language taught in the textbook.
    Do so in the format:

    *Story*
    1. *Question 1*
    2. *Question 2*
    3. *Question 3*

    Do not include any descriptions, labels, or footnotes.
    """

    messages = [{"role": "system", "content": system_prompt},{"role":"user", "content":str(story)}]
    response = groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=messages,
        temperature=0.0,
        max_tokens=4096
    )
    return response.choices[0].message.content.strip()

def gradeReadingComprehension(textbookParsed, story, answers):
    system_prompt= f"""
    Given the following textbook, learn the language in the material. 
    \n {textbookParsed}\n
    Given the following story and reading questions
    \n{story}\n

    Identify if the answers to the questions are valid (once they are translated into English) and provide ONLY a Yes or No divided by a newline, no formatting based on the provided text.
    There should be 3 questions, and 3 grades.
    """


    messages = [{"role": "system", "content": system_prompt},{"role": "system", "content": answers}]
    response = groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=messages,
        temperature=0.0,
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
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a helpful language assistant."},
                {"role": "user", "content": context},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {str(e)}"

def chatbot(textbookParsed, user_input):
    print (textbookParsed)
    context = f"""You are a language assistant. Your primary role is to help users with language-related queries, such as grammar, vocabulary, translation, and language learning tips.
    
    Learn the language in the below textbook. Help the user to learn this language in your prompts.
    \n{textbookParsed}\n
    """
    
    while True:
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("Language Assistant: Goodbye! Have a great day!")
            break
        
        response = get_gpt4_response(user_input, context)
        return response 


def generatefillBlank(textbookParsed):
    q_list = read_csv_to_list("data/fillblank.csv")
    list_questions = []
    random_question = random.choice(q_list)
    fill_blank_question = random_question

    system_prompt= f"""Given the following textbook, learn the language in the material. 
    \n {textbookParsed}\n
    Translate the provided fill in the blank question into the language taught in the textbook, leaving all underscores untouched. Output each translated question individually on a new line with no formatting.

    """

    messages = [{"role": "system", "content": system_prompt},{"role":"user", "content":random_question}]
    response = groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=messages,
        temperature=0.0,
        max_tokens=4096
    )

    
    response_content = response.choices[0].message.content.strip().split("\n")
    response_text = "\n".join(response_content)

    return response.choices[0].message.content.strip().split("\n")

def gradeFillBlank(textbookParsed, fill_blank_question, answer):

    system_prompt= f"""Given the following textbook, learn the language in the material. 
    \n {textbookParsed}\n
    Here is a fill in the blank question in the language you learned:
    
    \n{fill_blank_question}\n

    Now, given the following answer, please answer whether or not the answer reasonably answers the question in that language. 
    Please give a very brief explanation as to why the answer is correct or incorrect.
    """

    messages = [{"role": "system", "content": system_prompt},{"role": "system", "content": answer}]
    response = groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=messages,
        temperature=0.0,
        max_tokens=4096
    )

    return response.choices[0].message.content.strip()
