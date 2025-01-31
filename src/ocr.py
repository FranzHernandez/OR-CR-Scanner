import numpy as np
from pdf2image import convert_from_bytes
from paddleocr import PaddleOCR
import streamlit as st

ocr = PaddleOCR(use_angle_cls=True, lang='en')

#@st.cache_data
def readExtractPDF(pdf_list:list):
    with st.spinner('Extracting info from PDF...'):
        #Raw text container
        cr_text = []

        try: 
            for pdf in pdf_list:
                #Needs to be converted to 'convert_from_bytes' in Streamlit
                images = convert_from_bytes(pdf.read(), poppler_path=r'poppler-24.08.0\Library\bin', fmt='tiff')
            
                for image in images:
                    result = ocr.ocr(np.array(image), cls=True, det=True, rec=True)
                    raw_text = [text[1][0] for text in result[0]]

                    if any("CERTIFICATE" in t.upper() and "REGISTRATION" in t.upper() for t in raw_text):
                        cr_text.append(raw_text)

            if len(cr_text) > 0:
                fields = {
                    'cr_name': [], 'cr_no': [], 'or_no': [], 'engine': [],
                    'chassis': [], 'brand': [], 'series': [], 'date': []
                }

                for extract in cr_text:
                    fields['cr_no'].append(extract[-1][-10:]) 
                    extracted_data = {key: "" for key in fields if key != 'cr_no'}
                    
                    for i, text in enumerate(extract):
                        if "OWNER" in text and "NAME" in text:
                            cr_name = extract[i + 1].split("SUBJECT")[0].replace(",", "").strip() if "SUBJECT" in extract[i + 1].upper() else extract[i + 1]
                            extracted_data['cr_name'] = cr_name
                        elif "VIN" in text:
                            vin_options = extract[i + 1:i + 4]
                            for vin in vin_options:
                                if len(vin) == 17 and " " not in vin:
                                    extracted_data['chassis'] = vin
                                elif len(vin) not in {17, 7} and len(vin.split()[0]) != 3:
                                    extracted_data['engine'] = vin
                        elif "AMOUNT" in text:
                            j = 1
                            while len(extract[i + j]) not in range(15, 18):
                                j += 1
                            extracted_data['or_no'] = extract[i + j]
                        elif "MAKE" in text and "BRAND" in text:
                            brand_options = extract[i + 1:i + 5]
                            extracted_data['brand'] = next((b for b in brand_options if 3 <= len(b) < 15 and b not in ['SUV', 'AUV', 'ATV']), "")
                        elif "NET" in text and "WEIGHT" in text:
                            series_options = extract[i + 1:i + 5]
                            extracted_data['series'] = next((s for s in series_options if len(s) > 5), "")
                        elif "DATE" in text.upper() and "O" not in text.upper():
                            if "/" in text:
                                extracted_data['date'] = text.split()[1].strip()
                            else:
                                date_options = extract[i + 1:i + 5]
                                extracted_data['date'] = next((d for d in date_options if "/" in d and "M" not in d), "")
                    
                    for key in extracted_data:
                        fields[key].append(extracted_data[key])

                return fields
        except Exception as e:
            st.write(e)

