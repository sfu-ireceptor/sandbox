
import argparse
import yaml
import sys
import airr
from airr.schema import Schema

# Extract the block specified from the YAML file. We are expecting an OpenAPI style
# YAML document with the AIRR specific headers and structure. Currently the code
# does not handle the $ref structure, so only basic blocks will be decoded correctly.
def extractBlock(airr_spec_file, block):

    # Check for a correct block
    if not block in spec_dict:
        print("ERROR: Expected to find a " + block + " object, none found")
        return 1

    # Check to see if it has an OpenAPI properties block.
    block_spec = spec_dict[block]
    if not "properties" in block_spec:
        print("ERROR: Expected to find a properties object, none found")
        return 1

    properties_spec = block_spec["properties"]

    # For each property generated a single line with name, type, and description
    for key, value in properties_spec.items():
        if not "description" in value:
            print("Warning: Expected to find a 'description' object, none found")
            desc_info = ""
        else:
            desc_info = value["description"]

        if not "type" in value:
            print("Warning: Expected to find a 'type' object, none found")
            type_info = ""
        else:
            type_info = value["type"]

        # Print out the key, type, and description TSV separated
        print(key + "\t" + type_info + "\t" + desc_info.strip())
    return 0

def getArguments():
    # Set up the command line parser
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=""
    )

    # The YAML spec file to load
    parser.add_argument("airr_spec_file")

    # Parse the command line arguements.
    options = parser.parse_args()
    return options


if __name__ == "__main__":
    # Get the command line arguments.
    options = getArguments()

    # Open the file
    try:
        with open(options.airr_spec_file, 'r') as f:
            spec_dict = yaml.safe_load(f)
    except yaml.YAMLError as error:
            print("ERROR: YAML load error detected in " + airr_spec_file + ": " + str(error))
            sys.exit(1)
    except IOError as error:
        print("ERROR: Unable to open YAML file " + airr_spec_file + ": " + str(error))
        sys.exit(1)
    except Exception as error:
        print("ERROR: Unable to open YAML file " + airr_spec_file + ": " + str(error))
        sys.exit(1)
    # Track the blocks that we are interested in
    blocks = ['Study', 'Subject', 'Diagnosis', 'Sample', 'CellProcessing',
     'NucleicAcidProcessing', 'PCRTarget', 'SequencingRun', 'RawSequenceData',
     'DataProcessing', 'SampleProcessing', 'Repertoire', 'Rearrangement']

    table = []
    labels = ['airr']
    for block in blocks:
        schema = Schema(block)
        for field in schema.properties:
            field_dict = dict()
            #print(field)
            field_dict['airr'] = field
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

    #print(labels)
    for label in labels:
        print(label,end='\t')
    print("")
    for row in table:
        for label in labels:
            if label in row:
                print(row[label], end='\t')
            else:
                print("", end='\t')
        print("")
    #print(table)
    # Return success
    sys.exit(0)

