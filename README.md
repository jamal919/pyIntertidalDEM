# pyIntertidalDEM
pyIntertidalDEM is a set of libraries and procedures written in python to 
extract shorelines from spectral images using a sophisticated shoreline extraction
algorithm.

The toolbox is developed to be used for Sentinel 2 2A/B products, but structured
in a way which can be easily extended for any similar high/low resolution 
spectral images.

The toolbox consists of four individual modules - 
* preprep - pre-processing of files before image processing
* improc - image processing for shoreline generation
* vertref - vertically reference the shorelines using water levels
* utils - general utility functions

These modules are developed in Python v3 environment and it is recommended to run
the program in Python v3 rather than Python v2. 

## Setup and Processing
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

## Optinal Arguments (default values in parenthesis)
Threshold for creating watermask i.e- data[data>factor*std]=Land (Float): stdfactor = (0.5)
Water Mask creation water blob removal threshold: MaskWater = (10000)
Water Mask creation land blob removal threshold: MaskLand = (5000) 
Specialized testing Directory for watermask:  additionalDirectory = (None) 

## Optional Image processing parameters (default values in parenthesis)
Scaling Factor of hue for median thresholding: hue_channel_scaling_factor = (0.4)
Scaling Factor of Value for median thresholding: value_channel_scaling_factor= (5.0)
Binary water map blob removal size for land features: blob_removal_land= (10000)
Binary water map blob removal size for water features: blob_removal_Water= (50000)

## Flags to save the outputs in png format
Save png for Water mask creation  (True/False): prepWmaskPNGflag= False                                              
Save png while channel construction (True/False): procChannelPNGflag= False                                            
Save png while binary water map creation (True/False): procWaterMapPngFlag= False                                           
Save png while filtering water maps (True/False): procblobRemovalpngFlag= False

## Usage
For dependency checking, run the following command - 
	$ ./depcheck.py

To run the analysis change the parameters as described in Step 3 and run it with -
	$ ./main.py


## Publications
The result of this work is currenly being communicated.