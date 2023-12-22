import logging
import asyncio

from collections import defaultdict

from typing import List, Union, Optional, Tuple, Type, DefaultDict, Any, Dict
from pydantic import BaseModel, create_model

from gentopia import PromptTemplate

from gentopia.assembler.task import AgentAction
from gentopia.agent.conversational_agent import ConvAgent
from gentopia.agent.react import ReactAgent
from gentopia.model.agent_model import AgentType
from gentopia.output.console_output import ConsoleOutput
from gentopia.llm.client.huggingface import HuggingfaceLLMClient

from gentopia.tools.basetool import BaseTool


logger = logging.getLogger(__name__)

class ReactConvAgent(ConvAgent, ReactAgent):
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
    _messages: DefaultDict[Any, List] = defaultdict(list)
    

    def send(
            self,
            message: Union[Dict, str],
            recipient: ConvAgent,
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
            recipient: ConvAgent,
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
        sender: ConvAgent,
        request_reply: bool = None
    ):
        self._messages[sender.name].append(message)
        print(f"received message: {message}")
        if not request_reply: return

        reply = self.generate_reply(
            message,
            sender
        )
        return self.send(
            reply,
            sender
        )
    
    async def a_receive(self, message: Union[Dict, str], sender: ConvAgent, request_reply: bool = None):
        self._messages[sender.name].append(message)

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
        sender: ConvAgent,
        output: Optional[ConsoleOutput] = ConsoleOutput(),
        **kwargs
    ) -> Union[str, Dict, None]:
            """
            Generate llm response based on the received message from User or other agents

            :param message: instructions from user or messages from other agents during the conversation
            :type message: Union[list[Dict], Dict]
            :param sender: Another conversational agent in the conversation with this agent
            :type sender: ConvAgent
            :raises AssertionError: _description_
            :return: Reply message to send back to the sender
            :rtype: Union[str, Dict, None]
            """
            if all((message is None, sender is None)):
                error_msg = f"Either {message=} or {sender=} must be provided."
                logger.error(error_msg)
                raise AssertionError(error_msg)

            if message is None:
                message = self._messages[sender]

            if isinstance(message, dict):
                instruction = message["content"]
            else:
                instruction = message

            agent_outputs = self.run(instruction, max_iterations=1)
            # agent_outputs = self.stream(instruction=instruction, max_iterations=1)
                
            # instruction = self._compose_prompt(prompt)
            # logging.info(f"Prompt: {prompt}")
            # output.thinking(self.name)
            # reply_completion = self.llm.completion(prompt=instruction, stop=["Observation:"])

            # if response.state == "error":
            #     print("Failed to retrieve response from LLM")
            #     raise ValueError("Failed to retrieve response from LLM")
            
            # output.done()

            # self.intermediate_steps.append([self._parse_output(response.content), ])
            # if isinstance(self.intermediate_steps[-1][0], AgentFinish):
            #     break
            # action = self.intermediate_steps[-1][0].tool
            # tool_input = self.intermediate_steps[-1][0].tool_input

            # content = ""
            # output.print(f"[blue]{self.name}: ")
            # for i in reply_completion:
            #     content += i.content
            #     output.panel_print(i.content, self.name, True)
            # output.clear()
            # print(f"generated reply message: {content}")
            return agent_outputs.output

