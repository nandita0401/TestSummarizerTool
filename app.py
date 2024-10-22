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

import io

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to clean special characters not supported by FPDF's Latin-1 encoding
def clean_text_for_pdf(text):
    replacements = {
        '‘': "'", '’': "'",  # Smart single quotes
        '“': '"', '”': '"',  # Smart double quotes
        '–': '-', '—': '-',  # En dash, Em dash
        '…': '...',          # Ellipsis
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

# Function to save summary as PDF
def create_pdf_for_download(summary_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Clean the text to replace special characters
    cleaned_text = clean_text_for_pdf(summary_text)

    # Encode the text to avoid encoding errors
    try:
        summary_text_encoded = summary_text.encode('latin-1', 'replace').decode('latin-1')
    except UnicodeEncodeError as e:
        st.error(f"Encoding error: {e}")
        return None

    # Write the text to the PDF
    pdf.multi_cell(0, 10, summary_text_encoded)

    # Save the PDF content to a string (binary) and return it in a BytesIO object
    pdf_buffer = io.BytesIO()
    pdf_output = pdf.output(dest='S').encode('latin1')  # Get the PDF output as a string
    pdf_buffer.write(pdf_output)  # Write it to the buffer
    pdf_buffer.seek(0)  # Reset the buffer's position to the start
    
    return pdf_buffer

# Load the summarization model
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# Start the Streamlit app
st.title("Text Summarization Tool")

# Initialize session state for summary if it doesn't exist
if 'summary_text' not in st.session_state:
    st.session_state['summary_text'] = ""  # Initialize to an empty string

# Input text area for users to enter text
input_text = st.text_area("Enter your text here:", height=300)

# PDF to upload
uploaded_file = st.file_uploader("Upload a PDF document", type="pdf")
if uploaded_file is not None:
    pdf_text = extract_text_from_pdf(uploaded_file)
    st.text_area("Extracted Text from PDF:", value=pdf_text, height=300)

if st.button("Summarize"):
    if input_text:
        # Check if the input is appropriate for summarization
        if len(input_text.split()) < 50:
            st.warning("The text is too short for summarization. Please provide a longer input.")
        elif len(input_text.split()) > 1024:
            input_text = ' '.join(input_text.split()[:1024])  # Truncate if too long
            st.warning("The input text was too long and has been truncated for summarization.")

        # Perform summarization and store it in session state
        summary = summarizer(input_text, max_length=130, min_length=30, do_sample=False)
        st.session_state['summary_text'] = summary[0]['summary_text']  # Store the summary in session state
        st.subheader("Summary:")
        st.write(st.session_state['summary_text'])

    elif uploaded_file is not None:
        if len(pdf_text.split()) < 50:
            st.warning("The PDF text is too short for summarization.")
        elif len(pdf_text.split()) > 1024:
            pdf_text = ' '.join(pdf_text.split()[:1024])  # Truncate if too long
            st.warning("The PDF text was too long and has been truncated for summarization.")

        # Perform summarization and store it in session state
        summary = summarizer(pdf_text, max_length=130, min_length=30, do_sample=False)
        st.session_state['summary_text'] = summary[0]['summary_text']  # Store the summary in session state
        st.subheader("Summary from PDF:")
        st.write(st.session_state['summary_text'])
    else:
        st.warning("Please enter some text or upload a PDF to summarize.")

# Button to download the summary as PDF
if st.button("Generate Summary as PDF"):
    if st.session_state['summary_text']:  # Access the summary from session state
        pdf_buffer = create_pdf_for_download(st.session_state['summary_text'])
        if pdf_buffer:
            st.download_button(
                label="Click to download",
                data=pdf_buffer,
                file_name="Summary.pdf",
                mime="application/pdf"
            )
    else:
        st.warning("No summary available to download.")