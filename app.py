import os
import streamlit as st
import pandas as pd
# from dotenv import load_dotenv
from PIL import Image
from pathlib import Path
import html as _html
from typing import Tuple
from urllib.parse import quote_plus

# Load environment early so helper modules see env vars when imported
# Use override=True so values in .env replace any existing environment variables
# load_dotenv(override=True)


from utils.gpt import chat
from utils.sheets import load_industry_sheets
from utils.resume import extract_text_from_pdf, limit_text

st.set_page_config(page_title="Econ Club Internship Assistant", page_icon="🎓", layout="wide")

# Load logo if present; avoid crashing the app when the image is missing or unreadable.
assets_dir = Path(__file__).resolve().parent / "assets"
logo_path = assets_dir / "club_logo.png"
try:
    if logo_path.exists():
        logo = Image.open(logo_path)
        st.image(logo, width=150)
    else:
        st.header("Econ Club Internship Assistant")
except Exception:
    st.header("Econ Club Internship Assistant")

# Style
st.markdown("""
<style>
/* tighter chat width */
.block-container {max-width: 1000px;}
/* subtle dividers */
hr {margin: 0.5rem 0 1rem 0;}
</style>
""", unsafe_allow_html=True)

# -------------- session --------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.user = {"name": "", "major": "", "grad_year": "", "industry": "", "location": ""}
    st.session_state.index = 0
    st.session_state.results = pd.DataFrame()
if "industries" not in st.session_state:
    try:
        st.session_state.industries = load_industry_sheets()  # Dict[str, DataFrame]
    except Exception as e:
        st.error(f"Could not load Google Sheets. {e}")
        st.stop()

# Helpers
def filter_rows(df: pd.DataFrame, major: str, location: str = "") -> pd.DataFrame:
    out = df.copy()
    if major:
        out = out[out["Eligible Majors"].astype(str).str.contains(major, case=False, na=False)]
    if location:
        out = out[out["Location"].astype(str).str.contains(location, case=False, na=False)]
    return out.reset_index(drop=True)

def format_batch(rows: pd.DataFrame) -> str:
    """Return an HTML string for a batch of internship rows.

    Each internship shows a blue title link and an 'Apply here' button.
    """
    parts = []
    def _normalize_link(link: str, title: str, company: str) -> Tuple[str, bool]:
        """Return (url, is_fallback).

        If the provided link is a valid external URL (has http/https or contains a dot and no leading '/'),
        normalize and return it with is_fallback=False. Otherwise return a Google search URL with is_fallback=True.
        """
        link = (link or "").strip()
        if not link:
            return ("https://www.google.com/search?q=" + quote_plus(f"{title} {company} application"), True)
        low = link.lower()
        # Already an absolute URL
        if low.startswith("http://") or low.startswith("https://") or low.startswith("//"):
            return (link if low.startswith("http") else ("https:" + link), False)
        # Looks like a domain without scheme
        if "." in link and not link.startswith("/"):
            return ("https://" + link, False)
        # Anything else (starts with '/' or contains spaces) -> fallback to search
        return ("https://www.google.com/search?q=" + quote_plus(f"{title} {company} application"), True)

    for _, r in rows.iterrows():
        title = _html.escape(str(r["Internship Title"]).strip())
        company = _html.escape(str(r["Company"]).strip())
        loc = _html.escape(str(r["Location"]).strip())
        raw_link = str(r["Link"]).strip()
        link, was_fallback = _normalize_link(raw_link, title, company)

        # Prepare safe variants for HTML href and JS onclick
        link_href = _html.escape(link, quote=True)
        # JS-escape backslashes and single quotes
        link_js = link.replace('\\', '\\\\').replace("'", "\\'")
        frag = []
        frag.append('<div style="margin-bottom:0.75rem; padding:6px 0; border-bottom:1px solid #eee;">')
        # Title: use an actual href plus onclick backup; target=_blank opens in new tab
        frag.append(
            f'<a href="{link_href}" target="_blank" rel="noopener noreferrer" onclick="window.open(\'{link_js}\', \'_blank\')" '
            f'style="color:#1a73e8;font-weight:600;text-decoration:underline;font-size:1.03em;">{title}</a> '
        )
        frag.append(f'<span style="color:#444;">&nbsp;at&nbsp;<em>{company}</em></span>')
        frag.append(f'<div style="color:#666;margin-top:4px;">📍 {loc if loc else "Location: N/A"}</div>')
        # Apply button also uses window.open
        frag.append(
            f'<a href="{link_href}" target="_blank" rel="noopener noreferrer" onclick="window.open(\'{link_js}\', \'_blank\')" '
            f'style="display:inline-block;margin-top:6px;padding:6px 10px;background:#1a73e8;color:#fff;border-radius:6px;text-decoration:none;">Apply here</a>'
        )
        if was_fallback:
            frag.append('<span style="margin-left:8px;color:#999;font-size:0.9em;">(search)</span>')
        frag.append('</div>')
        item_html = ''.join(frag)
        parts.append(item_html)

    # Wrap the batch in a container so spacing is preserved when rendered as HTML
    return "".join(parts)


def assistant_say(text: str):
    st.session_state.messages.append({"role": "assistant", "content": text})
    with st.chat_message("assistant"):
        st.markdown(text, unsafe_allow_html=True)


def user_say(text: str):
    st.session_state.messages.append({"role": "user", "content": text})
    with st.chat_message("user"):
        st.markdown(text, unsafe_allow_html=True)

# -------------- sidebar: resume feedback --------------
with st.sidebar:
    st.header("Resume or experience feedback")
    st.caption("Paste your resume text or upload a PDF. The AI will suggest fit and improvements.")
    resume_text = st.text_area("Paste text", height=180, placeholder="Paste resume bullets, roles, projects, skills...")
    pdf_file = st.file_uploader("Or upload PDF", type=["pdf"])
    target_note = st.text_input("Optional: target role or industry", placeholder="Example: Finance internships in NYC")

    if st.button("Get feedback"):
        content = resume_text
        if not content and pdf_file:
            try:
                content = extract_text_from_pdf(pdf_file)
            except Exception as e:
                st.error(f"Could not read PDF. {e}")
        if not content:
            st.warning("Add text or upload a PDF")
        else:
            content = limit_text(content)
            prompt = [
                {"role": "system", "content": "You are a practical career assistant for college students. Be concise and specific. Avoid fluff."},
                {"role": "user", "content": f"Here is my resume content:\n\n{content}\n\nTarget (optional): {target_note or 'none'}\n\nGive feedback on fit for internships, suggest improvements, and list 3 concrete next actions."}
            ]
            try:
                out = chat(prompt, temperature=0.4)
                st.success("Feedback ready")
                st.markdown(out)
            except Exception as e:
                st.error(f"OpenAI error: {e}")

st.title("Econ Club Internship Assistant")

# -------------- greeting or instructions --------------
if len(st.session_state.messages) == 0:
    greeting = (
        "Hi there, welcome to the Econ Club Internship Assistant.\n\n"
        "How to use this chat:\n"
        "• Start with your **name** or your **major**\n"
        "• The assistant will ask a few quick questions\n"
        "• Then it will show **5 internships at a time** with links\n"
        "• You can ask for **more** until the list ends\n"
        "• You can try another **industry** or **location** anytime\n\n"
        "Say hello to begin."
    )
    assistant_say(greeting)

# -------------- show history --------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# -------------- chat input --------------
prompt = st.chat_input("Type here")
if prompt:
    user_say(prompt)

    # Steps
    # 0: ask name
    if st.session_state.step == 0:
        st.session_state.user["name"] = prompt.strip()
        reply = f"Nice to meet you. What is your major?"
        assistant_say(reply)
        st.session_state.step = 1

    # 1: ask major
    elif st.session_state.step == 1:
        st.session_state.user["major"] = prompt.strip()
        # List industries available from sheet tabs
        tabs = list(st.session_state.industries.keys())
        tab_list = ", ".join(tabs)
        reply = f"Got it. Which industry do you want to explore first? Choices: {tab_list}"
        assistant_say(reply)
        st.session_state.step = 2

    # 2: ask industry
    elif st.session_state.step == 2:
        choice = prompt.strip()
        tabs_lower = {k.lower(): k for k in st.session_state.industries.keys()}
        if choice.lower() not in tabs_lower:
            reply = "I did not find that industry. Please type one of the listed options."
            assistant_say(reply)
        else:
            sel = tabs_lower[choice.lower()]
            st.session_state.user["industry"] = sel
            reply = "Any preferred location? You can type city or state. You can also type skip."
            assistant_say(reply)
            st.session_state.step = 3

    # 3: ask location then fetch
    elif st.session_state.step == 3:
        location = "" if prompt.strip().lower() == "skip" else prompt.strip()
        st.session_state.user["location"] = location

        df = st.session_state.industries[st.session_state.user["industry"]]
        results = filter_rows(df, st.session_state.user["major"], location)
        st.session_state.results = results
        st.session_state.index = 0

        if len(results) == 0:
            assistant_say("I could not find any internships for that combo. Do you want to try another industry or change the location?")
            st.session_state.step = 5  # switch flow
        else:
            batch = results.iloc[0:5]
            st.session_state.index = 5
            show = format_batch(batch)
            reply = f"Here are 5 internships:\n\n{show}\n\nDo you want to see more?"
            assistant_say(reply)
            st.session_state.step = 4

    # 4: more paging or end
    elif st.session_state.step == 4:
        say = prompt.strip().lower()
        if say in ["yes", "y", "more", "next", "show more"]:
            start, end = st.session_state.index, st.session_state.index + 5
            batch = st.session_state.results.iloc[start:end]
            if len(batch) == 0:
                assistant_say("We reached the end of the list. Do you want to look into another industry or change the location?")
                st.session_state.step = 5
            else:
                st.session_state.index += len(batch)
                show = format_batch(batch)
                reply = f"Here are more:\n\n{show}\n\nDo you want to see more?"
                assistant_say(reply)
        else:
            assistant_say("Okay. Do you want to try another industry or update the location?")
            st.session_state.step = 5

    # 5: switch industry or location
    elif st.session_state.step == 5:
        text = prompt.strip()
        # simple intent guess
        if text.lower().startswith("industry"):
            # expected: "industry Finance" or "industry Research"
            parts = text.split(maxsplit=1)
            if len(parts) == 2:
                new_ind = parts[1].strip()
                tabs_lower = {k.lower(): k for k in st.session_state.industries.keys()}
                if new_ind.lower() in tabs_lower:
                    st.session_state.user["industry"] = tabs_lower[new_ind.lower()]
                    assistant_say("Got it. Any location filter? You can type skip.")
                    st.session_state.step = 3
                else:
                    assistant_say("I did not find that industry. Try again with a listed one.")
            else:
                assistant_say("Type like this: industry Finance")
        elif text.lower().startswith("location"):
            # expected: "location NYC" or "location skip"
            parts = text.split(maxsplit=1)
            if len(parts) == 2:
                val = parts[1].strip()
                st.session_state.user["location"] = "" if val.lower() == "skip" else val
                # rerun the filter with new location on current industry
                df = st.session_state.industries[st.session_state.user["industry"]]
                results = filter_rows(df, st.session_state.user["major"], st.session_state.user["location"])
                st.session_state.results = results
                st.session_state.index = 0
                if len(results) == 0:
                    assistant_say("No results for that filter. Try another location or industry.")
                else:
                    batch = results.iloc[0:5]
                    st.session_state.index = 5
                    show = format_batch(batch)
                    assistant_say(f"Here are 5 internships:\n\n{show}\n\nDo you want to see more?")
                    st.session_state.step = 4
            else:
                assistant_say("Type like this: location NYC  or  location skip")
        else:
            # guide the user
            assistant_say("You can type one of these:\n• industry Finance\n• industry Research\n• location NYC\n• location skip")
