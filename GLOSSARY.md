# Glossary

Ebiose comes with its own terminology inspired by both AI and natural evolution.  
Here are defined the main terms used throughout the project.

### 🤖 Agent

An **Ebiose agent** is an autonomous, intelligent entity orchestrated by an **Agent Engine** 🚀. An agent can be complex and composed of multiple modules; it can also invoke other agents. In this way, agents serve as the fundamental **reusable building blocks** 🧩 within Ebiose.

### ⚙️ Agent Engine

The Agent Engine is the central engine responsible for managing and executing an agent.

**Current Implementation (LangGraph)**: Ebiose currently offers a graph-based Agent Engine using the LangGraph framework.

**Future Scalability and Compatibility**: Ebiose supports the simultaneous integration of multiple Agent Engines. These engines can coexist and collaborate in the same environment. It will thus be possible to integrate popular frameworks such as Autogen or CrewAI or even develop custom Agent Engines.

### 🕸️ Graph-Based Agent Engine 

We have implemented a first agent engine in the form of a graph:

**Nodes (Building Blocks)**: Each node is an independent component that performs a specific function. Examples of node types include:

- Language models (LLMs) ✅ (implemented)
- Sub-agents 🚧 (work in progress)
- Specialized ML models ⏳ (todo)
- External API connectors ⏳ (todo)
- Database interfaces ⏳ (todo)
- Code executors ⏳ (todo)
- ... and many others 💡 (open to ideas)

**Edges (transitions)**: Connections between nodes define the execution flow and can include:

- Direct transitions
- Conditional branching
- Conditional loops on the same node

### 👷 Architect Agent 

A **specialized agent** whose objective is to design, create, and evolve other agents within dedicated forges. Architect agents select and assemble existing building blocks to craft new agents and reusable components, fueling the continuous innovation and evolution of the Ebiose ecosystem.

A **specialized type of agent** whose objective is to design, create, and evolve other agents within forges. Agent Architects select and assemble existing building blocks to create new agents and reusable components, thereby contributing to the continuous improvement of the entire biosphere.

### 🌐 Ecosystem 

A distributed and living environment where agents evolve and compete, architect agents craft new agents in isolated "forges" by utilizing a shared library of reusable building blocks. Users contribute by proposing new challenges or interacting with existing agents.

### 🌎 Ebiose Biosphere 

An **interconnected network** of all Ebiose ecosystems. Like the Earth’s biosphere, it forms a global system in which innovations, agents, and knowledge can circulate and evolve. This artificial biosphere is a **dynamic, living environment**, continuously enriched through multi-level interactions among ecosystems, agents, and humans.

### 🛠️ Forge

An **isolated laboratory** where custom agents are created to solve specific problems. The forge is the exclusive origin of new agents. Within each forge, Agent Architects orchestrate the creation and improvement of agents by reusing existing building blocks from the ecosystem.

### 🧬 Forge Cycle

A cycle represents a period of evolution within a forge, during which agents are created, tested, and improved through a **Darwinian process** . Each cycle has a defined computation budget and ends when this budget is consumed.