
import argparse
import yaml
import sys
import airr
from airr.schema import Schema


# Recursive function to extract fields from a AIRR YAML specification into a flat table.
# Parameters:
# - block: The schema block to extract.
# - airr_class: The airr class field. For iReceptor this stays constant through the
#   hierarchy, and is either "repertoire" or "rearrangement"
def extractBlock(block, airr_class, airr_subclass, airr_api_query, airr_api_response, labels, table):

    schema = Schema(block)
    for field in schema.properties:
        field_dict = dict()
        #print(field)
        field_dict['airr'] = field
        field_dict['ir_class'] = airr_class
        field_dict['ir_subclass'] = block
        #if len(airr_subclass) > 0:
        #    prefix = airr_subclass +'.'
        #else:
        #    prefix = ''
        #field_dict['ir_adc_api_query'] = prefix + field
        #field_dict['ir_adc_api_response'] = prefix + field
        field_dict['ir_adc_api_query'] = airr_api_query + field
        field_dict['ir_adc_api_response'] = airr_api_response + field
        table.append(field_dict)

        field_spec = schema.spec(field)
        for k,v in field_spec.items():
            if k == 'x-airr':
                for xairr_k, xairr_v in v.items():
                    if xairr_k == 'format' or xairr_k == 'ontology':
                       continue
                    else:
                        value = xairr_v
                        if isinstance(value, str):
                            value = value.strip()
                        label = 'airr_'+xairr_k
                        if not label in labels:
                            labels.append(label)
                        field_dict[label] = value
                    #print("%s: %s"%(xairr_k,value))
            else:
                if k == '$ref':
                    if v == "#/Ontology":
                        field_dict["airr_type"] = "ontology"
                    else:
                        ref_array = v.split("/")
                        new_schema_name = ref_array[1]
                        labels, table = extractBlock(new_schema_name, airr_class, field_dict['airr'],
                                                     airr_api_query+field_dict['airr']+'.',
                                                     airr_api_response+field_dict['airr']+'.',
                                                     labels, table)
                        # print(labels)
                elif k == 'items':
                    for item_key, item_value in v.items():
                        if item_key == '$ref':
                            ref_array = item_value.split("/")
                            new_schema_name = ref_array[1]
                            labels, table = extractBlock(new_schema_name, airr_class, field_dict['airr'],
                                                         airr_api_query+field_dict['airr']+'.',
                                                         airr_api_response+field_dict['airr']+'.0.',
                                                         labels, table)
                        elif item_key == 'allOf':
                            # print('allOf')
                            for ref_dict in item_value:
                                # print(ref_dict)
                                if '$ref' in ref_dict:
                                    ref_array = ref_dict['$ref'].split("/")
                                    new_schema_name = ref_array[1]
                                    labels, table = extractBlock(new_schema_name, airr_class, field_dict['airr'],
                                                                 airr_api_query+field_dict['airr']+'.',
                                                                 airr_api_response+field_dict['airr']+'.0.',
                                                                 labels, table)

                elif k == 'format' or k == 'ontology' or k == 'items':
                    continue
                elif k == 'example' and not isinstance(v, str):
                    continue
                    #field_dict["airr_example"] = v['id'] + ', ' + v['value']
                else:
                    if k == 'enum':
                        value = ','.join(v) 
                        #for element in v:
                        #    value = value + "," + element
                    else: 
                        value = v
                    if isinstance(value, str):
                        value = value.strip()
                    label = 'airr_'+k
                    if not label in labels:
                        labels.append(label)
                    field_dict[label] = value

                    #print("%s: %s"%(k,value))
    return labels, table

def getArguments():
    # Set up the command line parser
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=""
    )

    # The YAML spec file to load
    #parser.add_argument("airr_spec_file")

    # Parse the command line arguements.
    options = parser.parse_args()
    return options

if __name__ == "__main__":
    # Get the command line arguments.
    options = getArguments()

    # Create an empty table. This gets populated by the traversal of the YAML block
    # that is processed.
    table = []
    # Create an initial set of lables for the mapping file. These are mappings that don't
    # exist in the YAML file but are needed in the mapping file.
    labels = ['airr', 'ir_class', 'ir_subclass', 'ir_adc_api_query', 'ir_adc_api_response']
    # Recursively process the Repertoire block, as it is the key defining block that is
    # includive of everything at the Repertoire level. This will recursively process any
    # $ref entries in the YAML and built correct entries for each field.
    labels, table = extractBlock('Repertoire', 'repertoire', '', '', '', labels, table)
    # Recursively process the Rearrangement block, as it is the key defining block that is
    # includive of everything at the Rearangement level.
    labels, table = extractBlock('Rearrangement', 'rearrangement', '', '', '', labels, table)

    # Once we have our table built, we need to print it out.
    # First print out the header labels.
    for label in labels:
        print(label,end='\t')
    print("")

    # Now print out each row.
    for row in table:
        # For each row, because it is a TSV file, we have to do things in the same order.
        # So we iterated over the labels and print out the information if we have it for
        # this row, otherwise print out an empty column (a simple tab character).
        for label in labels:
            # If the label is in the row, print the info, otherwise print an empty tab column.
            # The end of our print isn't a new line, it is a tab character, so we stay on
            # the same row.
            if label in row:
                print(row[label], end='\t')
            else:
                print("", end='\t')
        # End of row, print a new line character.
        print("")

    # We are done, return success
    sys.exit(0)

