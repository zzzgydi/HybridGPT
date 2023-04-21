import uuid
import textwrap
import tiktoken

from hybrid.llm import llm_chat


class Memory:
    def __init__(self):
        self.data = []

    def add(self, data):
        self.data.append(data)

    def get_context(self, data: str, num=5):
        return self.data[-num:]

    def summarize_memory_if_large(self, memory: str, max_tokens: int) -> str:
        """
        Summarize a memory string if it exceeds the max_tokens limit.

        Args:
            memory (str): The memory string to be summarized.
            max_tokens (int): The maximum token limit.

        Returns:
            str: The summarized memory string.
        """
        num_tokens = len(tiktoken.encoding_for_model("gpt-3.5-turbo").encode(memory))

        if num_tokens > max_tokens:
            avg_chars_per_token = len(memory) / num_tokens
            chunk_size = int(avg_chars_per_token * 400)
            chunks = textwrap.wrap(memory, chunk_size)
            summary_size = int(max_tokens / len(chunks))
            memory = ""

            print(f"Summarizing memory, {len(chunks)} chunks.")

            for chunk in chunks:
                response = llm_chat(
                    messages=[
                        {
                            "role": "user",
                            "content": f"Shorten the following memory chunk of an autonomous agent from a first person perspective, {summary_size} tokens max.",
                        },
                        {
                            "role": "user",
                            "content": f"Do your best to retain all semantic information including tasks performed by the agent, website content, important data points and hyper-links:\n\n{chunk}",
                        },
                    ],
                    max_tokens=300,
                )

                memory += response + "\n\n"

        return memory


memory = Memory()
