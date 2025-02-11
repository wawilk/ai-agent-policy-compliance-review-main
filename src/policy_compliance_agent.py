import os
from typing import List
from jinja2 import Environment, FileSystemLoader

from semantic_kernel import Kernel
from semantic_kernel.contents import ChatHistory
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureChatPromptExecutionSettings
from semantic_kernel.connectors.ai.function_calling_utils import (
    kernel_function_metadata_to_function_call_format,
)

from semantic_kernel.functions import KernelArguments


from src.plugins.document_parser import DocumentParserPlugin
from src.utils.response_format import PolicyComplianceReport
from azure.identity import DefaultAzureCredential, get_bearer_token_provider  
from dotenv import load_dotenv
load_dotenv()
endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
print("endpoint=",endpoint)
class PolicyComplianceAgent:
    def __init__(self, underlier_policy: str, master_policy: str):
        agent_name = "policy_compliance_agent"
        self.kernel = Kernel()
        
        token_provider = get_bearer_token_provider(  
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"  
        )
        # Create the Azure Chat Completion client.
        self.client = AzureChatCompletion(service_id=agent_name, instruction_role="system", ad_token_provider=token_provider)
        self.kernel.add_service(self.client)

        # Add the document parser plugin to the kernel.
        self.kernel.add_plugin(DocumentParserPlugin(), "DocumentParser")

        # Create the request settings for the agent.
        request_settings = AzureChatPromptExecutionSettings(service_id=agent_name)
        
        # Set the reasoning effort and the maximum completion according to environment variables.
        request_settings.max_completion_tokens = os.getenv('MAX_COMPLETION_TOKENS')
        # change by wayne, next line commented out
        # because using gpt-4o
        #request_settings.reasoning_effort = os.getenv('REASONING_EFFORT')

        # Enable the function calling and disable parallel tool calls for reasoning models.
        request_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
        request_settings.parallel_tool_calls = None
        request_settings.tool_choice = None
        request_settings.tools = [
            kernel_function_metadata_to_function_call_format(f) for f in self.kernel.get_full_list_of_function_metadata()
        ]

        request_settings.response_format = PolicyComplianceReport
        
        # Retrieve the rule list and populate the prompt template for the policy compliance agent.
        path=os.getenv('PATH_TO_RULE_LIST')
        print("PATH_TO_RULE_LIST=",path)
        #open the file for read
        with open(path, 'r', encoding='utf-8') as file:
            self.rule_list = file.read()
        prompt_template_dir=os.getenv('PROMPT_TEMPLATE_DIR')
        print("PROMPT_TEMPLATE_DIR=",prompt_template_dir)
        self.env = Environment(loader=FileSystemLoader(prompt_template_dir))
        self.developer_message = self.env.get_template('policy_compliance_agent.jinja').render(rule_list=self.rule_list, 
                                                                                               underlier_policy=underlier_policy,
                                                                                               master_policy=master_policy)
        print("creating agent")
        # Create the chat completion agent.
        self.agent = ChatCompletionAgent(
                            service_id=agent_name,
                            kernel=self.kernel,
                            name=agent_name,
                            arguments=KernelArguments(settings=request_settings),
                            )
        print("agent created")

    async def get_response(self):
        chat = ChatHistory()
        # change by Wayne, commennted out next line added one below that
        #chat.add_developer_message(self.developer_message)
        chat.add_system_message(self.developer_message)
        #
        chat.add_user_message('Begin your analysis and produce the final compliance report.')
        #argument_overrides=KernelArguments(parallel_tool_calls=None, tool_choice=None)
        print("invoking agent")
        response = self.agent.invoke(chat)
        print("agent invoked")
        return response
    
    async def run(self):
        print("running agent")
        response_generator = await self.get_response()
        print("response_generator=",response_generator)
        async for response in response_generator:
            return response