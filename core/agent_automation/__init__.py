"""Querty-OS Agent Automation Package"""

from .action_executor import Action, ActionExecutor, ActionResult, ActionStatus, CommandAction
from .agent_automation import Agent, AgentAutomationSystem, AgentMode, Task, TaskStatus
from .workflow_templates import WorkflowStep, WorkflowTemplate, WorkflowTemplates

__version__ = "0.1.0"
__all__ = [
    "Agent",
    "AgentAutomationSystem",
    "AgentMode",
    "Task",
    "TaskStatus",
    "ActionExecutor",
    "Action",
    "CommandAction",
    "ActionResult",
    "ActionStatus",
    "WorkflowTemplates",
    "WorkflowTemplate",
    "WorkflowStep",
]
