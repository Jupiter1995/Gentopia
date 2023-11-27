import argparse
import os

# from gentopia import chat
from gentopia.assembler.agent_assembler import AgentAssembler
from gentopia.output import enable_log


def main():

    enable_log(log_level='info')

    # parser = argparse.ArgumentParser(description='Assemble an agent with given name.')
    # parser.add_argument('name_training', type=str, help='Name of the training agent to assemble.')
    # parser.add_argument('name_nutrition', type=str, help='Name of the nutrition agent to assemble.')
    # parser.add_argument('--print_agent', action='store_true', help='Print the agent if specified.')

    # args = parser.parse_args()
    # trainer = args.name_training
    # nutritionist = args.name_nutrition
    # print_agent = args.print_agent

    trainer = "mark"
    nutritionist = "elena"
    print_agent = "True"

    # check if agent_name is under directory ./gentpool/pool/
    if not os.path.exists(f'./multi_agent_test/agents/{trainer}'):
        raise ValueError(f'Agent {trainer} does not exist. Check ./agents/ for available agents.')
    
    if not os.path.exists(f'./multi_agent_test/agents/{nutritionist}'):
        raise ValueError(f'Agent {nutritionist} does not exist. Check ./agents/ for available agents.')

    trainer_config_path = f'./multi_agent_test/agents/{trainer}/agent.yaml'
    nutritionist_config_path = f"./multi_agent_test/agents/{nutritionist}/agent.yaml"

    trainer_assembler = AgentAssembler(file=trainer_config_path)
    nutritionist_assembler = AgentAssembler(file=nutritionist_config_path)

    begin_messages = input("Please input your expectations of your training goal and also your food preference:")

    # # assembler.manager = LocalLLMManager()
    # print(f">>> Assembling agent {agent_name}...")
    trainer_agent = trainer_assembler.get_agent()
    nutritionist_agent = nutritionist_assembler.get_agent()

    trainer_agent.initiate_conversation(nutritionist_agent, message=begin_messages)

    


if __name__ == '__main__':
    main()