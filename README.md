# 🎲 AI-Powered D&D Game Master 🐉


An intelligent Dungeon Master powered by AI that creates dynamic, engaging D&D adventures! This console-based application generates unique storylines, manages NPCs, and handles combat mechanics while adapting to player choices.

## ✨ Features

- 🤖 AI-driven storyline generation using GPT models
- 🎭 Dynamic NPC creation and management
- ⚔️ Turn-based combat system with D&D 5e rules
- 🌍 Procedural world generation
- 🎲 Realistic dice rolling mechanics
- 💬 Natural language processing for player commands

## 🏗️ Project Structure

```bash
dnd_ai_dm/
├── core/ # Core game mechanics
│ ├── game_manager.py # Main game controller
│ ├── story_generator.py # AI story generation
│ ├── npc_manager.py # NPC handling
│ └── combat_system.py # Combat mechanics
├── models/ # Game entities
│ ├── character.py # Player character
│ ├── npc.py # NPC definition
│ └── world_state.py # World tracking
├── utils/ # Utility functions
│ ├── dice.py # Dice rolling
│ └── text_processor.py # Text handling
└── main.py # Entry point
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/msadeqsirjani/dnd_ai_dm.git
```

2. **Create a virtual environment**

```bash
python -m venv venv
```

3. **Activate the virtual environment**

```bash
source venv/bin/activate
```

4. **Install requirements**

```bash
pip install -r requirements.txt
```


5. **Set up environment variables**

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=<your-openai-api-key>
```

### 🎮 Running the Game

```bash
python main.py
```

## 🎯 Core Components

### 🤖 Story Generator

- Utilizes OpenAI's GPT models
- Creates dynamic quest narratives
- Adapts story based on player choices

### 🎭 NPC Manager

- Generates unique NPCs with personalities
- Manages NPC interactions and relationships
- Tracks NPC locations and knowledge

### ⚔️ Combat System

- Initiative-based turn order
- D&D 5e combat rules
- Dice rolling mechanics

### 🌍 World State

- Tracks game world status
- Manages locations and quests
- Handles time and weather systems

## 📝 Example Gameplay

```bash
Welcome to AI D&D!
=================
Your quest begins:
You find yourself in the village of Eldermist, where rumors of strange
disappearances have been circulating...
What would you like to do?: talk to innkeeper
```

### Adding New Features

1. Create new modules in appropriate directories
2. Update the GameManager to integrate new features
3. Add tests for new functionality
4. Update documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT API
- D&D 5e SRD for game mechanics

## 📞 Contact

MOHAMMADSAEGH SIRJANI - [@msadeqsirjani](https://twitter.com/msadeqsirjani)

Project Link: [https://github.com/msadeqsirjani/dnd-ai-dm](https://github.com/msadeqsirjani/dnd-ai-dm)

---
<p align="center">
  Made with ❤️ by MOHAMMADSADEGH SIRJANI
</p>

