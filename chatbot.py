#######################################################
# Initialise Wikipedia agent
#######################################################
import wikipedia

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

#######################################################
#  Initialise AIML agent
#######################################################
import aiml

# Create a Kernel object. No string encoding (all I/O is unicode)
kern = aiml.Kernel()
kern.setTextEncoding(None)

# Use the Kernel's bootstrap() method to initialize the Kernel. The
# optional learnFiles argument is a file (or list of files) to load.
# The optional commands argument is a command (or list of commands)
# to run after the files are loaded.
# The optional brainFile argument specifies a brain file to load.
kern.bootstrap(learnFiles="mybot-logics.xml")


#######################################################
#Part A
#######################################################
import csv
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

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


#######################################################
# Welcome user
#######################################################
print("Welcome to this chat bot. Please feel free to ask questions from me!")
#######################################################
# Main loop
#######################################################


while True:
    knowledge_base_path = 'KB.csv'
    knowledge_base = load_knowledge_base(knowledge_base_path)
    
    #get user input
    try:
        userInput = input("> ")
    except (KeyboardInterrupt, EOFError) as e:
        print("Bye!")
        break
    #pre-process user input and determine response agent (if needed)
    responseAgent = 'aiml'
    #activate selected response agent
    if responseAgent == 'aiml':
        answer = kern.respond(userInput)
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
        #elif cmd == 31:
        elif cmd == 99:
            print("I did not get that, please try again.")
        else:
            answer = get_answer(userInput, knowledge_base)
    else:
        print(answer)
        