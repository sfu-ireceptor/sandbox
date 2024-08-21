import sys
import argparse
import json
import csv

def convert(value):
    # Try to convert strings
    if type(value) is str and len(value) > 0:
        # If it looks like it might be JSON string, try to convert
        if value[0] == '{' and value[-1] == '}':
            try:
                # If successful, return it
                return json.loads(value)
            except:
                # If conversion fails, return original
                return value
        else:
            try:
                # Try to convert to int first.
                if '.' not in value:
                    return int(value)
                # If the value has a decimal point, try converting to a float
                return float(value)
            except ValueError:
                # If conversion fails, return the original string
                return value
    return value



# Transform an input TSV file into a JSON array with key value pairs
# according to the values in the row.
def tsv_to_json(tsv_file_handle, json_file_handle):
    # Read the TSV data from the file handle
    reader = csv.DictReader(tsv_file_handle, delimiter='\t')

    # Convert the data to a list of dictionaries
    data = []
    for row in reader:
        dictionary = dict()
        for key, value in row.items():
            dictionary[key] = convert(value)
        data.append(dictionary)

    # Write the data to the JSON file handle
    json.dump(data, json_file_handle, indent=4)
    print('', file=json_file_handle)

def getArguments():
    # Set up the command line parser
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=""
    )
    parser = argparse.ArgumentParser()

    # The input TSV file name
    parser.add_argument("tsv_file_name")
    # JSON output file name
    parser.add_argument(
        "-o",
        "--output",
        dest="json_file_name",
        default="",
        help="The output file, uses stdout if no file provided.")
    # Verbosity flag
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Run the program in verbose mode.")

    # Parse the command line arguements.
    options = parser.parse_args()
    return options


if __name__ == "__main__":
    # Get the command line arguments.
    options = getArguments()

    # Open the ouput file, use stdout if no file name supplied.
    if options.json_file_name == "":
        json_file = sys.stdout
    else:
        try:
            json_file = open(options.json_file_name, mode='w', encoding='utf-8')
        except Exception as e:
            # Gereate an error on failure
            print('ERROR: Unable to open output file %s'%(options.json_file_name))
            print('ERROR: Reason =' + str(e))
            sys.exit(1)

    # Open the input file
    try:
        tsv_file = open(options.tsv_file_name, mode='r', encoding='utf-8')
    except Exception as e:
        # Generate an error on failure
        print('ERROR: Unable to open input file %s'%(options.tsv_file_name))
        print('ERROR: Reason =' + str(e))
        sys.exit(1)

    # Perform the conversion
    tsv_to_json(tsv_file, json_file)

