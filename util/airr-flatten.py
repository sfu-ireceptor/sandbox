
import collections
import argparse
import yaml
import sys
import airr
from airr.schema import Schema


# Recursive function to extract fields from a AIRR YAML specification into a
# flat table. The function processes all $ref objects recursively to build up
# a table of entries with all fields from all sub-objects in the YAML definition.
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
# - labels: An array of labels that have been found thus far in the query. When
#   a new label is found it should be added to the labels array.
# - table: An array of dictionaries, each row in the table is a field in the spec, and
#   each dictionary a key value pair where the labels are the keys and the values
#   are the field values for those labels. 
#
# Returns:
# - labels: A new set of labels based on the labels provided plus any
# added by the current object.
# - table: An array of dictionaries, based on the table provided but with
# new rows added as per the fields that were found in the current object.

def extractBlock(block, airr_class, airr_api_query, airr_api_response, labels, table):

    # Use the AIRR library to get an AIRR Schema block for the current block.
    schema = Schema(block)

    # Get the required fields for this schema object
    required_fields = schema.required

    # For each field in the schema, process it
    for field in schema.properties:
        # Create a new dictionary entry for the field.
        field_dict = dict()
        # Set up the basic field mappings for the stanard iReceptor fields.
        field_dict['airr'] = field
        field_dict['airr_spec'] = True
        # If the field is required, set the attribute.
        if field in required_fields:
            field_dict['airr_required'] = True
        else:
            field_dict['airr_required'] = False
        field_dict['ir_class'] = airr_class
        field_dict['ir_subclass'] = block
        field_dict['ir_adc_api_query'] = airr_api_query + field
        field_dict['ir_adc_api_response'] = airr_api_response + field
        field_dict['airr_is_array'] = False
        field_tag = field+airr_class

        # Get the object that describes the specification for this field and
        # process it.
        field_spec = schema.spec(field)
        append = True
        if '$ref' in field_spec and not field_spec['$ref'] == "#/Ontology":
            append = False
        if 'type' in field_spec and field_spec['type'] == 'array':
            if '$ref' in field_spec['items'] or 'allOf' in field_spec['items']:
                append = False
            else:
                field_dict['airr_is_array'] = True
        if append:    
            # Add the field to the table.
            table[field_tag] = field_dict

        for k,v in field_spec.items():
            # A field in the AIRR specification either has "normal" field specs
            # such as type, description, and example or it has AIRR specific field
            # specifications in a custom x-airr object. This custom object has things
            # about the MiAIRR standard and the ADC API. We have to handle both.

            # Handle the x-airr schema objects
            if k == 'x-airr':
                # Iterated over the x-airr schema objects.
                for xairr_k, xairr_v in v.items():
                    # If it is an ontology object, we don't record anything.
                    if xairr_k == 'ontology':
                       continue
                    # The miairr tag is a controlled vocabulary of "essential",
                    # "important", or "defined". It controls the setting of two
                    # columns in the mapping, airr_miairr and airr_required.
                    elif xairr_k == 'miairr':
                        # The miairr tag is a controlled vocabulary of "essential",
                        # "important", or "defined". If this field exists and is 
                        # set to one of these, then the airr_miairr label should be
                        # set to True as it is a MiAIRR field. If it isn't one of these
                        # values then it is an error.
                        if xairr_v in ['essential', 'important', 'defined']:
                            label = 'airr_miairr'
                            if not label in labels:
                                labels.append(label)
                            # Add the value of this field to the column.
                            field_dict[label] = True

                            # The airr_required field should be True for all MiAIRR terms.
                            #label = 'airr_required'
                            #if not label in labels:
                            #    labels.append(label)
                            ## Add the value of this field to the column.
                            #field_dict[label] = True
                        else:
                            print("Warning: Invalid x_airr:miairr field %s"%(xairr_v))
                    else:
                        # If it is a string value, we want to clean it up, in case
                        # there is some extra white space...
                        value = xairr_v
                        if isinstance(value, str):
                            value = value.strip()
                        # Create a new label for this field, as we want to keep track
                        # of this as a column in our table. We prefic all of the AIRR
                        # columns with airr_ to differentiate them.
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
                        # We want to add on a .value qualifier to the ADC API variable
                        # names as we return the value component of the ontology in
                        # the API.
                        field_dict['ir_adc_api_query'] = field_dict['ir_adc_api_query'] + '.label'
                        field_dict['ir_adc_api_response'] = field_dict['ir_adc_api_response'] + '.label'
                        # For ontology fields, we need to create a second entry for
                        # the id component of the ontology.
                        # Create a new dictionary entry for the id field.
                        id_dict = dict()
                        # Set up the basic field mappings for the iReceptor fields.
                        id_dict['airr'] = field + "_id"
                        id_dict['ir_class'] = airr_class
                        id_dict['ir_subclass'] = block
                        # Create the .id qualifier for the API names.
                        id_dict['ir_adc_api_query'] = airr_api_query + field + ".id"
                        id_dict['ir_adc_api_response'] = airr_api_response + field + ".id"
                        id_dict['airr_is_array'] = False
                        id_dict['airr_type'] = "string"
                        id_field_tag = id_dict['airr']+airr_class
                        table[id_field_tag] = id_dict
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
                            # Note the API response has a .0. in it because this
                            # is an array.
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
                                    # Note the API response has a .0. in it because
                                    # this is an array.
                                    labels, table = extractBlock(new_schema_name,
                                               airr_class,
                                               airr_api_query+field_dict['airr']+'.',
                                               airr_api_response+field_dict['airr']+'.0.',
                                               labels, table)
                        elif item_key == 'type':
                            # This is the special ase of handling a "type" for an "array". 
                            # The only arrays that have a type are array fields. If this
                            # is the case, we want to set the type of the array field.
                            # First add it to the labels if we don't already have it.
                            label = 'airr_type'
                            if not label in labels:
                                labels.append(label)
                            # Strip off any whitespace if it is a string...
                            value = item_value 
                            if isinstance(v, str):
                                value = v.strip()
                            field_dict[label] = value
                elif k == 'example':
                    # Processing an example - some special cases...
                    # First add it to the labels if we don't already have it.
                    label = 'airr_'+k
                    if not label in labels:
                        labels.append(label)
                    if isinstance(v,dict):
                        # If it is a dict() then we have an ontology term, process
                        # the ID and value for the ontology.
                        field_dict[label] = str(v['id']) + ', ' + v['label']
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
    table = collections.OrderedDict()
    # Create an initial set of lables for the mapping file. These are mappings
    # that don't exist in the YAML file but are needed in the mapping file.
    labels = ['airr', 'airr_spec', 'airr_required', 'ir_class', 'ir_subclass',
              'ir_adc_api_query', 'ir_adc_api_response', 'airr_is_array']
    initial_labels = ['airr', 'ir_class', 'ir_subclass',
                      'ir_adc_api_query', 'ir_adc_api_response', 'airr_is_array']
    # Recursively process the Repertoire block, as it is the key defining block
    # that is # includive of everything at the Repertoire level. This will
    # recursively process any $ref entries in the YAML and built correct
    # entries for each field.
    labels, table = extractBlock('Repertoire', 'Repertoire',
                                 '', '', labels, table)
    # Recursively process the Rearrangement block, as it is the key defining block
    # that is includive of everything at the Rearangement level.
    labels, table = extractBlock('Rearrangement', 'Rearrangement',
                                 '', '', labels, table)

    # Recursively process the Clone block, as it is the key defining block
    # that is includive of everything at the Clone level.
    labels, table = extractBlock('Clone', 'Clone',
                                 '', '', labels, table)

    # We need to do some special processing for our ontologies. The _id field of 
    # the ontology does not have an entry in the spec, so we need to copy a bunch
    # of values from the _value field to the _id field.
    for field, field_dict in table.items():
        if field_dict['airr_type'] == 'ontology':
            # Get the field name and generate the ontology id field name
            field = field_dict['airr']
            id_field = field + "_id"
            id_field_tag = id_field + field_dict['ir_class']
            #print("Ontology term %s, %s"%(field, id_field))
            # We want this field to be type string not ontology.
            field_dict['airr_type'] = 'string'
            # If the id field is in the table, update the id fields column values
            if id_field_tag in table:
                #print("Ontology ID field %s"%(id_field))
                # Get the dictionary for the id_field
                id_dict = table[id_field_tag]
                # For each column in the value field, copy it to the id field. Note
                # we do this for all of the generated fields from the spec, not the
                # special fields that are generated.
                for column in field_dict:
                    # Initial labels contains the special fields, we don't want
                    # to overwrite these.
                    if not column in initial_labels:
                        #print("Overwriting Ontology ID field %s[%s]"%(id_field, column))
                        id_dict[column] = field_dict[column]
                        # We want to add some info to the ID description/name/title fields.
                        if column == "airr_description" or column == "airr_name" or column == "airr_title":
                            id_dict[column] = id_dict[column] + " (Ontology ID)"
                # We want the type of the id field to be string.
                id_dict['airr_type'] = 'string'
                # We want the airr_spec field to be TRUE.
                id_dict['airr_spec'] = True
                # Finally, we store the updated dict in the table.
                table[id_field_tag] = id_dict

    # Once we have our table built, we need to print it out.

    # First print out the header labels.
    for label in labels:
        print(label,end='\t')
    print("")

    # Now print out each row.
    for field, field_dict in table.items():
        # For each row, because it is a TSV file, we have to do things in the
        # same order. So we iterated over the labels and print out the information
        # if we have it for this row, otherwise print out an empty column (a
        # simple tab character).
        for label in labels:
            # If the label is in the row, print the info, otherwise print an
            # empty tab column. The end of our print isn't a new line, it is a
            # tab character, so we stay on the same row.
            if label in field_dict:
                print(field_dict[label], end='\t')
            else:
                print("", end='\t')
        # End of row, print a new line character.
        print("")

    # We are done, return success
    sys.exit(0)

