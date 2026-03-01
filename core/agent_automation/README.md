# Agent Automation

Autonomous agent system for task planning and execution in Querty-OS.

## Overview

The agent automation framework enables AI agents to plan and execute complex multi-step tasks with varying levels of autonomy.

## Agent Modes

### 1. Autonomous Mode
- Fully autonomous execution
- No user intervention required
- Best for: Routine tasks, system maintenance
- Risk Level: Requires trust

### 2. Supervised Mode
- User confirmation for each step
- Balance between automation and control
- Best for: Important tasks, first-time operations
- Risk Level: Medium

### 3. Interactive Mode
- Step-by-step with user guidance
- Full user control and visibility
- Best for: Learning, complex tasks, critical operations
- Risk Level: Low

## Features

- **Task Planning**: Break down goals into executable steps
- **Multi-step Execution**: Coordinate complex workflows
- **Context Awareness**: Maintain state across steps
- **Error Handling**: Graceful failure recovery
- **Learning**: Improve from feedback
- **Task Queue**: Manage multiple concurrent tasks

## Architecture

```
agent-automation/
├── agent_automation.py     # Main automation framework
├── task_planner.py         # Task planning with LLM (TODO)
├── action_executor.py      # Action execution engine (TODO)
├── learning_engine.py      # Learning from feedback (TODO)
└── workflow_templates.py   # Predefined workflows (TODO)
```

## Usage

```python
from core.agent_automation import AgentAutomationSystem, AgentMode

# Create automation system
system = AgentAutomationSystem()

# Create an agent
agent = system.create_agent("assistant", AgentMode.SUPERVISED)

# Submit a task
task = system.submit_task("assistant", "Install updates and restart")

# Process tasks
system.process_queue()

# Check status
print(f"Status: {task.status}")
```

## Task Examples

### System Maintenance
```
Goal: "Update all applications"
Steps:
1. Check for available updates
2. Download updates
3. Install updates
4. Verify installation
```

### Multi-OS Workflow
```
Goal: "Process document with Linux tools"
Steps:
1. Open file in Android
2. Transfer to Linux chroot
3. Run processing command
4. Return result to Android
```

### Automation Chain
```
Goal: "Daily morning routine"
Steps:
1. Check calendar
2. Read news headlines
3. Check weather
4. Summarize emails
5. Present daily briefing
```

## Learning System

Agents improve through:
- **Success Patterns**: Remember what works
- **Failure Analysis**: Learn from mistakes
- **User Preferences**: Adapt to user habits
- **Feedback Integration**: Incorporate corrections

## Safety Features

- **Confirmation Points**: Critical actions require confirmation
- **Rollback Support**: Undo changes if needed
- **Dry Run Mode**: Preview actions without execution
- **Action Logging**: Full audit trail
- **Resource Limits**: Prevent runaway operations

## Configuration

Settings in `/etc/querty-os/agent-automation.conf`:
- Default agent mode
- Confirmation thresholds
- Resource limits
- Learning rate
- Task timeout

## Development Status

- [x] Agent framework
- [x] Task planning structure
- [x] Execution modes
- [ ] LLM integration for planning
- [ ] Action executor implementation
- [ ] Learning engine
- [ ] Workflow templates
- [ ] Safety controls
