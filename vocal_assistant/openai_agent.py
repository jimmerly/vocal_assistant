from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
OpenAI.api_key = os.getenv('OPENAI_API_KEY')


class OpenAIAgent:
    def __init__(self, model='gpt-3.5-turbo'):
        self.client = OpenAI()
        self.model = model
        self.memory = []
        self.memory_limit = 10

    def create_chat_completion(self, messages):
        response = self.client.chat.completions.create(
            model = self.model,
            messages = messages
        )

        return response.choices[0].message.content
        
    def get_response(self, command):
        messages = [
                {"role": "system", "content": "You are a vocal assistant. You have to answer in a simple, efficient and concise way. Your answer should not take more than 30 seconds to say out loud."},
            ]
        
        messages.extend(self.memory)

        messages.append({"role": "user", "content": command})
        
        assistant_reply = self.create_chat_completion(messages)

        if assistant_reply:
            self.memory.extend([
                {"role": "user", "content": command},
                {"role": "assistant", "content": assistant_reply}
            ])
            self.memory = self.memory[-self.memory_limit:]
        return assistant_reply
    
    def get_command_label(self, command):
        messages=[
                {"role": "system", "content": "You are a vocal assistant."},
                {"role": "system", "content": "Your role is to classify the user's command and return only the corresponding label."},
                {"role": "system", "content": "The labels are: to-do list, weather, trivia, joke, normal questions."},
                {"role": "system", "content": "if you recognize the user's command as a todo list request (for example), then return 'to-do list'."},
                {"role": "user", "content": command}
            ]

        label = self.create_chat_completion(messages)
        return label
    
    def get_todo_command_label(self, command):
        messages = [
                {"role": "system", "content": "You are a vocal assistant."},
                {"role": "system", "content": "You must classify the following command for a todo list functionality, only return one of the followings."},
                {"role": "system", "content": "add, remove, list, none"},
                {"role": "system", "content": "For example if the user says 'I want to go running tomorrow at 10 am', return just 'add'."},
                {"role": "user", "content": command}
            ]
        
        label = self.create_chat_completion(messages)
        return label
    
    def generated_todo(self, command):
        messages = [
            {"role": "system", "content": "You are a vocal assistant."},
            {"role": "system", "content": "The user is trying to add a task to their todo list, your job is to format their request into a concise task."},
            {"role": "system", "content": "For instance, if the user says 'I need to buy milk at 5 pm', you should rephrase it as 'Buy milk at 5 pm'."},
            {"role": "system", "content": "Ignore any word that are not part of the task itself."},
            {"role": "user", "content": command}
        ]

        todo = self.create_chat_completion(messages)
        return todo
    
    def get_approve_deny(self, command):
        messages = [
            {"role": "system", "content": "You are an assistant tasked with classifying user responses."},
            {"role": "system", "content": "The user will approve or deny a proposal. Determine whether the user approves or denies."},
            {"role": "system", "content": "for example, user says 'yes' mean approve; user says 'no' mean deny."},
            {"role": "system", "content": "Return 'approve' or 'deny'"},
            {"role": "user", "content": command}
        ]

        decision = self.create_chat_completion(messages)
        return decision
    
    def recognize_todo(self, tasks, command):
        messages = [
            {"role": "system", "content": "Your task is to match the user's command to one of the element of a todo list."},
            {"role": "system", "content": "The user wants to remove a specific task from his to-do list."},
            {"role": "system", "content": "Identify the task from their command and return it"},
            {"role": "system", "content": "if you find a task that matches his request, return the exact task text, nothing more. Else, return 'none'."},
        ]

        for index, task in enumerate(tasks):
            messages.append(
                {"role": "system", "content": f"{index+1}: {task}"}
            )

        messages.append(
            {"role": "user", "content": command}
        )

        todo = self.create_chat_completion(messages)
        return todo
    
    def extract_information(self, info, command):
        messages = [
            {"role": "system", "content": "You are an AI assistant tasked with extracting specific information from user commands."},
            {"role": "system", "content": f"Extract the following detail: {info}"},
            {"role": "system", "content": f"If the user's message contains any '{info}', return only that detail."},
            {"role": "system", "content": f"If the user's message doesn't contain any '{info}' return only 'none'."},
            {"role": "system", "content": f"Remember, your response should only contain the {info} or 'none'."},
            {"role": "user", "content": command}
        ]

        extract = self.create_chat_completion(messages)

        return extract
    
    def rephrase(self, text):

        messages = [
            {"role": "system", "content": "You are a helpful rephrasing assistant. You need to rephrase a vocal assistant message in a different, yet equivalent way."},
            {"role": "system", "content": "Keep the same meaning and average length, but change the structure and words if possible."},
            {"role": "system", "content": "Try to avoid using uncommon or complicated words in the rephrased version, keep it simple."},
            {"role": "system", "content": "Keep in mind that the text should be simple and concise, and shouldn't take more than 20 seconds to say out loud."},
            {"role": "user", "content": text}
        ]

        rephrased_command = self.create_chat_completion(messages)

        return rephrased_command
    
    def check_trivia_answer(self, correct_answer, user_answer):
        messages = [
            {'role': 'system', 'content': 'You are an AI assistant.'},
            {'role': 'system', 'content': 'You will check if the user answer match the correct answer, case insensitive'},
            {'role': 'system', 'content': 'The user might use phrases like "I think", "maybe", "I believe", etc...'},
            {'role': 'system', 'content': 'But you need to focus on if any part of the user answer match the correct answer'},
            {'role': 'system', 'content': 'if match, reply "correct", if not, replay "incorrect"'},
            {'role': 'system', 'content': 'the correct answer is {correct_answer}, the user answered {user_answer}.'}
        ]

        judge = self.create_chat_completion(messages)
        return judge