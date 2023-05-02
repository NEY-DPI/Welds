import streamlit as st
import pandas as pd
from io import StringIO
import func as f
import frontend as fr
import altair as alt
import matplotlib.pyplot as plt
from matplotlib.ticker import (AutoMinorLocator, MultipleLocator)
import json

'''
# Welds
'''

# Save / Load
with st.sidebar.expander("Save / Load"):
    fr.download_upload_settings()

# Mode
with st.sidebar.expander("Settings"):
    calc_mode = st.selectbox('Calculation Mode', ['Values along weld', 'Max per weld'],
                             key='calc mode',
                             index=0,
                             help='''
                             "Values along weld" : meant for a few continuous welds,
                             like for bridge longitudinal welds\n
                             "Max per weld" : meant for many discrete welds, like for bridge stiffeners welds
                             ''')

# Forces Input
with st.sidebar.expander("Input Forces"):
    forces_input_mode = st.selectbox('Forces Input Mode', ['From Wingraf', 'From Excel'],
                                     key='forces input mode',
                                     index=0)
    if forces_input_mode == 'From Wingraf':
        # TODO: give instructions for wingraf
        forces_input = st.file_uploader("Choose a file")
    elif forces_input_mode == 'From Excel':
        forces_input = None
        # TODO: download template excel
        # TODO: upload excel
        pass

# Weld Inputs
with st.sidebar.expander("Weld Inputs"):
    weld_inputs_mode = st.selectbox('Weld Input Mode', ['Unique values', 'From Excel'],
                                    key='weld input mode',
                                    index=0)

    if weld_inputs_mode == 'Unique values':
        list_of_weld_types = ['double fillet', 'single fillet', 'double partial pen', 'single partial pen', 'full pen']
        w_type = st.selectbox('Weld type', list_of_weld_types, index=0, key='weld type', help=None)
        col1, col2 = st.columns(2)
        with col1:
            a = st.number_input(r'$\small{a (mm)}$', min_value=3, value=6, step=1, key='a', help='''
                            Weld size. For fillet welds:\n
                            $\\leq7mm$ -> 1x pass\n
                            $\\leq9mm$ -> 2x pass\n
                            $\\leq11mm$ -> 4x pass\n
                            ''')
            tpl1 = st.number_input('$\small{t_{pl1} (mm)}$', min_value=0, value=15, step=1, key='tpl1',
                                   help="Thickness of welded plate")
            beta_w = st.number_input('$\small{\\beta_w}$', min_value=0.00, value=0.90, step=0.01, key='beta_w', help='''
                        S235 -> $\\beta_w$ = 0.80\n
                        S275 -> $\\beta_w$ = 0.85\n
                        S355 -> $\\beta_w$ = 0.90\n
                        S420 -> $\\beta_w$ = 0.10\n
                        S460 -> $\\beta_w$ = 0.10\n
                        ''')
        with col2:
            fu = st.number_input('$\small{f_u (MPa)}$', min_value=0, value=470, step=1, key='fu',
                                 help="$\small{f_u}$ of welded plates (470MPa for S355)")
            tpl2 = st.number_input('$\small{t_{pl2} (mm)}$', min_value=0, value=15, step=1, key='tpl2', help="Thickness of receiver plate")
            g_M2 = st.number_input('$\small{\\gamma_{M2}}$', min_value=0.00, value=1.25, step=0.01, key='g_m2', help=None)
        weld_inputs = {
            'w_type': w_type,
            'a' : a,
            'tpl1': tpl1,
            'tpl2': tpl2,
            'beta_w': beta_w,
            'fu': fu,
            'g_M2': g_M2
        }

    elif weld_inputs_mode == 'From Excel':
        # TODO: download template excel
        # TODO: upload excel
        pass


# Calculated values
fw_perp = 0.9 * fu / g_M2
fw_vm = fu / (beta_w * g_M2)
weld_inputs['fw_perp'] = fw_perp
weld_inputs['fw_vm'] = fw_vm


# Calculate graph
with st.expander("Graph"):
    forces = f.get_forces(forces_input_mode, forces_input)
    weld = f.get_weld_inputs(weld_inputs_mode, weld_inputs)
    f.calc_graph(forces, weld, calc_mode)






# Calculated Values
with st.expander("Calculated values"):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        string = '\small{' + 'f_{w,\perp}' + f'= {"{:.2f}".format( fw_perp )}' + 'MPa' + '}'
        st.latex(string)
    with col2:
        string = '\small{' + 'f_{w,vm}' + f'= {"{:.2f}".format(fw_vm)}' + 'MPa' + '}'
        st.latex(string)

# Manual input of forces
with st.expander("Manual input of forces"):
    init = pd.DataFrame(
        [
           {"LC": "1", "N": 10, "M": 10, "Vt": 10, "Vl": 10}
       ]
    )
    forces_man = st.experimental_data_editor(init, width=None, height=None, use_container_width=False,
                                                num_rows="dynamic", disabled=False, key=8)
    df_man = forces_man
    df_man['d'] = forces_man['LC']
    df_man['w_type'] = w_type
    df_man['tpl1'] = tpl1
    df_man['tpl2'] = tpl2
    df_man['a'] = a

    calc_cut = f.calculate(df_man, fw_vm, fw_perp)
    st.pyplot(fig=f.make_plot_man(calc_cut), clear_figure=None, use_container_width=True)


