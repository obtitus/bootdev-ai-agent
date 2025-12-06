import json


def format_json_output(expression: str, result: float, indent: int = 2) -> str:
    if isinstance(result, float) and result.is_integer():
        result = int(result)

    output_data = {"expression": expression, "result": result}

    return json.dumps(output_data, indent=indent)
