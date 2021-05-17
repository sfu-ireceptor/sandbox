import argparse
import yaml
import sys

# Extract the block specified from the YAML file. We are expecting an OpenAPI style
# YAML document with the AIRR specific headers and structure. Currently the code
# does not handle the $ref structure, so only basic blocks will be decoded correctly.
def extractBlock(airr_spec_file, block):
    # Open the file
    try:
        with open(airr_spec_file, 'r') as f:
            spec_dict = yaml.safe_load(f)
    except yaml.YAMLError as error:
            print("ERROR: YAML load error detected in " + airr_spec_file + ": " + str(error))
            return 1
    except IOError as error:
        print("ERROR: Unable to open YAML file " + airr_spec_file + ": " + str(error))
        return 1
    except Exception as error:
        print("ERROR: Unable to open YAML file " + airr_spec_file + ": " + str(error))
        return 1

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
    # The YAML block to decode.
    parser.add_argument("block")

    # Parse the command line arguements.
    options = parser.parse_args()
    return options


if __name__ == "__main__":
    # Get the command line arguments.
    options = getArguments()
    # Extract and print out the block information.
    error_code = extractBlock(options.airr_spec_file, options.block)
    # Return success
    sys.exit(error_code)

