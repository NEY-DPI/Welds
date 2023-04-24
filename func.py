import pandas as pd


def decode(data):
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
    df_M = pd.DataFrame(results1[1], columns=['cut', 'quad', 'seg', 'x', 'y', 'z', 'M'])
    df_Vt = pd.DataFrame(results1[2], columns=['cut', 'quad', 'seg', 'x', 'y', 'z', 'Vt'])
    df_Vl = pd.DataFrame(results1[3], columns=['cut', 'quad', 'seg', 'x', 'y', 'z', 'Vl'])
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


