from langchain.chains import LLMChain, SequentialChain
from langchain_openai import ChatOpenAI
from Templates.ItineraryTemplate import ItineraryTemplate
from Templates.MappingTemplate import MappingTemplate
from Templates.ValidationTemplate import ValidationTemplate
from Templates.UpdateItineraryTemplate import UpdateItineraryTemplate
import logging

logging.basicConfig(level=logging.INFO)

# Define Agent class to 1) validate, 2) provide itinerary, 3) map itinerary addresses
class Agent(object):
    def __init__(
        self,
        open_ai_api_key,
        model="gpt-3.5-turbo",
        temperature=0,
        verbose=True,
    ):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self._openai_key = open_ai_api_key

        self.chat_model = ChatOpenAI(
            model=model, temperature=temperature, openai_api_key=self._openai_key
        )
        self.validation_prompt = ValidationTemplate()
        self.itinerary_prompt = ItineraryTemplate()
        self.mapping_prompt = MappingTemplate()
        self.update_itinerary_prompt = UpdateItineraryTemplate()
        self.validation_chain = self._set_up_validation_chain(verbose)
        self.agent_chain = self._set_up_agent_chain(verbose)
        self.update_chain = self._set_up_update_chain(verbose)

    def _set_up_validation_chain(self, verbose=True):
        validation_agent = LLMChain(
            llm=self.chat_model,
            prompt=self.validation_prompt.chat_prompt,
            output_parser=self.validation_prompt.parser,
            output_key="validation_output",
            verbose=verbose,
        )

        overall_chain = SequentialChain(
            chains=[validation_agent],
            input_variables=["query", "format_instructions"],
            output_variables=["validation_output"],
            verbose=verbose,
        )

        return overall_chain

    def _set_up_agent_chain(self, verbose=True):
        travel_agent = LLMChain(
            llm=self.chat_model,
            prompt=self.itinerary_prompt.chat_prompt,
            verbose=verbose,
            output_key="agent_suggestion",
        )

        parser = LLMChain(
            llm=self.chat_model,
            prompt=self.mapping_prompt.chat_prompt,
            output_parser=self.mapping_prompt.parser,
            verbose=verbose,
            output_key="mapping_list",
        )

        overall_chain = SequentialChain(
            chains=[travel_agent, parser],
            input_variables=["query", "format_instructions"],
            output_variables=["agent_suggestion", "mapping_list"],
            verbose=verbose,
        )

        return overall_chain

    def _set_up_update_chain(self, verbose=True):
        
        parser = LLMChain(
            llm=self.chat_model,
            prompt=self.update_itinerary_prompt.chat_prompt,
            verbose=verbose,
            output_key="itinerary",
        )

        overall_chain = SequentialChain(
            chains=[parser],
            input_variables=["query", "mapping_list"],
            output_variables=["itinerary"],
            verbose=verbose,
        )
        
        return overall_chain
    
    def validate_travel(self, query):
        self.logger.info(
            "Validating query with {} model".format(self.chat_model.model_name)
        )
        validation_result = self.validation_chain(
            {
                "query": query,
                "format_instructions": self.validation_prompt.parser.get_format_instructions(),
            }
        )

        validation_test = validation_result["validation_output"].dict()

        if validation_test["plan_is_valid"] == "0":
            self.logger.warning("User request was not valid!")
            print("\n######\n Travel plan is not valid \n######\n")
            print(validation_test["updated_request"])
            return validation_result

        else:
            self.logger.info("Query is valid")
        return validation_test

    def suggest_travel(self, query):
        self.logger.info(
            "Validating query with {} model".format(self.chat_model.model_name)
        )
        validation_result = self.validation_chain(
            {
                "query": query,
                "format_instructions": self.validation_prompt.parser.get_format_instructions(),
            }
        )

        validation_test = validation_result["validation_output"].dict()

        if validation_test["plan_is_valid"] == "0":
            self.logger.warning("User request was not valid!")
            return None, None, validation_test["updated_request"]

        else:
            self.logger.info("Query is valid")
            self.logger.info("Getting travel suggestions")

            self.logger.info(
                "User request is valid, calling agent with {} model".format(
                    self.chat_model.model_name
                )
            )
            try:
                agent_result = self.agent_chain(
                    {
                        "query": query,
                        "format_instructions": self.mapping_prompt.parser.get_format_instructions(),
                    }
                )

                trip_suggestion = agent_result["agent_suggestion"]
                list_of_places = agent_result["mapping_list"].dict()
        
            except:
                return None, None, False

            return trip_suggestion, list_of_places, True
    
    def update_itinerary(self, query, mapping_list):
        try:
            itinerary = self.update_chain(
                {
                    "query": query,
                    "mapping_list": mapping_list,
                }
            )

            trip_suggestion = itinerary["itinerary"]
    
        except:
            return None

        return trip_suggestion