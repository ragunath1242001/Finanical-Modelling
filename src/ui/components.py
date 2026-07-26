import streamlit as st


def teaching_block(question: str, calculation: str, impact: str, notes: str) -> None:
    st.subheader("What this module answers")
    st.write(question)
    st.subheader("Calculation trace")
    st.code(calculation, language="text")
    st.subheader("Plain-English explanation")
    st.write(impact)
    st.subheader("Notes")
    st.info(notes)
