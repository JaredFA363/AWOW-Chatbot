import wikipedia
import aiml
from AI_Functionalities import similarity_based_program, rule_based_logic, image_pred, speech_recog, fuzzy_logic
from nltk.sem import Expression
from nltk.inference import ResolutionProver
from tkinter import *
from tkinter import filedialog

#For weather agent
APIkey = "5403a1e0442ce1dd18cb1bf7c40e776f" 

#bootstrap() method to initialise Kernel. Optional learnFiles argument is a file (or list) to load.
kern = aiml.Kernel()
kern.setTextEncoding(None)
kern.bootstrap(learnFiles="mybot-logics.xml")

#For image recognition
selected_filename = None

def browse_file():
    global selected_filename
    filename = filedialog.askopenfilename(initialdir="/", title="Select Image File", filetypes=(("Image files", "*.jpg;*.jpeg;*.png"), ("All files", "*.*")))
    print("Selected file:", filename)
    selected_filename = filename        

if __name__ == "__main__":
    # loading kbs
    knowledge_base_path = 'WOW-KB.csv'
    knowledge_base = similarity_based_program.load_knowledge_base(knowledge_base_path)
    logic_kb_path = 'WOW-logical-kb.csv'
    logic_kb, read_expr = rule_based_logic.load_logic_kb(logic_kb_path)

    print("Welcome! Ask me anything or type 'exit' to end the conversation.")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() == 'chow':
            print("Chatbot: Goodbye! Have a great day.")
            break

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

                        prover = ResolutionProver()
                        contradiction = prover.prove(negation_expr, logic_kb)
                        
                        if contradiction:
                            print('Incorrect: The provided information contradicts with the existing knowledge base.')
                            answer = "Contradiction Found"
                        else:
                            # If no contradictions, append the expression to the knowledge base
                            logic_kb.append(expr) 
                            print('OK, I will remember that',object,'is', subject)
                            answer = "Fact Remembered"
                            
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
                           prover = ResolutionProver()
                           contradiction = prover.prove(negation_expr, logic_kb)
                           
                           if contradiction:
                               print('Incorrect: The provided information contradicts with the existing knowledge base.')
                           else:
                               print("Incorrect: The provided information is not supported by the existing knowledge base.")
                    
                    elif cmd == 41: # image classification
                        window = Tk()
                        button = Button(window,text="Browse",command=browse_file)
                        button.pack()
                        window.mainloop()
                        image_pred.predict_image(selected_filename)
                        answer = "Identified"
                        
                    elif cmd == 51: #voice commands
                        user_input = speech_recog.speech_to_text()
                        answer = similarity_based_program.get_answer(user_input, knowledge_base)
                        
                    elif cmd == 61: #Fuzzy reccommendation
                        beauty_score = int(input("Give a score for the architectural beauty you want. (from 1 to 10)"))
                        historical_score = int(input("Give a score for the historical significance you want.(from 1 to 10)"))
                        while 0 > historical_score > 10 or 0 > beauty_score > 10:
                            print("Please enter a value below 10 and above 0")
                            beauty_score = int(input("Give a score for the architectural beauty you want. (from 1 to 10)"))
                            historical_score = int(input("Give a score for the historical significance you want.(from 1 to 10)"))
                        reccomendation = fuzzy_logic.fuzzy_wonder_recommendation(historical_score, beauty_score)
                        answer = "Recommended Wonder of the World:", reccomendation
                        
                    elif cmd == 99:
                        print("I did not get that")
                        answer = "Please, Try Again"
            print("Chatbot: " , answer )
        else:
            print("Chatbot: I'm sorry, I don't have enough information to answer that.")