#===============================================================================================
#===============================================================================================
#===============================================================================================
#===============================================================================================
# IRRIGATION EMISSIONS (MODELLING EXERCISE)
#===============================================================================================
#===============================================================================================
#===============================================================================================
#===============================================================================================



#===============================================================================================
#===============================================================================================
# Import required modules and preliminary settings
#===============================================================================================
#===============================================================================================

# Import os module and set working directory
import os
#os.chdir(r"/home/pro/projects/CoolFarmAlliance/Modeling_exercise/")


# Import pandas module to import csv table as a data frame data structure
import pandas as pd


# Import numpy to vectorize functions 
import numpy as np

#===============================================================================================
#===============================================================================================
# END Import required modules and preliminary settings
#===============================================================================================
#===============================================================================================


#===============================================================================================
#===============================================================================================
# User defined variables
#===============================================================================================
#===============================================================================================


#===============================================================================================
# Single choice variables
#===============================================================================================

# Proportion of area irrigated (dimensionless)

A_irri = 0.5


# Area of the assessment[ha]

A = 10


# Irrigation method ("Drip", "Sprinkler", "Surface")

Method_irri = "Surface"


# Irrigation region

Region_irri = "GLO U"
# Chose GLO U because it allows to use emission factors for both electricity and
# diesel as power source


#===============================================================================================
# END Single choice variables
#===============================================================================================


#===============================================================================================
# Multiple choice variables
#===============================================================================================

#===============================================================================================
# Irrigation events



# Choose measuring unit for irrigation (COMMENT OUT UNUSED ONE!!!)

#irrigation_meas_unit = "mm"
irrigation_meas_unit = "m3"


# Irrigation events measured as depth [mm]

D_irri_mm = np.array([2, 1, 7, 4, 3])


# ALTERNATIVELY irrigation events measured as volume [m3]

V_irri_m3 = np.array([20, 10, 70, 40, 30])


# END Irrigation events
#===============================================================================================


#===============================================================================================
# Power source


Power_irri = []


# Specify irrigation power source for each subsequent irrigation event ("Diesel", "Electricity").
# ALTERNATIVELY(!) set default power source (COMMENT OUT UNUSED ONE!!)

Power_irri = ["Electricity", "Electricity", "Diesel", "Electricity", "Diesel"]
#default_power = "Electricity"


# END Power source
#===============================================================================================


#===============================================================================================
# END Multiple choice variables
#===============================================================================================    


#===============================================================================================
#===============================================================================================
# END User defined variables
#===============================================================================================
#===============================================================================================


#===============================================================================================
#===============================================================================================
# Variables defined as function of user's choices
#===============================================================================================
#===============================================================================================

# Choose irrigation input for model and transform into data frame (for merging/joining with
# power source data

if irrigation_meas_unit == "mm":
    H2O_irri = D_irri_mm


if irrigation_meas_unit == "m3":
    H2O_irri = V_irri_m3


# Define vector with default power source

if not Power_irri:
    Power_irri = [default_power] * len(H2O_irri)



#===============================================================================================
#===============================================================================================
# END Variables defined as function of user's choices
#===============================================================================================
#===============================================================================================



#===============================================================================================
#===============================================================================================
# Selection of emission factors based on user defined variables
#===============================================================================================
#===============================================================================================

# Import table with emission factors as data frame

ef_df = pd.read_csv(r"C:/Users/Methods/irrigation_test/Table 9.6.csv")


# Rename column with Emission factors

ef_df.rename(columns={list(ef_df.columns)[len(list(ef_df.columns))-1]: 'Emission Factor'}, inplace=True)



# Subset data frame (extract for Method and Region)

EF_irri_df = ef_df.loc[(ef_df['Method'] == Method_irri) &
                       (ef_df['Region'] == Region_irri) , ]



# Transform list of power sources for the irrigation events into a data frame with explict index
# for merging, i.e. JOIN type database operation)

Power_irri_df = pd.DataFrame({'Power Source': Power_irri})
Power_irri_df.reset_index(inplace = True)

# Merge (JOIN) data frame of power sources with emission factor data frame on common
# column "power source"

Power_irri_ef_df = Power_irri_df.merge(EF_irri_df, left_on='Power Source', right_on='Power source')


# Set order of dataframe rows (for clarity, not stricly required)

Power_irri_ef_df = Power_irri_ef_df.sort_values('index')

#===============================================================================================
#===============================================================================================
# END Selection of emission factors based on user defined variables
#===============================================================================================
#===============================================================================================


#===============================================================================================
#===============================================================================================
# Compile data frame with model inputs (for model testing via manual calculation)
#===============================================================================================
#===============================================================================================


# Transform irrigation vector into data frame with explicit index (for merging, i.e. JOIN type
# database operation)

H2O_irri_df = pd.DataFrame({'H2O_irri': H2O_irri})
H2O_irri_df.reset_index(inplace = True)



model_input_df = Power_irri_ef_df.merge(H2O_irri_df, left_on='index', right_on='index')


# Set order according to users specification

model_input_df = model_input_df.sort_values('index')


#===============================================================================================
# Complete an edit model input data frame 


# Select irrigation measuring unit

if irrigation_meas_unit == "mm":
    irri_meas_unit = ["mm"] * len(model_input_df.index)
    conv_mm_m3 = [10] * len(model_input_df.index)


if irrigation_meas_unit == "m3":
    irri_meas_unit = ["m3"] * len(model_input_df.index)
    conv_mm_m3 = ["ND"] * len(model_input_df.index)


# Insert colomns with model inputs into data frame
model_input_df['Irri_meas_unit'] = irri_meas_unit
model_input_df['Conv_mm_m3'] = conv_mm_m3
model_input_df['A_irri'] = A_irri
model_input_df['A'] = A


# Set column order

model_input_df = model_input_df[['index', 'Irri_meas_unit', 'H2O_irri', 'Conv_mm_m3',
                                 'A_irri', 'A', 'Method', 'Power source', 'Region', 'Emission Factor']]

# END Complete an edit model input data frame 
#===============================================================================================


# Extract model inputs from data frame as numerical vectors

H2O_irri = model_input_df['H2O_irri'].values
A_irri = model_input_df['A_irri'].values
A = model_input_df['A'].values
EF_irri = model_input_df['Emission Factor'].values


#===============================================================================================
#===============================================================================================
# END Compile data frame with model inputs (for model testing via manual calculation)
#===============================================================================================
#===============================================================================================


#===============================================================================================
#===============================================================================================
# Define model. Model assumptions: 1)  previous irrigation events do not affect the emissions
# of following irrigation events 
#===============================================================================================
#===============================================================================================

# Define function for water input as irrigation depth [mm]

if irrigation_meas_unit == "mm":
    
    def Irrig_emiss_fun (H2O_irri, A_irri, A, EF_irri):
        L_irrigation = (H2O_irri * A_irri * A * 10) * EF_irri
        return(L_irrigation)
    


# Define function for water input as irrigation volume [m3]

if irrigation_meas_unit == "m3":
    
    def Irrig_emiss_fun (H2O_irri, A_irri, A, EF_irri):
        L_irrigation = (H2O_irri * A_irri * A) * EF_irri
        return(L_irrigation)
    



# Define vectorized function
Irrig_emiss_fun_v = np.vectorize(Irrig_emiss_fun)

#===============================================================================================
#===============================================================================================
# END Define model. Model assumptions: 1)  previous irrigation events do not affect the
# emissions of following irrigation events 
#===============================================================================================
#===============================================================================================



#===============================================================================================
#===============================================================================================
# Implement model 
#===============================================================================================
#===============================================================================================

# Calculate emissions for each irrigation event (vector)

Irrig_emiss_v = Irrig_emiss_fun_v(H2O_irri, A_irri, A, EF_irri)


# Calculate total emissions for all irrigation events (scalar)

Irrig_emiss = str(round(np.sum(Irrig_emiss_v), 3))


#===============================================================================================
#===============================================================================================
# END Implement model 
#===============================================================================================
#===============================================================================================



#===============================================================================================
#===============================================================================================
# Testing of model functionality
#===============================================================================================
#===============================================================================================


#===============================================================================================
# Print input data frame and model output  for testing (i.e. manual calculation)
#===============================================================================================


# Insert vector with emissions for each irrigation event into data frame with model inputs

model_input_df['kg CO2e'] = Irrig_emiss_v

model_test_df = model_input_df.drop('index', axis = 1)



# Print input and output of model run for manual calculation

print(model_test_df)

print("Total modelled emissions for all irrigation events = " + Irrig_emiss + " kg CO2e")


#===============================================================================================
# END Print input data frame and model output  for testing (i.e. manual calculation)
#===============================================================================================


#===============================================================================================
# Manual re-calculation of model output (valid only for specific instance of model run) 
#===============================================================================================


irri_1 = (2*0.5*10*10)*0.3445
irri_2 = (1*0.5*10*10)*0.3445
irri_3 = (7*0.5*10*10)*0.3418
irri_4 = (4*0.5*10*10)*0.3445
irri_5 = (3*0.5*10*10)*0.3418

np.around(np.array([irri_1, irri_2, irri_3, irri_4, irri_5]), 3)
round(irri_1 + irri_2 + irri_3 + irri_4 + irri_5, 3)


#===============================================================================================
# END Manual re-calculation of model output (valid only for specific instance of model run) 
#===============================================================================================

#===============================================================================================
#===============================================================================================
# END Testing of model functionality
#===============================================================================================
#===============================================================================================


#===============================================================================================
#===============================================================================================
#===============================================================================================
#===============================================================================================
# END IRRIGATION EMISSIONS (MODELLING EXERCISE)
#===============================================================================================
#===============================================================================================
#===============================================================================================
#=============================================================================================== 

