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


# Quick start

## Installation

First, clone the repository:

```bash
git clone git@github.com:ebiose-ai/ebiose-core.git && cd ebiose
```

Ebiose uses [uv](https://docs.astral.sh/uv/) as a packaging and dependency manager. See [Astral's uv documentation](https://docs.astral.sh/uv/getting-started/installation/) to install it.  

If you don't want to use `uv`, you can still use the `requirements.txt` file for installing the dependencies with `pip` or `conda`.

## Install Project Dependencies with uv

Once uv is installed, use it to install your project dependencies. In your project directory, run:

```sh
uv sync
```

For more detailed instructions or troubleshooting tips, refer to the [official uv documentation](https://docs.astral.sh/uv/).

> 💡 For the following, you may need to add the root of the repository to your `PYTHONPATH` environment variable. You may also use a `.env` file to do so.

## Understand forges and forge cycles

The Jupyter notebook [quickstart.ipynb](notebooks/quickstart.ipynb) is the easiest way to 
understand the basics and start experimenting with Ebiose. 
This notebook allows you to try so-called **architect agents** and **forges** on your very own problematic.

## Implement your own forge

To go further, the `examples/` directory contains a practical example of a complete forge
made to optimize agents specialized in solving math problems. Look at `examples/[math_forge/math_forge.py](math_forge/math_forge.py)` for the implemetation of the 'MathLangGraphForge` forge.

To run a cycle of the Math forge, execute the following command in your project directory:

```sh
uv run ./examples/math_forge/run.py
```

As soon as first agents have been written in the save path, you can evaluate an agent by executing:

```sh
uv run ./examples/math_forge/evaluate.py
```

Start from here to implement your own forge, with the corresponding `compute_fitness` method.

## LLM model APIs support

As of today, the easiest way to experiment with Ebiose is to use the OpenAI API. To do so, all you have to do is to set your OpenAI API key via an `.env` file or by executing:

```bash
export OPENAI_API_KEY=<your_openai_api_key>
```

To use other LLM providers, you may refer to [LangChain's API support](https://python.langchain.com/docs/integrations/llms/) and modify our [LangChain backend implementation](ebiose/backends/langgraph/compute_intensive_batch_processor.py) accordingly.

<!-- ## Code overview -->

<!-- ## Roadmap -->


## Contact

For any question, comment, idea or else, feel free to ask on [Discord](https://discord.gg/naewTgYnDt) and directly create an issue.

**All feedback will be very valuable. Thanks.**
