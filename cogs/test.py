import discord
from discord.ext import commands

# create a class
class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # verify if bot is on
    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot ready!")
        # print(RIOT_API_KEY)

    @commands.command()
    async def ping(self, ctx):
        ping_embeded = discord.Embed(title="Discord Bot Ping", description="Latency in ms", color=discord.Color.blue())
        ping_embeded.set_image(url="https://pics.craiyon.com/2024-05-12/B8R3tffeQAy5DVA5MQncrQ.webp")
        ping_embeded.add_field(name=f"{self.bot.user.name}'s Latency (ms): ", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        ping_embeded.set_footer(text=f"Requested by {ctx.author.name}.")
        
        await ctx.send(embed=ping_embeded)

    # joining members
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = discord.utils.get(member.guild.text_channels, name='general')
        if channel:
            await channel.send(f"Welcome to the monkey squad, {member.mention}!")
        role = discord.utils.get(member.guild.roles, name='monkey')
        if role:
            await member.add_roles(role)

async def setup(bot):
    await bot.add_cog(Test(bot))
