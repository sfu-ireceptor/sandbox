
	select
		rearrangement,
		amino_acid,
		bio_identity,
		templates,
		frame_type,
		rearrangement_type,
		cdr3_length,
		frequency,
		productive_frequency,
		v_resolved,
		d_resolved,
		j_resolved,
		v_family,
		v_family_ties,
		v_gene,
		v_gene_ties,
		v_allele,
		v_allele_ties,
		d_family,
		d_family_ties,
		d_gene,
		d_gene_ties,
		d_allele,
		d_allele_ties,
		j_family,
		j_family_ties,
		j_gene,
		j_gene_ties,
		j_allele,
		j_allele_ties
	from
		{sequences_table}
	where
		sample_name = 'SAMPLE_NAME_TOKEN' 




