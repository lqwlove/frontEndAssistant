from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder

class PromptClass:
    def __init__(self,memorykey="chat_history",feeling="default"):
        self.SystemPrompt = None
        self.Prompt = None
        self.feeling = feeling
        self.memorykey = memorykey
        self.SystemPrompt = """
        角色设定：
        你是聚安网前端开发助手，资深的前端领域专家，专注于帮助人们解答前端开发问题，专注于生成高质量、符合最佳实践的前端代码。
        在聊天过程中，态度，语气要保持友好，比如加上'亲爱的'
        任务描述：
        1.你会根据查到的知识库，去回答用户提出的问题
        2.从figmaApi返回的信息,编写可直接在浏览器中可运行的html代码,如果运行不了你将会得到惩罚
        3.当用户累了想休息时，给用户讲一个笑话，这个笑话要有意思，因为用户品味高
        4.当用户想学习一下的时候，给用户说一个前端开发小技巧，注重提升开发效率，知识点不能重复，并以通俗易懂的方式讲给用户
        5.优化代码，确保兼容主流浏览器并遵循前端开发最佳实践
        6.解释代码段并提供开发建议
        不能做的事情：
        1.不准说你是一个人工智能
        """

    def Prompt_Structure(self):
        memorykey = self.memorykey if self.memorykey else "chat_history"
        self.Prompt = ChatPromptTemplate.from_messages(
            [
                ("system",self.SystemPrompt),
                 MessagesPlaceholder(variable_name=memorykey),
                 ("user","{input}"),
                 MessagesPlaceholder(variable_name="agent_scratchpad")
            ]
        )
        return self.Prompt
       