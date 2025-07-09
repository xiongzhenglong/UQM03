import pytest
import asyncio
import json

from src.core.engine import UQMEngine, ValidationError, ExecutionError

# Minimal mock connector and context for testing
def mock_get_source_data(step_name):
    if step_name == "get_products":
        return [
            {"product_id": 1, "product_name": "A", "supplier_id": 10},
            {"product_id": 2, "product_name": "B", "supplier_id": 20},
        ]
    if step_name == "suppliers":
        return [
            {"supplier_id": 10, "supplier_name": "供应商甲", "country": "中国"},
            {"supplier_id": 20, "supplier_name": "供应商乙", "country": "美国"},
        ]
    return []

class DummyConnector:
    async def execute_query(self, query):
        # Simulate query filtering by country
        if "中国" in query:
            return [{"supplier_id": 10, "supplier_name": "供应商甲", "country": "中国"}]
        if "美国" in query:
            return [{"supplier_id": 20, "supplier_name": "供应商乙", "country": "美国"}]
        return []

class DummyConnectorManager:
    async def get_default_connector(self):
        return DummyConnector()

@pytest.mark.asyncio
async def test_enrich_with_supplier_param():
    # UQM config from UQM_Enrich_用例集.md 2.5
    uqm_config = {
        "metadata": {
            "name": "EnrichProductWithSupplierParam",
            "description": "产品补充供应商信息，支持国家参数过滤"
        },
        "parameters": [
            {"name": "supplier_country", "type": "string", "default": None}
        ],
        "steps": [
            {
                "name": "get_products",
                "type": "query",
                "config": {
                    "data_source": "products",
                    "dimensions": [
                        {"expression": "product_id", "alias": "product_id"},
                        {"expression": "product_name", "alias": "product_name"},
                        {"expression": "supplier_id", "alias": "supplier_id"}
                    ]
                }
            },
            {
                "name": "enrich_with_supplier",
                "type": "enrich",
                "config": {
                    "source": "get_products",
                    "lookup": {
                        "table": "suppliers",
                        "columns": ["supplier_id", "supplier_name", "country"],
                        "where": [
                            {
                                "field": "country",
                                "operator": "=",
                                "value": "$supplier_country",
                                "conditional": {
                                    "type": "parameter_not_empty",
                                    "parameter": "supplier_country",
                                    "empty_values": [None, ""]
                                }
                            }
                        ]
                    },
                    "on": {"left": "supplier_id", "right": "supplier_id"},
                    "join_type": "left"
                }
            }
        ],
        "output": "enrich_with_supplier"
    }
    parameters = {"supplier_country": "中国"}

    engine = UQMEngine()
    context = {
        "get_source_data": mock_get_source_data,
        "connector_manager": DummyConnectorManager(),
    }

    # Substitute parameters
    try:
        processed_config = engine._substitute_parameters(uqm_config, parameters)
    except Exception as e:
        print(f"Parameter substitution error: {e}")
        assert False, f"Parameter substitution failed: {e}"

    # Run enrich step manually to catch errors
    from src.steps.enrich_step import EnrichStep
    enrich_step_cfg = processed_config["steps"][1]["config"]
    enrich_step = EnrichStep(enrich_step_cfg)
    try:
        result = await enrich_step.execute(context)
        print("Enrich result:", result)
    except Exception as e:
        print(f"Enrich step error: {e}")
        assert False, f"Enrich step failed: {e}" 