
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
   page_title="Emotion Analytics Dashboard",
   page_icon="🧠",
   layout="wide",
   initial_sidebar_state="expanded"
)

st.markdown("""
   <style>
   @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&family=Playfair+Display:wght@700&display=swap');
   
   * {
       font-family: 'Poppins', sans-serif;
   }
   
   h1, h2, h3 {
       font-family: 'Playfair Display', serif;
       color: #1a1a2e;
   }
   
   .main {
       background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
       padding: 2rem;
   }
   
   .metric-card {
       background: white;
       padding: 1.5rem;
       border-radius: 12px;
       box-shadow: 0 4px 15px rgba(0,0,0,0.08);
       border-left: 4px solid #6366f1;
   }
   
   .metric-value {
       font-size: 2rem;
       font-weight: 700;
       color: #6366f1;
       margin: 0.5rem 0;
   }
   
   .metric-label {
       font-size: 0.9rem;
       color: #666;
       text-transform: uppercase;
       letter-spacing: 0.5px;
   }
   
   .chart-container {
       background: white;
       border-radius: 12px;
       padding: 1.5rem;
       box-shadow: 0 4px 15px rgba(0,0,0,0.08);
       margin: 1rem 0;
   }
   </style>
""", unsafe_allow_html=True)

if 'journal_entries' not in st.session_state:
   st.session_state.journal_entries = []

def load_sample_data():
   dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
   emotions_list = ['happy', 'anxious', 'sad', 'neutral', 'overwhelmed']
   
   entries = []
   for i, date in enumerate(dates):
       entry = {
           'date': date,
           'text': f"Journal entry {i+1}. Today was a {'great' if i % 3 == 0 else 'challenging'} day.",
           'primary_emotion': np.random.choice(emotions_list),
           'emotions': np.random.choice(emotions_list, size=np.random.randint(1, 4), replace=False).tolist(),
           'sentiment_score': np.random.uniform(-1, 1),
           'mood_stability': np.random.uniform(0, 100),
           'word_count': np.random.randint(50, 500),
           'emotional_intensity': np.random.uniform(0, 100),
       }
       entries.append(entry)
   return entries

def calculate_mental_health_metrics(entries):
   if not entries:
       return {}
   
   emotions = [e['primary_emotion'] for e in entries]
   sentiment_scores = [e['sentiment_score'] for e in entries]
   mood_stability = [e['mood_stability'] for e in entries]
   emotional_intensity = [e['emotional_intensity'] for e in entries]
   
   metrics = {
       'total_entries': len(entries),
       'dominant_emotion': Counter(emotions).most_common(1)[0][0] if emotions else 'N/A',
       'avg_sentiment': np.mean(sentiment_scores),
       'sentiment_trend': 'Improving' if sentiment_scores[-1] > sentiment_scores[0] else 'Declining',
       'stability_score': np.mean(mood_stability),
       'avg_intensity': np.mean(emotional_intensity),
       'recent_intensity': np.mean(emotional_intensity[-7:]) if len(emotional_intensity) >= 7 else np.mean(emotional_intensity),
       'burnout_risk': 'High' if np.mean(emotional_intensity[-7:]) > 75 else 'Medium' if np.mean(emotional_intensity[-7:]) > 50 else 'Low',
   }
   return metrics

def get_emotion_color(emotion):
   colors = {
       'happy': '#ffd93d',
       'anxious': '#ff6b6b',
       'sad': '#4d96ff',
       'neutral': '#95e1d3',
       'overwhelmed': '#a8d8ff'
   }
   return colors.get(emotion, '#95e1d3')

st.markdown("<h1 style='text-align: center; margin-bottom: 3rem;'>🧠 Emotion Analytics Dashboard</h1>", unsafe_allow_html=True)

with st.sidebar:
   st.markdown("### 📊 Dashboard Controls")
   
   view_option = st.radio(
       "Select View",
       ["Overview", "Detailed Analysis", "Trends & Predictions", "Risk Assessment"],
       label_visibility="collapsed"
   )
   
   st.markdown("---")
   
   use_sample = st.checkbox("Use Sample Data", value=True)
   
   if st.button("🔄 Refresh Data", use_container_width=True):
       st.session_state.journal_entries = load_sample_data()
       st.rerun()
   
   st.markdown("---")
   st.markdown("### ⚠️ Safety Notice")
   st.info(
       "This dashboard is a support tool, not a substitute for professional mental health care. "
       "Please consult a therapist for proper diagnosis and treatment."
   )

if use_sample or not st.session_state.journal_entries:
   entries = load_sample_data()
else:
   entries = st.session_state.journal_entries

metrics = calculate_mental_health_metrics(entries)

if view_option == "Overview":
   col1, col2, col3, col4 = st.columns(4)
   
   with col1:
       st.markdown(f"""
       <div class='metric-card'>
           <div class='metric-label'>Total Journal Entries</div>
           <div class='metric-value'>{metrics.get('total_entries', 0)}</div>
       </div>
       """, unsafe_allow_html=True)
   
   with col2:
       stability = metrics.get('stability_score', 0)
       color = '#388e3c' if stability > 70 else '#f57c00' if stability > 50 else '#d32f2f'
       st.markdown(f"""
       <div class='metric-card'>
           <div class='metric-label'>Mood Stability</div>
           <div class='metric-value' style='color: {color};'>{stability:.1f}%</div>
       </div>
       """, unsafe_allow_html=True)
   
   with col3:
       sentiment = metrics.get('avg_sentiment', 0)
       st.markdown(f"""
       <div class='metric-card'>
           <div class='metric-label'>Average Sentiment</div>
           <div class='metric-value'>{sentiment:.2f}</div>
       </div>
       """, unsafe_allow_html=True)
   
   with col4:
       burnout = metrics.get('burnout_risk', 'Low')
       risk_color = '#d32f2f' if burnout == 'High' else '#f57c00' if burnout == 'Medium' else '#388e3c'
       st.markdown(f"""
       <div class='metric-card'>
           <div class='metric-label'>Burnout Risk</div>
           <div class='metric-value' style='color: {risk_color};'>{burnout}</div>
       </div>
       """, unsafe_allow_html=True)
   
   st.markdown("---")
   
   col1, col2 = st.columns([1, 1])
   
   with col1:
       st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
       emotion_counts = Counter([e['primary_emotion'] for e in entries])
       fig = go.Figure(data=[go.Pie(
           labels=list(emotion_counts.keys()),
           values=list(emotion_counts.values()),
           marker=dict(colors=[get_emotion_color(e) for e in emotion_counts.keys()]),
           hole=0.4
       )])
       fig.update_layout(
           title="Emotion Distribution",
           height=350,
           margin=dict(l=0, r=0, t=30, b=0),
           showlegend=True
       )
       st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
       st.markdown("</div>", unsafe_allow_html=True)
   
   with col2:
       st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
       df_entries = pd.DataFrame(entries)
       sentiment_data = df_entries.groupby(df_entries['date'].dt.date)['sentiment_score'].mean()
       
       fig = go.Figure(data=[go.Scatter(
           x=sentiment_data.index,
           y=sentiment_data.values,
           mode='lines+markers',
           fill='tozeroy',
           line=dict(color='#6366f1', width=3),
           marker=dict(size=8, color='#6366f1'),
           fillcolor='rgba(99, 102, 241, 0.1)',
           name='Sentiment Score'
       )])
       fig.update_layout(
           title="Sentiment Timeline",
           height=350,
           xaxis_title="Date",
           yaxis_title="Sentiment Score",
           margin=dict(l=40, r=20, t=30, b=40),
           hovermode='x unified'
       )
       st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
       st.markdown("</div>", unsafe_allow_html=True)

elif view_option == "Risk Assessment":
   st.markdown("### ⚠️ Mental Health Risk Assessment")
   
   col1, col2, col3 = st.columns(3)
   
   recent_intensity = metrics.get('recent_intensity', 0)
   stability = metrics.get('stability_score', 0)
   sentiment = metrics.get('avg_sentiment', 0)
   
   with col1:
       risk_color = '#d32f2f' if recent_intensity > 75 else '#f57c00'
       risk_level = 'High' if recent_intensity > 75 else 'Medium'
       st.markdown(f"""
       <div class='metric-card' style='border-left-color: {risk_color};'>
           <div class='metric-label'>Burnout Risk</div>
           <div class='metric-value' style='color: {risk_color};'>{risk_level}</div>
       </div>
       """, unsafe_allow_html=True)
   
   with col2:
       stability_color = '#388e3c' if stability > 70 else '#f57c00'
       st.markdown(f"""
       <div class='metric-card' style='border-left-color: {stability_color};'>
           <div class='metric-label'>Stability Index</div>
           <div class='metric-value' style='color: {stability_color};'>{stability:.1f}%</div>
       </div>
       """, unsafe_allow_html=True)
   
   with col3:
       sentiment_color = '#d32f2f' if sentiment < -0.3 else '#f57c00'
       st.markdown(f"""
       <div class='metric-card' style='border-left-color: {sentiment_color};'>
           <div class='metric-label'>Mood Status</div>
           <div class='metric-value' style='color: {sentiment_color};'>{sentiment:.2f}</div>
       </div>
       """, unsafe_allow_html=True)
   
   st.warning(
       "⚠️ **Important**: This assessment is for informational purposes only. "
       "If you need help, please contact a mental health professional or crisis line."
   )

st.markdown("---")
st.markdown(
   """
   <div style='text-align: center; color: #666; margin-top: 2rem;'>
       <p>© 2024 Emotion Analytics Dashboard | Built with Streamlit & Plotly</p>
   </div>
   """,
   unsafe_allow_html=True
)
