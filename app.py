import streamlit as st
import calendar
from datetime import datetime, date
import json
from collections import defaultdict
import requests
import os

# Page config
st.set_page_config(page_title="Habit Tracker", page_icon="📅", layout="wide")

# GitHub Gists configuration (read from Streamlit Secrets or environment)
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", os.getenv("GITHUB_TOKEN", ""))
GIST_ID = st.secrets.get("GIST_ID", os.getenv("GIST_ID", ""))

def load_from_gist():
    """Load data from GitHub Gist"""
    if not GIST_ID or not GITHUB_TOKEN:
        return None
    
    try:
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        response = requests.get(f"https://api.github.com/gists/{GIST_ID}", headers=headers)
        
        if response.status_code == 200:
            gist_data = response.json()
            content = gist_data['files']['habit_data.json']['content']
            return json.loads(content)
        else:
            st.error(f"Failed to load from Gist: {response.status_code}")
    except Exception as e:
        st.error(f"Error loading from Gist: {e}")
    
    return None

def save_to_gist(data):
    """Save data to GitHub Gist"""
    if not GIST_ID or not GITHUB_TOKEN:
        return False
    
    try:
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        payload = {
            "files": {
                "habit_data.json": {"content": json.dumps(data, indent=2)}
            }
        }
        
        response = requests.patch(f"https://api.github.com/gists/{GIST_ID}", 
                               json=payload, headers=headers)
        
        if response.status_code == 200:
            return True
        else:
            st.error(f"Failed to save to Gist: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Error saving to Gist: {e}")
        return False

# Load data from GitHub Gist
def load_data():
    # Try to load from GitHub Gist
    gist_data = load_from_gist()
    if gist_data:
        return gist_data
    
    # Fallback to default data if Gist is not available
    return get_default_data()

# Save data to GitHub Gist (automatic)
def save_data(data):
    # Store in session state
    st.session_state.habits = data
    
    # Try to save automatically to GitHub Gist
    if save_to_gist(data):
        st.session_state.last_save_status = "✅ Auto-saved to GitHub Gist"
    else:
        # Fallback: generate JSON for manual copying if API fails
        st.session_state.last_save_json = json.dumps(data, indent=2)
        st.session_state.last_save_status = "⚠️ Manual save required - GitHub Gist not available"

# Default data structure
def get_default_data():
    return {
        'Tennis': {'color': '#FF6B6B', 'count': {}},
        'DSA Solving': {'color': '#4ECDC4', 'count': {}},
        'Finance Learning': {'color': '#FFE66D', 'count': {}},
        'notes': {}
    }

# Calculate streak for a habit
from datetime import timedelta

def calculate_streak(habit_data, end_date):
    dates = sorted([datetime.strptime(d, "%Y-%m-%d").date() for d in habit_data['count'].keys()], reverse=True)
    if not dates:
        return 0
    
    streak = 0
    current = end_date
    
    for d in dates:
        if d == current:
            streak += 1
            current = date(current.year, current.month, current.day - 1) if current.day > 1 else date(current.year, current.month - 1 if current.month > 1 else 12, calendar.monthrange(current.year, current.month - 1 if current.month > 1 else 12)[1])
        elif d < current:
            break
    
    return streak

# Initialize session state
if 'habits' not in st.session_state:
    st.session_state.habits = load_data()
    # Ensure notes key exists for backward compatibility
    if 'notes' not in st.session_state.habits:
        st.session_state.habits['notes'] = {}

if 'current_month' not in st.session_state:
    st.session_state.current_month = datetime.now().month

if 'current_year' not in st.session_state:
    st.session_state.current_year = datetime.now().year

if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'calendar'

if 'last_save_json' not in st.session_state:
    st.session_state.last_save_json = ""

if 'last_save_status' not in st.session_state:
    st.session_state.last_save_status = ""

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background-color: #0a0a0a;
    }

    .postit-fade {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 120px;
        background: linear-gradient(to bottom, rgba(245,200,87,0), rgba(245,200,87,1));
        border-radius: 0 0 10px 10px;
        pointer-events: none;
    }

    
    .day-cell {
        border: 1px solid #333;
        padding: 4px 8px 10px 8px;
        min-height: 80px;
        min-width: 80px;
        background: #1a1a1a;
        border-radius: 5px;
        position: relative;
        margin-top: 8px;
    }
    
    .day-number {
        font-weight: bold;
        margin-bottom: 3px;
        color: #ffffff;
        font-size: 20px;
    }
    
    .empty-cell {
        background: #0a0a0a;
        border: 1px solid #222;
    }
    
    .dots-container {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-top: 3px;
    }
    
    .dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        display: inline-block;
    }
    
    .stat-card {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: white;
        font-weight: bold;
        background: #1a1a1a;
        border: 2px solid;
    }
    
    .header-day {
        text-align: center;
        font-weight: bold;
        padding: 10px;
        background: #1a1a1a;
        border-radius: 5px;
        color: #888;
        font-size: 12px;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1a1a;
        color: #888;
        border-radius: 5px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #2a2a2a;
        color: white;
    }
    
    h1, h2, h3 {
        color: white !important;
    }
    
    .stSelectbox label, .stNumberInput label, .stTextInput label, .stColorPicker label {
        color: #888 !important;
    }
    
    div[data-testid="stSidebarContent"] {
        background-color: #0f0f0f;
    }
    
    .stTextArea textarea {
        background-color: #0a0a0a !important;
        color: #e0e0e0 !important;
        border: 1px solid #333 !important;
        font-family: 'Futura', sans-serif !important;
        font-size: 20px !important;
        line-height: 1.6 !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #555 !important;
    }
    
    .save-notice {
        background: #1a3a1a;
        border: 1px solid #2a5a2a;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
        color: #88ff88;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("📅 Habit Tracker")

# Sidebar for controls
with st.sidebar:
    st.header("Controls")
    
    # Month navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("◀", use_container_width=True):
            if st.session_state.current_month == 1:
                st.session_state.current_month = 12
                st.session_state.current_year -= 1
            else:
                st.session_state.current_month -= 1
            st.rerun()
    
    with col2:
        st.markdown(f"<div style='text-align: center; padding: 8px; color: white;'>{calendar.month_name[st.session_state.current_month]} {st.session_state.current_year}</div>", unsafe_allow_html=True)
    
    with col3:
        if st.button("▶", use_container_width=True):
            if st.session_state.current_month == 12:
                st.session_state.current_month = 1
                st.session_state.current_year += 1
            else:
                st.session_state.current_month += 1
            st.rerun()
    
    st.divider()
    
    # Add habit section
    st.subheader("Add Habit Activity")
    current_date = datetime.now()
    selected_day = st.number_input("Day", min_value=1, max_value=31, value=current_date.day if st.session_state.current_month == current_date.month else 1)
    selected_habit = st.selectbox("Habit", [k for k in st.session_state.habits.keys() if k != 'notes'])
    
    if st.button("➕ Add Activity", use_container_width=True):
        date_key = f"{st.session_state.current_year}-{st.session_state.current_month:02d}-{selected_day:02d}"
        if date_key not in st.session_state.habits[selected_habit]['count']:
            st.session_state.habits[selected_habit]['count'][date_key] = 0
        st.session_state.habits[selected_habit]['count'][date_key] += 1
        save_data(st.session_state.habits)
        st.success(f"Added {selected_habit}!")
        st.rerun()
    
    st.divider()
    
    # Remove habit section
    st.subheader("Remove Activity")
    remove_day = st.number_input("Day to remove from", min_value=1, max_value=31, value=current_date.day if st.session_state.current_month == current_date.month else 1, key="remove_day")
    remove_habit = st.selectbox("Habit to remove", [k for k in st.session_state.habits.keys() if k != 'notes'], key="remove_habit")
    
    if st.button("➖ Remove One", use_container_width=True):
        date_key = f"{st.session_state.current_year}-{st.session_state.current_month:02d}-{remove_day:02d}"
        if date_key in st.session_state.habits[remove_habit]['count']:
            if st.session_state.habits[remove_habit]['count'][date_key] > 1:
                st.session_state.habits[remove_habit]['count'][date_key] -= 1
            else:
                del st.session_state.habits[remove_habit]['count'][date_key]
            save_data(st.session_state.habits)
            st.success(f"Removed one {remove_habit}!")
            st.rerun()
        else:
            st.warning("No activity on that day!")
    
    st.divider()
    
    # Manage Habits section
    st.subheader("Manage Habits")
    
    with st.expander("➕ Add New Habit"):
        new_habit_name = st.text_input("Habit Name")
        new_habit_color = st.color_picker("Color", "#9B59B6")
        if st.button("Create Habit", use_container_width=True):
            if new_habit_name and new_habit_name not in st.session_state.habits and new_habit_name != 'notes':
                st.session_state.habits[new_habit_name] = {'color': new_habit_color, 'count': {}}
                save_data(st.session_state.habits)
                st.success(f"Added {new_habit_name}!")
                st.rerun()
            elif new_habit_name in st.session_state.habits:
                st.error("Habit already exists!")
            else:
                st.error("Please enter a habit name!")
    
    with st.expander("🎨 Edit Habit Colors"):
        for habit_name in [k for k in st.session_state.habits.keys() if k != 'notes']:
            col1, col2 = st.columns([3, 1])
            with col1:
                new_color = st.color_picker(f"{habit_name}", st.session_state.habits[habit_name]['color'], key=f"color_{habit_name}")
            with col2:
                if st.button("💾", key=f"save_{habit_name}"):
                    st.session_state.habits[habit_name]['color'] = new_color
                    save_data(st.session_state.habits)
                    st.rerun()
    
    with st.expander("🗑️ Delete Habit"):
        delete_habit = st.selectbox("Select habit to delete", [k for k in st.session_state.habits.keys() if k != 'notes'], key="delete_select")
        if st.button("Delete", use_container_width=True, type="primary"):
            del st.session_state.habits[delete_habit]
            save_data(st.session_state.habits)
            st.success(f"Deleted {delete_habit}!")
            st.rerun()
    
    st.divider()
    
    # Data management
    st.subheader("📦 Data Management")
    
    # GitHub Gists sync
    with st.expander("☁️ GitHub Gists Sync"):
        # Check if credentials are available
        gist_available = GIST_ID and GITHUB_TOKEN
        
        if gist_available:
            st.success("🔑 GitHub Gist credentials found - Auto-sync enabled!")
            st.markdown(f"**Gist ID:** `{GIST_ID}`")
            
            if st.button("🔄 Load from Gist", use_container_width=True):
                loaded_data = load_data()
                st.session_state.habits = loaded_data
                st.success("Loaded from GitHub Gist!")
                st.rerun()
            
            if st.button("💾 Save to Gist", use_container_width=True):
                save_data(st.session_state.habits)
                st.rerun()
            
            # Show last save status
            if st.session_state.last_save_status:
                if "✅" in st.session_state.last_save_status:
                    st.success(st.session_state.last_save_status)
                else:
                    st.warning(st.session_state.last_save_status)
        else:
            st.warning("⚠️ GitHub Gist credentials not found")
            st.markdown("**To enable automatic sync:**")
            st.markdown("""
            1. Create a GitHub Personal Access Token:
               - Go to GitHub → Settings → Developer settings
               - Personal access tokens → Tokens (classic)
               - Generate new token → Check "gist" permission
               - Copy the token
            
            2. Create a GitHub Gist:
               - Go to gist.github.com
               - Create new gist with filename "habit_data.json"
               - Add content: `{}`
               - Copy the Gist ID from URL
            
            3. Add to Streamlit secrets:
               - `GITHUB_TOKEN`: your token
               - `GIST_ID`: your gist id
            """)
        
        # Fallback manual instructions (only show if Gist failed)
        if st.session_state.last_save_json and not gist_available:
            st.markdown("**Manual Save Instructions:**")
            st.code(st.session_state.last_save_json, language="json")
            st.info("Copy the JSON above and manually update your GitHub Gist")
    
    st.divider()
    
    data_json = json.dumps(st.session_state.habits, indent=2)
    st.download_button(
        label="💾 Download Backup",
        data=data_json,
        file_name="habit_tracker_backup.json",
        mime="application/json",
        use_container_width=True
    )
    
    uploaded_file = st.file_uploader("📁 Upload Backup", type=['json'])
    if uploaded_file is not None:
        try:
            uploaded_data = json.load(uploaded_file)
            st.session_state.habits = uploaded_data
            save_data(st.session_state.habits)
            st.success("Data restored successfully!")
            st.rerun()
        except:
            st.error("Invalid backup file!")

# Tabs for different views
tab1, tab2 = st.tabs(["📅 Calendar", "📊 Dashboard"])

with tab1:
    # Calculate monthly totals and streaks
    monthly_totals = {}
    today = date.today()
    
    for habit_name, habit_data in st.session_state.habits.items():
        if habit_name == 'notes':
            continue
        total = 0
        for date_key, count in habit_data['count'].items():
            if date_key.startswith(f"{st.session_state.current_year}-{st.session_state.current_month:02d}"):
                total += count
        monthly_totals[habit_name] = total
    
    # Display monthly stats at top
    st.subheader(f"📊 {calendar.month_name[st.session_state.current_month]} {st.session_state.current_year} Summary")
    cols = st.columns(len(monthly_totals))
    for idx, (habit_name, total) in enumerate(monthly_totals.items()):
        habit_data = st.session_state.habits[habit_name]
        streak = calculate_streak(habit_data, today)
        with cols[idx]:
            st.markdown(f"""
            <div class="stat-card" style="border-color: {habit_data['color']};">
                <div style="font-size: 28px; margin-bottom: 5px;">{total}</div>
                <div style="font-size: 16px; margin-bottom: 8px;">{habit_name}</div>
                <div style="font-size: 14px; color: #888;">🔥 {streak} day streak</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # Calendar view
    st.subheader(f"📅 {calendar.month_name[st.session_state.current_month]} {st.session_state.current_year}")
    
    # Get calendar data
    cal = calendar.monthcalendar(st.session_state.current_year, st.session_state.current_month)
    
    # Day headers
    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    header_cols = st.columns(7)
    for idx, day_name in enumerate(day_names):
        with header_cols[idx]:
            st.markdown(f'<div class="header-day">{day_name}</div>', unsafe_allow_html=True)
    
    # Calendar grid
    for week in cal:
        cols = st.columns(7)
        for idx, day in enumerate(week):
            with cols[idx]:
                if day == 0:
                    st.markdown('<div class="day-cell empty-cell"></div>', unsafe_allow_html=True)
                else:
                    date_key = f"{st.session_state.current_year}-{st.session_state.current_month:02d}-{day:02d}"
                    
                    # Collect all dots for this day
                    dots_html = ""
                    for habit_name, habit_data in st.session_state.habits.items():
                        if habit_name == 'notes':
                            continue
                        if date_key in habit_data['count']:
                            count = habit_data['count'][date_key]
                            for _ in range(count):
                                dots_html += f'<span class="dot" style="background: {habit_data["color"]};"></span>'
                    
                    st.markdown(f"""
                    <div class="day-cell">
                        <div class="day-number">{day}</div>
                        <div class="dots-container">{dots_html}</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    st.divider()
    
st.divider()
st.subheader("📝 Journal Entries")

# Ensure notes are stored as a list
if not isinstance(st.session_state.habits.get("notes", {}), list):
    old_notes = st.session_state.habits.get("notes", {})
    converted = []
    for yr, txt in old_notes.items():
        converted.append({
            "date": f"{yr}-01-01",
            "text": txt
        })
    st.session_state.habits["notes"] = converted
    save_data(st.session_state.habits)

with st.form("add_journal_entry"):
    colA, colB = st.columns([2,1])

    with colA:
        new_text = st.text_area(
            "Write your note...",
            placeholder="Your thoughts, reflections, ideas..."
        )

    with colB:
        chosen_date = st.date_input("Select Date")

    submitted = st.form_submit_button("Add Entry")

    if submitted and new_text.strip():
        st.session_state.habits["notes"].append({
            "date": chosen_date.strftime("%Y-%m-%d"),   # store sortable format
            "text": new_text.strip()
        })
        save_data(st.session_state.habits)
        st.success("Journal entry added!")
        st.rerun()

notes = st.session_state.habits["notes"]
notes = sorted(
    notes,
    key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"),
    reverse=True
)

postit_style = """
    background-color: #F5C857;
    padding: 16px;
    border-radius: 10px;
    box-shadow: 0px 6px 16px rgba(0,0,0,0.4);
    margin: 10px;
    font-family: 'Helvetica Neue', sans-serif;
    color: #222222;
    height: 320px;
    position: relative;
    overflow: hidden;
"""

date_style = """
    font-size: 18px;
    font-weight: 700;
    color: #222222;
    margin-bottom: 8px;
"""


text_style = """
    font-size: 17px;
    line-height: 1.5;
    margin-bottom: -20px;
"""

st.markdown("### 📌 Your Notes")

# Render 5 cards per row
for i in range(0, len(notes), 5):
    row = notes[i:i+5]
    cols = st.columns(5)

    for idx, entry in enumerate(row):
        with cols[idx]:
            import html

            formatted_date = datetime.strptime(entry["date"], "%Y-%m-%d").strftime("%d %b %Y")
            
            text = entry["text"]
            text = text.replace("\r\n", "\n").replace("\r", "\n")
            safe_text = html.escape(text).replace("\n", "<br>")
            
            # --- show card first ---
            st.markdown(
                f"""
                <div style="{postit_style}; cursor:pointer;">
                    <div style="{date_style}">{formatted_date}</div>
                    <div style="{text_style}">{safe_text}</div>
                    <div class="postit-fade"></div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # --- popover trigger appears below ---
            with st.popover("", use_container_width=True):
                st.markdown(f"### {formatted_date}")
                st.markdown(
                    f"<div style='font-size:18px; line-height:1.6; white-space:pre-wrap; padding-bottom:24px;'>{text}</div>",
                    unsafe_allow_html=True
                )




with tab2:
    st.subheader("📊 Visualization Dashboard")
    
    # Month selector for dashboard
    dash_col1, dash_col2 = st.columns(2)
    with dash_col1:
        dash_month = st.selectbox("Select Month", list(calendar.month_name)[1:], index=st.session_state.current_month - 1, key="dash_month")
    with dash_col2:
        dash_year = st.selectbox("Select Year", range(2024, 2027), index=st.session_state.current_year - 2024, key="dash_year")
    
    dash_month_num = list(calendar.month_name).index(dash_month)
    
    # Calculate data for the selected month
    monthly_data = defaultdict(int)
    for habit_name, habit_data in st.session_state.habits.items():
        if habit_name == 'notes':
            continue
        total = 0
        for date_key, count in habit_data['count'].items():
            if date_key.startswith(f"{dash_year}-{dash_month_num:02d}"):
                total += count
        monthly_data[habit_name] = total
    
    # Create heatmap data
    st.subheader("🔥 Monthly Heatmap")
    
    for habit_name, habit_data in st.session_state.habits.items():
        if habit_name == 'notes':
            continue
        st.markdown(f"<div style='color: white; margin-bottom: 10px; font-weight: bold;'>{habit_name}</div>", unsafe_allow_html=True)
        
        max_count = max([habit_data['count'].get(f"{dash_year}-{dash_month_num:02d}-{day:02d}", 0) 
                        for day in range(1, 32)], default=1)
        
        # Create columns for heatmap
        days_in_month = calendar.monthrange(dash_year, dash_month_num)[1]
        
        # Display in rows of 7
        for week_start in range(0, days_in_month, 7):
            cols = st.columns(7)
            for i in range(7):
                day = week_start + i + 1
                if day <= days_in_month:
                    with cols[i]:
                        date_key = f"{dash_year}-{dash_month_num:02d}-{day:02d}"
                        count = habit_data['count'].get(date_key, 0)
                        opacity = min(count / max_count, 1) if max_count > 0 else 0.1
                        
                        color = habit_data['color']
                        st.markdown(f"""
                            <div style='width: 100%; height: 40px; background: {color}; 
                                 opacity: {opacity}; border-radius: 3px; display: flex; 
                                 align-items: center; justify-content: center; color: white; 
                                 font-size: 12px; border: 1px solid #333; font-weight: bold;'>
                                {day}
                            </div>
                        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    st.divider()
    
    # Activity Distribution
    st.subheader("📈 Activity Distribution")
    
    if sum(monthly_data.values()) > 0:
        pie_cols = st.columns([2, 1])
        
        with pie_cols[0]:
            # Create a simple visual representation
            total = sum(monthly_data.values())
            
            for habit_name, count in monthly_data.items():
                percentage = (count / total * 100) if total > 0 else 0
                color = st.session_state.habits[habit_name]['color']
                
                st.markdown(f"""
                <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 10px;'>
                    <div style='min-width: 150px; color: white;'>{habit_name}</div>
                    <div style='flex-grow: 1; height: 30px; background: {color}; 
                         border-radius: 5px; display: flex; align-items: center; 
                         justify-content: center; color: white; font-weight: bold;'>
                        {count} ({percentage:.1f}%)
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with pie_cols[1]:
            st.markdown("### Totals")
            for habit_name, count in monthly_data.items():
                color = st.session_state.habits[habit_name]['color']
                st.markdown(f"""
                <div style='padding: 10px; margin: 5px 0; background: #1a1a1a; 
                     border-left: 12px solid {color}; border-radius: 5px;'>
                    <div style='color: white; font-weight: bold;'>{habit_name}</div>
                    <div style='color: {color}; font-size: 24px;'>{count}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No data for this month yet!")
