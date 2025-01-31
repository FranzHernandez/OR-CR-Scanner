import hmac
import streamlit as st
from office365_api import base64decoder
from ocr import readExtractPDF
from download_reupload import get_file

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], base64decoder(st.secrets["password"])):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False

if not check_password():
    st.stop()  # Do not continue if check_password is not True.

# st.set_page_config(layout="wide")

st.title("PFO OR/CR Scanner")

st.header("Upload", divider='blue')
envelope = st.text_input("Envelope Number", "")
upload_file = st.file_uploader("Please upload PDF/s here.", type=['pdf'], accept_multiple_files=True)
is_clicked = st.button("EXTRACT", type="primary", use_container_width=True)
if is_clicked and len(upload_file) > 0:
    if envelope == "":
        st.error("Please enter envelope number.", icon="🚨")
    else:
        processed_texts = readExtractPDF(upload_file)
        try:
            get_file(file_n=base64decoder(st.secrets["file_name"]), folder=base64decoder(st.secrets["folder_name"]), processed_texts=processed_texts, envelope=envelope)
        except Exception as e:
            st.write(e)

st.header("Description", divider='red')
st.text("This app is used to automatically extract pertinent information from scanned ORs/CRs and upload the details to the PFO FSG database.")

st.header("Instructions", divider='green')
st.text("1. Please ensure that the scanned OR/CR is in PDF format.")
st.text("2. The system is only applicable to ORs/CRs of the modern format.")
st.text("3. Multiple PDFs may be uploaded; however, please refrain from having the OR and CR on the same page in the PDF.")
st.text("4. Please have the Excel database file closed when uploading the PDF files to avoid errors.")
st.text("5. Kindly verify if the uploaded details are correct and make corrections if necessary.")