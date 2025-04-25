---
title: Amazon Bedrock Agents
sidebar_position: 30
toc_max_heading_level: 4
---

# Amazon Bedrock Agents Integration

In this tutorial, we will walk you through the process of integrating Amazon Bedrock Agents and Flows into Solace Agent Mesh (SAM). This integration allows you to create agents that can interact with one or multiple Bedrock Agents or Flows, extending your SAM project with powerful AI capabilities from AWS.

## What are Amazon Bedrock Agents and Flows?

Amazon Bedrock Agents are AI assistants that can be customized to perform specific tasks using foundation models (FMs). They can connect to enterprise systems and data sources, allowing them to take actions on behalf of users.

Amazon Bedrock Flows are visual workflows that orchestrate multiple foundation models to solve complex problems. They allow you to chain together different AI capabilities without writing code.

By integrating these services with SAM, you can:
- Use SAM's extensible framework to combine Bedrock agents and flows with other plugins
- Create conversational interfaces that leverage Bedrock agents and flows
- Connect your SAM agents to enterprise data sources through Bedrock
- Maintain a consistent experience across different agent providers by centralizing them in SAM

:::info[Learn about Bedrock Agents and Flows]
Check the official documentation for [Amazon Bedrock Agents](https://aws.amazon.com/bedrock/agents/) and [Amazon Bedrock Flows](https://aws.amazon.com/bedrock/flows/) to learn more about these features.
:::


## Setting Up the Environment

### Create Bedrock Agents and Flows

Follow these steps to create your Bedrock resources:

1. **Log in to your AWS console**
   - Navigate to the Amazon Bedrock service

2. **Create Bedrock Agents**
   - Go to the **Agents** tab in the Bedrock console
   - Click "Create agent"
   - Follow the wizard to configure your agent:
     - Select a foundation model
     - Define the agent's instructions
     - Configure knowledge bases (optional)
     - Set up action groups (if needed)
   - Once created, **create an alias** for your agent by selecting it and clicking "Create alias"
   - **Copy the Agent ID and Alias ID** from the agent details page - you'll need these for the SAM configuration

3. **Create Bedrock Flows**
   - Go to the **Flows** tab in the Bedrock console
   - Click "Create flow"
   - Use the visual editor to design your flow
   - Connect nodes to create your workflow
   - Test and publish your flow
   - **Create an alias** for your flow
   - **Copy the Flow ID and Alias ID** - you'll need these for the SAM configuration

4. **Set up IAM permissions**
   - Ensure your IAM user or role has the following permissions:
     - `bedrock:InvokeAgent`
     - `bedrock:InvokeFlow`
     - Any other permissions required by your specific Bedrock configuration

### Create a SAM Project

You must [install Solace Agent Mesh and Solace Mesh Agent (SAM) CLI](../getting-started/installation.md), and then you'll want to [create a new Solace Agent Mesh project](../getting-started/quick-start.md).


## Integrating Bedrock with SAM

### Adding the `sam-bedrock-agent` Plugin

The `sam-bedrock-agent` plugin from the [solace-agent-mesh-core-plugins](https://github.com/SolaceLabs/solace-agent-mesh-core-plugins/tree/main/sam-bedrock-agent) repository creates a bridge between SAM and Amazon Bedrock services. This plugin allows your SAM agents to invoke Bedrock Agents and Flows as actions.

1. **Add the plugin to your SAM project**:

```sh
solace-agent-mesh plugin add sam-bedrock-agent --pip -u git+https://github.com/SolaceLabs/solace-agent-mesh-core-plugins#subdirectory=sam-bedrock-agent
```

This command downloads and installs the plugin into your SAM project using the `pip` package manager. (Optionally, you can use `--poetry`, `--conda`, or `--uv` to specify the package manager.)

:::warning[Requires Git]
Make sure you have Git installed on your system, as the command uses Git to fetch the plugin from GitHub.
:::

### Creating a Bedrock Agent Configuration

After adding the plugin, you need to create a configuration file for your specific Bedrock agent instance:

1. **Create the agent configuration**:

```sh
solace-agent-mesh add agent <new_agent_name> --copy-from sam_bedrock_agent:bedrock_agent
```

Replace `<new_agent_name>` with a descriptive name for your agent, such as `bedrock_summarizer` or `bedrock_customer_service`.

2. **Locate the configuration file**:

This command creates a `<new_agent_name>.yaml` file in the `configs/agents/` directory of your SAM project.

:::tip[Naming Convention]
Choose a descriptive name that reflects the purpose of your Bedrock integration. This name will be used to reference the agent in your SAM project.
:::

## Configuring the Bedrock Agent

The configuration file you created needs to be edited to connect to your specific Amazon Bedrock resources. This section explains each part of the configuration and how to customize it.

### Understanding the Configuration Structure

Open the `<new_agent_name>.yaml` file in your editor. The core of the agent's configuration consists of three main sections:

1. **amazon_bedrock_runtime_config**: AWS connection settings
2. **bedrock_agents**: List of Bedrock agents to expose as actions
3. **bedrock_flows**: List of Bedrock flows to expose as actions

### Example Configuration

Here's an annotated example of the configuration file:

```yaml
# ... other config ...
flows:
  - name: {{SNAKE_CASE_NAME}}_action_request_processor
    components:
      # ... broker_input section (handles incoming messages) ...
      - component_name: action_request_processor
        component_module: {{MODULE_DIRECTORY}}.agents.bedrock_agent.bedrock_agent_agent_component
        component_config:
          agent_name: {{SNAKE_CASE_NAME}} # Your agent name as seen by SAM
          # ... other component settings ...
          
          # AWS Connection Configuration
          amazon_bedrock_runtime_config:
            # Optional: Custom AWS endpoint URL (usually not needed)
            endpoint_url:
            
            # AWS credentials and region configuration
            boto3_config:
              # The AWS region where your Bedrock resources are located
              region_name: "us-east-1"
              
              # AWS credentials (alternatively, use AWS profiles)
              aws_access_key_id:
              aws_secret_access_key:
              # aws_session_token: # If using temporary credentials

          # Bedrock Agents Configuration
          bedrock_agents:
            - name: summarize_text # The name of this action in SAM
              description: "Summarize text using Bedrock agent" # User-friendly description
              param_description: "Text to summarize" # Description of the input parameter
              bedrock_agent_id: "abcdef123456" # Your actual Bedrock agent ID
              bedrock_agent_alias_id: "xyz789" # Your actual Bedrock agent alias ID
              allow_files: true # Enable file uploads to the agent

              # --- Add more agents ---

          # Bedrock Flows Configuration
          bedrock_flows:
            - name: analyze_sentiment # The name of this action in SAM
              description: "Analyze sentiment using Bedrock flow" # User-friendly description
              param_description: "Text to analyze" # Description of the input parameter
              bedrock_flow_id: "flow123456" # Your actual Bedrock flow ID
              bedrock_flow_alias_id: "flowalias789" # Your actual Bedrock flow alias ID

              # -- Add more flows --
              
      # ... broker_request_response, broker_output sections ...
```

### Customizing Your Configuration

Follow these steps to customize your configuration:

1. **Configure AWS Connection**:
   - Set the `region_name` to the AWS region where your Bedrock resources are located
   - Choose one of these authentication methods:
     - Set `aws_access_key_id` and `aws_secret_access_key` directly in the config
     - Use AWS profiles by removing these fields and configuring your AWS CLI profile
     - Use environment variables (see Environment Variables section below)

Check the [boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/session.html) for more details.

2. **Configure Bedrock Agents**:
   - For each Bedrock agent you want to expose:
     - Set a descriptive `name` for the action (e.g., `answer_questions`, `generate_content`)
     - Provide a clear `description` of what the agent does
     - Set `param_description` to explain what input the user should provide
     - Replace `bedrock_agent_id` with your actual Bedrock agent ID
     - Replace `bedrock_agent_alias_id` with your actual Bedrock agent alias ID
     - Set `allow_files` to `true` if your agent can process file uploads

3. **Configure Bedrock Flows**:
   - For each Bedrock flow you want to expose:
     - Set a descriptive `name` for the action
     - Provide a clear `description` of what the flow does
     - Set `param_description` to explain what input the user should provide
     - Replace `bedrock_flow_id` with your actual Bedrock flow ID
     - Replace `bedrock_flow_alias_id` with your actual Bedrock flow alias ID

:::info
You must provide at least one Bedrock agent or flow configuration. If you're only using agents, you can remove the `bedrock_flows` section, and vice versa.
:::

### Environment Variables

The Bedrock agent integration requires standard Solace connection variables and can use AWS environment variables for authentication.

#### Required Solace Variables:
- **SOLACE_BROKER_URL**: URL of your Solace broker
- **SOLACE_BROKER_USERNAME**: Username for Solace broker authentication
- **SOLACE_BROKER_PASSWORD**: Password for Solace broker authentication
- **SOLACE_BROKER_VPN**: Solace message VPN name
- **SOLACE_AGENT_MESH_NAMESPACE**: Namespace for your SAM project

#### Optional AWS Variables:
If you prefer to use environment variables for AWS authentication instead of configuration in the YAML file:
- **AWS_ACCESS_KEY_ID**: Your AWS access key
- **AWS_SECRET_ACCESS_KEY**: Your AWS secret key
- **AWS_SESSION_TOKEN**: If using temporary credentials
- **AWS_REGION** or **AWS_DEFAULT_REGION**: AWS region for Bedrock services

:::tip[AWS Credentials Precedence]
AWS credentials are loaded in this order:
1. Explicit credentials in the YAML configuration
2. Environment variables
3. AWS configuration files (~/.aws/credentials)
4. EC2/ECS instance profiles (if running on AWS)
:::

## Running and Testing Your Integration

### Starting Your SAM Project

After configuring your Bedrock agent integration, build and run your SAM project:

```sh
sam run -b
```

The `-b` flag rebuilds the project before running it, ensuring that your configuration changes are applied.

### Testing the Integration

There are several ways to test your Bedrock agent integration, the simplest way to test is through the SAM web UI:

1. Open your browser and navigate to the SAM web interface (typically at http://localhost:5001)
2. Start a conversation with your agent
3. Ask a question that would trigger your Bedrock agent or flow

**Example**: If you configured a Bedrock agent for text summarization:
```
Summarize the following text: "The quick brown fox jumps over the lazy dog. The lazy dog did not chase the fox. The fox was brown and quick, while the dog was lazy and slow. Despite their differences, they both enjoyed the sunny day in the meadow."
```

#### Testing with File Uploads

If you've enabled file uploads for your Bedrock agent (`allow_files: true`), you can test file processing:

1. In the SAM web UI, use the file upload button to attach a supported file
2. Include a prompt that references the file, such as "Summarize this document"
3. The file will be sent to the Bedrock agent along with your prompt

:::info[Supported File Types]
Bedrock agents support these file types for uploads:
- PDF documents (.pdf)
- Text files (.txt)
- Word documents (.doc)
- CSV files (.csv)
- Excel spreadsheets (.xls, .xlsx)

There's a limit of 5 files with a total size of 10MB.
:::

## Troubleshooting

### Common Issues and Solutions

#### Authentication Errors

**Issue**: "Unable to locate credentials" or "Access denied" errors
**Solution**:
- Verify your AWS credentials are correctly configured
- Check that your IAM user/role has the necessary permissions
- Try using AWS CLI to test your credentials: `aws bedrock list-foundation-models`

#### Configuration Errors

**Issue**: "Invalid agent ID" or "Invalid flow ID" errors
**Solution**:
- Double-check your Bedrock agent and flow IDs in the configuration
- Ensure you've created aliases for your agents and flows
- Verify the region in your configuration matches where your Bedrock resources are located

#### Connection Issues

**Issue**: SAM can't connect to Bedrock services
**Solution**:
- Check your network connectivity
- Verify that Bedrock services are available in your configured region
- Check for any VPC or firewall restrictions

#### File Upload Issues

**Issue**: Files aren't being processed by the Bedrock agent
**Solution**:
- Verify `allow_files` is set to `true` in your configuration
- Check that your file type is supported
- Ensure the file size is under the 10MB limit
- Check the model context length

## Conclusion

You've now successfully integrated Amazon Bedrock Agents and Flows with your Solace Agent Mesh project. This integration allows you to leverage AWS's powerful AI services while maintaining the flexibility and extensibility of the SAM framework.

### Next Steps

After completing this integration, you might want to:

1. **Explore advanced configurations** - Customize your Bedrock agent integration with more complex configurations
2. **Combine with other SAM plugins** - Integrate your Bedrock agent with other SAM plugins for more comprehensive solutions
3. **Create specialized agents** - Build multiple Bedrock agent integrations with different specializations

For more information on other SAM integrations, check out the other tutorials in this documentation section.
