from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        if self.store.get_collection_size() == 0:
            return "Knowledge base is empty. No relevant documents found."

        chunks = self.store.search(question, top_k=top_k)
        if not chunks:
            return "No relevant context found in knowledge base."

        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk.get("metadata", {}).get("source") or chunk.get("id") or f"doc_{i}"
            context_parts.append(f"[{i}] Source: {source}\n{chunk['content']}")

        context = "\n\n".join(context_parts)
        prompt = (
            "You are a helpful knowledge assistant. Answer the question based ONLY on the provided context.\n"
            "If the answer cannot be found in the context, state clearly that the information is not available.\n"
            "Always cite the source number(s) like [1], [2] when referencing facts.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n"
            "Answer:"
        )
        return self.llm_fn(prompt)
