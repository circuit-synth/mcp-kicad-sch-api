"""MCP KiCAD Schematic API Server

Model Context Protocol server providing KiCAD schematic manipulation tools for AI agents.
"""

import asyncio
import logging

import click
from .server import main as serve

__version__ = "0.3.0"

@click.command()
@click.option(
    "--verbose", 
    "-v", 
    count=True, 
    help="Increase verbosity (use -v, -vv, or -vvv)"
)
def main(verbose: int):
    """MCP KiCAD Schematic API Server"""
    # Configure logging based on verbosity
    if verbose == 0:
        logging.basicConfig(level=logging.WARNING, format="%(message)s")
    elif verbose == 1:
        logging.basicConfig(level=logging.INFO, format="%(message)s")
    else:
        logging.basicConfig(level=logging.DEBUG, format="%(name)s: %(message)s")

    # Run the async server
    asyncio.run(serve())

__all__ = ["main"]