# Discord Bot Project

This project is a simple Discord bot written in Python. It demonstrates basic bot setup, authentication, and usage of the Discord API, APIs for games like League of Legends, Valorant, Pokemon, TFT.

## Project Structure

```
discord-bot/
├── main.py        # Main Python script for the bot
├── token.txt      # File containing your Discord bot token
```

## Getting Started

1. **Clone the repository:**

   ```
   git clone https://github.com/LQNguyen05-max/discord-bot.git
   ```

2. **Install dependencies:**
   Make sure you have Python 3.x installed. Install the required packages:

   ```
   pip install discord.py
   ```

3. **Bot Token:**

   - Place your Discord bot token in a file named `token.txt` in the project root directory.
   - Make an .env and call your APIs in there.
   - **Never share your token publicly!**

4. **Run the bot:**
   ```
   python main.py
   ```

## Git Troubleshooting

If you encounter errors when pushing to GitHub, such as:

```
! [rejected]        main -> main (non-fast-forward)
error: failed to push some refs to 'https://github.com/LQNguyen05-max/discord-bot.git'
hint: Updates were rejected because the tip of your current branch is behind
hint: its remote counterpart. If you want to integrate the remote changes,
hint: use 'git pull' before pushing again.
```

This means your local branch is behind the remote. To fix:

1. Pull the latest changes from the remote:
   ```
   git pull discord-bot main
   ```
   If you see `fatal: refusing to merge unrelated histories`, run:
   ```
   git pull discord-bot main --allow-unrelated-histories
   ```
2. Resolve any merge conflicts if prompted.
3. Push your changes again:
   ```
   git push -u discord-bot main
   ```

## License

This project is for educational purposes. Please check the repository for license details.
