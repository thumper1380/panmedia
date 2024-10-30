# retrieve the langchain agent
from langchain.globals import set_debug
from langchain.agents import AgentType, initialize_agent as ia, create_openai_tools_agent
from langchain.tools import BaseTool
from typing import Sequence, List, Optional, Dict, Any, Union, Tuple
from .prompts import SYSTEM_MESSAGE
from django.utils import timezone
from .models import Conversation
from langchain.agents import AgentExecutor, OpenAIFunctionsAgent
from .callbacks import DjangoCallbackHandler
from .memory import DjangoConversationBufferMemory as DjangoConversationBufferSummaryMemory
from langchain_community.chat_models import ChatOpenAI

from langchain.callbacks.manager import CallbackManager
from django.conf import settings
from langchain.prompts import SystemMessagePromptTemplate, MessagesPlaceholder
from langchain import hub

GPT_3 = "gpt-3.5-turbo-1106"
MEMORY_KEY = "chat_history"
GPT_4 = "gpt-4-1106-preview"

# import django time zone


def handle_error(error) -> str:
    """return last chars of error message."""
    return str(error)


def initialize_agent(conversation: Conversation, update, debug=True, tools: Sequence[BaseTool] = None) -> AgentExecutor:
    # set_debug(debug)

    handler = DjangoCallbackHandler(conversation=conversation, update=update)

    llm = ChatOpenAI(
        model=GPT_3,
        openai_api_key=settings.OPENAI_API_KEY,
        callbacks=[handler],
        temperature=0.8,
        # max_tokens=300,
        # streaming=True
    )

    current_date_time = timezone.now().strftime("%d/%m/%Y %H:%M:%S")

    system_message_prompt = SystemMessagePromptTemplate.from_template(
        template=SYSTEM_MESSAGE,
        partial_variables={
            "current_date_time": current_date_time,
        }
    )

    memory = DjangoConversationBufferSummaryMemory(llm=llm, conversation=conversation, memory_key=MEMORY_KEY, return_messages=True,)

    # prompt = hub.pull("hwchase17/openai-tools-agent")

    # agent_executor = ia(
    #     llm=llm,
    #     tools=tools,
    #     agent=AgentType.OPENAI_FUNCTIONS,
    #     # agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    #     agent_kwargs={
    #         "extra_prompt_messages": [MessagesPlaceholder(variable_name=MEMORY_KEY)],
    #         "system_message": system_message_prompt,
    #     },
    #     memory=memory,
    #     max_iterations=10,
    #     callback_manager=CallbackManager(handlers=[handler]),
    #     early_stopping_method="generate",
    #     verbose=debug,
    #     handle_parsing_errors=handle_error,
    # )

    propmt = hub.pull("hwchase17/openai-tools-agent")
    
    print("propmt", propmt.messages)
    
    agent = create_openai_tools_agent(
        tools=tools,
        llm=llm,
        prompt=propmt,
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=debug,
        
    )

    return agent_executor
