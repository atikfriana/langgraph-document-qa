"""
LangGraph construction and compilation.

Assembles the graph described in Phase 1 Section 3: `retrieve -> decide_tool
-> (tool_exec ->) generate`, compiled with the checkpointer so conversation
memory (Phase 1 Section 5) is automatically persisted per `thread_id`. This
is the only module that wires nodes and edges together — nodes themselves
have no knowledge of graph topology.
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.graph.edges import NODE_GENERATE, NODE_TOOL_EXEC, route_after_decide_tool
from app.graph.nodes.decide_tool import decide_tool_node
from app.graph.nodes.generate import generate_node
from app.graph.nodes.retrieve import retrieve_node
from app.graph.nodes.tool_exec import tool_exec_node
from app.graph.state import AgentState
from app.memory.checkpointer import get_checkpointer

NODE_RETRIEVE = "retrieve"
NODE_DECIDE_TOOL = "decide_tool"


def build_agent_graph() -> CompiledStateGraph:
    """Build and compile the document Q&A agent graph."""
    graph_builder = StateGraph(AgentState)

    graph_builder.add_node(NODE_RETRIEVE, retrieve_node)
    graph_builder.add_node(NODE_DECIDE_TOOL, decide_tool_node)
    graph_builder.add_node(NODE_TOOL_EXEC, tool_exec_node)
    graph_builder.add_node(NODE_GENERATE, generate_node)

    graph_builder.add_edge(START, NODE_RETRIEVE)
    graph_builder.add_edge(NODE_RETRIEVE, NODE_DECIDE_TOOL)
    graph_builder.add_conditional_edges(
        NODE_DECIDE_TOOL,
        route_after_decide_tool,
        {
            NODE_TOOL_EXEC: NODE_TOOL_EXEC,
            NODE_GENERATE: NODE_GENERATE,
        },
    )
    graph_builder.add_edge(NODE_TOOL_EXEC, NODE_GENERATE)
    graph_builder.add_edge(NODE_GENERATE, END)

    return graph_builder.compile(checkpointer=get_checkpointer())