# Import LangChain's memory module for storing conversation history
from langchain.memory import ConversationBufferMemory


# ------------------------------------------------------------
# Shared memory initialization
# ------------------------------------------------------------
# Create a single shared memory buffer instance that stores conversation history
# - memory_key: identifies how the memory is referenced across agents
# - return_messages=True: keeps full message objects instead of plain text
_shared_memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
)


# ------------------------------------------------------------
# Get shared memory instance
# ------------------------------------------------------------
# Purpose: Provides global access to the same memory object used by all agents.
# Ensures that all agents (symptom, lifestyle, etc.) share a consistent conversation state.
def get_shared_memory() -> ConversationBufferMemory:
    return _shared_memory



def reset_memory():
    _shared_memory.clear()
