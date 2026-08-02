"""
Tests for the LangGraph agent's routing behavior.

Per Phase 1 Section 7, the critical property to verify is that the tool is
called precisely when needed and not otherwise. These tests exercise the
compiled graph end-to-end but replace the chat model with a scripted fake
(`_ScriptedChatModel`) so no real Gemini calls happen and routing decisions
are fully deterministic and assertable.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolCall

from app.graph.builder import build_agent_graph
from app.memory.session_store import build_thread_config


class _ScriptedChatModel:
    """A fake chat model that returns pre-scripted responses in sequence.

    Mimics the subset of `BaseChatModel` the graph nodes rely on: `invoke`
    and `bind_tools` (returns self, since binding doesn't change which
    scripted response comes next).
    """

    def __init__(self, responses: list[AIMessage]) -> None:
        self._responses = list(responses)
        self.call_count = 0

    def bind_tools(self, _tools):  # noqa: ANN001
        return self

    def invoke(self, _messages):  # noqa: ANN001
        response = self._responses[self.call_count]
        self.call_count += 1
        return response


class _RecordingScriptedChatModel(_ScriptedChatModel):
    """Same as `_ScriptedChatModel`, but records the exact message list it
    was invoked with on each call, so tests can assert on what was actually
    sent to the model -- this is what makes the regression test below
    possible."""

    def __init__(self, responses: list[AIMessage]) -> None:
        super().__init__(responses)
        self.received_messages: list[list] = []

    def invoke(self, messages):  # noqa: ANN001
        self.received_messages.append(list(messages))
        return super().invoke(messages)


@pytest.fixture
def patched_vector_store(sample_retrieved_chunks):
    with patch(
        "app.graph.nodes.retrieve.get_vector_store_client"
    ) as mock_getter:
        mock_client = mock_getter.return_value
        mock_client.similarity_search.return_value = sample_retrieved_chunks
        yield mock_client


class TestGraphRoutingWhenDocumentSufficient:
    def test_does_not_call_tool_when_context_answers_question(
        self, patched_vector_store
    ) -> None:
        # Realistic router content: the router's own prompt instructs it to
        # answer "NO_TOOL_NEEDED" only, but this test intentionally exercises
        # a router response WITH real content to prove the fix holds even if
        # the model doesn't perfectly follow that instruction -- this is the
        # exact shape of message that caused the original bug.
        router_response = AIMessage(
            content="The Aurora M1 has a 10 hour battery life.", tool_calls=[]
        )
        final_response = AIMessage(content="The Aurora M1 has a 10 hour battery life.")
        scripted_model = _ScriptedChatModel([router_response, final_response])

        with patch("app.graph.nodes.decide_tool.get_chat_model", return_value=scripted_model), \
             patch("app.graph.nodes.generate.get_chat_model", return_value=scripted_model):
            graph = build_agent_graph()
            result = graph.invoke(
                {
                    "messages": [HumanMessage(content="What is the battery life?")],
                    "session_id": "s1",
                },
                config=build_thread_config("s1"),
            )

        assert result["tool_result"] is None
        final_message = result["messages"][-1]
        assert "battery" in final_message.content.lower()


class TestGraphRoutingWhenToolNeeded:
    def test_calls_tool_when_question_is_out_of_document_scope(
        self, patched_vector_store
    ) -> None:
        tool_call_response = AIMessage(
            content="",
            tool_calls=[
                ToolCall(
                    name="web_search",
                    args={"query": "current stock price of Aurora Robotics"},
                    id="call_1",
                )
            ],
        )
        final_response = AIMessage(content="Based on the latest web results, ...")
        scripted_model = _ScriptedChatModel([tool_call_response, final_response])

        with patch("app.graph.nodes.decide_tool.get_chat_model", return_value=scripted_model), \
             patch("app.graph.nodes.generate.get_chat_model", return_value=scripted_model), \
             patch("app.tools.web_search_tool.web_search.invoke", return_value="Stock is at $42."):
            graph = build_agent_graph()
            result = graph.invoke(
                {
                    "messages": [
                        HumanMessage(
                            content="What is Aurora Robotics' current stock price?"
                        )
                    ],
                    "session_id": "s2",
                },
                config=build_thread_config("s2"),
            )

        assert result["tool_result"] is not None


class TestGraphMemory:
    def test_second_turn_retains_first_turn_history(self, patched_vector_store) -> None:
        router_response_1 = AIMessage(content="Battery life is 10 hours.", tool_calls=[])
        final_response_1 = AIMessage(content="10 hours.")
        router_response_2 = AIMessage(content="Yes, 10 hours.", tool_calls=[])
        final_response_2 = AIMessage(content="Yes, as I mentioned, 10 hours.")
        scripted_model = _ScriptedChatModel(
            [router_response_1, final_response_1, router_response_2, final_response_2]
        )

        with patch("app.graph.nodes.decide_tool.get_chat_model", return_value=scripted_model), \
             patch("app.graph.nodes.generate.get_chat_model", return_value=scripted_model):
            graph = build_agent_graph()
            config = build_thread_config("s3")

            graph.invoke(
                {"messages": [HumanMessage(content="Battery life?")], "session_id": "s3"},
                config=config,
            )
            second_result = graph.invoke(
                {
                    "messages": [HumanMessage(content="Are you sure?")],
                    "session_id": "s3",
                },
                config=config,
            )

        history_roles = [type(m).__name__ for m in second_result["messages"]]
        assert history_roles.count("HumanMessage") == 2


class TestGenerateNodeExcludesRouterAnswer:
    """Regression test for the empty-AIMessage bug.

    Root cause: `generate_node` was forwarding `state["messages"]` verbatim
    into the final Gemini call. When the router decided no tool was needed,
    it had already appended its own content-bearing AIMessage to
    `state["messages"]` -- so the final prompt ended in an assistant turn
    instead of the user's question. Gemini correctly treats "asked to
    continue after its own completed turn" as nothing left to say, returning
    finish_reason=STOP with output_tokens=0 and empty content -- with no
    exception anywhere in the pipeline.

    This test proves the fix: it asserts the exact message list sent to the
    final `model.invoke()` call never ends in a content-bearing AIMessage,
    using a router response with REAL content (not the empty-string stand-in
    the original fixtures used, which never would have caught this).
    """

    def test_final_prompt_does_not_end_with_router_answer(
        self, patched_vector_store
    ) -> None:
        router_response = AIMessage(
            content="The Aurora M1 has a 10 hour battery life.", tool_calls=[]
        )
        final_response = AIMessage(content="Confirmed: 10 hours.")
        scripted_model = _RecordingScriptedChatModel([router_response, final_response])

        with patch("app.graph.nodes.decide_tool.get_chat_model", return_value=scripted_model), \
             patch("app.graph.nodes.generate.get_chat_model", return_value=scripted_model):
            graph = build_agent_graph()
            result = graph.invoke(
                {
                    "messages": [HumanMessage(content="What is the battery life?")],
                    "session_id": "s4",
                },
                config=build_thread_config("s4"),
            )

        assert scripted_model.call_count == 2, "expected exactly one router call and one generation call"

        generation_call_messages = scripted_model.received_messages[1]
        last_sent_message = generation_call_messages[-1]
        is_dangling_ai_message = (
            isinstance(last_sent_message, AIMessage) and not last_sent_message.tool_calls
        )
        assert not is_dangling_ai_message, (
            "generate_node must never send Gemini a prompt ending in a "
            "content-bearing AIMessage -- this is exactly what causes "
            "finish_reason=STOP with output_tokens=0 and empty content."
        )

        final_message = result["messages"][-1]
        assert final_message.content == "Confirmed: 10 hours."

    def test_final_prompt_ends_with_tool_message_when_tool_was_called(
        self, patched_vector_store
    ) -> None:
        """Companion assertion: when the tool WAS called, the final prompt
        should end on the ToolMessage, and this must remain unaffected by
        the fix (tool-call behavior must not regress)."""
        tool_call_response = AIMessage(
            content="",
            tool_calls=[
                ToolCall(name="web_search", args={"query": "latest news"}, id="call_1")
            ],
        )
        final_response = AIMessage(content="Here's what I found.")
        scripted_model = _RecordingScriptedChatModel([tool_call_response, final_response])

        with patch("app.graph.nodes.decide_tool.get_chat_model", return_value=scripted_model), \
             patch("app.graph.nodes.generate.get_chat_model", return_value=scripted_model), \
             patch("app.tools.web_search_tool.web_search.invoke", return_value="Some result."):
            graph = build_agent_graph()
            graph.invoke(
                {
                    "messages": [HumanMessage(content="What's the latest news?")],
                    "session_id": "s5",
                },
                config=build_thread_config("s5"),
            )

        generation_call_messages = scripted_model.received_messages[1]
        from langchain_core.messages import ToolMessage

        assert isinstance(generation_call_messages[-1], ToolMessage)