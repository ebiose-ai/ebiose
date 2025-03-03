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
 

👀 **Must read** 👀
- [Founding article](https://bit.ly/ebiose-blog-post) *(10 min)*
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
git clone git@github.com:ebiose-ai/ebiose-core.git && cd ebiose
```

Ebiose uses [uv](https://docs.astral.sh/uv/) as a packaging and dependency manager. See [Astral's uv documentation](https://docs.astral.sh/uv/getting-started/installation/) to install it.  

If you don't want to use `uv`, you can still use the `requirements.txt` file to install dependencies with `pip` or `conda`.

## 📦 Install Project Dependencies with uv

Once uv is installed, use it to install your project dependencies. In your project directory, run:

```sh
uv sync
```

For more detailed instructions or troubleshooting tips, refer to the [official uv documentation](https://docs.astral.sh/uv/).

> 💡 Pro Tip: You may need to add the root of the repository to your `PYTHONPATH` environment variable. Alternatively, use a `.env` file to do so.

## 🔍 Understand forges and forge cycles

The Jupyter notebook [quickstart.ipynb](notebooks/quickstart.ipynb) is the easiest way to understand the basics and start experimenting with Ebiose. This notebook lets you try out **architect agents** and **forges** on your very own challenges. 🤓

## 🛠️ Implement your own forge

To go further, the `examples/` directory features a complete forge example designed to optimize agents that solve math problems. Check out `examples/[math_forge/math_forge.py](math_forge/math_forge.py)` for the implementation of the 'MathLangGraphForge' forge.

To run a cycle of the Math forge, execute the following command in your project directory:

```sh
uv run ./examples/math_forge/run.py
```

Once agents are written to the save path, evaluate an agent by executing:

```sh
uv run ./examples/math_forge/evaluate.py
```

Kick off your journey by implementing your own forge with the accompanying `compute_fitness` method! 🎉

## 🤖 LLM model APIs support

As of today, the easiest way to experiment with Ebiose is to use the OpenAI API. Just set your OpenAI API key via an `.env` file or run:

```bash
export OPENAI_API_KEY=<your_openai_api_key>
```

For support with other LLM providers, refer to [LangChain's API support](https://python.langchain.com/docs/integrations/llms/) and modify our [LangChain backend implementation](ebiose/backends/langgraph/compute_intensive_batch_processor.py) as needed.

## 📞 Contact

For questions, comments, or ideas, feel free to join our [Discord](https://discord.gg/naewTgYnDt) or open an issue.

**All feedback is highly appreciated. Thanks! 🎊**
