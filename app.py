import streamlit as st
import pandas as pd
from deep_translator import GoogleTranslator, single_detection
import time
import io

st.set_page_config(page_title="Multilingual Translator", layout="wide")

# Title
st.title("🌍 Multilingual Translator & Transliterator")
st.write("Upload an Excel file, select a column, and choose languages to translate and transliterate the text.")

# Upload file
uploaded_file = st.file_uploader("📤 Upload Excel File (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("✅ File uploaded successfully!")

        # Select column
        columns = df.columns.tolist()
        text_column = st.selectbox("Select column to translate:", columns)

        # Select language pair
        st.markdown("### 🌐 Translation Settings")
        available_languages = GoogleTranslator(source='auto', target='en').get_supported_languages(as_dict=True)
        lang_keys = list(available_languages.keys())

        source_lang = st.selectbox("Translate from (source language)", options=lang_keys, index=lang_keys.index("arabic"))
        target_lang = st.selectbox("Translate to (target language)", options=lang_keys, index=lang_keys.index("english"))

        do_transliterate = st.checkbox("🔡 Show Transliteration (Latin script)", value=True)

        if st.button("🚀 Translate"):
            progress = st.progress(0)
            status_text = st.empty()
            start_time = time.time()

            translator = GoogleTranslator(source=source_lang, target=target_lang)
            translations = []
            transliterations = []
            errors = 0

            text_list = df[text_column].astype(str).tolist()
            total = len(text_list)

            for i, text in enumerate(text_list):
                try:
                    translated = translator.translate(text)
                    translations.append(translated)

                    if do_transliterate:
                        # Get transliteration only for supported languages
                        transliterations.append(GoogleTranslator(source=source_lang, target="en").translate(text))
                    else:
                        transliterations.append("")
                except Exception:
                    translations.append("⚠️ Error")
                    transliterations.append("")
                    errors += 1

                progress.progress((i + 1) / total)
                status_text.text(f"Processing {i + 1} of {total}...")

            # Append to DataFrame
            df["Translated"] = translations
            if do_transliterate:
                df["Transliteration"] = transliterations

            # Time summary
            elapsed = time.time() - start_time
            st.success(f"✅ Done! Time taken: {elapsed:.2f} seconds | Errors: {errors}")

            # Preview
            st.dataframe(df)

            # Download
            output = io.BytesIO()
            df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)

            st.download_button(
                label="📥 Download Translated Excel",
                data=output,
                file_name="translated_output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error("⚠️ Something went wrong. Please check your file format.")
        st.exception(e)
