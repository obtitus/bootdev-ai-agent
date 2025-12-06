# main.py

import sys
from pkg.calculator import Calculator
from pkg.render import format_json_output


def main():
    calculator = Calculator()
    if len(sys.argv) <= 1:
        print("Calculator App")
        print("Usage: python main.py '<expression>'")
        print("Example: python main.py '2 + 5'")
        return

    expression = " ".join(sys.argv[1:])
    try:
        result = calculator.evaluate(expression)
        if result is not None:
            print(format_json_output(expression, result))
        else:
            print("Error: Expression is empty or contains only whitespace.")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
