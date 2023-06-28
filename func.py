import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
from matplotlib.ticker import (AutoMinorLocator, MultipleLocator)
from io import StringIO
import streamlit as st


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


def decode(data, calc_mode):
    appending = False
    list = []
    results = []

    for line in data:
        if not appending:
            if "no." in line:
                list = []
                appending = True
        else:
            if len(line.split()) < 2:
                appending = False
                results.append(list)
            else:
                list.append(line)
    if appending:
        appending = False
        results.append(list)

    results1 = []
    for list in results:
        list1 = []
        for line in list:
            list1.append([float(x) for x in line.split()])
        results1.append(list1)

    df_N = pd.DataFrame(results1[0], columns=['cut', 'quad', 'seg', 'x', 'y', 'z', 'N'])
    if calc_mode == 'Max per weld':
        df_N['N'] = df_N['N'].abs()
        df_N_max = df_N.groupby(['cut', 'quad']).max().reset_index()
        df_N_mean = df_N.groupby(['cut', 'quad']).mean().reset_index()
        df_N = df_N_mean
        df_N['N'] = df_N_max['N']

    df_M = pd.DataFrame(results1[1], columns=['cut', 'quad', 'seg', 'x', 'y', 'z', 'M'])
    if calc_mode == 'Max per weld':
        df_M['M'] = df_M['M'].abs()
        df_M = df_M.groupby(['cut', 'quad']).max().reset_index()

    df_Vt = pd.DataFrame(results1[2], columns=['cut', 'quad', 'seg', 'x', 'y', 'z', 'Vt'])
    if calc_mode == 'Max per weld':
        df_Vt['Vt'] = df_Vt['Vt'].abs()
        df_Vt = df_Vt.groupby(['cut', 'quad']).max().reset_index()

    df_Vl = pd.DataFrame(results1[3], columns=['cut', 'quad', 'seg', 'x', 'y', 'z', 'Vl'])
    if calc_mode == 'Max per weld':
        df_Vl['Vl'] = df_Vl['Vl'].abs()
        df_Vl = df_Vl.groupby(['cut', 'quad']).max().reset_index()

    df = pd.DataFrame()

    df['cut'] = df_N['cut']
    df['x'] = df_N['x']
    df['y'] = df_N['y']
    df['z'] = df_N['z']
    df['N'] = df_N['N']
    df['M'] = df_M['M']
    df['Vt'] = df_Vt['Vt']
    df['Vl'] = df_Vl['Vl']
    return df


def get_forces(mode, data, calc_mode):
    if mode == 'From Wingraf':
        if data is not None:
            stringio = StringIO(data.getvalue().decode("utf-8"))
            read_data = stringio.readlines()
            forces = decode(read_data, calc_mode)

            cut_list = forces['cut'].tolist()
            cut_list2 = []
            for item in cut_list:
                item2 = str(item)
                item3 = item2.split(".")
                item4 = item3[0]
                cut_list2.append(item4)
            forces['cut'] = cut_list2
            return forces
    elif mode == 'From Excel':
        if data is not None:
            #TODO
            return


def get_distances(df_cut):
    list_x = df_cut['x'].values.tolist()
    list_y = df_cut['y'].values.tolist()
    list_z = df_cut['z'].values.tolist()
    list_d = []
    for i in range(len(list_x)):
        list_d.append(((list_x[i] - list_x[0]) ** 2 +
                       (list_y[i] - list_y[0]) ** 2 +
                       (list_z[i] - list_z[0]) ** 2) ** 0.5)
    max_d = max(list_d)
    list_d = [x / max_d for x in list_d]
    return list_d


def get_distances_per_weld(df):
    df_sort = df.sort_values(by=['x'])
    x0 = df_sort['x'].values.tolist()[0]
    y0 = df_sort['y'].values.tolist()[0]
    z0 = df_sort['z'].values.tolist()[0]
    list_x = df['x'].values.tolist()
    list_y = df['y'].values.tolist()
    list_z = df['z'].values.tolist()
    list_d = []
    for i in range(len(list_x)):
        list_d.append(((list_x[i] - x0) ** 2 +
                       (list_y[i] - y0) ** 2 +
                       (list_z[i] - z0) ** 2) ** 0.5)
    max_d = max(list_d)
    list_d = [x / max_d for x in list_d]
    return list_d


def calculate(df):
    list_d = df['d'].values.tolist()
    w_type = df['w_type'].values.tolist()
    tpl1 = df['tpl1'].values.tolist()
    tpl2 = df['tpl2'].values.tolist()
    a = df['a'].values.tolist()
    fw_vm = df['fw_vm'].values.tolist()
    fw_perp = df['fw_perp'].values.tolist()
    N = df['N'].abs().values.tolist()
    M = df['M'].abs().values.tolist()
    Vt = df['Vt'].abs().values.tolist()
    Vl = df['Vl'].abs().values.tolist()

    # eccentricity (mm)
    e = []
    for x in range(len(list_d)):
        if w_type[x] == 'single fillet':
            e.append(tpl1[x]/2 + a[x]/2)
        elif w_type[x] == 'single partial pen':
            e.append(tpl1[x]/2 - a[x]/2)
        else:
            e.append(0)
    df.loc[:, 'e'] = e

    # M due to e (kNm/m)
    M_e = []
    for x in range(len(list_d)):
        M_e.append(N[x] * e[x] / 1000)
    df.loc[:, 'M_e'] = M_e

    # Sigma_perp_N (MPa)
    sig_perp_N = []
    for x in range(len(list_d)):
        if w_type[x] == 'double fillet':
            sig_perp_N.append(0.707 * N[x] / (2 * a[x]))
        elif w_type[x] == 'single fillet':
            sig_perp_N.append(0.707 * N[x] / a[x])
        elif w_type[x] == 'double partial pen':
            sig_perp_N.append(N[x] / (2 * a[x]))
        elif w_type[x] == 'single partial pen':
            sig_perp_N.append(N[x] / (a[x]))
        elif w_type[x] == 'full pen':
            sig_perp_N.append(N[x] / (tpl1[x]))
    df.loc[:, 'sig_perp_N (MPa)'] = sig_perp_N

    # Sigma_perp_M (MPa)
    sig_perp_M = []
    for x in range(len(list_d)):
        if w_type[x] == 'double fillet':
            sig_perp_M.append(0.707 * M[x] * 1000 / ((tpl1[x] + 2 * (a[x]/(0.707*3))) * a[x]))
        elif w_type[x] == 'single fillet':
            sig_perp_M.append(0.707 * M[x] * 1000 / (a[x]**2 / 6))
        elif w_type[x] == 'double partial pen':
            sig_perp_M.append(M[x] * 1000 / ((tpl1[x]-a[x]) * a[x]))
        elif w_type[x] == 'single partial pen':
            sig_perp_M.append(M[x] * 1000 / (a[x]**2 / 6))
        elif w_type[x] == 'full pen':
            sig_perp_M.append(M[x] * 1000 / (tpl1[x]**2 / 6))
    df.loc[:, 'sig_perp_M (MPa)'] = sig_perp_M

    # Sigma_perp_Me (MPa)
    sig_perp_Me = []
    for x in range(len(list_d)):
        if w_type[x] == 'double fillet':
            sig_perp_Me.append(0.707 * M_e[x] * 1000 / ((tpl1[x] + 2 * (a[x]/(0.707*3))) * a[x]))
        elif w_type[x] == 'single fillet':
            sig_perp_Me.append(0.707 * M_e[x] * 1000 / (a[x] ** 2 / 6))
        elif w_type[x] == 'double partial pen':
            sig_perp_Me.append(M_e[x] * 1000 / ((tpl1[x] - a[x]) * a[x]))
        elif w_type[x] == 'single partial pen':
            sig_perp_Me.append(M_e[x] * 1000 / (a[x] ** 2 / 6))
        elif w_type[x] == 'full pen':
            sig_perp_Me.append(M_e[x] * 1000 / (tpl1[x] ** 2 / 6))
    df.loc[:, 'sig_perp_Me (MPa)'] = sig_perp_Me

    # Sigma_perp_Vt (MPa)
    sig_perp_Vt = []
    for x in range(len(list_d)):
        if w_type[x] == 'double fillet':
            sig_perp_Vt.append(0.707 * Vt[x] / (2 * a[x]))
        elif w_type[x] == 'single fillet':
            sig_perp_Vt.append(0.707 * Vt[x] / a[x])
        else:
            sig_perp_Vt.append(0)
    df.loc[:, 'sig_perp_Vt (MPa)'] = sig_perp_Vt

    # Sigma_perp (MPa)
    sig_perp = []
    for x in range(len(list_d)):
        sig_perp.append(sig_perp_N[x] + sig_perp_M[x] + sig_perp_Me[x] + sig_perp_Vt[x])
    df.loc[:, 'sig_perp (MPa)'] = sig_perp

    # Tau_perp (MPa)
    tau_perp = []
    for x in range(len(list_d)):
        if w_type[x] == 'double fillet':
            tau_perp.append(sig_perp[x])
        elif w_type[x] == 'single fillet':
            tau_perp.append(sig_perp[x])
        elif w_type[x] == 'double partial pen':
            tau_perp.append(Vt[x] / (2 * a[x]))
        elif w_type[x] == 'single partial pen':
            tau_perp.append(Vt[x] / (a[x]))
        elif w_type[x] == 'full pen':
            tau_perp.append(Vt[x] / tpl1[x])
    df.loc[:, 'tau_perp (MPa)'] = tau_perp

    # Tau_long (MPa)
    tau_long = []
    for x in range(len(list_d)):
        if w_type[x] == 'double fillet':
            tau_long.append(Vl[x] / (2 * a[x]))
        elif w_type[x] == 'single fillet':
            tau_long.append(Vl[x] / (a[x]))
        elif w_type[x] == 'double partial pen':
            tau_long.append(Vl[x] / (2 * a[x]))
        elif w_type[x] == 'single partial pen':
            tau_long.append(Vl[x] / (a[x]))
        elif w_type[x] == 'full pen':
            tau_long.append(Vl[x] / (tpl1[x]))
    df.loc[:, 'tau_long (MPa)'] = tau_long

    # VM stress (MPa)
    sig_vm = []
    for x in range(len(list_d)):
        sig_vm.append((sig_perp[x]**2 + 3 * (tau_perp[x]**2 + tau_long[x]**2)) ** 0.5)
    df.loc[:, 'sig_vm (MPa)'] = sig_vm

    # uc perp (-)
    uc_perp = []
    for x in range(len(list_d)):
        uc_perp.append(sig_perp[x] / fw_perp[x])
    df.loc[:, 'uc_perp (-)'] = uc_perp

    # uc vm (-)
    uc_vm = []
    for x in range(len(list_d)):
        uc_vm.append(sig_vm[x] / fw_vm[x])
    df.loc[:, 'uc_vm (-)'] = uc_vm

    # uc (-)
    uc = []
    for x in range(len(list_d)):
        uc.append(max(uc_perp[x], uc_vm[x]))
    df.loc[:, 'uc (-)'] = uc

    return df


def calc_req_a(df, weld):
    df_req_a = df.copy().reset_index()
    df_req_a['a'] = 3
    df_req_a = calculate(df_req_a)

    while df_req_a['uc (-)'].max() > 1:
        for i in range(len(df_req_a['d'].values.tolist())):
            if df_req_a['uc (-)'][i] > 1:
                df_req_a['a'][i] += 1
        df_req_a = calculate(df_req_a)
    return df_req_a


def make_plot(list_of_df, list_of_df_req, display_cut, data_to_display, show_req):
    if 'uc' in data_to_display:
        y_limit = 1
    else:
        y_limit = 500

    plt.figure(figsize=(14, 8))
    ax1 = plt.gca()
    ax2 = ax1.twinx()
    ax1.set_ylim(0, 40)
    ax2.set_ylim(0, y_limit)
    ax1.set_xlim(0, 1)

    ax1.xaxis.set_major_locator(MultipleLocator(0.05))
    ax1.yaxis.set_major_locator(MultipleLocator(5))
    ax1.yaxis.set_minor_locator(MultipleLocator(1))
    ax2.yaxis.set_major_locator(MultipleLocator(0.05*y_limit))
    ax1.grid(which='major', color='#CCCCCC', linestyle=':')
    ax2.grid(which='major', color='#CCCCCC', linestyle='--')
    ax1.grid(which='minor', color='#CCCCCC', linestyle=':')

    ax1.plot(list_of_df[0]['d'][:], list_of_df[0]['tpl1'][:], color='blue', linestyle='--', linewidth=1,
             label=f't welded plate (mm)', marker='.')
    ax1.plot(list_of_df[0]['d'][:], list_of_df[0]['tpl2'][:], color='green', linestyle='--', linewidth=1,
             label=f't receiver plate (mm)', marker='.')

    if show_req == 'Show required weld size':
        for i in range(len(display_cut)):
            if display_cut[i]:
                df = list_of_df_req[i]
                ax1.plot(df['d'][:], df['a'][:], color='red', label='weld size (mm)',
                         marker='.')
                ax2.plot(df['d'][:], df[data_to_display][:], color='black', linewidth=1,
                         label=f'{data_to_display} cut {df["cut"].values[0]}', marker='.')
    else:
        ax1.plot(list_of_df[0]['d'][:], list_of_df[0]['a'][:], color='red', label='weld size (mm)', marker='.')
        for i in range(len(display_cut)):
            if display_cut[i]:
                df = list_of_df[i]
                ax2.plot(df['d'][:], df[data_to_display][:], color='black', linewidth=1,
                         label=f'{data_to_display} cut {df["cut"].values[0]}', marker='.')

    ax1.set_xlabel('x (m)')
    ax1.set_ylabel('(mm)')
    ax2.set_ylabel(data_to_display)
    ax1.legend(loc='upper left', bbox_to_anchor=(0.1, 1), framealpha=1, facecolor='white')
    ax2.legend(loc='best', bbox_to_anchor=(0.9, 1), framealpha=1, facecolor='white')

    ax1.set_axisbelow(True)
    ax2.set_axisbelow(True)

    return plt


def make_plot_per_weld(df, df_req_a, data_to_display, show_req):
    if 'uc' in data_to_display:
        y_limit = 1
    else:
        y_limit = 500

    plt.figure(figsize=(14, 8))
    ax1 = plt.gca()
    ax2 = ax1.twinx()
    ax1.set_ylim(0, 40)
    ax2.set_ylim(0, y_limit)
    ax1.set_xlim(0, 1)

    ax1.xaxis.set_major_locator(MultipleLocator(0.05))
    ax1.yaxis.set_major_locator(MultipleLocator(5))
    ax1.yaxis.set_minor_locator(MultipleLocator(1))
    ax2.yaxis.set_major_locator(MultipleLocator(0.05*y_limit))
    ax1.grid(which='major', color='#CCCCCC', linestyle=':')
    ax2.grid(which='major', color='#CCCCCC', linestyle='--')
    ax1.grid(which='minor', color='#CCCCCC', linestyle=':')

    ax1.plot(df['d'][:], df['tpl1'][:], color='blue', linestyle='--', linewidth=1,
             label=f't welded plate (mm)', marker='.')
    ax1.plot(df['d'][:], df['tpl2'][:], color='green', linestyle='--', linewidth=1,
             label=f't receiver plate (mm)', marker='.')

    if show_req == 'Show required weld size':
        ax1.plot(df['d'][:], df_req_a['a'][:], color='red', label='required weld size (mm)', marker='.')
        ax2.plot(df['d'][:], df_req_a[data_to_display][:], color='black', linewidth=1, label=f'{data_to_display}', marker='.')
    else:
        ax1.plot(df['d'][:], df['a'][:], color='red', label='weld size (mm)', marker='.')
        ax2.plot(df['d'][:], df[data_to_display][:], color='black', linewidth=1, label=f'{data_to_display}', marker='.')

    ax1.set_xlabel('x (m)')
    ax1.set_ylabel('(mm)')
    ax2.set_ylabel(data_to_display)
    ax1.legend(loc='upper left', framealpha=1, facecolor='white')
    ax2.legend(loc='best', framealpha=1, facecolor='white')

    ax1.set_axisbelow(True)
    ax2.set_axisbelow(True)

    return plt


def calc_graph(forces, weld, calc_mode):
    if forces is None:
        return
    if calc_mode == 'Values along weld':
        forces_by_cut = forces.groupby('cut').first().reset_index()
        list_of_cuts = forces_by_cut['cut'].values.tolist()
        list_of_df = []
        for cut in list_of_cuts:
            df_cut = forces[forces['cut'] == cut]
            list_distances = get_distances(df_cut)
            df_cut['d'] = list_distances
            df_cut = df_cut.sort_values(by=['d']).reset_index()
            if isinstance(weld, pd.DataFrame):
                df_cut['w_type'] = ''
                df_cut['tpl1'] = 0
                df_cut['tpl2'] = 0
                df_cut['a'] = 0
                df_cut['beta_w'] = 0
                df_cut['fu'] = 0
                df_cut['g_M2'] = 0
                df_cut['fw_vm'] = 0
                df_cut['fw_perp'] = 0
                for j in range(len(list_distances)):
                    checking = True
                    i = 0
                    chosen_i = 0
                    while checking:
                        if list_distances[j] <= weld['x'][i]:
                            chosen_i = i
                            checking = False
                        else:
                            i += 1
                    df_cut['w_type'][j] = weld['w_type'][chosen_i]
                    df_cut['tpl1'][j] = weld['tpl1'][chosen_i]
                    df_cut['tpl2'][j] = weld['tpl2'][chosen_i]
                    df_cut['a'][j] = weld['a'][chosen_i]
                    df_cut['beta_w'][j] = weld['beta_w'][chosen_i]
                    df_cut['fu'][j] = weld['fu'][chosen_i]
                    df_cut['g_M2'][j] = weld['g_M2'][chosen_i]
                    df_cut['fw_vm'][j] = weld['fw_vm'][chosen_i]
                    df_cut['fw_perp'][j] = weld['fw_perp'][chosen_i]
            else:
                df_cut['w_type'] = weld['w_type']
                df_cut['tpl1'] = weld['tpl1']
                df_cut['tpl2'] = weld['tpl2']
                df_cut['a'] = weld['a']
                df_cut['beta_w'] = weld['beta_w']
                df_cut['fu'] = weld['fu']
                df_cut['g_M2'] = weld['g_M2']
                df_cut['fw_vm'] = weld['fw_vm']
                df_cut['fw_perp'] = weld['fw_perp']

            calc_cut = calculate(df_cut)
            list_of_df.append(calc_cut)
    elif calc_mode == 'Max per weld':
        forces_by_cut = forces.groupby('cut').first().reset_index()
        list_of_cuts = forces_by_cut['cut'].values.tolist()
        list_of_df = []
        df_mean = forces.groupby('cut').mean(numeric_only=True)
        df_max = forces.groupby(['cut']).max()
        df_new = df_max
        df_new['x'] = df_mean['x']
        df_new['y'] = df_mean['y']
        df_new['z'] = df_mean['z']
        list_distances = get_distances_per_weld(df_new)
        df_new['d'] = list_distances
        df_cut = df_new.sort_values(by=['d']).reset_index()

        df_cut['w_type'] = weld['w_type']
        df_cut['tpl1'] = weld['tpl1']
        df_cut['tpl2'] = weld['tpl2']
        df_cut['a'] = weld['a']
        df_cut['beta_w'] = weld['beta_w']
        df_cut['fu'] = weld['fu']
        df_cut['g_M2'] = weld['g_M2']
        df_cut['fw_vm'] = weld['fw_vm']
        df_cut['fw_perp'] = weld['fw_perp']

        calc_cut = calculate(df_cut)
        list_of_df.append(calc_cut)

    st.markdown("Select what to display")
    col1, col2 = st.columns(2)
    with col1:
        data_to_display = st.selectbox(
            'Select what to display',
            ('uc (-)', 'uc_vm (-)', 'uc_perp (-)', 'sig_vm (MPa)', 'tau_long (MPa)', 'tau_perp (MPa)',
             'sig_perp (MPa)', 'sig_perp_Vt (MPa)', 'sig_perp_Me (MPa)', 'sig_perp_N (MPa)'),
            label_visibility="collapsed", key="data_to_display")
    with col2:
        show_req = st.selectbox(
            'Show required',
            ('Show required weld size', 'Show input weld size'),
            label_visibility="collapsed", key="show_req")

    if calc_mode == 'Max per weld':
        list_of_df_req = []
        for df in list_of_df:
            df_req_a = calc_req_a(df, weld)
            list_of_df_req.append(df_req_a)

        df = pd.concat(list_of_df)
        df_req_a = pd.concat(list_of_df_req)

        df_mean = df.groupby('cut').mean(numeric_only=True)
        df_max = df.groupby(['cut']).max()
        df_new = df_max
        df_new['x'] = df_mean['x']
        df_new['y'] = df_mean['y']
        df_new['z'] = df_mean['z']
        list_distances = get_distances_per_weld(df_new)
        df_new['d'] = list_distances

        df_req_a = df_req_a.groupby(['cut']).max()
        df_req_a['x'] = df_mean['x']
        df_req_a['y'] = df_mean['y']
        df_req_a['z'] = df_mean['z']
        df_req_a['d'] = list_distances

        df_new = df_new.sort_values(by=['d']).reset_index()
        df_req_a = df_req_a.sort_values(by=['d']).reset_index()

        st.pyplot(fig=make_plot_per_weld(df_new, df_req_a, data_to_display, show_req), clear_figure=None,
                  use_container_width=True)

    elif calc_mode == 'Values along weld':
        n_col = 8
        cols = st.columns(n_col)
        display_cut = []
        for i in range(len(list_of_cuts)):
            with cols[i % n_col]:
                display_cut.append(st.checkbox(f'{list_of_cuts[i]}', key=10 + i, value=True))

        list_of_df_req = []
        for df in list_of_df:
            df_req_a = calc_req_a(df, weld)
            list_of_df_req.append(df_req_a)

        st.pyplot(fig=make_plot(list_of_df, list_of_df_req, display_cut, data_to_display, show_req), clear_figure=None,
                  use_container_width=True)



##
def make_plot_man(df):
    list_lc = df['d'][:].values.tolist()
    count = len(list_lc)
    list_lc_i = range(count)

    plt.figure(figsize=(14, 8))
    ax1 = plt.gca()
    ax2 = ax1.twinx()
    ax1.set_ylim(0, 40)
    ax2.set_ylim(0, 1)
    ax1.set_xlim(-1, count)

    ax1.xaxis.set_major_locator(MultipleLocator(1))
    ax1.yaxis.set_major_locator(MultipleLocator(5))
    ax1.yaxis.set_minor_locator(MultipleLocator(1))
    ax2.yaxis.set_major_locator(MultipleLocator(0.05))
    ax1.grid(which='major', color='#CCCCCC', linestyle=':')
    ax2.grid(which='major', color='#CCCCCC', linestyle='--')
    ax1.grid(which='minor', color='#CCCCCC', linestyle=':')

    width = 0.1
    offset = width * 0
    list = [x + offset for x in list_lc_i]
    ax1.bar(list, df['tpl1'][:], color='blue',
            label=f't welded plate (mm)', width=width)
    offset = width * 1
    list = [x + offset for x in list_lc_i]
    ax1.bar(list, df['tpl2'][:], color='green',
            label=f't receiver plate (mm)', width=width)
    offset = width * 2
    list = [x + offset for x in list_lc_i]
    ax1.bar(list, df['a'][:], color='red',
            label='weld size (mm)', width=width)
    offset = width * 3
    list = [x + offset for x in list_lc_i]
    ax2.bar(list, df['uc (-)'][:], color='black', label='uc (-)', width=width)

    ax1.set_xlabel('x (m)')
    ax1.set_ylabel('(mm)')
    ax2.set_ylabel('uc (-)')
    ax1.legend(loc='upper left', framealpha=1, facecolor='white')
    ax2.legend(loc='best', framealpha=1, facecolor='white')

    ax1.set_axisbelow(True)
    ax2.set_axisbelow(True)

    return plt

