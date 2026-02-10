#!/usr/bin/env python3
"""
Example Calculator Plugin
Demonstrates a tool plugin that performs arithmetic operations.
"""

from core.plugin_system import Plugin, PluginType


class CalculatorPlugin(Plugin):
    """Calculator tool plugin."""

    def __init__(self):
        super().__init__(name="Calculator", version="1.0.0", plugin_type=PluginType.TOOL)
        self.metadata = {
            "author": "Querty-OS Team",
            "description": "Basic arithmetic calculator",
            "operations": ["add", "subtract", "multiply", "divide"],
        }

    def initialize(self) -> bool:
        """Initialize the calculator plugin."""
        self.enabled = True
        return True

    def execute(self, **kwargs) -> any:
        """Execute calculator operation."""
        operation = kwargs.get("operation")
        a = kwargs.get("a", 0)
        b = kwargs.get("b", 0)

        if operation == "add":
            return a + b
        elif operation == "subtract":
            return a - b
        elif operation == "multiply":
            return a * b
        elif operation == "divide":
            if b == 0:
                raise ValueError("Division by zero")
            return a / b
        else:
            raise ValueError(f"Unknown operation: {operation}")

    def shutdown(self):
        """Shutdown the calculator plugin."""
        self.enabled = False


# Example usage
if __name__ == "__main__":
    calc = CalculatorPlugin()
    calc.initialize()

    print(f"Plugin: {calc.get_info()}")
    print(f"5 + 3 = {calc.execute(operation='add', a=5, b=3)}")
    print(f"10 - 4 = {calc.execute(operation='subtract', a=10, b=4)}")
    print(f"6 * 7 = {calc.execute(operation='multiply', a=6, b=7)}")
    print(f"15 / 3 = {calc.execute(operation='divide', a=15, b=3)}")
