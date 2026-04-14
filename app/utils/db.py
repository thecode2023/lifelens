"""Database connection and query utilities for LifeLens."""
import sqlite3
import pandas as pd
import streamlit as st
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'lifelens.db')


def get_connection():
    """Get SQLite connection."""
    return sqlite3.connect(DB_PATH, check_same_thread=False)


@st.cache_data(ttl=3600)
def query(sql: str, params: tuple = ()) -> pd.DataFrame:
    """Execute SQL and return DataFrame."""
    conn = get_connection()
    df = pd.read_sql_query(sql, conn, params=params)
    conn.close()
    return df


@st.cache_data(ttl=3600)
def get_all_counties() -> pd.DataFrame:
    """Get all county health data with index scores."""
    df = query("""
        SELECT c.county_fips, c.county_name, c.state_abbr, c.state_fips, c.population,
               f.*
        FROM dim_county c
        JOIN fact_county_health f ON c.county_fips = f.county_fips
        ORDER BY c.state_abbr, c.county_name
    """)
    # Remove duplicate county_fips column from f.*
    df = df.loc[:, ~df.columns.duplicated()]
    return df


@st.cache_data(ttl=3600)
def get_county(fips: str) -> pd.Series:
    """Get single county record."""
    df = query("SELECT * FROM fact_county_health WHERE county_fips = ?", (fips,))
    if len(df) == 0:
        return None
    return df.iloc[0]


@st.cache_data(ttl=3600)
def get_county_with_meta(fips: str) -> pd.Series:
    """Get county data with name/state."""
    df = query("""
        SELECT c.county_name, c.state_abbr, c.population, f.*
        FROM dim_county c
        JOIN fact_county_health f ON c.county_fips = f.county_fips
        WHERE c.county_fips = ?
    """, (fips,))
    if len(df) == 0:
        return None
    return df.iloc[0]


@st.cache_data(ttl=3600)
def get_state_avg(state_fips: str) -> pd.Series:
    """Get state-level averages."""
    df = query("SELECT * FROM agg_state_health WHERE state_fips = ?", (state_fips,))
    if len(df) == 0:
        return None
    return df.iloc[0]


@st.cache_data(ttl=3600)
def get_national_avg() -> pd.Series:
    """Get national averages."""
    df = query("SELECT * FROM agg_national_health")
    return df.iloc[0]


@st.cache_data(ttl=3600)
def get_county_list() -> pd.DataFrame:
    """Get list of counties for dropdown selection."""
    return query("""
        SELECT c.county_fips, c.county_name, c.state_abbr, c.population,
               f.health_equity_index, f.hei_tier
        FROM dim_county c
        JOIN fact_county_health f ON c.county_fips = f.county_fips
        ORDER BY c.state_abbr, c.county_name
    """)
