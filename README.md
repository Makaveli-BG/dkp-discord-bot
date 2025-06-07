# DKP Discord Bot

A powerful Discord bot that integrates with Google Sheets to manage and display DKP (previously known as: Dragon Kill Points) statistics for gaming guilds. Track player performance, view leaderboards, and compare stats with beautiful visualizations.

## Features

### 🔗 Account Management
- **Link Discord to Game ID**: Connect your Discord account to your in-game character
- **Unlink Accounts**: Remove the connection between Discord and game ID
- **Automatic Validation**: Prevents duplicate linking and ensures data integrity

### 📊 Statistics & Analytics
- **Personal Stats**: View detailed DKP and performance statistics
- **Player Lookup**: Check stats for other linked players
- **Real-time Data**: Stats are synchronized with Google Sheets database
- **Categorized Display**: Organized sections for DKP, battle stats, and additional info

### 🏅 Leaderboards
- **Multiple Categories**: Rankings by DKP Score, Goals, Kill Counts, Power, and more
- **Top 10 Rankings**: See the best performers in each category
- **User Highlighting**: Your position is highlighted when you appear on leaderboards
- **Dynamic Formatting**: Automatically handles different number formats (K, M, percentages)

### ⚔️ Player Comparison
- **Head-to-Head Stats**: Compare your performance with other players
- **Visual Charts**: Beautiful matplotlib-generated comparison charts
- **Detailed Breakdown**: Side-by-side comparison of all comparable stats
- **Advantage Indicators**: Clear visual indicators showing who performs better

### 🛡️ Security & Management
- **Channel Restrictions**: Commands only work in designated channels
- **Data Validation**: Robust error handling and data validation
- **Permission Controls**: Secure access to sensitive operations

## Commands

### Account Management
```
$linkme <ID>     - Link your Discord account to a game ID
$unlink          - Unlink your Discord account from current ID
```

### Statistics
```
$stats           - View your own statistics
$stats @user     - View another user's statistics
```

### Leaderboards
```
$leaderboard [category]  - View top 10 players by category

Available categories:
- score    - DKP Score (default)
- goal     - DKP Goal
- rate     - DKP completion rate
- kills    - Base T4 Kills
- power    - Base Power
- dead     - Base Dead
- kvk      - KVK Kills (T4 + T5)
```

### Comparison
```
$compare @user   - Compare your stats with another player
```

### Help & Debug
```
$how             - Display help information
$debug           - Debug sheet structure (for troubleshooting)
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Discord Bot Token
- Google Sheets API credentials
- Google Sheets document with player data

### Required Python Packages
```bash
pip install discord.py gspread oauth2client matplotlib python-dotenv
```

### Configuration

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd dkp-discord-bot
   ```

2. **Create `.env` file**
   ```env
   # Discord Bot Configuration
   DISCORD_BOT_TOKEN=your_discord_bot_token
   COMMAND_PREFIX=$
   
   # Google Sheets Configuration
   GOOGLE_SHEET_ID=your_google_sheet_id
   CREDENTIALS_FILE=credentials.json
   
   # Discord Channel Configuration
   ALLOWED_CHANNEL_ID=your_channel_id
   
   # Logging Configuration
   LOG_LEVEL=INFO
   ```

3. **Set up Google Sheets API**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google Sheets API
   - Create credentials (Service Account)
   - Download the JSON credentials file as `credentials.json`
   - Share your Google Sheet with the service account email

4. **Create Discord Bot**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create new application
   - Go to "Bot" section
   - Create bot and copy the token
   - Enable necessary intents (Message Content Intent)

5. **Invite Bot to Server**
   - In Discord Developer Portal, go to OAuth2 > URL Generator
   - Select "bot" scope and necessary permissions
   - Use generated URL to invite bot to your server

### Running the Bot
```bash
python bot.py
```

## Google Sheets Structure

The bot expects a Google Sheets document with the following structure:

### Required Columns
- **Column A**: ID (Player ID)
- **Column B**: IN-GAME NAME (Player's in-game name)
- **Column C**: Discord ID (Linked Discord user)
- ![image](https://github.com/user-attachments/assets/8cd16a8b-1015-4a5b-93fa-7d6c6314d628)


### DKP Columns (auto-detected)
- **DKP SCORE**: Current DKP score
- **DKP GOAL**: Target DKP goal
- **DKP RATE**: Completion percentage
- ![image](https://github.com/user-attachments/assets/31db3403-f76e-4776-ad0f-c8091da21cba)


### XLSX File
Here's a ready document for it, but you'll have to map from where it'll take the stats.
[DKP Discord Bot.xlsx](https://github.com/user-attachments/files/20641315/DKP.Discord.Bot.xlsx)


## Features in Detail

### Color-Coded DKP Performance
- 🔴 **Red (Low)**: Below 100% of DKP goal
- 🔵 **Blue (Medium)**: 100-300% of DKP goal  
- 🟢 **Green (High)**: Above 300% of DKP goal

### Number Formatting
The bot intelligently handles various number formats:
- Large numbers: 1,000,000 → 1M
- Thousands: 1,500 → 1.5K
- Percentages: 150%
- Comma-separated values

### Error Handling
- Graceful handling of missing data
- User-friendly error messages
- Automatic fallbacks for malformed data
- Debug tools for troubleshooting

## Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check if bot is online
   - Verify command is used in allowed channel
   - Check Discord permissions

2. **"Not linked" errors**
   - Use `$linkme <ID>` to link your account
   - Verify your ID exists in the Google Sheet

3. **Google Sheets errors**
   - Verify credentials.json is properly configured
   - Check if service account has access to the sheet
   - Ensure sheet name matches configuration

4. **Permission errors**
   - Verify bot has necessary Discord permissions
   - Check channel restrictions

### Debug Commands
Use `$debug` to troubleshoot:
- View sheet structure
- Check column mappings
- Verify your data row
- Test Discord ID matching

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Contact the bot developer
- Check the troubleshooting section

## Acknowledgments

- Built with discord.py
- Google Sheets integration via gspread
- Data visualization with matplotlib
- Developed for gaming guild management

---

**Bot by 义 Ragńàr | Powered by Discord & Google Sheets**
