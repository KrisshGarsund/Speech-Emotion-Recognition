import os
import io
import time
import tempfile
import requests
import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wav
import librosa
import plotly.graph_objects as go
import streamlit as st

# ===============================
# Page config and global styles
# ===============================
st.set_page_config(
    page_title="AuraVoice - Speech Emotion Recognition",
    page_icon="🎤",
    layout="wide"
)

ACCENT = "#c4f82a"
BG_DARK = "#0B0C10"
CARD_BG = "#141823"
TEXT = "#E6F1FF"
TEXT_MUTED = "#8892b0"

st.markdown(
    f"""
    <style>
      .stApp {{ background: radial-gradient(1200px 800px at 0% 0%, #0b0c10 0%, #0b0c10 40%, #0f1220 100%); }}
      section[data-testid="stSidebar"] {{ background-color: {CARD_BG}; border-right: 1px solid rgba(255,255,255,0.08); }}
      .auravoice-title {{
        display:flex; align-items:center; gap:.6rem; font-weight:800; letter-spacing:.5px;
        color:{TEXT};
      }}
      .badge {{ padding:.2rem .5rem; border-radius:.4rem; border:1px solid rgba(255,255,255,.1); color:{TEXT_MUTED}; }}
      .card {{ background:{CARD_BG}; border:1px solid rgba(255,255,255,0.06); padding:1.25rem 1.25rem; border-radius:14px; }}
      .accent {{ color:{ACCENT}; }}
      .muted {{ color:{TEXT_MUTED}; }}
      .metric-card {{ display:flex; align-items:center; gap:14px; }}
      .metric-dot {{ width:10px; height:10px; border-radius:50%; background:{ACCENT}; box-shadow:0 0 16px {ACCENT}; }}
      .stButton>button {{ background:{ACCENT}; color:black; font-weight:700; border:none; }}
      .stProgress > div > div > div {{ background:{ACCENT}; }}
      .st-emotion-cache-1y4p8pa p, .stMarkdown p {{ color:{TEXT_MUTED}; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ===============================
# Config
# ===============================
DEFAULT_API = os.environ.get("AURAVOICE_API", "http://127.0.0.1:5000/predict")

EMOJI_MAP = {
    "Happy": "😊", "Sad": "😢", "Angry": "😠", "Fearful": "😳",
    "Calm": "🍃", "Surprised": "😲", "Disgust": "🤢", "Neutral": "😐"
}

# ===============================
# Utils
# ===============================
def send_to_backend(file_path: str, api_url: str):
    with open(file_path, "rb") as f:
        files = {"file": f}
        try:
            resp = requests.post(api_url, files=files, headers={"Accept": "application/json"}, timeout=60)
            data = resp.json()
            return data, None
        except Exception as e:
            return None, f"API error: {e}"

def to_csv_bytes(result: dict) -> bytes:
    out = io.StringIO()
    out.write("Emotion,Probability\n")
    probs = ((result.get("detailed_analysis") or {}).get("all_emotions") or [])
    for p in probs:
        out.write(f"{p['emotion']},{p['percentage']}%\n")
    out.write("\n")
    out.write(f"Predicted Emotion,{result.get('prediction','')}\n")
    out.write(f"Confidence,{result.get('confidence','')}\n")
    return out.getvalue().encode()

def plot_confidence_gauge(confidence_pct: float):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=confidence_pct,
        number={"suffix": "%", "font": {"color": TEXT, "size": 32}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": TEXT_MUTED},
            "bar": {"color": ACCENT},
            "bgcolor": "rgba(255,255,255,0.02)",
            "bordercolor": "rgba(255,255,255,0.08)",
            "steps": [
                {"range": [0, 50], "color": "rgba(220,53,69,.15)"},
                {"range": [50, 75], "color": "rgba(255,193,7,.12)"},
                {"range": [75, 100], "color": "rgba(40,167,69,.12)"},
            ],
        },
        domain={"x":[0,1],"y":[0,1]}
    ))
    fig.update_layout(height=240, margin=dict(l=20,r=20,t=20,b=10), paper_bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT))
    return fig

def plot_probabilities_bar(prob_items: list):
    if not prob_items:
        return None
    labels = [p["emotion"].title() for p in prob_items]
    values = [p["percentage"] for p in prob_items]
    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker=dict(color=ACCENT),
        hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        height=360,
        margin=dict(l=80, r=20, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, color=TEXT_MUTED, range=[0,100]),
        yaxis=dict(showgrid=False, color=TEXT_MUTED),
        font=dict(color=TEXT)
    )
    return fig

def visualize_waveform(file_path: str):
    try:
        y, sr = librosa.load(file_path, mono=True)
        dur = len(y)/sr
        st.caption(f"Waveform • {dur:.2f}s @ {sr} Hz")
        st.line_chart(y)
    except Exception:
        st.caption("Waveform preview unavailable for this file")

# ===============================
# Sidebar
# ===============================
st.sidebar.markdown("<div class='auravoice-title'><span style='color:#c4f82a'>◉</span> AuraVoice <span class='badge'>Streamlit</span></div>", unsafe_allow_html=True)
api_url = st.sidebar.text_input("Backend API", value=DEFAULT_API, help="Flask /predict endpoint")
st.sidebar.divider()
st.sidebar.markdown("**Input Source**")
mode = st.sidebar.segmented_control("Input Source", options=["Upload", "Record"], default="Upload", label_visibility="collapsed")
duration = None
if mode == "Record":
    duration = st.sidebar.slider("Recording duration (s)", 2, 10, 4)
st.sidebar.divider()
st.sidebar.markdown("**Session**")
clear_session = st.sidebar.button("Clear History")
if clear_session:
    st.session_state.pop("history", None)

# ===============================
# Header
# ===============================
colA, colB = st.columns([0.72, 0.28])
with colA:
    st.markdown(
        f"""
        <div class="card" style="display:flex; gap:10px; align-items:center;">
          <div class="metric-dot"></div>
          <div>
            <div style="font-size:22px; font-weight:800; color:{TEXT}">Decode the <span class='accent'>Emotion</span> Within the Voice</div>
            <div class="muted">Upload audio or record live. Get instant predictions with confidence and detailed probabilities.</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with colB:
    stats = st.container()
    with stats:
        hist = st.session_state.get("history", [])
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.metric("Analyses this session", len(hist))
        st.markdown("</div>", unsafe_allow_html=True)

st.write("")

# ===============================
# Input section
# ===============================
left, right = st.columns([0.52, 0.48])
prediction_result = None

with left:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    if mode == "Upload":
        uploaded = st.file_uploader("Upload an audio file", type=["wav","mp3","ogg","webm","m4a","flac"], accept_multiple_files=False)
        temp_path = None
        if uploaded is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded.name)[1] or ".wav") as tmp:
                tmp.write(uploaded.read())
                temp_path = tmp.name
            st.audio(temp_path)
            visualize_waveform(temp_path)
        if st.button("Analyze Emotion", type="primary", disabled=(uploaded is None)):
            with st.spinner("Analyzing..."):
                data, err = send_to_backend(temp_path, api_url)
            if err:
                st.error(err)
            elif data and ("prediction" in data or "detailed_analysis" in data):
                prediction_result = data
            else:
                st.error("Unexpected response from backend")
    else:
        fs = 44100
        st.caption("Record using your microphone")
        rec_go = st.button("Start Recording", type="primary")
        temp_path = None
        if rec_go and duration:
            with st.spinner("Recording..."):
                recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="float32")
                sd.wait()
            recording_int16 = (recording * 32767).astype(np.int16)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                wav.write(tmp.name, fs, recording_int16)
                temp_path = tmp.name
            st.success("Recording complete")
            st.audio(temp_path)
            visualize_waveform(temp_path)
        if st.button("Analyze Recording", disabled=(temp_path is None)):
            with st.spinner("Analyzing..."):
                data, err = send_to_backend(temp_path, api_url)
            if err:
                st.error(err)
            elif data and ("prediction" in data or "detailed_analysis" in data):
                prediction_result = data
            else:
                st.error("Unexpected response from backend")
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Results")
    if prediction_result is None:
        st.caption("Results will appear here after analysis.")
    else:
        emotion = prediction_result.get("prediction") or prediction_result.get("emotion") or "—"
        conf_val = prediction_result.get("confidence")
        try:
            if isinstance(conf_val, str) and conf_val.endswith("%"):
                confidence_pct = float(conf_val.replace("%",""))
            elif isinstance(conf_val, (int, float)) and conf_val <= 1:
                confidence_pct = float(conf_val) * 100
            else:
                confidence_pct = float(conf_val or 0)
        except Exception:
            confidence_pct = 0.0

        emoji = EMOJI_MAP.get(emotion, "🎧")
        st.markdown(f"#### {emoji} {emotion}")
        st.plotly_chart(plot_confidence_gauge(confidence_pct), use_container_width=True, theme=None)

        analysis = (prediction_result.get("detailed_analysis") or {})
        probs = analysis.get("all_emotions") or []
        if probs:
            fig = plot_probabilities_bar(probs)
            if fig:
                st.plotly_chart(fig, use_container_width=True, theme=None)
        summary = analysis.get("analysis_text")
        if summary:
            st.markdown("**Summary**")
            st.write(summary)
        recs = analysis.get("recommendations") or []
        if recs:
            st.markdown("**Recommendations**")
            for r in recs:
                st.write(f"- {r}")

        item = {
            "ts": int(time.time()),
            "emotion": emotion,
            "confidence": round(confidence_pct, 2),
            "detail": analysis,
        }
        hist = st.session_state.get("history", [])
        hist.append(item)
        st.session_state["history"] = hist

        csv_bytes = to_csv_bytes(prediction_result)
        st.download_button("Download CSV", data=csv_bytes, file_name=f"emotion_prediction_{int(time.time())}.csv", mime="text/csv")
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")

# ===============================
# History section
# ===============================
st.markdown("### Recent Analyses")
hist = st.session_state.get("history", [])
if not hist:
    st.caption("No analyses yet.")
else:
    cols = st.columns(3)
    for i, h in enumerate(reversed(hist[-9:])):
        with cols[i % 3]:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown(f"**{EMOJI_MAP.get(h['emotion'], '🎧')} {h['emotion']}**")
            st.progress(min(100, max(0, int(h['confidence']))))
            st.caption(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(h['ts'])))
            st.markdown("</div>", unsafe_allow_html=True)


