import pandas as pd
import streamlit as st

def filter_search_view(data):
    st.title("🔍 Advanced Filter Search")

    # ---------------- TOTAL COUNTS ----------------
    total_real = len(data[~data['group'].str.contains('demo', case=False, na=False)])
    total_demo = len(data[data['group'].str.contains('demo', case=False, na=False)])
    st.markdown(f"**Total Real Accounts:** {total_real} | **Total Demo Accounts:** {total_demo}")

    # ---------------- ACCOUNT TYPE RADIO ----------------
    account_type = st.radio(
        "Select Account Type",
        ["Real Account", "Demo Account"],
        horizontal=True
    )

    df = data.copy()

    # ---------------- FILTER ACCOUNT TYPE ----------------
    if 'group' in df.columns:
        if account_type == "Real Account":
            df = df[~df['group'].str.contains('demo', case=False, na=False)]
        else:
            df = df[df['group'].str.contains('demo', case=False, na=False)]

    # ---------------- SEARCH FILTERS IN ONE ROW ----------------
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        login_filter = st.text_input("Search by Login", placeholder="Enter login", key="login_search_bar")

    with col2:
        name_options = ["All"] + sorted(df['name'].dropna().unique().tolist())
        name_filter = st.selectbox("Filter by Name", name_options)

    with col3:
        group_options = ["All"] + sorted(df['group'].dropna().unique().tolist())
        base_filter = st.selectbox("Filter by Base Symbol", group_options)

    # ---------------- APPLY FILTERS ----------------
    if login_filter:
        df = df[df['login'].astype(str).str.contains(login_filter, case=False)]

    if name_filter != "All":
        df = df[df['name'] == name_filter]

    if base_filter != "All":
        df = df[df['group'] == base_filter]

    # ---------------- APPLY SIDEBAR FILTERS ----------------
    if 'group_filter' in st.session_state and st.session_state.group_filter:
        df = df[df['group'].isin(st.session_state.group_filter)]
    if 'name_filter' in st.session_state and st.session_state.name_filter:
        df = df[df['name'].isin(st.session_state.name_filter)]
    if 'email_filter' in st.session_state and st.session_state.email_filter:
        df = df[df['email'].isin(st.session_state.email_filter)]
    if 'leverage_filter' in st.session_state and st.session_state.leverage_filter:
        df = df[df['leverage'].isin(st.session_state.leverage_filter)]
    if 'login_search' in st.session_state and st.session_state.login_search:
        df = df[df['login'].astype(str).str.contains(st.session_state.login_search)]
    if 'balance' in df.columns:
        min_bal = st.session_state.get('min_balance', float(df['balance'].min()))
        max_bal = st.session_state.get('max_balance', float(df['balance'].max()))
        df = df[(df['balance'].astype(float) >= min_bal) & (df['balance'].astype(float) <= max_bal)]

    # ---------------- DISPLAY RESULTS ----------------
    st.subheader(f"{account_type} Results")
    st.write(f"**{len(df)} accounts found**")
    st.dataframe(df.head(500), use_container_width=True)

    # ---------------- TOP ACCOUNTS ----------------
    st.subheader(f"Top {account_type}s by Equity")
    if 'equity' in df.columns:
        top_eq = df.sort_values('equity', ascending=False).head(10)[['login', 'name', 'group', 'equity']]
        st.table(top_eq)

    st.subheader(f"Lowest Balance {account_type}s")
    if 'balance' in df.columns:
        low_bal = df.sort_values('balance', ascending=True).head(10)[['login', 'name', 'group', 'balance']]
        st.table(low_bal)
