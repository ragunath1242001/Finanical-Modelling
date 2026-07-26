import streamlit as st


def teaching_block(question: str, calculation: str, impact: str, interview: str) -> None:
    st.subheader("What this module answers")
    st.write(question)
    st.subheader("Calculation trace")
    st.code(calculation, language="text")
    st.subheader("Plain-English explanation")
    st.write(impact)
    st.subheader("Interview answer box")
    st.info(interview)
