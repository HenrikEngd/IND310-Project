import streamlit as st
import pandas as pd
from data_cache import load_market_data

# Hent data fra cache
try:
    data, adj_close_data, returns_df, betas = load_market_data()
    
    st.title("Beta Values")
    
    # Vis beta-verdier
    st.subheader("Calculated Beta Values")
    
    beta_df = pd.DataFrame({
        'Ticker': list(betas.keys()),
        'Beta': list(betas.values())
    })
    
    st.dataframe(beta_df, use_container_width=True)
    
    # Vis forklaring
    st.info("""
    **Beta** måler en aksjes følsomhet til markedsbevegelser:
    - β = 1: Aksjen følger markedet
    - β > 1: Aksjen er mer volatil enn markedet
    - β < 1: Aksjen er mindre volatil enn markedet
    - β < 0: Aksjen beveger seg mot markedet
    """)
    
except Exception as e:
    st.error(f"Kunne ikke laste data: {e}")
    st.stop()
