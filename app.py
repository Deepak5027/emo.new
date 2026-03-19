import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from collections import Counter
import random
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────── PAGE CONFIG ───────────────────────────
st.set_page_config(
    page_title="MindTrace – Emotion Analytics",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────── GLOBAL CSS ────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Serif+Display&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* ── Background ── */
.stApp {
    background: #0f0f1a;
    color: #e8e8f0;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #16162a !important;
    border-right: 1px solid #2a2a45;
}
section[data-testid="stSidebar"] * {
    color: #c8c8e0 !important;
}

/* ── Hide default header ── */
header[data-testid="stHeader"] { display: none; }

/* ── Metric Cards ── */
.card {
    background: #1c1c32;
    border: 1px solid #2e2e50;
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 0.8rem;
    position: relative;
    overflow: hidden;
}
.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--accent, #7c6af7);
    border-radius: 16px 16px 0 0;
}
.card-label {
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #7878a0;
    margin-bottom: 0.4rem;
}
.card-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent, #7c6af7);
    line-height: 1.1;
}
.card-sub {
    font-size: 0.78rem;
    color: #5a5a80;
    margin-top: 0.3rem;
}

/* ── Section headers ── */
.section-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.5rem;
    color: #e8e8f0;
    margin: 1.8rem 0 1rem;
}

/* ── Dashboard title ── */
.dash-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.4rem;
    color: #e8e8f0;
    letter-spacing: -0.5px;
}
.dash-sub {
    color: #5a5a80;
    font-size: 0.9rem;
    margin-top: 0.2rem;
}

/* ── Plotly chart containers ── */
.chart-wrap {
    background: #1c1c32;
    border: 1px solid #2e2e50;
    border-radius: 16px;
    padding: 1.2rem;
    margin-bottom: 1rem;
}

/* ── Textarea override ── */
textarea {
    background: #1c1c32 !important;
    color: #e8e8f0 !important;
    border: 1px solid #3a3a60 !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
}
textarea:focus {
    border-color: #7c6af7 !important;
    box-shadow: 0 0 0 2px rgba(124,106,247,0.25) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: #7c6af7 !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.2s !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stButton > button:hover {
    background: #6a58e5 !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(124,106,247,0.4) !important;
}

/* ── Radio buttons ── */
div[data-testid="stRadio"] label {
    color: #c8c8e0 !important;
}

/* ── Select box ── */
div[data-testid="stSelectbox"] select,
div[data-testid="stSelectbox"] > div {
    background: #1c1c32 !important;
    color: #e8e8f0 !important;
    border-color: #3a3a60 !important;
}

/* ── Slider ── */
div[data-testid="stSlider"] {
    color: #7c6af7 !important;
}

/* ── Info / Warning boxes ── */
div[data-testid="stInfo"], div[data-testid="stWarning"], div[data-testid="stSuccess"] {
    border-radius: 10px !important;
    border: 1px solid #2e2e50 !important;
    background: #1c1c32 !important;
}

/* ── Divider ── */
hr { border-color: #2e2e50 !important; }

/* ── Emotion pill badges ── */
.emotion-pill {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    margin: 2px;
}

/* ── Risk badge ── */
.risk-high   { color: #ff6b6b; }
.risk-medium { color: #ffd93d; }
.risk-low    { color: #6bcb77; }

/* ── Journal entry card ── */
.journal-card {
    background: #1c1c32;
    border: 1px solid #2e2e50;
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.9rem;
}
.journal-date {
    font-size: 0.75rem;
    color: #5a5a80;
    margin-bottom: 0.4rem;
}
.journal-text {
    color: #c8c8e0;
    font-size: 0.88rem;
    line-height: 1.6;
    margin-bottom: 0.6rem;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0f0f1a; }
::-webkit-scrollbar-thumb { background: #2e2e50; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────── EMOTION HELPERS ──────────────────────────

EMOTION_COLORS = {
    'happy':       '#ffd93d',
    'content':     '#6bcb77',
    'neutral':     '#95e1d3',
    'anxious':     '#ff9f43',
    'sad':         '#4d96ff',
    'overwhelmed': '#ff6b6b',
}

EMOTION_KEYWORDS = {
    'happy':       ['happy', 'joy', 'excited', 'great', 'wonderful', 'amazing', 'love', 'grateful', 'blessed', 'fantastic', 'delighted'],
    'content':     ['content', 'calm', 'peaceful', 'satisfied', 'okay', 'fine', 'good', 'relaxed', 'comfortable'],
    'anxious':     ['anxious', 'anxiety', 'worried', 'nervous', 'stress', 'tense', 'uneasy', 'panic', 'fear', 'dread'],
    'sad':         ['sad', 'unhappy', 'depressed', 'down', 'blue', 'cry', 'tears', 'heartbroken', 'lonely', 'miserable', 'grief'],
    'overwhelmed': ['overwhelmed', 'tired', 'exhausted', 'burnout', 'pressure', 'too much', 'can\'t cope', 'breaking', 'drained'],
    'neutral':     [],
}

POSITIVE_WORDS = {'happy', 'joy', 'great', 'wonderful', 'amazing', 'love', 'grateful', 'blessed',
                  'fantastic', 'delighted', 'content', 'calm', 'peaceful', 'satisfied', 'good',
                  'relaxed', 'comfortable', 'hope', 'laugh', 'smile', 'excited'}
NEGATIVE_WORDS = {'sad', 'unhappy', 'depressed', 'down', 'cry', 'tears', 'heartbroken', 'lonely',
                  'miserable', 'anxious', 'worried', 'nervous', 'stress', 'tense', 'panic', 'fear',
                  'overwhelmed', 'tired', 'exhausted', 'burnout', 'drained', 'angry', 'hate', 'worst'}


def detect_emotions(text: str) -> list:
    text_lower = text.lower()
    found = []
    for emotion, keywords in EMOTION_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            found.append(emotion)
    return found if found else ['neutral']


def calculate_sentiment(text: str) -> float:
    words = text.lower().split()
    pos = sum(1 for w in words if w in POSITIVE_WORDS)
    neg = sum(1 for w in words if w in NEGATIVE_WORDS)
    total = pos + neg
    if total == 0:
        return 0.0
    return round((pos - neg) / total, 3)


def calculate_intensity(text: str, emotions: list) -> float:
    base = 30 + len(text) * 0.05
    negative_emotions = {'anxious', 'sad', 'overwhelmed'}
    penalty = sum(15 for e in emotions if e in negative_emotions)
    return min(100, round(base + penalty + random.uniform(-5, 5), 1))


def primary_emotion(emotions: list) -> str:
    priority = ['overwhelmed', 'anxious', 'sad', 'happy', 'content', 'neutral']
    for p in priority:
        if p in emotions:
            return p
    return emotions[0]


# ──────────────────────── SAMPLE DATA GEN ──────────────────────────

def load_sample_data() -> list:
    sample_texts = [
        "Today was absolutely wonderful! I finished my project and my team loved it. Feeling so grateful.",
        "I couldn't sleep last night, anxiety kept me awake. Worried about tomorrow's presentation.",
        "Quiet Sunday. Made coffee, read for an hour. Content is the word.",
        "Overwhelmed with deadlines. Feel like I can't breathe. Everything is piling up at once.",
        "Went for a run this morning and it genuinely lifted my mood. Happy and energized now.",
        "Feeling low today. Missing family. Everything feels distant and heavy.",
        "Bit nervous about the meeting but it went well! Proud of how I handled it.",
        "Really tired. Long week. My mind keeps racing about things I can't control.",
        "Had lunch with an old friend. Laughed so much. Grateful for real connections.",
        "Sad again. Can't explain why. Just an emptiness that won't leave.",
        "Calm evening. Journaling helps me breathe. Feeling peaceful and reflective.",
        "Anxiety spiked again today. Work stress is becoming too much to handle.",
        "Great news: got the promotion! Excited and a little overwhelmed at the same time.",
        "Neutral day. Not good, not bad. Just... existing.",
        "Cried in the bathroom at work. Felt lonely and miserable. Need to talk to someone.",
        "Meditation session this morning. Feeling content and clear-headed going into the day.",
        "Stressed about finances. Worried constantly. Hard to focus on anything else.",
        "Wonderful hike today! Nature always resets me. Happy and calm now.",
        "Exhausted emotionally. Burnout is real. Need a break desperately.",
        "Grateful for small things today: warm tea, sunshine, a good book.",
    ]
    dates = pd.date_range(end=datetime.now(), periods=20, freq='D')
    entries = []
    for i, (date, text) in enumerate(zip(dates, sample_texts)):
        emo = detect_emotions(text)
        entries.append({
            'date': date,
            'text': text,
            'emotions': emo,
            'primary_emotion': primary_emotion(emo),
            'sentiment_score': calculate_sentiment(text),
            'emotional_intensity': calculate_intensity(text, emo),
            'word_count': len(text.split()),
            'mood_stability': round(random.uniform(40, 95), 1),
        })
    return entries


# ──────────────────────── METRIC HELPERS ───────────────────────────

def calculate_metrics(entries: list) -> dict:
    if not entries:
        return {}
    sentiments   = [e['sentiment_score'] for e in entries]
    intensities  = [e['emotional_intensity'] for e in entries]
    stabilities  = [e['mood_stability'] for e in entries]
    emotions     = [e['primary_emotion'] for e in entries]

    recent_int   = intensities[-7:] if len(intensities) >= 7 else intensities
    burnout_val  = np.mean(recent_int)

    return {
        'total_entries':    len(entries),
        'dominant_emotion': Counter(emotions).most_common(1)[0][0],
        'avg_sentiment':    round(np.mean(sentiments), 3),
        'sentiment_trend':  'Improving' if sentiments[-1] > sentiments[0] else 'Declining',
        'stability_score':  round(np.mean(stabilities), 1),
        'avg_intensity':    round(np.mean(intensities), 1),
        'recent_intensity': round(burnout_val, 1),
        'burnout_risk':     'High' if burnout_val > 72 else 'Medium' if burnout_val > 50 else 'Low',
        'total_words':      sum(e['word_count'] for e in entries),
    }


# ──────────────────────── PLOTLY THEME ─────────────────────────────

PLOT_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='DM Sans', color='#9090b8'),
    margin=dict(l=40, r=20, t=40, b=40),
    xaxis=dict(gridcolor='#22223a', linecolor='#22223a', zerolinecolor='#22223a'),
    yaxis=dict(gridcolor='#22223a', linecolor='#22223a', zerolinecolor='#22223a'),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#c8c8e0')),
)


# ════════════════════════ SESSION STATE ════════════════════════════

if 'journal_entries' not in st.session_state:
    st.session_state.journal_entries = []
if 'use_sample' not in st.session_state:
    st.session_state.use_sample = True


# ══════════════════════════ SIDEBAR ════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style='padding: 1rem 0 0.5rem;'>
        <span style='font-family:"DM Serif Display",serif;font-size:1.4rem;color:#e8e8f0;'>🧠 MindTrace</span><br>
        <span style='font-size:0.72rem;color:#5a5a80;letter-spacing:0.1em;text-transform:uppercase;'>Emotion Analytics</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    view_option = st.radio(
        "Navigate",
        ["📊 Overview", "✍️ Add Journal Entry", "📈 Trends & Predictions", "⚠️ Risk Assessment", "📋 Entry History"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("<span style='font-size:0.78rem;color:#5a5a80;text-transform:uppercase;letter-spacing:0.1em;'>Data Source</span>", unsafe_allow_html=True)
    use_sample = st.toggle("Use Sample Data", value=st.session_state.use_sample)
    st.session_state.use_sample = use_sample

    if st.button("🔄 Regenerate Sample", use_container_width=True):
        st.session_state.journal_entries = load_sample_data()
        st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style='background:#16162a;border:1px solid #2e2e50;border-radius:10px;padding:0.9rem;font-size:0.78rem;color:#7878a0;line-height:1.6;'>
        ⚠️ <strong style='color:#c8c8e0;'>Safety Notice</strong><br>
        This tool provides wellness insights only — not clinical diagnosis. 
        Please consult a licensed therapist or mental health professional for proper care.
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────── LOAD DATA ────────────────────────────────

if use_sample or not st.session_state.journal_entries:
    if not st.session_state.journal_entries or use_sample:
        entries = load_sample_data()
    else:
        entries = st.session_state.journal_entries
else:
    entries = st.session_state.journal_entries

metrics = calculate_metrics(entries)

view = view_option.split(" ", 1)[1] if " " in view_option else view_option


# ══════════════════════════ VIEWS ══════════════════════════════════

# ── HEADER ──
st.markdown(f"""
<div style='margin-bottom:1.5rem;'>
    <div class='dash-title'>Emotion Analytics Dashboard</div>
    <div class='dash-sub'>Tracking your mental wellness journey • {len(entries)} entries loaded</div>
</div>
""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━ VIEW: OVERVIEW ━━━━━━━━━━━━━━━━━━━━
if view == "Overview":

    # ── KPI Row ──
    c1, c2, c3, c4, c5 = st.columns(5)

    burnout = metrics.get('burnout_risk', 'Low')
    stability = metrics.get('stability_score', 0)
    sentiment = metrics.get('avg_sentiment', 0)

    with c1:
        st.markdown(f"""<div class='card' style='--accent:#7c6af7;'>
            <div class='card-label'>Total Entries</div>
            <div class='card-value'>{metrics.get('total_entries', 0)}</div>
            <div class='card-sub'>{metrics.get('total_words', 0):,} words written</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        dom = metrics.get('dominant_emotion', 'N/A')
        col = EMOTION_COLORS.get(dom, '#7c6af7')
        st.markdown(f"""<div class='card' style='--accent:{col};'>
            <div class='card-label'>Dominant Emotion</div>
            <div class='card-value' style='font-size:1.5rem;'>{dom.capitalize()}</div>
            <div class='card-sub'>Most frequent this period</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        scol = '#6bcb77' if sentiment > 0.1 else '#ff6b6b' if sentiment < -0.1 else '#ffd93d'
        st.markdown(f"""<div class='card' style='--accent:{scol};'>
            <div class='card-label'>Avg Sentiment</div>
            <div class='card-value' style='color:{scol};'>{sentiment:+.2f}</div>
            <div class='card-sub'>{metrics.get('sentiment_trend','N/A')}</div>
        </div>""", unsafe_allow_html=True)

    with c4:
        stcol = '#6bcb77' if stability > 70 else '#ffd93d' if stability > 50 else '#ff6b6b'
        st.markdown(f"""<div class='card' style='--accent:{stcol};'>
            <div class='card-label'>Mood Stability</div>
            <div class='card-value' style='color:{stcol};'>{stability:.1f}%</div>
            <div class='card-sub'>Higher = more stable</div>
        </div>""", unsafe_allow_html=True)

    with c5:
        rcol = '#ff6b6b' if burnout == 'High' else '#ffd93d' if burnout == 'Medium' else '#6bcb77'
        st.markdown(f"""<div class='card' style='--accent:{rcol};'>
            <div class='card-label'>Burnout Risk</div>
            <div class='card-value' style='color:{rcol};'>{burnout}</div>
            <div class='card-sub'>Based on last 7 days</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts Row 1 ──
    left, right = st.columns([1, 1])

    with left:
        emotion_counts = Counter([e['primary_emotion'] for e in entries])
        fig = go.Figure(go.Pie(
            labels=[k.capitalize() for k in emotion_counts.keys()],
            values=list(emotion_counts.values()),
            marker=dict(colors=[EMOTION_COLORS.get(k, '#95e1d3') for k in emotion_counts.keys()],
                        line=dict(color='#0f0f1a', width=2)),
            hole=0.52,
            textinfo='label+percent',
            textfont=dict(size=11, color='#e8e8f0'),
        ))
        fig.update_layout(**PLOT_LAYOUT, title=dict(text='Emotion Distribution', font=dict(color='#e8e8f0', size=14)), height=320)
        fig.add_annotation(text=f"<b>{len(entries)}</b><br>entries", x=0.5, y=0.5, showarrow=False,
                           font=dict(size=13, color='#c8c8e0'), align='center')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with right:
        df = pd.DataFrame(entries)
        df['date_only'] = df['date'].dt.date
        sent_by_day = df.groupby('date_only')['sentiment_score'].mean().reset_index()

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=sent_by_day['date_only'], y=sent_by_day['sentiment_score'],
            mode='lines+markers', name='Sentiment',
            line=dict(color='#7c6af7', width=2.5),
            marker=dict(size=7, color='#7c6af7', line=dict(color='#0f0f1a', width=1.5)),
            fill='tozeroy', fillcolor='rgba(124,106,247,0.08)',
        ))
        fig2.add_hline(y=0, line=dict(color='#3a3a60', dash='dot', width=1))
        fig2.update_layout(**PLOT_LAYOUT, title=dict(text='Sentiment Timeline', font=dict(color='#e8e8f0', size=14)),
                           height=320, yaxis_range=[-1.1, 1.1])
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

    # ── Charts Row 2 ──
    l2, r2 = st.columns([1, 1])

    with l2:
        # Emotion intensity bar chart
        df['intensity_rounded'] = df['emotional_intensity'].round(0)
        df['emo_color'] = df['primary_emotion'].map(EMOTION_COLORS)
        fig3 = go.Figure(go.Bar(
            x=df['date_only'], y=df['emotional_intensity'],
            marker=dict(color=df['emo_color'], line=dict(color='#0f0f1a', width=0.5)),
            name='Intensity',
        ))
        fig3.update_layout(**PLOT_LAYOUT, title=dict(text='Emotional Intensity Over Time', font=dict(color='#e8e8f0', size=14)),
                           height=290, bargap=0.25)
        st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})

    with r2:
        # Mood stability line
        stab_data = df.groupby('date_only')['mood_stability'].mean().reset_index()
        fig4 = go.Figure(go.Scatter(
            x=stab_data['date_only'], y=stab_data['mood_stability'],
            mode='lines+markers',
            line=dict(color='#6bcb77', width=2.5),
            marker=dict(size=7, color='#6bcb77', line=dict(color='#0f0f1a', width=1.5)),
            fill='tozeroy', fillcolor='rgba(107,203,119,0.07)',
            name='Stability'
        ))
        fig4.add_hline(y=70, line=dict(color='#ffd93d', dash='dot', width=1),
                       annotation_text='Stable threshold', annotation_font_color='#ffd93d')
        fig4.update_layout(**PLOT_LAYOUT, title=dict(text='Mood Stability Trend', font=dict(color='#e8e8f0', size=14)),
                           height=290, yaxis_range=[0, 110])
        st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})



# ━━━━━━━━━━━━━━━━━━━ VIEW: ADD JOURNAL ENTRY ━━━━━━━━━━━━━━━━━━━
elif view == "Add Journal Entry":
    st.markdown("<div class='section-title'>✍️ Add a New Journal Entry</div>", unsafe_allow_html=True)

    if use_sample:
        st.info("ℹ️ Sample data mode is ON. Disable it in the sidebar to save your own entries.")

    # ── helpers for live analysis ──
    def find_trigger_words(text):
        text_lower = text.lower()
        found = {}
        for emotion, keywords in EMOTION_KEYWORDS.items():
            matched = [kw for kw in keywords if kw in text_lower]
            if matched:
                found[emotion] = matched
        return found

    def sentiment_bar_html(score):
        pct   = int((score + 1) / 2 * 100)
        color = '#6bcb77' if score > 0.1 else '#ff6b6b' if score < -0.1 else '#ffd93d'
        label = 'Positive' if score > 0.1 else 'Negative' if score < -0.1 else 'Neutral'
        return (
            "<div style='margin:0.3rem 0 0.6rem;'>"
            "<div style='display:flex;justify-content:space-between;margin-bottom:4px;'>"
            f"<span style='font-size:0.75rem;color:#7878a0;'>Sentiment</span>"
            f"<span style='font-size:0.75rem;color:{color};font-weight:700;'>{label} ({score:+.2f})</span>"
            "</div>"
            "<div style='background:#12122a;border-radius:20px;height:8px;overflow:hidden;'>"
            f"<div style='width:{pct}%;height:100%;background:{color};border-radius:20px;'></div>"
            "</div></div>"
        )

    def intensity_bar_html(intensity):
        color = '#ff6b6b' if intensity > 72 else '#ffd93d' if intensity > 50 else '#6bcb77'
        return (
            "<div style='margin:0.3rem 0 0.6rem;'>"
            "<div style='display:flex;justify-content:space-between;margin-bottom:4px;'>"
            f"<span style='font-size:0.75rem;color:#7878a0;'>Emotional Intensity</span>"
            f"<span style='font-size:0.75rem;color:{color};font-weight:700;'>{intensity:.1f}%</span>"
            "</div>"
            "<div style='background:#12122a;border-radius:20px;height:8px;overflow:hidden;'>"
            f"<div style='width:{intensity:.0f}%;height:100%;background:{color};border-radius:20px;'></div>"
            "</div></div>"
        )

    # ── Layout: left = input | right = live panel ──
    left_col, right_col = st.columns([3, 2], gap="large")

    with left_col:
        st.markdown(
            "<div style='background:#1c1c32;border:1px solid #2e2e50;border-radius:14px;"
            "padding:1rem 1.2rem;margin-bottom:1rem;'>"
            "<p style='color:#7878a0;font-size:0.82rem;margin:0;line-height:1.6;'>"
            "&#10024; <b style='color:#c8c8e0;'>Live Analysis</b> &mdash; emotions, sentiment &amp; intensity are "
            "detected automatically as you type. The right panel updates instantly."
            "</p></div>",
            unsafe_allow_html=True
        )

        entry_date = st.date_input("📅 Entry Date", value=datetime.today())

        entry_text = st.text_area(
            "📝 What's on your mind?",
            placeholder=(
                "Start writing... e.g. 'I felt really anxious today about my exams. "
                "But after a walk I felt calmer and grateful for small things.'"
            ),
            height=220,
            key="journal_text_input"
        )

        col_a, col_b = st.columns([1, 1])
        with col_a:
            manual_mood = st.select_slider(
                "😶 Self-rated Mood",
                options=['Very Low', 'Low', 'Neutral', 'Good', 'Excellent'],
                value='Neutral'
            )
        with col_b:
            writing_context = st.selectbox(
                "🏷️ Context",
                ['Morning Reflection', 'Evening Check-in', 'Therapy Notes',
                 'Random Thoughts', 'Significant Event']
            )

        btn_col1, btn_col2 = st.columns([1, 1])
        with btn_col1:
            save_btn = st.button("💾 Save Entry", use_container_width=True)
        with btn_col2:
            analyse_btn = st.button("🔍 Analyse Now", use_container_width=True)

        if analyse_btn:
            if not entry_text.strip() or len(entry_text.strip()) < 3:
                st.error("Please write something before analysing.")
            else:
                st.session_state["force_analyse"] = True
                st.session_state["analyse_text"]  = entry_text

    # ── RIGHT PANEL: live prediction ──
    with right_col:
        st.markdown(
            "<div style='font-size:0.72rem;color:#5a5a80;text-transform:uppercase;"
            "letter-spacing:0.12em;margin-bottom:0.8rem;margin-top:0.1rem;'>"
            "⚡ Live Sentiment Analysis</div>",
            unsafe_allow_html=True
        )

        mood_map = {'Very Low': -0.4, 'Low': -0.15, 'Neutral': 0.0, 'Good': 0.15, 'Excellent': 0.4}

        # Use either live text or the text captured at Analyse Now click
        analyse_text = st.session_state.get("analyse_text", "") if st.session_state.get("force_analyse") else ""
        display_text = entry_text if (entry_text and len(entry_text.strip()) >= 3) else analyse_text
        if display_text and len(display_text.strip()) >= 3:
            entry_text_for_analysis = display_text
            live_emos      = detect_emotions(entry_text_for_analysis)
            live_prim      = primary_emotion(live_emos)
            live_sent      = calculate_sentiment(entry_text_for_analysis)
            live_intensity = calculate_intensity(entry_text_for_analysis, live_emos)
            live_triggers  = find_trigger_words(entry_text_for_analysis)
            live_words     = len(entry_text_for_analysis.split())

            live_sent = round(max(-1, min(1, live_sent + mood_map[manual_mood] * 0.3)), 3)

            prim_color    = EMOTION_COLORS.get(live_prim, '#7c6af7')
            burnout_label = 'High' if live_intensity > 72 else 'Medium' if live_intensity > 50 else 'Low'
            risk_color    = '#ff6b6b' if burnout_label == 'High' else '#ffd93d' if burnout_label == 'Medium' else '#6bcb77'

            # Primary emotion card
            st.markdown(
                f"<div class='card' style='--accent:{prim_color};margin-bottom:0.8rem;'>"
                f"<div class='card-label'>Detected Primary Emotion</div>"
                f"<div class='card-value' style='color:{prim_color};font-size:1.8rem;'>{live_prim.capitalize()}</div>"
                f"<div class='card-sub'>{live_words} words &nbsp;&middot;&nbsp; "
                f"Burnout risk: <b style='color:{risk_color};'>{burnout_label}</b></div>"
                "</div>",
                unsafe_allow_html=True
            )

            # Sentiment + intensity bars
            st.markdown(sentiment_bar_html(live_sent), unsafe_allow_html=True)
            st.markdown(intensity_bar_html(live_intensity), unsafe_allow_html=True)

            # All detected emotion pills
            pills_html = " ".join([
                f"<span style='display:inline-block;padding:3px 11px;border-radius:20px;"
                f"font-size:0.75rem;font-weight:600;margin:2px;"
                f"background:{EMOTION_COLORS.get(e, '#7c6af7')}22;"
                f"color:{EMOTION_COLORS.get(e, '#7c6af7')};"
                f"border:1px solid {EMOTION_COLORS.get(e, '#7c6af7')}55;'>"
                f"{e.capitalize()}</span>"
                for e in live_emos
            ])
            st.markdown(
                "<div style='margin:0.5rem 0;'>"
                "<div style='font-size:0.72rem;color:#5a5a80;margin-bottom:5px;'>All emotions detected</div>"
                f"{pills_html}</div>",
                unsafe_allow_html=True
            )

            # Trigger keywords
            if live_triggers:
                st.markdown(
                    "<div style='font-size:0.72rem;color:#5a5a80;margin:0.7rem 0 0.4rem;"
                    "text-transform:uppercase;letter-spacing:0.1em;'>Trigger Keywords Found</div>",
                    unsafe_allow_html=True
                )
                for emo, words in live_triggers.items():
                    ec = EMOTION_COLORS.get(emo, '#7c6af7')
                    chips = " ".join([
                        f"<code style='background:{ec}18;color:{ec};border:1px solid {ec}33;"
                        f"border-radius:5px;padding:1px 7px;font-size:0.72rem;'>{w}</code>"
                        for w in words
                    ])
                    st.markdown(
                        f"<div style='margin-bottom:5px;'>"
                        f"<span style='color:{ec};font-size:0.75rem;font-weight:600;'>{emo.capitalize()}</span>"
                        f" &nbsp;{chips}</div>",
                        unsafe_allow_html=True
                    )

            # Contextual wellness tip
            tips = {
                'overwhelmed': "💡 You seem overwhelmed. Try the 4-7-8 breathing technique right now.",
                'anxious':     "💡 Anxiety detected. Name 5 things you can see — it helps ground you.",
                'sad':         "💡 It's okay to feel sad. Reach out to someone you trust today.",
                'happy':       "💡 Great energy! Capture what made today good — it helps on harder days.",
                'content':     "💡 Contentment is underrated. You're doing well — keep this balance.",
                'neutral':     "💡 A neutral day is still a good day. What's one thing you're grateful for?",
            }
            tip = tips.get(live_prim, '')
            if tip:
                st.markdown(
                    f"<div style='background:#1c1c32;border:1px solid #2e2e50;"
                    f"border-left:3px solid {prim_color};border-radius:10px;"
                    f"padding:0.8rem 1rem;margin-top:0.8rem;"
                    f"font-size:0.82rem;color:#c8c8e0;line-height:1.6;'>{tip}</div>",
                    unsafe_allow_html=True
                )

            # Mini sentiment gauge
            gauge_fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=round((live_sent + 1) / 2 * 100, 1),
                title=dict(text="Sentiment Score", font=dict(color='#c8c8e0', size=11)),
                gauge=dict(
                    axis=dict(range=[0, 100], tickcolor='#3a3a60',
                              tickfont=dict(color='#5a5a80', size=9)),
                    bar=dict(color='#6bcb77' if live_sent > 0.1 else '#ff6b6b' if live_sent < -0.1 else '#ffd93d'),
                    bgcolor='#1c1c32', bordercolor='#2e2e50',
                    steps=[
                        dict(range=[0, 33],  color='#1a0f1a'),
                        dict(range=[33, 66], color='#1a1a20'),
                        dict(range=[66, 100], color='#0f1a0f'),
                    ],
                    threshold=dict(line=dict(color='#7c6af7', width=2), thickness=0.75, value=50),
                ),
                number=dict(font=dict(color='#e8e8f0', size=18), suffix="%"),
            ))
            gauge_fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', font=dict(family='DM Sans'),
                height=180, margin=dict(l=20, r=20, t=30, b=10)
            )
            st.plotly_chart(gauge_fig, use_container_width=True, config={'displayModeBar': False})

        else:
            st.markdown(
                "<div style='background:#1c1c32;border:1px dashed #2e2e50;border-radius:14px;"
                "padding:2.5rem 1.5rem;text-align:center;margin-top:0.5rem;'>"
                "<div style='font-size:2rem;margin-bottom:0.5rem;'>🧠</div>"
                "<div style='color:#5a5a80;font-size:0.85rem;line-height:1.7;'>"
                "Start typing in the journal box<br>and your emotion analysis<br>"
                "will appear here instantly.</div></div>",
                unsafe_allow_html=True
            )

    # ── Save logic ──
    if save_btn:
        if not entry_text.strip():
            st.error("Please write something before saving.")
        elif len(entry_text.strip()) < 10:
            st.error("Entry is too short. Write at least a sentence.")
        else:
            detected_emos = detect_emotions(entry_text)
            prim_emo      = primary_emotion(detected_emos)
            sentiment_val = calculate_sentiment(entry_text)
            intensity_val = calculate_intensity(entry_text, detected_emos)
            mood_map2     = {'Very Low': -0.4, 'Low': -0.15, 'Neutral': 0.0, 'Good': 0.15, 'Excellent': 0.4}
            sentiment_val = round(max(-1, min(1, sentiment_val + mood_map2[manual_mood] * 0.3)), 3)

            new_entry = {
                'date':                pd.Timestamp(entry_date),
                'text':                entry_text.strip(),
                'emotions':            detected_emos,
                'primary_emotion':     prim_emo,
                'sentiment_score':     sentiment_val,
                'emotional_intensity': intensity_val,
                'word_count':          len(entry_text.split()),
                'mood_stability':      round(random.uniform(40, 95), 1),
                'context':             writing_context,
                'manual_mood':         manual_mood,
            }
            st.session_state.journal_entries.append(new_entry)
            st.success(
                f"Entry saved! Primary emotion: **{prim_emo.capitalize()}** "
                f"· Sentiment: **{sentiment_val:+.2f}** · Intensity: **{intensity_val:.1f}%**"
            )
            st.rerun()

# ━━━━━━━━━━━━━━━━━━━ VIEW: TRENDS & PREDICTIONS ━━━━━━━━━━━━━━━━━
elif view == "Trends & Predictions":
    st.markdown("<div class='section-title'>📈 Trends & Predictions</div>", unsafe_allow_html=True)

    df = pd.DataFrame(entries)
    df['date_only'] = df['date'].dt.date
    df['day_num']   = (df['date'] - df['date'].min()).dt.days

    # ── Emotion Transition Heatmap ──
    emotions_ordered = ['happy', 'content', 'neutral', 'anxious', 'sad', 'overwhelmed']
    transition_matrix = pd.DataFrame(0, index=emotions_ordered, columns=emotions_ordered)
    emo_sequence = df['primary_emotion'].tolist()
    for i in range(len(emo_sequence) - 1):
        fr, to = emo_sequence[i], emo_sequence[i+1]
        if fr in transition_matrix.index and to in transition_matrix.columns:
            transition_matrix.loc[fr, to] += 1

    fig_heat = go.Figure(go.Heatmap(
        z=transition_matrix.values,
        x=[e.capitalize() for e in transition_matrix.columns],
        y=[e.capitalize() for e in transition_matrix.index],
        colorscale=[[0, '#0f0f1a'], [0.5, '#3a2a7a'], [1, '#7c6af7']],
        showscale=True,
        text=transition_matrix.values,
        texttemplate='%{text}',
        textfont=dict(color='#e8e8f0', size=11),
    ))
    fig_heat.update_layout(**PLOT_LAYOUT, height=350,
                           title=dict(text='Emotion Transition Matrix (what follows what)', font=dict(color='#e8e8f0', size=14)))
    st.plotly_chart(fig_heat, use_container_width=True, config={'displayModeBar': False})

    # ── Sentiment Regression Forecast ──
    col1, col2 = st.columns([3, 2])
    with col1:
        x = df['day_num'].values
        y = df['sentiment_score'].values
        coeffs = np.polyfit(x, y, 1)
        trend_line = np.poly1d(coeffs)
        future_days = np.arange(x.max() + 1, x.max() + 8)
        future_preds = trend_line(future_days)

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=df['date_only'], y=y,
            mode='markers', name='Actual',
            marker=dict(color='#7c6af7', size=8),
        ))
        all_dates = list(df['date_only']) + [
            (df['date'].max() + timedelta(days=int(d - x.max()))).date() for d in future_days
        ]
        trend_vals = trend_line(np.concatenate([x, future_days]))
        fig_trend.add_trace(go.Scatter(
            x=all_dates, y=trend_vals,
            mode='lines', name='Trend',
            line=dict(color='#6bcb77', width=2, dash='solid'),
        ))
        fig_trend.add_trace(go.Scatter(
            x=[d for d in all_dates if d > df['date_only'].max()],
            y=future_preds,
            mode='lines+markers', name='Forecast',
            line=dict(color='#ffd93d', width=2, dash='dot'),
            marker=dict(size=7, symbol='diamond', color='#ffd93d'),
        ))
        fig_trend.add_hline(y=0, line=dict(color='#3a3a60', dash='dot'))
        fig_trend.update_layout(**PLOT_LAYOUT, height=320,
                                title=dict(text='Sentiment Trend & 7-Day Forecast', font=dict(color='#e8e8f0', size=14)))
        st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})

    with col2:
        slope = coeffs[0]
        direction = "📈 Improving" if slope > 0.005 else "📉 Declining" if slope < -0.005 else "➡️ Stable"
        future_avg = round(float(np.mean(future_preds)), 3)
        st.markdown(f"""
        <div class='card' style='--accent:#ffd93d;margin-top:0;'>
            <div class='card-label'>7-Day Forecast</div>
            <div class='card-value' style='color:#ffd93d;font-size:1.5rem;'>{direction}</div>
            <div class='card-sub'>Predicted avg sentiment: <b style='color:#e8e8f0'>{future_avg:+.2f}</b></div>
        </div>
        <div class='card' style='--accent:#7c6af7;margin-top:0.6rem;'>
            <div class='card-label'>Entries This Week</div>
            <div class='card-value'>{min(7, len(entries))}</div>
            <div class='card-sub'>Consistency is key</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Emotion frequency bar ──
    emo_freq = Counter(df['primary_emotion'].tolist())
    fig_bar = go.Figure(go.Bar(
        x=[e.capitalize() for e in emo_freq.keys()],
        y=list(emo_freq.values()),
        marker=dict(color=[EMOTION_COLORS.get(e, '#7c6af7') for e in emo_freq.keys()],
                    line=dict(color='#0f0f1a', width=1)),
        text=list(emo_freq.values()), textposition='auto',
    ))
    fig_bar.update_layout(**PLOT_LAYOUT, height=260,
                          title=dict(text='Emotion Frequency Breakdown', font=dict(color='#e8e8f0', size=14)))
    st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})


# ━━━━━━━━━━━━━━━━━━━ VIEW: RISK ASSESSMENT ━━━━━━━━━━━━━━━━━━━━━
elif view == "Risk Assessment":
    st.markdown("<div class='section-title'>⚠️ Mental Health Risk Assessment</div>", unsafe_allow_html=True)

    st.warning("⚠️ This assessment is for informational wellness support only. It is NOT a clinical diagnosis. If you are struggling, please contact a mental health professional.")

    burnout      = metrics.get('burnout_risk', 'Low')
    stability    = metrics.get('stability_score', 0)
    sentiment    = metrics.get('avg_sentiment', 0)
    recent_int   = metrics.get('recent_intensity', 0)

    # ── Risk Score Gauges ──
    c1, c2, c3 = st.columns(3)

    def gauge(value, title, max_val=100, thresholds=(50, 75), reverse=False):
        norm = value / max_val
        if reverse:
            color = '#ff6b6b' if norm < thresholds[0]/max_val else '#ffd93d' if norm < thresholds[1]/max_val else '#6bcb77'
        else:
            color = '#6bcb77' if norm < thresholds[0]/max_val else '#ffd93d' if norm < thresholds[1]/max_val else '#ff6b6b'
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            title=dict(text=title, font=dict(color='#c8c8e0', size=12)),
            gauge=dict(
                axis=dict(range=[0, max_val], tickcolor='#3a3a60', tickfont=dict(color='#5a5a80')),
                bar=dict(color=color),
                bgcolor='#1c1c32',
                bordercolor='#2e2e50',
                steps=[
                    dict(range=[0, max_val*0.5], color='#12122a'),
                    dict(range=[max_val*0.5, max_val*0.75], color='#1a1a30'),
                    dict(range=[max_val*0.75, max_val], color='#20203a'),
                ],
            ),
            number=dict(font=dict(color='#e8e8f0', size=24)),
        ))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(family='DM Sans'), height=220,
                          margin=dict(l=20, r=20, t=40, b=10))
        return fig

    with c1:
        st.plotly_chart(gauge(recent_int, "Emotional Intensity (7d)"), use_container_width=True, config={'displayModeBar': False})
    with c2:
        st.plotly_chart(gauge(stability, "Mood Stability", reverse=True), use_container_width=True, config={'displayModeBar': False})
    with c3:
        # Normalize sentiment -1..1 to 0..100
        sent_norm = round((sentiment + 1) / 2 * 100, 1)
        st.plotly_chart(gauge(sent_norm, "Sentiment Health", reverse=True), use_container_width=True, config={'displayModeBar': False})

    # ── Overall Risk Summary ──
    rcol = '#ff6b6b' if burnout == 'High' else '#ffd93d' if burnout == 'Medium' else '#6bcb77'
    recs = {
        'High': [
            "Consider speaking with a mental health professional soon.",
            "Reduce obligations where possible — recovery requires space.",
            "Prioritize sleep, meals, and short mindful breaks.",
            "Reach out to a trusted friend or family member today.",
        ],
        'Medium': [
            "Keep journaling — consistency helps self-awareness.",
            "Monitor intensity over the next week.",
            "Try short daily breathing or meditation exercises.",
            "Maintain boundaries between work and personal time.",
        ],
        'Low': [
            "Great emotional balance! Keep up your journaling habit.",
            "Continue nurturing positive social connections.",
            "Celebrate small wins — they compound over time.",
            "Stay consistent with activities that ground you.",
        ],
    }

    st.markdown(f"""
    <div class='card' style='--accent:{rcol};margin-top:1rem;'>
        <div class='card-label'>Overall Burnout Risk Level</div>
        <div class='card-value' style='color:{rcol};font-size:2.5rem;'>{burnout}</div>
        <div class='card-sub'>Based on emotional intensity, stability, and sentiment analysis</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"<div class='section-title' style='font-size:1.1rem;'>💡 Recommendations for {burnout} Risk</div>", unsafe_allow_html=True)
    for r in recs.get(burnout, []):
        st.markdown(f"<div style='background:#1c1c32;border:1px solid #2e2e50;border-radius:8px;padding:0.7rem 1rem;margin-bottom:0.5rem;color:#c8c8e0;font-size:0.87rem;'>• {r}</div>", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━ VIEW: ENTRY HISTORY ━━━━━━━━━━━━━━━━━━━━━━━
elif view == "Entry History":
    st.markdown("<div class='section-title'>📋 Journal Entry History</div>", unsafe_allow_html=True)

    if not entries:
        st.info("No entries yet. Add a journal entry first!")
    else:
        # Filter controls
        fc1, fc2 = st.columns([2, 1])
        with fc1:
            filter_emo = st.multiselect(
                "Filter by emotion",
                options=[e.capitalize() for e in EMOTION_COLORS.keys()],
                default=[]
            )
        with fc2:
            sort_order = st.selectbox("Sort by", ["Newest First", "Oldest First"])

        filtered = entries.copy()
        if filter_emo:
            filter_lower = [e.lower() for e in filter_emo]
            filtered = [e for e in filtered if e['primary_emotion'] in filter_lower]

        if sort_order == "Newest First":
            filtered = sorted(filtered, key=lambda x: x['date'], reverse=True)
        else:
            filtered = sorted(filtered, key=lambda x: x['date'])

        st.markdown(f"<div style='color:#5a5a80;font-size:0.8rem;margin-bottom:0.8rem;'>Showing {len(filtered)} of {len(entries)} entries</div>", unsafe_allow_html=True)

        for entry in filtered:
            emo       = entry['primary_emotion']
            emo_color = EMOTION_COLORS.get(emo, '#7c6af7')
            date_str  = entry['date'].strftime('%A, %b %d %Y') if hasattr(entry['date'], 'strftime') else str(entry['date'])
            sent      = entry['sentiment_score']
            sent_str  = f"+{sent:.2f}" if sent > 0 else f"{sent:.2f}"
            all_emos  = entry.get('emotions', [emo])
            def make_pill(e):
                c = EMOTION_COLORS.get(e, '#7c6af7')
                return (f"<span class='emotion-pill' style='"
                        f"background:{c}22;color:{c};"
                        f"border:1px solid {c}44;'>"
                        f"{e.capitalize()}</span>")
            pills = ''.join([make_pill(e) for e in all_emos])
            text_preview = entry['text'][:220] + ('…' if len(entry['text']) > 220 else '')

            st.markdown(f"""
            <div class='journal-card'>
                <div class='journal-date'>{date_str} &nbsp;·&nbsp; {entry.get('word_count', len(entry['text'].split()))} words &nbsp;·&nbsp; Sentiment: <b style='color:#e8e8f0;'>{sent_str}</b> &nbsp;·&nbsp; Intensity: <b style='color:#e8e8f0;'>{entry['emotional_intensity']:.0f}%</b></div>
                <div class='journal-text'>{text_preview}</div>
                <div>{pills}</div>
            </div>
            """, unsafe_allow_html=True)


# ── FOOTER ──
st.markdown("""
<div style='text-align:center;color:#3a3a60;font-size:0.75rem;margin-top:3rem;padding-top:1rem;border-top:1px solid #1e1e35;'>
    MindTrace – Emotion Analytics Dashboard &nbsp;|&nbsp; Built with Streamlit & Plotly &nbsp;|&nbsp; 
    <span style='color:#ff6b6b;'>Not a substitute for professional mental health care.</span>
</div>
""", unsafe_allow_html=True)
