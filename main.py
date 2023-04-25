import streamlit as st
import pandas as pd
from io import StringIO
import func as f
import altair as alt
import matplotlib.pyplot as plt
from matplotlib.ticker import (AutoMinorLocator, MultipleLocator)

'''
# Welds
'''

# Inputs
with st.sidebar.expander("Inputs"):
    list_of_weld_types = ['double fillet', 'single fillet', 'double partial pen', 'single partial pen', 'full pen']
    w_type = st.selectbox('Weld type', list_of_weld_types, index=0, key=1, help=None)
    a = st.number_input('$a (mm)$', min_value=3, value=6, step=1, key=2, help='''
            Weld size. For fillet welds:\n
            $\\leq7mm$ -> 1x pass\n
            $\\leq9mm$ -> 2x pass\n
            $\\leq11mm$ -> 4x pass\n
            ''')
    tpl1 = st.number_input('$t_{pl1} (mm)$', min_value=0, value=15, step=1, key=3, help="Thickness of welded plate")
    tpl2 = st.number_input('$t_{pl2} (mm)$', min_value=0, value=15, step=1, key=4, help="Thickness of receiver plate")
    fu = st.number_input('$f_u (MPa)$', min_value=0, value=470, step=1, key=5, help="$f_u$ of welded plates (470MPa for S355)")
    beta_w = st.number_input('$\\beta_w$', min_value=0.00, value=0.90, step=0.01, key=6, help='''
        S235 -> $\\beta_w$ = 0.80\n
        S275 -> $\\beta_w$ = 0.85\n
        S355 -> $\\beta_w$ = 0.90\n
        S420 -> $\\beta_w$ = 0.10\n
        S460 -> $\\beta_w$ = 0.10\n
        ''')
    g_M2 = st.number_input('$\\gamma_{M2}$', min_value=0.00, value=1.25, step=0.01, key=7, help=None)


# Calculated Values
with st.expander("Calculated values"):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        fw_perp = 0.9 * fu / g_M2
        st.latex(r'f_{w,\perp}' + f'= {"{:.2f}".format( fw_perp )}' + 'MPa')
    with col2:
        fw_vm = fu / (beta_w * g_M2)
        st.latex(r'f_{w,vm}' + f'= {"{:.2f}".format( fw_vm )}' + 'MPa')

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


# Import forces from wingraf (txt)
with st.expander("Import txt file from wingraf"):
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        data = stringio.readlines()
        forces = f.decode(data)

        forces_by_cut = forces.groupby('cut').first().reset_index()
        list_of_cuts = forces_by_cut['cut'].values.tolist()


        #for each cut :
        cut = 1.1
        df_cut = forces[forces['cut'] == cut]
        list_distances = f.get_distances(cut, df_cut)
        df_cut['d'] = list_distances
        df_cut['w_type'] = w_type
        df_cut['tpl1'] = tpl1
        df_cut['tpl2'] = tpl2
        df_cut['a'] = a
        calc_cut = f.calculate(df_cut, fw_vm, fw_perp)
        st.pyplot(fig=f.make_plot(calc_cut), clear_figure=None, use_container_width=True)

