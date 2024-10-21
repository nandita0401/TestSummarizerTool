# Test Summarizer Tool

# Helps summarize a long story or article into a smaller one without reading it.
# Input - Long texts or PDF
# Give a short summary
# Download the output as a PDF

# Input Area: Where you can paste text or upload a PDF.
# Summarize Button: When you click it, the tool will summarize the text for you.
# Output Area: Where you see the summarized text.
# Download Button: Lets you save the summary as a PDF.

import streamlit as st
# Streamlit is a free, open-source Python library that allows users to 
# create and share interactive web apps for data science and machine learning

from transformers import pipeline
# In the above line you're saying - "Hey robot, I want to use your superpowers to 
# do something cool with words, and I’ll tell you exactly what task I need help with!"

import PyPDF2
# Read and extract information from PDF

from fpdf import FPDF
# write or create new PDF

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to save summary as PDF
def save_summary_as_pdf(summary_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, summary_text)
    pdf.output("Summary.pdf")

# Load the summarization model
summarizer = pipeline("summarization")

# Start the Streamlit app
st.title("Text Summarization Tool")

# Input text area for users to enter text
input_text = st.text_area("Enter your text here:", height=300)

# PDF to upload
uploaded_file = st.file_uploader("Upload a PDF document", type="pdf")
if uploaded_file is not None:
    pdf_text = extract_text_from_pdf(uploaded_file)
    st.text_area("Extracted Text from PDF:", value=pdf_text, height=300)

# Button to summarize the text
if st.button("Summarize"):
    if input_text:
        summary = summarizer(input_text, max_length=130, min_length=30, do_sample=False)
        st.subheader("Summary:")
        st.write(summary[0]['summary_text'])
    elif uploaded_file is not None:
        summary = summarizer(pdf_text, max_length=130, min_length=30, do_sample=False)
        st.subheader("Summary from PDF:")
        st.write(summary[0]['summary_text'])
    else:
        st.warning("Please enter some text or upload a PDF to summarize.")

# Button to download the summary as PDF
if st.button("Download Summary as PDF"):
    if 'summary' in locals():
        save_summary_as_pdf(summary[0]['summary_text'])
        st.success("Summary downloaded as PDF!")
    else:
        st.warning("No summary available to download.")
