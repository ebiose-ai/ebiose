# Contributing to Ebiose

Welcome to Ebiose! We’re excited that you’re interested in contributing to our project. Ebiose is a **distributed artificial intelligence factory** that enables humans and AI agents to collaborate in building tomorrow's AI in an open and democratic way. Your contributions will help us achieve this vision.

This guide will walk you through how to get started, the types of contributions we welcome, and how to submit your work.

---

## 🛠️ How to Contribute

We welcome all types of contributions, including but not limited to:
- **Code**: Bug fixes, new features, or improvements to existing code.
- **Documentation**: Improving the README, adding tutorials, or clarifying existing docs.
- **Ideas**: Suggesting new features or improvements.
- **Community**: Helping others on Discord, writing blog posts, or sharing your projects.

---

## 🚀 Getting Started

### 1. **Set Up Your Development Environment**
Before contributing, make sure you have the following:
- Python 3.12 or higher.
- [uv](https://docs.astral.sh/uv/) or `pip` for dependency management.
- A GitHub account.

#### Steps:
1. Fork the repository:
```bash
git clone git@github.com:your-username/ebiose.git && cd ebiose
```

2. Install dependencies:
```bash
uv sync  # or pip install -r requirements.txt
```

3. Add the project root to your PYTHONPATH:
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

### 2. Find an Issue to Work On
Check the [GitHub Issues](https://github.com/ebiose-ai/ebiose/issues) for open tasks.

Look for issues labeled `good first issue` if you’re new to the project.

If you have an idea, open a new issue to discuss it with the maintainers.

### 3. Make Your Changes
Create a new branch for your work:

```bash
git checkout -b feature/your-feature-name
```

Follow the project’s coding style and conventions.

Write clear commit messages:

```bash
git commit -m "feat: add support for Hugging Face models"
```

### 4. Submit a Pull Request (PR)
Push your changes to your fork:

```bash
git push origin feature/your-feature-name
```

Open a PR against the `main` branch of the Ebiose repository.

Fill out the PR template, including:
- A description of your changes.
- Screenshots or examples (if applicable).
- Reference to related issues (e.g., `Closes #123`).

## 🧑‍💻 Contribution Guidelines
Code Style
- Follow [PEP 8](https://peps.python.org/pep-0008/) for Python code.
- Use type hints where applicable.
- Keep functions and classes small and focused.

Documentation
- Update the `README`, glossary, or other docs if your changes affect them.
- Use clear and concise language.

Commit Messages
- Use the [Conventional Commits](https://www.conventionalcommits.org/) format:
    - feat: for new features.
    - fix: for bug fixes.
    - docs: for documentation changes.
    - chore: for maintenance tasks.

## 🐛 Reporting Bugs
If you find a bug, please open an issue on GitHub with the following details:
- A clear description of the problem.
- Steps to reproduce the issue.
- Expected vs. actual behavior.
- Screenshots or error logs (if applicable).

## 💡 Suggesting Features
Have an idea for a new feature or improvement? Open an issue and:
- Describe the feature and its benefits.
- Provide examples or use cases.
- Tag the issue with the `enhancement` label.

## 🛠️ Project Structure
Here’s a quick overview of the repository:
- `ebiose/`: Core implementation of architect agents, forges, and the Darwinian engine.
- `examples/`: Example forges and usage scripts (e.g., `math_forge`).
- `notebooks/`: Jupyter notebooks for quickstart and experimentation.

## 🤝 Community
Join our [Discord server](https://discord.gg/P5pEuG5a4V) to:
- Ask questions and get help.
- Share your projects and ideas.
- Collaborate with other contributors.

## 📜 Code of Conduct
We are committed to fostering a welcoming and inclusive community. Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before participating.

## 🙏 Acknowledgments
We appreciate all contributions, big or small. Thank you for helping us build Ebiose!

## ❓ Questions?
If you have any questions or need help, feel free to:
- Open an issue on GitHub.
- Join our [Discord server](https://discord.gg/P5pEuG5a4V).
- Reach out to the maintainers directly.

Happy contributing! 🎉

