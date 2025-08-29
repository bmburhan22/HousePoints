**Most important: Use `/sync` command first!**

**Next: Use `/register_houses` command to set up your houses**

HousePoints Discord Bot helps keep track of points of houses. Add new houses, members to houses. Add or deduct points from members/houses. Show Leaderboard. 
Create a .env file (using text editor) in the program folder (same folder as the python program file) 
Type ```TOKEN=YOUR-DISCORD-BOT-TOKEN``` in .env file then run the python file

## Available Commands

### Basic Commands
- **`/sync`** - Synchronize the Discord server members' attributes with the database
- **`/houses`** - Display information about houses and their points
- **`/user <@user_1> <@user_2> ... <@user_n>`** - Display points and house for mentioned users
- **`/leaderboard`** - Display a leaderboard of houses and their members' points

### Moderator Commands
- **`/points <amount> to <@user/@house>`** - Add points to users or all members of houses
- **`/points <amount> from <@user/@house>`** - Remove points from users or all members of houses

### Admin Commands
- **`/mod add <@role_1> <@role_2> ... <@role_n>`** - Add roles as moderators
- **`/mod remove <@role_1> <@role_2> ... <@role_n>`** - Remove roles as moderators
- **`/points_limit <limit>`** - Set the points limit
- **`/register <@house_1> <@house_2> ... <@house_n>`** - Register new houses
- **`/delete <@house_1> <@house_2> ... <@house_n>`** - Delete houses

## Screenshots

### Moderator Management
![Moderator Commands](mod.png)
*Add and remove moderators using `/mod add @user` and `/mod remove @user` commands*

### Adding Points
![Adding Points](addpoints.png)
*Add points to houses using `/points [amount] to @House [Name]` command*

### Deducting Points
![Deducting Points](deductpoints.png)
*Deduct points from houses using `/points [amount] from @House [Name]` command*