import pandas as pd
import streamlit as st
from MT5Service import MT5Service
import io

__all__ = ['get_login_symbol_matrix', 'get_detailed_position_table', 'display_position_table']

@st.cache_data(ttl=5)      # 🔥 Auto-cache for speed (reloads every 5 sec)
def get_login_symbol_matrix(accounts_df=None, positions_cache=None):
    svc = MT5Service()

    if accounts_df is not None and not accounts_df.empty:
        # Use provided accounts dataframe
        logins = accounts_df['login'].astype(str).unique()
    else:
        # Fallback to fetching all accounts
        accounts = svc.list_mt5_accounts()
        if not accounts:
            return pd.DataFrame()
        logins = [acc["Login"] for acc in accounts]

    matrix = {}
    all_symbols = set()

    # If positions_cache wasn't provided, try to read it from Streamlit session state
    if positions_cache is None:
        try:
            positions_cache = st.session_state.get('positions_cache')
        except Exception:
            positions_cache = None

    # Normalize positions data if cache is available
    positions_list = None
    if positions_cache:
        # positions_cache may contain {'data': [...], 'timestamp': ..., ...}
        if isinstance(positions_cache, dict) and 'data' in positions_cache:
            positions_list = positions_cache.get('data') or []
        elif isinstance(positions_cache, list):
            positions_list = positions_cache

    for login in logins:
        symbol_lots = {}

        # First try to use cached positions (faster, background scanner)
        if positions_list:
            # positions stored by scanner include 'Login' key
            for p in positions_list:
                try:
                    p_login = str(p.get('Login') or p.get('login') or '')
                except Exception:
                    p_login = ''
                if p_login != str(login):
                    continue

                symbol = p.get('Symbol') or p.get('symbol')
                volume = p.get('Vol') or p.get('volume') or 0
                order_type = p.get('Type') or p.get('type')

                try:
                    volume = float(volume)
                except Exception:
                    volume = 0.0

                if not symbol:
                    continue

                if symbol not in symbol_lots:
                    symbol_lots[symbol] = 0.0

                # Determine if position is buy or sell
                is_buy = False
                if isinstance(order_type, (int, float)):
                    is_buy = int(order_type) == 0
                elif isinstance(order_type, str):
                    is_buy = order_type.strip().lower().startswith('b')
                else:
                    is_buy = True

                symbol_lots[symbol] += volume if is_buy else -volume
                all_symbols.add(symbol)

        else:
            # Fallback: query MT5Service per-login
            positions = svc.get_open_positions(login)
            for p in positions or []:
                symbol = p.get('symbol') or p.get('Symbol')
                volume = p.get('volume') or p.get('Volume') or 0
                order_type = p.get('type') or p.get('Type')

                try:
                    volume = float(volume)
                except Exception:
                    volume = 0.0

                if not symbol:
                    continue

                if symbol not in symbol_lots:
                    symbol_lots[symbol] = 0.0

                is_buy = False
                if isinstance(order_type, (int, float)):
                    is_buy = int(order_type) == 0
                elif isinstance(order_type, str):
                    is_buy = order_type.strip().lower().startswith('b')
                else:
                    is_buy = True

                symbol_lots[symbol] += volume if is_buy else -volume
                all_symbols.add(symbol)

        matrix[login] = symbol_lots

    # Convert into DataFrame
    df = pd.DataFrame.from_dict(matrix, orient="index").fillna(0.0)

    if not df.empty and len(df.columns) > 0:
        # Add "All Login" Row
        df.loc["All Login"] = df.sum()

        # Sort columns alphabetically
        df = df[sorted(df.columns)]

        # Move All Login to top
        df = df.reindex(["All Login"] + [i for i in df.index if i != "All Login"])

    return df


def get_detailed_position_table(accounts_df=None, positions_cache=None):
    """
    Get detailed position table in Symbol × Login format with volumes.
    Returns DataFrame with columns: Symbol, Login, Volume
    """
    svc = MT5Service()

    if accounts_df is not None and not accounts_df.empty:
        logins = accounts_df['login'].astype(str).unique()
    else:
        try:
            accounts = svc.list_accounts_by_groups()
            if not accounts:
                return pd.DataFrame()
            logins = [str(acc["login"]) for acc in accounts]
        except Exception:
            return pd.DataFrame()

    # If positions_cache wasn't provided, try to read it from Streamlit session state
    if positions_cache is None:
        try:
            positions_cache = st.session_state.get('positions_cache')
        except Exception:
            positions_cache = None

    # Normalize positions data if cache is available
    positions_list = None
    if positions_cache:
        if isinstance(positions_cache, dict) and 'data' in positions_cache:
            positions_list = positions_cache.get('data') or []
        elif isinstance(positions_cache, list):
            positions_list = positions_cache

    all_records = []

    if positions_list:
        # Use cached positions
        for p in positions_list:
            try:
                p_login = str(p.get('Login') or p.get('login') or '')
                symbol = p.get('Symbol') or p.get('symbol')
                volume = p.get('Vol') or p.get('volume') or 0
                order_type = p.get('Type') or p.get('type')

                if not symbol or not p_login:
                    continue

                try:
                    volume = float(volume)
                except Exception:
                    volume = 0.0

                # Determine if position is buy or sell
                is_buy = True
                if isinstance(order_type, (int, float)):
                    is_buy = int(order_type) == 0
                elif isinstance(order_type, str):
                    is_buy = order_type.strip().lower().startswith('b')

                # Net volume (positive for buy, negative for sell)
                net_volume = volume if is_buy else -volume

                all_records.append({
                    'Symbol': symbol,
                    'Login': p_login,
                    'Volume': net_volume,
                    'Type': order_type
                })
            except Exception:
                continue
    else:
        # Fallback: query MT5Service per-login
        for login in logins:
            try:
                positions = svc.get_open_positions(login)
                for p in positions or []:
                    symbol = p.get('symbol') or p.get('Symbol')
                    volume = p.get('volume') or p.get('Volume') or 0
                    order_type = p.get('type') or p.get('Type')

                    if not symbol:
                        continue

                    try:
                        volume = float(volume)
                    except Exception:
                        volume = 0.0

                    is_buy = True
                    if isinstance(order_type, (int, float)):
                        is_buy = int(order_type) == 0
                    elif isinstance(order_type, str):
                        is_buy = order_type.strip().lower().startswith('b')

                    net_volume = volume if is_buy else -volume

                    all_records.append({
                        'Symbol': symbol,
                        'Login': str(login),
                        'Volume': net_volume,
                        'Type': order_type
                    })
            except Exception:
                continue

    if not all_records:
        return pd.DataFrame(columns=['Symbol', 'Login', 'Volume', 'Type'])

    df = pd.DataFrame(all_records)
    # Sort by Symbol, then by Login
    df = df.sort_values(['Symbol', 'Login']).reset_index(drop=True)
    return df


def display_position_table(accounts_df=None, positions_cache=None, show_details=True):
    """
    Display positions in Streamlit table format (Symbol × Login × Volume).
    """
    st.subheader('📊 Login vs Symbol - Position Details')
    
    try:
        df = get_detailed_position_table(accounts_df, positions_cache)

        if df.empty:
            st.info('No open positions found.')
            return

        # Show summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Positions", len(df))
        with col2:
            total_volume = df['Volume'].sum()
            st.metric("Total Net Volume", f"{total_volume:.2f}")
        with col3:
            unique_symbols = df['Symbol'].nunique()
            st.metric("Unique Symbols", unique_symbols)

        # Display full table
        st.write("**All Positions (grouped by Symbol):**")
        display_df = df[['Symbol', 'Login', 'Volume']].copy()
        display_df['Volume'] = display_df['Volume'].round(2)
        st.dataframe(display_df, use_container_width=True, height=400)

        # Show summary by symbol
        st.write("**Summary by Symbol:**")
        summary_df = df.groupby('Symbol')['Volume'].agg(['sum', 'count']).reset_index()
        summary_df.columns = ['Symbol', 'Total Volume', 'Position Count']
        summary_df['Total Volume'] = summary_df['Total Volume'].round(2)
        st.dataframe(summary_df, use_container_width=True)

        # Export to CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label='📥 Download Positions CSV',
            data=csv,
            file_name='open_positions.csv',
            mime='text/csv'
        )

    except Exception as e:
        st.error(f'Error displaying positions: {str(e)}')
