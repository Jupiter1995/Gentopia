import warnings
from typing import Union, Optional

from gentopia.agent.conversational_base_agent import ConvBaseAgent


class Environment:
    def __init__(self, name: str):


        self.agents: Dict[str, ConvBaseAgent] = {}  # Dictionary to store active agents
        self.messages = {}  # Dictionary to store messages from agents
        self._name = name
        
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, new_name: str) -> None:
        warnings.warn("You are changing the name of current environment. Please make sure the new name is still unique.")
        self._name = new_name

    def add_agent(self, agent: ConvBaseAgent):
        """
        Add a ConvBaseAgent to the environment.

        :param agent: The ConvBaseAgent instance to be added.
        :type agent: ConvBaseAgent
        """
        agent_name = agent.name
        self.agents[agent_name] = agent


    def publish(self, agent: ConvBaseAgent, message: str, **kwargs):
        """
        Store a message from an agent in the environment.

        :param agent: The ConvBaseAgent instance that is sending the message.
        :type agent: ConvBaseAgent
        :param message: The message to be stored in the environment.
        :type message: str
        """
        agent_name = agent.name
        if agent_name not in self.messages:
            self.messages[agent_name] = []
        self.messages[agent_name].append(message)

    def subscribe(self, topics: Union[list(ConvBaseAgent), ConvBaseAgent], top_k: Optional[int] = 5):
        """
        Retrieve messages sent to an agent from the environment.

        :param agent: The ConvBaseAgent instance that wants to retrieve messages.
        :type agent: ConvBaseAgent
        :return: A list of messages sent to the agent from the environment.
        :rtype: List[str]
        """
        agent_name = agent.name
        if agent_name in self.messages:
            return self.messages[agent_name]
        else:
            return []
