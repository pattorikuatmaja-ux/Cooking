import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# PENGATURAN API KEY DAN MODEL
# ==============================================================================

# Mengambil API key dari Streamlit Secrets untuk keamanan
# Pastikan Anda sudah mengatur variabel ini di Streamlit Cloud.
try:
    API_KEY = st.secrets["AIzaSyBWzMBC6hVzvooktYrFkO5fvrDuJKVxqio"]
except KeyError:
    st.error("API Key Gemini tidak ditemukan. Pastikan Anda telah menambahkannya di Streamlit Secrets.")
    st.stop()

MODEL_NAME = 'gemini-1.5-flash'

# ==============================================================================
# KONTEKS AWAL CHATBOT
# ==============================================================================

# Konteks awal untuk percakapan chatbot
INITIAL_CHATBOT_CONTEXT = [
    {
        "role": "user",
        "parts": ["Saya adalah Ahli Masak. Saya akan memberikan berbagai macam jenis resep masakan yang anda inginkan. Jawaban singkat dan jelas. Tolak pertanyaan selain tentang masakan."]
    },
    {
        "role": "model",
        "parts": ["Baik! Saya akan memberikan resep yang anda inginkan."]
    }
]

# ==============================================================================
# APLIKASI STREAMLIT
# ==============================================================================

st.title("👨‍🍳 Ahli Resep Masakan")

# Konfigurasi model Gemini
try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(
        MODEL_NAME,
        generation_config=genai.types.GenerationConfig(
            temperature=0.4,
            max_output_tokens=500
        )
    )
except Exception as e:
    st.error(f"Kesalahan saat menginisialisasi model Gemini: {e}")
    st.stop()

# Inisialisasi riwayat chat di Streamlit Session State
if "messages" not in st.session_state:
    st.session_state.messages = INITIAL_CHATBOT_CONTEXT.copy()

# Tampilkan riwayat pesan di antarmuka
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["parts"][0])

# Tangani input dari pengguna
user_input = st.chat_input("Ketik di sini untuk bertanya...")

if user_input:
    # Tambahkan input pengguna ke riwayat dan tampilkan
    st.session_state.messages.append({"role": "user", "parts": [user_input]})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Kirim riwayat chat ke model
    chat = model.start_chat(history=st.session_state.messages)
    
    # Tampilkan respons dari Gemini
    with st.chat_message("assistant"):
        with st.spinner("Sedang memproses..."):
            try:
                response = chat.send_message(user_input, request_options={"timeout": 60})
                if response and response.text:
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "model", "parts": [response.text]})
                else:
                    st.error("Maaf, saya tidak bisa memberikan balasan. Respons API kosong atau tidak valid.")
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")

