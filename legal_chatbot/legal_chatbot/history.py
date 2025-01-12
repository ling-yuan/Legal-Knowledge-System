from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory


class ChatHistory:
    def __init__(self, max_history: int = 50):
        self.store = {}  # 存储历史对话
        self.max_history = max_history

    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """获取会话历史"""
        if session_id not in self.store:
            self.store[session_id] = ChatMessageHistory()
        return self.store[session_id]

    def add_message(self, session_id: str, message: dict):
        """添加新消息"""
        history = self.get_session_history(session_id)
        if len(history.messages) >= self.max_history:
            # 移除最早的消息
            history.messages.pop(0)
        # 添加新消息
        if message.get("human"):
            history.add_user_message(message["human"])
        if message.get("ai"):
            history.add_ai_message(message["ai"])

    def get_messages(self, session_id: str) -> list:
        """获取会话消息列表"""
        history = self.get_session_history(session_id)
        return history.messages

    def clear_history(self, session_id: str):
        """清空会话历史"""
        if session_id in self.store:
            self.store[session_id] = ChatMessageHistory()

    def remove_session(self, session_id: str):
        """移除会话"""
        self.store.pop(session_id, None)
