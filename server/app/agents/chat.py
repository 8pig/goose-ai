from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

multi_chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一位优秀的技术专家，擅长解决各种开发中的技术问题"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
])