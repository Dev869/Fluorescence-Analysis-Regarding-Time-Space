from bass import analyze, samp_entropy_wrapper, poincare_batch, histent_wrapper, moving_statistics, psd_event, ap_entropy_wrapper

import numpy as np
from numpy import NaN, Inf, arange, isscalar, asarray, array
import pandas as pd
import time as t
import sys
import os

# The ekg module. Runs analysis of all aspects pertaining to ekg-signal analysis. Modified from the pleth_analysis module by Ryan Thorpe.

# Change 'breaths' to beats and breath-rate to heart-rate

def ekg_analysis(Data, Settings, Results):
    pd.options.display.max_columns = 25
    
    # Run detection
    Data, Settings, Results = analyze(Data, Settings, Results)
    
    # New ekg stuff
    key = Settings['Label']
    start_time = t.time()  # Changed from t.clock() to t.time()
    
    # Create results table
    ekg = pd.DataFrame(columns=['Heartbeats', 'Recording Length (s)', 'Mean Heartrate', 
                                'TTotal mean', 'TTotal std', 'PA Samp Ent', 
                                'Intv Samp Ent', 'PA Hist Ent', 'Intv Hist Ent'], 
                                index=[key])
    
    event_type = 'Peaks'
    
    # Total number of heartbeats
    try:
        ekg.loc[key, 'Heartbeats'] = Results['Peaks'][key]['Peaks Amplitude'].count()
    except:
        ekg.loc[key, 'Heartbeats'] = NaN
    
    # Length    
    try:
        t_sec = Data['trans'].index[-1] - Data['trans'].index[0]
        ekg.loc[key, 'Recording Length (s)'] = t_sec
    except:
        ekg.loc[key, 'Recording Length (s)'] = NaN
    
    # Heartrate   
    try:
        t_min = t_sec / 60
        ekg.loc[key, 'Mean Heartrate'] = ekg.loc[key, 'Heartbeats'] / t_min
    except:
        ekg.loc[key, 'Mean Heartrate'] = NaN
    
    # TTotal
    try:
        ekg.loc[key, 'TTotal mean'] = Results['Peaks'][key]['Intervals'].mean()
        ekg.loc[key, 'TTotal std'] = Results['Peaks'][key]['Intervals'].std()
    except:
        ekg.loc[key, 'TTotal mean'] = NaN
        ekg.loc[key, 'TTotal std'] = NaN
    
    # Shannon Entropy
    try:
        meas = 'Peaks Amplitude'
        Results = samp_entropy_wrapper(event_type, meas, Data, Settings, Results)
        ekg.loc[key, 'PA Samp Ent'] = float(Results['Sample Entropy'][meas])
    except:
        ekg.loc[key, 'PA Samp Ent'] = NaN
    
    try:
        meas = 'Intervals'
        Results = samp_entropy_wrapper(event_type, meas, Data, Settings, Results)
        ekg.loc[key, 'Intv Samp Ent'] = float(Results['Sample Entropy'][meas])
    except:
        ekg.loc[key, 'Intv Samp Ent'] = NaN
    
    # Poincare
    try:
        meas = 'Peaks Amplitude'
        Results = poincare_batch(event_type, meas, Data, Settings, Results)
        meas = 'Intervals'
        Results = poincare_batch(event_type, meas, Data, Settings, Results)
    except:
        print("Poincare Failed")
    
    # Hist Ent
    try:
        meas = 'all'
        Results = histent_wrapper(event_type, meas, Data, Settings, Results)
        ekg.loc[key, 'PA Hist Ent'] = float(Results['Histogram Entropy']['Peaks Amplitude'])
        ekg.loc[key, 'Intv Hist Ent'] = float(Results['Histogram Entropy']['Intervals'])
    except:
        print("Histogram Entropy Failed")
        ekg.loc[key, 'PA Hist Ent'] = NaN
        ekg.loc[key, 'Intv Hist Ent'] = NaN
    
    try:
        # Moving Stats
        meas = 'Intervals'
        window = 30  # seconds
        Results = moving_statistics(event_type, meas, window, Data, Settings, Results)
    except:
        pass
    
    # Power Spectral Density
    Settings['PSD-Event'] = pd.Series(index=['Hz', 'ULF', 'VLF', 'LF', 'HF', 'dx'])

    Settings['PSD-Event']['Hz'] = 100  # Frequency that the interpolation and PSD are performed with.
    Settings['PSD-Event']['ULF'] = 1  # Max of the range of the ultra low freq band. Range is 0:ulf
    Settings['PSD-Event']['VLF'] = 2  # Max of the range of the very low freq band. Range is ulf:vlf
    Settings['PSD-Event']['LF'] = 5  # Max of the range of the low freq band. Range is vlf:lf
    Settings['PSD-Event']['HF'] = 50  # Max of the range of the high freq band. Range is lf:hf. hf can be no more than (hz/2)
    Settings['PSD-Event']['dx'] = 10  # Segmentation for the area under the curve.
    
    meas = 'Intervals'
    scale = 'raw'
    Results = psd_event(event_type, meas, key, scale, Data, Settings, Results)  # Run PSD-Event analysis and generate graph
    
    Results['PSD-Event'][key]  # Output PSD-Event dataframe
    
    # Approximate Entropy
    meas = 'Intervals'
    Results = ap_entropy_wrapper(event_type, meas, Data, Settings, Results)  # Run approx. ent. analysis and generate graph
    Results['Approximate Entropy']  # Output approx. ent. dataframe
    
    # Save cumulative ekg data
    ekg.to_csv(os.path.join(Settings['Output Folder'], f"{Settings['Label']}_EKG.csv"))
    
    end_time = t.time()  # Changed from t.clock() to t.time()
    
    print(f'Heart Rate Variability Analysis Complete: {np.round(end_time - start_time, 4)} sec')
    
    return ekg