company_evaluation = dict(
    name="company_evaluation",
    description="Get the symbol for accessing news data for a company",
    parameters={
        "type": "OBJECT",
        "properties": {
            "symbol": {
                "type": "STRING",
                "description": "Symbol or company name of the company to be evaluated",
            },
        },
    },
)
