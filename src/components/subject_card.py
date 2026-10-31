
import streamlit as st

def subject_card(name, code, section, stats=None,footer_callback = None):

    with st.container(border=True):

        # Subject card styling
        st.markdown("""
            <style>
            div[data-testid="stVerticalBlockBorderWrapper"] {
                background-color: #FFFFFF !important;
                border: 1px solid #D1D5DB !important;
                border-left: 5px solid #E9459E !important;
                border-radius: 12px !important;
                padding: 15px !important;
            }
            </style>
        """, unsafe_allow_html=True)

        # Subject details
        st.markdown(
            f"<h3 style='color:#1E293B' background-color:#FFFFFF!important>{name}</h3>",
            unsafe_allow_html=True
        )

        st.markdown(
            f"<p style='color:#64748B'>Code: {code} | Section: {section}</p>",
            unsafe_allow_html=True
        )

        # Statistics inside the same container
        if stats:
            for icon, label, value in stats:
                st.markdown(
                    f"""
                    <p style="color:#000000; margin:10px 0;">
                        {icon} <b>{value}</b> {label}
                    </p>
                    """,
                    unsafe_allow_html=True
                )
        if footer_callback:
            footer_callback()    
