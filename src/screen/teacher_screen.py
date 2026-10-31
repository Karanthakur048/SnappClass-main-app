import time
import numpy as np
import pandas as pd
import streamlit as st
from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.dialog_create import create_subject_dialog
from src.components.subject_card import subject_card
from src.database.db import teacher_login, check_teacher_exists, create_teacher,get_teacher_subjects,get_attendance_for_teacher
from src.components.dialog_share_subject import share_subject_dialog
from src.Pipelines.face_pipeline import predict_attendance
from src.components.dialog_add_photo import add_photos_dialog
from src.database.config import supabase
from datetime import datetime
from src.components.dialog_attendance_results import attendance_results_dialog
from src.Pipelines import voice_pipeline
from src.components.dialog_voice_attendance import voice_attendance_dialog


def teacher_screen():
    
    style_background_dashboard()
    style_base_layout()
    if "teacher_data" in st.session_state:
        teacher_dashboard()

    elif 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type == "login":
        teacher_screen_login()
    elif st.session_state.teacher_login_type == "register":
        teacher_screen_register()



def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    
    c1, c2 = st.columns(2, vertical_alignment="center", gap="xxlarge")
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"""Welcome,{teacher_data['name']}""")
        st.button(
            "Logout",
            key="loginoutbtn",
            shortcut="control+backspace",
            on_click=lambda: (
                st.session_state.update(is_logged_in=False),
                st.session_state.pop("teacher_data", None),
            ),
            width="stretch",
        )
        
    st.space()    
    
    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab ='take_attendance'
   
    
    tab1 ,tab2, tab3  = st.columns(3)
    
    
    with tab1:
        if st.button('Take Attendance',width = 'stretch',icon  = ':material/ar_on_you:'):
            st.session_state.current_teacher_tab = "take_attendance"
            st.rerun()
             
             
             
    with tab2:
        if st.button('Manage Subjects',width = 'stretch',icon  = ':material/book_ribbon:',type = 'primary'):
            st.session_state.current_teacher_tab = "manage_subjects"
            st.rerun()
                                    
    with tab3:
        if st.button('Attendance Records',width = 'stretch',icon  = ':material/cards_stack:'):
            st.session_state.current_teacher_tab = "attendance_records"
            st.rerun()
                 
    st.divider()             
                 
    if st.session_state.current_teacher_tab == "take_attendance":
        teacher_tab_take_attendance()
        
    if st.session_state.current_teacher_tab == "manage_subjects":
        teacher_tab_manage_subjects() 
    if st.session_state.current_teacher_tab == "attendance_records":
        teacher_tab_attendance_records()                    
                 
                 
                 
                 
def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data['teacher_id']
    
    
    st.header('Take AI Attendance')
    
    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []
        
    subjects = get_teacher_subjects(teacher_id)  
    if not subjects:
        st.warning("You have not created any subjects yet! Please create one")
        return 
    
    subject_option = {f"{s['name']} - {s['subject_code']}":s['subject_id'] for s in subjects}
    col1, col2 = st.columns([3,1])
    
    
    
    with col1:
        selected_subject_label = st.selectbox('Select Subject',options = list(subject_option.keys()),key='subject_select')
        
        st.markdown("""
                    <style>
                    div[data-testid="stSelectbox"] label {
                        color: black !important;
}

                    </style>
                    """,unsafe_allow_html = True)
        
                 
        
        
    with col2:
        if st.button('Add photos',type = 'secondary',icon=':material/photo_prints:',width= 'stretch'):
            add_photos_dialog()
    
    selected_subject_id = subject_option[selected_subject_label]
    
    st.divider()
    
    
    if st.session_state.attendance_images:
        
        st.header('Added Photos')
        gallery_cols = st.columns(4)
        
        for idx, img in enumerate(st.session_state.attendance_images):
            with gallery_cols[idx % 4]:
                st.image(img,width = 'stretch',caption = f'photo{idx+1}')
    
    has_photos = bool(st.session_state.attendance_images)
    c1,c2,c3 =st.columns(3)
    with c1:
        if st.button("Clear all photos",width = 'stretch',type = 'tertiary',icon = ':material/delete:',disabled = not has_photos):
            st.session_state.attendance_images = []
            st.rerun()

    with c2:
        
        
        if st.button("Run Face Analysis",width = 'stretch',type = 'primary',icon = ':material/analytics:'):
            with st.spinner('Deep scanning classroom photos...'):
                all_detected_id = {}
                for idx,img in enumerate(st.session_state.attendance_images):
                    img_np  = np.array(img.convert('RGB'))
                    
                    detected, _, _ = predict_attendance(img_np)
                    
                    if detected:
                        for sid in detected.keys():
                            student_id = int(sid)

                            all_detected_id.setdefault(student_id,[]).append(f"Photo{idx+1}")

                enrolled_res = supabase.table('subject_students').select('*,students(*)').eq('subject_id', selected_subject_id).execute()
                
                enrolled_students = enrolled_res.data
                
                if not enrolled_students:
                    st.warning("No students enrolled in this course")
                else:
                    results, attendance_to_log = [],[]
                    
                    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


                    for node in enrolled_students:
                        student = node['students']
                        sources = all_detected_id.get(int(student['student_id']), [])
                        is_present = len(sources)>0
                        
                        results.append({
                            "Name":student['name'],
                            "ID": student['student_id'],
                            "Source": ", ".join(sources) if is_present else "-",
                            "Status": "✅ Present" if is_present else "❌Absent"
                        })
                        
                        
                        attendance_to_log.append({
                            'student_id': student['student_id'],
                            'subject_id': selected_subject_id,
                            'timestamp': current_timestamp,
                            'is_present': bool(is_present)
                            
                        })
                        
                        
                    attendance_results_dialog(pd.DataFrame(results),attendance_to_log)   
    with c3:
        if st.button('Use voice Attendence',width = 'stretch',icon =':material/mic:'):
            voice_attendance_dialog(selected_subject_id)
            
    
        
        
        
    
def teacher_tab_manage_subjects():
    
    teacher_id = st.session_state.teacher_data['teacher_id']
    col1, col2  = st.columns(2,gap = "large")
    with col1:
        st.header('Manage Subjects',)
    with col2:
        if st.button('Create new subject',width ='stretch'):
            create_subject_dialog(teacher_id)
        
    
    
    #list all Subjects

    subjects = get_teacher_subjects(teacher_id)
    if subjects:
        for sub in subjects:
            stats = [
                ("👨‍🎓", "Students", sub['total_students']),
                ("👥", "Classes ", sub['total_classes']),
            ]
            
            def share_btn(sub=sub):
                if st.button(
                   "Share Code:Introduction to memes",
                    key=f"share_{sub['subject_code']}",
                    icon=":material/share:",
        ):
                    share_subject_dialog(sub['name'], sub['subject_code'])

                
                
                st.space()    
                    
            subject_card(
                name = sub['name'],
                code = sub['subject_code'],
                section= sub['section'],
                stats = stats,
                footer_callback = share_btn,
                
        )
    else:
        st.warning("No Subjects Found.Create One Above")
                  
                    
def teacher_tab_attendance_records():
    st.header('Attendance Records')

    teacher_id = st.session_state.teacher_data['teacher_id']
    records = get_attendance_for_teacher(teacher_id)

    if not records:
        st.info("No attendance records yet.")
        return

    data = []
    for r in records:
        ts = r.get('timestamp')
        dt = datetime.fromisoformat(ts) if ts else None

        data.append({
            "ts_group": dt.strftime("%Y-%m-%d") if dt else None,
            "Time": dt.strftime("%Y-%m-%d %I:%M %p") if dt else "N/A",
            "Subject": r['subjects']['name'],
            "Subject Code": r['subjects']['subject_code'],
            "is_present": bool(r.get('is_present', False)),
        })

    df = pd.DataFrame(data)

    summary = (
        df.groupby(['ts_group', 'Time', 'Subject', 'Subject Code'])
        .agg(
            Present_Count=('is_present', 'sum'),
            Total_Count=('is_present', 'count'),
        )
        .reset_index()
    )

    summary['Attendance Stats'] = (
        "✅ " + summary['Present_Count'].astype(str) + " / "
        + summary['Total_Count'].astype(str) + " Students"
    )

    display_df = (
        summary.sort_values(by=['ts_group', 'Time'], ascending=False)
        [['Time', 'Subject', 'Subject Code', 'Attendance Stats']]
    )

    st.dataframe(display_df, width='stretch', hide_index=True)          
                 
                 
                 
                 
      
def login_teacher(username, password):
    if not username or not password:
        return False
    teacher = teacher_login(username, password)

    if teacher:
        st.session_state.user_role = 'teacher'
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True
    return False                                  
                                  
                 
# For login
def teacher_screen_login():
    c1, c2 = st.columns(
        2,
        vertical_alignment="center",
        gap="xxlarge"
    )
    with c1:
        header_dashboard()
    with c2:
        st.button(
            "Go back to Home",
            key="loginbackbtn",
            shortcut="control+backspace",
            on_click=lambda: st.session_state.update(login_type=None),
            width="stretch"
        )

    st.header('Login using password', text_alignment='center')

    teacher_username = st.text_input("Enter username", placeholder='karanthakur')
    teacher_password = st.text_input("Enter password", type='password', placeholder='@abc123')

    st.divider()

    btnc1, btnc2 = st.columns(2, gap="small")

    with btnc1:
        if st.button("login", icon=":material/passkey:", width="stretch"):
            if login_teacher(teacher_username, teacher_password):
                st.toast("welcome back!", icon="👋")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid username and password")

    with btnc2:
        st.button(
            "Register Instead",
            type="primary",
            icon=":material/passkey:",
            width="stretch",
            on_click=lambda: st.session_state.update(teacher_login_type="register")
        )

    st.markdown("""
<style>
div[data-testid="stTextInput"] input {
    background-color: #F8F9FF !important;
    color: black !important;
    border: 10px solid white !important;
}
div[data-testid="stTextInput"] input::placeholder {
    background-color: #F8F9FF !important;
    color: black !important;
}
div[data-testid="stTextInput"] label p {
    color: black !important;
}
[data-baseweb="base-input"] {
    background-color: #F8F9FF !important;
}
</style>
""", unsafe_allow_html=True)


# to send data in database
def register_teacher(teacher_username, teacher_password, teacher_pass_confirm, teacher_name):
    if not teacher_username or not teacher_password:
        return False, "All fields are required!"
    if check_teacher_exists(teacher_username):
        return False, "username already taken"
    if teacher_password != teacher_pass_confirm:
        return False, "password doesn't match"
    try:
        create_teacher(teacher_username, teacher_password, teacher_name)
        return True, "Successfully Created! Login Now"
    except Exception as e:
        st.error(f"Actual error: {str(e)}")
        return False, "Registration failed!"


def teacher_screen_register():
    c1, c2 = st.columns(
        2,
        vertical_alignment="center",
        gap="xxlarge"
    )

    with c1:
        header_dashboard()

    with c2:
        st.button(
            "Go back to Home",
            key="loginbackbtn",
            shortcut="control+backspace",
            on_click=lambda: st.session_state.update(login_type=None),
            width="stretch"
        )

    st.markdown("""
    <h2 class="Teacher">Register Your Teacher Profile </h2>
    """, unsafe_allow_html=True)

    teacher_username = st.text_input("Enter username", placeholder="karanthakur")
    teacher_name = st.text_input("Enter your name", placeholder="Karan Thakur")
    teacher_password = st.text_input("Enter password", type="password", placeholder="@abc123")
    teacher_pass_confirm = st.text_input("Confirm your password", type="password", placeholder="Enter password")

    st.markdown("""
<style>
h2.Teacher {
    white-space: nowrap !important;
    padding-top: 30px !important;
    padding-bottom: 30px !important;
}
div[data-testid="stTextInput"] input {
    background-color: #F8F9FF !important;
    color: black !important;
    border: 10px solid white !important;
}
div[data-testid="stTextInput"] input::placeholder {
    background-color: #F8F9FF !important;
    color: black !important;
}
div[data-testid="stTextInput"] label p {
    color: black !important;
}
[data-baseweb="base-input"] {
    background-color: #F8F9FF !important;
}
</style>
""", unsafe_allow_html=True)

    st.divider()

    btnc1, btnc2 = st.columns(2, gap="small")

    with btnc1:
        if st.button("Register Now", icon=":material/passkey:", width="stretch"):
            success, message = register_teacher(teacher_username, teacher_password, teacher_pass_confirm, teacher_name)
            if success:
                st.success(message)
                time.sleep(2)
                st.session_state.teacher_login_type = "login"
                st.rerun()
            else:
                st.error(message)

    with btnc2:
        st.button(
            "Login Instead",
            type="primary",
            icon=":material/passkey:",
            width="stretch",
            on_click=lambda: st.session_state.update(teacher_login_type='login')
        )