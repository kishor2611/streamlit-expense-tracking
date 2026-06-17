"""Main entry point for the application."""
import streamlit as st
from streamlit_gsheets_connection import GSheetsConnection

def main() -> None:
    """Run the main application."""
    # Establishes connection using your hidden service account credentials
    conn = st.connection("gsheets", type=GSheetsConnection)

    # Read data from a specific worksheet tab
    df = conn.read(worksheet="Orders", ttl=0)
    st.dataframe(df)


if __name__ == "__main__":
    main()
