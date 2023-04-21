import streamlit as st
import pandas as pd
from io import StringIO

'''
# Welds


'''

"## Import Files"
"### Import txt file from wingraf"
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    data = uploaded_file.readlines()

    appending = False
    list = []
    results = []

    for line in data:
        if not appending:
            if "no." in line:
                list = []
                appending = True
        else:
            if len(line.split()) < 1:
                appending = False
                results.append(list)
            else:
                list.append(line)

    results1 = []
    for list in results:
        list1 = []
        for line in list:
            list1.append([float(x) for x in line.split()])
        results1.append(list1)


    results1