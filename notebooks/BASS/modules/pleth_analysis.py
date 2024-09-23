from bass import analyze, samp_entropy_wrapper, poincare_batch, histent_wrapper, moving_statistics

import numpy as np
from numpy import NaN, Inf, arange, isscalar, asarray, array
import pandas as pd
import time as t
import sys
import os

# The pleth module. Runs analysis of all aspects pertaining to pleth-signal analysis.
def pleth_analysis(Data, Settings, Results):
    pd.options.display.max_columns = 25
    
    # Run detection
    Data, Settings, Results = analyze(Data, Settings, Results)
    
    # New pleth stuff
    key = Settings['Label']
    start_time = t.time()  # Changed from t.clock() to t.time()
    
    # Create results table
    pleth = pd.DataFrame(columns=['Breaths', 'Recording Length (s)', 'Mean Breath Rate', 
                                  'AUC', 'AUC STD', 'Insp Time mean', 'Insp Time std',
                                  'Exp Time mean', 'Exp Time std', 'TTotal mean', 'TTotal std',
                                  'Apnea Count Per Minute', 'TI Samp Ent', 'TE Samp Ent', 'TTot Samp Ent',
                                  'TI Hist Ent', 'TE Hist Ent', 'TTot Hist Ent'], index=[key])
    
    event_type = 'Bursts'
    
    # Total number of breaths
    try:
        pleth.loc[key, 'Breaths'] = Results['Bursts'][key]['Burst Duration'].count()
    except:
        pleth.loc[key, 'Breaths'] = NaN
    
    # Length    
    try:
        t_sec = Data['trans'].index[-1] - Data['trans'].index[0]
        pleth.loc[key, 'Recording Length (s)'] = t_sec
    except:
        pleth.loc[key, 'Recording Length (s)'] = NaN
    
    # Breath rate   
    try:
        t_min = t_sec / 60
        pleth.loc[key, 'Mean Breath Rate'] = pleth.loc[key, 'Breaths'] / t_min
    except:
        pleth.loc[key, 'Mean Breath Rate'] = NaN
    
    # Area under the curve
    try:
        pleth.loc[key, 'AUC'] = Results['Bursts'][key]['Burst Area'].mean()
        pleth.loc[key, 'AUC STD'] = Results['Bursts'][key]['Burst Area'].std()
    except:
        pleth.loc[key, 'AUC'] = NaN
        pleth.loc[key, 'AUC STD'] = NaN
    
    # Inspiration    
    try:
        pleth.loc[key, 'Insp Time mean'] = Results['Bursts'][key]['Burst Duration'].mean()
        pleth.loc[key, 'Insp Time std'] = Results['Bursts'][key]['Burst Duration'].std()
    except:
        pleth.loc[key, 'Insp Time mean'] = NaN
        pleth.loc[key, 'Insp Time std'] = NaN
    
    # Expiration
    try:
        pleth.loc[key, 'Exp Time mean'] = Results['Bursts'][key]['Interburst Interval'].mean()
        pleth.loc[key, 'Exp Time std'] = Results['Bursts'][key]['Interburst Interval'].std()
    except:
        pleth.loc[key, 'Exp Time mean'] = NaN
        pleth.loc[key, 'Exp Time std'] = NaN
    
    # TTotal
    try:
        pleth.loc[key, 'TTotal mean'] = Results['Bursts'][key]['Total Cycle Time'].mean()
        pleth.loc[key, 'TTotal std'] = Results['Bursts'][key]['Total Cycle Time'].std()
    except:
        pleth.loc[key, 'TTotal mean'] = NaN
        pleth.loc[key, 'TTotal std'] = NaN
    
    # Apnea
    timedifflst = []
    
    for i in range(len(Results['Bursts'][key]['Burst Start']) - 1):
        timediff = Results['Bursts'][key]['Burst Start'].iloc[i + 1] - Results['Bursts'][key]['Burst Start'].iloc[i]
        timedifflst.append(timediff)
    
    apnea_index = np.array(timedifflst).mean()
    apnea_thresh = 1.20 * apnea_index
    apnea_count = list(np.array(timedifflst) > apnea_thresh).count(True)
    apneas_per_minute = apnea_count / pleth.loc[key, 'Recording Length (s)'] * 60
    pleth.loc[key, 'Apnea Count Per Minute'] = apneas_per_minute
    
    # Shannon Entropy
    try:
        meas = 'Burst Duration'
        Results = samp_entropy_wrapper(event_type, meas, Data, Settings, Results)
        pleth.loc[key, 'TI Samp Ent'] = float(Results['Sample Entropy'][meas])
    except:
        pleth.loc[key, 'TI Samp Ent'] = NaN
    
    try:
        meas = 'Interburst Interval'
        Results = samp_entropy_wrapper(event_type, meas, Data, Settings, Results)
        pleth.loc[key, 'TE Samp Ent'] = float(Results['Sample Entropy'][meas])
    except:
        pleth.loc[key, 'TE Samp Ent'] = NaN
    
    try:
        meas = 'Total Cycle Time'
        Results = samp_entropy_wrapper(event_type, meas, Data, Settings, Results)
        pleth.loc[key, 'TTot Samp Ent'] = float(Results['Sample Entropy'][meas])
    except:
        pleth.loc[key, 'TTot Samp Ent'] = NaN
    
    # Poincare
    try:
        meas = 'Total Cycle Time'
        Results = poincare_batch(event_type, meas, Data, Settings, Results)
        meas = 'Burst Duration'
        Results = poincare_batch(event_type, meas, Data, Settings, Results)
        meas = 'Interburst Interval'
        Results = poincare_batch(event_type, meas, Data, Settings, Results)
    except:
        print("Poincare Failed")
    
    # Hist Ent
    try:
        meas = 'all'
        Results = histent_wrapper(event_type, meas, Data, Settings, Results)
        pleth.loc[key, 'TI Hist Ent'] = float(Results['Histogram Entropy']['Burst Duration'])
        pleth.loc[key, 'TE Hist Ent'] = float(Results['Histogram Entropy']['Interburst Interval'])
        pleth.loc[key, 'TTot Hist Ent'] = float(Results['Histogram Entropy']['Total Cycle Time'])
    except:
        print("Histogram Entropy Failed")
        pleth.loc[key, 'TI Hist Ent'] = NaN
        pleth.loc[key, 'TE Hist Ent'] = NaN
        pleth.loc[key, 'TTot Hist Ent'] = NaN
    
    try:
        # Moving Stats
        event_type = 'Bursts'
        meas = 'Total Cycle Time'
        window = 30  # seconds
        Results = moving_statistics(event_type, meas, window, Data, Settings, Results)
    except:
        pass
    
    pleth.to_csv(os.path.join(Settings['Output Folder'], f"{Settings['Label']}_Pleth.csv"))
    
    end_time = t.time()  # Changed from t.clock() to t.time()
    print(f'Pleth Analysis Complete: {np.round(end_time - start_time, 4)} sec')
    
    return pleth