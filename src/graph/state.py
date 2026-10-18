from langgraph.graph import MessagesState


class SupportState(MessagesState):
    requires_human_review: bool
    review_reason: str | None
    draft_response: str | None
    human_decision: str | None
