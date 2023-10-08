## This is for project development tracking, *don't merge* to the main branch

### Main structure for multi-agent framework development
#### 1 Prepare conversation base agent (may not use the existing base_agent implementation)
- Conversational abilities based on AutoGen, like send, intiatiate conversation, receive, end conversation, etc.
- sub/pub ability to the env memory based on MetaGPT

#### 2 Setup environment for handling agents and messages (may setup to be able to handle multi-topics)
- Confirm existing memory implementation first
- for now, similar to MetaGPT, publishing the message to the env memory everytime
- in the future, only when reaching agreement (definition TBD) between agents, then publish to env memory and treated as common knowledge. New added agent can sub directly from env memory to learn.
  
#### 3 Update assembler_agent 
- take new conversational agent inputs 
- connect to env and enable pub/sub from and to agent

