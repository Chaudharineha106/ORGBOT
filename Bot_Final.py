'''
import json
import requests
import os
import random
import textsim2
chatlist=[] 
prevQuestion="default"


class UltraChatBot():
    def __init__(self, json):
        self.json = json
        self.dict_messages = json['data']

    def Processingـmybot(incoming_message):
         data = text_similarity(incoming_message)
         print(data)
         return data
            

# Load your custom data from a JSON file
with open('Questions.json', 'r',encoding="utf8") as file:
    college_data = json.load(file)
# Create a new trainer for the chat bot

# Now, let's interact with the bot
print("Bot: Hi, how can I assist you today?")

def text_similarity(sentence1):
    global prevQuestion
    global college_data
    output=""
    dist=0
    myList=[]
    q=""
   
    print("pq:"+prevQuestion)
    if "yes:" in sentence1.lower():
       sentence1=sentence1.replace("yes:","").replace("Yes:","")
       new_data = [prevQuestion, sentence1]
        # Append new data to the existing list
       college_data.append(new_data)
       #print(college_data)
       # Write updated data back to clg.json
       with open('Questions.json', 'w', encoding="utf8") as file:
            json.dump(college_data, file, ensure_ascii=False, indent=4)
       return "Data added in Db"
            
    for input_text, response_text in college_data:
        matching_words_count = textsim2.count_matching_words(input_text, sentence1)
        if dist<=matching_words_count:
            dist=matching_words_count
            output=response_text
            if dist==1:
                myList.append(input_text)
            q=input_text
    if dist==1:
        output="Do you want to ask this : " 
        i=1 
        for item in myList:
            output=output+"\n"+str(i)+"."+ item
            i=i+1

    else: 
     if dist<2:
        output="I'm sorry, I couldn't understand your question. do you want to train if Yes then type yes:answer"
        prevQuestion=sentence1

    return output'
    '''
import json
import textsim2  # Import the text similarity module

class UltraChatBot:
    def __init__(self, user_type):
        """Initialize chatbot with the appropriate dataset based on user type (admin/user)."""
        self.user_type = user_type  # Store user type
        self.dataset = self.load_dataset()
        self.last_question = None  # Store the last unknown question for admin training

    def load_dataset(self):
        """Load dataset based on user type and ensure correct structure."""
        json_file = 'Employee_Chatbot.json' if self.user_type == "employees" else 'User_Chatbot.json'
        try:
            with open(json_file, 'r', encoding="utf8") as file:
                data = json.load(file)
                if isinstance(data, list) and all(isinstance(i, list) and len(i) == 2 for i in data):
                    print(f"✅ Loaded dataset from {json_file}: {len(data)} entries")  # Debugging print
                    return data  # ✅ Ensure dataset is a list of [question, answer]
                else:
                    print(f"❌ Error: {json_file} has an incorrect structure. Expected [['question', 'answer']].")
                    return []
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"❌ Error loading {json_file}: {e}")
            return []  # Return empty list if the file is missing or corrupted

    def process_incoming_message(self, incoming_message):
        """Process user message and return chatbot response."""
        return self.text_similarity(incoming_message)

    def text_similarity(self, user_input):
        """Find best matching response from dataset using word similarity and synonyms."""

        # ✅ Admin is giving an answer
        if self.user_type == "employees" and user_input.lower().startswith("yes:"):
            return self.train_chatbot(user_input.replace("yes:", "").strip())

        best_match = None
        highest_match_score = 0  # Track the best match score

        # ✅ Ensure dataset is valid before iterating
        if not self.dataset:
            return "⚠️ Sorry, no knowledge base is loaded."

        # ✅ Search for a matching response in the dataset
        for input_text, response_text in self.dataset:
            match_score = textsim2.count_matching_words(input_text, user_input)
            if match_score > highest_match_score:
                highest_match_score = match_score
                best_match = response_text

        # ✅ If a good match is found, return it
        if highest_match_score > 0:
            return best_match

        # ✅ If no match found, now store last question for training
        if self.user_type == "employees":
            self.last_question = user_input  # <-- Set ONLY here!
            return f"🤖 I don't know this. You can train me by typing 'yes: your answer'. Your question: {self.last_question}"
        else:
            return "🚫 You have no authority to see this data."


    def train_chatbot(self, new_answer):
        if self.last_question:
            entry = [self.last_question, new_answer.strip()]
            self.dataset.append(entry)

            json_file = 'Employee_Chatbot.json'
            try:
                with open(json_file, 'w', encoding="utf8") as file:
                    json.dump(self.dataset, file, ensure_ascii=False, indent=4)
                self.last_question = None
                return "✅ Thank you! Your input has been added in the correct format (question-answer)."
            except Exception as e:
                return f"❌ Error saving new data: {e}"
        else:
            return "⚠️ There's no previous question to train."


# Example Usage
if __name__ == "__main__":
    user_type = input("Enter user type (employees/user): ").strip().lower()
    chatbot = UltraChatBot(user_type)

    while True:
        user_message = input("You: ")
        if user_message.lower() == "exit":
            print("Chatbot: Goodbye! 👋")
            break
        response = chatbot.process_incoming_message(user_message)
        print(f"Chatbot: {response}")
