import streamlit as st
import json


def download_upload_settings():
    settings_to_download = {k: v for k, v in st.session_state.items()}
    st.download_button(
        label="Save",
        data=json.dumps(settings_to_download),
        file_name='saved_file.json',
        mime='application/json',
        use_container_width=True
    )

    uploaded_file = st.file_uploader(label="Load", help="")
    if uploaded_file is not None:
        uploaded_settings = json.load(uploaded_file)
    else:
        uploaded_settings = settings_to_download

    def upload_json_settings(json_settings):
        for k in json_settings.keys():
            st.session_state[k] = json_settings[k]
        return

    st.button(label="Load File",
              on_click=upload_json_settings,
              args=(uploaded_settings,),
              help="",
              type='primary',
              use_container_width=True)