from src.office365_api import SharePoint
from datetime import date
import pandas as pd
import io
import streamlit as st
from src.office365_api import base64decoder

today = str(date.today())
sharepoint = SharePoint()

#@st.cache_data
def modify_file(file_obj, folder, processed_texts, envelope):
    data = io.BytesIO(file_obj)
    ws_list = pd.ExcelFile(data).sheet_names
    df = pd.read_excel(data, sheet_name=ws_list[0], dtype={'NAME': str, 'CR NUMBER' : str, 'OR NUMBER': str, 'ENGINE NUMBER': str, 'CHASSIS NUMBER': str, 
                                                           'DATE': str, 'MAKE': str, 'SERIES': str, 'ENVELOPE': str, 'SCANNED': str})
   
    new_rows = pd.DataFrame({
        "NAME": processed_texts['cr_name'],
        "CR NUMBER": processed_texts['cr_no'],
        "OR NUMBER": processed_texts['or_no'],
        "ENGINE NUMBER": processed_texts['engine'],
        "CHASSIS NUMBER": processed_texts['chassis'],
        "DATE": processed_texts['date'],
        "MAKE": processed_texts['brand'],
        "SERIES": processed_texts['series'],
        "ENVELOPE": [envelope] * len(processed_texts['cr_name']),
        "SCANNED": [today] * len(processed_texts['cr_name'])
    })

    new_df = pd.concat([df, new_rows], ignore_index=True)

    #create the Excel object in-memory
    output_obj = io.BytesIO()
    writer = pd.ExcelWriter(output_obj, engine='xlsxwriter')
    new_df.to_excel(writer, index=False, sheet_name=ws_list[0])

    workbook = writer.book
    worksheet = writer.sheets[ws_list[0]]

    worksheet.set_column('A:J', 40)
    worksheet.autofilter('A1:J1')

    writer.close()
    output_obj.seek(0)

    upload_file(file_name=base64decoder(st.secrets["file_name"]), folder_name=folder, content=output_obj.read())

    st.success("Extraction and upload successful!", icon="✅")
    st.subheader("Results")
    st.dataframe(new_rows, hide_index=True)

#@st.cache_data
def upload_file(file_name, folder_name, content):
    sharepoint.upload_file(file_name, folder_name, content)

#@st.cache_data
def get_file(file_n, folder, processed_texts, envelope):
    with st.spinner('Uploading to database...'):
        file_obj = sharepoint.download_file(file_n, folder)
        modify_file(file_obj, folder, processed_texts, envelope)