
from langchain import PromptTemplate, LLMChainycRubwalWHNmjxzgt79bSdbBDt14oNWftzkMc2Lg
from langchain.llms import Cohere
from pydantic import BaseModel
from typing import Optional
import wikipediaapi
import getpass

COHERE_API_KEY = getpass.getpass('Enter your Cohere API Key: ')
cohere_llm = Cohere(cohere_api_key=COHERE_API_KEY, model="command")

def fetch_ipc_summary():
    user_agent = "IPCChatbot/1.0 (contact: myemail@example.com)"
    wiki = wikipediaapi.Wikipedia(user_agent=user_agent, language='en')
    page = wiki.page("Indian Penal Code")
    if not page.exists():
        raise ValueError("The Indian Penal Code page does not exist on Wikipedia.")
    return page.text[:5000]

ipc_content = fetch_ipc_summary()

class IPCResponse(BaseModel):
    section: Optional[str]
    explanation: Optional[str]

prompt_template = PromptTemplate(
    input_variables=["question"],
    template="""You are a legal assistant chatbot specialized in the Indian Penal Code (IPC). Refer to the following IPC document content to answer the user's query: {ipc_content} User Question: {question} Provide a detailed answer, mentioning the relevant section if applicable."""
)

def get_ipc_response(question: str) -> IPCResponse:
    formatted_prompt = prompt_template.format(ipc_content=ipc_content, question=question)
    response = cohere_llm.predict(formatted_prompt)
    if "Section" in response:
        section = response.split('Section')[1].split(':')[1].split('.')[0].strip()
        explanation = response.split(':', 1)[-1].strip()
    else:
        section = None
        explanation = response.strip()
    return IPCResponse(section=section, explanation=explanation)

from IPython.display import display
import ipywidgets as widgets

def display_response(response: IPCResponse):
    print(f"Section: {response.section if response.section else 'N/A'}")
    print(f"Explanation: {response.explanation}")

def on_button_click(b):
    user_question = text_box.value
    try:
        response = get_ipc_response(user_question)
        display_response(response)
    except Exception as e:
        print(f"Error: {e}")

text_box = widgets.Text(
    value='',
    placeholder='Ask about the Indian Penal Code',
    description='You:',
    disabled=False
)

button = widgets.Button(
    description='Ask',
    disabled=False,
    button_style='',
    tooltip='Click to ask a question about IPC',
    icon='legal'
)

button.on_click(on_button_click)
display(text_box, button)

