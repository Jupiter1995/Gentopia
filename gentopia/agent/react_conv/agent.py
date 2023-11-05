import logging
import asyncio

from collections import defaultdict

from typing import List, Union, Optional, Tuple, Type, Dict
from pydantic import BaseModel, create_model

from gentopia import PromptTemplate

from gentopia.assembler.task import AgentAction, AgentFinish
from gentopia.agent.conversational_base_agent import ConvBaseAgent
from gentopia.agent.react import ReactAgent
from gentopia.model.agent_model import AgentType, AgentOutput
from gentopia.llm.client.huggingface import HuggingfaceLLMClient

from gentopia.tools.basetool import BaseTool


logger = logging.getLogger(__name__)

class ReactConvAgent(ConvBaseAgent, ReactAgent):
    """
    Sequential ReactAgent class inherited from Conversational BaseAgent. Implementing ReAct agent paradigm https://arxiv.org/pdf/2210.03629.pdf

    :param name: Name of the agent, defaults to "ReactAgent".
    :type name: str, optional
    :param type: Type of the agent, defaults to AgentType.react.
    :type type: AgentType, optional
    :param version: Version of the agent.
    :type version: str
    :param description: Description of the agent.
    :type description: str
    :param target_tasks: List of target tasks for the agent.
    :type target_tasks: list[str]
    :param llm: Language model that the agent uses.
    :type llm: HuggingfaceLLMClient
    :param prompt_template: Template used to create prompts for the agent, defaults to None.
    :type prompt_template: PromptTemplate, optional
    :param plugins: List of plugins used by the agent, defaults to None.
    :type plugins: List[Union[BaseTool, BaseAgent]], optional
    :param examples: Fewshot examplars used for the agent, defaults to None.
    :type examples: Union[str, List[str]], optional
    :param args_schema: Schema for the arguments of the agent
    :type args_schema: Optional[Type[BaseModel]], optional
    """
    name: str = "ReactAgent_Conv"
    type: AgentType = AgentType.react
    version: str
    description: str
    target_tasks: list[str]
    llm: HuggingfaceLLMClient
    prompt_template: PromptTemplate
    plugins: List[BaseTool]
    examples: Union[str, List[str]] = None
    args_schema: Optional[Type[BaseModel]] = create_model("ReactArgsSchema", instruction=(str, ...))

    intermediate_steps: List[Tuple[AgentAction, str]] = []
    _messages: dict(list) = defaultdict(list)
    

    def send(
            self,
            message: Union[Dict, str],
            recipient: ConvBaseAgent,
            request_reply: bool = None
    ):
      recipient.receive(
           message,
           self,
           request_reply
      )

    async def a_send(
            self,
            message: Union[Dict, str],
            recipient: ConvBaseAgent,
            request_reply: bool = None
    ):
     await recipient.a_receive(
         message,
         self,
         request_reply
     )

    def receive(
        self,
        message: Union[Dict, str],
        sender: ConvBaseAgent,
        request_reply: bool = None
    ):
        if not request_reply: return

        reply = self.generate_reply(
            message,
            sender
        )
        return self.send(
            reply,
            sender
        )
    
    async def a_receive(self, message: Dict | str, sender: ConvBaseAgent, request_reply: bool = None):
        if not request_reply: return

        reply = await self.a_generate_reply(
            message,
            sender
        )
        if reply:
            await self.a_send(
                reply,
                sender
            )

    def generate_reply(
        self,
        message: Union[list[Dict], Dict],
        sender: ConvBaseAgent,
        **kwargs
    ) -> Union[str, Dict, None]:
            """
            Generate llm response based on the received message from User or other agents

            :param message: prompts from user or messages from other agents during the conversation
            :type message: Union[list[Dict], Dict]
            :param sender: Another conversational agent in the conversation with this agent
            :type sender: ConvBaseAgent
            :raises AssertionError: _description_
            :return: Reply message to send back to the sender
            :rtype: Union[str, Dict, None]
            """
            if all((message is None, sender is None)):
                error_msg = f"Either {messages=} or {sender=} must be provided."
                logger.error(error_msg)
                raise AssertionError(error_msg)

            if message is None:
                messages = self._messages[sender]

            if isinstance(messages, dict):
                prompt = messages["content"]
            else:
                prompt = messages

            reply_completion = self.llm.completion(prompt=prompt)
            return reply_completion.to_dict()

