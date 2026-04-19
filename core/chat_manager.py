from langchain_groq import ChatGroq
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from tools.scholar_tool import ScholarTool
from config import config


class ChatManager:

    def __init__(self):
        self.llm = ChatGroq(
            model=config.MODEL_NAME,
            temperature=config.TEMPERATURE,
            groq_api_key=config.GROQ_API_KEY,
        )
        self.history = ChatMessageHistory()
        self.scholar_tool = ScholarTool()
        self.system_prompt = ""
        self.chain = self._build_chain()

    def _build_chain(self):
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template("{system_prompt}"),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template("{input}"),
        ])
        chain = prompt | self.llm
        return RunnableWithMessageHistory(
            chain,
            lambda session_id: self.history,
            input_messages_key="input",
            history_messages_key="history",
        )

    def ask(self, user_query: str, system_prompt: str = "") -> dict:
        results = self.scholar_tool.search(user_query)
        scholar_context = self.scholar_tool.format_for_llm(results)
        enriched_input = (
            f"User Question: {user_query}\n\n"
            f"--- ACADEMIC SOURCES ---\n{scholar_context}\n"
            f"--- END OF SOURCES ---\n\n"
            f"Please answer the question using ONLY the sources above."
        )
        response = self.chain.invoke(
            {"input": enriched_input, "system_prompt": system_prompt},
            config={"configurable": {"session_id": "default"}}
        )
        if len(self.history.messages) > 10:
            self.history.messages = self.history.messages[-10:]
        return {"answer": response.content, "sources": results}

    def clear_memory(self):
        self.history.clear()

    @property
    def message_count(self):
        return len(self.history.messages)