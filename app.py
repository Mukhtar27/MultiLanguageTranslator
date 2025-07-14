import streamlit as st
import pandas as pd
from googletrans import Translator
import io
import time

# 📄 Title and instructions
st.title("📗 Multi-Language Translator with Transliteration")
st.write("Upload an Excel file with names or text. Choose source and target language for translation and transliteration.")

# 📂 File uploader
uploaded_file = st.file_uploader("Upload Excel file (.xlsx)", type=["xlsx"])

# Language selection options
LANGUAGE_OPTIONS = {
    "Arabic": "ar",
    "English": "en",
    "Hindi": "hi",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Chinese (Simplified)": "zh-CN",
    "Japanese": "ja",
    "Russian": "ru",
    "Urdu": "ur"
}

col1, col2 = st.columns(2)
with col1:
    source_lang_label = st.selectbox("Select source language", list(LANGUAGE_OPTIONS.keys()), index=0)
with col2:
    target_lang_label = st.selectbox("Select target language", list(LANGUAGE_OPTIONS.keys()), index=1)

source_lang = LANGUAGE_OPTIONS[source_lang_label]
target_lang = LANGUAGE_OPTIONS[target_lang_label]

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("✅ File uploaded successfully.")

    # Ask for column name containing text
    columns = df.columns.tolist()
    column = st.selectbox("Select column to translate:", columns)

    if st.button("🔁 Translate"):
        try:
            translator = Translator()
            translations = []
            transliterations = []
            errors = 0

            progress = st.progress(0)
            status_text = st.empty()
            start_time = time.time()

            for i, text in enumerate(df[column]):
                try:
                    result = translator.translate(str(text), src=source_lang, dest=target_lang)
                    translated_text = result.text
                    transliteration = result.pronunciation if result.pronunciation else ""
                except Exception:
                    translated_text = "⚠️ Error"
                    transliteration = ""
                    errors += 1

                translations.append(translated_text)
                transliterations.append(transliteration)

                progress.progress((i + 1) / len(df))
                status_text.text(f"Translating... {int((i + 1) / len(df) * 100)}%")

            elapsed = time.time() - start_time

            # Add results to DataFrame
            df["Translated"] = translations
            df["Transliteration"] = transliterations

            st.subheader("🔍 Preview")
            st.dataframe(df)

            # Download button
            output = io.BytesIO()
            df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)

            st.download_button(
                label="📥 Download Translated Excel",
                data=output,
                file_name="translated_output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.success(f"✅ Translation complete. Errors: {errors}")
            st.info(f"⏱️ Time elapsed: {elapsed:.2f} seconds")

        except Exception as e:
            st.error("⚠️ Something went wrong during translation.")
            st.exception(e)
