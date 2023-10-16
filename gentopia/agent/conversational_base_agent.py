import io
from abc import ABC, ABCMeta, abstractmethod
from typing import List, Dict, Union, Any, Optional, Type, Callable

from gentopia import PromptTemplate
from pydantic import BaseModel, create_model

from gentopia.llm.base_llm import BaseLLM
from gentopia.model.agent_model import AgentType, AgentOutput
from gentopia.memory.api import MemoryWrapper
# from gentopia.environment import Environment -- active this line after Environmentation implementation
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

    @property
    def name(self):
        return self.name
    
    @abstractmethod
    def send(
        self,
        message: Union[Dict, str],
        recipiant: "ConvAgent",
        request_reply: bool = None
    ):
        """Send method: send message to another agent"""
        pass
    
    async def a_send(
            self,
            message: Union[Dict, str],
            recipiant: "ConvAgent",
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

    def reset(self):
        """Reset the agent, clear the memory"""
        pass

    def learn(
            self,
            agent_name: Optional["ConvAgent"],
            top_k: int = 10
    ):
        """Add environment available knowledge to its own memory"""
        texts = self.subscribe_from_env(
            agent_name,
            top_k
        )
        self.memory.

    def publish_to_env(
            self,
            message: Union[Dict, str],
            topic_name: Union[list[str], str],
            request_ackownledge: bool = None
    ):
        """Publish message to a topic or multiple topics using agent names as topic names"""

        if not self.env or not isinstance(self.env, Environment):
            raise("No valid environment found! Please setup the environment for this agent before proceed.")
        
        ackownledge = self.env.publish(
            message,
            topic_name,
            request_ackownledge
        )

        if request_ackownledge:
            return ackownledge

    def subscribe_from_env(
            self,
            topic_name: Union[list[str], str] = None,
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
            raise("Subscribed topic(s) was not available to current environment!")
    
    def _get_env_agents(self):
        """Get all the agent names in this same environment"""
        return self.env.get_agents()

    def register_replay(self, ):
        pass
    
