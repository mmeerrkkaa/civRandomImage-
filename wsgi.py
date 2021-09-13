# -*- coding: utf-8 -*-
import discord
from fuzzywuzzy import process
from discord.utils import get
from discord.ext import commands
import time
from discord.ext.commands import has_permissions, MissingPermissions
import datetime

from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice

import random
import asyncio
import trueskill
import mpmath

import os
import dialogflow
from google.protobuf.json_format import MessageToDict
import jishaku
import re
import rolled


if 'mpmath' in trueskill.backends.available_backends():
	# mpmath can be used in the current environment
	trueskill.setup(backend='mpmath')


from pymongo import MongoClient

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "file.json"
project_id = "civilization"
session_id = "your_session_id"
language_code = "ru"
session_client = dialogflow.SessionsClient()
session = session_client.session_path(project_id, session_id)

cluster = MongoClient(f"mongodb+srv://root:discordGPT@cluster0.ej8oe.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

db = cluster['discord']
collestionuser = db['users']
collestionlobby = db['lobby']
collestionnation = db["nation"]


print(discord.__version__)


country = {"Америка": {"text": '''Бонус нации: Явное предначертание

Все сухопутные войска получают + 1 к радиусу обзора. На 50% снижена цена покупки клеток. Также очень часто рождается на реке.

Уникальный отряд: Минитмен: Сила 24
Б-17: Сила 70''',
"link": "https://prntscr.com/1ilgui3"},
"Австрия": {"text": "На будущее"}}


GuildId = 606231975531118603 # ид гильдии 
RatingChannel = 815465891973562418 # канал где находится рейтинг
MessageRatingChannel = 818831350639362058 # сообщение которое изменять при изменении рейтинга

guild_ids = [GuildId]
intents = discord.Intents.default()
intents.members = True

#client = discord.Client(intents=discord.Intents.all())
#client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all(), case_insensitive=True)
#bot = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True)

bot.load_extension("jishaku")
bot.remove_command('help')
slash = SlashCommand(bot, sync_commands=True)

embedcolorandom = ["0xCAFF33", "0x3393FF", "AC33FF", "FF3393", "33FF5B", "FFFC33"]

async def SelectMember(member_id):
	a = collestionuser.find_one({'id_member' : int(member_id)})
	return a


async def SelectLobby(id_message):
	if len(str(id_message)) > 4:
		a = collestionlobby.find_one({'id_message' : int(id_message)})
	else:
		a = collestionlobby.find_one({'ids' : int(id_message)})
	return a


@bot.event  # пи заходе выдать гражданина
async def on_member_join(member):
	user = await SelectMember(member.id)
	if user is None:
		collestionuser.insert_one({"id_member": member.id, "messages": 0, "joins": 1, "mutes": 0, "wins": 0, "rating": [1000, 50, 1000, 50], "games": 0, "VoiceTime": 0, "LastVoice": "None", "LastMessage": "None", "lobby": None})
	else:#Если существует
		collestionuser.update_one({"id_member": member.id}, {"$set": {"joins": 1}})

	#await createDb()
	try:
		if len(user["roles"]) != 0:
			for i in user["roles"]:
				roleAdd = get(gui.roles, name=i)
				await member.add_roles(roleAdd)
		else:
			role = "Гражданин | V"
			role = get(gui.roles, name=role)
			await member.add_roles(role)
	except:
		role = "Гражданин | V"
		role = get(gui.roles, name=role)
		await member.add_roles(role)


@bot.event
async def on_member_ban(guild, user):
	channel = value = bot.get_channel(608546051649175562)
	await channel.send(f"merka\n{user} Получил бан.")


@bot.event
async def on_member_remove(member):
   # chanadm = bot.get_channel(608283223792812032)
	if work == 1:
		channel = bot.get_channel(608283223792812032)
		await channel.send(f"{member} Покинул сервер.")
		collestionuser.update_one({"id_member": member.id}, {"$set": {"joins": 0}})

class Member_Update:
	def __init__(self, before, after, entry):
		self.author_update = after.id
		self.entry = entry
		self.before = before
		self.after = after
		self.action = Member_Update.__isTakeGive(self)
		self.role = Member_Update.__whatroles(self)


	def __isTakeGive(self):
		if len(self.before.roles) > len(self.after.roles):
			return "take" # забрали
		else:
			return "give" # дали

	def __whatroles(self):
		if self.action == "take":
			for i in self.before.roles:
				if i not in self.after.roles:
					return i.name
					break
		elif self.action == "give":
			for i in self.after.roles:
				if i not in self.before.roles:
					return i.name
					break


@bot.event
async def on_member_update(before, after):
	if after.roles != before.roles:

		entry = list(await after.guild.audit_logs(limit=1).flatten())[0]
		

		roleName = get(gui.roles, id=gui.get_member(entry.user.id).top_role.id)
		if str(roleName) not in ["Администратор", "Модератор", "Организатор"] and str(roleName) in ['Великий полководец | Топ 1']:
			Update_role = Member_Update(before, after, entry)

			if Update_role.action == 'give':

				if Update_role.role == "Полководец":
					if len(get(gui.roles, name="Полководец").members) <= 3:
						pass
					else:
						role = get(gui.roles, name = Update_role.role)
						member = gui.get_member(int(after.id))
						await member.remove_roles(role)

				else:
					role = get(gui.roles, name = Update_role.role)
					member = gui.get_member(int(after.id))
					await member.remove_roles(role)

			else:
				if Update_role.role == "Полководец":
					pass

				else:

					role = get(gui.roles, name = Update_role.role)
					member = gui.get_member(int(after.id))
					await member.add_roles(role)


		await UpdateRaiting()
		print(after)
		spis = []
		for role in after.roles[1:]:
			spis.append(role.name)
		collestionuser.update_one({"id_member": after.id}, {"$set": {"roles": spis}})


async def dialogfol(message):

	roleName = get(gui.roles, id=gui.get_member(message.author.id).top_role.id)
	if str(roleName) not in ["Администратор", "Модератор", "Организатор"]:
		return 0
	texts = str(message.content)
	text_input = dialogflow.types.TextInput(text=texts, language_code=language_code)
	query_input = dialogflow.types.QueryInput(text=text_input)
	session = session_client.session_path(project_id, str(random.randint(1, 1000000)))
	response_dialogflow = session_client.detect_intent(session=session, query_input=query_input)

	json_response = MessageToDict(response_dialogflow)
	if g == 1:
		await message.channel.send(json_response)
	json_response = json_response['queryResult'] # ["fulfillmentText"]
	if json_response['intent']["displayName"] == "Какие бонусы у $country":
		await message.channel.send(f"{json_response['parameters']['country']}\n{country[json_response['parameters']['country']]['link']}")
	elif json_response['intent']["displayName"] == "скачать":
		await message.channel.send(json_response["fulfillmentText"])
	elif json_response['intent']["displayName"] == "профиль":
		await infos(message)

	elif json_response['intent']["displayName"] == "отменить игру":
		await cancels(message, int(json_response['parameters']['number']))

	elif json_response['intent']["displayName"] == "изменить рейтинг":
		nam = gui.get_member(int(json_response['parameters']['member']))
		await setrating(message,nam , int(json_response['parameters']['number']))

	elif json_response['intent']["displayName"] == "создай":
		await createlobby(message)
	elif json_response['intent']["displayName"] == "addmember":

		for i in message.mentions:
			nam = gui.get_member(int(i.id))
			await addmembers(message, int(json_response['parameters']['number']), nam)

@bot.event
async def on_message(message):

	if message.author.id == 234395307759108106 or message. author. id == 235088799074484224 and message.channel.id != 617755335569965080:
		await message.delete()
	if message.author == bot.user:
		return

	if message.channel.id != 628625510280462391:
		await dialogfol(message)



	roleName = get(gui.roles, id=gui.get_member(message.author.id).top_role.id)

	if message.content.find('@everyone') != -1 and str(roleName) not in ["Администратор", "Модератор", "Организатор"]:

		await message.delete()

	channel = active_channel



	messagesa = await SelectMember(message.author.id)
	collestionuser.update_one({"id_member": message.author.id}, {"$set": {"messages": messagesa["messages"] + 1}})

	times = datetime.datetime.today() + datetime.timedelta(hours=3)

	collestionuser.update_one({"id_member": message.author.id}, {"$set": {"LastMessage": f'{times.day}.{times.month}.{times.year} - {times.hour}:{times.minute}'}})
	await bot.process_commands(message)
	if message.channel == active_channel:
		id_mess = await channel.fetch_message(message.id)
		await asyncio.sleep(5)
		await id_mess.delete()





@bot.event
async def on_ready():
	global channel_log, complete_channel, gui, members, active_channel

	#with open("members.json", "r") as read_file:
		#members = json.load(read_file)

	channel = bot.get_channel(608546051649175562) # закрытый чат
	complete_channel = bot.get_channel(818865271711203338)
	active_channel = bot.get_channel(818865123204005899)

	gui = bot.get_guild(GuildId)
	
	#await createDb()
	#await indRole()
	await UpdateRaiting()


	#await channel.send(len(members))
	channel_log = bot.get_channel(818425321984491550)
	print('Бот в сети {0.user}'.format(bot))



	while True:
		await bot.change_presence(activity=discord.Game(name="Sid Meier's Civilization V"))
		await asyncio.sleep(270)

		await bot.change_presence(activity=discord.Game(name="2"))

@bot.event
async def on_raw_reaction_add(messages):
	
	user_id = messages.user_id # ID пользователя, который добавил реакцию

   # message_id = messages.message_id
	if messages.user_id == bot.user.id:
		return -1
	dan = await SelectLobby(messages.message_id)

	if dan == None:
		if messages.emoji.name == "👥":
			date_format = "%I:%M"
			crat = await bot.get_channel(messages.channel_id).fetch_message(messages.message_id)
			cratdate = crat.created_at.strftime(date_format)
			mesactiv = await active_channel.history().flatten()
			print(cratdate)
			for i in mesactiv:
				print(i)
				if i.created_at.strftime(date_format) == cratdate:
					await MemberReaction(i, user_id) # await PlusMember(messages, user_id)
					break

	else:
		dan = [dan['id_message'], dan['id_leader_lobby'], dan['active']]
		if messages.emoji.name == "👑":
			await CrownReaction(messages, user_id)
		elif messages.emoji.name == "👥":
			await MemberReaction(messages, user_id) # await PlusMember(messages, user_id)
		elif messages.emoji.name == "🔄":
			if str(messages.user_id) == str(dan[1]) and int(dan[2]) <= 1:
				try:
					nam = gui.get_member(int(user_id))
					collestionlobby.update_one({"id_message": messages.message_id}, {"$set": {"voice_id": int(nam.voice.channel.id)}})
				except:
					nam = bot.get_user(int(user_id))
					collestionlobby.update_one({"id_message": messages.message_id}, {"$set": {"voice_id": 'None'}})
	
				await UpdateLobby(messages, user_id)
		elif messages.emoji.name == "☑️":
			await ReadyGame(messages,user_id)
		elif messages.emoji.name == "🚫":

			if str(user_id) == str(dan[1]) and int(dan[2]) <= 1:
				await CancelGame(messages, user_id)
		elif messages.emoji.name == "✅":
			if str(messages.user_id) == str(dan[1]) and int(dan[2]) == 1:
				await CompleteGame(messages, user_id)

	
	
   # await channel.send(f"{messages.emoji.name}")

g = 0
voicecham = "Дуэль"
@bot.command()
async def gact(ctx, text = None):
	global g
	global voicecham
	
	if text == None:
		if g == 1:
			g = 0
		else:
			g = 1
		await ctx.send(g)
	else:
		voicecham = text
		await ctx.send(voicecham)

	

@bot.event
async def on_voice_state_update(member, before, after):
	
	times = datetime.datetime.today() + datetime.timedelta(hours=3)
	collestionuser.update_one({"id_member": member.id}, {"$set": {"LastVoice": f"{times.day}.{times.month}.{times.year} - {times.hour}:{times.minute}"}})


	if g == 1:
		try:
			voice_channel = bot.get_channel(after.channel.id)
		except:
			return
		
		if voice_channel.name != voicecham:
			nam = gui.get_member(int(336119947736514560))
			if nam in voice_channel.members:
				for i in voice_channel.members:
					if i.id != 336119947736514560:
						nam = gui.get_member(int(i.id))
						channel = discord.utils.find(lambda x: x.name == voicecham, gui.channels)
						await nam.move_to(channel, reason = "Ёж")




async def CrownReaction(messages, user_id):

	leadLobMes = await SelectLobby(messages.message_id)
	leadLobMes = leadLobMes['id_leader_lobby']

	rows = collestionlobby.find()
	pos = get(gui.roles, id=gui.get_member(int(user_id)).top_role.id).position

	if pos >= 13:
		pass
	else:
		return 0
	nex = False

	for row in range(collestionlobby.count_documents({})):
		member_ids = rows[row]['id_members']
		if str(user_id) in member_ids and int(rows[row]['active']) <= 1 and str(rows[row]['id_message']) == str(messages.message_id):
			nex = True


	if nex == True:
		if leadLobMes == 'None':

			collestionlobby.update_one({"id_message": messages.message_id}, {"$set": {"id_leader_lobby": str(user_id)}})
			nam = bot.get_user(int(user_id))

			dsa = await SelectLobby(messages.message_id)
			dsa = dsa['ids']
			await channel_log.send(f"`[Лобби №{dsa}] {nam} взял организатора лобби`")
			await UpdateLobby(messages, user_id)
			return 0
		else:

			if str(user_id) == str(leadLobMes):
				return -1
			else:
				pass

		id_leader = await SelectLobby(messages.message_id)
		id_leader = id_leader['id_leader_lobby']

		raitLeader = await SelectMember(id_leader)
		raitLeader = raitLeader["rating"][0]

		mem_rait = await SelectMember(user_id)
		mem_rait = mem_rait["rating"][0]


		roleLeader = get(gui.roles, id=gui.get_member(int(id_leader)).top_role.id)
		roleMember = get(gui.roles, id=gui.get_member(int(user_id)).top_role.id)


		if roleLeader.position > roleMember.position:
			return 0
		elif roleLeader.position < roleMember.position:

			pass
			
		else:
			if raitLeader > mem_rait:
				return 0
			elif raitLeader < mem_rait:
				pass
			else:
				return 0
		nam = bot.get_user(int(id_leader))
		collestionlobby.update_one({"id_message": messages.message_id}, {"$set": {"id_leader_lobby": messages.user_id}})
		nam = bot.get_user(int(user_id))
		namy = bot.get_user(int(id_leader))

		dsa = await SelectLobby(messages.message_id)
		dsa = dsa['ids']

		await channel_log.send(f"`[Лобби №{dsa}] {nam} взял организатора лобби у {namy}`")

		await UpdateLobby(messages, user_id)




async def UpdateLobby(messages, user_id):
	channel = active_channel
	try:
		messages = await channel.fetch_message(messages.id)
	except:
		messages = await channel.fetch_message(messages.message_id)



	row = await SelectLobby(messages.id)
	row = [row['id_leader_lobby'], row['id_members'], row['active'], row['voice_id']]
	membId = row[1]

	non = False
	if user_id == "None":
		non = True
	elif len(membId) == 0:
		collestionlobby.update_one({"id_message": messages.id}, {"$set": {"active": 3}})

		nam = bot.get_user(int(user_id))

		dsa = await SelectLobby(messages.id)
		dsa = dsa['ids']

		await channel_log.send(f"`[Лобби №{dsa}] {nam} Покинул лобби. Игра отменена`")
		collestionuser.update_one({"id_member": int(user_id)}, {"$set": {"lobby": None}})
		await messages.clear_reactions()

		non = True

	text = ""
 
	role = "Великий полководец | Топ 1"
	role = get(gui.roles, name=role)

	namtop = role.members[0].id

	topId = await SelectMember(namtop)
	for i in membId:
		nam = bot.get_user(int(i))
		if str(i) == str(row[0]):
			text += '👑'
		if str(i) == str(topId['id_member']):
			text += '🏆'
		
		text += f' {nam.mention}'+"\n"
		
		reit = ""
		for i in membId:
			
			dsa = await SelectMember(i)
			reit += str(dsa['rating'][0]) + "\n"
	

	dsa = await SelectLobby(messages.id)
	dsaids = dsa['ids']
	dsa = dsa['active']


	embed = discord.Embed(title=f"СТАТУС: __{status[dsa]}__", color=random.randint(0, 0xffffff))
	
	if non == False:

		embed.add_field(name="\u200b",
					value=f"\u200b", inline=True)


		embed.add_field(name="\u200b",
				value=f"\u200b", inline=True)
		try:
			embed.add_field(name="Голосовой канал",
				value=f"{bot.get_channel(int(row[3]))}", inline=True)
		except:
			embed.add_field(name="Голосовой канал",
				value=f"НЕ указан", inline=True)
		embed.add_field(name="\u200b",
					value=f"\u200b", inline=True)
		embed.add_field(name="Участники",
					value=f"{text}", inline=True)
		embed.add_field(name="Рейтинг",
					value=f"{reit}", inline=True)


		embed.set_footer(text=f"№ {dsaids}")
	else:

			embed.add_field(name="\u200b",
					value=f"\u200b", inline=True)
			embed.add_field(name="Участники",
					value=f"\u200b", inline=True)
			embed.add_field(name="Рейтинг",
					value=f"\u200b", inline=True)

			embed.set_footer(text=f"№ {dsaids}")
			await messages.edit(embed=embed)
			await asyncio.sleep(30)
			await messages.delete()
	if non == False:

		await messages.edit(embed=embed)

async def UpdateRaiting(iters = 50):
	channel = bot.get_channel(RatingChannel)
	id_mess = await channel.fetch_message(MessageRatingChannel)

	rows = collestionuser.find(limit=iters).sort("rating.0", -1)
	role = "Великий полководец | Топ 1"
	role = get(gui.roles, name=role)
	namtop = role.members[0].id
	namremRol = gui.get_member(int(namtop))

	topone = await SelectMember(namtop)

	count = 0

	mesto = ""
	nams = ""
	rait = ""

	for row in rows:
		if count == iters:
			break
		nam = gui.get_member(int(row["id_member"]))
		if nam == None:
			continue
		if count == 0:

			namone = gui.get_member(int(row["id_member"]))


			if str(row["id_member"]) != str(topone['id_member']):
				if int(topone['rating'][0]) >= int(row['rating'][0]):
					pass
				else:


					await namone.add_roles(role)
					await namremRol.remove_roles(role)

					memc = get(gui.roles, name="Полководец")
					for i in memc.members:
						
						await i.remove_roles(memc)
			else:
				pass

			mesto += f"🏆"+"\n"
			nams += f"{str(nam.mention)}"+"\n"
			rait += f"*{str(row['rating'][0])}*" +"\n"
		else:
			mesto += f"{str(count+1)}"+"\n"
			nams += f"**{str(nam)}**"+"\n"
			rait += f"*{str(row['rating'][0])}*" +"\n"

		if "Почётный гражданин" not in nam.roles:
			if int(row['rating'][0]) > 1000:
				role = "Почётный гражданин"
				role = get(gui.roles, name=role)
				await nam.add_roles(role)

		count += 1
		

	embed = discord.Embed(title=f"\u200b", color=random.randint(0, 0xffffff))
	embed.add_field(name="Место",
			value=f"{mesto}", inline=True)
	embed.add_field(name="Ник",
		value=f"{nams}", inline=True)
	embed.add_field(name="Рейтинг",
		value=f"{rait}", inline=True)
	await id_mess.edit(embed=embed)

	role = "Почётный гражданин"
	role = get(gui.roles, name=role)

	for i in role.members:
		row = await SelectMember(i.id)
		if int(row['rating'][0]) <= 1000:
			await i.remove_roles(role)


async def ReadyGame(messages, user_id):
	
	raw = await SelectLobby(messages.message_id)
	raw = [raw['id_message'], raw['id_leader_lobby'], raw['active'], raw['id_members'], raw['ids']]
	
	if str(raw[1]) == str(user_id) and int(raw[2]) == 0:
		membId = raw[3]

		if len(membId) > 2:
			channel = active_channel
			id_mess = await channel.fetch_message(messages.message_id)
			await id_mess.clear_reactions()
			collestionlobby.update_one({"id_message": messages.message_id}, {"$set": {"active": 1}})
			times = datetime.datetime.today() + datetime.timedelta(hours=3)

			collestionlobby.update_one({"id_message": messages.message_id}, {"$set": {"date_start": times}})

			await UpdateLobby(messages, user_id)
			nam = bot.get_user(int(user_id))
			await channel_log.send(f"`[Лобби №{raw[4]}] {nam} подтвердил начало игры`")
			await id_mess.add_reaction('👑')
			await id_mess.add_reaction('✅')
			await id_mess.add_reaction('🚫')




async def CancelGame(messages, user_id):
	
	channel = active_channel
	id_mess = await channel.fetch_message(messages.message_id)
	collestionlobby.update_one({"id_message": messages.message_id}, {"$set": {"active": 3}})
	nam = bot.get_user(int(user_id))
	dsa = await SelectLobby(messages.message_id)
	await channel_log.send(f"`[Лобби №{dsa['ids']}] {nam} отменил игру`")

	for i in dsa["id_members"]:
		nam = await SelectMember(i)
		if nam["lobby"] == dsa["ids"]:

			collestionuser.update_one({"id_member": int(i)}, {"$set": {"lobby": None}})
	await id_mess.clear_reactions()
	await UpdateLobby(messages, user_id)
	await asyncio.sleep(30)
	await id_mess.delete()
	



async def CompleteGame(messages, user_id):

	row = await SelectLobby(messages.message_id)

	timesn = row['date_start']

	timesk = (datetime.datetime.today() + datetime.timedelta(hours=3)) - timesn

	hours, remainder = divmod(timesk.seconds, 3600)
	minutes, seconds = divmod(remainder, 60)

	timesk = f"{hours}:{minutes}"

	timesn = f"{timesn.day}.{timesn.month}.{timesn.year} - {timesn.hour}:{timesn.minute}"


	if hours == 0 and minutes < 20:
		return



	row = [row['id_members'], row['ids'], row['active']]
	membId = row[0]

	amemb = []
	
	summmu = 0
	summsig = 0
	for i in membId:
		raitMemb = await SelectMember(i)
		amemb.append([float(raitMemb['rating'][0]), raitMemb['rating'][1]])
		summmu += float(raitMemb['rating'][0])
		summsigm = float(raitMemb['rating'][1])

	emojiWin = "<:win:818703294641733644>"
	emojiLos = "<:los:818703340031836181>"






	rating_groups = []
	env = trueskill.TrueSkill(mu = summmu, sigma=summsigm,backend='mpmath',beta=summsigm/2, tau=summsigm/100)
	for i in amemb:

		

		rating_groups.append((env.create_rating(i[0], i[1]/3),))
	rated_rating_groups = env.rate(list(rating_groups))

	reit = ""
	for i in range(len(rating_groups)):

		a = rating_groups[i][0]
		d = rated_rating_groups[i][0]

		if round(a.mu) > round(d.mu):
			reit += f"{round(a.mu)} {emojiLos} {round(d.mu)} ({round(d.mu) - round(a.mu)})"+'\n'
		elif round(a.mu) < round(d.mu):
			reit += f"{round(a.mu)} {emojiWin} {round(d.mu)} (+{round(d.mu) - round(a.mu)}) "+'\n'
		else:
			reit += f"{round(a.mu)} {emojiWin} {round(d.mu)} "+'\n'

		dsa = await SelectMember(membId[i])
		rait = dsa['rating']
		if i == 0:



			wins = dsa["wins"]
			collestionuser.update_one({"id_member": int(membId[i])}, {"$set": {"wins": wins+1}})
		sigm = (len(rating_groups)/2) - i
		collestionuser.update_one({"id_member": int(membId[i])}, {"$set": {"rating": [round(d.mu), dsa['rating'][1]+sigm, rait[0], rait[1]]}})

		dsa = dsa["games"]

		collestionuser.update_one({"id_member": int(membId[i])}, {"$set": {"games": dsa+1}})

		collestionlobby.update_one({"id_message": messages.message_id}, {"$set": {"active": 2}})


	row = await SelectLobby(messages.message_id)
	row = [row['id_leader_lobby'], row['id_members'], row['active'], row['ids']]
	membId = row[1]

	text = ""
	for i in membId:
		nam = bot.get_user(int(i))

		bf = await SelectMember(nam.id)

		if bf['lobby'] == row[3]:
		
			collestionuser.update_one({"id_member": int(i)}, {"$set": {"lobby": None}})
		text += nam.mention+"\n"

	dsa = await SelectLobby(messages.message_id)
	await channel_log.send(f"`[Лобби №{dsa['ids']}] Игра завершена. {messages.message_id}`")
	channels = complete_channel # channels.last_message_id


	embed = discord.Embed(title=f"СТАТУС: __{status[row[2]]}__",    color=random.randint(0, 0xffffff))

	embed.add_field(name="Участники",
		value=f"{text}", inline=True)
	embed.add_field(name="Рейтинг",
		value=f"{reit}", inline=True)


	

	embed.add_field(name="начало игры",
		value=f"{timesn}", inline=False)
	embed.add_field(name="Время игры ⏲️",
		value=f"{timesk}", inline=False)

	if dsa['moves'] == 0:
		embed.add_field(name="Ходов",
			value=f"укажите командой !set {dsa['ids']} ходы.", inline=False)
	else:
		embed.add_field(name="Ходов",
			value=f"{dsa['moves']} ходов", inline=False)

	
	embed.set_footer(text=f"№ {dsa['ids']}")
	
	channel = active_channel
	id_mess = await channel.fetch_message(messages.message_id)
	await id_mess.delete()
	await complete_channel.send(embed=embed)

	time.sleep(1)
	collestionlobby.update_one({"id_message": messages.message_id}, {"$set": {"id_message": channels.last_message_id}})

  #  await id_mess.clear_reactions()
	nam = bot.get_user(int(user_id))
	
	await UpdateRaiting()
	

@bot.event
async def on_raw_reaction_remove(messages):
	user_id = messages.user_id # ID пользователя, который добавил реакцию

   # message_id = messages.message_id
	if user_id == 616257912779702333:
		return
	dan = await SelectLobby(messages.message_id)
	if dan == None:
		return -1
	else:
		if messages.emoji.name == "👑":
			await RemoveCrownReaction(messages, user_id)
		elif messages.emoji.name == "👥":
			await RemoveMemberReaction(messages, user_id) #await MemberReaction(messages, user_id) # await PlusMember(messages, user_id)

async def RemoveCrownReaction(messages,user_id):


	messagDB = await SelectLobby(messages.message_id)
	messagDB = [messagDB['id_leader_lobby'], messagDB['active']]

	if 1 < int(messagDB[1]) <= 3:
		return 0
	if str(messagDB[0]) == str(user_id):

		pass
	else:
		return 0

	
	collestionlobby.update_one({"id_message": messages.message_id}, {"$set": {"id_leader_lobby": 'None'}})
	nam = bot.get_user(int(user_id))

	dsa = await SelectLobby(messages.message_id)

	await channel_log.send(f"`[Лобби №{dsa['ids']}] {nam} убрал организатора лобби`")
	await UpdateLobby(messages, user_id) 




async def MemberReaction(messages, user_id, command = None):


	try:
		row = await SelectLobby(messages.id)
	except:
		row = await SelectLobby(messages.message_id)


	nam = bot.get_user(int(user_id))

	user = await SelectMember(int(user_id))

	if user["lobby"] != None:

		lobby = await SelectLobby(user['lobby'])

		if row['ids'] == user["lobby"]:
			print(0)
			return

		elif row['active'] == 0 and lobby['active'] != 0:
			pass
		else:
			await nam.send(f"`{nam.name} вы находитесь в сборящем лобби №{user['lobby']}. В присоединение отклонено. Если у вас возникли проблемы, обращайтесь к организаторам`")
			return -1


	membId = row['id_members']
	membId.append(str(user_id))


	collestionlobby.update_one({"id_message": row['id_message']}, {"$set": {"id_members": membId}})
	

	text = ""
	for i in membId:
		nam = bot.get_user(int(i))
		text += nam.mention+"\n"

	reit = ""
	for i in membId:

		dsa = await SelectMember(i)
		reit += str(dsa['rating'][0]) + "\n"

	nam = bot.get_user(int(user_id))

	dsa = await SelectLobby(row['id_message'])
	dsa = dsa['ids']
	collestionuser.update_one({"id_member": int(user_id)}, {"$set": {"lobby": dsa}})

	if command == None:
		await channel_log.send(f"`[Лобби №{dsa}] {nam} присоединился к лобби`")
	else:
		await channel_log.send(f"`{command} добавил в лобби [Лобби №{dsa}] {nam}`")
	await UpdateLobby(messages, user_id)
  #  await id_mess.edit(embed=embed)




async def RemoveMemberReaction(messages, user_id):
	nam = bot.get_user(int(user_id))

	dsa = await SelectLobby(messages.message_id)
	iiid = dsa['id_members']
	row = await SelectMember(int(user_id))
	

	if row["lobby"] == None or int(row["lobby"]) != int(dsa["ids"]):
		return -1

	if str(user_id) == str(dsa['id_leader_lobby']):
		collestionlobby.update_one({"id_message": messages.message_id}, {"$set": {"id_leader_lobby": 'None'}})


	del iiid[iiid.index(str(user_id))]
	collestionlobby.update_one({"id_message": messages.message_id}, {"$set": {"id_members": iiid}})
	collestionuser.update_one({"id_member": int(user_id)}, {"$set": {"lobby": None}})

	if len(iiid) != 0:
		await channel_log.send(f"`[Лобби №{dsa['ids']}] {nam} Покинул лобби`")
	await UpdateLobby(messages, user_id)


async def indRole():
	global gui
	
	memList = await gui.fetch_members(limit=1000).flatten()

	for member in memList:
		rolText = []
		members[str(member.id)] = "@everyone"
		for role in member.roles:
			rolText.append(role.name)


		rolText.pop(0)
		members[str(member.id)] = rolText


@commands.cooldown(1, 300, commands.BucketType.user)
@slash.slash(name="сбор",
			 description="Вы должны быть в голосовом канале",
			 options = [create_option(
				 name="сообщение",
				 description="Сообщение",
				 option_type=3,
				 required=False
				 )],
			 guild_ids=guild_ids)
@bot.command()
async def сбор(ctx, messB = None):
	if sbop == 1:
		try:
			channell = bot.get_channel(606231975531118609)

			embed = discord.Embed(title="СБОР", color=random.randint(0, 0xffffff))
			val = f"@everyone\n{ctx.author.mention} Собирает людей на игру.\nГолосовой канал - {ctx.author.voice.channel.mention}"

			if messB != None:
				val += "\n**Сообщение**: "+messB
			embed.add_field(name="\u200b",
			value=f"{val}",
							inline=False)
			embed.set_footer(text=f"!create")
			await ctx.send(embed=embed)
			await channell.send(embed=embed)

		except:
			pass



"""
@bot.command(pass_context=True)
async def nemecxol(ctx):
	global happy
	if happy == 0:
		happy +=1
	
		role = "супер новогодняя уникальная роль"
		role = get(gui.roles, name=role)
		PeoplGuild = await gui.fetch_members(limit=1000).flatten()
		a = []
		for member in PeoplGuild:
			a.append(str(member.id))
		
		await gui.get_member(int(random.choice(a))).add_roles(role)
		await ctx.send(f"{ctx.author.mention} Ну всё, роль улетела.")
	
"""
@bot.command()
async def das(ctx, member: discord.Member = None):
	

	if member is None:
		return
		
	embed = discord.Embed(title=f"123", color=random.randint(0, 0xffffff))
	embed.add_field(name="321", value=member.name, inline=True)
	await ctx.send(embed=embed)

	role = "Гражданин | V"
	role = get(gui.roles, name=role)
	await member.add_roles(role)

@bot.command(pass_context=True)
async def updateDB(ctx):
	await createDb()
	await ctx.send("UPDATED")
	



@bot.command(pass_context=True)
@has_permissions(ban_members=True)
async def tt(ctx, count = None):

	if count == None:
		await ctx.send(file=discord.File(r'members.json'))
		return
	await ctx.channel.purge(limit=int(count))

	


sbop = 1
work = 1

status = {0: "СБОР",
		1: "ИГРА",
		2: "ЗАВЕРШЕНО",
		3: "ОТМЕНЕНО"}


@bot.command(pass_context=True)
async def usr(ctx, mem_id):
	try: nam = gui.get_member(int(mem_id))
	except: nam = "Не на сервере"
	
	usrs = await SelectMember(mem_id)
	minVoic = usrs[7]/60
	await ctx.send(f"""id: {usrs[0]}
name: {nam}
сообщений: {usrs[1]}
на сервере?: {usrs[2]}
Запрет на бота?: {usrs[3]}
побед: {usrs[4]}
рейтинг: {usrs[5]}
игр: {usrs[6]}
секунд в голосовом канале: {usrs[7]}С|{round(minVoic, 1)}М|{round(minVoic/60, 1)}Ч
Последний заход в голосовой: {usrs[8]}
Последнее сообщение: {usrs[9]}
	""")

''' # топ рейтинга
cursor.execute(f"SELECT id_member, raiting FROM users ORDER BY raiting DESC;")
'''

@bot.command(pass_context=True)
async def aaa(ctx, iters = 0):

	rows = collestionuser.find().sort("rating", -1)

	count = 0
	
	mesto = ""
	nams = ""
	rait = ""
	for row in rows:
		if count == iters:
			break
		
		nam = gui.get_member(int(row['id_member']))
		mesto += f"{str(count+1)}"+"\n"
		nams += f"**{str(nam)}**"+"\n"
		rait += f"*{str(row['rating'][0])}*" +"\n"
		count += 1
		

	embed = discord.Embed(title=f"Рейтинг", color=random.randint(0, 0xffffff))
	embed.add_field(name="Место",
			value=f"{mesto}", inline=True)
	embed.add_field(name="Ник",
		value=f"{nams}", inline=True)
	embed.add_field(name="Рейтинг",
		value=f"{rait}", inline=True)
	await ctx.send(embed=embed)

@bot.command(pass_context=True)
@has_permissions(ban_members=True)
async def s(ctx, *args):
	argss = []
	summmu = 0
	summsigm = 0
	text = ""
	for i in args:
		res = re.sub(r"[\s,<, >, @, !]", "", i)
		usr = await SelectMember(res)
		rating = usr['rating']
		summmu += rating[0]
		summsigm += rating[1]
		argss.append([rating[0], rating[1], int(res)])
		nam = bot.get_user(int(res))
		text += nam.mention+"\n"


	emojiWin = "<:win:818703294641733644>"
	emojiLos = "<:los:818703340031836181>"

	rating_groups = []
	env = trueskill.TrueSkill(mu = summmu, sigma=summsigm,backend='mpmath',beta=summsigm/2, tau=summsigm/100)
	for i in argss:

		rating_groups.append((env.create_rating(i[0], i[1]/3),))
	rated_rating_groups = env.rate(list(rating_groups))

	reit = ""
	for i in range(len(rating_groups)):

		a = rating_groups[i][0]
		d = rated_rating_groups[i][0]

		if round(a.mu) > round(d.mu):
			reit += f"{round(a.mu)} {emojiLos} {round(d.mu)}"+'\n'
		elif round(a.mu) < round(d.mu):
			reit += f"{round(a.mu)} {emojiWin} {round(d.mu)}"+'\n'
		else:
			reit += f"{round(a.mu)} {emojiWin} {round(d.mu)}"+'\n'


	embed = discord.Embed(title=f"Симуляция игры",    color=random.randint(0, 0xffffff))

	embed.add_field(name="Участники",
		value=f"{text}", inline=True)
	embed.add_field(name="Рейтинг",
		value=f"{reit}", inline=True)

	await ctx.send(embed=embed)
	


@bot.command(pass_context=True)
async def vvv(ctx, *args):

	argss = [[]]
	summmu = 0
	summsigm = 0
	for i in args:
		if i != "|":
			argss[-1].append(float(i))
		else:
			summmu += float(argss[-1][0])
			summsigm += float(argss[-1][1])
			argss.append([])

	a = []
	for i in argss:
		a.append(i)
		env = trueskill.TrueSkill(mu = summmu, sigma=summsigm,backend='mpmath',beta=summsigm/2, tau=summsigm/100)

		rating_groups = []

		for i in a:
			rating_groups.append((env.create_rating(i[0], i[1]/3),))


	rated_rating_groups = env.rate(list(rating_groups))
	
	for i in range(len(rating_groups)):

		a = rating_groups[i][0]
		d = rated_rating_groups[i][0]
		await ctx.send(f"mu={d.mu}, si={d.sigma}")
	
	
@bot.command(pass_context=True)
async def www(ctx, *args):
	channel = bot.get_channel(818865123204005899)
	a = []
	for i in args:
		a.append(int(i))
	emojiWin = "<:win:818703294641733644>"
	emojiLos = "<:los:818703340031836181>"
	env = trueskill.TrueSkill(backend='mpmath')
	rating_groups = []
	for i in a:
		rating_groups.append((env.create_rating(i),))


	rated_rating_groups = env.rate(list(rating_groups))

	text = "Симуляция игры:\n"
	for i in range(len(rating_groups)):

		a = rating_groups[i][0]
		d = rated_rating_groups[i][0]

		if round(a.mu) > round(d.mu):
			if round(d.mu) < 0:
				text += f"{i+1} место: {round(a.mu)} {emojiLos} 0"+'\n'
			else:
				text += f"{i+1} место: {round(a.mu)} {emojiLos} {round(d.mu)}"+'\n'
		elif round(a.mu) < round(d.mu):
			text += f"{i+1} место: {round(a.mu)} {emojiWin} {round(d.mu)}"+'\n'
		else:
			text += f"{i+1} место: {round(a.mu)} {emojiWin} {round(d.mu)}"+'\n'
	await ctx.send(text)


@bot.command(pass_context=True)
async def ddd1(ctx, mes_id):
	dsad = await SelectLobby(mes_id)
	await ctx.send(dsad)

@bot.command(pass_context=True)
async def ddd2(ctx, mes_id):
	collestionlobby.remove({"id_message": int(mes_id)})
	await ctx.send("Удалено")


@bot.command(aliases = ['start', 'tst', 'create'])
async def __tst(ctx):
	await createlobby(ctx)



async def createlobby(ctx):

	role = "Великий полководец | Топ 1"
	role = get(gui.roles, name=role)
	namtop = role.members[0].id

	try:
		message = await ctx.channel.fetch_message(ctx.id)
	except:
		message = await ctx.channel.fetch_message(ctx.message.id)

	topId = await SelectMember(namtop)


	row = await SelectMember(int(ctx.author.id))

	if row["lobby"] != None:
		await ctx.author.send(f"`{ctx.author} вы находитесь в активном лобби №{row['lobby']}. В создании отклонено. Если у вас возникли проблемы, обращайтесь к организаторам`")
		await message.add_reaction('❌')
		return 0



	channels = active_channel
	raitMemb = await SelectMember(ctx.author.id)
	raitMemb = raitMemb["rating"][0]
	voicid = None

	embed = discord.Embed(title=f"СТАТУС: __{status[0]}__", color=random.randint(0, 0xffffff))
	embed.add_field(name="\u200b",
		value=f"\u200b", inline=True)
	embed.add_field(name="\u200b",
		value=f"\u200b", inline=True)

	try:
		embed.add_field(name="Голосовой канал",
			value=f"{ctx.author.voice.channel.mention}", inline=True)
		voicid = ctx.author.voice.channel.id
	except:
		embed.add_field(name="Голосовой канал",
			value=f"НЕ указан", inline=True)

	embed.add_field(name="\u200b",
		value=f"\u200b", inline=True)

	if str(ctx.author.id) == str(topId['id_member']):
		embed.add_field(name="Участники",
			value=f"🏆 {ctx.author.mention}", inline=True)
	else:
		embed.add_field(name="Участники",
			value=f"{ctx.author.mention}", inline=True)
	embed.add_field(name="Рейтинг",
		value=f" {raitMemb}", inline=True)

	lastid = collestionlobby.find(limit=1).sort('ids', -1)

	embed.set_footer(text=f"№ {lastid[0]['ids']+1}")

	
	await channel_log.send(f"`{ctx.author} создал лобби №{lastid[0]['ids'] + 1}`")
	await message.add_reaction('✅')
	await message.add_reaction('👥')

#   await ctx.send(embed=embed)
	message = await channels.send(embed=embed) # Возвращаем сообщение после отправки
	lst = channels.last_message_id
	arrays = [str(ctx.author.id)]
	time.sleep(1)

	collestionuser.update_one({"id_member": int(ctx.author.id)}, {"$set": {"lobby": lastid[0]['ids']+1}})
	collestionlobby.insert_one({"ids": lastid[0]['ids']+1, "id_message": lst, "id_leader_lobby": 'None', "id_members": arrays, "active": 0, "voice_id": f'{voicid}', "date_start": 'None', "moves": 0})
	await message.add_reaction('👑')
	await message.add_reaction('👥')
	await message.add_reaction('🔄')
	await message.add_reaction('☑️')
	await message.add_reaction('🚫')

# await ctx.send(f"{channel.last_message_id}")

@bot.command()
@has_permissions(ban_members=True)
async def setrating(ctx, id_memb: discord.Member = None, newRait = 0):

	if id_memb == None or newRait == None:
		return 0
	id_memb = id_memb.id

	if await SelectMember(id_memb)==None:
		return 0

	DoRait = await SelectMember(id_memb)
	DoRait = DoRait["rating"]

	nam = gui.get_member(int(id_memb))
	roleName = get(gui.roles, id=gui.get_member(ctx.author.id).top_role.id)

	await channel_log.send(f"`{roleName} {ctx.author.name} Установил рейтинг пользователю - {nam}: {DoRait[0]} | {newRait}`")
	await nam.send(f"`{roleName} {ctx.author.name} Установил вам новый рейтинг: {DoRait[0]} | {newRait}`")

	collestionuser.update_one({"id_member": id_memb}, {"$set": {"rating": [int(newRait), DoRait[1], DoRait[2], DoRait[3]]}})

	try:
		message = await ctx.channel.fetch_message(ctx.id)
		await message.add_reaction('✅')
	except:
		await ctx.message.add_reaction('✅')

	await UpdateRaiting()


@bot.command(pass_context=True)
@has_permissions(ban_members=True)
async def setgames(ctx, id_memb: discord.Member = None, newRait = 0):

	if id_memb == None or newRait == None:
		return 0
	id_memb = id_memb.id

	if await SelectMember(id_memb) == None:
		return 0

	collestionuser.update_one({"id_member": id_memb}, {"$set": {"games": newRait}})

	await ctx.message.add_reaction('✅')


@bot.command(pass_context=True)
@has_permissions(ban_members=True)
async def setwins(ctx, id_memb: discord.Member = None, newRait = 0):

	if id_memb == None or newRait == None:
		return 0
	id_memb = id_memb.id
	if await SelectMember(id_memb) == None:
		return 0

	collestionuser.update_one({"id_member": id_memb}, {"$set": {"wins": newRait}})
	await ctx.message.add_reaction('✅')


@bot.command()
async def roll_create(ctx):

	words = ['Америка','Голландия', 'Вавилон', 'Испания', 'Кельты', 'Австрия','Япония', 'Индонезия', 'Персия', 'Майя', 'Англия', 'Византия', 'Сонгай', 'Россия', 'Рим', 'Польша', 'Франция', 'Китай', 'Швеция', 'Карфаген', 'Греция', 'Индия', 'Сиам', 'Бразилия', 'Египет', 'Шошоны', 'Турция', 'Корея', 'Зулусы', 'Марокко', 'Аравия', 'Полинезия', 'Инки', 'Дания', 'Ассирия', 'Монголия', 'Ирокезы', 'Эфиопия', 'Ацтеки', 'Португалия', 'Германия']

	for i in words:
		collestionnation.insert_one({"name": i, "text": "Text", "point": None, "bans": 0})

	await ctx.send("create")
	
@bot.command()
async def roll(ctx, count, *args):
	print(args)
	user = await SelectMember(ctx.author.id)

	if user['lobby'] == None:
		return 0

	lobby = collestionlobby.find_one({'ids' : int(user['lobby'])})
	words = ['Америка', 'Вавилон', 'Испания', 'Кельты', 'Австрия','Япония', 'Индонезия', 'Персия', 'Майя', 'Англия', 'Византия', 'Сонгай', 'Россия', 'Рим', 'Польша', 'Франция', 'Китай', 'Швеция', 'Карфаген', 'Греция', 'Индия', 'Сиам', 'Бразилия', 'Египет', 'Шошоны', 'Турция', 'Корея', 'Зулусы', 'Марокко', 'Аравия', 'Полинезия', 'Инки', 'Дания', 'Ассирия', 'Монголия', 'Ирокезы', 'Эфиопия', 'Ацтеки', 'Португалия', 'Германия', "Нидерланды"]
	bans = "Баны: "
	for i in args:
		country = process.extractOne(i.title(), words)
		words.remove(country[0])
		bans += country[0]
		if country[1] != 100:
			bans += f"({country[1]}%)"

		if args[-1] != i:
			bans += ", "
	bans += "\n\n"


	random.shuffle(words)

	text = bans
	for i in lobby['id_members']:
		nam = bot.get_user(int(i))
		text += f"{nam.mention} выбирает из: "
		for q in range(int(count)):
			a = random.choice(words)
			words.remove(a)

			text += a
			if q != int(count) - 1:
				text +=  " / "
		text += "\n"


	await ctx.send(text)


@bot.command()
async def rolt(ctx, count, *args):
	user = await SelectMember(ctx.author.id)

	if user['lobby'] == None:
		return 0

	lobby = collestionlobby.find_one({'ids' : int(user['lobby'])})
	#words = ["Америка", "Египет"]
	words = ['Америка','Голландия', 'Вавилон', 'Испания', 'Кельты', 'Австрия','Япония', 'Индонезия', 'Персия', 'Майя', 'Англия', 'Византия', 'Сонгай', 'Россия', 'Рим', 'Польша', 'Франция', 'Китай', 'Швеция', 'Карфаген', 'Греция', 'Индия', 'Сиам', 'Бразилия', 'Египет', 'Шошоны', 'Турция', 'Корея', 'Зулусы', 'Марокко', 'Аравия', 'Полинезия', 'Инки', 'Дания', 'Ассирия', 'Монголия', 'Ирокезы', 'Эфиопия', 'Ацтеки', 'Португалия', 'Германия']
	bans = "Баны: "

	for i in args:
		country = process.extractOne(i.title(), words)
		words.remove(country[0])
		bans += country[0]
		if country[1] != 100:
			bans += f"({country[1]}%)"

		if args[-1] != i:
			bans += ", "
	bans += "\n\n"

	random.shuffle(words)

	text = bans
	members = []
	for i in lobby['id_members']:
		nam = gui.get_member(int(i))
		members.append(nam.display_name)

	imag = rolled.roll(members, count, words)

	#await ctx.send(file="deathl0x.png")
	await ctx.send(content = text,file=discord.File('deathl0x.png'))


@bot.command(pass_context=True)
@has_permissions(ban_members=True)
async def revoke(ctx, messages = None):
	if messages == None:
		return 0

	row = await SelectLobby(messages)
	if row == None:
		return 0

	count = 0
	for member in row['id_members']:
		mem =  await SelectMember(member)
		if count == 0:
			collestionuser.update_one({"id_member": int(member)}, {"$set": {"wins": mem['wins']-1}})
			count += 1

		collestionuser.update_one({"id_member": int(member)}, {"$set": {"rating": [mem['rating'][2], mem['rating'][3], mem['rating'][2], mem['rating'][3]]}})
		collestionuser.update_one({"id_member": int(member)}, {"$set": {"games": mem['games']-1}})
	
	collestionlobby.update_one({"id_message": row['id_message']}, {"$set": {"active": 3}})
	await ctx.message.add_reaction('✅')
	roleName = get(gui.roles, id=gui.get_member(ctx.author.id).top_role.id)
	await channel_log.send(f"`{roleName} {ctx.author.name} Отменил и вернул рейтинг за игру №{row['ids']}.`")
	
	msg = await complete_channel.fetch_message(int(row['id_message']))
	await msg.add_reaction('❌')
	
	embed=msg.embeds[0].copy()
	embed.add_field(name="Сообщение", value=f"{roleName} {ctx.author.mention} Отменил игру и вернул рейтинг", inline=False)
	await msg.edit(embed=embed)

@bot.command(pass_context=True)
@has_permissions(ban_members=True)
async def cancel(ctx, messages = None):
	await cancels(ctx, messages)


async def cancels(ctx, messages = None):
	
	if messages == None:
		return 0

	row = await SelectLobby(messages)
	if row == None:
		return 0
	row = [row['id_message'], row['ids'], row['id_members'], row['active']]

	if row[3] <= 1:
		pass
	else:
		return 0

	collestionlobby.update_one({"id_message": int(row[0])}, {"$set": {"active": 3}})

	channel = active_channel
	id_mess = await channel.fetch_message(int(row[0]))
	
	await id_mess.delete()

	nam = gui.get_member(int(ctx.author.id))
	roleName = get(gui.roles, id=gui.get_member(ctx.author.id).top_role.id)

	await channel_log.send(f"`{roleName} {ctx.author.name} Отменил игру №{row[1]}. {row[0]}`")
	membId = row[2]
	for i in membId:
		nam = gui.get_member(int(i))
		collestionuser.update_one({"id_member": int(i)}, {"$set": {"lobby": None}})
		await nam.send(f"`{roleName} {ctx.author.name} Отменил вашу игру №{row[1]}`")


	message = await ctx.channel.fetch_message(ctx.id)
	await message.add_reaction('✅')



		
		
@bot.command(pass_context=True)
async def cha(ctx, member: discord.Member = None, mect = None):
	channel = active_channel
	if member == None or mect == None:
		print(0)
		return 0


	user = await SelectMember(int(ctx.author.id))

	row = await SelectLobby(user['lobby'])
	row = [row['ids'], row['id_message'], row['id_leader_lobby'], row['id_members'], row['active'], row['voice_id']]
	id_message = int(row[1])
	print(row)
	if str(ctx.author.id) == str(row[2]) and  0 <= int(row[4]) <= 1:
		print(10)
		row = await SelectLobby(id_message)
		row = [row['id_members'], row['id_message']]
		member_ids = row[0]

		if str(member.id) not in member_ids:
			print(member_ids)
			print(1)
			return 0
		if 1<= int(mect) <= len(member_ids):
			pass
		else:
			print(2)
			return 0

		member_ids[member_ids.index(f"{member.id}")], member_ids[int(mect)-1] = member_ids[int(mect)-1], member_ids[member_ids.index(f"{member.id}")]

		row = await SelectLobby(id_message)
		row = [row['id_members'], row['id_message']]
		collestionlobby.update_one({"id_message": id_message}, {"$set": {"id_members": member_ids}})
		messages = await channel.fetch_message(int(row[1]))
		await UpdateLobby(messages, ctx.author.id)
		await ctx.message.add_reaction('✅')





@bot.command(pass_context=True)
async def kick(ctx, member: discord.Member = None):
	channel = active_channel

	if member == None or member == ctx.author:
		return 0


	nam = bot.get_user(int(member.id))

	user = await SelectMember(int(member.id))

	if user["lobby"] != None:
		pass


	row = await SelectLobby(user['lobby'])
	row = [row['ids'], row['id_message'], row['id_leader_lobby'], row['id_members'], row['active'], row['voice_id']]
	if str(ctx.author.id) == str(row[2]) and  0 <= int(row[4]) <= 1:
		id_message = int(row[1])
	else:
		return

	print(1)
	row = await SelectLobby(id_message)
	row = [row['id_members'], row['id_message'], row['ids']]
	member_ids = row[0]

	if str(member.id) in str(member_ids):
		del member_ids[member_ids.index(str(member.id))]

		sqliteAdd = member_ids

		collestionlobby.update_one({"id_message": id_message}, {"$set": {"id_members": sqliteAdd}})
		messages = await channel.fetch_message(int(row[1]))
		await UpdateLobby(messages, ctx.author.id)
		
		if int(row[2]) == int(user['lobby']):
			collestionuser.update_one({"id_member": int(member.id)}, {"$set": {"lobby": None}})
		await ctx.message.add_reaction('✅')
		await channel_log.send(f"`[Лобби №{row[2]}] {ctx.author} исключил {member}`")


@bot.command()
async def texst(ctx,nation, *, message:str):
	await ctx.send(f"{nation}, {message}")

@bot.command()
async def edit_text(ctx,nation, *, message:str):

	text = collestionnation.find_one({'name' : nation})

	if text == None:
		await ctx.send("Нация не найдена")
		return

	collestionnation.update_one({"name": nation}, {"$set": {"text": message}})

	await ctx.send(f'[{nation}][Изменение описания бонуса нации]\nПрошлый: {text["text"]}\n\nНовый: {message}')


@bot.command()
async def text(ctx,nation, *, message:str):
	collestionnation.update_one({"name": nation}, {"$set": {"text": message}})


@bot.command(pass_context=True)
async def set(ctx, ids = None, moves = None):
	if ids == None or moves == None:
		return 0

	row = collestionlobby.find_one({'ids' : int(ids)})
	if row == None:
		return 0

	if row['active'] == 2:
		pass
	else:
		return 0

	if str(ctx.author.id) in row['id_members']:
		collestionlobby.update_one({"id_message": int(row['id_message'])}, {"$set": {"moves": int(moves)}})

		channel = active_channel
		id_mess = await complete_channel.fetch_message(int(row['id_message']))


		msg = await complete_channel.fetch_message(int(row['id_message']))
		embed=msg.embeds[0].copy()
		embed.set_field_at(4, name='Ходов', value=f'{moves}', inline=False)
		#print(embed.fields[4])

		await msg.edit(embed=embed)

		await ctx.message.add_reaction('✅')
		nam = gui.get_member(int(ctx.author.id))
		roleName = get(gui.roles, id=gui.get_member(ctx.author.id).top_role.id)

		await channel_log.send(f"`[Лобби №{row['ids']}] {nam} Поставил кол во ходов равное {moves}`")




@slash.slash(name="editdb",
			 description="Редактирования базы данных.",
			 options = [create_option(
				 name="Категория",
				 description="выбор",
				 option_type=3,
				 required=True,
				 choices=[
				  create_choice(
					name="Кол-во сообщений",
					value="messages"
				  ),
				  create_choice(
					name="Запрет на бота",
					value="mutes"
				  ),
				  create_choice(
					name="Кол-во п  обед",
					value="wins"
				  ),
				  create_choice(
					name="Рейтинг",
					value="raiting"
				  ),
				  create_choice(
					name="Кол-во игр",
					value="games"
				  ),
				  create_choice(
					name="Время в голосовом канале",
					value="voicetime"
				  )]
				 ),
				 create_option(
				 name="Значение",
				 description="Новое значение.",
				 option_type=3,
				 required=True),

				 create_option(
				 name="Пользователь",
				 description="Пользователь у которого изменить",
				 option_type=6,
				 required=True)],


			 guild_ids=guild_ids)
@has_permissions(ban_members=True)
async def editDB(ctx, категория: str, значение: str, пользователь: discord.Member):
	#nam = gui.get_member(int(user_id))

	collestionuser.update_one({"id_member": пользователь.id}, {"$set": {категория: int(значение)}})
	await ctx.send(f"обновлено значения в базе данных у {пользователь}")

	if категория == "raiting":
		await setrating(ctx, пользователь, int(значение))
#    await ctx.message.add_reaction('✅')

@bot.command()
async def top(ctx, count, categ, srt = -1):
	#nam = gui.get_member(int(user_id))
	rows = collestionuser.find(limit=int(count)).sort(categ, int(srt)) 

	text = ""
	counts = 0
	for i in rows:
		counts += 1
		nam = gui.get_member(int(i['id_member']))
		text += f"{counts}:{nam} = {i[categ]}\n"
		if counts == int(count):
			break
		
	
	await ctx.send(text)


@bot.command(pass_context=True)
@has_permissions(ban_members=True)
async def addmember(ctx, messages, member: discord.Member):
	await addmembers(ctx, messages, member)
	

async def addmembers(ctx, messages, member: discord.Member):


	row = await SelectLobby(messages)
	if row == None:
		return 0
	row = [row['id_message'], row['ids'], row['id_members'], row['active']]

	if row[3] <= 1:
		pass
	else:
		return 0
	messages = await active_channel.fetch_message(row[0])

	await MemberReaction(messages, member.id, str(ctx.author))

	try:
		message = await ctx.channel.fetch_message(ctx.id)
	except: message = await ctx.channel.fetch_message(ctx.message.id)
	await message.add_reaction('✅')


@bot.command()
async def ccc(ctx):

	roleMember = get(gui.roles, id=gui.get_member(int(ctx.author.id)).top_role.id).position
	await ctx.send("https://prntscr.com/1ilgui3")



@bot.command()
@has_permissions(ban_members=True)
async def update(ctx):
	channel = bot.get_channel(609697373421305876)
	id_mess = await channel.fetch_message(616284559872622592)
	roleORG = get(ctx.guild.roles, name="Организатор")
	roleBAR = get(ctx.guild.roles, name="Варвар")
	text = f"""@everyone 
!!!ЗА НЕСОБЛЮДЕНИЕ ПРАВИЛ ВЫ ПОЛУЧАЕТЕ роль {roleBAR.mention}
1. Не ливаем до потери столицы или по согласованию с остальными игроками
2. Не копим учёных (кроме тех случаев, когда ведёте его сажать в академию)
3. Не шифтим 
4. Первый рестарт - больше половины голосов "за" до 10 хода включительно (4 голоса при FFA 6)
5. Войну можно объявлять до первой половины таймера
6. Высадка парашютистами/XCOM'ами во время войны только в ПЕРВОЙ половине таймера (исключение : свои границы)
7. Не захватывать гг через война/мир
8.Деньги с эльдорадо в поселенца и удаляем.
9. Передача городов другим игрокам запрещена. Разрешено передать только во время подписания мирного договора.
			-Разрешено "освобождение" захваченных городов. Условия: город передается игроку, ранее владевшему им; объявление войны во избежание отброса чьих либо войск за границы (юниты, находившиеся на территории по условиям открытых границ не учитываются)
10. Запрещено захватывать ГГшку и передавать другому игроку для "освобождения" (можно передать через 50 ходов, если до захвата она была нейтральная)
11. Запрещен двойной буст в виде грабежей караванов друг друга, и раздел денег между сторонами
12. Запрещено чинить улучшения после грабежа вражеских и нейтральных клеток с целью разграбить снова (абуз голды)
13. Запрещено захватывать ГГшку, если у вас мирный договор с её союзником
14. Устные договора нерушимы (пример : не воюем на фрегатах, ядерном оружии и прочие). Объявить об этом в игровой чат.
15. При голосовании за мирового лидера (ООН) державы могут отдавать голоса только В ПОЛЬЗУ СЕБЯ САМИХ! (FFA ONLY)
16. Не трейдиться с ботом, караваны можно пускать (Только мир/война, границы, посольство)
17. ученых с Хаббла только сажать
18. {roleORG.mention} может выдавать наказания даже за те случаи, которые не упоминаются в пунктах выше
19. Откаты запрещены. Только если кто то вылетел.
20. 1 клик на прогрузе.
21. Запрещены военные действия в конце таймера( Генералы в т.ч)"""
	await id_mess.edit(content=text)





@slash.slash(name="info",
			 description="Статистика",
			 options = [create_option(
				 name="Пользователь",
				 description="Ид/@/ник.",
				 option_type=6,
				 required=False
				 )],
			 guild_ids=guild_ids)
@bot.command()
async def info(ctx, пользователь: discord.Member = None):
	await infos(ctx, пользователь)



async def infos(ctx, пользователь: discord.Member = None):

	emojiRait = "<:swordX:619211942887817236>"
	emojwin = "<:win:818703294641733644>"
	if пользователь == None:
		пользователь = ctx.author

	embed = discord.Embed(title=f"Информация о пользователе", color=random.randint(0, 0xffffff))

	use = await SelectMember(пользователь.id)


	embed.add_field(name="🌎 Ник", value=пользователь.name, inline=True)

	rows = collestionuser.find().sort("rating.0", -1)


	count = 1
	text = ""
	for row in rows:
		if str(row['id_member']) == str(пользователь.id):
			if count == 1:
				text = "🏆 "+str(count)
			elif count == 2:
				text = "🥈 "+str(count)
			elif count == 3:
				text = "🥉 "+str(count)
			break

		count += 1
		text = "🔰 "+str(count)
	embed.add_field(name=f"🛡️ Место", value=text, inline=True)

	embed.add_field(name="\u200b", value="\u200b", inline=True)
	try:
		embed.add_field(name=f"{emojiRait} Победы", value=f"{use['wins']} ({round((use['wins']/use['games']) * 100)}%)", inline=True)
	except:
		embed.add_field(name=f"{emojiRait} Победы", value=f"{use['wins']}", inline=True)
	embed.add_field(name=f"{emojwin}  Рейтинг", value=f"{use['rating'][0]}", inline=True)


	minVoic = use['VoiceTime']/60

	#embed.add_field(name=f"⏲️ В голосовом", value=f"{use['VoiceTime']}С|{round(minVoic, 1)}М|{round(minVoic/60, 1)}Ч", inline=False)

	embed.add_field(name="\u200b", value="\u200b", inline=True)
	embed.set_footer(text=f"Игр: {use['games']}")

	try:
		await ctx.channel.send(embed=embed)
	except:
		await ctx.send(embed=embed)

@bot.command(pass_context=True)
async def UploadDB(ctx):
	await ctx.send(file=discord.File(r'Discord.db'))


@bot.command()
async def tu(ctx, member: discord.Member = None):

	if member == None:
		member = ctx.author
	user = await SelectMember(member.id)
	await ctx.send(user)
	await ctx.send(user["messages"])

@bot.command()
async def tj(ctx):

	for member in collestionuser.find():
		collestionuser.update_one({"id_member": member['id_member']}, {"$set": {"rating": [1000, 50, 1000, 50]}})
		collestionuser.update_one({"id_member": member['id_member']}, {"$set": {"wins": 0}})
		collestionuser.update_one({"id_member": member['id_member']}, {"$set": {"games": 0}})
		collestionuser.update_one({"id_member": member['id_member']}, {"$set": {"lobby": None}})

	await ctx.send("+")



	
	


'''@bot.command()
async def dbtransfer(ctx):
	channel = bot.get_channel(608546051649175562)
	await cursor.execute("SELECT * FROM users")
	usersDB = await cursor.fetchall()
	count = 0
	await channel.send(f"{count}|{len(usersDB)}")
	for i in usersDB:
		collestionuser.insert_one({"id_member": i[0], "messages": i[1], "joins": i[2], "mutes": i[3], "wins": i[4], "rating": i[5], "games": i[6], "VoiceTime": 0, "LastVoice": i[8], "LastMessage": i[9]})
		count += 1

		if count % 100 == 0:
			await channel.send(f"{count}|{len(usersDB)}")
	await channel.send(f"{count}|{len(usersDB)} +")'''


async def createDb():
	memList = await gui.fetch_members(limit=1000).flatten()

	for member in memList:
		dsa = await SelectMember(member.id)
		if dsa==None:
			collestionuser.insert_one({"id_member": member.id, "messages": 0, "joins": 1, "mutes": 0, "wins": 0, "rating": [1000, 50, 1000, 50
				], "games": 0, "VoiceTime": 0, "LastVoice": "None", "LastMessage": "None", "lobby": None})
		else:
			pass


bot.run("NjE2MjU3OTEyNzc5NzAyMzMz.XWZ85w.A1snc5zDOVMTfTGqmsK8jlZzFGU")

#ioloop = asyncio.get_event_loop()
#ioloop.run_until_complete(createDb())
#ioloop.run_until_complete(GetNamBot())
