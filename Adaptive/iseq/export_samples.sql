
	select
		sample_name,
		total_t_cells,
		total_templates,
		productive_templates,
		fraction_productive,
		total_rearrangements,
		productive_rearrangements,
		productive_clonality,
		max_productive_frequency,
		test_name,
		locus,
		sample_tags
	from
		{samples_table}

