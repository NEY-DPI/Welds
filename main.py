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
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    data = stringio.readlines()

    appending = False
    list = []
    results = []

    for line in data:
        print(line)
        if not appending:
            if "no." in line:
                list = []
                appending = True
        else:
            if line == " ":
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
