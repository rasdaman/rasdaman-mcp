#!/usr/bin/env python3
"""
Rasdaman MCP Server — A FastMCP-based server for rasdaman operations.
Supports http and stdio transports, background execution, and clean shutdown.
"""

import argparse
import logging
import os
from typing import Any

import requests
from fastmcp import FastMCP

from src.rasdaman_actions import RasdamanActions

LOGGING_FORMAT = "%(levelname)s: %(message)s"
DEFAULT_LOG_LEVEL = "INFO"
NOISY_LIBS = [
    "docket.worker",
    "mcp.server.streamable_http_manager",
    "mcp.server.lowlevel.server",
]
DEFAULT_RASDAMAN_URL = "http://localhost:8080/rasdaman/ows"
DEFAULT_RASDAMAN_USERNAME = "rasguest"
DEFAULT_RASDAMAN_PASSWORD = "rasguest"
DEFAULT_MCP_PORT = 8000
DEFAULT_MCP_HOST = "127.0.0.1"
DEFAULT_MCP_TRANSPORT = "stdio"


# ---------------------------------------
# Setup logging, arg parsing & validation
# ---------------------------------------


def configure_logging(log_level=DEFAULT_LOG_LEVEL):
    """Configure root logging and silence noisy third-party libraries."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=LOGGING_FORMAT,
        stream=None
    )
    # Silence noisy libraries (suppress INFO-level noise)
    for lib in NOISY_LIBS:
        logging.getLogger(lib).setLevel(logging.WARNING)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Rasdaman MCP server -- LLM-powered access to a rasdaman database.")
    parser.add_argument(
        "--transport", type=str, default=DEFAULT_MCP_TRANSPORT,
        choices=[DEFAULT_MCP_TRANSPORT, "http"],
        help=f"Transport protocol for communication with the MCP client (default: {DEFAULT_MCP_TRANSPORT})",
    )
    parser.add_argument(
        "--port", type=int, default=DEFAULT_MCP_PORT,
        help=f"Port for HTTP transport (default: {DEFAULT_MCP_PORT})",
    )
    parser.add_argument(
        "--host", type=str, default=DEFAULT_MCP_HOST,
        help=f"Host for HTTP transport (default: {DEFAULT_MCP_HOST})",
    )
    parser.add_argument(
        "--rasdaman-url", type=str, default=os.getenv("RASDAMAN_URL", DEFAULT_RASDAMAN_URL),
        help=f"rasdaman OWS endpoint (default: {DEFAULT_RASDAMAN_URL})",
    )
    parser.add_argument(
        "--username", type=str, default=os.getenv("RASDAMAN_USERNAME", DEFAULT_RASDAMAN_USERNAME),
        help=f"rasdaman username (default: {DEFAULT_RASDAMAN_USERNAME})",
    )
    parser.add_argument(
        "--password", type=str, default=os.getenv("RASDAMAN_PASSWORD", DEFAULT_RASDAMAN_PASSWORD),
        help=f"rasdaman password (default: {DEFAULT_RASDAMAN_PASSWORD})",
    )
    parser.add_argument(
        "--log-level", type=str, default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: INFO)",
    )
    return parser.parse_args()


def validate_rasdaman_connection(rasdaman_url):
    """Validate rasdaman_url is reachable"""
    try:
        resp = requests.head(rasdaman_url, timeout=5)
        logging.debug(f"Rasdaman URL is reachable: {resp.status_code}")
    except requests.RequestException as e:
        logging.warning(f"Could not reach Rasdaman at {rasdaman_url}: {e}")


# ------------------------
# FastMCP App Factory
# ------------------------

def create_mcp_app(rasdaman_url, rasdaman_username, rasdaman_password) -> FastMCP:
    """Factory function to build the FastMCP app with tools."""
    mcp = FastMCP(
        name="Rasdaman MCP Server",
        instructions="""This server provides access to a rasdaman multi-dimensional geo-spatial database instance.
Follow this workflow for best results:

1. DISCOVER: Start with `list_coverages()` to see available datacubes;
2. EXPLORE: Use `describe_coverage(coverage_id)` to understand a specific datacube (axes, bands, metadata);
3. LEARN: WCPS query syntax with `wcps_query_crash_course()`;
4. EXECUTE: Use `execute_wcps_query(query)` to run a WCPS query;
5. DEEP-DIVE: when the crash course is not enough or a query keeps failing,
   list detailed documentation chapters with `wcps_doc_chapters()` and fetch
   the relevant one with `wcps_get_chapter(name)` (after errors, start with
   the 'common-errors' chapter).

**IMPORTANT RULES:**

- Always subset data (temporal and spatial) to avoid retrieving GBs of data;
- Use encode() with appropriate format: 'png' for 2D visualization, 'netcdf' for n-D data, 'json' for 1-D data;
- Scalar results (avg, min, max, etc.) don't need encode();
- Use 'and'/'or' not '&&'/'||'; pow() not '^'; '$c.band' not '$c[band]' or '$c/band';
- The let clause consists of a **single** 'let' keyword followed by multiple **comma-separated** variable definitions.
"""
    )

    ras_actions = RasdamanActions(
        rasdaman_url=rasdaman_url, username=rasdaman_username, password=rasdaman_password
    )

    @mcp.tool()
    def list_coverages() -> str:
        """
        Lists all available datacubes (coverages) in rasdaman.
        """
        return ras_actions.list_coverages_action()

    @mcp.tool()
    def describe_coverage(coverage_id: str) -> str:
        """
        Retrieves structural metadata for a specific datacube (coverage).
        """
        return ras_actions.describe_coverage_action(coverage_id)

    @mcp.tool()
    def wcps_query_crash_course() -> str:
        """
        Returns a crash course on writing WCPS queries:
        learn the basic syntax, common operations, and best practices for WCPS queries.
        It's recommended to check this before executing queries.
        """
        return ras_actions.wcps_query_crash_course_action()

    @mcp.tool()
    def execute_wcps_query(wcps_query: str) -> dict:
        """
        Executes a Web Coverage Processing Service (WCPS) query in rasdaman.
        Use this for spatio-temporal subsetting of datacubes, processing, aggregation, filtering.

        Returns a structured dictionary indicating success, result_type, original query, the
        actual result value for scalar and small JSON or file path for large/binary results.

        **Important:** Show the actual WCPS query and the result file path to the user.
        """
        return ras_actions.execute_wcps_query_action(wcps_query)

    @mcp.tool()
    def wcps_doc_chapters() -> str:
        """
        Lists the detailed WCPS documentation chapters, one per topic, each
        with a description of what it covers and when to fetch it. Use when
        the crash course is not detailed enough — pick the chapter matching
        your problem and fetch it with wcps_get_chapter(name). After a failed
        query, the 'common-errors' chapter maps error symptoms to fixes.
        """
        lines = []
        for path in sorted(_chapters_dir().glob("*.md")):
            desc = _chapter_description(path)
            lines.append(f"- {path.stem}: {desc}")
        return "\n".join(lines) if lines else "No documentation chapters installed."

    @mcp.tool()
    def wcps_get_chapter(name: str) -> str:
        """
        Returns one full WCPS documentation chapter (markdown) by name, as
        listed by wcps_doc_chapters(). Example: wcps_get_chapter("switch-case").
        """
        path = _chapters_dir() / f"{name.strip()}.md"
        if not path.is_file():
            available = ", ".join(p.stem for p in sorted(_chapters_dir().glob("*.md")))
            return f"Unknown chapter '{name}'. Available chapters: {available}"
        return path.read_text()

    return mcp


# ---------------------------------------
# WCPS documentation chapters
# ---------------------------------------
# Chapters are markdown files shipped with the package; each carries its own
# description in YAML-style frontmatter (---\ndescription: ...\n---). Adding a
# chapter = dropping a new .md file into src/wcps_chapters/ — no other change.

def _chapters_dir():
    from pathlib import Path
    return Path(__file__).resolve().parent / "wcps_chapters"


def _chapter_description(path) -> str:
    lines = path.read_text().splitlines()
    if lines and lines[0].strip() == "---":
        for line in lines[1:10]:
            if line.strip() == "---":
                break
            if line.startswith("description:"):
                return line[len("description:"):].strip()
    return "(no description)"


def main():
    """Entrypoint."""
    args = parse_args()
    log_level = args.log_level.upper()
    configure_logging(log_level=log_level)
    validate_rasdaman_connection(args.rasdaman_url)
    mcp = create_mcp_app(args.rasdaman_url, args.username, args.password)
    if args.transport == 'http':
        mcp.run(transport=args.transport, port=args.port, host=args.host, log_level=log_level, show_banner=False)
    else:
        mcp.run(transport=args.transport, log_level=log_level, show_banner=False)


if __name__ == "__main__":
    main()
