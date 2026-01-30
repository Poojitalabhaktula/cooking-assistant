import streamlit as st
from groq import Groq
import os
import tempfile
from gtts import gTTS
from langdetect import detect

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="AI Multi-Language Cooking Assistant",
    page_icon="🍳",
    layout="wide"   # 👈 important for columns
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ---------------- HELPERS ----------------
def detect_language(text):
    try:
        return detect(text)
    except:
        return "en"

def generate_recipe(prompt, lang):
    system_prompt = f"""
You are a professional AI cooking assistant.

RULES:
1. Answer ONLY cooking-related questions.
2. If unrelated, reply ONLY:
   "Sorry, I only provide cooking and recipe-related information."
3. For recipes:
   - Mention VEG or NON-VEG
   - Ingredients with quantities
   - Step-by-step cooking process
4. Respond in {lang}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )

    return response.choices[0].message.content

def update_recipe(old_recipe, suggestion, lang):
    prompt = f"""
Here is the original recipe:
{old_recipe}

User suggestion:
{suggestion}

Update the recipe based on the suggestion.
Keep ingredients, steps clear and improve accordingly.
Respond fully in {lang}.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a professional cooking assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )

    return response.choices[0].message.content

def text_to_audio(text, lang):
    try:
        tts = gTTS(text=text, lang=lang)
    except:
        tts = gTTS(text=text, lang="en")

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmp.name)
    return tmp.name

# ---------------- SESSION ----------------
if "recipe" not in st.session_state:
    st.session_state.recipe = ""

if "lang" not in st.session_state:
    st.session_state.lang = "en"

# ---------------- UI ----------------
st.title("🍽️ AI Multi-Language Cooking Assistant")

user_input = st.text_input("Enter your recipe question")

if st.button("Generate Recipe"):
    if user_input.strip():
        st.session_state.lang = detect_language(user_input)
        st.session_state.recipe = generate_recipe(
            user_input, st.session_state.lang
        )
    else:
        st.warning("Please enter a recipe question")

# ---------------- MAIN LAYOUT ----------------
if st.session_state.recipe:
    col1, col2 = st.columns([2, 1])  # 👈 Windows-style layout

    # 🔹 LEFT COLUMN – RECIPE
    with col1:
        st.subheader("📖 Recipe")
        st.write(st.session_state.recipe)

        audio = text_to_audio(
            st.session_state.recipe, st.session_state.lang
        )
        st.subheader("🔊 Voice Output")
        st.audio(audio)

    # 🔹 RIGHT COLUMN – SUGGESTIONS
    with col2:
        st.subheader("📝 Recipe Customization")

        suggestion = st.text_area(
            "Suggestions",
            placeholder="Less oil / Diet version / Cooker method / More spicy"
        )

        if st.button("Update Recipe"):
            if suggestion.strip():
                updated = update_recipe(
                    st.session_state.recipe,
                    suggestion,
                    st.session_state.lang
                )
                st.session_state.recipe = updated
                st.success("✅ Recipe updated based on your suggestion!")
            else:
                st.warning("Please enter a suggestion")

                