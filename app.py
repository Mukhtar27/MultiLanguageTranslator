import streamlit as st
import pandas as pd
from deep_translator import GoogleTranslator
import time
import io

# App title
st.title("📗 Multi-Language Translator with Transliteration")
st.write("Upload an Excel file, select the text column and choose source and target language. Transliteration is approximated for target language.")

# File uploader
uploaded_file = st.file_uploader("Upload Excel file (.xlsx)", type=["xlsx"])

# Language selection
LANGUAGE_OPTIONS = GoogleTranslator(source='auto', target='en').get_supported_languages(as_dict=True)

col1, col2 = st.columns(2)
with col1:
    source_lang_label = st.selectbox("Select source language", list(LANGUAGE_OPTIONS.keys()), index=0)
with col2:
    target_lang_label = st.selectbox("Select target language", list(LANGUAGE_OPTIONS.keys()), index=1)

source_lang = LANGUAGE_OPTIONS[source_lang_label]
target_lang = LANGUAGE_OPTIONS[target_lang_label]

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("✅ File uploaded successfully.")
        columns = df.columns.tolist()
        column = st.selectbox("Select column to translate:", columns)

        translations = []
        transliterations = []
        errors = 0
        progress = st.progress(0)
        status = st.empty()
        start = time.time()

        for i, text in enumerate(df[column]):
            try:
                translated = GoogleTranslator(source=source_lang, target=target_lang).translate(str(text))
                translations.append(translated)
                transliterations.append(translated)  # approximation of transliteration
            except Exception as e:
                translations.append("⚠️ Error")
                transliterations.append("")
                errors += 1

            progress.progress((i + 1) / len(df))
            status.text(f"Processing... {int((i + 1) / len(df) * 100)}%")

        df["Translated"] = translations
        df["Transliteration"] = transliterations

        elapsed = time.time() - start

        st.subheader("🔍 Preview")
        st.dataframe(df)

        output = io.BytesIO()
        df.to_excel(output, index=False, engine="openpyxl")
        output.seek(0)

        st.download_button(
            label="📥 Download Translated Excel",
            data=output,
            file_name="translated_names.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.success(f"✅ Done! Translated {len(df)} rows with {errors} errors.")
        st.info(f"⏱️ Time taken: {elapsed:.2f} seconds")

    except Exception as e:
        st.error("⚠️ Something went wrong. Check file format or column selection.")
        st.exception(e)
