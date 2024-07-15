from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

# Define Validation class for pydantic Field.
# This allows you to specify validation rules for fields and set default values
# Pydantic forces the output model type (ex. float to int), but if its not parsable, it throws validation error
class Validation(BaseModel):
    plan_is_valid: str = Field(
        description="This field is 'True' if the plan is feasible, 'False' otherwise"
    )
    updated_request: str = Field(description="Your update to the plan")


# Define ValidationTemplate
class ValidationTemplate(object):
    def __init__(self):
        # System template gives context and sets the stage for LLM
        self.system_template = """
      You are a travel planner agent who helps users make detailed and accurate travel plans.

      The user's request will be denoted by four hashtags. Determine if the user's
      request is reasonable and achievable within the constraints they set.

      A valid request should contain the following:
      - A start and end location
      - A trip duration that is reasonable given the start and end location
      - Some other details, like the user's interests and/or preferred mode of transport

      Any request that is not viable or contains potentially dangerous or harmful activities is not valid,
      regardless of what other details are provided.

      If the request is not valid, set
      plan_is_valid = "0" and use your travel knowledge to update the request to make it valid,
      keeping the request within 100 words.

      Otherwise, if the request seems reasonable, set plan_is_valid = "1" and don't revise the request.

      {format_instructions}
    """

        # Human template is inputted as a query variable
        self.human_template = """
      ####{query}####
    """

        self.parser = PydanticOutputParser(pydantic_object=Validation)

        self.system_message_prompt = SystemMessagePromptTemplate.from_template(
            self.system_template,
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            },
        )
        self.human_message_prompt = HumanMessagePromptTemplate.from_template(
            self.human_template, input_variables=["query"]
        )

        self.chat_prompt = ChatPromptTemplate.from_messages(
            [self.system_message_prompt, self.human_message_prompt]
        )
