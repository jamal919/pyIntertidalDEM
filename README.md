# Application running and Arguments
Step 1: Run depcheck.py for checking for library and dependency error checks

Step 2: Edit main.py positional arguments

	indatadir = $ Directory of Zipped Data
	wkdir = $ Directory of saving unzipped data
	prepdir = $ Directory of saving preprocessed data   
	improcdir= $ Directory of saving processed data
	waterleveldir= $ Directory of water level dat files
	vertrefdir= $ Saving Intermediate data for vertical referencing

Step 3:Optinal Arguments:(default values)

## Preprocessing Optional Params 
		stdfactor = (0.5) 
	- Threshold for creating watermask i.e- data[data>factor*std]=Land (Float)
		MaskWater = (10000)  
	- Water Mask creation water blob removal threshold 
		MaskLand = (5000) 
	- Water Mask creation land blob removal threshold                                       additionalDirectory = (None) 
Specialized testing Directory for watermask                                 
	- processing Optional params 
		hue_channel_scaling_factor = (0.4)                                      
	- Scaling Factor of hue for median thresholding
		value_channel_scaling_factor= (5.0)                                    
	- Scaling Factor of Value for median thresholding
		
		blob_removal_land= (10000)
	- Binary water map blob removal size for land features
		
		blob_removal_Water= (50000)
	- Binary water map blob removal size for water features

## Boolean Params of png saving
		prepWmaskPNGflag= False                                              
	- Save png for Water mask creation  (True/False)
		procChannelPNGflag= False                                            
	- Save png while channel construction (True/False)
		procWaterMapPngFlag= False                                           
	- Save png while binary water map creation (True/False)
		procblobRemovalpngFlag= False                                        
	- Save png while filtering water maps (True/False)


# USEAGE: ./main.py

