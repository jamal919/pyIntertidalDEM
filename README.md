# Setup and Processing
Step 1: Run depcheck.py for checking for library and dependency error checks

Step 2: Edit directory locaitons inside main.py

	indatadir = $ Directory of Zipped Data
	wkdir = $ Directory of saving unzipped data
	prepdir = $ Directory of saving preprocessed data   
	improcdir= $ Directory of saving processed data
	waterleveldir= $ Directory of water level dat files
	vertrefdir= $ Saving Intermediate data for vertical referencing

Step 3: Change the different processing parameters
Step 4: Run the program with following command
     	./main.py

# Optinal Arguments (default values in parenthesis)
Threshold for creating watermask i.e- data[data>factor*std]=Land (Float): stdfactor = (0.5)
Water Mask creation water blob removal threshold: MaskWater = (10000)
Water Mask creation land blob removal threshold: MaskLand = (5000) 
Specialized testing Directory for watermask:  additionalDirectory = (None) 

# Optional Image processing parameters (default values in parenthesis)
Scaling Factor of hue for median thresholding: hue_channel_scaling_factor = (0.4)
Scaling Factor of Value for median thresholding: value_channel_scaling_factor= (5.0)
Binary water map blob removal size for land features: blob_removal_land= (10000)
Binary water map blob removal size for water features: blob_removal_Water= (50000)

# Flags to save the outputs in png format
Save png for Water mask creation  (True/False): prepWmaskPNGflag= False                                              
Save png while channel construction (True/False): procChannelPNGflag= False                                            
Save png while binary water map creation (True/False): procWaterMapPngFlag= False                                           
Save png while filtering water maps (True/False): procblobRemovalpngFlag= False

# USEAG
Dependency checking:
	   ./depcheck.py

Running analysis:
	./main.py