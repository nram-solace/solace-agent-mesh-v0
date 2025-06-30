import sys
import os
import click

from cli.commands.build import build_command
from cli.utils import log_error, log_success
from cli import __version__


def run_solace_ai_connector(configs):
    try:
        from solace_ai_connector.main import main
    except ImportError:
        log_error("Failed to import Solace AI Connector.")
        return 1

    sys.argv = [sys.argv[0].replace("solace-agent-mesh", "solace-ai-connector"), *configs]
    return sys.exit(main())


FILES_TO_EXCLUDE = []


def run_command(
    use_system_env, config_files, exclude_files, quick_build, ignore_build, force_build
):
    """Run the Solace Agent Mesh application."""

    # Print prominent version banner when attempting to start
    click.echo()
    click.echo(click.style("=" * 60, fg="blue", bold=True))
    click.echo(click.style(f"🚀 STARTING SOLACE AGENT MESH", fg="blue", bold=True))
    click.echo(click.style(f"   Version: {__version__}", fg="cyan", bold=True))
    click.echo(click.style("=" * 60, fg="blue", bold=True))
    click.echo()

    config = click.get_current_context().obj["solace_agent_mesh"]
    build_dir = config["build"]["build_directory"]
    build_config_dir = os.path.join(build_dir, "configs")

    if force_build or (not ignore_build and not os.path.exists(build_dir)):
        build_command(skip_without_asking=quick_build)

    click.echo(click.style("📋 Initializing Solace Agent Mesh application...", fg="yellow"))

    if not use_system_env:
        try:
            from dotenv import load_dotenv

            env_file = config["env_file"]
            load_dotenv(env_file, override=True)
        except ImportError:
            log_error(
                "Failed to import dotenv. Please install it using 'pip install python-dotenv'"
            )
            return 1
        except Exception as e:
            log_error(f"Failed to load environment variables. {e}")
            return 1

    if not config_files:
        if not os.path.exists(build_config_dir):
            log_error("No build directory found. Run 'solace-agent-mesh build' first.")
            return 1

        config_files = [
            os.path.join(build_config_dir, f)
            for f in os.listdir(build_config_dir)
            if f.endswith(".yaml")
        ]

    # Exclude files
    # only basename of the files
    exclude_files = [os.path.basename(f) for f in exclude_files] + FILES_TO_EXCLUDE
    config_files = [f for f in config_files if os.path.basename(f) not in exclude_files]

    # Print prominent success message with version before starting the connector
    click.echo()
    click.echo(click.style("✅ SUCCESS!", fg="green", bold=True))
    click.echo(click.style(f"   Solace Agent Mesh version {__version__} is ready to start", fg="green"))
    click.echo(click.style("   Launching components...", fg="green"))
    click.echo()

    return run_solace_ai_connector(config_files)
