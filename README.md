# ChatGPT Telegram Bot

This is the fork of original [ChatGPT Telegram Bot](https://github.com/father-bot/chatgpt_telegram_bot) github repo.

This repo is ChatGPT re-created as Telegram Bot. **And it works great.**

The main goal of this fork is to deploy the [original one](https://github.com/father-bot/chatgpt_telegram_bot) along with implementing my own specific needs.

## Features
- Low latency replies (it usually takes about 3-5 seconds)
- No request limits
- Message streaming
- GPT-4 and GPT-4 Turbo support
- DALLE 2 (choose 👩‍🎨 Artist mode to generate images)
- Voice message recognition
- Code highlighting
- special chat modes: 👩🏼‍🎓 Assistant, 👩🏼‍💻 Code Assistant, 👩‍🎨 Artist, and others.
- List of allowed Telegram users
- Track $ balance spent on OpenAI API



## News (compared to forked repo)
### MKrinitskiy:
- *19 Aug 2024*: added [`gpt-4o-mini`](https://openai.com/index/gpt-4o-mini-advancing-cost-efficient-intelligence/) support
- *19 May 2024*: Replaced `gpt-4-turbo` with [GPT-4o](https://platform.openai.com/docs/models/gpt-4o).
- *24 Apr 2024*: Added [gpt-4-turbo-2024-04-09](https://platform.openai.com/docs/models/gpt-4-turbo-and-gpt-4) support (aliased as `gpt-4-turbo`)
- *25 Apr 2024*: Added summarizing chat mode
- *26 Apr 2024*: Added text files summarizing in the summarizing chat mode
- *28 Apr 2024*: DALL-E 2 changed to DALL-E 3

## Bot commands
- `/retry` – Regenerate last bot answer
- `/new` – Start new dialog
- `/mode` – Select chat mode
- `/balance` – Show balance
- `/settings` – Show settings
- `/help` – Show help

## Setup
1. Get your [OpenAI API](https://openai.com/api/) key

2. Get your Telegram bot token from [@BotFather](https://t.me/BotFather)

3. Edit `config/config.example.yml` to set your tokens and run 2 commands below (*if you're advanced user, you can also edit* `config/config.example.env`):
    ```bash
    mv config/config.example.yml config/config.yml
    mv config/config.example.env config/config.env
    ```

4. 🔥 And now **run**:
    ```bash
    docker-compose --env-file config/config.env up --build
    ```



## References
1. [*Build ChatGPT from GPT-3*](https://learnprompting.org/docs/applied_prompting/build_chatgpt)
1. Main contributor: @karfly
3. [Father.Bot](https://father.bot).
