# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 19:30:59 2024

@author: jared
"""
####################API'S & IMPORTS##############
import wikipedia
import aiml
import json, requests

############Part A###################
import csv
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('stopwords')

def preprocess_text(text):
    # Tokenize, remove stopwords, and apply stemming
    stop_words = set(stopwords.words('english'))
    stemmer = PorterStemmer()
    tokens = nltk.word_tokenize(text.lower())
    stemmed_tokens = [stemmer.stem(token) for token in tokens if token.isalnum() and token not in stop_words]
    return ' '.join(stemmed_tokens)

def load_knowledge_base(file_path):
    # Load knowledge base from CSV file
    kb = {}
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) >= 2:
                question = preprocess_text(row[0])
                answer = row[1]
                kb[question] = answer
    return kb

def get_answer(user_query, knowledge_base):
    #threshold score
    threshold = 0.5
    
    # Preprocess user query
    preprocessed_query = preprocess_text(user_query)

    # Prepare TF-IDF vectors
    corpus = list(knowledge_base.keys()) + [preprocessed_query]
    tfidf_vectorizer = TfidfVectorizer(use_idf=True, sublinear_tf=True)
    tfidf_matrix = tfidf_vectorizer.fit_transform(corpus)

    # Calculate cosine similarity
    similarity_scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()

    # Find the index of the most similar question
    most_similar_index = similarity_scores.argmax()

    # Return the corresponding answer
    #return knowledge_base.get(corpus[most_similar_index], "I'm sorry, I don't understand.")

    # Check if the similarity score meets the threshold
    if similarity_scores[most_similar_index] >= threshold:
        # Return the corresponding answer
        return knowledge_base.get(corpus[most_similar_index], "I'm sorry, I don't understand.")
    else:
        return "I'm sorry, I don't have enough information to answer that."



#################Weather agent#############
APIkey = "5403a1e0442ce1dd18cb1bf7c40e776f" 

# Create a Kernel object. No string encoding (all I/O is unicode)
kern = aiml.Kernel()
kern.setTextEncoding(None)
#bootstrap() method to initialise Kernel. Optional learnFiles argument is a file (or list) to load.
kern.bootstrap(learnFiles="mybot-logics.xml")


###########################Part B#######################
import sys
from nltk.sem import Expression
from nltk.inference import ResolutionProver, ResolutionProverCommand
read_expr = Expression.fromstring
import pandas

#initialise KB
logic_kb=[]
data = pandas.read_csv('WOW-logical-kb.csv', header=None)
[logic_kb.append(read_expr(row)) for row in data[0]]
prover = ResolutionProver()

# Check for contradiction in the knowledge base
contradiction = prover.prove(read_expr('all x. (P(x) -> ~P(x))'), logic_kb)

# If there is a contradiction, show an error message and terminate
if contradiction:
    print("Error: Contradiction in the knowledge base.")
    sys.exit(0)
else:
    print("Knowledge base is consistent.")

# contradictions function
def check_for_contradictions(expr, kb):
    # Create a prover instance
    prover = ResolutionProver()

    # Formulate the negation of the new expression
    negation_expr = Expression.fromstring('~(' + str(expr) + ')')

    # Combine the new expression and its negation using logical disjunction
    combined_expr = Expression.fromstring(str(expr) + ' | ' + str(negation_expr))

    # Try to resolve the combined expressions with the existing knowledge base
    result = prover.prove(combined_expr, assumptions=kb)

    return not result  # If result is True, there is a contradiction; if False, no contradiction

# negation function
def adjust_negation(expression):
    if expression[0] == '-':
        # Remove the leading "-"
        return expression[1:]
    else:
        # Add a leading "-"
        return '-' + expression

def extract_wonder_name(statement):
    """
    Extract wonder name and category from the statement between "Check that" and "is".
    Return the wonder name without spaces.
    """
    start_index = statement.find("Check that") + len("Check that")
    end_index = statement.find("is")

    if start_index == -1 or end_index == -1:
        return None, None  # "Check that" or "is" not found in the statement

    # Extract the wonder name and category
    wonder_info = statement[start_index:end_index].strip()
    wonder_info = wonder_info.replace(" ", "")  # Remove spaces
    wonder_name, category = wonder_info, statement[end_index+3:].strip()  # Extract category after "is"

    return wonder_name, category

####################Part C################################
from tensorflow.keras.models import load_model
from tkinter import filedialog
from tkinter import *
from tensorflow.keras.preprocessing import image
import numpy as np

selected_filename = None

def browse_file():
    global selected_filename
    filename = filedialog.askopenfilename(initialdir="/", title="Select Image File", filetypes=(("Image files", "*.jpg;*.jpeg;*.png"), ("All files", "*.*")))
    print("Selected file:", filename)
    selected_filename = filename

def predict_image(filename):
    model = load_model("wow_model.h5")
    # Load and preprocess the image
    img = image.load_img(filename, target_size=(200, 200))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0

    # Make predictions with the model
    predictions = model.predict(img_array)
    predicted_class_index = np.argmax(predictions)
    predicted_classes = ["Burj Khalifa", "Christ the Redeemer", "Pyramids of Giza", "Roman Colosseum", "Taj Mahal"]

    # Print the predicted class
    if predicted_class_index < len(predicted_classes):
        print("Predicted image: ", predicted_classes[predicted_class_index])
    else:
        print("Could not discern image")
        
####################Extra func voice recognition#######
import speech_recognition as sr

def speech_to_text():
    # Initialize the recognizer
    recognizer = sr.Recognizer()

    # Open the microphone and start recording
    with sr.Microphone() as source:
        print("Please speak something...")
        recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
        audio_data = recognizer.listen(source)  # Listen for the audio input

    try:
        # Recognize speech using Google Speech Recognition
        text = recognizer.recognize_google(audio_data)
        print("You said:", text)
        return text

    except sr.UnknownValueError:
        print("Sorry, I could not understand what you said.")
        return None

    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        return None

##################Main################################
if __name__ == "__main__":
    # Replace 'your_kb.csv' with the actual path to your CSV file
    knowledge_base_path = 'WOW-KB.csv'
    knowledge_base = load_knowledge_base(knowledge_base_path)

    print("Welcome! Ask me anything or type 'exit' to end the conversation.")
    
    while True:
        user_input = input("You: ")
        if user_input == "I want to speak to you":
            user_input = speech_to_text()
        
        if user_input.lower() == 'chow':
            print("Chatbot: Goodbye! Have a great day.")
            break
        elif user_input == 'What is this picture':
            #loaded_model = load_model("wow_model.h5")
            window = Tk()
            button = Button(window,text="Browse",command=browse_file)
            button.pack()
            window.mainloop()
            print(selected_filename)
            predict_image(selected_filename)
        if user_input:
            answer = get_answer(user_input, knowledge_base)
            #print("Chatbot:", answer)
            if answer == "I'm sorry, I don't have enough information to answer that.":
                #pre-process user input and determine response agent (if needed)
                responseAgent = 'aiml'
                #activate selected response agent
                if responseAgent == 'aiml':
                    answer = kern.respond(user_input)
                #post-process the answer for commands
                if answer[0] == '#':
                    params = answer[1:].split('$')
                    cmd = int(params[0])
                    if cmd == 0:
                        print(params[1])
                        break
                    elif cmd == 1:
                        try:
                            wSummary = wikipedia.summary(params[1], sentences=3,auto_suggest=False)
                            print(wSummary)
                        except:
                            print("Sorry, I do not know that. Be more specific!")
                    #elif cmd == 2:
                    elif cmd == 31: # if input pattern is "I know that * is *"
                        object,subject=params[1].split(' is ')
                        expr=read_expr(subject + '(' + object + ')')
                        # >>> ADD SOME CODES HERE to make sure expr does not contradict 
                        # with the KB before appending, otherwise show an error message.
                        negation_expression = adjust_negation(str(expr))
                        negation_expr = Expression.fromstring(negation_expression)
                        #if check_for_contradictions(expr, logic_kb):
                        if negation_expr in logic_kb:
                            print('Error: The new information contradicts with the existing knowledge base.')
                        else:
                            # If no contradictions, append the expression to the knowledge base
                            logic_kb.append(expr) 
                            print('OK, I will remember that',object,'is', subject)
                    elif cmd == 32: # if the input pattern is "check that * is *"
                        #object,subject=params[1].split(' is ')
                        object,subject = extract_wonder_name(user_input)
                        #expr = read_expr(category + '(' + wonder_name + ')')
                        expr=read_expr(subject + '(' + object + ')')
                        answer=ResolutionProver().prove(expr, logic_kb, verbose=True)
                        if answer:
                           print('Correct.')
                        else:
                           # Check for contradiction
                           negation_expression = adjust_negation(str(expr))
                           negation_expr = Expression.fromstring(negation_expression)
                           contradiction_check = check_for_contradictions(expr, logic_kb)

                           # If there's a contradiction, provide that information
                           if negation_expr in logic_kb:
                              print('Incorrect: The provided information contradicts with the existing knowledge base.')
                           else:
                              print("Incorrect: The provided information is not supported by the existing knowledge base.")
                    elif cmd == 99:
                        print("I did not get that, please try again.")
            print("Chatbot:", answer)
        else:
            print("Chatbot: I'm sorry, I don't have enough information to answer that.")
            