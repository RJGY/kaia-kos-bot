import discord
from discord import SelectOption
from discord.ext import tasks
from discord.ui import Select, Button, View
import datetime as dt
import requests
import os
import logging
import datetime
import numbers
import time

from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

hypixel_api_key = os.getenv('HYPIXEL_API_KEY')
minecraft_api_host = 'https://api.mojang.com/users/profiles/minecraft/'
hypixel_api_host = 'https://api.hypixel.net/v2'

"""File helper functions"""
def populate_player_list():
    f = open("player_list.txt", "r")
    player_list = [line.rstrip('\n') for line in f.readlines()]
    return player_list


def save_to_file(player_list: list[str]):
    f = open("player_list.txt", "w")
    text = "\n".join(player_list)
    f.write(text)


"""API Helper functions"""
def convert_username_to_uuid(username: str):
    uuid_obj = requests.get(minecraft_api_host + username)
    if uuid_obj.status_code != 200:
        return
    return uuid_obj.json()["id"]


def get_player_data_hypixel(key: str, uuid: str):
    json_obj = requests.get(f"{hypixel_api_host}/player?key={key}&uuid={uuid}")
    if json_obj.status_code != 200:
        return
    return json_obj.json()

def get_player_status_hypixel(key: str, uuid: str):
    json_obj = requests.get(f"{hypixel_api_host}/status?key={key}&uuid={uuid}")
    if json_obj.status_code != 200:
        return
    return json_obj.json()

def get_numbers_from_json(json_obj, numbers_list=None):
    if numbers_list is None:
        numbers_list = []

    if isinstance(json_obj, dict):
        for value in json_obj.values():
            get_numbers_from_json(value, numbers_list)
    elif isinstance(json_obj, list):
        for item in json_obj:
            get_numbers_from_json(item, numbers_list)
    elif isinstance(json_obj, numbers.Number):
        numbers_list.append(json_obj)
    return numbers_list
        

class APICommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.player_list = populate_player_list()


    """Listeners"""
    @commands.Cog.listener()
    async def on_ready(self):
        synced = await self.bot.tree.sync()
        for command in synced:
            logging.info(f'Synced {command.name} with slash commands.')
        logging.info(f'Synced {len(synced)} commands with slash commands.')

            
    """Commands"""
    @discord.app_commands.command(name='test', description='Test command to make sure im not going insane :3.')
    async def test_command(self, interaction: discord.Interaction):
        await interaction.response.send_message('Test command.')

        
    @discord.app_commands.command(name='list', description='Get list of players')
    async def get_list_command(self, interaction: discord.Interaction):
        await interaction.response.defer()

        if not self.player_list:
            embed = discord.Embed(
                title='Error',
                colour=discord.Colour.red(),    
                timestamp=dt.datetime.now()
            )
            embed.set_author(name='KOS Bot')
            embed.add_field(name=f'yo retard u dont have any people in ur list', value=f'')
            await interaction.followup.send(embed=embed)
            return

        for uuid in self.player_list:
            data = get_player_data_hypixel(hypixel_api_key, uuid)
            if not data:
                embed = discord.Embed(
                    title='Error',
                    colour=discord.Colour.red(),    
                    timestamp=dt.datetime.now()
                )
                embed.set_author(name='KOS Bot')
                embed.add_field(name=f'Hypixel api fucking sucks or my api key died so u gonna have to wait for me to regenerate it :3.', value=f'UUID: {uuid}')
                await interaction.followup.send(embed=embed)
                return
            if not 'lastLogin' in data['player'].keys():
                numbers = get_numbers_from_json(data['player']['stats']['Pit']['profile'])
                numbers.sort()
                index = -1
                candidate = numbers[index] / 1000
                current_time = int(time.time())
                while candidate > current_time:
                    index -= 1
                    candidate = numbers[index] / 1000
                dt_object = datetime.datetime.fromtimestamp(candidate)
                print(dt_object.strftime('%c'))
                difference = datetime.datetime.now() - dt_object
                print(f'Time since last action: {difference.days} days, {difference.seconds // 3600} hours, {(difference.seconds % 3600) // 60} minutes, {(difference.seconds % 60)} seconds')
                embed = discord.Embed(
                    title=f'{data["player"]["displayname"]}',
                    colour=discord.Colour.blue(),    
                    timestamp=dt.datetime.now()
                )
                embed.set_author(name='KOS Bot')
                embed.add_field(name='This guy sucks and has api disabled against them.', value='', inline=False)
                embed.add_field(name=f'Time since last pit action: {difference.days} days, {difference.seconds // 3600} hours, {(difference.seconds % 3600) // 60} minutes, {(difference.seconds % 60)} seconds', value='', inline=False)
                await interaction.followup.send(embed=embed)
            else:
                dt_object = datetime.datetime.fromtimestamp(data['player']['lastLogin'] / 1000)
                print(dt_object.strftime('%c'))
                difference = datetime.datetime.now() - dt_object
                print(difference.seconds % 86400)
                print(f'Time since last login: {difference.days} days, {difference.seconds // 3600} hours, {(difference.seconds % 3600) // 60} minutes, {(difference.seconds % 60)} seconds')
                status = get_player_status_hypixel(hypixel_api_key, uuid)
                print(status)
                print(f"Online: {status['session']['online']}")
                embed = discord.Embed(
                    title=f'{data["player"]["displayname"]}',
                    colour=discord.Colour.blue(),    
                    timestamp=dt.datetime.now()
                )
                embed.set_author(name='KOS Bot')
                embed.add_field(name=f'Time since last login: {difference.days} days, {difference.seconds // 3600} hours, {(difference.seconds % 3600) // 60} minutes, {(difference.seconds % 60)} seconds', value='', inline=False)
                embed.add_field(name=f"Online: {status['session']['online']}", value='', inline=False)
                await interaction.followup.send(embed=embed)

    @discord.app_commands.command(name='add', description='Add to list of players')
    @discord.app_commands.describe(username='The username of the player.')
    async def add_list_command(self, interaction: discord.Interaction, username: str):
        await interaction.response.defer()

        uuid = convert_username_to_uuid(username)

        if not uuid:
            embed = discord.Embed(
                title='Error',
                colour=discord.Colour.red(),    
                timestamp=dt.datetime.now()
            )
            embed.set_author(name='KOS Bot')
            embed.add_field(name=f'Minecraft api fucking sucks and died for some reason idk.', value='')
            await interaction.followup.send(embed=embed)
            return
        
        if uuid in self.player_list:
            embed = discord.Embed(
                title='Error',
                colour=discord.Colour.red(),    
                timestamp=dt.datetime.now()
            )
            embed.set_author(name='KOS Bot')
            embed.add_field(name=f'Retard that guy is already on the list.', value='')
            await interaction.followup.send(embed=embed)
            return
        self.player_list.append(uuid)
        save_to_file(self.player_list)

        embed = discord.Embed(
            title='Added user',
            colour=discord.Colour.green(),    
            timestamp=dt.datetime.now()
        )
        embed.set_author(name='KOS Bot')
        embed.add_field(name=f'{username} was added to the list', value=f'UUID: {uuid}')
        await interaction.followup.send(embed=embed)
        return
    

    @discord.app_commands.command(name='remove', description='Remove from list of players')
    @discord.app_commands.describe(username='The username of the player.')
    async def remove_list_command(self, interaction: discord.Interaction, username: str):
        await interaction.response.defer()

        uuid = convert_username_to_uuid(username)

        if not uuid:
            embed = discord.Embed(
                title='Error',
                colour=discord.Colour.red(),    
                timestamp=dt.datetime.now()
            )
            embed.set_author(name='KOS Bot')
            embed.add_field(name=f'Minecraft api fucking sucks and died for some reason idk.', value='')
            await interaction.followup.send(embed=embed)
            return
        
        if uuid not in self.player_list:
            embed = discord.Embed(
                title='Error',
                colour=discord.Colour.red(),    
                timestamp=dt.datetime.now()
            )
            embed.set_author(name='KOS Bot')
            embed.add_field(name=f'Retard that guy cant be removed cause theyre not on the list.', value='')
            await interaction.followup.send(embed=embed)
            return
        self.player_list.remove(uuid)
        save_to_file(self.player_list)

        embed = discord.Embed(
            title='Removed user',
            colour=discord.Colour.green(),    
            timestamp=dt.datetime.now()
        )
        embed.set_author(name='KOS Bot')
        embed.add_field(name=f'{username} was removed from the list', value=f'UUID: {uuid}')
        await interaction.followup.send(embed=embed)
        return
            

    @commands.hybrid_command(name='sync', description='Syncs the bot with slash commands.')
    async def sync_command(self, ctx: commands.Context):
        """Syncs the bot with slash commands."""
        await ctx.defer()
        synced = await self.bot.tree.sync()
        for command in synced:
            await ctx.send(f'Synced {command.name} with slash commands.')
        await ctx.send(f'Synced {len(synced)} commands with slash commands.')
            
        
async def setup(bot: commands.Bot):
    await bot.add_cog(APICommands(bot))
    

if __name__ == '__main__':
    player_list = populate_player_list()
    print(player_list)
    save_to_file(['asdf','balls'])
    uuid = convert_username_to_uuid('duck669s')
    pass