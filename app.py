import streamlit as st
import pandas as pd
import io
import time
from googletrans import Translator

# Title
st.title("🌐 Multilingual Translator with Transliteration")
st.write("Upload an Excel file with text and choose languages to translate. Optionally, get transliteration.")

# Upload file
uploaded_file = st.file_uploader("Upload Excel file (.xlsx)", type=["xlsx"])

# Language selection
language_map = {
    "English": "en",
    "Arabic": "ar",
    "Hindi": "hi",
    "French": "fr",
    "German": "de"
}

source_lang = st.selectbox("Select source language", list(language_map.keys()))
target_lang = st.selectbox("Select target language", list(language_map.keys()))

add_transliteration = st.checkbox("Include Transliteration")

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("✅ File uploaded successfully.")
    
    col_to_translate = st.selectbox("Select column to translate", df.columns.tolist())

    translator = Translator()
    translations = []
    transliterations = []

    progress = st.progress(0)
    status_text = st.empty()
    start_time = time.time()

    for i, text in enumerate(df[col_to_translate]):
        try:
            result = translator.translate(str(text), src=language_map[source_lang], dest=language_map[target_lang])
            translations.append(result.text)
            if add_transliteration:
                transliterations.append(result.pronunciation or "")
            else:
                transliterations.append("")
        except Exception as e:
            translations.append("⚠️ Error")
            transliterations.append("")

        progress.progress((i + 1) / len(df))
        status_text.text(f"Translating {i+1}/{len(df)}")

    elapsed_time = time.time() - start_time

    df["Translated"] = translations
    if add_transliteration:
        df["Transliteration"] = transliterations

    st.subheader("Preview")
    st.dataframe(df)

    output = io.BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")
    output.seek(0)

    st.download_button(
        label="📥 Download Translated File",
        data=output,
        file_name="translated_output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.info(f"✅ Done! Time elapsed: {elapsed_time:.2f} seconds")
