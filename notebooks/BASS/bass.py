from __future__ import absolute_import, print_function
import os
from bass_functions import *
from modules.pleth_analysis import pleth_analysis
from modules.ekg_analysis import ekg_analysis

class BASS_Dataset:
    '''
    Imports dataset as an object
    
    Attributes
    ----------
    Batch: list
        Contains all instances of the BASS_Dataset object in order to be referenced by the global runBatch function.
    Data: dict
        Instance data
    Settings: dict
        Instance settings
    Results: dict
        Instance results
    
    Methods
    -------
    run_analysis(settings=None, analysis_module=None):
        Highest level of the object-oriented analysis pipeline. First syncs the settings of all BASS_Dataset objects 
        (stored in Batch), then runs the specified analysis module on each one.
        
    Parameters
    ----------
    inputLocation: str
        Path to the input directory.
    label: str
        Label for the dataset.
    outputLocation: str
        Path to the output directory.
    fileType: str, default='Plain'
        Type of the file.
    timeScale: str, default='seconds'
        Time scale used in the data.
    
    Required Input
    --------------
    inputLocation, label, outputLocation
    
    Notes
    ------
    Analysis must be called after the object is initialized and Settings are added if the Settings are to be added manually
    (not via the interactive check and load settings function). Analysis runs according to batch-oriented protocol and
    is specific to the analysis module determined by the "analysis_module" parameter.
    '''
    
    Batch = []
    
    def __init__(self, inputDir, fileName, outputDir, fileType='Plain', timeScale='seconds'):
        self.Data = {}
        self.Settings = {}
        self.Results = {}        
        self.Settings['folder'] = inputDir
        self.Settings['Label'] = fileName
        self.Settings['Output Folder'] = outputDir
        self.Settings['File Type'] = fileType
        self.Settings['Time Scale'] = timeScale
        BASS_Dataset.Batch.append(self) # Appends each object instance into a list of datasets
        print(f"\n############   {self.Settings['Label']}   ############\n") # Display object instance label
        self.Data, self.Settings = load_wrapper(self.Data, self.Settings) # Loads data and settings
        
    def run_analysis(self, analysis_mod, settings=None, batch=True):
        '''
        Runs in either single (batch=False) or batch mode. Assuming batch mode, this function first syncs settings of each dataset within 
        BASS_Dataset.Batch to the entered parameter "settings", then runs analysis on each instance within Batch.
        
        Parameters
        ----------
        analysis_mod: str
            The name of the analysis module to be used.
        settings: dict or str, optional
            Can be a dictionary of settings or the path to a settings file (default is None, which uses self.Settings).
        batch: bool, default=True
            Determines if the analysis is performed on only the self-instance or as a batch on all object instances.
        
        Returns
        -------
        None
        '''
        
        # Run batch if "batch" is True
        if batch:
            # Sets default "settings" to self.Settings
            if settings is None:
                settings = self.Settings
            
            for dataset in BASS_Dataset.Batch:
                # Sync settings to those of a specific object instance
                try:
                    exclusion_list = ['plots folder', 'folder', 
                                      'Sample Rate (s/frame)', 'Output Folder', 
                                      'Baseline', 'Baseline-Rolling', 'Settings File', 'Time Scale',
                                      'Label', 'File Type', 'HDF Key', 'HDF Channel']
                    
                    for key in settings.keys():
                        if key not in exclusion_list:
                            dataset.Settings[key] = settings[key]
                
                except Exception as e:
                    print(f"Error syncing settings: {e}")
                    dataset.Settings['Settings File'] = settings
                    dataset.Settings = load_settings(dataset.Settings)
                
                print(f"\n############   {dataset.Settings['Label']}   ############\n") # Display object instance label
                
                if analysis_mod == 'pleth':
                    pleth_analysis(dataset.Data, dataset.Settings, dataset.Results)
                elif analysis_mod == 'ekg':
                    ekg_analysis(dataset.Data, dataset.Settings, dataset.Results)
        
        # Run a single object if "batch" is False
        else:
            if settings is not None:
                # Sync settings to those of a specific object instance
                try:
                    exclusion_list = ['plots folder', 'folder', 
                                      'Sample Rate (s/frame)', 'Output Folder', 
                                      'Baseline', 'Baseline-Rolling', 'Settings File', 'Time Scale',
                                      'Label', 'File Type', 'HDF Key', 'HDF Channel']
                    
                    for key in settings.keys():
                        if key not in exclusion_list:
                            self.Settings[key] = settings[key]
                
                except Exception as e:
                    print(f"Error syncing settings: {e}")
                    self.Settings['Settings File'] = settings
                    self.Settings = load_settings(self.Settings)
                
            if analysis_mod == 'pleth':
                pleth_analysis(self.Data, self.Settings, self.Results)
            elif analysis_mod == 'ekg':
                ekg_analysis(self.Data, self.Settings, self.Results)


# END OF CODE
print("BASS ready!")