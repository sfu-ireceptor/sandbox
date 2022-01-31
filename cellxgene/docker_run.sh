#!/bin/sh

sudo docker run -v "/data/cellxgene/data/:/data/" -p 5005:5005 cellxgene launch --host 0.0.0.0 data/pbmc3k.h5ad
