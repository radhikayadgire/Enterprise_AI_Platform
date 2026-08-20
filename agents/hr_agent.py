"""Agent that answers HR policy questions using the HR tool."""

from tools.hr_tool import lookup_policy


class HRAgent:
    def run(self, question: str) -> str:
        return lookup_policy(question)
