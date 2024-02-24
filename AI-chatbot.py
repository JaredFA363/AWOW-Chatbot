####################API'S & IMPORTS##############
import wikipedia
import aiml

from AI_Functionalities import similarity_based_program, rule_based_logic, image_pred, speech_recog

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
from nltk.inference import ResolutionProver
import pandas

#initialise KB
logic_kb=[]
data = pandas.read_csv('WOW-logical-kb.csv', header=None)
read_expr = Expression.fromstring
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

####################Part C################################
from tkinter import *
from tkinter import filedialog
selected_filename = None

def browse_file():
    global selected_filename
    filename = filedialog.askopenfilename(initialdir="/", title="Select Image File", filetypes=(("Image files", "*.jpg;*.jpeg;*.png"), ("All files", "*.*")))
    print("Selected file:", filename)
    selected_filename = filename        

##################Main################################
if __name__ == "__main__":
    # Replace 'your_kb.csv' with the actual path to your CSV file
    knowledge_base_path = 'WOW-KB.csv'
    knowledge_base = similarity_based_program.load_knowledge_base(knowledge_base_path)

    print("Welcome! Ask me anything or type 'exit' to end the conversation.")
    
    while True:
        user_input = input("You: ")
        if user_input == "I want to speak to you":
            user_input = speech_recog.speech_to_text()
        
        if user_input.lower() == 'chow':
            print("Chatbot: Goodbye! Have a great day.")
            break
        elif user_input == 'What is this picture':
            window = Tk()
            button = Button(window,text="Browse",command=browse_file)
            button.pack()
            window.mainloop()
            image_pred.predict_image(selected_filename)
            pass
        if user_input:
            answer = similarity_based_program.get_answer(user_input, knowledge_base)

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

                    elif cmd == 31: # if input pattern is "I know that * is *"

                        object,subject = rule_based_logic.extract_wonder_name_kb_addition(user_input)
                        expr=read_expr(subject + '(' + object + ')')

                        negation_expression = rule_based_logic.adjust_negation(str(expr))
                        negation_expr = Expression.fromstring(negation_expression)

                        if negation_expr in logic_kb:
                            print('Error: The new information contradicts with the existing knowledge base.')
                        else:
                            # If no contradictions, append the expression to the knowledge base
                            logic_kb.append(expr) 
                            print('OK, I will remember that',object,'is', subject)
                    elif cmd == 32: # if the input pattern is "check that * is *"
                        object,subject = rule_based_logic.extract_wonder_name(user_input)
                        expr=read_expr(subject + '(' + object + ')')
                        answer=ResolutionProver().prove(expr, logic_kb, verbose=True)
                        if answer:
                           print('Correct.')
                        else:
                           # Check for contradiction
                           negation_expression = rule_based_logic.adjust_negation(str(expr))
                           negation_expr = Expression.fromstring(negation_expression)

                           # If there's a contradiction, provide that information
                           if negation_expr in logic_kb:
                              print('Incorrect: The provided information contradicts with the existing knowledge base.')
                           else:
                              print("Incorrect: The provided information is not supported by the existing knowledge base.")
                    elif cmd == 99:
                        print("I did not get that, please try again.")
            print("Chatbot: " , answer )
        else:
            print("Chatbot: I'm sorry, I don't have enough information to answer that.")
            