#!/usr/bin/env python3
"""
Querty-OS Command-Line Interface
Provides CLI commands for system control and monitoring.
"""

import json
import logging
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

logger = logging.getLogger("querty-cli")
console = Console()


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option("--config", type=click.Path(), help="Config file path")
@click.pass_context
def cli(ctx, debug: bool, config: Optional[str]):
    """Querty-OS - AI-Powered Mobile Operating System"""
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug
    ctx.obj["config"] = config

    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


@cli.command()
@click.pass_context
def status(ctx):
    """Display system status"""
    console.print("[bold blue]Querty-OS System Status[/bold blue]\n")

    table = Table(title="Service Status")
    table.add_column("Service", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Info")

    services = [
        ("AI Daemon", "Running", "LLM loaded"),
        ("Memory Manager", "Running", "8192/8192 tokens"),
        ("Input Handlers", "Running", "Voice, Camera, Text"),
        ("OS Control", "Running", "Android + Linux"),
        ("Network Manager", "Running", "Connected"),
    ]

    for service, status, info in services:
        table.add_row(service, status, info)

    console.print(table)


@cli.group()
def service():
    """Service management commands"""
    pass


@service.command()
@click.argument("service_name")
def start(service_name: str):
    """Start a service"""
    console.print(f"[green]Starting service:[/green] {service_name}")
    logger.info(f"Starting service: {service_name}")


@service.command()
@click.argument("service_name")
def stop(service_name: str):
    """Stop a service"""
    console.print(f"[yellow]Stopping service:[/yellow] {service_name}")
    logger.info(f"Stopping service: {service_name}")


@service.command()
@click.argument("service_name")
def restart(service_name: str):
    """Restart a service"""
    console.print(f"[blue]Restarting service:[/blue] {service_name}")
    logger.info(f"Restarting service: {service_name}")


@cli.group()
def task():
    """Task execution commands"""
    pass


@task.command()
@click.argument("task_description")
@click.option("--priority", type=int, default=1, help="Task priority (1-5)")
@click.option("--mode", type=click.Choice(["auto", "interactive"]), default="auto")
def execute(task_description: str, priority: int, mode: str):
    """Execute a task"""
    console.print(f"[bold]Executing task:[/bold] {task_description}")
    console.print(f"Priority: {priority}, Mode: {mode}")
    logger.info(f"Task: {task_description}, priority={priority}, mode={mode}")


@task.command()
def list():
    """List active tasks"""
    console.print("[bold]Active Tasks[/bold]\n")

    table = Table()
    table.add_column("ID", style="cyan")
    table.add_column("Description")
    table.add_column("Status", style="green")
    table.add_column("Priority")

    tasks = [
        ("001", "Process camera input", "Running", "3"),
        ("002", "Update system packages", "Queued", "2"),
    ]

    for task_id, desc, status, priority in tasks:
        table.add_row(task_id, desc, status, priority)

    console.print(table)


@task.command()
@click.argument("task_id")
def cancel(task_id: str):
    """Cancel a task"""
    console.print(f"[red]Cancelling task:[/red] {task_id}")
    logger.info(f"Cancelling task: {task_id}")


@cli.group()
def logs():
    """Log management commands"""
    pass


@logs.command()
@click.option("--lines", "-n", type=int, default=50, help="Number of lines to show")
@click.option("--follow", "-f", is_flag=True, help="Follow log output")
@click.option("--service", help="Filter by service name")
def show(lines: int, follow: bool, service: Optional[str]):
    """Show system logs"""
    if service:
        console.print(f"[bold]Logs for service:[/bold] {service}")
    else:
        console.print("[bold]System Logs[/bold]")

    console.print(f"Showing last {lines} lines...")
    if follow:
        console.print("[dim]Following log output... (Ctrl+C to stop)[/dim]")


@logs.command()
def clear_logs():
    """Clear system logs"""
    console.print("[yellow]Clearing system logs...[/yellow]")
    logger.warning("Logs cleared by user")


@cli.group()
def memory():
    """Memory management commands"""
    pass


@memory.command()
def info():
    """Show memory information"""
    console.print("[bold blue]Memory Information[/bold blue]\n")

    table = Table()
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    metrics = [
        ("Total Tasks", "42"),
        ("Context Tokens", "6234/8192"),
        ("Utilization", "76%"),
        ("Oldest Task", "2024-01-15 10:30:00"),
    ]

    for metric, value in metrics:
        table.add_row(metric, value)

    console.print(table)


@memory.command()
def optimize():
    """Optimize memory usage"""
    console.print("[yellow]Optimizing memory...[/yellow]")
    logger.info("Memory optimization started")


@memory.command()
@click.confirmation_option(prompt="Are you sure you want to clear all memory?")
def clear_memory():
    """Clear all memory"""
    console.print("[red]Clearing all memory...[/red]")
    logger.warning("Memory cleared by user")


@cli.group()
def config():
    """Configuration commands"""
    pass


@config.command()
def show_config():
    """Show current configuration"""
    console.print("[bold]Current Configuration[/bold]\n")
    config_data = {
        "llm_mode": "deterministic",
        "max_context_tokens": 8192,
        "storage_path": "~/.querty",
    }
    console.print(json.dumps(config_data, indent=2))


@config.command()
@click.argument("key")
@click.argument("value")
def set_config(key: str, value: str):
    """Set a configuration value"""
    console.print(f"[green]Setting {key} = {value}[/green]")
    logger.info(f"Config updated: {key}={value}")


if __name__ == "__main__":
    cli(obj={})
