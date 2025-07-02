<div align="center">
  <img src="https://i.postimg.cc/XYrHyJKL/ebiose.png"/>
  <h4> Autonomous AI Agents that Self-Evolve </h4>
  <h3>

[![Website](https://img.shields.io/website?url=https%3A%2F%2Febiose.com&style=for-the-badge&logo=curl&label=ebiose.com)](https://ebiose.com)

[![Discord](https://img.shields.io/badge/Discord-Join%20Us-7289DA?style=for-the-badge&logo=discord)](https://discord.gg/P5pEuG5a4V)

[![GitHub Repo stars](https://img.shields.io/github/stars/ebiose-ai/ebiose?style=for-the-badge&logo=github&logoColor=EFBF04&color=EFBF04)](https://star-history.com/#ebiose-ai/ebiose)
[![License](https://img.shields.io/github/license/ebiose-ai/ebiose?style=for-the-badge&logo=gitbook&link=https%3A%2F%2Fgithub.com%2Febiose-ai%2Febiose%2Fblob%2Fmain%2FLICENSE)](/LICENSE)

[![HackerNews](https://img.shields.io/badge/Live_on_Hacker_News-%E2%9A%A1-orange?logo=ycombinator&style=for-the-badge)]([/LICENSE](https://news.ycombinator.com/shownew))



<i>Copyright © 2025 Inria</i></h4>

  </h3>
</div>

Ebiose is a **distributed artificial intelligence factory**, an open source project from the Inria’s incubator (French lab). Our vision: enabling humans and agents to collaborate in building tomorrow's AI in an open and democratic way.

> "AI is set to reshape our world, but who gets to decide its form and for whose benefit? Instead of a future dictated by a few tech giants, what if we could build AI collectively and openly?"

<div align="center">

### ⏰ _July 2, 2025_ – **Ebiose** just hit **“Show HN”** 🚀 

We just posted **Ebiose** in the “Show HN” section.  
If you believe in an open and democratic AI, your support there is critical:

👉 Open the “Show HN” feed → <a href="https://news.ycombinator.com/shownew">[news.ycombinator.com/shownew](https://news.ycombinator.com/shownew)</a>  
👉 Find the post **“Show HN: Ebiose – A Darwin‑Style Playground for Self‑Evolving AI Agents”**  
👉 Smash the ▲ up‑vote and drop a comment or question  

*Thank you for helping us kick‑start the community!*

</div>


**👀 Must read 👀**

- [Founding blog post](https://ebiose.com/blog/ai-for-all-and-by-all) *(10 min)*
- [Glossary](GLOSSARY.md) *(3 min)*

## 🧪 Current status: Beta 0.1

This first beta version implements the foundations of our vision.

### ✅ What's included

- **Architect agents**: Specialized AIs for designing and evolving other agents
- **Darwinian engine**: Evolutionary system enabling continuous improvement of agents through mutation and selection
- **Forges**: Isolated environments where architect agents create custom agents to solve specific problems
- **LangGraph Compatibility**: Integration with the LangGraph ecosystem for agent orchestration

With the latest release (June 2025):
- **A shared centralized ecosystem**: Use Ebiose’s cloud to kickstart a forge cycle with curated agents from our shared ecosystem.
The top-performing agents are automatically promoted and reintegrated, making the ecosystem stronger with every cycle. 👉 [\[Access the Ebiose cloud now.\]](https://app.ebiose.com/login)
- **LiteLLM support**: Ebiose now integrates with [LiteLLM](https://www.litellm.ai/) to simplify the 
management of your own LLMs.


### 🚨 Points of caution

- **Proof of concept**: Don't expect complex or production-ready agents
- **Initial architect agent to be improved**: The first implemented architect agent is still simple
- **Early stage**: Be prepared to work through initial issues and contribute to improvements! 😇


# 🚀 Quick start

## 🔧 Installation

First, clone the repository:

```bash
git clone git@github.com:ebiose-ai/ebiose.git && cd ebiose
```

## ⚙️ Initialization

Initialize the project by running the following command:

```bash
make init
```

This command will perform the following actions:

- Copy the `model_endpoints_template.yml` file to `model_endpoints.yml` if the file doesn't exist, and instruct you to fill it with your API keys.
- Copy the `.env.example` file to `.env` if the file doesn't exist.

## 🔥 Run your first Ebiose forge cycle

There are two ways to start running Ebiose:

- ~~the most straightforward way is to use Docker: go to section
[🐳 With Docker](#-with-docker);~~ 🚧 Docker support for the new release is currently untested. See [Issue #26](https://github.com/ebiose-ai/ebiose/issues/26) for details.

- if you are not yet confortable with Ebiose and wish to understand
the basics of Ebiose step by step, you may also install the project dependencies
and go through the [`quickstart.ipynb`](notebooks/quickstart.ipynb) Jupyter notebook to understand the basics of Ebiose, step by step; follow the steps to install Ebiose [💻 Locally](#-locally).

<!-- ### 🐳 With Docker

> 🚨 Docker support for the new release is currently untested. See [Issue #26](https://github.com/ebiose-ai/ebiose/issues/26) for details.

To build and run Ebiose using Docker, follow these steps:

1. Ensure you have Docker installed on your system.
2. If running Linux, ensure you have followed the post installation steps: <https://docs.docker.com/engine/install/linux-postinstall/>
3. Build the Docker image using the following command:

    ```bash
    make build
    ```

4. Ensure you have created and filled in the `model_endpoints.yml` file with your OpenAI API key. A basic `model_endpoints.yml` file looks like this:

    ```yaml
    default_endpoint_id: "gpt-4o-mini"
    endpoints:
    - endpoint_id: "gpt-4o-mini"
      provider: "OpenAI"
      api_key: "YOUR_OPENAI_API_KEY" 
    ```

5. Run the Docker image using the following command, which mounts the `model_endpoints.yml` file and passes environment variables from `.env`:

    ```bash
    make run
    ```

    This command mounts the `model_endpoints.yml` file from your local directory into the container, allowing the application to access your API key without including it in the image. It also passes environment variables defined in the `.env` file to the container. -->

### 💻 Locally

#### 📦 Install Project Dependencies

Ebiose uses [uv](https://docs.astral.sh/uv/) as a packaging and dependency manager. See [Astral's uv documentation](https://docs.astral.sh/uv/getting-started/installation/) to install it.  

Once uv is installed, use it to install your project dependencies. In your project directory, run:

To install all required dependencies

```sh
uv sync
```

By default, Ebiose supports OpenAI models but other major providers can also be used. Refer to [🤖 Model APIs support](#-model-apis-support)

For more detailed instructions or troubleshooting tips, refer to the [official uv documentation](https://docs.astral.sh/uv/).

> 💡 If you don't want to use `uv`, you can still use `pip install -r requirements.txt` command.

> 💡 Pro Tip: You may need to add the root of the repository to your `PYTHONPATH` environment variable. Alternatively, use a `.env` file to do so.

#### 🔍 Understand forges and forge cycles

The Jupyter notebook [`quickstart.ipynb`](notebooks/quickstart.ipynb) is the easiest way to understand the basics and start experimenting with Ebiose. This notebook lets you try out **architect agents** and **forges** on your very own challenges. 🤓

#### 🛠️ Implement your own forge

To go further, the `examples/` directory features a complete forge example designed to optimize agents that solve math problems. Check out [`examples/math_forge/math_forge.py`](math_forge/math_forge.py) for the implementation of the `MathLangGraphForge` forge.

For demonstration purposes, the `run.py` script is configured to manage a forge cycle with only two agents per generation, using a tiny budget of $0.02. The cycle should take 1 to 2 minutes to consume the budget using the default model endpoint `gpt-4o-mini`. Each generated agent will be 
evaluated on 5 math problems from GSM-8k test dataset.

To run a cycle of the Math forge, execute the following command in your project directory:

```sh
uv run ./examples/math_forge/run.py
```

<!-- Once agents are written to the save path, evaluate an agent by executing:

```sh
uv run ./examples/math_forge/evaluate.py
```

> 🚨 The command `uv run ./examples/math_forge/evaluate.py` won't work if using Ebiose's cloud. See [Issue #27](https://github.com/ebiose-ai/ebiose/issues/27) for details.

> 🚨 You must change the path to the agent's JSON file by modifying the following variable:

```
AGENT_JSON_FILE = Path("data/2025-02-28_17-49-05/generation=2/agents/agent-211c7fe5-d329-470e-bdd9-ae7ee6ce0be3.json")
```

> 🚨 Also, if needed, change the following variables:

```
N_PROBLEMS = 2 # number of problems to evaluate on
BUDGET = 0.1 # budget for evaluation in dollars
``` -->

Kick off your journey by implementing your own forge with the accompanying `compute_fitness` method! 🎉

# 🤖 Model APIs support

As of today, Ebiose uses LangChain/LangGraph to implement agents. Using the different providers of LLMs, and ML models, has been made as easy as possible. 

Since June 2025, Ebiose has been integrated with LiteLLM and now offers its own cloud — making model management even easier.

## Ebiose Cloud

The fastest and easiest way to run your forge in just a few steps with 
$10 free credits. 

### 1. Create your account  
Sign up at [Ebiose Cloud](https://app.ebiose.com/login).

### 2. Add your API key  
Generate your Ebiose API key and add it to your `model_endpoints.yml` file:

```yaml
ebiose:
  api_key: "your-ebiose-api-key"  # Replace with your Ebiose API key
  api_base: "https://cloud.ebiose.com/"
```
### 3. Set your default model  
Specify the model to use by default:
```YAML
default_endpoint_id: "azure/gpt-4o-mini"
```

> 🚧 As of June 2025, the Ebiose web app only allows you to create an API key with $10 in free credits to experiment with running your own forges. More features coming soon.


> 🚨 To run a forge cycle with Ebiose cloud, be sure to set it up
using the dedicated [`CloudForgeCycleConfig` class](ebiose/core/forge_cycle.py#L87).

### ✅ Supported models

Ebiose Cloud currently supports the following models:

- `azure/gpt-4o-mini`
- `azure/gpt-4.1-mini`
- `azure/gpt-4.1-nano`
- `azure/gpt-4o`

More models to come. Feel free to ask.

## Using LiteLLM

Ebiose integrates with [LiteLLM](https://www.litellm.ai/), either through the cloud or a self-hosted proxy.  
Refer to the [LiteLLM documentation](https://docs.litellm.ai/docs/) to get started and generate your LiteLLM API key.

Once you have your key, update the `model_endpoints.yml` file as follows:

```yaml
lite_llm:
  use: true                 # Set to true to enable LiteLLM
  use_proxy: false          # Set to true if using a self-hosted LiteLLM proxy
  api_key: "your-litellm-api-key"         # Replace with your LiteLLM API key
  api_base: "your-litellm-proxy-url"      # Optional: your LiteLLM proxy URL
```

Finally, define your LiteLLM endpoints using the appropriate model naming format:
```YAML
endpoints:
  - endpoint_id: "azure/gpt-4o-mini"
    provider: "Azure OpenAI"
```

> 🚨 To run a forge cycle without Ebiose cloud, be sure to set it up using the dedicated [`LocalForgeCycleConfig` class](ebiose/core/forge_cycle.py#L01).

> 🚨 The "local" mode for running forge cycles has not been fully tested. Use with caution and report any issues. See [Issue #29](https://github.com/ebiose-ai/ebiose/issues/29) for details.

## Using Your Own Access to LLM Providers
You may also use your own credentials **without going through LiteLLM**.  
To do so, define the model endpoints you want to use in the `model_endpoints.yml` file located at the root of the project.

Fill in your secret credentials using the examples below.

For other providers not listed here, refer to [LangChain's documentation](https://python.langchain.com/docs/integrations/providers/)  
and adapt the [`LangGraphLLMApi` class](ebiose/backends/langgraph/llm_api.py) as needed.  
Issues and pull requests are welcome!

> 🚨 To run a forge cycle without Ebiose cloud, be sure to set it up using the dedicated [`LocalForgeCycleConfig` class](ebiose/core/forge_cycle.py#L01).

> 🚨 The "local" mode for running forge cycles has not been fully tested. Use with caution and report any issues. See [Issue #29](https://github.com/ebiose-ai/ebiose/issues/29) for details.

### OpenAI

To use OpenAI LLMs, fill the `model_endpoints.yml` file at the root of the project,
with, for example:

```yaml
default_endpoint_id: "gpt-4o-mini"
endpoints:
  - endpoint_id: "gpt-4o-mini"
    provider: "OpenAI"
    api_key: "YOUR_OPENAI_API_KEY"
```

### Azure OpenAI

To use OpenAI LLMs on Azure, fill the `model_endpoints.yml` file at the root of the project, with, for example:

```yaml
endpoints:
  - endpoint_id: "azure/gpt-4o-mini"
    provider: "Azure OpenAI"
    api_key: "YOUR_AZURE_OPENAI_API_KEY"
    endpoint_url: "AZURE_OPENAI_ENDPOINT_URL"
    api_version: "API_VERSION"
    deployment_name: "DEPLOYMENT_NAME"
```

### Azure ML LLMs

To use other LLMs hosted on Azure fill the `model_endpoints.yml` file at the root
of the project, with, for example:

```yaml
endpoints:
  - endpoint_id: "llama3-8b"
    provider: "Azure ML"
    api_key: "YOUR_AZURE_ML_API_KEY"
    endpoint_url: "AZURE_ENDPOINT_URL"
```

### Anthropic (not tested yet)

To use Anthropic LLMs, fill the `model_endpoints.yml` file at the root of the project,
with, for example:

```yaml
endpoints:
  - endpoint_id: "claude-3-sonnet-20240229"
    provider: "Anthropic"
    api_key: "YOUR_OPENAI_API_KEY"
```

> 🚨 Dont'forget to install Langchain's Anthropic library by executing
`uv sync --extra anthropic` or `pip install -U langchain-anthropic`

### HuggingFace (not tested yet)

To use HuggingFace LLMs, fill the `model_endpoints.yml` file at the root of the project, with, for example:

```yaml
endpoints:
  - endpoint_id: "microsoft/Phi-3-mini-4k-instruct"
    provider: "Hugging Face"
```

> 🚨 Dont'forget to install Langchain's Hugging Face library by executing
`uv sync --extra huggingface` or `pip install -U langchain-huggingface`
and login with the following:

```
from huggingface_hub import login
login()
```

### OpenRouter

To use OpenRouter LLMs, fill the `model_endpoints.yml` file at the root of the project, with, for example:

```yaml
endpoints:
  - endpoint_id: "openrouter/quasar-alpha"
    provider: "OpenRouter"
    api_key: "YOUR_OPENROUTER_API_KEY"  # Fill in your OpenRouter API key
    endpoint_url: "https://openrouter.ai/api/v1"  # OpenRouter API endpoint URL
```

It needs openai library which is installed by default.

### Google (not tested yet)

To use Google LLMs, fill the `model_endpoints.yml` file at the root of the project, with, for example:

```yaml
endpoints:
  - endpoint_id: "gemini-2.5-pro-exp-03-25"
    provider: "Google"
    api_key: "YOUR_GOOGLE_API_KEY"  # Fill in your Google API key
```

> 🚨 Don't forget to install Langchain's Google GenAI library by executing
`uv sync --extra google` or `pip install langchain-google-genai`.

### Ollama (not tested yet)

To use Ollama LLMs, fill the `model_endpoints.yml` file at the root of the project, with, for example:

```yaml
endpoints:
  - endpoint_id: "ModelName"  # Replace with the actual model name, e.g., "llama3-8b"
    provider: "Ollama"
    endpoint_url: "http://<Ollama host IP>:11434/v1"
```

> 🚨 Don't forget to install Langchain's Ollama library by executing
`uv sync --extra ollama` or `pip install langchain-ollama`

### Others

Again, we wish to be compatible with every provider you are used to, so feel free to open an issue and contribute to expanding our LLMs' coverage. Check first if LangChain
is compatible with your preferred provider [here](https://python.langchain.com/docs/integrations/providers/).

# 🔍 Observability

> 🚨 **Langfuse Version Warning**: Ebiose currently uses Langfuse version 2.x.x. Updating to Langfuse 3.x.x is planned but not yet implemented due to compatibility issues. See [Issue #28](https://github.com/ebiose-ai/ebiose/issues/28) for details.

Ebiose uses Langfuse's `@observe` decorator to be able to observe nested agent's traces.
LangFuse can be easily self-hosted.
See [Langfuse's documentation](https://langfuse.com/self-hosting) to do so.
Once Langfuse's server is running, you can set Langfuse credentials in your
`.env` file by adding:

```
# Langfuse credentials
LANGFUSE_SECRET_KEY="your_langfuse_secret_key"
LANGFUSE_PUBLIC_KEY="your_langfuse_public_key"
LANGFUSE_HOST="your_langfuse_host"
```

# 📝 Logging

Ebiose uses [Loguru](https://loguru.readthedocs.io/en/stable/) for logging purpose.
You have nothing to do to set it up but can adapt logs to your needs easily.

# 🆘 Troubleshooting

Here are some common issues users might face and their solutions:

### Issue 1: uv Command Not Found

Solution: Ensure `uv` is installed correctly. Follow the
[official installation guide](https://docs.astral.sh/uv/getting-started/installation/). Alternatively, use `pip`:

```bash
pip install -r requirements.txt
```

### Issue 2: Python Environment Conflicts

Solution: Use a virtual environment to isolate dependencies:

```bash
python -m venv ebiose-env
source ebiose-env/bin/activate  # On Windows: ebiose-env\Scripts\activate
uv sync  # or pip install -r requirements.txt
```

### Issue 3: Missing API Keys

Solution: Ensure your API keys are set in the `model_endpoints.yml` file, for example:

```yaml
endpoints:

  # OpenAI endpoints
  - endpoint_id: "gpt-4o-mini"
    provider: "OpenAI"
    api_key: "YOUR_OPENAI_API_KEY" # fill in your OpenAI API key
    
```

### Issue 4: Jupyter Notebook Not Running

Solution: Ensure Jupyter is installed and the kernel is set correctly:

```bash
pip install notebook
jupyter notebook
```

### Issue 5: ModuleNotFoundError

Solution: Set the `.env` PYTHONPATH variable as shown in the `.env.example` file. Alternatively, add the project root to your PYTHONPATH:

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

# 📜 Code of Conduct

We are committed to fostering a welcoming and inclusive community. Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before participating.

# 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

- **Report Bugs**: Open an issue on GitHub with detailed steps to reproduce the problem.
- **Suggest Features**: Share your ideas for new features or improvements.
- **Submit Pull Requests**: Fork the repository, make your changes, and submit a PR. Please follow our [contribution guidelines](CONTRIBUTING.md).

For more details, check out our [Contribution Guide](CONTRIBUTING.md).

# 📜 License

Ebiose is licensed under the [MIT License](LICENSE). This means you're free to use, modify, and distribute the code, as long as you include the original license.

## ❓ Questions?

If you have any questions or need help, feel free to:

- Open an issue on GitHub.
- Join our [Discord server](https://discord.gg/P5pEuG5a4V).
- Reach out to the maintainers directly.

**All feedback is highly appreciated. Thanks! 🎊**
