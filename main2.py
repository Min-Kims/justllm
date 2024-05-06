import streamlit as st
#구동한 것이 Streamlit 상 로그로 남도록
from loguru import logger
#메모리를 가지고 있는 Conver~~~Chain 가져오기
from langchain.chains import ConversationalRetrievalChain
#LLM : OpenAI
from langchain.chat_models import ChatOpenAI
#몇개까지의 대화를 메모리로 넣어줄지 정하는 부분
from langchain.memory import ConversationBufferMemory
#메모리 구축을 위한 추가적 라이브러리
from langchain.callbacks import get_openai_callback
from langchain.memory import StreamlitChatMessageHistory
from dotenv import load_dotenv

def main():
    st.set_page_config(page_title="김민 챗봇 데모", page_icon="🦜")
    st.title("🦜 김민 챗봇 데모")

        if "conversation" not in st.session_state:
            st.session_state.conversation = None

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = None

        if "processComplete" not in st.session_state:
            st.session_state.processComplete = None

        with st.sidebar:
            process = st.button("Process")

        if process:
            #Streamlit Secret키 가져오기
            openai_api_key = st.secrets["openai"]["api_key"]
            if not openai_api_key:
                st.info("API 키가 설정되지 않았습니다. secret.toml파일을 확인해주세요.")
                st.stop()

        st.session_state.conversation = get_conversation_chain(openai_api_key) 

        st.session_state.processComplete = True
    
    #채팅창의 메세지들이 계속 유지되기 위한 코드
        if 'messages' not in st.session_state:
            st.session_state['messages'] = [{"role": "assistant", 
                                            "content": "안녕하세요! 주어진 문서에 대해 궁금하신 것이 있으면 언제든 물어봐주세요!"}]

    #메세지들마다 Role에 따라 마크다운 할것이다. (한 번 메세지가 입력될 때마다 묶는 것)
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])


    #히스토리를 구현해줘야 우리의 질문을 기억해서 댇답해줌
        history = StreamlitChatMessageHistory(key="chat_messages")

    #질문 창 만들기
        # Chat logic
        if query := st.chat_input("질문을 입력해주세요."):
            st.session_state.messages.append({"role": "user", "content": query})

            with st.chat_message("user"):
                st.markdown(query)

            with st.chat_message("assistant"):

                chain = st.session_state.conversation

    #로딩할 때 빙글빙글 돌아가는 영역 구현
                with st.spinner("Thinking..."):
                    try:
                        result = chain({"question": query})
                        with get_openai_callback() as cb:
                            st.session_state.chat_history = result.get('chat_history', [])
                        response = result.get('answer', "답변을 찾을 수 없습니다.")
                        source_documents = result.get('source_documents', [])

                        st.markdown(response)
                        if source_documents:
                            with st.expander("참고 문서 확인"):
                                for doc in source_documents:
                                    st.markdown(doc.metadata.get('source', '출처 정보 없음'), help=doc.page_content)
                    except Exception as e:
                        st.error(f"처리 중 오류가 발생했습니다: {e}")

    # Add assistant message to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})                    


#위에서 선언한 모든것들을 담아보는 것
def get_conversation_chain(openai_api_key):
    llm = ChatOpenAI(openai_api_key=openai_api_key, model_name = 'gpt-3.5-turbo',temperature=0)
    conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=llm, 
            chain_type="stuff", 
            memory=ConversationBufferMemory(memory_key='chat_history', return_messages=True, output_key='answer'),
            get_chat_history=lambda h: h,
            return_source_documents=True,
        )

    return conversation_chain

if __name__ == '__main__':
    main()  







# class StreamHandler(BaseCallbackHandler):
#     def __init__(self, container, initial_text=""):
#         self.container = container
#         self.text = initial_text

#     def on_llm_new_token(self, token: str, **kwargs) -> None:
#         self.text += token
#         self.container.markdown(self.text)

