---
title: MCP Integration
sidebar_position: 20
---

# MCP Integration

In this tutorial, we will walk you through the process of integrating a Model Context Protocol (MCP) Server into Solace Agent Mesh.

:::info[Learn about agents and plugins]
You should have an understanding of agents and plugins in the Solace Agent Mesh. For more information, see [Agents](../concepts/agents.md) and [Using Plugins](../concepts/plugins/use-plugins.md).
:::

The Solace Agent Mesh MCP Server Plugin adds capabilities for interacting with servers that implement the Model Context Protocol (MCP). 

It provides **an Agent (`mcp_server`)** that allows SAM to act as an MCP client, connecting to external MCP servers (like `server-filesystem` or `server-everything`) and exposing their tools, resources, and prompts as SAM actions.

As an example, you are going to integrate the [MCP server-filesystem Server](https://www.npmjs.com/package/@modelcontextprotocol/server-filesystem) into the Solace Agent Mesh Framework to perform simple filesystem commands.

## Setting Up the Environment

You must [install Solace Agent Mesh and Solace Mesh Agent (SAM) CLI](../getting-started/installation.md), and then you'll want to [create a new Solace Agent Mesh project](../getting-started/quick-start.md).

This project also requires the installation of Node.js and the NPM package manager.

## Adding the MCP Server Plugin

The integration process involves two main steps:

1. **Add the Plugin**: Install the `sam-mcp-server` plugin
2. **Instantiate an Agent**: Create a specific MCP server agent instance

### Step 1: Add the Plugin

You will be using the `sam-mcp-server` plugin from the [solace-agent-mesh-core-plugins](https://github.com/SolaceLabs/solace-agent-mesh-core-plugins/tree/main/sam-mcp-server) repo for this tutorial. This plugin creates an agent that communicates with the MCP Server.

Once you have your project set up, you can add the `sam_mcp_server` plugin to the project using the following command:

```sh
solace-agent-mesh plugin add sam_mcp_server --pip -u git+https://github.com/SolaceLabs/solace-agent-mesh-core-plugins#subdirectory=sam-mcp-server
```

### Step 2: Instantiate the Agent

Use the `solace-agent-mesh add agent` command to create a configuration file for your specific MCP server instance. Replace `<new_agent_name>` with a descriptive name (e.g., `filesystem_docs`):

```sh
solace-agent-mesh add agent filesystem_docs --copy-from sam_mcp_server:mcp_server
```

This command creates a new YAML file in `configs/agents/` named `filesystem_docs.yaml`. The template variables inside the copied file will be automatically replaced with your chosen agent name.

### Step 3: Configure Environment Variables

For each MCP Server agent instance, you need to set specific environment variables. The naming convention uses the uppercase version of your agent name.

For our `filesystem_docs` agent, add these to your `.env` file:

```sh
# Required Solace connection variables (used by all agents)
SOLACE_BROKER_URL=...
SOLACE_BROKER_USERNAME=...
SOLACE_BROKER_PASSWORD=...
SOLACE_BROKER_VPN=...
SOLACE_AGENT_MESH_NAMESPACE=...

# MCP Server specific variables
FILESYSTEM_DOCS_SERVER_COMMAND="npx -y @modelcontextprotocol/server-filesystem ${HOME}/sandbox"
FILESYSTEM_DOCS_SERVER_DESCRIPTION="Provides access to filesystem"
```

The `FILESYSTEM_DOCS_SERVER_COMMAND` runs the `filesystem` MCP Server and allows it to manage files in the `${HOME}/sandbox` directory.

Next, create the sandbox directory and create a file:

```sh
mkdir ${HOME}/sandbox
touch ${HOME}/sandbox/my_file
```

### Step 4: Build and Run your project

Now, you can build and run the your solace-agent-mesh project:

```sh
sam run -b
```

For more information, see [Solace Agent Mesh CLI](../concepts/cli.md).

## Advanced Configuration

### Passing Environment Variables to MCP Servers

By default, no environment variables are passed to the MCP server process. You can explicitly specify which environment variables should be passed using two configuration options in your agent's YAML file:

1. **`environment_file`**: Path to a file containing environment variables in the standard `.env` format.
2. **`environment_variables`**: A dictionary where you can define environment variables directly.

Variables defined in `environment_variables` will override any variables with the same name loaded from the `environment_file`.

To configure these options, edit your agent's YAML file (e.g., `configs/agents/filesystem_docs.yaml`):

```yaml
shared_config:
  - mcp_server_info: &mcp_server_info
      # Other server configuration...
      
      # Optional: Load variables from a .env file
      environment_file: .env.mcp.production
      
      # Optional: Define variables directly (these override .env.production)
      environment_variables:
        MY_API_KEY: ${SECRET_API_KEY}  # Reference another env var
        ANOTHER_VAR: "some_static_value"
        DEBUG_MODE: "false"  # Overrides DEBUG_MODE if it was in .env.production
```

### Additional Configuration Options

The MCP server agent configuration supports several other options:

- **`timeout`**: Maximum time (in seconds) to wait for a response from the MCP server
- **`server_startup_timeout`**: Maximum time (in seconds) to wait for the MCP server to start
- **`enable_sampling`**: Set to true to allow the MCP server to make LLM requests back through SAM

```yaml
component_config:
  # ... other configuration
  timeout: 90
  server_startup_timeout: 30
  enable_sampling: false
```

## How It Works

The `mcp_server` agent starts the process specified by the `*_SERVER_COMMAND` environment variable. It communicates with this process using standard input/output (stdio) according to the MCP specification.

When the agent starts, it connects to the MCP server, queries its capabilities (tools, resources, prompts), and dynamically creates corresponding SAM actions:
- Tools become actions with the same name
- Resources become `get_<resource_name>` actions
- Prompts become `use_prompt_<prompt_name>` actions

This allows you to interact with various MCP-compliant tools and servers seamlessly within the Solace Agent Mesh ecosystem.

## Testing the Plugin

First, you must retrieve a list of the files from the filesystem.

```sh
curl --location 'http://localhost:5050/api/v1/request' \
--header 'Authorization: Bearer None' \
--form 'prompt="List the files on the filesystem."' \
--form 'stream="false"'
```

The response includes the file you created in a previous step as expected:

````json
{
  "created": 1739378715,
  "id": "restapi-3570a20d-d4a8-4780-946b-5e1ea3b11ee4",
  "response": {
    "content": "Here are the files in the allowed directory:\n```text\n[FILE] my_file\n```",
    "files": []
  },
  "session_id": "3dbd8425-2962-45e1-be2a-ec7f2cd4a09c"
}
````

Next, create a simple JSON file.

```sh
curl --location 'http://localhost:5050/api/v1/request' \
--header 'Authorization: Bearer None' \
--form 'prompt="Create a json file with two mock employees in the allowed directory of the filesystem."' \
--form 'stream="false"'
```

You will get the following response indicating the requested file was created:

```json
{
  "created": 1739379547,
  "id": "restapi-864e38b0-ebb6-4dcd-85ec-1e325dcbfb00",
  "response": {
    "content": "OK. I have created a json file with two mock employees in the allowed directory of the filesystem. The file is located at `/Users/myuserid/sandbox/employees.json`.",
    "files": []
  },
  "session_id": "e6580943-9a55-4787-a9ca-2bb839725933"
}
```

To verify that the file exists, run the following command:

```sh
cat ${HOME}/sandbox/employees.json
```

You should see the data for the two mock employees in the JSON file:

```json
[
  {
    "firstName": "John",
    "lastName": "Doe",
    "employeeId": 1
  },
  {
    "firstName": "Jane",
    "lastName": "Smith",
    "employeeId": 2
  }
]
```
