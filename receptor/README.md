# From IEDB

- Export all receptors from IEDB

From the Excel spreadsheet from IEDB

- Generate a Junction AA for Chain 2 (TRB) column
  - Check if calculate exists
  - Check if curated exists
  - If curated is the same as calculate with C*[WF] then fill in junction_aa

- Generate a _calculated and _curated column for v_gene and j_gene
  - Generate a gene call based on whether the call is allele or gene
  - Essentially drop the allele part

- Generate a v-gene and j_gene column
  - Take the respective _calculated if it exists
  - If not then take the respective _curated value

# Receptor Exports

- 2024-08-06-TRB is the initial IEDB TRB export
- 2025-07-11-TRA is the initial IEDB TRA export
- 2025-08-25-TR-IG is a combined IG and TR export
  - Includes updates for TRA and TRB from previous exports

