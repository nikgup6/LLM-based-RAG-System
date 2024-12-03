import streamlit as st
import requests

st.title("LLM-Based RAG System")
st.write("Enter your query below:")

# User input
user_query = st.text_input("Your Query:")

if st.button("Submit"):
    if not user_query.strip():
        st.error("Please enter a query.")
    else:
        with st.spinner("Processing your query..."):
            # Send query to Flask backend
            response = requests.post("http://localhost:5001/query", json={"query": user_query})
            if response.status_code == 200:
                answer = response.json().get("answer")
                st.success("Answer:")
                st.write(answer)
            else:
                st.error(f"Error: {response.json().get('error')}")
