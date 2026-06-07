from email import message

from dotenv import load_dotenv
from langsmith import traceable

load_dotenv()

import langchain
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

MAX_ITERATION = 10
# MODEL = "qwen3.5:0.8b"
MODEL = "gemma3:270m"

## ---- defined tools


@tool
def get_product_price(product: str) -> float:
    """Lookup the price of the product in the catalog
    Args:
        product (str): _description_
    Returns:
        float: _description_
    """
    print(f">>Executing get_product_price (product='{product}')")
    prices = {"laptop": 1299.99, "headphones": 149.95, "keyboard": 89.5}
    return prices.get(product, 0)


@tool
def apply_discount(price: float, discount_tier: str) -> float:
    """apply discount tire to a price and return the final price
    Available tiers: bronze,silver,gold
    Args:
        price (float): _description_
        discount_tier (str): _description_

    Returns:
        float: _description_
    """
    discount_percentages = {"bronze": 5, "silver": 12, "gold": 23}
    discount = discount_percentages.get(discount_tier, 0)
    return round(price * (1 - discount / 100), 2)


##-- defination Agent loop
##traceable is gives the traceable in langchain smith
@traceable(name="Langchain Agent Loop")
def run_agent(question: str):
    tools = [get_product_price, apply_discount]
    tools_dict = {t.name: t for t in tools}

    # llm = init_chat_model(f"ollama:{MODEL}", temperature=0)

    llm = init_chat_model("gpt-4.1", model_provider="openai", temperature=0)
    llm_with_tools = llm.bind_tools(tools)

    print(f"Question:{question}")
    print("=" * 60)

    ## message for LLM brain
    messages = [
        SystemMessage(
            content="You are helpful shopping assistant"
            "You have access to a product catalog tool and discount tool"
            "STRICT RULE- you must follow exactly these:\n"
            "1.Never guess or assume product price."
            "You must call get_product_price to get the real price\n"
            "2.Only call apply_discount after you have receiced the price from get_product_price, pass the exact price"
            " returned by get_product_price - Do not pass made up number\n"
            "3.Never calculate discount using yourself using math, always use apply_discount tool"
            "4. If the user does not specify discount tier, ask them which tier to use. do not assume one"
        ),
        HumanMessage(content=question),
    ]

    # ---now call LLM with iteration until LLM gives result
    for iteration in range(1, MAX_ITERATION + 1):
        # print(iteration)
        _ai_messages = llm_with_tools.invoke(messages)
        tools_call = _ai_messages.tool_calls

        # if not tool_call this is the final answer
        if not tools_call:
            print(f"Final Answer: {_ai_messages.content}")
            return _ai_messages.content

        # process ony FIRST tool call --force one tool per iteration, these days LLM can return multiple tool
        tool_call = tools_call[0]
        tool_name = tool_call.get("name")
        tool_args = tool_call.get("args", {})
        tool_call_id = tool_call.get(
            "id"
        )  # id will be helping us to trace the tool call

        print(f" [Tool selected] {tool_name} with args: {tool_args}")
        ##get tool to use from tool_dict by tool name;this variable will be python langchain tool which will use to call obeservation
        tool_to_use = tools_dict.get(tool_name)
        if tool_to_use is None:
            raise ValueError(f"Tool '{tool_name}' not found")
        observation = tool_to_use.invoke(tool_args)

        print(f" [Tool Result] {observation}")
        ## now append ai_message and tool result to message so that LLM will not what are the result in history
        messages.append(_ai_messages)
        messages.append(
            ToolMessage(content=str(observation), tool_call_id=tool_call_id)
        )


if __name__ == "__main__":
    print("Hello Langchain Agent")
    print()
    run_agent("what is the price of laptop after applying bronze tier discount?")
    print("=" * 60)
    print("Compeleted")
