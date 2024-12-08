from legal_chatbot import MULTI_PROMPT_ROUTER_TEMPLATE as RounterTemplate
from legal_chatbot import LAWYER_PROMPT_TEMPLATE as LawyerTemplate
from legal_chatbot import SEARCH_PROMPT_TEMPLATE as SearchTemplate
from langchain.prompts import PromptTemplate
from langchain.chains.router.llm_router import RouterOutputParser
from langchain_core.runnables import RunnableLambda, RunnableSerializable
from langchain_core.language_models.llms import LLM


class RouterChain:

    @classmethod
    def from_llm(cls, llm: LLM, *args, **kwargs):
        prompt_dicts = [
            {
                "key": "lawyer",
                "description": "适合回答法律相关问题",
                "template": LawyerTemplate,
            },
            {
                "key": "search",
                "description": "适合回答",
                "template": SearchTemplate,
            },
        ]
        destinations = [f"{p['key']}: {p['description']}" for p in prompt_dicts]
        router_template = RounterTemplate.format(destinations="\n".join(destinations))
        router_prompt = PromptTemplate(
            template=router_template,
            input_variables=["input"],
        )
        # print(router_template)
        chain = router_prompt | llm | RunnableLambda(cls.parse_output)
        return chain

    @classmethod
    def parse_output(cls, output):
        parser = RouterOutputParser()
        data = parser.parse(output)
        # return data.get("destination", None)
        return data


# class
