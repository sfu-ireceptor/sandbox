
import argparse
import yaml
import sys
import airr
from airr.schema import Schema


# Recursive function to extract fields from a AIRR YAML specification into a flat table.
# The function processes all $ref objects recursively to build up a table of entries with
# all fields from all sub-objects in the YAML definition.
#
# Parameters:
# - block: The schema block to extract.
# - airr_class: The airr class field. For iReceptor this stays constant through the
#   hierarchy, and is either "repertoire" or "rearrangement"
# - airr_api_query: The hierarchical tag for the AIRR API query. This is essentially
#   the query field that the API requires (e.g. study.study_id) and is built as we 
#   traverse the heirarchy of the Repertoire object.
# - airr_api_response: The hierarchical tag for the AIRR API response. This tells us
#   the hierarchy of the object that this field needs to go in. It is similar to
#   airr_api_query except for those objects that are arrays they are denoted with a
#   .0. string (e.g. sample.0.sample_id denotes that sample_id is part of the sample
#   array response.
# - labels: An array of labels that have been found thus far in the query. When a new label
#   is found it should be added to the labels array.
# - table: An array of dictionaries, each row in the table a field in the spec, and
#   each dictionary a key value pair where the labels are the keys and the values
#   are the field values for those labels. 
#
# Returns:
# - labels: A new set of labels based on the labels provided plus any added by the current
#   object.
# - table: An array of dictionaries, based on the table provided but with new rows added
#   as per the fields that were found in the current object.

def extractBlock(block, airr_class, airr_api_query, airr_api_response, labels, table):

    # Use the AIRR library to get an AIRR Schema block for the current block.
    schema = Schema(block)

    # For each field in the schema, process it
    for field in schema.properties:

        # and not feild_spec['$ref'] == "#/Ontology":
        # Create a new dictionary entry for the field.
        field_dict = dict()
        # Set up the basic field mappings for the stanard iReceptor fields.
        field_dict['airr'] = field
        field_dict['ir_class'] = airr_class
        field_dict['ir_subclass'] = block
        field_dict['ir_adc_api_query'] = airr_api_query + field
        field_dict['ir_adc_api_response'] = airr_api_response + field

        # Get the object that describes the specification for this field and
        # process it.
        field_spec = schema.spec(field)
        append = True
        if '$ref' in field_spec and not field_spec['$ref'] == "#/Ontology":
            append = False
        if 'type' in field_spec and field_spec['type'] == 'array':
            if '$ref' in field_spec['items'] or 'allOf' in field_spec['items']:
                append = False
        if append:    
            # Add the field to the table.
            table.append(field_dict)

        for k,v in field_spec.items():
            # A field in the AIRR specification either has "normal" field specifications
            # such as type, description, and example or it has AIRR specific field
            # specifications in a custom x-airr object. This custom object has things
            # about the MiAIRR standard and the ADC API. We have to handle both.

            # Handle the x-airr schema objects
            if k == 'x-airr':
                # Iterated over the x-airr schema objects.
                for xairr_k, xairr_v in v.items():
                    # If it is a format or ontology object, we don't record anything.
                    if xairr_k == 'format' or xairr_k == 'ontology':
                       continue
                    else:
                        # If it is a string value, we want to clean it up, in case there
                        # is some extra white space...
                        value = xairr_v
                        if isinstance(value, str):
                            value = value.strip()
                        # Create a new label for this field, as we want to keep track of
                        # this as a column in our table. We prefic all of the AIRR columns
                        # with airr_ to differentiate them.
                        label = 'airr_'+xairr_k
                        # Only add it if it isn't in the labels already.
                        if not label in labels:
                            labels.append(label)
                        # Add the value if this field to the column.
                        field_dict[label] = value
            else:
                # We are processing normal YAML spec fields.
                if k == '$ref':
                    # Handle a $ref field to another object
                    if v == "#/Ontology":
                        # If the $ref is to an Ontology, mark the type as ontology.
                        field_dict["airr_type"] = "ontology"
                        # We want to add on a .value qualifier to the ADC API variable names as
                        # we return the value component of the ontology in the API.
                        field_dict['ir_adc_api_query'] = field_dict['ir_adc_api_query'] + '.value'
                        field_dict['ir_adc_api_response'] = field_dict['ir_adc_api_response'] + '.value'
                    else:
                        # If the $ref is to another object, then handle that object by
                        # recursion. We get the object to use from the name.
                        ref_array = v.split("/")
                        new_schema_name = ref_array[1]
                        # We recurse on the new schema block, making sure that we track
                        # that we are processing a new object and that the API field 
                        # references need to reference the hierarchy correctly. 
                        labels, table = extractBlock(new_schema_name, airr_class,
                                                     airr_api_query+field_dict['airr']+'.',
                                                     airr_api_response+field_dict['airr']+'.',
                                                     labels, table)
                elif k == 'items':
                    # Handle a list of items, meaning we have an array. In the AIRR
                    # specification we can have an array of $ref objects or an
                    # "allOf" directive of $ref objects which means we have to process
                    # each element.
                    for item_key, item_value in v.items():
                        if item_key == '$ref':
                            # The item is a $ref, get the sub-object and process it.
                            ref_array = item_value.split("/")
                            new_schema_name = ref_array[1]
                            # Note the API response has a .0. in it because this is an array.
                            labels, table = extractBlock(new_schema_name, airr_class,
                                                         airr_api_query+field_dict['airr']+'.',
                                                         airr_api_response+field_dict['airr']+'.0.',
                                                         labels, table)
                        elif item_key == 'allOf':
                            # The item is an allOf so process each element.
                            for ref_dict in item_value:
                                # The item is a $ref, get the sub-object and process it.
                                if '$ref' in ref_dict:
                                    ref_array = ref_dict['$ref'].split("/")
                                    new_schema_name = ref_array[1]
                                    # Note the API response has a .0. in it because this is an array.
                                    labels, table = extractBlock(new_schema_name, airr_class,
                                                                 airr_api_query+field_dict['airr']+'.',
                                                                 airr_api_response+field_dict['airr']+'.0.',
                                                                 labels, table)
                elif k == 'example':
                    # Processing an example - some special cases...
                    # First add it to the labels if we don't already have it.
                    label = 'airr_'+k
                    if not label in labels:
                        labels.append(label)
                    if isinstance(v,dict):
                        # If it is a dict() then we have an ontology term, process
                        # the ID and value for the ontology.
                        field_dict[label] = str(v['id']) + ', ' + v['value']
                    elif not isinstance(v, str):
                        # If it isn't a string, store it
                        field_dict[label] = v
                    else:
                        # If it is a string, then we want to strip it in case it has
                        # odd white space...
                        field_dict[label] = v.strip()
                elif k == 'enum':
                    # First add it to the labels if we don't already have it.
                    label = 'airr_'+k
                    if not label in labels:
                        labels.append(label)
                    # Handle the enum case, where we join the enum fields so
                    # we can track them.
                    value = ','.join(v) 
                    field_dict[label] = value
                else:
                    # If we get here, we are processing "normal" fields...
                    # First add it to the labels if we don't already have it.
                    label = 'airr_'+k
                    if not label in labels:
                        labels.append(label)
                    # Strip off any whitespace if it is a string...
                    value = v
                    if isinstance(v, str):
                        value = v.strip()
                    field_dict[label] = value

    # We are done, return the labels and the table.
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
    labels, table = extractBlock('Repertoire', 'Repertoire', '', '', labels, table)
    # Recursively process the Rearrangement block, as it is the key defining block that is
    # includive of everything at the Rearangement level.
    labels, table = extractBlock('Rearrangement', 'Rearrangement', '', '', labels, table)

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

