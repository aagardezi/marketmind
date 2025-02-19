shareprice = dict(
    name="shareprice",
    description="Get the current share price for the symbol supplied",
    parameters={
        "type": "OBJECT",
        "properties": {
            "symbol": {
                "type": "STRING",
                "description": "Symbol for the company",
            },
        },
    },
)