import discord
from discord.ext import commands
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
from collections import Counter, defaultdict
from bs4 import BeautifulSoup

load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")

bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())

# verify if bot is on
@bot.event
async def on_ready():
    print("Bot ready!")
    # print(RIOT_API_KEY)

# joining members
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name='general')
    if channel:
        await channel.send(f"Welcome to the monkey squad, {member.mention}!")
    role = discord.utils.get(member.guild.roles, name='monkey')
    if role:
        await member.add_roles(role)

# adding roles to members
@bot.event 
async def on_raw_reaction_add(payload):
    emoji_role_map = {
        '1️⃣': 'valorant',
        '2️⃣': 'lol',
        '3️⃣': 'tft',
        '4️⃣': 'pokemon'
    }
    guild = bot.get_guild(payload.guild_id)
    if guild is None:
        return
    role_name = emoji_role_map.get(str(payload.emoji))
    if role_name is None:
        return
    role = discord.utils.get(guild.roles, name=role_name)
    if role is None:
        return
    member = guild.get_member(payload.user_id)
    if member is None or member.bot:
        return
    bot_member = guild.get_member(bot.user.id)
    bot_top_role = bot_member.top_role if bot_member else None
    if bot_top_role is None:
        return
    if bot_top_role.position <= role.position:
        return
    if not bot_top_role.permissions.manage_roles:
        return
    await member.add_roles(role)
    print(f"Added {role_name} role to {member.display_name}")

# deleting roles to members
@bot.event
async def on_raw_reaction_remove(payload):
    emoji_role_map = {
        '1️⃣': 'valorant',
        '2️⃣': 'lol',
        '3️⃣': 'tft',
        '4️⃣': 'pokemon'
    }
    guild = bot.get_guild(payload.guild_id)
    if guild is None:
        return
    role_name = emoji_role_map.get(str(payload.emoji))
    if role_name is None:
        return
    role = discord.utils.get(guild.roles, name=role_name)
    if role is None:
        return
    member = guild.get_member(payload.user_id)
    if member is None or member.bot:
        return
    bot_member = guild.get_member(bot.user.id)
    bot_top_role = bot_member.top_role if bot_member else None
    if bot_top_role is None:
        return
    if bot_top_role.position <= role.position:
        return
    if not bot_top_role.permissions.manage_roles:
        return
    await member.remove_roles(role)
    print(f"Removed {role_name} role from {member.display_name}")


# League of Legends
@bot.command()

async def get_summoner_info(ctx, game_name, tag_line):
    """
    Usage: .get_summoner_info <game_name> <tag_line>
    Example: .get_summoner_info Faker KR1
    """
    account_url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    account_response = requests.get(account_url, headers=headers)
    # Debug to check API response
    # print("Account API response: ", account_response.status_code, account_response.text)
    if account_response.status_code == 200:
        puuid = account_response.json().get('puuid')
    else:
        await ctx.send("User not found!")
        return
    # 1. Get PUUID from Account-V1 (CHECK)
    summoner_url = f"https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
    summoner_response = requests.get(summoner_url, headers=headers)

    # 2. Get summoner info from Summoner-V4 (CHECK)
    if summoner_response.status_code == 200:
        summoner_data = summoner_response.json()
        summoner_level = summoner_data.get('summonerLevel', 'N/A')
    else:
        await ctx.send("Summoner info not found!")
        return

    if account_response.status_code == 200:
        account_data = account_response.json()
        summoner_name = f"{account_data.get('gameName', 'N/A')}#{account_data.get('tagLine', 'N/A')}"
    else:
        summoner_name = 'N/A'

    # Get last played match date 
    match_url = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=1"
    match_response = requests.get(match_url, headers=headers)

    if match_response.status_code == 200 and match_response.json():
        match_id = match_response.json()[0]
        match_detail_url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}"
        match_detail_response = requests.get(match_detail_url, headers=headers)
        if match_detail_response.status_code == 200:
            match_data = match_detail_response.json()
            game_end_timestamp = match_data.get('info', {}).get('gameEndTimestamp')
            if game_end_timestamp:
                last_played = datetime.fromtimestamp(game_end_timestamp/1000).strftime('%m-%d-%Y %H:%M:%S')
            else:
                last_played = 'N/A'
        else:
            last_played = 'N/A'
    else:
        last_played = 'N/A'

    msg = (
        f"Summoner Name: {summoner_name}\n"
        f"Summoner Level: {summoner_level}\n"
        f"Last Played Date: {last_played}\n"
    )
    # await ctx.send(msg)

    # 3. Get user ranking for this season
    league_ranked_url = f"https://na1.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}"
    league_ranked_response = requests.get(league_ranked_url, headers=headers)
    if league_ranked_response.status_code == 200:
        league_entries = league_ranked_response.json()
        # Find Solo/Duo queue or use the first available
        solo_entry = next((entry for entry in league_entries if entry.get('queueType') == 'RANKED_SOLO_5x5'), None)
        entry = solo_entry if solo_entry else (league_entries[0] if league_entries else None)
        if entry:
            league_queue_type = entry.get('queueType', 'N/A')
            league_tier = entry.get('tier', 'N/A')
            league_rank = entry.get('rank', 'N/A')
            league_win = entry.get('wins', 0)
            league_loss = entry.get('losses', 0)
            total_games = league_win + league_loss
            win_rate = round((league_win/total_games) * 100, 2) if total_games > 0 else 0
            rank_msg = (
                f"Queue Type: {league_queue_type}\n"
                f"Tier: {league_tier}\n"
                f"Rank: {league_rank}\n"
                f"Wins: {league_win}\n"
                f"Losses: {league_loss}\n"
                f"Win Rate: {win_rate}%\n"
            )
        else:
            rank_msg = "No ranked data found."
        # await ctx.send(rank_msg)
    else:
        await ctx.send("Could not retrieve ranked info.")

    # 4. Get top 3 champions played in last 10 matches, get how many wins, games, kills, deaths
    matches_url = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=10"
    matches_response = requests.get(matches_url, headers=headers)
    match_ids = matches_response.json() if matches_response.status_code == 200 else []

    # keep track on what we are countering
    champion_counter = Counter()
    champion_wins = Counter()
    champion_games = Counter()
    champion_kills = defaultdict(int)
    champion_deaths = defaultdict(int)
    champion_lanes = defaultdict(list)

    for match_id in match_ids:
        match_detail_url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}"
        match_detail_response = requests.get(match_detail_url, headers=headers)
        if match_detail_response.status_code == 200:
            match_data = match_detail_response.json()
            participants = match_data.get('info', {}).get('participants', [])
            for p in participants:
                if p.get('puuid') == puuid:
                    champion_name = p.get('championName', 'N/A')
                    champion_counter[champion_name] += 1
                    if p.get('win'):
                        champion_wins[champion_name] += 1
                    champion_kills[champion_name] += p.get('kills', 0)
                    champion_deaths[champion_name] += p.get('deaths', 0)
                    lane = p.get('lane', 'UNKNOWN')
                    champion_lanes[champion_name].append(lane)

    # receive the top 3 champs countered
    top_3 = champion_counter.most_common(3)
    top_3_details = []
    for champ, count in top_3:
        wins = champion_wins[champ]
        kills = champion_kills[champ]
        deaths = champion_deaths[champ]
        lanes = champion_lanes[champ]
        most_played_lane = Counter(lanes).most_common(1)[0][0] if lanes else "UNKNOWN"
        top_3_details.append(
            f"{champ}: {count} games, {wins} wins, {round(kills/deaths,2)} kda, Lane: {most_played_lane} "
        )
    top_3_str = "\n".join(top_3_details) if top_3_details else "No data"

    embed = discord.Embed(title="Summoner Info:", color=discord.Color.blue())
    embed.set_image(url="https://cdn.discordapp.com/attachments/1422740867143438457/1423908196820455565/p1.png?ex=68e20559&is=68e0b3d9&hm=4a7f5965db1922184d947ef70b49ace8255a383c1e60ea8a315149a43fed1de2&")
    embed.add_field(name="Summoner Name:", value=summoner_name, inline=True)
    embed.add_field(name="Summoner Level", value=summoner_level, inline=True)
    embed.add_field(name="Last Played Date", value=last_played, inline=False)
    embed.add_field(name="Ranked Stats", value=rank_msg, inline=False)
    embed.add_field(name="Top 3 Champions within the latest 10 match", value=top_3_str, inline=False)
    await ctx.send(embed=embed)

# patch notes 
@bot.command()
async def patch_notes(ctx):
    import re
    url = "https://www.leagueoflegends.com/en-us/news/tags/patch-notes/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # find the first patch notes article link
    article = soup.find("a", href=lambda x: x and "/news/game-updates/patch-" in x)
    patch_number = "Unknown"
    if article:
        patch_url = "https://www.leagueoflegends.com" + article.get("href")
        patch_response = requests.get(patch_url)
        patch_soup = BeautifulSoup(patch_response.text, "html.parser")
        summary = patch_soup.find("p").text.strip() if patch_soup.find("p") else "See full patch notes at the link below."
        
        # find the Patch Highlights section and its image
        highlights_section = patch_soup.find(lambda tag: tag.name == "h2" and "Patch Highlights" in tag.text)
        img_url = ""
        if highlights_section:
            parent = highlights_section.find_parent()
            img_tag = parent.find("img") if parent else None
            if not img_tag:
                next_img = highlights_section.find_next("img")
                img_tag = next_img if next_img else None
            img_url = img_tag["src"] if img_tag and "src" in img_tag.attrs else ""
        if not img_url:
            img_tag = patch_soup.find("img", src=lambda x: x and (".jpg" in x or ".png" in x))
            img_url = img_tag["src"] if img_tag and "src" in img_tag.attrs else ""
        
        # try to extract patch number from image URL or patch URL
        match = re.search(r'(\d+\.\d+)', img_url)
        if not match:
            match = re.search(r'patch-(\d+)-(\d+)-notes', patch_url)
            if match:
                patch_number = f"{match.group(1)}.{match.group(2)}"
        else:
            patch_number = match.group(1)
        patch_title = f"Patch {patch_number}"
    else:
        patch_title = "Patch Notes"
        patch_url = url
        summary = "Could not fetch patch notes."
        img_url = ""

    embed = discord.Embed(title=patch_title, url=patch_url, description=summary, color=discord.Color.blue())
    if img_url and img_url.startswith('http'):
        embed.set_image(url=img_url)
    await ctx.send(embed=embed)

# Valorant
# Player stats
# Patch Notes

# TFT
# Player stats
# Patch Notes

# Pokemon
# Pokemon Wikipedia
# Pokemon Gambling
# lets add some changes

# open discord api 
with open("discord-bot/token.txt") as file:
    token = file.read()

bot.run(token)