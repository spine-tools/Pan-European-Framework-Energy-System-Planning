import spinedb_api as api
from spinedb_api import DatabaseMapping
from spinedb_api.dataframes import to_dataframe
from spinedb_api.parameter_value import convert_map_to_table, IndexedValue
from sqlalchemy.exc import DBAPIError
import datetime
import pandas as pd
import sys
import numpy as np
import json
import yaml 
import time as time_lib

if len(sys.argv) > 1:
    url_spineopt = sys.argv[1]
else:
    exit("Please provide spineopt database url as argument. They should be of the form ""sqlite:///path/db_file.sqlite""")

def nested_index_names(value, names = None, depth = 0):
    if names is None:
        names = []
    if depth == len(names):
        names.append(value.index_name)
    elif value.index_name != names[-1]:
        raise RuntimeError(f"Index names at depth {depth} do no match: {value.index_name} vs. {names[-1]}")
    for y in value.values:
        if isinstance(y, IndexedValue):
            nested_index_names(y, names, depth + 1)
    return names

def update_parameter_value(db_map : DatabaseMapping, id_int : int, class_name : str,parameter : str,alternative : str,elements : tuple,value : any) -> None:
    db_value, value_type = api.to_database(value)
    _, error = db_map.update_parameter_value_item(id=id_int, entity_class_name=class_name,entity_byname=elements,parameter_definition_name=parameter,alternative_name=alternative,value=db_value,type=value_type)
    if error:
        raise RuntimeError(error)

def add_or_update_parameter_value(db_map : DatabaseMapping, class_name : str,parameter : str,alternative : str,elements : tuple,value : any) -> None:
    db_value, value_type = api.to_database(value)
    db_map.add_or_update_parameter_value(entity_class_name=class_name,entity_byname=elements,parameter_definition_name=parameter,alternative_name=alternative,value=db_value,type=value_type)

def add_entity_group(db_map : DatabaseMapping, class_name : str, group : str, member : str) -> None:
    _, error = db_map.add_entity_group_item(group_name = group, member_name = member, entity_class_name=class_name)
    if error is not None:
        raise RuntimeError(error)

def add_entity(db_map : DatabaseMapping, class_name : str, name : tuple, ent_description = None) -> None:
    _, error = db_map.add_entity_item(entity_byname=name, entity_class_name=class_name, description = ent_description)
    if error is not None:
        raise RuntimeError(error)

def add_parameter_value(db_map : DatabaseMapping,class_name : str,parameter : str,alternative : str,elements : tuple,value : any) -> None:
    db_value, value_type = api.to_database(value)
    _, error = db_map.add_parameter_value_item(entity_class_name=class_name,entity_byname=elements,parameter_definition_name=parameter,alternative_name=alternative,value=db_value,type=value_type)
    if error:
        raise RuntimeError(error)

def add_scenario(db_map : DatabaseMapping,name_scenario : str) -> None:
    _, error = db_map.add_scenario_item(name=name_scenario)
    if error is not None:
        raise RuntimeError(error)

def add_scenario_alternative(db_map : DatabaseMapping,name_scenario : str, name_alternative : str, rank_int = None) -> None:
    _, error = db_map.add_scenario_alternative_item(scenario_name = name_scenario, alternative_name = name_alternative, rank = rank_int)
    if error is not None:
        raise RuntimeError(error)

def scenario_development(config):

    with DatabaseMapping(url_spineopt) as sopt_db:

        scenarios_in_db = [scenario_i["name"] for scenario_i in sopt_db.get_scenario_items()]
        for scenario_name in config["scenarios"]:
            
            if scenario_name not in scenarios_in_db:
                add_scenario(sopt_db,scenario_name)
                alt_names = config["scenarios"][scenario_name]
                for alt_name in alt_names:
                    add_scenario_alternative(sopt_db,scenario_name,alt_name,alt_names.index(alt_name)+1)
        try:
            sopt_db.commit_session("Added scenario")
        except:
            print("###################################################################### commit error")  

def storage_setup(config):

    with DatabaseMapping(url_spineopt) as sopt_db:
        list_rep = [entity_i["name"] for entity_i in sopt_db.get_entity_items(entity_class_name = "temporal_block") if "representative_period" in entity_i["name"]]
        list_otb = [entity_i["name"] for entity_i in sopt_db.get_entity_items(entity_class_name = "temporal_block") if "operations" in entity_i["name"]]                    
    
        for param_map in sopt_db.get_parameter_value_items(entity_class_name = "node", parameter_definition_name = "has_state"):
            if bool(param_map["parsed_value"]):
                if all(sto+"_" not in param_map["entity_byname"][0] for sto in config["short-term-storage"]):
                    add_or_update_parameter_value(sopt_db,"node","is_longterm_storage","Base",(param_map["entity_byname"][0],),True)
                    cyclic_condition_status = [entity_i for entity_i in sopt_db.get_parameter_value_items(entity_class_name = "node__temporal_block", alternative_name = "Base", parameter_definition_name = "cyclic_condition") if param_map["entity_byname"][0] == entity_i["entity_byname"][0]]
                    if cyclic_condition_status and sopt_db.get_entity_item(entity_class_name = "temporal_block",name = "all_rps"):
                        try:
                            add_entity(sopt_db,"node__temporal_block",(param_map["entity_byname"][0],"all_rps"))
                        except:
                            print(f"Entity class node__temporal_block with all_rps already added")
                            pass
                    elif any(sto+"_" in param_map["entity_byname"][0] for sto in config["long-term-storage"]):
                        add_entity(sopt_db,"node__temporal_block",(param_map["entity_byname"][0],"all_rps"))
                        for tb in list_otb:
                            add_entity(sopt_db,"node__temporal_block",(param_map["entity_byname"][0],tb))
                            add_or_update_parameter_value(sopt_db,"node__temporal_block","cyclic_condition","Base",(param_map["entity_byname"][0],tb),True)

                else:
                    if list_rep:
                        # identifying long-term cyclic condition
                        for node_map in sopt_db.get_entity_items(entity_class_name = "node__temporal_block"):
                            if node_map["entity_byname"][0] == param_map["entity_byname"][0]:
                                item_id = node_map["id"]
                                sopt_db.remove_item("entity",item_id)
                        for rep in list_rep:
                            try:
                                add_entity(sopt_db,"node__temporal_block",(param_map["entity_byname"][0],rep))
                            except:
                                print(f"Entity node__temporal_bloc with {rep}")
                                pass
                            add_or_update_parameter_value(sopt_db,"node__temporal_block","cyclic_condition","Base",(param_map["entity_byname"][0],rep),True)
                    else:
                        add_or_update_parameter_value(sopt_db,"node","is_longterm_storage","Base",(param_map["entity_byname"][0],),True)
                        for tb in list_otb:
                            try:
                                add_entity(sopt_db,"node__temporal_block",(param_map["entity_byname"][0],tb))
                            except:
                                print(f"Entity node__temporal_bloc with {tb}")
                                pass
                            add_or_update_parameter_value(sopt_db,"node__temporal_block","cyclic_condition","Base",(param_map["entity_byname"][0],tb),True)
        try:
            sopt_db.commit_session("Added storage_setup")
        except:
            print("###################################################################### commit error") 

def update_parameters(config):

    with DatabaseMapping(url_spineopt) as sopt_db:

        resolution_ = config["resolution"]
        parameter_value = {"type":"duration","data":resolution_}
        for parameter_map in sopt_db.get_parameter_value_items(parameter_definition_name = "resolution"):
            if "planning" not in parameter_map["entity_byname"][0]:
                add_or_update_parameter_value(sopt_db, parameter_map["entity_class_name"], "resolution", parameter_map["alternative_name"], parameter_map["entity_byname"], parameter_value)
        #add_or_update_parameter_value(sopt_db, "node", "initial_storages_invested_available", "Base", ("CO2-storage", ), 0.2*1e3/config["emission_factor"])
        #add_or_update_parameter_value(sopt_db, "node", "fix_storages_invested_available", "Base", ("CO2-storage", ), 0.2*1e3/config["emission_factor"])
        #add_or_update_parameter_value(sopt_db, "node", "initial_storages_invested_available", "Base", ("atmosphere", ), 2.6*1e3/config["emission_factor"])
        #add_or_update_parameter_value(sopt_db, "node", "fix_storages_invested_available", "Base", ("atmosphere", ), 2.6*1e3/config["emission_factor"])        
        
        try:
            sopt_db.commit_session("Update parameters")
        except:
            print("###################################################################### commit error")  

def fix_no_investable_by_2030(config):

    indexes_ = ["2030-01-01T00:00:00","2040-01-01T00:00:00","2050-01-01T00:00:00","2060-01-01T00:00:00"]
    values_ = [0.0,None,None,None]
    parameter_value = {"type":"time_series","data":dict(zip(indexes_,values_))}

    parameter_name_map = {"unit":"fix_units_invested","node":"fix_storages_invested","connection":"fix_connections_invested"}

    with DatabaseMapping(url_spineopt) as sopt_db:
        fix_config = config["no_investable_2030"]
        parsed_entities = {class_i:[entity_map["name"] for entity_map in sopt_db.get_entity_items(entity_class_name=class_i) if entity_map["name"].split("_")[0] in fix_config[class_i]] for class_i in ["unit","node"]}

        parsed_entities["connection"] = []
        for entity_map in sopt_db.get_entity_items(entity_class_name="connection"):
            if entity_map["name"].split("_")[1] in fix_config["connection"]:
                parsed_entities["connection"].append(entity_map["name"])
                
        for entity_class in parsed_entities:
            for entity_name in parsed_entities[entity_class]:
                check_existing_param = sopt_db.get_parameter_value_items(entity_class_name = entity_class, parameter_definition_name = parameter_name_map[entity_class], entity_byname = (entity_name,))
                if not check_existing_param:
                    add_parameter_value(sopt_db,entity_class,parameter_name_map[entity_class],"Base",(entity_name,),parameter_value)

        try:
            sopt_db.commit_session("fix invested variables")
        except:
            print("###################################################################### fix invested variables commit error")  

def ramping_constraints(config):

    with DatabaseMapping(url_spineopt) as sopt_db:
        entities = [entity_i for entity_i in sopt_db.get_entity_items(entity_class_name = "unit__to_node") if any(tech in entity_i["entity_byname"][0] for tech in config["ramping"])]
        for entity in entities:
            for tech in config["ramping"]:
                if tech in entity["entity_byname"][0] and config["ramping"][tech][0] in entity["entity_byname"][1]:
                    ramp_value = config["ramping"][tech][1]
                    add_or_update_parameter_value(sopt_db,"unit__to_node","ramp_up_limit","Base",entity["entity_byname"],ramp_value)
                    add_or_update_parameter_value(sopt_db,"unit__to_node","ramp_down_limit","Base",entity["entity_byname"],ramp_value)
                    add_or_update_parameter_value(sopt_db,"unit__to_node","start_up_limit","Base",entity["entity_byname"],ramp_value)
                    add_or_update_parameter_value(sopt_db,"unit__to_node","shut_down_limit","Base",entity["entity_byname"],ramp_value)
                    break

        try:
            sopt_db.commit_session("ramping constraints")
        except:
            print("###################################################################### ramping constraints commit error")  
        
def refinery_constraints(config):
    with DatabaseMapping(url_spineopt) as sopt_db:
        list_otb = [entity_i["name"] for entity_i in sopt_db.get_entity_items(entity_class_name = "temporal_block") if "operations" in entity_i["name"]]    
        entities = {type_:[entity_i["name"] for entity_i in sopt_db.get_entity_items(entity_class_name = "unit") if any(tech in entity_i["name"] for tech in config["refineries"][type_]["techs"])] for type_ in config["refineries"]}
        all_rps  = sopt_db.get_entity_item(entity_class_name = "temporal_block",name = "all_rps")
        for type_ in ["bio","syn"]:
            add_entity(sopt_db,"investment_group",(f"{type_}fuels",))
            
            coefficient_2030 = config["refineries"][type_]["share_2030"]
            coefficient_2040 = config["refineries"][type_]["share_2040"]
            coefficient_2050 = config["refineries"][type_]["share_2050"]
            refinery_cap = 0
            for tech in entities["fossil"]:
                initial_cap = sopt_db.get_parameter_value_item(entity_class_name = "unit", alternative_name = "Base", parameter_definition_name = "initial_units_invested_available", entity_byname = (tech,))
                if initial_cap:
                    refinery_cap += initial_cap["parsed_value"]
            for tech in entities[type_]:
                add_entity(sopt_db,"unit__investment_group",(tech,f"{type_}fuels"))

            index_ = ["2030-01-01T00:00:00","2040-01-01T00:00:00","2050-01-01T00:00:00","2060-01-01T00:00:00"]
            value_ = [coefficient_2030*refinery_cap,coefficient_2040*refinery_cap,coefficient_2050*refinery_cap,coefficient_2050*refinery_cap]
            parameter_value = {"type":"time_series","data":dict(zip(index_,value_))}
            add_parameter_value(sopt_db,"investment_group","maximum_entities_invested_available","Base",(f"{type_}fuels",),parameter_value)

        for entity_HC in [entity_i["name"] for entity_i in sopt_db.get_entity_items(entity_class_name="node") if "HC_" in entity_i["name"]]:
            add_entity(sopt_db,"node",(f"bunker-{entity_HC}",))
            add_parameter_value(sopt_db,"node","has_state","Base",(f"bunker-{entity_HC}",),True)
            add_parameter_value(sopt_db,"node","is_longterm_storage","Base",(f"bunker-{entity_HC}",),True)
            for tb in list_otb:
                add_entity(sopt_db,"node__temporal_block",(f"bunker-{entity_HC}",tb))
                add_parameter_value(sopt_db,"node__temporal_block","cyclic_condition","Base",(f"bunker-{entity_HC}",tb),True)
            if all_rps:
                add_entity(sopt_db,"node__temporal_block",(f"bunker-{entity_HC}","all_rps"))
            add_entity(sopt_db,"connection",(f"bunker-connection-{entity_HC}",))
            add_parameter_value(sopt_db,"connection","connection_type","Base",(f"bunker-connection-{entity_HC}",),"connection_type_lossless_bidirectional")
            add_entity(sopt_db,"connection__from_node",(f"bunker-connection-{entity_HC}",entity_HC))
            add_entity(sopt_db,"connection__to_node",(f"bunker-connection-{entity_HC}",f"bunker-{entity_HC}"))
            add_entity(sopt_db,"connection__node__node",(f"bunker-connection-{entity_HC}",f"bunker-{entity_HC}",entity_HC))
            add_parameter_value(sopt_db,"connection__node__node","fix_ratio_out_in_connection_flow","Base",(f"bunker-connection-{entity_HC}",f"bunker-{entity_HC}",entity_HC),1.0)

        try:
            sopt_db.commit_session("refinery constraints")
        except:
            print("###################################################################### refinery constraints commit error")  

def onshore_potentials(config):

    with DatabaseMapping(url_spineopt) as sopt_db:
        maximum_entities = [parameter_map  for parameter_map in sopt_db.get_parameter_value_items(parameter_definition_name = "maximum_entities_invested_available") if "wind-on" in parameter_map["entity_byname"][0] or "solar-PV" in parameter_map["entity_byname"][0]]
        for max_entity in maximum_entities:
            add_or_update_parameter_value(sopt_db,"investment_group","maximum_entities_invested_available","Base",max_entity["entity_byname"],max_entity["parsed_value"]*config["onshore_potentials"])
        try:
            sopt_db.commit_session("vre onshore potentials update")
        except:
            print("###################################################################### vre onshore potentials update commit error")  


def main():

    with open(sys.argv[2], 'r') as file:
        config = yaml.safe_load(file)

    print("adding scenarios to be analyzed")
    # scenario_development(config)

    print("storage_setup")
    # storage_setup(config)

    print("updating_parameters")
    # update_parameters(config)

    print("fixing invested variables")
    # fix_no_investable_by_2030(config)

    print("ramping constraints")
    ramping_constraints(config)

    print("refinery constraints")
    #refinery_constraints(config)

    print("vre onshore potentials updates")
    onshore_potentials(config)

if __name__ == "__main__":
    main()