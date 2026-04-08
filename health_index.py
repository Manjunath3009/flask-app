import json
import re
import datetime

class SS_error(Exception):
    pass

class Attribute_error(Exception):
    pass

def fetch_op_config_params(config_json):
    op_config_params = {}
    for prop in config_json:
        if prop["propertyType"] == "Computed":
            op_config_params.update({prop['name']: prop['propertyId']})
    return op_config_params


def fetch_ip_config_params(config_json):
    config_params = {}
    for prop in config_json:
        if prop["propertyType"] == "Raw":
            config_params.update({prop['name']: prop['propertyId']})
    return config_params

def get_attribute_names(HI_MD):
    attribute_names = set()
    for system in list(HI_MD.keys()):
        for fault in HI_MD[system]["faults"]:
            attributes = fault["attributes"]
            attribute_names.update(attributes.keys())

    return attribute_names  # sorted list for consistency

def get_attrs_weight_sum(attributes):
    sum = 0
    for attribute in attributes:
        sum = sum + attributes[attribute]["weightage"]
    return sum


def fetch_all_ss_weight_sum(HI_MD):
    sum = 0
    for sys in HI_MD.keys():
        sum = sum + HI_MD[sys]["subs_weight"]
    return sum


def fetch_attr_value(args,sys, attribute):
    body = args.get("body")

    if sys not in body:
        raise SS_error(f"Invalid Sub System request: {sys}")

    if attribute not in body[sys]:
        raise AttributeError(f"Invalid Attribute request: {attribute} in {sys}")

    attribute_val = body[sys][attribute]["actual_value"]
    return attribute_val



def fetch_subs_max_score(HI_MD, sys):
    subsystem = sys
    max_score = 5
    faults = HI_MD[sys]["faults"]
    Subsystem_weight = float(HI_MD[sys]["subs_weight"]) / 100
    sys_max_score_sum = []

    # looping for faults in each subsystems
    for fault in faults:
        fault_name = fault["fault_name"]
        fault_id = fault["fault_id"]
        attributes = fault["attributes"]
        # weightsum = get_attrs_weight_sum(attributes)
        attr_max_weight_sum = []

        # looping for fault attribute in each fault
        for attribute in attributes:
            attribute_name = attribute
            limit = attributes[attribute]["limit"]  # fetch limit of attribute from master data
            limit_value = attributes[attribute]["limit_value"]  # fetch limit_value of attribute from master data
            weight = attributes[attribute]["weightage"]
            weight_score = weight * max_score
            attr_max_weight_sum.append(weight_score)

        ssystemFaultSum = sum(attr_max_weight_sum)
        sys_max_score_sum.append(ssystemFaultSum)

    return float(sum(sys_max_score_sum) * Subsystem_weight)


def dump_output(output, subsystem):
  
    output_update = {
      subsystem: output	
    }
    return output_update


def main(args: dict, query_params: dict) -> dict:
    HI_MD = {
	"bearing_system": {
		"subs_id": 1,
		"subs_weight": 25,
		"faults": [
			{
				"fault_id": "RTR-Mech-4",
				"fault_logic": "(B6 or B7) and (B9 or B10)",
				"fault_name": "Rotor Anomaly",
				"attributes": {
					"k_de_radial_vibration_overall_x": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_de_radial_vibration_overall_y": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_nde_radial_vibration_overall_x": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_nde_radial_vibration_overall_y": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					}
				},
				"rpn": 32
			},
			{
				"fault_id": "BRG-LO-1",
				"fault_logic": "(B16) and (B6 or B7 or B8 or B9 or B10 or B11 or B12 or B14 or B15)",
				"fault_name": "Thrust/Radial Bearing Anomaly due to Lube Oil Pressure",
				"attributes": {
					"lo_header_pressure": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 76
					},
					"k_de_radial_vibration_overall_x": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_de_radial_vibration_overall_y": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_de_radial_bearing_temperature": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_nde_radial_vibration_overall_x": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_nde_radial_vibration_overall_y": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_nde_radial_bearing_temperature": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"thrust_bearing_active_side_gap": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_thrust_bearing_temperature_active_side": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_thrust_bearing_temperature_inactive_side": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					}
				},
				"rpn": 32
			},
			{
				"fault_id": "BRG-LO-2",
				"fault_logic": "(B17) and (B6 or B7 or B8 or B9 or B10 or B11 or B12 or B14 or B15)",
				"fault_name": "Thrust/Radial Bearing Anomaly due to Lube Oil Temperature",
				"severity": "Important",
				"attributes": {
					"lo_header_temperature": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 72
					},
					"k_de_radial_vibration_overall_x": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_de_radial_vibration_overall_y": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_de_radial_bearing_temperature": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_nde_radial_vibration_overall_x": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_nde_radial_vibration_overall_y": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_nde_radial_bearing_temperature": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"thrust_bearing_active_side_gap": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_thrust_bearing_temperature_active_side": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_thrust_bearing_temperature_inactive_side": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					}
				},
				"rpn": 18
			},
			{
				"fault_id": "BRG-LOQ-3",
				"fault_logic": "(B18) and (B6 or B7 or B8 or B9 or B10 or B11 or B12 or B14 or B15)",
				"fault_name": "Thrust/Radial Bearing Anomaly due to Lube Oil Quality",
				"attributes": {
					"lo_viscosity": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 74
					},
					"k_de_radial_vibration_overall_x": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_de_radial_vibration_overall_y": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_de_radial_bearing_temperature": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_nde_radial_vibration_overall_x": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_nde_radial_vibration_overall_y": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_nde_radial_bearing_temperature": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"thrust_bearing_active_side_gap": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_thrust_bearing_temperature_active_side": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_thrust_bearing_temperature_inactive_side": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					}
				},
				"rpn": 32
			},
			{
				"fault_id": "BRG-Mech-1",
				"fault_logic": "(B12 or B13 or B14 or B15) and not (((B16) and (B6 or B7 or B8 or B9 or B10 or B11 or B12 or B14 or B15)) and ((B17) and (B6 or B7 or B8 or B9 or B10 or B11 or B12 or B14 or B15)) and ((B18) and (B6 or B7 or B8 or B9 or B10 or B11 or B12 or B14 or B15)))",
				"fault_name": "Thrust Bearing Anomaly due to Mech Issue",
				"attributes": {
					"thrust_bearing_active_side_gap": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"thrust_bearing_inactive_side_gap": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_thrust_bearing_temperature_active_side": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_thrust_bearing_temperature_inactive_side": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"lo_header_pressure": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"lo_header_temperature": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"lo_viscosity": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_de_radial_vibration_overall_x": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_de_radial_vibration_overall_y": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_de_radial_bearing_temperature": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_nde_radial_vibration_overall_x": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_nde_radial_vibration_overall_y": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_nde_radial_bearing_temperature": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					}
				},
				"rpn": 32
			},
			{
				"fault_id": "BRG-Mech-2",
				"fault_logic": "(B6 or B7 or B8) and not ((B6 or B7) and (B9 or B10))",
				"fault_name": "DE Radial Bearing Anomaly due to Mech Issue",
				"attributes": {
					"k_de_radial_vibration_overall_x": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_de_radial_vibration_overall_y": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_de_radial_bearing_temperature": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_nde_radial_vibration_overall_x": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_nde_radial_vibration_overall_y": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					}
				},
				"rpn": 32
			},
			{
				"fault_id": "BRG-Mech-3",
				"fault_logic": "(B9 or B10 or B11) and not ((B6 or B7) and (B9 or B10))",
				"fault_name": "NDE Radial Bearing Anomaly due to Mech Issue",
				"attributes": {
					"k_de_radial_vibration_overall_x": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_de_radial_vibration_overall_y": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_nde_radial_vibration_overall_x": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_nde_radial_vibration_overall_y": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"k_nde_radial_bearing_temperature": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					}
				},
				"rpn": 32
			}
		]
	    },
	"dry_gas_seal_system": {
		"subs_id": 2,
		"subs_weight": 20,
		"faults": [
			{
				"fault_id": "dgs_1",
				"fault_logic": "S9",
				"fault_name": "Primary seal gas filter anomaly",
				"attributes": {
					"dp_over_seal_gas_filter": {
						"limit": "High",
						"weightage": 3,
						"limit_value": 3,
						"expected_value": 50
					}
				},
				"rpn": 32
			},
			{
				"fault_id": "dgs_2",
				"fault_logic": "S13",
				"fault_name": "Buffer gas filter anomaly",
				"attributes": {
					"buffer_gas_filter_dp": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					}
				},
				"rpn": 18
			},
			{
				"fault_id": "dgs_3",
				"fault_logic": "(S6 or S14)",
				"fault_name": "PDCV malfuction",
				"severity": "Important",
				"attributes": {
					"reference_line_dp": {
						"limit": "High",
						"weightage": 1,
						"limit_value": 1,
						"expected_value": 50
					},
					"pdcv_valve_opening": {
						"limit": "High",
						"weightage": 1,
						"limit_value": 1,
						"expected_value": 50
					}
				},
				"rpn": 8
			},
			{
				"fault_id": "dgs_4",
				"fault_logic": "S10 or S11",
				"fault_name": "Outboard Seal Malfuction",
				"attributes": {
					"primary_vent_pressure_flow": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"secondary_vent_pressure_flow": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					}
				},
				"rpn": 48
			},
			{
				"fault_id": "dgs_5",
				"fault_logic": "(S10)",
				"fault_name": "Inboard Seal malfuction",
				"attributes": {
					"primary_vent_pressure_flow": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					}
				},
				"rpn": 48
			},
			{
				"fault_id": "dgs_6",
				"fault_logic": "(S7)",
				"fault_name": "Primary seal temperature anomaly",
				"attributes": {
					"primary_seal_gas_supply_temperature": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					}
				},
				"rpn": 27
			},
			{
				"fault_id": "dgs_7",
				"fault_logic": "(S8)",
				"fault_name": "Primary seal gas supply anomaly",
				"attributes": {
					"primary_seal_gas_supply_pressure_flow": {
						"limit": "High",
						"weightage": 3,
						"limit_value": 3,
						"expected_value": 50
					}
				},
				"rpn": 8
			},
			{
				"fault_id": "dgs_8",
				"fault_logic": "(S12 or S15 or S16)",
				"fault_name": "Buffer gas supply anomaly",
				"attributes": {
					"buffer_gas_supply_pressure_flow": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"secondary_supply_pcv_opening": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"buffer_gas_pcv_opening": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					}
				},
				"rpn": 8
			}
		]
	    },
	"performance": {
		"subs_id": 3,
		"subs_weight": 20,
		"faults": [
			{
				"fault_id": "per_1",
				"fault_logic": "(P10 or P17 or P18)",
				"fault_name": "Comp Inlet Supply anomaly",
				"attributes": {
					"suction_flow": {
						"limit": "High",
						"weightage": 3,
						"limit_value": 3,
						"expected_value": 50
					},
					"compressor_inlet_temperature": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"compressor_inlet_pressure": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					}
				},
				"rpn": 18
			},
			{
				"fault_id": "per_2",
				"fault_logic": "P22",
				"fault_name": "Inlet Filter Anomaly ",
				"attributes": {
					"inlet_filter_dp": {
						"limit": "High",
						"weightage": 3,
						"limit_value": 3,
						"expected_value": 50
					}
				},
				"rpn": 12
			},
			{
				"fault_id": "per_3",
				"fault_logic": "(P13 or P14 or P19) and  not (P10 or P17 or P18))",
				"fault_name": "Compressor Performance degradation",
				"severity": "Important",
				"attributes": {
					"efficiency_deviation_expected_actual": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"compressor_discharge_temperature": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"compressor_discharge_pressure": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"suction_flow": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"compressor_inlet_temperature": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"compressor_inlet_pressure": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					}
				},
				"rpn": 18
			},
			{
				"fault_id": "per_4",
				"fault_logic": "(P21 or P20) and P6",
				"fault_name": "Liquid slugs",
				"attributes": {
					"suction_scrubber_level": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"k_de_radial_vibration_overall_x": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"k_nde_radial_vibration_overall_x": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					}
				},
				"rpn": 18
			},
			{
				"fault_id": "per_5",
				"fault_logic": "(P13)",
				"fault_name": "Fouling/corrosion/erosion risk",
				"attributes": {
					"efficiency_deviation_expected_actual": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					}
				},
				"rpn": 18
			},
			{
				"fault_id": "per_6",
				"fault_logic": "(P15 or P16)",
				"fault_name": "IGV/Suction throttle valve malfunction",
				"attributes": {
					"igv_angle_actuator_position": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"suction_throttling_valve_percent": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					}
				},
				"rpn": 18
			},
			{
				"fault_id": "per_7",
				"fault_logic": "(P7 or P8)",
				"fault_name": "Interstage Cooler anomaly",
				"attributes": {
					"interstage_cooler_gas_outlet_temperature": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"interstage_cooler_temp_control_valve_opening": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					}
				},
				"rpn": 18
			},
			{
				"fault_id": "per_8",
				"fault_logic": "(P9)",
				"fault_name": "Interstage Separator anomaly",
				"attributes": {
					"interstage_separator_level": {
						"limit": "High",
						"weightage": 3,
						"limit_value": 3,
						"expected_value": 50
					}
				},
				"rpn": 12
			}
		]
	    },
	"lo_system": {
		"subs_id": 4,
		"subs_weight": 20,
		"faults": [
			{
				"fault_id": "loq_1",
				"fault_logic": "(L4 or L5 or L6)",
				"fault_name": "Comp Inlet Supply anomaly",
				"attributes": {
					"lo_viscosity": {
						"limit": "High",
						"weightage": 3,
						"limit_value": 3,
						"expected_value": 5
					},
					"lo_tan": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"lo_composition_analysis": {
						"limit": "High",
						"weightage": 1,
						"limit_value": 1,
						"expected_value": 50
					}
				},
				"rpn": 18
			},
			{
				"fault_id": "lof_2",
				"fault_logic": "L3",
				"fault_name": "Lube Oil Filter Anomaly",
				"attributes": {
					"oil_filter_dp": {
						"limit": "High",
						"weightage": 3,
						"limit_value": 3,
						"expected_value": 10
					}
				},
				"rpn": 12
			},
			{
				"fault_id": "lop_p_3",
				"fault_logic": "((L1 and (L9 or L10 or L11)) and (L14 or L15))",
				"fault_name": "Loss of pressure due to Pump anomaly",
				"severity": "Important",
				"attributes": {
					"lo_header_pressure": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"lo_pumps_discharge_pressure": {
						"limit": "High",
						"weightage": 3,
						"limit_value": 3,
						"expected_value": 50
					},
					"lube_oil_pcv_position": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"lube_oil_return_flow_rate": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"main_lube_oil_pump_current_run_signal": {
						"limit": "High",
						"weightage": 1,
						"limit_value": 1,
						"expected_value": 50
					},
					"aux_lube_oil_pump_current_run_signal": {
						"limit": "High",
						"weightage": 1,
						"limit_value": 1,
						"expected_value": 50
					}
				},
				"rpn": 18
			},
			{
				"fault_id": "loc_co_4",
				"fault_logic": "(L2 and L13)",
				"fault_name": "Loss of cooling due to Cooler Anomaly",
				"attributes": {
					"lo_header_temperature": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"delta_temperature_lo_tank_vs_lo_cooler_discharge": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					}
				},
				"rpn": 18
			},
			{
				"fault_id": "loc_ac_5",
				"fault_logic": "(L2 and L17 and L18)",
				"fault_name": "Loss of cooling Due to Fan-Motor Issue",
				"attributes": {
					"lo_header_temperature": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 5
					},
					"air_cooler_fan_1_run_status": {
						"limit": "High",
						"weightage": 1,
						"limit_value": 1,
						"expected_value": 50
					},
					"air_cooler_fan_2_run_status": {
						"limit": "High",
						"weightage": 1,
						"limit_value": 1,
						"expected_value": 50
					}
				},
				"rpn": 18
			}
		]
	    },
	"transmission": {
		"subs_id": 5,
		"subs_weight": 15,
		"faults": [
			{
				"fault_id": "gbb_1",
				"fault_logic": "(T6 or T7 or T17 or T18 or T23) and not ((T6 or T7) and (T8 or T9)) or (T23 or T24)",
				"fault_name": "LSS GB DE RB anomaly",
				"attributes": {
					"lss_de_radial_vibration_overall_x": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"lss_de_radial_vibration_overall_y": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"lss_de_radial_bearing_temperature_a": {
						"limit": "High",
						"weightage": 1,
						"limit_value": 1,
						"expected_value": 50
					},
					"lss_de_radial_bearing_temperature_b": {
						"limit": "High",
						"weightage": 1,
						"limit_value": 1,
						"expected_value": 50
					},
					"lss_de_casing_vibration": {
						"limit": "High",
						"weightage": 1,
						"limit_value": 1,
						"expected_value": 50
					},
					"lss_nde_radial_vibration_overall_x": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"lss_nde_radial_vibration_overall_y": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"lss_nde_casing_vibration": {
						"limit": "High",
						"weightage": 1,
						"limit_value": 1,
						"expected_value": 50
					}
				},
				"rpn": 18
			},
			{
				"fault_id": "gbb_2",
				"fault_logic": "(T8 or T9 or T15 or T16 or T24) and not ((T6 or T7) and (T8 or T9)) or (T23 or T24)",
				"fault_name": "LSS GB NDE RB anomaly",
				"attributes": {
					"lss_nde_radial_vibration_overall_x": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"lss_nde_radial_vibration_overall_y": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"lss_nde_radial_bearing_temperature_a": {
						"limit": "High",
						"weightage": 1,
						"limit_value": 1,
						"expected_value": 50
					},
					"lss_nde_radial_bearing_temperature_b": {
						"limit": "High",
						"weightage": 1,
						"limit_value": 1,
						"expected_value": 50
					},
					"lss_nde_casing_vibration": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"lss_de_radial_vibration_overall_x": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"lss_de_radial_vibration_overall_y": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"lss_de_casing_vibration": {
						"limit": "High",
						"weightage": 1,
						"limit_value": 1,
						"expected_value": 50
					}
				},
				"rpn": 18
			},
			{
				"fault_id": "gbb_3",
				"fault_logic": "(T11 or T12 or T21 or T22 or T25) and not (((T11 or T12) and (T13 or T14)) or (T25 and T26))",
				"fault_name": "HSS GB DE RB anomaly",
				"attributes": {
					"hss_de_radial_vibration_overall_x": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"hss_de_radial_vibration_overall_y": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"hss_de_radial_bearing_temperature_a": {
						"limit": "High",
						"weightage": 1,
						"limit_value": 1,
						"expected_value": 50
					},
					"hss_de_radial_bearing_temperature_b": {
						"limit": "High",
						"weightage": 1,
						"limit_value": 1,
						"expected_value": 50
					},
					"hss_de_casing_vibration": {
						"limit": "High",
						"weightage": 1,
						"limit_value": 1,
						"expected_value": 50
					},
					"hss_nde_radial_vibration_overall_x": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"hss_nde_radial_vibration_overall_y": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"hss_nde_casing_vibration": {
						"limit": "High",
						"weightage": 1,
						"limit_value": 1,
						"expected_value": 50
					}
				},
				"rpn": 16
			},
			{
				"fault_id": "gbb_4",
				"fault_logic": "(T13 or T14 or T19 or T20 or T26) and not (((T11 or T12) and (T13 or T14)) or (T25 and T26))",
				"fault_name": "HSS GB NDE RB anomaly",
				"attributes": {
					"hss_nde_radial_vibration_overall_x": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"hss_nde_radial_vibration_overall_y": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"hss_nde_radial_bearing_temperature_a": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"hss_nde_radial_bearing_temperature_b": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"hss_nde_casing_vibration": {
						"limit": "High",
						"weightage": 1,
						"limit_value": 1,
						"expected_value": 50
					},
					"hss_de_radial_vibration_overall_x": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"hss_de_radial_vibration_overall_y": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"hss_de_casing_vibration": {
						"limit": "High",
						"weightage": 1,
						"limit_value": 1,
						"expected_value": 50
					}
				},
				"rpn": 8
			},
			{
				"fault_id": "gbb_5",
				"fault_logic": "((T6 or T7) and (T8 or T9)) or (T23 or T24)",
				"fault_name": "LSS Shaft anomaly",
				"attributes": {
					"lss_de_radial_vibration_overall_x": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"lss_de_radial_vibration_overall_y": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"lss_nde_radial_vibration_overall_x": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"lss_nde_radial_vibration_overall_y": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"lss_de_casing_vibration": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"lss_nde_casing_vibration": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					}
				},
				"rpn": 12
			},
			{
				"fault_id": "gbb_6",
				"fault_logic": "(((T11 or T12) and (T13 or T14)) or (T25 and T26))",
				"fault_name": "HSS Shaft anomaly",
				"attributes": {
					"hss_de_radial_vibration_overall_x": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"hss_de_radial_vibration_overall_y": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"hss_nde_radial_vibration_overall_x": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"hss_nde_radial_vibration_overall_y": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"hss_de_casing_vibration": {
						"limit": "High",
						"weightage": 1,
						"limit_value": 1,
						"expected_value": 50
					},
					"hss_nde_casing_vibration": {
						"limit": "High",
						"weightage": 1,
						"limit_value": 1,
						"expected_value": 50
					}
				},
				"rpn": 6
			},
			{
				"fault_id": "gbb_7",
				"fault_logic": "T27 or T28 or T29 or T30)",
				"fault_name": "LSS GB thrust bearing anomaly",
				"attributes": {
					"lss_thrust_bearing_active_side_gap": {
						"limit": "High or Low",
						"weightage": 1,
						"limit_value": 1,
						"expected_value": 50
					},
					"lss_thrust_bearing_inactive_side_gap": {
						"limit": "High or Low",
						"weightage": 1,
						"limit_value": 1,
						"expected_value": 50
					},
					"lss_thrust_bearing_active_side_temp": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"lss_thrust_bearing_inactive_side_temp": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					}
				},
				"rpn": 27
			},
			{
				"fault_id": "gbb_8",
				"fault_logic": "(T31 or T32 or T33 or T34)",
				"fault_name": "HSS GB thrust bearing anomaly",
				"attributes": {
					"hss_thrust_bearing_active_side_gap": {
						"limit": "High or Low",
						"weightage": 1,
						"limit_value": 1,
						"expected_value": 50
					},
					"hss_thrust_bearing_inactive_side_gap": {
						"limit": "High or Low",
						"weightage": 1,
						"limit_value": 1,
						"expected_value": 50
					},
					"hss_thrust_bearing_active_side_temp": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					},
					"hss_thrust_bearing_inactive_side_temp": {
						"limit": "High",
						"weightage": 2,
						"limit_value": 2,
						"expected_value": 50
					}
				},
				"rpn": 27
			}
		]
	    }
    }
    ip_sub_systems = list(HI_MD.keys())

    ip_params_list = get_attribute_names(HI_MD)
    #print(ip_params_list)
    #op_params_list = fetch_op_config_params(sesuite_helper.config_json['properties'])
    output_list = []
    
    all_ss_weight = fetch_all_ss_weight_sum(HI_MD)
    ss_scoresum = []
    all_ss_fault_score_sum = []
    bad_health_sum = []
    # looping for subsystems
    for sys in ip_sub_systems:
        BadHIobj = {}
        Subsystem_name = sys
        Subsystem_id = HI_MD[sys]["subs_id"]
        Subsystem_weight = HI_MD[sys]["subs_weight"]
        faults = HI_MD[sys]["faults"]

        F_score_to_weight = []  # to store sum of score * weight of a single fault
        fault_score_sum = []

        # looping for faults in each subsystems
        for fault in faults:
            fault_name = fault["fault_name"]
            fault_id = fault["fault_id"]
            attributes = fault["attributes"]
            rpn = float(fault["rpn"])
            F_weightsum = get_attrs_weight_sum(attributes)  # sum of weightage of all attributes in a single fault

            # looping for fault attribute in each fault
            for attribute in attributes:
                attribute_name = attribute
                limit = attributes[attribute]["limit"]  # fetch limit of attribute from master data
                limit_value = float(attributes[attribute]["limit_value"])  # fetch limit_value of attribute from master data
                A_weight = attributes[attribute]["weightage"]  # fetch weight of attribute from master data
                expected_value = float(attributes[attribute]["expected_value"])  # fetch expected_value of attribute from master data
                actual_value = float(fetch_attr_value( args,sys,attribute))  # fetch actual_value of attribute from request json

                try:
                    scorefactor = abs(((limit_value - actual_value) / (limit_value - expected_value)) * 100)  # calculation of score factor
                except:
                    scorefactor = 1

                # calculation of score using score factor
                if scorefactor >= 0 and scorefactor < 20:
                    score = 1
                elif scorefactor >= 20 and scorefactor < 40:
                    score = 2
                elif scorefactor >= 40 and scorefactor < 60:
                    score = 3
                elif scorefactor >= 60 and scorefactor < 80:
                    score = 4
                else:
                    score = 5
                A_score = score
                A_score_to_weight = A_score * A_weight  # multiply score and weight of each attribute of the single fault
                F_score_to_weight.append(A_score_to_weight)  # store score_to_weight of all attributes of a single fault

            fsum = sum(F_score_to_weight)  # sum all the score_to_weight of all faults in subsystem
            wsum = F_weightsum  # extracted weight sum of all attributes of a single fault
            f_value = (fsum / wsum) * (1 - (rpn / 125))  # calculating HI of single fault
            fault_score_sum.append(f_value)  # appending calculated HI of single faults to list, so that it holds all faults of subs

        sub_fault_score = sum(fault_score_sum)  # taking sum of appended list
        ss_weight = Subsystem_weight  # extracted subsystem weight

        no_of_faults = int(len(HI_MD[sys]["faults"]))
        ss_value = (sub_fault_score * ss_weight) / no_of_faults
        all_ss_fault_score_sum.append(ss_value)  # appending calculated HI of single subs to list, so that it holds all faults of all subs
        actual_ss_score = ss_value
        design_subs_score = fetch_subs_max_score(HI_MD, sys)  # fetch max subsystem score
        ss_bad_health = abs(design_subs_score - actual_ss_score)
        # bad_health_sum.append(ss_bad_health)

        output_update = dump_output(ss_bad_health, sys)
        output_list.append(output_update)

        # print(actual_ss_score)
        # print(design_subs_score)
        # print(sys , ss_bad_health)
        # bad_health_sum.append(ss_bad_health)

        # if ss_value > 100:
        #     ss_value = 100
    hi = sum(all_ss_fault_score_sum) / 5
    good_hi = hi / 100
    bad_hi = 10 - good_hi
    output_update = dump_output(good_hi, "good_health")
    output_list.append(output_update)
    output_update = dump_output(bad_hi, "bad_health")
    output_list.append(output_update)
    # print(good_hi)
    # print(bad_hi)
    # print(bad_health_sum)
    return output_list
    # sesuite_helper.SaveData(data=output_list)


if __name__ == "__main__":
    main()
