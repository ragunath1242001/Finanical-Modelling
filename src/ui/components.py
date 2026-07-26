import streamlit as st


def teaching_block(question: str, calculation: str, impact: str, notes: str) -> None:
    st.subheader("What this module answers")
    st.write(question)
    st.subheader("Calculation trace")
    st.code(calculation, language="text")
    st.subheader("Explanation")
    st.write(impact)
    st.subheader("Note")
    st.info(notes)
