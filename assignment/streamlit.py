import streamlit as st
import requests

# Set the FastAPI endpoint URL
FASTAPI_URL = "http://localhost:8000/query"

st.title("Query Response App")

# Create a text input for the query
user_query = st.text_input("Enter your query:")

if st.button("Submit Query"):
    if user_query:
        try:
            # Send the query to the FastAPI backend using URL parameters
            response = requests.post(f"{FASTAPI_URL}?query={requests.utils.quote(user_query)}")
            response_data = response.json()

            if response.status_code == 200:
                bot_response = response_data.get("bot_response", "")
                if bot_response:
                    # Display the markdown-formatted bot response
                    st.markdown(bot_response)
                else:
                    st.warning("No response from the bot.")
            else:
                st.error(f"Error: {response_data.get('message', 'Unknown error')}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter a query.")
