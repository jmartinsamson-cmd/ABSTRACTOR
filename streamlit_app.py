import streamlit as st

st.set_page_config(page_title="Abstractor", layout="wide")

st.title("Abstractor (Minimal Reset)")
st.markdown("This is a clean start. Core processing modules are archived in `archive/legacy_backend_20251027/`.")

with st.expander("What changed?"):
    st.write("""
    - Heavy processing/extraction/pipeline code was archived.
    - This UI is minimal and just confirms the app boots.
    - Reintroduce features by selectively restoring modules from the archive.
    """)

st.subheader("Quick Health Check")
st.success("Streamlit UI loaded. No backend processing is active.")
