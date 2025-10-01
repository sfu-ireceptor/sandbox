#!/bin/bash
# Base source: ChapGPT
# Prompt: Write a bash script that processes a TSV file, takes a list of column headers as input,
# and outputs the file with only the columns specified by the headers

# Function to print the usage of the script
usage() {
    echo "Usage: $0 <filename> <column_headers>"
    echo "Example: $0 data.tsv 'Column1,Column2,Column3'"
    exit 1
}

# Check if the correct number of arguments are provided
if [ $# -ne 2 ]; then
    usage
fi

# Assign arguments to variables
filename=$1
headers=$2

# Check if the file exists
if [ ! -f "$filename" ]; then
    echo "Error: File '$filename' not found!"
    exit 1
fi

# Convert headers into an array
IFS=',' read -r -a header_array <<< "$headers"

# Get the header line
header_line=$(head -n 1 "$filename")

# Convert the header line into an array
IFS=$'\t' read -r -a column_headers <<< "$header_line"

# Initialize an array to store column numbers
column_numbers=()

# Loop through each header provided by the user
for header in "${header_array[@]}"; do
    # Find the column index (1-based) for the current header
    for i in "${!column_headers[@]}"; do
        if [ "${column_headers[$i]}" == "$header" ]; then
            column_numbers+=($(($i + 1)))
            break
        fi
    done
done

# Check if all headers were found
if [ ${#column_numbers[@]} -ne ${#header_array[@]} ]; then
    echo "Error: One or more column headers not found in the file!"
    exit 1
fi

# Join column numbers with commas
column_numbers_str=$(IFS=,; echo "${column_numbers[*]}")

# Extract the specified columns using cut
cut -f"$column_numbers_str" "$filename"

