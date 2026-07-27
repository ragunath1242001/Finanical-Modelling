"""Shared Streamlit styling for the application shell."""

from __future__ import annotations

import plotly.express as px
import streamlit as st


def configure_plotly_defaults() -> None:
    px.defaults.template = "plotly_white"
    px.defaults.color_discrete_sequence = ["#0F766E", "#2563EB", "#B7791F", "#B42318", "#4C6FFF", "#64748B"]


def inject_custom_style() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ink: #17202A;
            --muted: #5D6D7E;
            --panel: #FFFFFF;
            --line: #D9E2EC;
            --teal: #0F766E;
            --teal-dark: #115E59;
            --blue: #2563EB;
            --amber: #B7791F;
            --rose: #B42318;
            --soft-blue: #EAF2FF;
            --soft-teal: #E6F4F1;
            --soft-amber: #FFF7E6;
        }

        .stApp {
            background:
                linear-gradient(180deg, #F4F8FB 0%, #F7FAFC 42%, #F5F7FA 100%);
            color: var(--ink);
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #102A43 0%, #123B52 58%, #0F766E 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.18);
        }

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] h4,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
        section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
            color: #F8FAFC !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSelectbox"] {
            position: relative;
        }

        section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
            background: #FFFFFF;
            border-color: rgba(255, 255, 255, 0.44);
            border-radius: 8px;
            position: relative;
            padding-right: 1.8rem;
        }

        section[data-testid="stSidebar"] div[data-baseweb="select"] > div::after {
            content: "";
            position: absolute;
            right: 0.85rem;
            top: 50%;
            transform: translateY(-35%);
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid var(--teal);
            pointer-events: none;
            z-index: 5;
        }

        section[data-testid="stSidebar"] div[data-baseweb="select"] *,
        section[data-testid="stSidebar"] div[data-baseweb="select"] [role="combobox"],
        section[data-testid="stSidebar"] div[data-baseweb="select"] input,
        section[data-testid="stSidebar"] div[data-baseweb="select"] span {
            color: #102A43 !important;
            -webkit-text-fill-color: #102A43 !important;
        }

        section[data-testid="stSidebar"] div[data-baseweb="select"] svg,
        section[data-testid="stSidebar"] div[data-baseweb="select"] svg * {
            color: #0F766E !important;
            fill: #0F766E !important;
            stroke: #0F766E !important;
            opacity: 1 !important;
            visibility: visible !important;
        }

        section[data-testid="stSidebar"] .stSlider [data-testid="stTickBar"] {
            background: rgba(255, 255, 255, 0.22);
        }

        .main .block-container {
            padding-top: 1.5rem;
            max-width: 1320px;
        }

        .app-hero {
            background:
                linear-gradient(135deg, rgba(15, 118, 110, 0.96), rgba(37, 99, 235, 0.86) 54%, rgba(183, 121, 31, 0.86));
            border: 1px solid rgba(255, 255, 255, 0.38);
            border-radius: 12px;
            padding: 1.25rem 1.35rem;
            margin: 0.25rem 0 1.2rem 0;
            box-shadow: 0 18px 45px rgba(16, 42, 67, 0.18);
        }

        .app-hero h1 {
            color: white;
            font-size: 2rem;
            line-height: 1.15;
            margin: 0 0 0.45rem 0;
            letter-spacing: 0;
        }

        .app-hero p {
            color: rgba(255, 255, 255, 0.9);
            margin: 0;
            max-width: 920px;
            font-size: 0.98rem;
        }

        .hero-chips {
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
            margin-top: 0.85rem;
        }

        .hero-chip {
            border: 1px solid rgba(255, 255, 255, 0.36);
            background: rgba(255, 255, 255, 0.15);
            color: white;
            border-radius: 999px;
            padding: 0.28rem 0.65rem;
            font-size: 0.82rem;
            font-weight: 650;
        }

        h2, h3 {
            letter-spacing: 0;
            color: #102A43;
        }

        div[data-testid="stMetric"] {
            background: var(--panel);
            border: 1px solid var(--line);
            border-left: 4px solid var(--teal);
            border-radius: 10px;
            padding: 0.8rem 0.95rem;
            box-shadow: 0 10px 26px rgba(16, 42, 67, 0.08);
        }

        div[data-testid="stMetricLabel"] p {
            color: var(--muted);
            font-weight: 700;
        }

        div[data-testid="stMetricValue"] {
            color: var(--ink);
            font-weight: 800;
        }

        button[kind="primary"], div.stButton > button, div[data-testid="stDownloadButton"] button {
            border-radius: 8px;
            border: 1px solid rgba(15, 118, 110, 0.25);
            background: linear-gradient(135deg, var(--teal), var(--teal-dark));
            color: white;
            font-weight: 700;
            box-shadow: 0 10px 22px rgba(15, 118, 110, 0.18);
        }

        div.stButton > button:hover, div[data-testid="stDownloadButton"] button:hover {
            border-color: rgba(37, 99, 235, 0.55);
            box-shadow: 0 12px 28px rgba(37, 99, 235, 0.20);
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.35rem;
            border-bottom: 1px solid var(--line);
        }

        .stTabs [data-baseweb="tab"] {
            background: #FFFFFF;
            border: 1px solid var(--line);
            border-bottom: none;
            border-radius: 8px 8px 0 0;
            padding: 0.45rem 0.85rem;
            color: var(--muted);
            font-weight: 700;
        }

        .stTabs [aria-selected="true"] {
            background: var(--soft-teal);
            color: var(--teal-dark);
            border-color: rgba(15, 118, 110, 0.32);
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid var(--line);
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 8px 22px rgba(16, 42, 67, 0.06);
        }

        div[data-testid="stPlotlyChart"] {
            background: #FFFFFF;
            border: 1px solid var(--line);
            border-radius: 10px;
            padding: 0.35rem;
            box-shadow: 0 8px 22px rgba(16, 42, 67, 0.06);
        }

        div[data-baseweb="input"] > div, div[data-baseweb="select"] > div, textarea {
            border-radius: 8px;
            border-color: var(--line);
        }

        div[data-testid="stSlider"] {
            background: rgba(255, 255, 255, 0.55);
            border-radius: 10px;
            padding: 0.35rem 0.55rem 0.15rem 0.55rem;
        }

        div[data-testid="stExpander"] {
            background: #FFFFFF;
            border: 1px solid var(--line);
            border-radius: 10px;
            box-shadow: 0 8px 22px rgba(16, 42, 67, 0.05);
        }

        .cap-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(245px, 1fr));
            gap: 0.8rem;
            margin: 0.7rem 0 1rem 0;
        }

        .cap-card {
            background: #FFFFFF;
            border: 1px solid var(--line);
            border-top: 4px solid var(--teal);
            border-radius: 10px;
            padding: 0.95rem;
            box-shadow: 0 12px 28px rgba(16, 42, 67, 0.08);
            min-height: 148px;
        }

        .cap-icon {
            width: 2.1rem;
            height: 2.1rem;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
            background: var(--soft-blue);
            color: var(--blue);
            font-weight: 900;
            margin-bottom: 0.55rem;
        }

        .cap-card h4 {
            margin: 0 0 0.35rem 0;
            color: #102A43;
            font-size: 1rem;
        }

        .cap-card p {
            color: var(--muted);
            font-size: 0.9rem;
            margin: 0;
            line-height: 1.42;
        }

        .stAlert {
            border-radius: 10px;
            border: 1px solid rgba(15, 118, 110, 0.2);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
