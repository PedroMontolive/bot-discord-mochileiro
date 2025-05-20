# 🤖 Mochileiro Discord Bot

A work-in-progress full management system for Discord servers, built in Python, focused on:

- Open source and full control in the hands of the server owner  
- Replaces multiple bots with a single, simple, and customizable solution  
- Easy to modify and expand for users with basic Python knowledge  

Ideal for those who want autonomy and don’t want to depend on third-party bots that can disappear or change policies without notice.

---

## ⚙️ Features (in development)

- Welcome system with reaction-based role assignment  
- Modular structure using Cogs  
- Uses `.env` to secure tokens and sensitive variables  
- Ready for expansion with admin commands, moderation tools, and API integrations  

---

## 🚀 How to run the bot locally

### 1. Prerequisites

- Python 3.10 or higher  
- Git  
- Code editor (VS Code recommended)  
- Discord account and a server you manage  

### 2. Clone the repository

```bash
git clone https://github.com/PedroMontolive/bot-discord-mochileiro.git
cd bot-discord-mochileiro
```

### 3. Create and activate a virtual environment

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:

```cmd
python -m venv venv
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure the `.env` file

Rename `.example.env` to `.env` and fill in:

```env
DISCORD_TOKEN=your_token_here
```

> 💡 Get your token by creating an application and bot at the [Discord Developer Portal](https://discord.com/developers/applications)

### 6. Run the bot

```bash
python main.py
```

---

## 👨‍🔧 How to contribute

1. Fork the repository  
2. Create a branch: `git checkout -b my-feature`  
3. Make your changes  
4. Submit a pull request  

---

> Made with coffee and stubbornness by [Pedro Montolive](https://github.com/PedroMontolive) ☕

---

## 🛠️ Extra setup steps

### ✅ 1. Enable verification / initial role

To set up the verification message with reaction and role assignment:

```bash
!setup
```

This command will create the verification message in the designated channel.

---

### 🎟️ 2. Enable ticket system

1. Run the command in Discord:

```bash
!setup_suporte
```

2. You will receive a private message with the following IDs:
   - Server ID (GUILD_ID)
   - Staff role ID (STAFF_ROLE_ID)
   - Ticket category ID (CATEGORIA_TICKET_ID)

3. Copy these IDs into your `.env` file like this:

```env
GUILD_ID=your_id_here
STAFF_ROLE_ID=your_id_here
CATEGORIA_TICKET_ID=your_id_here
```

4. Save the file and **restart the bot** to apply the changes.

---
