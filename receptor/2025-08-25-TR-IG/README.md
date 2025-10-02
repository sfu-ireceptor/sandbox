# Full TR and IG export as of 2025-08-25

This export was produced on 2025-08-25, using the process described in
the directory above. 

Generated full files for TR[AG], TR[BD], IG heavy and IG light

Also generated a difference file for the TR[BD] receptors that were added
from the IEDB export from 2024-08-06 (the original export).

No receptors were removed, so we can do an additional annotation of these
receptors and simply add it to the previous computed chain annotations.


## Generate TRA/TRB
```bash
bash ../iedb2chains.sh 2025-08-25-iedb_tcr_positive_v3.tsv tra TR[ABGD]
bash ../iedb2chains.sh 2025-08-25-iedb_tcr_positive_v3.tsv trb TR[ABGD]
```

## Generate IG heavy and light
```bash
bash ../iedb2chains.sh 2025-08-25-bcr_receptor_table_export_1753794648.tsv heavy IG[HKL]
bash ../iedb2chains.sh 2025-08-25-bcr_receptor_table_export_1753794648.tsv light IG[HKL]
```

## Get file counts
```bash
wc -l *tr*unique*.tsv
  24877 2025-08-25-iedb_tcr_positive_v3_tail_tra_full_chain_unique.tsv
 135067 2025-08-25-iedb_tcr_positive_v3_tail_trb_full_chain_unique.tsv
 159944 total

wc -l *bcr*unique*.tsv
  2881 2025-08-25-bcr_receptor_table_export_1753794648_tail_heavy_full_chain_unique.tsv
  2064 2025-08-25-bcr_receptor_table_export_1753794648_tail_light_full_chain_unique.tsv
  4945 total

```

## Compute differences between this and the 2024-08-06 TRB export
```bash
grep -F -x -v -f ../2024-08-06/iedb_tcr_positive_v3_tail_trb_full_receptor_unique_2024-08-06.tsv 2025-08-25-iedb_tcr_positive_v3_tail_trb_full_chain_unique.tsv > 2025-08-25_trb_additions_from_2024-08-06.tsv
```

## Compute differences between this and the 2025-07-11 TRA export
```bash
grep -F -x -v -f ../2025-07-11/iedb_tcr_positive_v3_tail_tra_full_receptor_unique_2025-07-11.tsv 2025-08-25-iedb_tcr_positive_v3_tail_tra_full_chain_unique.tsv > 2025-08-25_tra_additions_from_2025-07-11.tsv
```

## The differences between exports

```bash
wc -l *additions*.tsv
 1296 2025-08-25_tra_additions_from_2025-07-11.tsv
  246 2025-08-25_trb_additions_from_2024-08-06.tsv
 1542 total
```

