#!/usr/bin/env python3
"""
Example Greeter Skill Plugin
Demonstrates a skill plugin for AI interactions.
"""

from datetime import datetime
from core.plugin_system import Plugin, PluginType


class GreeterSkill(Plugin):
    """Greeter skill plugin."""

    def __init__(self):
        super().__init__(name="Greeter", version="1.0.0", plugin_type=PluginType.SKILL)
        self.metadata = {
            "author": "Querty-OS Team",
            "description": "Greet users with time-appropriate messages",
            "capabilities": ["greet", "farewell", "check_time"],
        }

    def initialize(self) -> bool:
        """Initialize the greeter skill."""
        self.enabled = True
        return True

    def execute(self, **kwargs) -> any:
        """Execute greeter skill."""
        action = kwargs.get("action", "greet")
        name = kwargs.get("name", "User")

        if action == "greet":
            hour = datetime.now().hour
            if hour < 12:
                greeting = "Good morning"
            elif hour < 18:
                greeting = "Good afternoon"
            else:
                greeting = "Good evening"
            return f"{greeting}, {name}! How can I assist you today?"

        elif action == "farewell":
            return f"Goodbye, {name}! Have a great day!"

        elif action == "check_time":
            now = datetime.now()
            return f"It's currently {now.strftime('%H:%M:%S')} on {now.strftime('%A, %B %d, %Y')}"

        else:
            raise ValueError(f"Unknown action: {action}")

    def shutdown(self):
        """Shutdown the greeter skill."""
        self.enabled = False


# Example usage
if __name__ == "__main__":
    greeter = GreeterSkill()
    greeter.initialize()

    print(f"Plugin: {greeter.get_info()}")
    print("\nExamples:")
    print(greeter.execute(action="greet", name="Alice"))
    print(greeter.execute(action="check_time"))
    print(greeter.execute(action="farewell", name="Alice"))
