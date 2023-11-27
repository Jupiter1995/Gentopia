import io
from abc import ABC, ABCMeta, abstractmethod
from typing import List, Dict, Union, Any, Optional, Type, DefaultDict
from collections import defaultdict

from gentopia import PromptTemplate
from pydantic import BaseModel, create_model

from gentopia.llm.base_llm import BaseLLM
from gentopia.model.agent_model import AgentType, AgentOutput
from gentopia.memory.api import MemoryWrapper
from gentopia.output.console_output import ConsoleOutput
from gentopia.environment.environment import Environment
from rich import print as rprint

from gentopia.tools import BaseTool

class ConvBaseAgent(ABC, BaseModel):
    """Converstaional Base Agent class defining the essential attributes and methods for an interactive ALM Agent.

    :param name: The name of the agent.
    :type name: str
    :param type: The type of the agent.
    :type type: AgentType
    :param version: The version of the agent.
    :type version: str
    :param description: A brief description of the agent.
    :type description: str
    :param target_tasks: List of target tasks for the agent.
    :type target_tasks: List[str]
    :param env: The environment where this agent residuals
    :type env: str
    :param llm: BaseLLM instance or dictionary of BaseLLM instances (eg. for ReWOO, two separate LLMs are needed).
    :type llm: Union[BaseLLM, Dict[str, BaseLLM]]
    :param prompt_template: PromptTemplate instance or dictionary of PromptTemplate instances. (eg. for ReWOO, two separate PromptTemplates are needed).
    :type prompt_template: Union[PromptTemplate, Dict[str, PromptTemplate]]
    :param plugins: List of plugins available for the agent. PLugins can be tools or other agents.
    :type plugins: List[Any]
    :param args_schema: Schema for arguments, defaults to a model with "instruction" of type str.
    :type args_schema: Optional[Type[BaseModel]]
    :param memory: An instance of MemoryWrapper.
    :type memory: Optional[MemoryWrapper]
    """

    name: str
    type: AgentType
    version: str
    description: str
    target_tasks: List[str]
    env: Optional[Environment] = None
    llm: Union[BaseLLM, Dict[str, BaseLLM]]
    prompt_template: Union[PromptTemplate, Dict[str, PromptTemplate]]
    plugins: List[Any]
    args_schema: Optional[Type[BaseModel]] = create_model("ArgsSchema", instruction=(str, ...))
    memory: Optional[MemoryWrapper]
    max_consecutive_auto_reply: Optional[int] = 100

    _conv_history: DefaultDict[Any, List] = defaultdict(list)
    
    def initiate_conversation(
        self,
        recipient: "ConvAgent",
        clear_history: Optional[bool] = True,
        request_reply: Optional[bool] = True,
        **context
    ) -> None:
        """
        Initiate the conversation with other agent

        :param recipient: The agent will be talked with
        :type recipient: ConvAgent
        :param clear_history: whether to clear the conversation history with the recipient agent, defaults to True
        :type clear_history: Optional[bool], optional
        :return: None
        :rtype: None
        """
        if clear_history:
            self.clear_conv_history(recipient)

        messages = self.generate_first_message(**context)
        self.send(messages, recipient=recipient, request_reply=request_reply)
        

    @abstractmethod
    def send(
        self,
        message: Union[Dict, str],
        recipient: "ConvAgent",
        request_reply: bool = None
    ):
        """Send method: send message to another agent"""
        pass
    
    async def a_send(
            self,
            message: Union[Dict, str],
            recipient: "ConvAgent",
            request_reply: bool = None
    ):
        """Async send method: send message to another agent"""
        pass

    @abstractmethod
    def receive(
        self,
        message: Union[Dict, str],
        sender: "ConvAgent",
        request_reply: bool = None
    ):
        pass

    async def a_receive(
            self,
            message: Union[Dict, str],
            sender: "ConvAgent",
            request_reply: bool = None
    ):
        pass

    @abstractmethod
    def generate_reply(
        self,
        message: Union[list[Dict], Dict],
        sender: "ConvAgent",
        **kwargs
    ):
        """Abstract method for reply generation"""
        pass
  
    
    async def a_generate_reply(
            self,
            message: Union[list[Dict], Dict],
            sender: "ConvAgent",
            **kwargs
    ):
        pass

    def clear_conv_history(self, recipient: "ConvAgent"):
        """
        Clear conversation history with the recipient agent
        (Update to utilize memory in the future)

        :param recipient: The agent associated with the targeted conversation history
        :type recipient: ConvAgent
        """
        if recipient in self._conv_history:
            self._conv_history[recipient].clear()
        else:
            self._conv_history.clear()

    def generate_first_message(self,**context):
        return context["message"]

    def learn(
            self,
            agent_name: Union[list[str], str],
            top_k: int = 10
    ) -> None:
        """Add environment available knowledge to its own memory"""
        texts = self.subscribe_from_env(
            agent_name,
            top_k
        )
        self.memory.save_memory_I(
            query="environment messages",
            response=texts,
            output=ConsoleOutput
        )

    @classmethod
    def publish_to_env(
            self,
            message: Union[Dict, str],
            request_ackownledge: Optional[bool] = False
    ):
        """
        Publish message to a topic or multiple topics using agent names as topic names

        :param message: _description_
        :type message: Union[Dict, str]
        :param topic_name: _description_
        :type topic_name: Union[list[str], str]
        :param request_ackownledge: _description_, defaults to None
        :type request_ackownledge: bool, optional
        :return: _description_
        :rtype: _type_
        """

        if not self.env or not isinstance(self.env, Environment):
            raise("No valid environment found! Please setup the environment for this agent before proceed.")
        
        ackownledge = self.env.publish(
            message,
            self.name,
            request_ackownledge
        )

        if request_ackownledge:
            return ackownledge

    @classmethod
    def subscribe_from_env(
            self,
            topic_name: Union[list[str], str],
            top_k: int
        ):
        topic_list = self._get_env_agents()
        
        if not topic_name:
            knowledge_message = self.env.subscribe(
                topic_list,
                top_k
            )
            return knowledge_message
        elif topic_name in topic_list:
            knowledge_message = self.env.subscribe(
                topic_name,
                top_k
            )
            return knowledge_message
        else:
            raise("Subscribed agent(s) was not available to current environment!")
    
    def _get_env_agents(self):
        """Get all the agent names in this same environment"""
        return self.env.get_agents()

    def register_reply(self, ):
        pass
    
    @property
    def conversation_history(self, recipient: Optional["ConvAgent"] = None):
        if recipient:
            return self._conv_history[recipient]
        else:
            return self._conv_history