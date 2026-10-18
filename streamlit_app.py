from typing import Any
from uuid import uuid4

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.types import Command

from src.config import (
    AGENT_NODE_NAME,
    APP_NAME,
    CHECKPOINT_LIST_LIMIT,
    PAGE_ICON,
    PAGE_LAYOUT,
    PAGE_TITLE,
    THREAD_ID_LENGTH,
    THREAD_ID_PREFIX,
)


st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=PAGE_LAYOUT,
)


@st.cache_resource(show_spinner=False)
def load_backend():
    from src.graph.workflow import (
        checkpointer,
        support_graph,
    )

    return support_graph, checkpointer


def generate_thread_id() -> str:
    suffix = uuid4().hex[:THREAD_ID_LENGTH]
    return f"{THREAD_ID_PREFIX}-{suffix}"


def create_config(
    thread_id: str,
) -> dict:
    return {
        "configurable": {
            "thread_id": thread_id,
        }
    }


def extract_interrupt(
    result: dict,
) -> dict | None:
    interrupts = result.get("__interrupt__", ())

    if not interrupts:
        return None

    return interrupts[0].value


def get_persisted_interrupt(
    graph,
    config: dict,
) -> dict | None:
    snapshot = graph.get_state(config)

    if not snapshot.interrupts:
        return None

    return snapshot.interrupts[0].value


def get_saved_messages(
    graph,
    config: dict,
) -> list:
    snapshot = graph.get_state(config)

    if not snapshot.values:
        return []

    return snapshot.values.get("messages", [])


def load_conversation_ids(
    checkpointer,
) -> list[str]:
    conversation_ids = []
    seen_ids = set()

    for checkpoint in checkpointer.list(
        None,
        limit=CHECKPOINT_LIST_LIMIT,
    ):
        thread_id = (
            checkpoint.config
            .get("configurable", {})
            .get("thread_id")
        )

        if thread_id and thread_id not in seen_ids:
            seen_ids.add(thread_id)
            conversation_ids.append(thread_id)

    return conversation_ids


def initialize_session_state() -> None:
    if "active_thread" not in st.session_state:
        st.session_state.active_thread = (
            generate_thread_id()
        )

    if "conversation_ids" not in st.session_state:
        st.session_state.conversation_ids = []

    if "pending_interrupt" not in st.session_state:
        st.session_state.pending_interrupt = None

    if "interrupt_thread" not in st.session_state:
        st.session_state.interrupt_thread = None


def select_thread(
    thread_id: str,
) -> None:
    st.session_state.active_thread = thread_id
    st.session_state.pending_interrupt = None
    st.session_state.interrupt_thread = None


def add_conversation_id(
    thread_id: str,
) -> None:
    conversation_ids = (
        st.session_state.conversation_ids
    )

    if thread_id in conversation_ids:
        conversation_ids.remove(thread_id)

    conversation_ids.insert(0, thread_id)


def create_new_chat() -> None:
    thread_id = generate_thread_id()

    add_conversation_id(thread_id)
    select_thread(thread_id)


def display_sidebar(
    checkpointer,
) -> None:
    with st.sidebar:
        st.header("My conversations")

        if st.button(
            "+ New chat",
            type="primary",
            use_container_width=True,
        ):
            create_new_chat()
            st.rerun()

        st.divider()

        if not st.session_state.conversation_ids:
            st.caption("No saved conversations yet.")
            return

        for thread_id in (
            st.session_state.conversation_ids
        ):
            is_active = (
                thread_id
                == st.session_state.active_thread
            )

            button_label = thread_id

            if is_active:
                button_label = f"● {thread_id}"

            if st.button(
                button_label,
                key=f"thread_{thread_id}",
                use_container_width=True,
                disabled=is_active,
            ):
                select_thread(thread_id)
                st.rerun()


def build_display_turns(
    messages: list,
    hide_last_assistant: bool = False,
) -> list[dict[str, str | None]]:
    turns = []
    current_turn = None

    for message in messages:
        if isinstance(message, HumanMessage):
            if current_turn is not None:
                turns.append(current_turn)

            current_turn = {
                "user": str(message.text),
                "assistant": None,
            }

        elif (
            isinstance(message, AIMessage)
            and current_turn is not None
            and not message.tool_calls
            and str(message.text).strip()
        ):
            current_turn["assistant"] = str(
                message.text
            )

    if current_turn is not None:
        turns.append(current_turn)

    if hide_last_assistant and turns:
        turns[-1]["assistant"] = None

    return turns


def display_conversation(
    graph,
    config: dict,
    review_pending: bool,
) -> None:
    messages = get_saved_messages(
        graph=graph,
        config=config,
    )

    turns = build_display_turns(
        messages=messages,
        hide_last_assistant=review_pending,
    )

    if not turns:
        st.info(
            "Start a conversation by asking a "
            "question below."
        )
        return

    for turn in turns:
        with st.chat_message("user"):
            st.markdown(turn["user"])

        if turn["assistant"]:
            with st.chat_message("assistant"):
                st.markdown(turn["assistant"])


def resume_graph(
    graph,
    config: dict,
    human_decision: dict[str, Any],
) -> None:
    with st.status(
        "Resuming the workflow...",
        expanded=False,
    ) as status:
        result = graph.invoke(
            Command(resume=human_decision),
            config=config,
        )

        status.update(
            label="Review completed",
            state="complete",
        )

    st.session_state.pending_interrupt = (
        extract_interrupt(result)
    )


def display_human_review(
    graph,
    config: dict,
    interrupt_data: dict,
) -> None:
    st.warning("Human review is required")

    with st.container(border=True):
        st.subheader("Human Review Panel")

        st.write("Reason:")
        st.write(interrupt_data["review_reason"])

        st.write("Draft response:")
        st.markdown(
            interrupt_data["draft_response"]
        )

        edited_response = st.text_area(
            "Edit the response if necessary",
            value=interrupt_data["draft_response"],
            height=250,
            key=(
                "review_text_"
                f"{st.session_state.active_thread}"
            ),
        )

        approve_column, edit_column, reject_column = (
            st.columns(3)
        )

        with approve_column:
            approve_clicked = st.button(
                "Approve",
                type="primary",
                use_container_width=True,
            )

        with edit_column:
            edit_clicked = st.button(
                "Submit edit",
                use_container_width=True,
            )

        with reject_column:
            reject_clicked = st.button(
                "Reject",
                use_container_width=True,
            )

        if approve_clicked:
            resume_graph(
                graph=graph,
                config=config,
                human_decision={
                    "action": "approve",
                },
            )
            st.rerun()

        if edit_clicked:
            if not edited_response.strip():
                st.error(
                    "The edited response cannot be empty."
                )
            else:
                resume_graph(
                    graph=graph,
                    config=config,
                    human_decision={
                        "action": "edit",
                        "edited_response": (
                            edited_response.strip()
                        ),
                    },
                )
                st.rerun()

        if reject_clicked:
            resume_graph(
                graph=graph,
                config=config,
                human_decision={
                    "action": "reject",
                },
            )
            st.rerun()


def run_user_query(
    graph,
    config: dict,
    user_query: str,
) -> dict:
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        complete_response = ""

        for message_chunk, metadata in graph.stream(
            {
                "messages": [
                    HumanMessage(content=user_query)
                ]
            },
            config=config,
            stream_mode="messages",
        ):
            if (
                metadata.get("langgraph_node")
                != AGENT_NODE_NAME
            ):
                continue

            chunk_text = str(message_chunk.text)

            if chunk_text:
                complete_response += chunk_text

                response_placeholder.markdown(
                    complete_response + "▌"
                )

        response_placeholder.markdown(
            complete_response
        )

    snapshot = graph.get_state(config)

    return {
        "__interrupt__": snapshot.interrupts,
    }


def main() -> None:
    initialize_session_state()

    st.title(APP_NAME)

    with st.spinner(
        "Starting the support assistant..."
    ):
        graph, checkpointer = load_backend()

    if not st.session_state.conversation_ids:
        stored_conversations = (
            load_conversation_ids(checkpointer)
        )

        st.session_state.conversation_ids = (
            stored_conversations
        )

        add_conversation_id(
            st.session_state.active_thread
        )

    display_sidebar(checkpointer)

    st.caption(
        f"Conversation: "
        f"{st.session_state.active_thread}"
    )

    config = create_config(
        st.session_state.active_thread
    )

    if (
        st.session_state.interrupt_thread
        != st.session_state.active_thread
    ):
        st.session_state.pending_interrupt = (
            get_persisted_interrupt(
                graph=graph,
                config=config,
            )
        )

        st.session_state.interrupt_thread = (
            st.session_state.active_thread
        )

    interrupt_data = (
        st.session_state.pending_interrupt
    )

    display_conversation(
        graph=graph,
        config=config,
        review_pending=interrupt_data is not None,
    )

    if interrupt_data is not None:
        display_human_review(
            graph=graph,
            config=config,
            interrupt_data=interrupt_data,
        )

        st.info(
            "Customer input is disabled until the "
            "human review is completed."
        )
        return

    user_query = st.chat_input(
        "Ask Ranjith's Tech support a question"
    )

    if user_query:
        add_conversation_id(
            st.session_state.active_thread
        )

        result = run_user_query(
            graph=graph,
            config=config,
            user_query=user_query,
        )

        st.session_state.pending_interrupt = (
            extract_interrupt(result)
        )

        st.session_state.interrupt_thread = (
            st.session_state.active_thread
        )

        st.rerun()


if __name__ == "__main__":
    main()
