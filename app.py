import streamlit as st
import time
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# This tells Streamlit to look into the "Secrets" you just saved
GSHEETS_URL = st.secrets["GSHEETS_URL"]

# --- 1. CONFIG & STYLING (Material 3 / Google Stitch Vibe) ---
st.set_page_config(page_title="StitchStretch", page_icon="🧘", layout="centered")

# Replace this with your Google Sheet URL (Ensure it is shared as "Anyone with link can edit")
GSHEETS_URL = "https://docs.google.com/spreadsheets/d/1I9aVaXoQ64gV4iJuHVe4NM9hihHlr27V6ycdGHXPL1s/edit?usp=sharing"

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Google Sans', sans-serif; }
    .main { background-color: #F8F9FA; }
    .stButton>button { 
        border-radius: 24px; height: 60px; width: 100%; 
        background-color: #D3E3FD; color: #041E49; border: none;
        font-weight: 500; font-size: 18px; margin-bottom: 10px;
    }
    .stButton>button:hover { background-color: #A8C7FA; }
    .timer-card { 
        background: white; border-radius: 32px; padding: 30px; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.05); text-align: center;
        border: 1px solid #E0E0E0;
    }
    .timer-display { font-size: 90px; font-weight: 400; color: #1B1B1F; margin: 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA & PERSISTENCE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'pose_duration' not in st.session_state: st.session_state.pose_duration = 30

ROUTINES = {
    "Morning ☀️": [
        {"name": "Child's Pose", "img": "https://yoga-api-nzy4.onrender.com/images/childs_pose.png"},
        {"name": "Cat-Cow", "img": "https://yoga-api-nzy4.onrender.com/images/cat_cow.png"},
        {"name": "Downward Dog", "img": "https://yoga-api-nzy4.onrender.com/images/downward_dog.png"},
        {"name": "Cobra", "img": "https://yoga-api-nzy4.onrender.com/images/cobra.png"},
        {"name": "Low Lunge (R)", "img": "https://yoga-api-nzy4.onrender.com/images/low_lunge.png"},
        {"name": "Low Lunge (L)", "img": "https://yoga-api-nzy4.onrender.com/images/low_lunge.png"},
        {"name": "Warrior II (R)", "img": "https://yoga-api-nzy4.onrender.com/images/warrior_ii.png"},
        {"name": "Warrior II (L)", "img": "https://yoga-api-nzy4.onrender.com/images/warrior_ii.png"},
        {"name": "Forward Fold", "img": "https://yoga-api-nzy4.onrender.com/images/forward_fold.png"},
        {"name": "Mountain Pose", "img": "https://yoga-api-nzy4.onrender.com/images/mountain_pose.png"}
    ],
    "Before Sleep 🌙": [
        {"name": "Neck Rolls", "img": "https://yoga-api-nzy4.onrender.com/images/neck_rolls.png"},
        {"name": "Seated Forward Fold", "img": "https://yoga-api-nzy4.onrender.com/images/seated_forward_fold.png"},
        {"name": "Thread the Needle", "img": "https://yoga-api-nzy4.onrender.com/images/thread_the_needle.png"},
        {"name": "Pigeon (R)", "img": "https://yoga-api-nzy4.onrender.com/images/pigeon.png"},
        {"name": "Pigeon (L)", "img": "https://yoga-api-nzy4.onrender.com/images/pigeon.png"},
        {"name": "Puppy Pose", "img": "https://yoga-api-nzy4.onrender.com/images/puppy_pose.png"},
        {"name": "Happy Baby", "img": "https://yoga-api-nzy4.onrender.com/images/happy_baby.png"},
        {"name": "Supine Twist (R)", "img": "https://yoga-api-nzy4.onrender.com/images/supine_twist.png"},
        {"name": "Supine Twist (L)", "img": "https://yoga-api-nzy4.onrender.com/images/supine_twist.png"},
        {"name": "Butterfly Pose", "img": "https://yoga-api-nzy4.onrender.com/images/bound_angle.png"}
    ]
}

def log_to_sheets(routine_name):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        existing_data = conn.read(spreadsheet=GSHEETS_URL)
        new_entry = pd.DataFrame([{"Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Routine": routine_name}])
        updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
        conn.update(spreadsheet=GSHEETS_URL, data=updated_df)
        st.toast("Saved to Exercise Log! 📋")
    except Exception as e:
        st.error("Sheet Connection Error. Check your URL.")

def play_audio(url):
    st.components.v1.html(f'<audio autoplay><source src="{url}" type="audio/mp3"></audio>', height=0)

# --- 3. UI SCREENS ---
def run_routine(name):
    poses = ROUTINES[name]
    progress = st.progress(0)
    status = st.empty()
    img_box = st.empty()
    timer_box = st.empty()
    
    for i, pose in enumerate(poses):
        progress.progress((i + 1) / len(poses))
        status.markdown(f"<h3 style='text-align:center;'>{pose['name']}</h3>", unsafe_allow_html=True)
        img_box.image(pose['img'], use_container_width=True)
        
        for t in range(st.session_state.pose_duration, -1, -1):
            timer_box.markdown(f"<div class='timer-card'><div class='timer-display'>{t}s</div></div>", unsafe_allow_html=True)
            if t == 3: play_audio("https://www.soundjay.com/buttons/beep-07.mp3")
            if t == 0: play_audio("https://indiemusicbox.s3.amazonaws.com/downloads/meditation-bell-pack/Meditation+Bell+1.mp3")
            time.sleep(1)
            
    st.balloons()
    log_to_sheets(name)
    if st.button("Finish & Return Home"): st.rerun()

# --- 4. MAIN APP ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center;'>🧘 StitchStretch</h1>", unsafe_allow_html=True)
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "admin" and pw == "stretch2026":
            st.session_state.logged_in = True
            st.rerun()
else:
    tab1, tab2, tab3 = st.tabs(["Start Routine", "Custom Settings", "View Log"])
    
    with tab1:
        c1, c2 = st.columns(2)
        if c1.button("☀️ Morning"): run_routine("Morning ☀️")
        if c2.button("🌙 Sleep"): run_routine("Before Sleep 🌙")

    with tab2:
        st.session_state.pose_duration = st.slider("Pose Timer (Seconds)", 15, 60, st.session_state.pose_duration, 5)
        st.info("Your custom timer is saved for this session.")

    with tab3:
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            df = conn.read(spreadsheet=GSHEETS_URL)
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)
        except:
            st.write("Connect your Google Sheet to see the log here.")