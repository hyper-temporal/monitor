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


def setup_cli_logging(config_path: Optional[str]) -> None:
    """Initialize logging from config file."""
    from cyb.infrastructure.logger import setup_logging
    from cyb.infrastructure import Config
    
    # Load config to get log level
    cfg = Config(config_path=config_path)
    log_level_str = cfg.get("logging", {}).get("level", "INFO")
    
    # Convert string to logging level
    level = getattr(logging, log_level_str.upper(), logging.INFO)
    setup_logging(level=level)


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="cyb")
@click.option("-c", "--config", type=click.Path(exists=True), 
              help="Config file path (default: ~/.cyb/config.yaml)")
@click.pass_context
def cli(ctx: click.Context, config: Optional[str]) -> None:
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
    
    ctx.obj["config"] = config
    
    setup_cli_logging(config)
    
    # Show help if no subcommand provided
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.option("-n", "--count", type=int, default=None, 
              help="Number of packets to capture (0=unlimited, default from config)")
@click.option("--filter", type=str, help="Filter by executable name or IP")
@click.pass_context
def monitor(ctx: click.Context, count: Optional[int], filter: Optional[str]) -> None:
    """
    Start real-time network monitoring.
    
    Displays live connections with process information, destination IPs,
    and ports. Requires elevated privileges (sudo).
    """
    from cyb.service import NetworkMonitorService as Monitor
    from cyb.infrastructure import Config
    
    try:
        # Load config once to get packet_count default
        config_path = ctx.obj.get("config")
        cfg = Config(config_path=config_path)
        
        # Use CLI count if provided, otherwise get from config
        if count is None:
            count = cfg.get("capture", {}).get("packet_count", 0)
        
        # Pass Config object instead of path to avoid re-loading
        mon = Monitor(config=cfg)
        mon.run(limit=count, filter_expr=filter)
    except PermissionError:
        click.secho("✗ Requires root/sudo access", fg="red", err=True)
        sys.exit(1)
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", err=True)
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
