#!/bin/bash 

# Find the current output files
# find -L . -name "*header*" -print 

# Count unique sequences
find -L . -name "*header*" -print | xargs cat | grep TRBV | sort -u | wc -l
#3168022

# Count unique TRBV genes
find -L . -name "*header*" -print | xargs cat | grep TRBV | cut -f 3 | sort -u | wc -l
#57

# Count unique TRBJ genes
find -L . -name "*header*" -print | xargs cat | grep TRBV | cut -f 4 | sort -u | wc -l
#13

# Count unique Junction AA 
find -L . -name "*header*" -print | xargs cat | grep TRBV | cut -f 5 | sort -u | wc -l
#48738

# Count unique IEDB Receptors
find -L . -name "*header*" -print | xargs cat | grep TRBV | cut -f 6 | sort -u | wc -l
#49889

# Count unique V/J/Junction/Receptors tuples
# find -L . -name "*header*" -print | xargs cat | grep TRBV | cut -f 3,4,5,6 | sort -u | wc -l
#54819

# Count unique V/J/Junction tuples
find -L . -name "*header*" -print | xargs cat | grep TRBV | cut -f 3,4,5 | sort -u | wc -l
#54816

# Extract the individual data elements
find -L . -name "*header*" -print | xargs cat | grep TRBV | cut -f 3 | sort -u > TRBV.tsv
find -L . -name "*header*" -print | xargs cat | grep TRBV | cut -f 4 | sort -u > TRBJ.tsv
find -L . -name "*header*" -print | xargs cat | grep TRBV | cut -f 5 | sort -u > TRBJunction.tsv
find -L . -name "*header*" -print | xargs cat | grep TRBV | cut -f 6 | jq -r '.[]' | sort -u > TRBReceptor.tsv
find -L . -name "*header*" -print | xargs cat | grep TRBV | cut -f 7 | jq -r '.[]' | sort -u > TRBEpitope.tsv
find -L . -name "*header*" -print | xargs cat | grep TRBV | cut -f 8 | jq -r '.[]' | sort -u > TRBAntigen.tsv
find -L . -name "*header*" -print | xargs cat | grep TRBV | cut -f 9 | jq -r '.[]' | sort -u > TRBAntigenSpecies.tsv
find -L . -name "*header*" -print | xargs cat | grep TRBV | cut -f 10 | jq -r '.[]' | sort -u > TRBHLA.tsv

# Get the counts
wc -l *.tsv
#    260 TRBAntigen.tsv
#     96 TRBAntigenSpecies.tsv
#   1441 TRBEpitope.tsv
#    121 TRBHLA.tsv
#     13 TRBJ.tsv
#  48738 TRBJunction.tsv
#  51364 TRBReceptor.tsv
#     57 TRBV.tsv

# Graph
echo -e "v_gene" > v_gene_tmp.tsv
cut -f 3 hits-sequences-trb-t1d.tsv >> v_gene_tmp.tsv
python3 /data/src/gateway/resources/tapis_apps/rearrangement-stats-singularity/airr_histogram.py v_gene v_gene_tmp.tsv v_gene.png v_gene.tsv "v_gene"

echo -e "j_gene" > j_gene_tmp.tsv
cut -f 4 hits-sequences-trb-t1d.tsv >> j_gene_tmp.tsv
python3 /data/src/gateway/resources/tapis_apps/rearrangement-stats-singularity/airr_histogram.py j_gene j_gene_tmp.tsv j_gene.png j_gene.tsv "j_gene"

echo -e "v_gene\tj_gene" > v_j_heatmap_tmp.tsv
cut -f 3,4 hits-sequences-trb-t1d.tsv >> v_j_heatmap_tmp.tsv
xvals=`cat v_j_heatmap_tmp.tsv | cut -f 1 | awk 'BEGIN {FS=","} {if (NR>1) print($1)}' | sort | uniq | awk '{if (NR>1) printf(",%s", $1); else printf("%s", $1)}'`
yvals=`cat v_j_heatmap_tmp.tsv | cut -f 2 | awk 'BEGIN {FS=","} {if (NR>1) print($1)}' | sort | uniq | awk '{if (NR>1) printf(",%s", $1); else printf("%s", $1)}'`
python3 /data/src/gateway/resources/tapis_apps/rearrangement-stats-singularity/airr_heatmap.py v_gene j_gene $xvals $yvals v_j_heatmap_tmp.tsv vj_heatmap.png vj_heatmap.tsv "V/J Heatmap"

echo -e "epitope" > epitope_tmp.tsv
find -L . -name "*header*" -print | xargs cat | grep TRBV | cut -f 7 |  jq -r '.[]' >> epitope_tmp.tsv
python3 /data/src/gateway/resources/tapis_apps/rearrangement-stats-singularity/airr_histogram.py epitope epitope_tmp.tsv TRB_epitope.png TRB_epitope.tsv "TRB Epitopes"

echo -e "antigen" > antigen_tmp.tsv
find -L . -name "*header*" -print | xargs cat | grep TRBV | cut -f 8 |  jq -r '.[]' >> antigen_tmp.tsv
python3 /data/src/gateway/resources/tapis_apps/rearrangement-stats-singularity/airr_histogram.py antigen antigen_tmp.tsv TRB_antigen.png TRB_antigen.tsv "TRB Antigens"

echo -e "species" > species_tmp.tsv
find -L . -name "*header*" -print | xargs cat | grep TRBV | cut -f 9 |  jq -r '.[]' >> species_tmp.tsv
python3 /data/src/gateway/resources/tapis_apps/rearrangement-stats-singularity/airr_histogram.py species species_tmp.tsv TRB_species.png TRB_species.tsv "TRB Species"

echo -e "HLA" > hla_tmp.tsv
find -L . -name "*header*" -print | xargs cat | grep TRBV | cut -f 10 |  jq -r '.[]' >> hla_tmp.tsv
python3 /data/src/gateway/resources/tapis_apps/rearrangement-stats-singularity/airr_histogram.py HLA hla_tmp.tsv TRB_HLA.png TRB_HLA.tsv "TRB HLA"






