import random
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Information",
    page_icon="💊",
    layout="wide"
)

random_quotes = [
    "“Time and health are two precious assets that we don't recognize and appreciate until they have been depleted.” - Denis Waitley",
    "“A fit body, a calm mind, a house full of love. These things cannot be bought - they must be earned.” - Naval Ravikant",
    "“A good laugh and a long sleep are the best cures in the doctor's book.” - Irish proverb",
    "“Let food be thy medicine and medicine be thy food.” - Hippocrates",
    "“A sad soul can be just as lethal as a germ.” - John Steinbeck",
    "“Good health is not something we can buy. However, it can be an extremely valuable savings account.” - Anne Wilson Schaef",
    "“Health is not valued until sickness comes.” - Thomas Fuller",
    "“Your body hears everything your mind says.” - Naomi Judd",
    "“The way you think, the way you behave, the way you eat, can influence your life by 30 to 50 years.” - Deepak Chopra",
    "“If you're happy, if you're feeling good, then nothing else matters.” - Robin Wright",
    "“The first wealth is health.” - Ralph Waldo Emerson"
]

st.sidebar.success(random.choice(random_quotes))


diseases_df = pd.read_csv("https://raw.githubusercontent.com/smgestupa/ccs311-cs41s1-streamlit-symptoscan/main/datasets/diseases.csv")
symptoms_df = pd.read_csv("https://raw.githubusercontent.com/smgestupa/ccs311-cs41s1-streamlit-symptoscan/main/datasets/symptoms.csv")


"# 💊 Information"

"SymptoScan comes with its own set of constraints as it relies on the programmer's dataset rather than utilizing ChatGPT to apply in order to practice NLP methods covered in prior lessons. It's important to note that while SymptoScan can offer valuable insights, it is not a substitute for professional medical advice, diagnosis, or treatment."

"SymptoScan remains a practical resource for users seeking preliminary insights into their health conditions."

st.divider()

col1, col2 = st.columns(2)

with col1:
    "## Diseases Dataset"

    "By articulating the symptoms you're currently facing, the chatbot employs its programmed algorithms to analyze the information and provide potential explanations or suggestions."

    st.dataframe(data=diseases_df)

with col2:
    "## Symptoms Dataset"

    "By informing the chatbot about various symptoms you may be experiencing, it can help identify potential illnesses."

    st.dataframe(data=symptoms_df)