import math

class UnitError(Exception):
    pass

class CustomAttributeError(Exception):
    pass

class DatatypeError(Exception):
    pass

def convert_temp(val, unit, attr, req):
    """
    Converts temperature from the given unit to Celsius (SI unit).

    Args:
    - val (float): Temperature value to be converted.
    - unit (str): Unit of temperature (`°K`, `°F`, `°C`).
    - attr (str): Attribute name for which conversion is performed.
    - req (str): Request name indicating the context of conversion.

    Returns:
    - float: Converted temperature value in Celsius.

    Raises:
    - UnitError: If an invalid temperature unit is provided.
    """
    try:
        if unit == "°K":
            return val - 273.15
        elif unit == "°F":
            return (val - 32) * (5 / 9)
        elif unit == "°C":
            return val
        else:
            raise UnitError(f"Invalid unit request: {unit} for attribute {attr} in {req}. Accepted only: °K, °F, or °C as temperature units for calculation")
    except UnitError as ue:
        raise UnitError(f"Error converting temperature: {ue}")


def convert_vol_flow_rate(val, unit, attr, req):
    """
    Converts volume flow rate from the given unit to m³/hr (SI unit).

    Args:
    - val (float): Volume flow rate value to be converted.
    - unit (str): Unit of volume flow rate (`GPM`, `CFM`, `m³/hr`).
    - attr (str): Attribute name for which conversion is performed.
    - req (str): Request name indicating the context of conversion.

    Returns:
    - float: Converted volume flow rate value in m³/hr.

    Raises:
    - UnitError: If an invalid volume flow rate unit is provided.
    """
    try:
        if unit == "GPM":
            return val * 227.1247
        elif unit == "CFM":
            return val * 1.699
        elif unit == "m³/hr":
            return val
        else:
            raise UnitError(f"Invalid unit request: {unit} for attribute: {attr} in {req}. Accepted only: GPM, CFM, or m³/hr as volume flow units for calculation")
    except UnitError as ue:
        raise UnitError(f"Error converting volume flow rate: {ue}")


def convert_mass_flow_rate(val, unit, attr, req):
    """
    Converts mass flow rate from the given unit to kg/s (SI unit).

    Args:
    - val (float): Mass flow rate value to be converted.
    - unit (str): Unit of mass flow rate (`kg/hr`, `kg/s`).
    - attr (str): Attribute name for which conversion is performed.
    - req (str): Request name indicating the context of conversion.

    Returns:
    - float: Converted mass flow rate value in kg/s.

    Raises:
    - UnitError: If an invalid mass flow rate unit is provided.
    """
    try:
        if unit == "kg/hr":
            return val / 3600
        elif unit == "kg/s":
            return val
        else:
            raise UnitError(f"Invalid unit request: {unit} for attribute: {attr} in {req}. Accepted only: kg/hr, kg/s as mass flow units for calculation")
    except UnitError as ue:
        raise UnitError(f"Error converting mass flow rate: {ue}")


def convert_pressure(val, unit, attr, req):
    """
    Converts pressure from the given unit to bar (SI unit).

    Args:
    - val (float): Pressure value to be converted.
    - unit (str): Unit of pressure (`kgf/cm²`, `PSI`, `bar`).
    - attr (str): Attribute name for which conversion is performed.
    - req (str): Request name indicating the context of conversion.

    Returns:
    - float: Converted pressure value in bar.

    Raises:
    - UnitError: If an invalid pressure unit is provided.
    """
    try:
        if unit == "kgf/cm²":
            return val * 0.980665
        elif unit == "PSI":
            return val * 0.0689476
        elif unit == "bar":
            return val
        else:
            raise UnitError(f"Invalid unit request: {unit} for attribute: {attr} in {req}. Accepted only: kgf/cm², PSI, or bar as pressure units for calculation")
    except UnitError as ue:
        raise UnitError(f"Error converting pressure: {ue}")


def update_output(req, design_val, operating_val, res_unit, deviation_val):
    """
    Updates the output dictionary with calculated values and units.

    Args:
    - req (str): Request name indicating the KPI being calculated.
    - design_val (float): Design value for the KPI.
    - operating_val (float): Operating value calculated for the KPI.
    - res_unit (str): Unit of measurement for the KPI result.
    - deviation_val (float): Deviation percentage from the design value.

    Returns:
    - dict: Updated output dictionary containing values and units for the KPI.

    """
    design_val = round(design_val, 3)
    operating_val = round(operating_val, 3)
    deviation_val = round(deviation_val, 3)
    
    update = {
        "values": {
            f"{req}_design": design_val,
            f"{req}_operating": operating_val,
            f"{req}_deviation": deviation_val
        },
        "units": {
            f"{req}_design": f"{res_unit}",
            f"{req}_operating": f"{res_unit}",
            f"{req}_deviation": "%"
        }
    }
    return update


def fetch_values(body, attri, req):
    """
    Fetches the value of the specified attribute from the request body.

    Args:
    - body (dict): The request body containing parameters and units.
    - attri (str): Attribute name whose value needs to be fetched.
    - req (str): Request name indicating the context of the attribute.

    Returns:
    - float: Value of the specified attribute.

    Raises:
    - CustomAttributeError: If the specified attribute is missing in the request body.
    - DatatypeError: If the attribute value is not of type int or float.
    """
    try:
        value = body["request"][req]["parameters"][attri]
        if isinstance(value, (int, float)):
            return value
        else:
            raise DatatypeError(f"Invalid datatype {type(value)}. Accepted only: int/float as datatype for attribute: {attri} values in {req}")
    except KeyError as ke:
        raise CustomAttributeError(f"Missing attribute: {attri} in {req}")
    except (DatatypeError, CustomAttributeError) as e:
        raise e


def fetch_units(body, attri, req,units):
    """
    Fetches the unit of the specified attribute from the request body.

    Args:
    - body (dict): The request body containing parameters and units.
    - attri (str): Attribute name whose unit needs to be fetched.
    - req (str): Request name indicating the context of the attribute.

    Returns:
    - str: Unit of the specified attribute.

    Raises:
    - CustomAttributeError: If the specified attribute unit is missing in the request body.
    - DatatypeError: If the unit value is not of type string.
    """
    try:
        unit = body["request"][req]["units"][attri]
        if isinstance(unit, str):
            accepted_units = units[req][attri]
            if unit in accepted_units:
                return unit
            else:
                raise UnitError(f"Invalid Unit : {unit}. Accepted only: {accepted_units} as units for attribute: {attri} under units in requested KPI {req}")
        else:
            raise DatatypeError(f"Invalid datatype {type(unit)}. Accepted only: string as datatype for attribute: {attri} units in {req}")
    except KeyError as ke:
        raise CustomAttributeError(f"Missing attribute: {attri} in {req}")
    except (DatatypeError, CustomAttributeError,UnitError) as e:
        raise e


def main(args: dict[str, dict[str, any]], query_params: dict[str, dict[str, any]]):
    """
    Main function to calculate various Key Performance Indicators (KPIs) based on the provided request.

    Args:
    - args (dict): Dictionary containing the request body with parameters and units.
    - query_params (dict): Dictionary.

    Returns:
    - list: List of dictionaries containing calculated KPI values and units.

    Raises:
    - ValueError: If an invalid KPI request is provided.
    - CustomAttributeError: If any required attribute is missing in the request body.
    """
    KPIs = ["pressure_ratio", "polytropic_efficiency", "shaft_power", "adiabatic_efficiency", "surge_margin", "power_consumption", "polytropic_exponent", "polytropic_head"]
    units = {
            "pressure_ratio": {
                "Po": ["kgf/cm²","PSI","bar"],
                "Pi": ["kgf/cm²","PSI","bar"],
                "design": ["","-"]
                },
            "polytropic_efficiency": {
                    "Ki": ["","-"],
                    "Ko": ["","-"],
                    "n" : ["","-"],
                    "design": ["%"]
                },
            "shaft_power":{
                    "Fair": ["kg/hr","kg/s"],
                    "H1": ["kJ/kg"],
                    "H2": ["kJ/kg"],
                    "Nmech": ["%"],
                    "design": ["kw"]
                },
            "surge_margin": {
                "Current_flow": ["CFM","GPM","m³/hr"],
                "Surge_inline_flow": ["CFM","GPM","m³/hr"],
                "design": ["%"]
                },
            "power_consumption": {
                "V": ["V"],
                "I": ["A"],
                "Power_factor": ["","-"],
                "design": ["kw"]
                },
            "polytropic_exponent": {
                "Po": ["kgf/cm²","PSI","bar"],
                "Pi": ["kgf/cm²","PSI","bar"],
                "Rowo": ["kg/m³"],
                "Rowi": ["kg/m³"],
                "design": ["","-"]
                },
            "adiabatic_efficiency": {
                "Ki": ["","-"],
                "Ko": ["","-"],
                "Pi": ["kgf/cm²","PSI","bar"],
                "Po": ["kgf/cm²","PSI","bar"],
                "n": ["","-"],
                "design": ["%"]
                },
            "polytropic_head": {
                "Zi": ["","-"],
                "Zo": ["","-"],
                "R": ["kJ/kg.K"],
                "Mw": ["g/mol"],
                "Po": ["kgf/cm²","PSI","bar"],
                "Pi": ["kgf/cm²","PSI","bar"],
                "Ti": ["°F","°C","°K"],
                "n": ["","-"],
                "design": ["kJ/kg"]
                }
    }
    output_list = []
    body = args.get("body")
    requests = body["request"].keys()

    try:
        for req in requests:
            if req in KPIs:
                if req == "pressure_ratio":
                    try:
                        Po = fetch_values(body, "Po", req)
                        Pi = fetch_values(body, "Pi", req)
                        PR = fetch_values(body, "design", req)

                        Po_unit = fetch_units(body, "Po", req,units)  
                        Pi_unit = fetch_units(body, "Pi", req,units)  
                        PR_design_unit = fetch_units(body, "design", req,units)  

                        Po_val = convert_pressure(Po, Po_unit, "Po",req)
                        Pi_val = convert_pressure(Pi, Pi_unit, "Pi",req)
                        PR_val = PR

                        res_unit = ""
                        
                        PR_operating = Po_val / Pi_val
                        PR_deviation = abs((PR_val - PR_operating) / PR_val) * 100
                        output_update1 = update_output(req, PR_val, PR_operating, res_unit, PR_deviation)
                        output_list.append(output_update1)
                        
                    except CustomAttributeError as ae:
                        raise CustomAttributeError(f"Error calculating {req}: Missing: {ae}")

                elif req == "polytropic_efficiency":
                    try:
                        Ki = fetch_values(body, "Ki", req)
                        Ko = fetch_values(body, "Ko", req)
                        n = fetch_values(body, "n", req)
                        PE_design = fetch_values(body, "design", req)

                        Ki_unit = fetch_units(body, "Ki", req,units)  
                        Ko_unit = fetch_units(body, "Ko", req,units)  
                        n_unit = fetch_units(body, "n", req,units)  
                        PE_design_unit = fetch_units(body, "design", req,units)  

                        Ki_val = Ki
                        Ko_val = Ko
                        n_val = n
                        PE_design_val = PE_design

                        Kavg = (Ki_val + Ko_val) / 2
                        PE_operating = abs(((Kavg - 1) / Kavg) * (n_val / (n_val - 1))) * 100
                        PE_deviation = abs((PE_design_val - PE_operating) / PE_design_val) * 100
                        res_unit = "%"
                        output_update2 = update_output(req, PE_design_val, PE_operating, res_unit, PE_deviation)
                        output_list.append(output_update2)              
                        
                    except CustomAttributeError as ae:
                        raise CustomAttributeError(f"Error calculating {req}: Missing: {ae}")
                
                elif req == "shaft_power":
                    try:
                        Fair = fetch_values(body, "Fair", req)
                        H1 = fetch_values(body, "H1", req)
                        H2 = fetch_values(body, "H2", req)
                        Nmech = fetch_values(body, "Nmech", req)
                        SP_design = fetch_values(body, "design", req)

                        Fair_unit = fetch_units(body, "Fair", req,units) 
                        H1_unit = fetch_units(body, "H1", req,units) 
                        H2_unit = fetch_units(body, "H2", req,units) 
                        Nmech_unit = fetch_units(body, "Nmech", req,units) 
                        SP_design_unit = fetch_units(body, "design", req,units) 

                        Fair_val = convert_mass_flow_rate(Fair, Fair_unit, "Fair",req)
                        H1_val = H1
                        H2_val = H2
                        Nmech_val = Nmech
                        SP_design_val = SP_design

                        Wgas = Fair_val * (H2_val - H1_val)
                        SP_operating = abs(Wgas / Nmech_val)
                        SP_deviation = (abs(SP_design_val - SP_operating) / SP_design_val) * 100
                        res_unit = "kw"
                        output_update3 = update_output(req, SP_design_val, SP_operating, res_unit, SP_deviation)
                        output_list.append(output_update3)
                    
                    except CustomAttributeError as ae:
                        raise CustomAttributeError(f"Error calculating {req}: Missing: {ae}")

                elif req == "surge_margin":
                    try:
                        Currentflow = fetch_values(body, "Current_flow", req)
                        Surgeflow = fetch_values(body, "Surge_inline_flow", req)
                        SM_design = fetch_values(body, "design", req)

                        Currentflow_unit = fetch_units(body, "Current_flow", req,units)
                        Surgeflow_unit = fetch_units(body, "Surge_inline_flow", req,units)
                        SM_design_unit = fetch_units(body, "design", req,units)

                        Currentflow_val = convert_vol_flow_rate(Currentflow, Currentflow_unit, "Current_flow",req)
                        Surgeflow_val = convert_vol_flow_rate(Surgeflow, Surgeflow_unit, "Surge_inline_flow",req)
                        SM_design_val = SM_design

                        res_unit = "%"

                        SM_operating = ((Currentflow_val - Surgeflow_val) / Currentflow_val) * 100
                        SM_deviation = (abs(SM_design_val - SM_operating) / SM_design_val) * 100
                        output_update4 = update_output(req, SM_design_val, SM_operating, res_unit, SM_deviation)
                        output_list.append(output_update4)
                        
                    except CustomAttributeError as ae:
                        raise CustomAttributeError(f"Error calculating {req}: Missing: {ae}")
                
                elif req == "power_consumption":
                    try:
                        V = fetch_values(body, "V", req)
                        I = fetch_values(body, "I", req)
                        Power_factor = fetch_values(body, "Power_factor", req)
                        PC_design = fetch_values(body, "design", req)

                        V_unit = fetch_units(body, "V", req,units)
                        I_unit = fetch_units(body, "I", req,units)
                        Power_Factor_unit = fetch_units(body, "Power_factor", req,units)
                        PC_design_unit = fetch_units(body, "design", req,units)

                        V_val = V
                        I_val = I
                        Power_factor_val = Power_factor
                        PC_design_val = PC_design

                        res_unit = "kw"

                        PC_operating = abs(math.sqrt(3) * V_val * I_val * Power_factor_val) / 1000
                        PC_deviation = (abs(PC_design_val - PC_operating) / PC_design_val) * 100
                        output_update5 = update_output(req, PC_design_val, PC_operating, res_unit, PC_deviation)
                        output_list.append(output_update5)
                        
                    except CustomAttributeError as ae:
                        raise CustomAttributeError(f"Error calculating {req}: Missing: {ae}")

                elif req == "polytropic_exponent":
                    try:
                        Po = fetch_values(body, "Po", req)
                        Pi = fetch_values(body, "Pi", req)
                        Rowo = fetch_values(body, "Rowo", req)
                        Rowi = fetch_values(body, "Rowi", req)
                        PO_design = fetch_values(body, "design", req)

                        Po_unit = fetch_units(body, "Po", req,units)
                        Pi_unit = fetch_units(body, "Pi", req,units)
                        Rowo_unit = fetch_units(body, "Rowo", req,units)
                        Rowi_unit = fetch_units(body, "Rowi", req,units)
                        PO_design_unit = fetch_units(body, "design", req,units)

                        Po_val = convert_pressure(Po, Po_unit, "Po",req)
                        Pi_val = convert_pressure(Pi, Pi_unit, "Pi",req)
                        Rowo_val = Rowo
                        Rowi_val = Rowi
                        PO_design_val = PO_design

                        res_unit = ""

                        PO_operating = math.log(Po_val / Pi_val) / math.log(Rowo_val / Rowi_val)
                        PO_deviation = (abs(PO_design_val - PO_operating) / PO_design_val) * 100
                        output_update6 = update_output(req, PO_design_val, PO_operating, res_unit, PO_deviation)
                        output_list.append(output_update6)
                        
                    except CustomAttributeError as ae:
                        raise CustomAttributeError(f"Error calculating {req}: Missing: {ae}")

                elif req == "adiabatic_efficiency":
                    try:
                        Ki = fetch_values(body, "Ki", req)
                        Ko = fetch_values(body, "Ko", req)
                        Pi = fetch_values(body, "Pi", req)
                        Po = fetch_values(body, "Po", req)
                        n = fetch_values(body, "n", req)
                        AE_design = fetch_values(body, "design", req)

                        Po_unit = fetch_units(body, "Po", req,units)
                        Pi_unit = fetch_units(body, "Pi", req,units)
                        Ki_unit = fetch_units(body, "Ki", req,units)
                        Ko_unit = fetch_units(body, "Ko", req,units)
                        n_unit = fetch_units(body, "n", req,units)
                        AE_design_unit = fetch_units(body, "design", req,units)

                        Po_val = convert_pressure(Po, Po_unit, "Po",req)
                        Pi_val = convert_pressure(Pi, Pi_unit, "Pi",req)
                        Ko_val = Ko
                        Ki_val = Ki
                        n_val = n
                        AE_design_val = AE_design

                        res_unit = "%"

                        Kavg = (Ki_val + Ko_val) / 2

                        temp1 = (Kavg - 1) / Kavg
                        temp2 = ((n_val - 1) / n_val)
                        temp3 = Po_val / Pi_val
                        AE_operating = ((math.pow(temp3, temp1) - 1) / (math.pow(temp3, temp2) - 1)) * 100
                        AE_deviation = (abs(AE_design_val - AE_operating) / AE_design_val) * 100

                        output_update7 = update_output(req, AE_design_val, AE_operating, res_unit, AE_deviation)
                        output_list.append(output_update7)
                            
                    except CustomAttributeError as ae:
                        raise CustomAttributeError(f"Error calculating {req}: Missing: {ae}")

                elif req == "polytropic_head":
                    try:
                        Zi = fetch_values(body, "Zi", req)
                        Zo = fetch_values(body, "Zo", req)
                        R = fetch_values(body, "R", req)
                        Mw = fetch_values(body, "Mw", req)
                        Po = fetch_values(body, "Po", req)
                        Pi = fetch_values(body, "Pi", req)
                        Ti = fetch_values(body, "Ti", req)
                        n = fetch_values(body, "n", req)
                        PH_design = fetch_values(body, "design", req)

                        Zi_unit = fetch_units(body, "Zi", req,units)
                        Zo_unit = fetch_units(body, "Zo", req,units)
                        R_unit = fetch_units(body, "R", req,units)
                        Mw_unit = fetch_units(body, "Mw", req,units)
                        Po_unit = fetch_units(body, "Po", req,units)
                        Pi_unit = fetch_units(body, "Pi", req,units)
                        Ti_unit = fetch_units(body, "Ti", req,units)
                        n_unit = fetch_units(body, "n", req,units)
                        PH_design_unit = fetch_units(body, "design", req,units)

                        Po_val = convert_pressure(Po, Po_unit, "Po",req)
                        Pi_val = convert_pressure(Pi, Pi_unit, "Pi",req)
                        Ti_val = convert_temp(Ti, Ti_unit, "Ti",req) + 273
                        Zi_val = Zi
                        Zo_val = Zo
                        R_val = R
                        Mw_val = Mw
                        n_val = n
                        PH_design_val = PH_design

                        res_unit = "kj/kg"

                        Zavg = (Zi_val + Zo_val) / 2
                        term1 = (Zavg * R_val * Ti_val) / Mw_val
                        term2 = n_val / (n_val - 1)
                        term3 = ((Po_val / Pi_val) ** ((n_val - 1) / n_val)) - 1
                        PH_operating = abs(term1 * term2 * term3)
                        PH_deviation = (abs(PH_design_val - PH_operating) / PH_design_val) * 100
                        output_update = update_output(req, PH_design_val, PH_operating, res_unit, PH_deviation)
                        output_list.append(output_update)

                    except CustomAttributeError as ae:
                        raise CustomAttributeError(f"Error calculating {req}: Missing: {ae}")
                
            else:
                raise ValueError(f"Invalid KPI request: {req}")

    except (ValueError, CustomAttributeError, UnitError, DatatypeError) as e:
        raise e

    return output_list
