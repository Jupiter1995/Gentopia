from typing import List

class Environment:
    def __init__(self, memory: VectorStore):
        self.memory = memory

    def subscribe(self, agent: ConvBaseAgent):
        # Convert agent information to a format that can be stored in the VectorStore
        agent_info = agent.get_agent_info()  # Method to extract relevant information
        # Create a document with the agent information
        document = Document(page_content=agent_info)
        self.memory.add_documents([document])

    def publish(self, data: str):
        # Store the data in the VectorStore
        document = Document(page_content=data)
        self.memory.add_documents([document])

    def get_agents(self) -> List[ConvBaseAgent]:
        agents = []
        documents = self.memory.retriever.get_relevant_documents("")
        for doc in documents:
            # Reconstruct agents from the document content
            agent_info = doc.page_content
            agent = ConvBaseAgent.create_from_info(agent_info)  # Method to reconstruct agent from stored information
            agents.append(agent)
        return agents
