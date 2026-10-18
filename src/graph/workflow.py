import os
import sqlite3
from functools import lru_cache

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.types import interrupt

from src.agents.tools import RETRIEVAL_TOOLS
from src.config import (
    AUTHORIZATION_TERMS,
    CHECKPOINT_DATABASE_PATH,
    CONTROLLED_ACTION_TERMS,
    GOOGLE_API_KEY_ENV,
    INSUFFICIENT_EVIDENCE_TERMS,
    LLM_MODEL_NAME,
    LLM_TEMPERATURE,
    SAFETY_TERMS,
)
from src.graph.state import SupportState
from src.prompts import (
    AUTHORIZATION_REVIEW_REASON,
    EMPTY_EDIT_RESPONSE,
    INSUFFICIENT_EVIDENCE_REVIEW_REASON,
    REJECTED_RESPONSE,
    SAFETY_REVIEW_REASON,
    SYSTEM_PROMPT,
)


load_dotenv()


@lru_cache(maxsize=1)
def get_llm() -> ChatGoogleGenerativeAI:
    api_key = os.getenv(GOOGLE_API_KEY_ENV)

    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY was not found. Add it to the .env file."
        )

    return ChatGoogleGenerativeAI(
        model=LLM_MODEL_NAME,
        google_api_key=api_key,
        temperature=LLM_TEMPERATURE,
    )


@lru_cache(maxsize=1)
def get_tool_calling_llm():
    return get_llm().bind_tools(RETRIEVAL_TOOLS)


def support_agent(
    state: SupportState,
) -> dict:
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        *state["messages"],
    ]

    response = get_tool_calling_llm().invoke(messages)

    return {
        "messages": [response],
    }


def get_latest_human_text(
    state: SupportState,
) -> str:
    for message in reversed(state["messages"]):
        if isinstance(message, HumanMessage):
            return str(message.text)

    return ""


def get_latest_ai_message(
    state: SupportState,
) -> AIMessage | None:
    for message in reversed(state["messages"]):
        if isinstance(message, AIMessage):
            return message

    return None


def determine_review_reason(
    user_text: str,
    draft_response: str,
) -> str | None:
    combined_text = (
        f"{user_text}\n{draft_response}"
    ).lower()

    if any(
        term in combined_text
        for term in SAFETY_TERMS
    ):
        return SAFETY_REVIEW_REASON

    contains_authorization = any(
        term in user_text.lower()
        for term in AUTHORIZATION_TERMS
    )

    contains_controlled_action = any(
        term in user_text.lower()
        for term in CONTROLLED_ACTION_TERMS
    )

    if contains_authorization and contains_controlled_action:
        return AUTHORIZATION_REVIEW_REASON

    if any(
        term in draft_response.lower()
        for term in INSUFFICIENT_EVIDENCE_TERMS
    ):
        return INSUFFICIENT_EVIDENCE_REVIEW_REASON

    return None


def review_decision(
    state: SupportState,
) -> dict:
    latest_ai_message = get_latest_ai_message(state)

    if latest_ai_message is None:
        return {
            "requires_human_review": False,
            "review_reason": None,
            "draft_response": None,
            "human_decision": None,
        }

    user_text = get_latest_human_text(state)
    draft_response = str(latest_ai_message.text)

    review_reason = determine_review_reason(
        user_text=user_text,
        draft_response=draft_response,
    )

    return {
        "requires_human_review": review_reason is not None,
        "review_reason": review_reason,
        "draft_response": draft_response,
        "human_decision": None,
    }


def human_review(
    state: SupportState,
) -> dict:
    human_response = interrupt(
        {
            "review_reason": state["review_reason"],
            "draft_response": state["draft_response"],
            "allowed_actions": [
                "approve",
                "edit",
                "reject",
            ],
        }
    )

    action = str(
        human_response.get("action", "")
    ).strip().lower()

    if action == "approve":
        return {
            "human_decision": "approve",
        }

    if action == "edit":
        edited_response = str(
            human_response.get("edited_response", "")
        ).strip()

        if not edited_response:
            edited_response = EMPTY_EDIT_RESPONSE

        return {
            "messages": [
                AIMessage(content=edited_response),
            ],
            "human_decision": "edit",
            "draft_response": edited_response,
        }

    return {
        "messages": [
            AIMessage(content=REJECTED_RESPONSE),
        ],
        "human_decision": "reject",
    }


def route_after_agent(
    state: SupportState,
) -> str:
    latest_message = state["messages"][-1]

    if (
        isinstance(latest_message, AIMessage)
        and latest_message.tool_calls
    ):
        return "tools"

    return "review"


def route_after_review(
    state: SupportState,
) -> str:
    if state.get("requires_human_review", False):
        return "human_review"

    return "end"


def build_graph(
    checkpointer: SqliteSaver,
):
    workflow = StateGraph(SupportState)

    workflow.add_node(
        "support_agent",
        support_agent,
    )

    workflow.add_node(
        "retrieval_tools",
        ToolNode(RETRIEVAL_TOOLS),
    )

    workflow.add_node(
        "review_decision",
        review_decision,
    )

    workflow.add_node(
        "human_review",
        human_review,
    )

    workflow.add_edge(
        START,
        "support_agent",
    )

    workflow.add_conditional_edges(
        "support_agent",
        route_after_agent,
        {
            "tools": "retrieval_tools",
            "review": "review_decision",
        },
    )

    workflow.add_edge(
        "retrieval_tools",
        "support_agent",
    )

    workflow.add_conditional_edges(
        "review_decision",
        route_after_review,
        {
            "human_review": "human_review",
            "end": END,
        },
    )

    workflow.add_edge(
        "human_review",
        END,
    )

    return workflow.compile(
        checkpointer=checkpointer,
    )


checkpoint_connection = sqlite3.connect(
    str(CHECKPOINT_DATABASE_PATH),
    check_same_thread=False,
)

checkpointer = SqliteSaver(
    checkpoint_connection,
)

checkpointer.setup()

support_graph = build_graph(
    checkpointer=checkpointer,
)
