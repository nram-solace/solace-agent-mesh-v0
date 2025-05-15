---
title: Installation
sidebar_position: 20
---

# Prerequisites

Before you begin, make sure you have the following:

- **Python 3.10.16+**
- **pip** (usually included with Python)
- **Operating System**: macOS, Linux, or Windows (via [WSL](https://learn.microsoft.com/en-us/windows/wsl/))
- **LLM API key** from any major provider or your own custom endpoint.

# Installation

[Solace Agent Mesh Module](https://pypi.org/project/solace-agent-mesh) comes with two components:
1. **Solace Agent Mesh (SAM) CLI**: To create, build, run, and extend Solace Agent Mesh.
2. **Solace Agent Mesh framework**: A Python-based framework that you can build upon to customize and extend the capabilities of Solace Agent Mesh.

Installing the PyPi package will install both the SAM CLI and the framework (which is built on the Python SDK).

:::tip
We recommend that you install the package in a virtual environment to avoid conflicts with other Python packages.
:::

<details>
    <summary>Creating a Virtual Environment</summary>

1. Create a virtual environment.

```
python3 -m venv .venv
```

2. Activate the environment.

   To activate on Linux or Unix platforms:
    ```sh
    source .venv/bin/activate
    ```

    To activate on Windows:

    ```cmd
    .venv\Scripts\activate
    ```
</details>

**Install Solace Agent Mesh**

1. The following command installs the Solace Agent Mesh (SAM) CLI in your environment:

```sh
pip install solace-agent-mesh
```
:::info Docker Alternative
Alternatively, you can use our pre-built Docker image to run SAM CLI commands without a local Python installation. This is useful for quick tasks or CI/CD environments.

To verify the installation using Docker, you can run:
```sh
docker run --rm solace/solace-agent-mesh:latest --version
```
This command pulls the latest image (if not already present) and executes `solace-agent-mesh --version` inside the container. The `--rm` flag ensures the container is removed after execution.

For more complex operations like building a project, you'll need to mount your project directory into the container. See the [Quick Start guide](./quick-start.md) for an example.
:::

<details>
    <summary>PlantUML Installation Guide</summary>

    <p><strong>Note:</strong> Installing PlantUML on the local machine is required to create PlantUML diagrams. Without proper installation, the PlantUML functionality will not be available.</p>

    <h3>Installation Instructions</h3>

    <h4>Linux</h4>
    <ul>
        <li><strong>Ubuntu/Debian:</strong> <code>sudo apt install plantuml</code></li>
        <li><strong>Fedora/RHEL:</strong> <code>sudo dnf install plantuml</code></li>
        <li><strong>Arch Linux:</strong> <code>sudo pacman -S plantuml</code></li>
    </ul>

    <h4>Windows</h4>
    <ul>
        <li>Using <a href="https://docs.chocolatey.org/en-us/choco/setup/">Chocolatey</a>: <code>choco install plantuml</code></li>
    </ul>

    <h4>macOS</h4>
    <ul>
        <li>Using Homebrew: <code>brew install plantuml</code></li>
    </ul>
</details>

2. Run the following SAM CLI command (`solace-agent-mesh`) to verify your installation:

```sh
solace-agent-mesh --version
```

:::tip
For easier access to the SAM CLI, it also comes with the `sam` alias.

```sh
sam --version
```
:::

To get the list of available commands, run:

```sh
solace-agent-mesh --help
```
