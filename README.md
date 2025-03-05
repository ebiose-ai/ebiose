<div align="center">
  <img src="https://i.postimg.cc/XYrHyJKL/ebiose.png"/>
  <h4> Autonomous AI Agents that Self-Evolve </h4>
  <h3>

[![Website](https://img.shields.io/website?url=https%3A%2F%2Febiose.com&style=for-the-badge&logo=curl&label=ebiose.com)](https://ebiose.com)

[![Discord](https://img.shields.io/badge/Discord-Join%20Us-7289DA?style=for-the-badge&logo=discord)](https://discord.gg/P5pEuG5a4V) 

[![GitHub Repo stars](https://img.shields.io/github/stars/ebiose-ai/ebiose?style=for-the-badge&logo=github&logoColor=EFBF04&color=EFBF04)](https://star-history.com/#ebiose-ai/ebiose)
[![License](https://img.shields.io/github/license/ebiose-ai/ebiose?style=for-the-badge&logo=gitbook&link=https%3A%2F%2Fgithub.com%2Febiose-ai%2Febiose%2Fblob%2Fmain%2FLICENSE)](/LICENSE)


  </h3>
</div>

Ebiose is a **distributed artificial intelligence factory**, an open source project from the Inria’s incubator (French lab). Our vision: enabling humans and agents to collaborate in building tomorrow's AI in an open and democratic way.

> "AI can just as easily become the weapon of a surveillance capitalism dystopia as the foundation of a democratic renaissance."
 

👀**Must read**
- [Founding blog post](https://bit.ly/ebiose-blog-post) *(10 min)*
- [Glossary](GLOSSARY.md) *(3 min)*
## 🧪 Current status: Beta 0.1

This first beta version implements the foundations of our vision.

### ✅ What's included

- **Architect agents**: Specialized AIs for designing and evolving other agents
- **Darwinian engine**: Evolutionary system enabling continuous improvement of agents through mutation and selection
- **Forges**: Isolated environments where architect agents create custom agents to solve specific problems
- **LangGraph Compatibility**: Integration with the LangGraph ecosystem for agent orchestration

### 🚨 Points of caution

- **Proof of concept**: Don't expect complex or production-ready agents
- **Initial architect agent to be improved**: The first implemented architect agent is still simple
- **Empty ecosystems**: For now, your forges start with unpopulated ecosystems
- **Early stage**: Be prepared to work through initial issues and contribute to improvements! 😇

# 🚀 Quick start

## 🔧 Installation

First, clone the repository:

```bash
git clone git@github.com:ebiose-ai/ebiose-core.git && cd ebiose-core
```

## 📦 Install Project Dependencies 
Ebiose uses [uv](https://docs.astral.sh/uv/) as a packaging and dependency manager. See [Astral's uv documentation](https://docs.astral.sh/uv/getting-started/installation/) to install it.  

Once uv is installed, use it to install your project dependencies. In your project directory, run:

```sh
uv sync
```

For more detailed instructions or troubleshooting tips, refer to the [official uv documentation](https://docs.astral.sh/uv/).

> 💡 If you don't want to use `uv`, you can still use `pip install -r requirements.txt` command.

> 💡 Pro Tip: You may need to add the root of the repository to your `PYTHONPATH` environment variable. Alternatively, use a `.env` file to do so.

## 🔍 Understand forges and forge cycles

The Jupyter notebook [quickstart.ipynb](notebooks/quickstart.ipynb) is the easiest way to understand the basics and start experimenting with Ebiose. This notebook lets you try out **architect agents** and **forges** on your very own challenges. 🤓

## 🛠️ Implement your own forge

To go further, the `examples/` directory features a complete forge example designed to optimize agents that solve math problems. Check out [`examples/math_forge/math_forge.py`](math_forge/math_forge.py) for the implementation of the `MathLangGraphForge` forge.

To run a cycle of the Math forge, execute the following command in your project directory:

```sh
uv run ./examples/math_forge/run.py
```

Once agents are written to the save path, evaluate an agent by executing:

```sh
uv run ./examples/math_forge/evaluate.py
```
> 🚨 You must change the path to the agent's JSON file by modifying the following variable:
```
AGENT_JSON_FILE = Path("data/2025-02-28_17-49-05/generation=2/agents/agent-211c7fe5-d329-470e-bdd9-ae7ee6ce0be3.json")
```
> 🚨 Also, if needed, change the following variables:
```
N_PROBLEMS = 2 # number of problems to evaluate on
BUDGET = 0.1 # budget for evaluation in dollars
```

Kick off your journey by implementing your own forge with the accompanying `compute_fitness` method! 🎉

# 🤖 Model APIs support

As of today, Ebiose uses LangChain/LangGraph to implement agents. Using the different providers of LLMs, and ML models, has been made as easy as possible. 

## Model endpoints
Models, for now LLMs, and in the future any other ML models, must be defined as 
[`ModelEndpoint`](ebiose/core/model_endpoint.py) instances. The most straightforward
way to define the model endpoints to which you have access to is to create a 
`model_endpoints.yml` file by copy-paste-renaming the [`model_endpoints_template.yml]`(model_endpoints_template.yml)
YAML file at the root of the project, and fill it with your secret credentials.

## Main model endpoints
We have implemented the most popular LLM APIs. For others, please refer to [LangChain's documentation](https://python.langchain.com/docs/integrations/providers/) and adapt 
the [`LangGraphComputeIntensiveBatchProcessor` class](ebiose/backends/langgraph/compute_intensive_batch_processor.py) accordingly. Issues and pull requests are 
welcomed.

### OpenAI
To use OpenAI LLMs, fill the `model_endpoints.yml` file at the root of the project, 
with, for example:
```
endpoints:
  - endpoint_id: "gpt-4o-mini"
    provider: "OpenAI"
    api_key: "YOUR_OPENAI_API_KEY"
```
> 🚨 Dont'forget to install Langchain's OpenAI library by executing 
`uv add langchain-openai` or `pip install langchain-openai`.

### Azure OpenAI
To use OpenAI LLMs on Azure, fill the `model_endpoints.yml` file at the root of the project, with, for example:
```
endpoints:
  - endpoint_id: "azure-gpt-4o-mini"
      provider: "Azure OpenAI"
      api_key: "YOUR_AZURE_OPENAI_API_KEY"
      endpoint_url: "AZURE_OPENAI_ENDPOINT_URL"
      api_version: "API_VERSION"
      deployment_name: "DEPLOYMENT_NAME"
```

> 🚨 Dont'forget to install Langchain's OpenAI library by executing 
`uv add langchain-openai` or `pip install langchain-openai`.

### Azure ML LLMs
To use other LLMs hosted on Azure fill the `model_endpoints.yml` file at the root
of the project, with, for example:
```
endpoints:
  - endpoint_id: "llama3-8b"
    provider: "Azure ML"
    api_key: "YOUR_AZURE_ML_API_KEY"
    endpoint_url: "AZURE_ENDPOINT_URL"
```

### Anthropic (not tested yet)
To use Anthropic LLMs, fill the `model_endpoints.yml` file at the root of the project, 
with, for example:
```
endpoints:
  - endpoint_id: "claude-3-sonnet-20240229"
    provider: "Anthropic"
    api_key: "YOUR_OPENAI_API_KEY"
```
> 🚨 Dont'forget to install Langchain's Anthropic library by executing 
`uv add langchain-anthropic` or `pip install -U langchain-anthropic`

### HuggingFace (not tested yet)
To use HuggingFace LLMs, fill the `model_endpoints.yml` file at the root of the project, with, for example:
```
endpoints:
  - endpoint_id: "microsoft/Phi-3-mini-4k-instruct"
    provider: "Hugging Face"
```
> 🚨 Dont'forget to install Langchain's Hugging Face library by executing 
`uv add langchain-huggingface` or `pip install -U langchain-huggingface`
and login with the following:
```
from huggingface_hub import login
login()
```

### Others
Again, we wish to be compatible with every provider you are used to, so feel free to open an issue and contribute to expanding our LLMs' coverage. Check first if LangChain
is compatible with your preferred provider [here](https://python.langchain.com/docs/integrations/providers/).

# 🔍 Observability 

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

```
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
