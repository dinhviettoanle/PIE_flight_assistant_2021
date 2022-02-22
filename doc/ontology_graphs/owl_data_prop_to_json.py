import re, json
import owlready2 as owl

onto_filename = "../../src/ontology/final-archi.owl"
json_filename = "./ontology_properties.json"
onto = owl.get_ontology(onto_filename).load()

def format_key(s):
    return str(s).split(".")[1]

def insert_value(subdict, parent, new_value):
    for k, v in subdict.items():
        if k == parent:
            v[new_value] = {}
            return True
        if isinstance(v, dict):
            has_been_inserted = insert_value(v, parent, new_value)
            if not has_been_inserted: continue
            else: return True
    return False

def format_dict(subdict):
    for k, v in subdict.items():
        if v == {}: 
            subdict[k] = ""
        if isinstance(v, dict):
            format_dict(v)

def main():
    dict_onto = {}
    dict_class_to_prop = {}


    # Make root properties
    for prop in list(onto.disjoint_properties())[0].entities:
        dict_onto[format_key(prop)] = {}

    not_done_prop = [format_key(a) for a in onto.data_properties() if str(a.is_a[1]) != "owl.topDataProperty"]

    # Insert subproperties
    while len(not_done_prop) > 0:
        for prop in onto.data_properties():
            if format_key(prop) not in not_done_prop: continue
            str_parent = format_key(prop.is_a[1])
            str_prop = format_key(prop)
            if str_parent == "owl.topDataProperty": continue
            is_inserted = insert_value(dict_onto, str_parent, str_prop)
            
            if is_inserted:
                # print(str_parent, str_prop)
                not_done_prop.remove(str_prop)

    # Format dict
    format_dict(dict_onto)
    print(json.dumps(dict_onto, indent=4, sort_keys=True))

    with open(json_filename, 'w') as json_file:
        json.dump(dict_onto, json_file, indent=4, sort_keys=True)

if __name__ == '__main__':
    main()