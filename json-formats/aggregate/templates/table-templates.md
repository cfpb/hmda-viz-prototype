* left trailing commas where there could be more than one *
* theres a line somewhere, descriptive is good but can make it overcomplex *

# table i

"institutions": [
	"name",
	"name"
]

# table 1

"tracts": [
	{
		"State/County/Tract Number": { // including msa/md(total) and invalid geo
			"% min pop": 0,
			"median income as % of msa/md": 0,
			"loan dispositions": [
				{
					"loan disposition": { // loans originated, apps approved, etc
						"loan types": [
							{
								"loan type": { // FHA, conventional, etc
									"count": 0,
									"value": 0
								},
							}
						]
					},
				},
			]
		},
	},
]

# table 2

"tracts": [
	{
		"State/County/Tract Number": {
			"loan types": [
				"loan type": { // FHA, conventional, etc
					"count": 0,
					"value": 0
				},
			]
		},
	},
]

# table 3-1

"borrower-characteristics": [
	{
		"characteristic": [ // race, ethnicity, etc
			{
				"categories": [
					{
						"category": { // american indian, asian, etc
							"purchasers": [
								{
									"purchaser": { // fannie mae, ginnie mae, etc
										"count": 0,
										"value": 0
									},
								}
							]
						},
					}
				]
			},
		]
	},
],
"census-characteristics": [
	{
		"characteristic": [ // race, income, etc
			{
				"categories": [
					{
						"category": { // american indian, asian, etc
							"purchasers": [
								{
									"purchaser": { // fannie mae, ginnie mae, etc
										"count": 0,
										"value": 0
									},
								}
							]
						},
					}
				]
			},
		]
	},
],
"total": {
	"purchasers": [
		{
			"purchaser": { // fannie mae, ginnie mae, etc
				"count": 0,
				"value": 0
			},
		},
	]
}

# table 3-2

"no reported pricing data": {
	"purchasers": [
		{
			"purchaser": { // fannie mae, ginnie mae, etc
				"first-lien-count": 0,
				"junior-lien-count": 0
			},
		}
	]
},
"reported pricing data": {
	"purchasers": [
		{
			"purchaser": { // fannie mae, ginnie mae, etc
				"first-lien-count": 0,
				"junior-lien-count": 0
			},
		}
	]
},
"percentage points above average prime offer rate: only includes loans with APR above the threshold": [
	{
		"percentage range": { // 1.50-1.99, 2.00-2.49, etc
			"purchasers": [
				{
					"purchaser": { // fannie mae, ginnie mae, etc
						"first-lien-count": 0,
						"junior-lien-count": 0
					},
				}
			]
		}
	},
],
"hoepa loans": {
	"purchasers": [
		{
			"purchaser": { // fannie mae, ginnie mae, etc
				"first-lien-count": 0,
				"junior-lien-count": 0
			},
		}
	]
}

# table 4-1, -2, -3, -4, -5, -6, -7

"races": [
	{
		"race": [ // american indian, asian, etc
			{
				"genders": [
					{
						"gender": { // male, female, joint
							"dispositions": [
								{
									"disposition": { // applications received, loans originated, etc
										"count": 0,
										"value": 0
									},
								}
							]
						},
					}
				]
			},
		]
	}
],
"enthnicities": [
	{
		"enthicity": [ // hispanic or latino, not hispanic or latino, etc
			{
				"genders": [
					{
						"gender": { // male, female, joint
							"dispositions": [
								{
									"disposition": { // applications received, loans originated, etc
										"count": 0,
										"value": 0
									},
								}
							]
						},
					}
				]
			},
		]
	}
],
"minority statuses": [
	{
		"status": [ // white non-hispanic, other
			{
				"genders": [
					{
						"gender": { // male, female, joint
							"dispositions": [
								{
									"disposition": { // applications received, loans originated, etc
										"count": 0,
										"value": 0
									},
								}
							]
						},
					}
				]
			},
		]
	}
],
"incomes": [
	{
		"income": [ // less than 50%, 50-79%, etc
			{
				"dispositions": [
					{
						"disposition": { // applications received, loans originated, etc
							"count": 0,
							"value": 0
						},
					}
				]
			},
		]
	}
],
"total": {
	"dispositions": [
		{
			"disposition": { // applications received, loans originated, etc
				"count": 0,
				"value": 0
			},
		},
	]
}

# table 5-1, -2, -3, -4, -6, -7 (there is no -5)

"incomes": [
	"income": { // less the 50%, 50-79%, etc
		"races": [
			"race": { // american indian, asian, etc
				"dispositions": [
					{
						"disposition": { // applications received, loans originated, etc
							"count": 0,
							"value": 0
						},
					},
				]
			}
		],
		"ethnicities": [
			"ethnicity": { // hispanic, not hispanic, etc
				"dispositions": [
					{
						"disposition": { // applications received, loans originated, etc
							"count": 0,
							"value": 0
						},
					},
				]
			}
		],
		"minority statuses": [
			"status": { // white non-hispanic, others
				"dispositions": [
					{
						"disposition": { // applications received, loans originated, etc
							"count": 0,
							"value": 0
						},
					},
				]
			}
		],
	}
],
"total": {
	"dispositions": [
		{
			"disposition": { // applications received, loans originated, etc
				"count": 0,
				"value": 0
			},
		},
	]
}

# table 7-1, -2, -3, -4, -5, -6, -7

"type of tracts": [
	"types of comp": { // racial comp, income char
		"comp": { // less than 10%, 10-19%, etc (for income its low income, moderate income, etc)
			"dispositions": [
				{
					"disposition": { // applications received, loans originated, etc
						"count": 0,
						"value": 0
					},
				},
			]
		}
	}
],
"income & racial comp": [
	"incomes": { // low, moderate, etc
		"income": { // less than 10%, 10-19%, etc
			"dispositions": [
				{
					"disposition": { // applications received, loans originated, etc
						"count": 0,
						"value": 0
					},
				},
			]
		}
	}
],
"small county": {
	"dispositions": [
		{
			"disposition": { // applications received, loans originated, etc
				"count": 0,
				"value": 0
			},
		},
	]
},
"all other tracts": {
	"dispositions": [
		{
			"disposition": { // applications received, loans originated, etc
				"count": 0,
				"value": 0
			},
		},
	]
},
"total": {
	"dispositions": [
		{
			"disposition": { // applications received, loans originated, etc
				"count": 0,
				"value": 0
			},
		},
	]
}

# table 8-1, -2, -3, -4, -6, -7 (there is no -5)

"applicant-characteristics": [
	{
		"characteristic": [ // race, ethnicity, etc
			{
				"categories": [
					{
						"category": { // american indian, asian, etc
							"denial reasons": [
						{
							"reason": { // debt-to-income, employment, etc
								"number": 0,
								"%": 0
							},
						}
					]
						},
					}
				]
			},
		]
	},
]

# table 9

"ages of homes": [
	"age": { // 2000-2010, 1990-1999, etc
		"loan dispositions": [
			{
				"loan disposition": { // loans originated, apps approved, etc
					"loan types": [
						{
							"loan type": { // FHA, conventional, etc
								"count": 0,
								"value": 0
							},
						}
					]
				},
			},
		]
	},
]

# table 11-1, -2, -3, -4, -5, -6, -7, -8, -9, -10 (count and values are in 2 separate tables but merged here)

"borrower-characteristics": [
	{
		"characteristic": [ // race, ethnicity, etc
			{
				"categories": [
					{
						"category": { // american indian, asian, etc, OR less than 10%, 10-19%, etc, OR male, female, etc
							"pricing data": [
								{
									"pricing": { // no reporting data, reported data, 1.50-1.99, mean, median, etc
										"count": 0,
										"value": 0
									},
								}
							]
						},
					}
				]
			},
		]
	},
],
"census-characteristics": [
	{
		"characteristic": [ // racial comp, income characteristics
			{
				"categories": [
					{
						"category": { // american indian, asian, etc, OR less than 10%, 10-19%, etc, OR male, female, etc
							"pricing data": [
								{
									"pricing": { // no reporting data, reported data, 1.50-1.99, mean, median, etc
										"count": 0,
										"value": 0
									},
								}
							]
						},
					}
				]
			},
		]
	},
]

# table 12-1

"borrower-characteristics": [
	{
		"characteristic": [ // race, ethnicity, etc
			{
				"categories": [
					{
						"category": { // american indian, asian, etc, OR less than 10%, 10-19%, etc, OR male, female, etc
							"dispositions": [
								{
									"disposition": { // applications received, loans originated, etc
										"count": 0,
										"value": 0
									},
								}
							]
						},
					}
				]
			},
		]
	},
],
"census-characteristics": [
	{
		"characteristic": [ // racial comp, income characteristics
			{
				"categories": [
					{
						"category": { // american indian, asian, etc, OR less than 10%, 10-19%, etc, OR male, female, etc
							"dispositions": [
								{
									"disposition": { // applications received, loans originated, etc
										"count": 0,
										"value": 0
									},
								}
							]
						},
					}
				]
			},
		]
	},
]

# table 12-2 (count and values are in 2 separate tables but merged here) - alot like 11's

"borrower-characteristics": [
	{
		"characteristic": [ // race, ethnicity, etc
			{
				"categories": [
					{
						"category": { // american indian, asian, etc, OR less than 10%, 10-19%, etc, OR male, female, etc
							"pricing data": [
								{
									"pricing": { // no reporting data, reported data, 1.50-1.99, mean, median, etc
										"count": 0,
										"value": 0
									},
								}
							]
						},
					}
				]
			},
		]
	},
],
"census-characteristics": [
	{
		"characteristic": [ // racial comp, income characteristics
			{
				"categories": [
					{
						"category": { // less than 10%, 10-19%, etc OR low income, moderate, etc
							"pricing data": [
								{
									"pricing": { // no reporting data, reported data, 1.50-1.99, mean, median, etc
										"count": 0,
										"value": 0
									},
								}
							]
						},
					}
				]
			},
		]
	},
]

# table a-1, -2, -3

"dispositions": [
	{
		"disposition": { // total, loans originated, approved not accepted, etc
			"loan types": [
				{
					"loan type": { // FHA, conventional, etc
						"loan-uses": [
							{
								"loan-use": { // purchase, refi, improvement
									"first-lien": 0,
									"junior-lien": 0
								}
							}
						]
					},
				}
			]
		},
	}
]

# table a-4 - alot like 11's and 12's

"borrower-characteristics": [
	{
		"characteristic": { // race, ethnicity, etc
			"categories": [
				{
					"category": { // american indian, asian, etc, OR less than 10%, 10-19%, etc, OR male, female, etc
						"dispositions": [
							{
								"disposition": { // preappovals
									"count": 0,
									"value": 0
								},
							}
						]
					},
				}
			]
		},
	},
],
"census-characteristics": [
	{
		"characteristic": [ // racial comp, income characteristics
			{
				"categories": [
					{
						"category": { // american indian, asian, etc, OR less than 10%, 10-19%, etc, OR male, female, etc
							"dispositions": [
								{
									"disposition": { // preappovals
										"count": 0,
										"value": 0
									},
								}
							]
						},
					}
				]
			},
		]
	},
]

# table b

"types of dwellings": [
	{
		"type": { // 1-4 family, manufactured
			"statuses": [
				{
					"status": { // incidence of pricing, hoepa status
						"loan-uses": [
							{
								"loan-use": { // purchase, refi, improvement
									"first-lien": 0,
									"junior-lien": 0
								}
							}
						]
					}
				}
			}
		}
	}
]
