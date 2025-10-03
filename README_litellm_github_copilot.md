# LiteLLM GitHub Copilot Integration

This repository now supports GitHub Copilot models through LiteLLM integration, allowing you to use GitHub's AI models for document processing tasks.

## Setup

### 1. Install Dependencies

The required dependencies are already included in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Set up your GitHub token for accessing Copilot models:

```bash
export GITHUB_TOKEN="your_github_token_here"
```

You can also add this to your `.env` file:

```
GITHUB_TOKEN=your_github_token_here
```

### 3. Configuration

Update your `pageindex/config.yaml` to use GitHub Copilot models:

```yaml
# Use GitHub Copilot models via LiteLLM
model: "github_copilot/gpt-4o"
# or
model: "github_copilot/gpt-4"

# Optional: explicitly enable LiteLLM (auto-detected for github_copilot models)
use_litellm: true

# Other configuration options remain the same
toc_check_page_num: 20
max_page_num_each_node: 10
max_token_num_each_node: 20000
if_add_node_id: "yes"
if_add_node_summary: "yes"
if_add_doc_description: "no"
if_add_node_text: "no"
```

## Available Models

GitHub Copilot models available through LiteLLM:

- `github_copilot/gpt-4o` - Latest GPT-4 Omni model
- `github_copilot/gpt-4` - GPT-4 model
- `github_copilot/gpt-3.5-turbo` - GPT-3.5 Turbo model

## Usage

The integration is automatic. When you use a `github_copilot/` prefixed model, the system will:

1. Automatically detect it's a GitHub Copilot model
2. Use LiteLLM instead of the OpenAI client
3. Configure the appropriate authentication using your `GITHUB_TOKEN`

### Example Usage in Code

```python
from pageindex.utils import get_api_function, is_github_copilot_model

# Configure model
model = "github_copilot/gpt-4o"

# Get the appropriate API function
api_function = get_api_function(model)

# Use the function (automatically uses LiteLLM for GitHub Copilot models)
response = api_function(model, "Your prompt here")
print(response)

# Check if a model is a GitHub Copilot model
if is_github_copilot_model(model):
    print("Using GitHub Copilot model")
```

### Async Usage

```python
from pageindex.utils import get_api_function_async
import asyncio

async def example():
    model = "github_copilot/gpt-4o"
    api_function = get_api_function_async(model)
    response = await api_function(model, "Your prompt here")
    print(response)

# Run async function
asyncio.run(example())
```

## Benefits

1. **Cost Efficiency**: GitHub Copilot models may offer different pricing compared to direct OpenAI API calls
2. **Access Control**: Use your GitHub organization's Copilot subscription
3. **Unified Interface**: Same API interface for both OpenAI and GitHub Copilot models
4. **Automatic Detection**: No need to manually configure which client to use

## Troubleshooting

### Common Issues

1. **Missing GITHUB_TOKEN**: Ensure your GitHub token is set in environment variables
2. **litellm not installed**: Run `pip install -r requirements.txt` to install all dependencies
3. **GitHub Copilot access**: Ensure your GitHub account has Copilot access

### Error Messages

- `"GITHUB_TOKEN environment variable is required for GitHub Copilot models"`: Set the GITHUB_TOKEN environment variable
- `"litellm is not available"`: Install litellm package: `pip install litellm`

## Fallback

If LiteLLM is not available or there are issues with GitHub Copilot models, the system will fall back to using standard OpenAI models with the OpenAI client.