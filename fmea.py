import re

class SS_error(Exception):
    pass

class Attribute_error(Exception):
    pass

class typeError(Exception):
    pass    

def fetch_subsystems(body):
    """
    Fetches subsystem names from the given request body.

    Args:
    - body (dict): Request body containing subsystem data.

    Returns:
    - list: List of subsystem names.

    """
    return body.keys()

def fetch_attributes(body, sys):
    """
    Fetches attribute names for a given subsystem from the request body.

    Args:
    - body (dict): Request body containing subsystem data.
    - sys (str): Subsystem name for which attributes are fetched.

    Returns:
    - list: List of attribute names for the specified subsystem.

    """
    return body[sys].keys()

def min_func(body, sys, attribute):
    """
    Retrieves the minimum value for a specified attribute of a subsystem.

    Args:
    - body (dict): Request body containing subsystem data.
    - sys (str): Subsystem name.
    - attribute (str): Attribute name for which the minimum value is retrieved.

    Returns:
    - float: Minimum value of the attribute.

    """
    min_val = body[sys][attribute]["min_value"]
    return min_val

def max_func(body, sys, attribute):
    """
    Retrieves the maximum value for a specified attribute of a subsystem.

    Args:
    - body (dict): Request body containing subsystem data.
    - sys (str): Subsystem name.
    - attribute (str): Attribute name for which the maximum value is retrieved.

    Returns:
    - float: Maximum value of the attribute.

    """
    max_val = body[sys][attribute]["max_value"]
    return max_val

def compute_attribute(IP_attr_list, attribute, FMEA, sys, body):
    """
    Computes the evaluation of an attribute based on its type and actual value.

    Args:
    - IP_attr_list (list): List of attributes for the subsystem.
    - attribute (str): Attribute name to compute.
    - FMEA (dict): FMEA data structure containing attribute types(Master data containing faults details).
    - sys (str): Subsystem name.
    - body (dict): Request body containing subsystem data.

    Returns:
    - tuple: Two dictionaries P1 and P2 containing evaluation results.

    Raises:
    - typeError: If the attribute value has an invalid data type.

    """
    P1 = {}
    P2 = {}
    for at in IP_attr_list:
        if at == attribute:
            attribute_type = FMEA[sys]["parameters"][attribute]
            attribute_val = body[sys][attribute]["actual_value"]
            
            if attribute_type in ["L14", "L15","L16","L17","L18"]:
                try:
                    if isinstance(attribute_val, bool):
                        
                        if attribute_type in ["L14", "L15"]:
                            attribute_fval = attribute_val
                            P1.update({str(attribute_type): str(attribute_fval)})
                            if attribute_val:
                                P2.update({str(attribute_type): {str(attribute): "ON"}})
                            else:
                                P2.update({str(attribute_type): {str(attribute): "OFF"}})
                        elif attribute_type in ["L17", "L18"]:
                            attribute_fval = (not attribute_val)
                            P1.update({str(attribute_type): str(attribute_fval)})
                            if attribute_val:
                                P2.update({str(attribute_type): {str(attribute): "ON"}})
                            else:
                                P2.update({str(attribute_type): {str(attribute): "OFF"}})
                    else:
                        raise typeError(f"Invalid datatype: {type(attribute_val)} in attribute: {attribute} in {sys}. Accepted only: boolean types.")
                except typeError as te:
                        raise typeError(f"{te}")      
            else:  
                try:     
                    if isinstance(attribute_val, (int, float)):   
                        min1 = min_func(body, sys, attribute)
                        max1 = max_func(body, sys, attribute)
                        if float(attribute_val) < min1:
                            P1.update({str(attribute_type): "True"})
                            P2.update({str(attribute_type): {str(attribute): "Low"}})
                        elif float(attribute_val) > max1:
                            P1.update({str(attribute_type): "True"})
                            P2.update({str(attribute_type): {str(attribute): "High"}})
                        else:
                            P1.update({str(attribute_type): "False"})
                            P2.update({str(attribute_type): {str(attribute): "Normal"}})
                    else:
                        raise typeError(f"Invalid data type: {type(attribute_val)} in attribute: {attribute} in {sys}. Accepted only: int/float types.")
                except typeError as te:
                    raise typeError(f"{te}")
    return P1, P2

def replace_variables(expression, all_params_dict, res2_dict):
    """
    Replaces variables in the given expression with their corresponding values.

    Args:
    - expression (str): Expression containing variables to replace.
    - all_params_dict (dict): Dictionary mapping variable names to their values.
    - res2_dict (dict): Dictionary containing symptom mappings.

    Returns:
    - tuple: Updated expression with replaced variables and a dictionary of symptoms.

    """
    matches = re.findall(r'[A-Za-z]\d+', expression)
    symptoms = {}
    for key in res2_dict.keys():
        if key in matches:
            symptoms.update(res2_dict[key])

    for key, value in all_params_dict.items():
        expression = re.sub(r'\b' + re.escape(key) + r'\b', str(value), expression) 

    return expression, symptoms  

def main(args: dict, query_params: dict) -> dict:
    """
    Main function to process FMEA data and compute fault statuses.

    Args:
    - args (dict): Dictionary containing the request body with subsystem and attribute data.
    - query_params (dict): Dictionary containing query parameters (not used in current implementation).

    Returns:
    - dict: List of dictionaries containing computed fault statuses for each subsystem.

    Raises:
    - SS_error: If an invalid subsystem is requested.
    - Attribute_error: If an invalid attribute is requested for a subsystem.
    - typeError: If an attribute value has an invalid data type.

    """

    FMEA = {
	"bearing_system": {
		"faults": [
			{
				"fault_id": "RTR-Mech-4",
				"fault_logic": "(B6 or B7) and (B9 or B10)",
				"fault_name": "Rotor Anomaly",
				"severity": "Important",
				"cause": "Unbalance.Misalighment.Both DE and NDE bearings damage Looseness.Coulping damage.Electrical discharge.Sensor bias or drift.",
				"effects": "High Vibration,seal leakage, overload, rotor damage, blade casing rubbing, catastrophic damage",
				"actions": "Check the calibration of sensor.Investigate with high frequency vibration analysis. Check Carbon brush integrity.Check magnetism of the rotor.Check rotor unbalance, misalignment. Looseness.Check coupling integrity.Check foundation bolt integrity.Check both bearings for clearance and pad wear etc."
			},
			{
				"fault_id": "BRG-LO-1",
				"fault_logic": "(B16) and (B6 or B7 or B8 or B9 or B10 or B11 or B12 or B14 or B15)",
				"fault_name": "Thrust/Radial Bearing Anomly due to Lube Oil Pressure",
				"severity": "Serious",
				"cause": "Loss Of lube Oil Cooling,Sensor bias or drift",
				"effects": "Overload. Babbitt wear/ failure. Oil film degradation. Bearing damage. Rotor damage. Displacement alarm/trip.",
				"actions": "Check the calibarion of sensor.Check cooling water supply pressure. Check bypass control valve. Open coolers and stabilise temperature.Check cooling water pumps for blockages, ensure strainer is clean, If malfunction of cooler is suspected, isolate and inspect it. Line walk the system to check for leaks."
			},
			{
				"fault_id": "BRG-LO-2",
				"fault_logic": "(B17) and (B6 or B7 or B8 or B9 or B10 or B11 or B12 or B14 or B15)",
				"fault_name": "Thrust/Radial Bearing Anomly due to Lube Oil Temperature",
				"severity": "Important",
				"cause": "Loss Of lube Oil Cooling, Sensor bias or drift",
				"effects": "Overload. Babbitt wear/ failure. Oil film degradation. Bearing damage. Rotor damage. Displacement alarm/trip.",
				"actions": "Check the calibarion of sensor.Check cooling water supply pressure. Check bypass control valve. Open coolers and stabilise temperature.Check cooling water pumps for blockages, ensure strainer is clean, If malfunction of cooler is suspected, isolate and inspect it. Line walk the system to check for leaks."
			},
			{
				"fault_id": "BRG-LOQ-3",
				"fault_logic": "(B18) and (B6 or B7 or B8 or B9 or B10 or B11 or B12 or B14 or B15)",
				"fault_name": "Thrust/Radial Bearing Anomly due to Lube Oil Quality",
				"severity": "Medium",
				"cause": "Loss of Lube Oil Quality, Oil contamination, Oil Foaming",
				"effects": "High vibration.    Increase of brg clearance.Seal leakage. Overload Babbitt failure Bearing/rotor damage Oil film instability",
				"actions": "Check oil tank for free water by draining 1L into a sample bottle. Switch cooler if water contamination.Take an oil sample and check water content, viscosity, TAN. Check no breather caps or man covers have been removed and left open to allow debris into the tank. Recondition or replace oil."
			},
			{
				"fault_id": "BRG-Mech-1",
				"fault_logic": "(B12 or B13 or B14 or B15) and not (((B16) and (B6 or B7 or B8 or B9 or B10 or B11 or B12 or B14 or B15)) and ((B17) and (B6 or B7 or B8 or B9 or B10 or B11 or B12 or B14 or B15)) and ((B18) and (B6 or B7 or B8 or B9 or B10 or B11 or B12 or B14 or B15)))",
				"fault_name": "Thrust Bearing Anomly due to Mech Issue",
				"severity": "Important",
				"cause": "Multiple surge events Pad overload due to misalignment. Liquid slugs in inlet scrubber Balance piston wear Balance line blockage Electrical dischargePad pivot wear, Axial float change, Coupling issue (gear coulping lock or diaphgram column prestretch)Sensor bias or drift",
				"effects": "High vibration. Increase of brg clearance.Seal leakage. Overload Babbitt failure Bearing/rotor damage Oil film instability",
				"actions": "Check calibration of sensor.Assess likely cause and time to trip if intervention not possible. Intervention options. reduce thrust load. Ensure parts availability.Check axial vibration trends to establish if the machine  has surged and potentially damaged/wiped the pads.If required inspect the thrust pads and collar to check for damage / wiping.Carry out a bump check to establish what float is in the machine, compare to previous overhaul report for measurement. Check the gear coupling/pre-strech diaphgram coupling "
			},
			{
				"fault_id": "BRG-Mech-2",
				"fault_logic": "(B6 or B7 or B8) and not ((B6 or B7) and (B9 or B10))",
				"fault_name": "DE Radial Bearing Anomly due to Mech Issue",
				"severity": "Important",
				"cause": " Bush/Pad wear and tear Increase in Brg Clearance Mulitple Surge Events Electrical DischargeLiquid Slugs Ingession, bearing aging.Sensor bias or drift",
				"effects": "Bearing temperatures high,  Bearing damage, temp high trip of comp ",
				"actions": "Check calibration of sensor. Investigate with high frequency vibration analysis. Assess likely cause and time to fail(trip) if intervention not possible. Intervention options,reduce speed, Parts availability. Check the trends to establish if its either both X and Y probes or one. Inspect bearing for the following, wiping, internal clearances, oil coking / hot spots. Change bearing if required.  ."
			},
			{
				"fault_id": "BRG-Mech-3",
				"fault_logic": "(B9 or B10 or B11) and not ((B6 or B7) and (B9 or B10))",
				"fault_name": "NDE Radial Bearing Anomly due to Mech Issue",
				"severity": "Important",
				"cause": "Bush/Pad wear and tear Increase in Brg Clearance Mulitple Surge Events Electrical DischargeLiquid Slugs Ingession, bearing aging.Sensor bias or drift",
				"effects": "Bearing temperatures high,  Bearing damage, temp high trip of comp ",
				"actions": "Check calibration of sensor. Investigate with high frequency vibration analysis. Assess likely cause and time to fail(trip) if intervention not possible. Intervention options,reduce speed, Parts availability. Check the trends to establish if its either both X and Y probes or one. Inspect bearing for the following, wiping, internal clearances, oil coking / hot spots. Change bearing if required.  ."
			}
		],
		"parameters" : {
            "k_de_radial_vibration_overall_x": "B6",
            "k_de_radial_vibration_overall_y": "B7",
            "k_de_radial_bearing_temperature": "B8",
            "k_nde_radial_vibration_overall_x": "B9",
            "k_nde_radial_vibration_overall_y": "B10",
            "k_nde_radial_bearing_temperature": "B11",
            "thrust_bearing_active_side_gap": "B12",
            "thrust_bearing_inactive_side_gap": "B13",
            "k_thrust_bearing_temperature_active_side": "B14",
            "k_thrust_bearing_temperature_inactive_side": "B15",
            "lo_header_pressure": "B16",
            "lo_header_temperature": "B17",
            "lo_viscosity": "B18",
            "lo_tan": "B19"
        }
	},
    "lo_system" : {
        "faults": [
        {
            "fault_id": "LOQ-1",
            "fault_logic": "(L4 or L5 or L6)",
            "fault_name": "Loss of lube oil quality",
            "severity": "Medium",
            "cause": "Oil foaming. Water contamination. LO degradation. Solid particles contamination. Hydrocarbon contamination. Leaking cooler",
            "effects": "Oil viscosity drop/rise. Oil film instability. Bearing corrosion. Bearing erosion. Gear damage",
            "actions": "Check oil tank for free water by draining 1L into a sample bottle. Switch cooler if water contamination. Take an oil sample and check water content, viscosity, TAN. Check no breather caps or man covers have been removed and left open to allow debris into the tank. Do filter cleaning. Recondition or replace oil."
        },
        {
            "fault_id": "LOF-2",
            "fault_logic": "(L3)",
            "fault_name": "Lube Oil Filter Anomaly.",
            "severity": "Serious",
            "cause": "Lube Oil Dp High, Filter Clogging/Jam. Sensor bias or drift.",
            "effects": "Bearing overheating. Bearing seizure. Babbitt failure. Journal damage. Low lube oil pressure.",
            "actions": "Check filter DP, changeover and clean/replace the standby filter. Check the Filter DP transmitter."
        },
        {
            "fault_id": "LOP-P-3",
            "fault_logic": "(L1 and (L9 or L10 or L11)) and (L14 or L15)",
            "fault_name": "Loss of pressure due to Pump anomaly.",
            "severity": "Medium",
            "cause": "PCV malfunction. LO Pump degradation. Line failure/leakage. LO tank level low, Tank high pressure (Tank is not open to atmosphere), Auto start logic of Pump issue, Discharge PT malfunction. Sensor bias or drift.",
            "effects": "Bearing overheating. Bearing seizure. Babbitt failure. Journal damage. Low lube oil pressure.",
            "actions": "Check the Discharge PT integrity. Switch on both oil pumps and stabilize oil pressure. Assess malfunction. Line walk the system and check for leaks, ensure PSVs are seated. Check spillback/PCV valves are set correctly and not returning oil back to the tank. Ensure no hand valves have been left shut for the standby pump. Check oil level in tank, Open tank overhead vents for release of pressure. Check PCV function for Integrity. Check Auto Logic Function tests, check functioning of the auto changeover switch. If maintenance has recently been performed check correct rotation of pump. Ensure NRVs are working correctly."
        },
        {
            "fault_id": "LOC-CO-4",
            "fault_logic": "(L2 and L13)",
            "fault_name": "Loss of cooling due to Cooler Anomaly",
            "severity": "Serious",
            "cause": "Cooler failure. Cooler fouling. CW temperature anomaly. Sensor bias or drift.",
            "effects": "Oil instability. Bearing overheating. LO varnishing.",
            "actions": "Check the calibration of sensor. Check cooling water supply pressure. Open both coolers and stabilize temperature. If malfunction of one cooler is suspected, isolate and inspect it. Line walk the system to check for leaks. Check cooling water pumps for blockages, ensure strainer is clean."
        },
        {
            "fault_id": "LOC-AC-5",
            "fault_logic": "(L2 and L17 and L18)",
            "fault_name": "Loss of cooling Due to Fan-Motor Issue",
            "severity": "Important",
            "cause": "Unable to deliver air to the cooler",
            "effects": "Oil instability. Bearing overheating.",
            "actions": "Offline: Check the Fan and Motor/coupling/belt Integrity and rectify."
        }
     ],
     "parameters": {
        "lo_header_pressure": "L1",
        "lo_header_temperature": "L2",
        "oil_filter_dp": "L3",
        "lo_viscosity": "L4",
        "lo_tan": "L5",
        "lo_composition_analysis": "L6",
        "oil_tank_level": "L7",
        "oil_tank_temperature": "L8",
        "lo_pumps_discharge_pressure": "L9",
        "lube_oil_pcv_position": "L10",
        "lube_oil_return_flow_rate": "L11",
        "lo_cooler_bypass_valve_tcv_position": "L12",
        "delta_temperature_lo_tank_vs_lo_cooler_discharge": "L13",
        "main_lube_oil_pump_current_run_signal": "L14",
        "aux_lube_oil_pump_current_run_signal": "L15",
        "lube_oil_tank_heater_run_signal": "L16",
        "air_cooler_fan_1_run_status": "L17",
        "air_cooler_fan_2_run_status": "L18"
        }
    },
	"performance" : {
        "faults": [
        {
            "fault_id": "PER-1",
            "fault_logic": "(P10 or P17 or P18)",
            "fault_name": "Comp Inlet Supply anomaly",
            "severity": "Important",
            "cause": "Onstream equipment like suction scrubber etc issue, Pipe line leak or jam, Suction strainer jam or leakage. Sensor bias or drift",
            "effects": "Process Upsets in the downstream assets and the compressor",
            "actions": "Check calibration of sensor. Assess of leaks/jam in the upstream equipment or pipe line or Suction strainers etc."
        },
        {
            "fault_id": "PER-2",
            "fault_logic": "(P22)",
            "fault_name": "Inlet Filter Anomaly",
            "severity": "Serious",
            "cause": "Filter jam/Choke. Sensor bias or drift",
            "effects": "Inlet pressure change leading to process upsets",
            "actions": "Check the calibration of sensor. Change over the filter if standby is available and replace the filter."
        },
        {
            "fault_id": "PER-3",
            "fault_logic": "(P13 or P14 or P19) and not (P10 or P17 or P18)",
            "fault_name": "Compressor Performance degradation",
            "severity": "Important",
            "cause": "Impeller damage Change in molecular weight (for non-air and non-closed-loop applications) Fouling / corrosion / erosion of flowpath components Casing leaks Seal leakage Instrument malfunction",
            "effects": "Efficiency reduction",
            "actions": "For non-air, non-closed-loop applications: Perform a gas analysis or reconfirm molecular weight. Check instruments accuracy (flow meter, suction and discharge temperature and pressure transmitters). If all of the above are ok, then performance deviation is genuine. At this point: Confirm IGV operability. Check for casing leaks. Confirm seal integrity. If all of the above is ok the reason for degradation could be internal clearances have increased and/or flowpath has fouled up or has been damaged. In this case, at first opportunity: Carry out borescope inspection to verify if there is internal damage. If fouling is identified, wash the machine if possible. Monitor efficiency to determine speed of degradation and plan rotor replacement when it becomes unsustainable."
        },
        {
            "fault_id": "PER-4",
            "fault_logic": "(P21 or P20) and P6",
            "fault_name": "Liquid slugs",
            "severity": "Important",
            "cause": "Suction scrubber internal malfunction Suction scrubber overload. Suction scrubber liquid level high. Scrubber LCV or its Controller malfunction. Instrument Malfunction",
            "effects": "Liquid slugs ingestion: increased risk of seal damage and balance line plugging, possibly leading to seals leakage and/or thrust bearing failure. Coupling overload, impeller damage",
            "actions": "Short term: reduce flow. Correct problem at process level (reduce scrubber level or act on process), monitor seals leakages, axial shaft position, thrust bearing temperature."
        },
        {
            "fault_id": "PER-5",
            "fault_logic": "P13",
            "fault_name": "Fouling / corrosion / erosion risk",
            "severity": "Serious",
            "cause": "If fouling: Soft & sticky particles in process gas (Polymerization Precipitation, liquids carryover, etc.) Unexpected gas composition change If corrosion / erosion: Compressor materials incompatible with gas Hard & abrasive particles in process gas Online compressor washing Unexpected gas composition change",
            "effects": "Progressive contamination of impeller blades, distortion of aerodynamic characteristics, degradation of compressor performance curve. Possible unbalance if parts of deposits detach from impeller surface, possible progressive obstruction of balance line over time, with consequent axial thrust increase. If corrosion / erosion: Progressive removal of impeller / volute / diffuser material, usually undetected until a piece of the impeller fails, detaches and creates an unbalance and potential damage to gaspath / flow obstruction. Possible alteration of the impeller blades shapes with consequent aerodynamic change inside operating range. Possible degradation of labys with consequent permanent efficiency loss and rotor behavior changes",
            "actions": "If fouling: Short term; Wash compressor if possible. Long term, investigate application of coating on affected gas path. Change gas inlet Temp. Borescope inspection at opportunity. If corrosion / erosion: Replace corroded parts with better material grade. In case of erosion consider coating of gas path. Borescope at opportunity."
        },
        {
            "fault_id": "PER-6",
            "fault_logic": "(P15 or P16)",
            "fault_name": "IGV/Suction throttle valve malfunction",
            "severity": "Serious",
            "cause": "Actuator malfunction (Hydraulic or Electric) Loss of feed to the actuator Actuator blockage Linkage blockage Linkage bushing failure Thermal growth leading to insufficient clearance with casing and IGV getting stuck",
            "effects": "Low efficiency, Reduced flow, High Vibrations",
            "actions": "Check IGV/Suction throttle integrity and operability. Check calibration of the positioner. Check IGV/Suction throttle actuator and feed. Check all linkage connections. Carry out borescope examination to identify presence of internal damage."
        },
        {
            "fault_id": "PER-7",
            "fault_logic": "P7 or P8",
            "fault_name": "Interstage Cooler anomaly",
            "severity": "Serious.",
            "cause": "Intercoolers integrity, Intercoolers coolant supply issue, TV malfunction, TV control loop issue.",
            "effects": "The temperature change will affect the dew point temperature and hence separators efficiency. Moreover, large inlet temp to the compressor will lead to its performance loss.",
            "actions": "Check the interstage coolers integrity. Check the temp control valve for any anomaly. Conduct loop proof test for temp control valve. Check cooling water supply line for any leakage / blockage / supply issue."
        },
        {
            "fault_id": "PER-8",
            "fault_logic": "P9",
            "fault_name": "Interstage Separator anomaly",
            "severity": "Important",
            "cause": "Separator / scrubber internal damage, separator drain line choke, separator mesh damage, separator / line leakage, separator / line blockage.",
            "effects": "Ineffective moisture separation from the process gas leading to liquid sludge ingress and subsequently corrosion in line, compressors casings, thus damage to internals.",
            "actions": "Check Separator / scrubbers internals. Check drain line of the separator. Check the transmitter."
        }
        ],
         "parameters": {
        "suction_scrubber_level": "P6",
        "interstage_cooler_gas_outlet_temperature": "P7",
        "interstage_cooler_temp_control_valve_opening": "P8",
        "interstage_separator_level": "P9",
        "suction_flow": "P10",
        "discharge_flow": "P11",
        "head_deviation_actual_expected": "P12",
        "efficiency_deviation_expected_actual": "P13",
        "compressor_discharge_temperature": "P14",
        "igv_angle_actuator_position": "P15",
        "suction_throttling_valve_percent": "P16",
        "compressor_inlet_temperature": "P17",
        "compressor_inlet_pressure": "P18",
        "compressor_discharge_pressure": "P19",
        "k_de_radial_vibration_overall_x": "P20",
        "k_nde_radial_vibration_overall_x": "P21",
        "inlet_filter_dp": "P22"
        }
    },
	"transmission" : {
         "faults": [
        {
            "fault_id": "GBB-1",
            "fault_logic": "(T6 or T7 or T17 or T18 or T23) and not ((T6 or T7) and (T8 or T9)) or (T23 or T24)",
            "fault_name": "LSS GB DE RB anomaly",
            "severity": "Important",
            "cause": "Bush/Pad wear and tear Increase in Brg Clearance Mulitple Surge Events Electrical Discharge Liquid Slugs Ingession, bearing aging.Sensor bias or drift",
            "effects": "Bearing temperatures high,  Bearing damage, temp high trip of comp",
            "actions": "Check the calibration of sensor. Investigate with high frequency vibration analysis. Assess likely cause and time to fail(trip) if intervention not possible. Intervention options; reduce speed, Parts availability. Check the trends to establish if its either both X and Y probes or one. Inspect bearing for the following, wiping, internal clearances, oil coking / hot spots. Change bearing if required."
        },
        {
            "fault_id": "GBB-2",
            "fault_logic": "(T8 or T9 or T15 or T16 or T24) and not ((T6 or T7) and (T8 or T9)) or (T23 or T24)",
            "fault_name": "LSS GB NDE RB anomaly",
            "severity": "Important",
            "cause": "Bush/Pad wear and tear Increase in Brg Clearance Mulitple Surge Events Electrical Discharge Liquid Slugs Ingession, bearing aging.Sensor bias or drift",
            "effects": "Bearing temperatures high,  Bearing damage, temp high trip of comp",
            "actions": "Check the calibration of sensor. Investigate with high frequency vibration analysis. Assess likely cause and time to fail(trip) if intervention not possible. Intervention options; reduce speed, Parts availability. Check the trends to establish if its either both X and Y probes or one. Inspect bearing for the following, wiping, internal clearances, oil coking / hot spots. Change bearing if required."
        },
        {
            "fault_id": "GBB-3",
            "fault_logic": "(T11 or T12 or T21 or T22 or T25) and not (((T11 or T12) and (T13 or T14)) or (T25 and T26))",
            "fault_name": "HSS GB DE RB anomaly",
            "severity": "Medium",
            "cause": "Bush/Pad wear and tear Increase in Brg Clearance Mulitple Surge Events Electrical Discharge Liquid Slugs Ingession, bearing aging.Sensor bias or drift",
            "effects": "Bearing temperatures high,  Bearing damage, temp high trip of comp",
            "actions": "Check the calibration of sensor. Investigate with high frequency vibration analysis. Assess likely cause and time to fail(trip) if intervention not possible. Intervention options; reduce speed, Parts availability. Check the trends to establish if its either both X and Y probes or one. Inspect bearing for the following, wiping, internal clearances, oil coking / hot spots. Change bearing if required."
        },
        {
            "fault_id": "GBB-4",
            "fault_logic": "(T13 or T14 or T19 or T20 or T26) and not (((T11 or T12) and (T13 or T14)) or (T25 and T26))",
            "fault_name": "HSS GB NDE RB anomaly",
            "severity": "Serious",
            "cause": "Bush/Pad wear and tear Increase in Brg Clearance Mulitple Surge Events Electrical Discharge Liquid Slugs Ingession, bearing aging.Sensor bias or drift",
            "effects": "Bearing temperatures high,  Bearing damage, temp high trip of comp",
            "actions": "Check the calibration of sensor. Investigate with high frequency vibration analysis. Assess likely cause and time to fail(trip) if intervention not possible. Intervention options; reduce speed, Parts availability. Check the trends to establish if its either both X and Y probes or one. Inspect bearing for the following, wiping, internal clearances, oil coking / hot spots. Change bearing if required."
        },
        {
            "fault_id": "GBB-5",
            "fault_logic": "((T6 or T7) and (T8 or T9)) or (T23 or T24)",
            "fault_name": "LSS Shaft anomaly",
            "severity": "Medium",
            "cause": "Unbalance Misalignment Both DE and NDE bearings damage Looseness, Coupling damage Electrical discharge Gear Anomaly.Sensor bias or drift",
            "effects": "High Vibration,seal leakage, overload, rotor damage, blade casing rubbing, catastrophic damage",
            "actions": "Check calibration of sensor. Investigate with high frequency vibration analysis. Check Carbon brush integrity. Check magnetism of the rotor Check rotor unbalance, misalignment. Looseness. Check coupling integrity. Check foundation bolt integrity. Check both bearings for clearance and pad wear etc. Check gear integrity."
        },
        {
            "fault_id": "GBB-6",
            "fault_logic": "(((T11 or T12) and (T13 or T14)) or (T25 and T26))",
            "fault_name": "HSS Shaft anomaly",
            "severity": "Important",
            "cause": "Unbalance Misalignment Both DE and NDE bearings damage Looseness, Coupling damage Electrical discharge Gear Anomaly.Sensor bias or drift",
            "effects": "High Vibration,seal leakage, overload, rotor damage, blade casing rubbing, catastrophic damage",
            "actions": "Check calibration of sensor. Investigate with high frequency vibration analysis. Check Carbon brush integrity. Check magnetism of the rotor Check rotor unbalance, misalignment. Looseness. Check coupling integrity. Check foundation bolt integrity. Check both bearings for clearance and pad wear etc. Check gear integrity."
        },
        {
            "fault_id": "GBB-7",
            "fault_logic": "(T27 or T28 or T29 or T30)",
            "fault_name": "LSS GB thrust bearing anomaly",
            "severity": "Important",
            "cause": "Axial float issue in driver or driven Pad overload due to misalignment. Electrical discharge Pad pivot wear, Axial float change of the gear box, Collar wear. Coupling issue (gear coupling lock or diaphragm coupling pre-stretch).Sensor bias or drift",
            "effects": "High vibration. Increase of brg clearance. Seal leakage. Overload. Babbitt failure Bearing/rotor damage Oil film instability",
            "actions": "Check if the lube oil header temp, pressure and quality has not altered (if lube oil system is available). Assess likely cause and time to trip if intervention not possible. Check calibration of sensor. Intervention options; reduce thrust load. Ensure parts availability. Check axial vibration trends to establish if the driver or driven has change in axial thrust and potentially damaged/wiped the pads. If required inspect the thrust pads and collar to check for damage / wiping. Carry out a bump check to establish what float is in the machine, compare to previous overhaul report for measurement. Check the gear coupling/pre-stretch diaphragm coupling."
        },
        {
            "fault_id": "GBB-8",
            "fault_logic": "(T31 or T32 or T33 or T34)",
            "fault_name": "HSS GB thrust bearing anomaly",
            "severity": "Important",
            "cause": "Axial float issue in driver or driven Pad overload due to misalignment. Electrical discharge Pad pivot wear, Axial float change of the gear box, Collar wear. Coupling issue (gear coupling lock or diaphragm coupling pre-stretch).Sensor bias or drift",
            "effects": "High vibration. Increase of brg clearance. Seal leakage. Overload. Babbitt failure Bearing/rotor damage Oil film instability",
            "actions": "Check if the lube oil header temp, pressure and quality has not altered (if lube oil system is available). Assess likely cause and time to trip if intervention not possible. Check calibration of sensor. Intervention options; reduce thrust load. Ensure parts availability. Check axial vibration trends to establish if the driver or driven has change in axial thrust and potentially damaged/wiped the pads. If required inspect the thrust pads and collar to check for damage / wiping. Carry out a bump check to establish what float is in the machine, compare to previous overhaul report for measurement. Check the gear coupling/pre-stretch diaphragm coupling."
        }
        ],
     "parameters": {
        "lss_de_radial_vibration_overall_x": "T6",
        "lss_de_radial_vibration_overall_y": "T7",
        "lss_nde_radial_vibration_overall_x": "T8",
        "lss_nde_radial_vibration_overall_y": "T9",
        "lss_axial_temperature": "T10",
        "hss_de_radial_vibration_overall_x": "T11",
        "hss_de_radial_vibration_overall_y": "T12",
        "hss_nde_radial_vibration_overall_x": "T13",
        "hss_nde_radial_vibration_overall_y": "T14",
        "lss_nde_radial_bearing_temperature_a": "T15",
        "lss_nde_radial_bearing_temperature_b": "T16",
        "lss_de_radial_bearing_temperature_a": "T17",
        "lss_de_radial_bearing_temperature_b": "T18",
        "hss_nde_radial_bearing_temperature_a": "T19",
        "hss_nde_radial_bearing_temperature_b": "T20",
        "hss_de_radial_bearing_temperature_a": "T21",
        "hss_de_radial_bearing_temperature_b": "T22",
        "lss_de_casing_vibration": "T23",
        "lss_nde_casing_vibration": "T24",
        "hss_de_casing_vibration": "T25",
        "hss_nde_casing_vibration": "T26",
        "lss_thrust_bearing_active_side_gap": "T27",
        "lss_thrust_bearing_inactive_side_gap": "T28",
        "lss_thrust_bearing_active_side_temp": "T29",
        "lss_thrust_bearing_inactive_side_temp": "T30",
        "hss_thrust_bearing_active_side_gap": "T31",
        "hss_thrust_bearing_inactive_side_gap": "T32",
        "hss_thrust_bearing_active_side_temp": "T33",
        "hss_thrust_bearing_inactive_side_temp": "T34"
        }
    },
	"dry_gas_seal_system" : {
        "faults": [
        {
            "fault_id": "DGS-1",
            "fault_logic": "(S9)",
            "fault_name": "Primary seal gas filter anomaly",
            "severity": "Serious",
            "cause": "Jammed filter, filter internal damage, filter leakage. Sensor bias or drift.",
            "effects": "Large filter DP will lead to larger seal pressure. Moreover, dirty process gas may entrain the DGS, thus damaging its internals.",
            "actions": "Check the calibration of sensor. Check the filter efficiency and change to standby the filter if required. Repair/replace the filter internals."
        },
        {
            "fault_id": "DGS-2",
            "fault_logic": "(S13)",
            "fault_name": "Buffer gas filter anomaly",
            "severity": "Important",
            "cause": "Jammed filter, filter internal damage, filter leakage. Sensor bias or drift.",
            "effects": "Large filter DP will lead to larger seal pressure. Moreover, dirty process gas may entrain the DGS, thus damaging its internals.",
            "actions": "Check the calibration of sensor. Check the filter efficiency and change to standby the filter if required. Repair/replace the filter internals."
        },
        {
            "fault_id": "DGS-3",
            "fault_logic": "(S6 or S14)",
            "fault_name": "PDCV malfunction",
            "severity": "Medium",
            "cause": "Internal valve packing leak Jamming Contamination Internal valve component failure, Valve set point loss. Sensor bias or drift",
            "effects": "Valve cannot maintain DP setpoint Excessive flow through inboard laby towards primary seal, causing primary seal failure.",
            "actions": "Check the calibration of sensor. Check valve set point. Check valve internals for any damage, and repair/replace if necessary. Conduct the PDCV control loop function test."
        },
        {
            "fault_id": "DGS-4",
            "fault_logic": "(S10 or S11)",
            "fault_name": "Outboard Seal Malfunction",
            "severity": "Serious",
            "cause": "OB secondary seals fouling OB seal faces contact OB dynamic seal failure OB seal hang-up OB face thermal overload/shock, OB seal contamination, Internal Labyrinth fail in tandem",
            "effects": "OB seal leakage, potential containment risk, Complete seal failure risk",
            "actions": "Ensure upstream and downstream PSVs, check valves, transmitters are all working correctly. Inspect and monitor trend sec seal gas system. Ensure spare seals cartridge is available. Assess risk. Monitor and replace seals at opportunity. Replace seal."
        },
        {
            "fault_id": "DGS-5",
            "fault_logic": "(S10)",
            "fault_name": "Inboard Seal malfunction",
            "severity": "Serious",
            "cause": "IB secondary seals failure .IB secondary seals fouling IB seal faces contact IB dynamic seal failure IB seal hang-up IB rotating face thermal overload/shock, Process gas side Labyrinth jam",
            "effects": "Potential IB seal process gas leakage, Loss of containment.",
            "actions": "Ensure upstream and downstream PSVs, check valves, transmitters are all working correctly. Inspect and monitor trend sec seal gas system. Ensure spare seals cartridge is available. Assess risk. Monitor and replace seals at opportunity. Replace seal."
        },
        {
            "fault_id": "DGS-6",
            "fault_logic": "(S7)",
            "fault_name": "Primary seal temperature anomaly",
            "severity": "Important",
            "cause": "Process / Primary Seal Chamber Separation Laby Failure Seal gas supply PDV failure Primary seal gas below dew point Lack of separation gas Seal gas superheater malfunction. Sensor bias or drift.",
            "effects": "Seals contamination, fouling: increased risk of seals failure.",
            "actions": "Check calibration of sensor. Monitor seal leakage. Check integrity of seal gas supply PDV. Check superheater functionality if available. Check separation gas. Check seal supply filters for damage and are fitted correctly."
        },
        {
            "fault_id": "DGS-7",
            "fault_logic": "(S8)",
            "fault_name": "Primary seal gas supply anomaly",
            "severity": "Medium",
            "cause": "PCV Failure in primary gas line Line Blockage System Leakage. Sensor bias or drift",
            "effects": "Unfiltered process gas to seal Dirt in the seal area Possible liquid condensation in the seal Possible Seal Damage / Failure.",
            "actions": "Check the calibration of sensor. Check N2 supply system for any leaks or damage. Ensure upstream and downstream PSVs, check valves, transmitters are all working correctly. Inspect PCV and check functionality. Replace Filters."
        },
        {
            "fault_id": "DGS-8",
            "fault_logic": "(S12 or S15 or S16)",
            "fault_name": "Buffer gas supply anomaly",
            "severity": "Medium",
            "cause": "PCV Failure in buffer gas line Line Blockage System Leakage. Sensor bias or drift.",
            "effects": "Primary Seal gas to atmospheric vent Possible loss of containment.",
            "actions": "Check the calibration of sensor. Check N2 supply system for any leaks or damage. Ensure upstream and downstream PSVs, check valves, transmitters are all working correctly. Inspect PCV and check functionality. Replace Filters."
        }
        ],
     "parameters": {
        "reference_line_dp": "S6",
        "primary_seal_gas_supply_temperature": "S7",
        "primary_seal_gas_supply_pressure_flow": "S8",
        "dp_over_seal_gas_filter": "S9",
        "primary_vent_pressure_flow": "S10",
        "secondary_vent_pressure_flow": "S11",
        "buffer_gas_supply_pressure_flow": "S12",
        "buffer_gas_filter_dp": "S13",
        "pdcv_valve_opening": "S14",
        "secondary_supply_pcv_opening": "S15",
        "buffer_gas_pcv_opening": "S16"
      }
    }
   } 
    l1 = []
    l2 = []
    res1_dict = {}
    res2_dict = {}
    
    body = args.get("body")
    ip_sub_systems = fetch_subsystems(body)
      
    for sys in ip_sub_systems:
        try:
            if sys in FMEA.keys(): 
                IP_attr_list = fetch_attributes(body, sys)
                MD_params = FMEA[sys]["parameters"].keys()
                
                for attribute in IP_attr_list:
                    if attribute in MD_params:
                        P1,P2 = compute_attribute(IP_attr_list, attribute, FMEA, sys, body)                       
                        res1_dict.update(P1)
                        res2_dict.update(P2)
                        l1.append(MD_params)
                        all_params_dict = res1_dict
                    else:
                        raise Attribute_error(f"Invalid Attribute request: {attribute} in {sys}")

            else:
                raise SS_error(f"Invalid Sub System request: {sys}")
          
        except SS_error as se:
            raise SS_error(f"Invalid Sub System request: {sys}")
        except Attribute_error as ae:
            raise Attribute_error(f"Invalid Attribute request: {attribute} in {sys}")
        except typeError as te:
            raise typeError(f"{te}")
            
    output_list = []
    for system in FMEA.keys():
        for fault in FMEA[system]["faults"]:
            fault_logic = fault["fault_logic"]
            name = fault["fault_name"]
            fault_id = fault["fault_id"]
            causes = fault["cause"]
            effects = fault["effects"]
            actions = fault["actions"]
            severity = fault["severity"]
            
            replaced_logic,symptoms = replace_variables(fault_logic,res1_dict,res2_dict) 
            # l1.append(replaced_logic)
            # l2.append(symptoms)
            
            output = eval(replaced_logic)
            if (output):
                    update = {system:{"fault_id":fault_id,
                             "fault_name" : name,
                             "fault_status":"Active",
                             "severity":severity,
                             "causes":causes,
                             "effects":effects,
                             "actions":actions,
                             "symptoms": symptoms }}
                    output_list.append(update) 
            else:
                    update = {system:{"fault_id" : fault_id,
                           "fault_name" : name,
                           "fault_status": "Inactive"}}
                    output_list.append(update) 
    
    # return f"{l2}"
    return f"{output_list}"

 

