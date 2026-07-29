import streamlit as st
from groq import Groq

client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)

st.title("My Grok AI")

if "messages" not in st.session_state:
    st.session_state.messages=[]

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

prompt=st.chat_input("Nhập câu hỏi")

if prompt:
    st.session_state.messages.append({
        "role":"user",
        "content":prompt
    })

    with st.chat_message("user"):
        st.write(prompt)

    completion=client.chat.completions.create(
        model="llama-4-scout-17b-16e",
        messages=st.session_state.messages
    )

    answer=completion.choices[0].message.content

    st.session_state.messages.append({
        "role":"assistant",
        "content":answer
    })

    with st.chat_message("assistant"):
        st.write(answer)
