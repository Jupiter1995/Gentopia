## Essential functionality definition for *Environment* class [Updated by Nov. 3 2023]
#### `subscribe()` [needs to be updated]
- Should allow to subscribe to more than one topics. 
- The subscribtion will be based on agent name(s)
- Should provide an variable to specific how much messages the subscirber want to subscribe, something like top_k

#### `publish()` [needs to be updated]
- Using agent name(s) as topic(s) to publish messages to the env
- Allow user to customize whether receive a acknowledgement after publishing.

#### `get_agents()` [needs to be implemented]
- retrieve back all the agent names in current environment.

#### Other questions need to be solved
- when intializing different agents, sometime we want to set the same env to those agents, but sometimes we don't. We need to a way to retrieve the initialized environment.