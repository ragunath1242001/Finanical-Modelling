from __future__ import annotations

import streamlit as st


def metrics_row(items: list[tuple[str, str]]) -> None:
    """Render a compact row of Streamlit metrics."""
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        col.metric(label, value)


def render_app_header(app_name: str, app_tagline: str) -> None:
    st.markdown(
        f"""
        <div class="app-hero">
            <h1>{app_name}</h1>
            <p>{app_tagline}</p>
            <div class="hero-chips">
                <span class="hero-chip">Risk analytics</span>
                <span class="hero-chip">Regulatory reporting</span>
                <span class="hero-chip">Governance controls</span>
                <span class="hero-chip">Study guide</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_capability_cards(capabilities: list[tuple[str, str, str]]) -> None:
    for row_start in range(0, len(capabilities), 3):
        columns = st.columns(3)
        for column, capability in zip(columns, capabilities[row_start : row_start + 3]):
            icon, area, description = capability
            with column:
                with st.container(border=True):
                    st.markdown(f"#### `{icon}` {area}")
                    st.write(description)


def modelling_depth_label(depth: str, purpose: str, methodology: str, assumptions: str, limitations: str) -> None:
    st.caption(f"Modelling depth: {depth} | View mode: {st.session_state.get('view_mode', 'Standard View')}")
    expanded = st.session_state.get("view_mode") == "Learning View"
    with st.expander("Methodology, assumptions and limitations", expanded=expanded):
        st.write(f"Purpose: {purpose}")
        st.write(f"Methodology: {methodology}")
        st.write(f"Assumptions: {assumptions}")
        st.write(f"Limitations: {limitations}")
        st.info("Educational approximation only. This is not a production regulatory, accounting, or capital-compliance engine.")


def teaching_block(question: str, calculation: str, impact: str, notes: str) -> None:
    if st.session_state.get("view_mode") != "Learning View":
        with st.expander("Learning notes and calculation trace", expanded=False):
            _render_teaching_block(question, calculation, impact, notes)
        return
    _render_teaching_block(question, calculation, impact, notes)


def _render_teaching_block(question: str, calculation: str, impact: str, notes: str) -> None:
    st.subheader("What this module answers")
    st.write(question)
    st.subheader("Calculation trace")
    st.code(calculation, language="text")
    st.subheader("Explanation")
    st.write(impact)
    st.subheader("Note")
    st.info(notes)
