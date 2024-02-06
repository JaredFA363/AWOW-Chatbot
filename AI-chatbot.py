# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 19:30:59 2024

@author: jared
"""
####################API'S##############
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
data = pandas.read_csv('logical-kb.csv', header=None)
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



##################Main################################
if __name__ == "__main__":
    # Replace 'your_kb.csv' with the actual path to your CSV file
    knowledge_base_path = 'KB.csv'
    knowledge_base = load_knowledge_base(knowledge_base_path)

    print("Welcome! Ask me anything or type 'exit' to end the conversation.")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() == 'chow':
            print("Chatbot: Goodbye! Have a great day.")
            break
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
                        object,subject=params[1].split(' is ')
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
            
            
            """#pre-process user input and determine response agent (if needed)
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
                elif cmd == 99:
                    print("I did not get that, please try again.")
        #answer = get_answer(user_input, knowledge_base)
        #print("Chatbot:", answer)"""