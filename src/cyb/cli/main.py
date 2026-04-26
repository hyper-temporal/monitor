"""
CLI entry point for Cyb network observability tool.

Implements Click-based CLI with proper error handling, logging, and
modular subcommands following enterprise patterns.
"""

import sys
import logging
from pathlib import Path
from typing import Optional

import click

from cyb import __version__
from cyb.infrastructure import get_logger


def setup_cli_logging(verbose: bool) -> None:
    """Initialize logging for CLI."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level)


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="cyb")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging")
@click.option("-c", "--config", type=click.Path(exists=True), 
              help="Config file path (default: ~/.cyb/config.yaml)")
@click.pass_context
def cli(ctx: click.Context, verbose: bool, config: Optional[str]) -> None:
    """
    Cyb: Enterprise network observability for your machine.
    
    Monitor outbound traffic, create rules, and control network access
    with fine-grained visibility into process-level connections.
    
    Examples:
        cyb monitor              # Start real-time monitoring
        cyb export --format json # Export connection history
    """
    # Ensure context object exists
    if ctx.obj is None:
        ctx.obj = {}
    
    ctx.obj["verbose"] = verbose
    ctx.obj["config"] = config
    
    setup_cli_logging(verbose)
    
    # Show help if no subcommand provided
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.option("-n", "--count", type=int, default=100, 
              help="Number of recent connections to show")
@click.option("--filter", type=str, help="Filter by executable name or IP")
@click.pass_context
def monitor(ctx: click.Context, count: int, filter: Optional[str]) -> None:
    """
    Start real-time network monitoring.
    
    Displays live connections with process information, destination IPs,
    and ports. Requires elevated privileges (sudo).
    """
    from cyb.backend import Monitor
    
    try:
        mon = Monitor(config_path=ctx.obj.get("config"))
        mon.run(limit=count, filter_expr=filter)
    except PermissionError:
        click.secho("✗ Requires root/sudo access", fg="red", err=True)
        sys.exit(1)
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", err=True)
        if ctx.obj.get("verbose"):
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.group()
def config() -> None:
    """Manage configuration."""
    pass


@config.command("show")
@click.pass_context
def config_show(ctx: click.Context) -> None:
    """Display current configuration."""
    from cyb.infrastructure import Config
    
    try:
        cfg = Config(config_path=ctx.obj.get("config"))
        click.echo("\nActive Configuration:\n")
        click.echo(f"  Database: {cfg.get('storage', {}).get('db_path', 'N/A')}")
        click.echo(f"  Capture Interface: {cfg.get('capture', {}).get('interface', 'N/A')}")
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", err=True)
        sys.exit(1)


@cli.command()
@click.option("--format", type=click.Choice(["json", "csv", "sql"]), 
              default="json", help="Export format")
@click.option("--output", type=click.Path(), help="Output file (default: stdout)")
@click.pass_context
def export(ctx: click.Context, format: str, output: Optional[str]) -> None:
    """Export connection history."""
    from cyb.core.export import Exporter
    
    try:
        exp = Exporter()
        data = exp.export(format=format)
        
        if output:
            Path(output).write_text(data)
            click.secho(f"✓ Exported to {output}", fg="green")
        else:
            click.echo(data)
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", err=True)
        sys.exit(1)


def main() -> None:
    """Entry point for console script."""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n\n✗ Interrupted")
        sys.exit(130)
    except Exception as e:
        click.secho(f"✗ Fatal error: {e}", fg="red", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
