import time
import spacy
import regex as re
import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

spacy.prefer_gpu()
nlp = spacy.load("en_core_web_sm")

st.set_page_config(
    page_title="SymptoScan",
    page_icon="🩺"
)

def write_bot_message(response):
    with st.chat_message('assistant'):
        message_placeholder = st.empty()
        full_response = ""

        for character in response:
            full_response += character
            time.sleep(0.025)

            message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)
        
        st.session_state.messages.append({'role': 'assistant', 'content': full_response})

def get_most_similar_response(df, column, query, top_k=1):
    # Remove special characters
    special_chars_pattern = r'[^a-zA-z0-9\s(\)\[\]\{\}]'
    query = re.sub(special_chars_pattern, '', query.strip())

    # Remove stop words and specific POS tags
    doc = nlp(query)

    remove_pos = ["PRON", "PROPN", "AUX", "CCONJ", "NUM"]
    filtered_query = ' '.join([token.text for token in doc if not token.is_stop or token.pos_ not in remove_pos])
      
    # Prepare data
    vectorizer = TfidfVectorizer(use_idf=True, max_df=0.5,min_df=1, ngram_range=(1,3))
    all_data = list(df[column]) + [filtered_query]

    # Vectorize with TF-IDF
    tfidf_matrix = vectorizer.fit_transform(all_data)

    # Compute Similarity
    document_vectors = tfidf_matrix[:-1]
    query_vector = tfidf_matrix[-1]
    similarity_scores = cosine_similarity(query_vector, document_vectors)

    # Pick the Top k response
    sorted_indeces = similarity_scores.argsort()[0][::-1][:top_k]

    # Get the similarity score of the chosen response
    similarity_score = similarity_scores[0][similarity_scores.argsort()[0][::-1][:top_k]][0] * 100

    # Fetch the corresponding response
    most_similar_responses = df.iloc[sorted_indeces][column].values

    responses = []
    for response in most_similar_responses:
      response_row = df.loc[df[column] == response]
      responses.append([response_row.index.item(), response_row.to_numpy()[0]])

    return responses, similarity_score


diseases_df = pd.read_csv("datasets/diseases.csv")
symptoms_df = pd.read_csv("datasets/symptoms.csv")


"""# 🩺 SymptoScan"""

def disable_chat_input():
    st.session_state.disable_chat_input = True

if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_state" not in st.session_state:
    st.session_state.current_state = "NOT_ASKING"

if "possible_diseases" not in st.session_state:
    st.session_state.possible_diseases = []

if "current_symptom" not in st.session_state:
    st.session_state.current_symptom = []

if "experiencing_symptoms" not in st.session_state:
    st.session_state.experiencing_symptoms = []

if "disable_chat_input" not in st.session_state:
    st.session_state.disable_chat_input = False

if len(st.session_state.messages) == 0:
    st.session_state.messages.append({'role': 'assistant', 'content': 'Good day! You can start or continue this chat by telling us what symptoms you are currently experiencing.\n\nIt would help us if you specify what symptoms: e.g. "I am experiencing symptoms such as runny nose, coughing, sore throat."'})

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])


current_state = st.session_state.current_state
possible_diseases = st.session_state.possible_diseases
current_symptom = st.session_state.current_symptom
experiencing_symptoms = st.session_state.experiencing_symptoms

if prompt := st.chat_input('Ask away!', disabled=st.session_state.disable_chat_input, on_submit=disable_chat_input):
    with st.chat_message('user'):
        st.markdown(prompt)

    st.session_state.messages.append({'role': 'user', 'content': prompt})

if current_state == "NOT_ASKING" and prompt is not None:
    if prompt in ['help', 'Help']:
        write_bot_message('Good day! You can start or continue this chat by telling us what symptoms you are currently experiencing.\n\nIt would help us if you specify what symptoms: e.g. "I am experiencing symptoms such as runny nose, coughing, sore throat."')
    
    else:
        responses, similarity_score = get_most_similar_response(diseases_df, 'General Symptoms', prompt, top_k=3)

        row_index, row = responses[0]

        if similarity_score <= 10:
            write_bot_message(f'We have failed to scan your symptoms, please try again and we recommend listing out what symptoms you are experiencing.\n\n(e.g. I am experiencing symptoms such as runny nose, coughing, sore throat.)')
        else:
            write_bot_message(f'Based on the symptoms you are experiencing, you may be experiencing {row[0]}. Symptoms of {row[0]} include: {row[2]}. Is the diagnosis correct?\n\n(Type Yes & enter if correct.)')
            st.session_state.current_state = "IS_ASKING"
            st.session_state.possible_diseases = responses

    st.session_state.disable_chat_input = False
    st.rerun()

elif current_state == "IS_ASKING" and prompt is not None and prompt in ["yes", "Yes"]:
    row_index, row = possible_diseases[0]

    st.session_state.current_state = "NOT_ASKING"
    st.session_state.possible_diseases = []
    st.session_state.current_symptom = []
    st.session_state.experiencing_symptoms = []

    write_bot_message(f'Glad we got it correct! You are experiencing {row[0]}. {row[3]}.\n\nThe symptoms include, which more than one of these you are currently experiencing: {row[2]}. Our recommendation: {row[4]}.')
    
    st.session_state.disable_chat_input = False
    st.rerun()

elif current_state == "IS_ASKING" and prompt is not None and prompt not in ["yes", "Yes"]:
    st.session_state.current_state = "ASKING_SYMPTOM"

    if len(st.session_state.possible_diseases) - 1 <= 0:
        st.session_state.current_state = "SCAN_FAILED"
        st.rerun()

    else:
        st.session_state.possible_diseases.pop(0)
        row_index, row = st.session_state.possible_diseases[0]
        st.session_state.current_symptom = [row_index, row[2].split(", ")]

        st.session_state.disable_chat_input = False
        st.rerun()

elif current_state == "SCAN_FAILED":
    st.session_state.current_state = "NOT_ASKING"
    st.session_state.possible_diseases = []
    st.session_state.current_symptom = []
    st.session_state.experiencing_symptoms = []
    st.session_state.disable_chat_input = False

    write_bot_message(f'We have failed to scan your symptoms, please try again and we recommend listing out what symptoms you are experiencing.\n\n(e.g. I am experiencing symptoms such as runny nose, coughing, sore throat.)')

    st.rerun()
    
elif current_state == "WAITING_SYMPTOM_CALCULATION":
    likelihood = (len(experiencing_symptoms) / len(current_symptom)) * 100
    
    if likelihood >= 60.0:
        row_index, row = st.session_state.possible_diseases[0]

        st.session_state.current_state = "NOT_ASKING"
        st.session_state.possible_diseases = []
        st.session_state.current_symptom = []
        st.session_state.experiencing_symptoms = []

        write_bot_message(f'You might be experiencing {row[0]}. {row[3]}.\n\nThe symptoms include, which more than one of these you are currently experiencing: {row[2]}. Our recommendation: {row[4]}.\n\n(If you are not confident in our answer, please try again and we recommend listing out what you are experiencing.)')
    
    else:
        st.session_state.current_state = "ASKING_SYMPTOM"
        st.session_state.experiencing_symptoms = []

        row_index, row = st.session_state.possible_diseases[0]
        st.session_state.current_symptom = [row_index, row[2].split(", ")]

    st.session_state.disable_chat_input = False
    st.rerun()

elif current_state == "ASKING_SYMPTOM" and len(possible_diseases) > 0:

    if len(current_symptom[1]) == 0 and len(st.session_state.possible_diseases) - 1 == 0:
        st.session_state.current_state = "SCAN_FAILED"
        st.rerun()

    elif len(current_symptom[1]) == 0:
        row_index, row = st.session_state.possible_diseases.pop(0)
        st.session_state.current_symptom = [row_index, row[2].split(", ")]

        st.session_state.current_state = "WAITING_SYMPTOM_CALCULATION"
        st.rerun()

    row_index, symptoms = current_symptom
    response, _ = get_most_similar_response(symptoms_df, 'Symptom', symptoms[0])

    write_bot_message(f'Are you experiencing: {symptoms[0].capitalize()}? {response[0][1][1]}.')

    st.session_state.current_state = "WAITING_SYMPTOM_ANSWER"

elif current_state == "WAITING_SYMPTOM_ANSWER":
    st.session_state.current_state = "ASKING_SYMPTOM"

    if prompt in ["yes", "Yes"]:
        experiencing_symptoms.append(st.session_state.current_symptom[1].pop(0))
    else:
        st.session_state.current_symptom[1].pop(0)

    st.session_state.disable_chat_input = False
    st.rerun()