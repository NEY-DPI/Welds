import streamlit as st
import pandas as pd
from io import StringIO
import func as f

'''
# Welds


'''

"## Import Files"
"### Import txt file from wingraf"
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    data = stringio.readlines()
    forces = f.decode(data)
    forces_by_cut = forces.groupby('cut').first()
    list_of_cuts = forces_by_cut[0]
    list_of_cuts
