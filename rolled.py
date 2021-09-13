from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps
import random
from pymongo import MongoClient

cluster = MongoClient(f"mongodb+srv://root:discordGPT@cluster0.ej8oe.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

db = cluster['discord']
collestionnation = db["nation"]




def nick_roll(nick, nomer):
	nick = nick

	img = Image.open(f"./back/back_nick.jpg").convert("RGBA").resize((512, 128))
	idraw = ImageDraw.Draw(img)

	font = ImageFont.truetype("arial.ttf", size=30)

	# рисуем по полям
	idraw.rectangle((0, 0, 511, 127), outline=(0, 0, 0))

	idraw.text((10, 10), f"({nomer})", "black", font=font)  # номер игрока

	nicksize = 210


	font = ImageFont.truetype("arial.ttf", size= round(32 - len(nick) / 5))
	#print(round(30 - len(nick) / 5))

	nicksize = 250 - (len(nick) * 7 - (round(len(nick) / 5) * 6))
	
	idraw.text((nicksize, 45), nick, "black", font=font)  # никнейм
	return img


def nation_roll(country):
	count = 1

	img = Image.open(f"./back/back.jpg").convert("RGBA").resize((512, 128))
	idraw = ImageDraw.Draw(img)
	# иконки
	flag = Image.open(f"./nation/{country}/flag.png").resize((90, 90))
	leader = Image.open(f"./nation/{country}/leader.png").resize((80, 80))
	# flag = ImageOps.fit(Image.open(f'./{country}/flag.png'), (90,90), Image.ANTIALIAS)
	icon_1 = Image.open(f"./nation/{country}/unit_1.png").resize((55, 55))
	# icon_1 = ImageOps.fit(Image.open(f'./{country}/unit_1.png'), (55,55), Image.ANTIALIAS)
	icon_2 = Image.open(f"./nation/{country}/unit_2.png").resize((55, 55))

	
	nat_bon = collestionnation.find_one({'name' : country})
	bonus_text = str(nat_bon['text']) # загрузка из базы данных


	font = ImageFont.truetype("verdana.ttf", size=30)
	font_country = ImageFont.truetype("arial.ttf", size=20)
	font_text = ImageFont.truetype("arial.ttf", size=15)

	# рисуем по полям
	idraw.rectangle((0, 0, 511, 127), outline=(0, 0, 0))

	if len(country) >= 10:
		font_country = ImageFont.truetype("arial.ttf", size=15)
		idraw.text((10, 10), country, "black", font=font_country)

	else:
		idraw.text((15, 10), country, "black", font=font_country)

	idraw.text((230, 128 - 85), bonus_text, "black", font=font_text)

	img.paste(flag, (10, 128 - 95), flag)
	img.paste(icon_1, (110, 128 - 125), icon_1)
	img.paste(icon_2, (110, 128 - 60), icon_2)
	img.paste(leader, (150, 128 - 105), leader)
	return img


def roll_image(nick, count_nation, nomer, *country):
	country = list(country[0])

	img = Image.new("RGBA", (512, 128*(count_nation+1)), "white")
	idraw = ImageDraw.Draw(img)

	user = nick_roll(nick, nomer)
	img.paste(user, (0, 0), user)


	for i in range(count_nation):
		roll_nation = nation_roll(country[i])
		img.paste(roll_nation, (0, user.size[1] * (i+1)), roll_nation)

	return img


def rolls(nick, count_nation, *nation):
	
	nation = list(nation[0])
	nick = list(nick)
	#print(nation[0])

	ele = {4: {"floors": 2},
	6: {"floors": 2},
	8: {"floors": 2},
	9: {"floors": 3},
	10: {"floors": 2},
	12: {"floors": 3}}

	if len(nick) in ele:
		width = int(len(nick) / ele[len(nick)]['floors']) # наций на одном этаже
		lis = ele[len(nick)]['floors'] # этажей


	else:
		width = len(nick)
		lis = 1

	img = Image.new("RGBA", (width * 512, (128 * (count_nation + 1)) * lis), "white")
	idraw = ImageDraw.Draw(img)


	count = 1
	for q in range(lis):

		for i in range(width):

			nation_random = []
			for ds in range(count_nation):

				country_random = random.choice(nation)
				nation.pop(nation.index(country_random))
				nation_random.append(country_random)

			imageroll = roll_image(nick[count - 1], count_nation, count, nation_random)
			img.paste(imageroll, (i * imageroll.size[0], imageroll.size[1] * q), imageroll)
			count += 1

	return img



def roll(nick, count_nation, *nation):

	"""
	:nick: list массив ников для вставки под ник
	:count_nation: int Кол во наций для ролла
	:nation: list Нации для выбора
	"""

	img = rolls(nick, int(count_nation), nation[0])

	img = img.resize((img.size[0], img.size[1]))

	img.save("deathl0x.png")


#roll(["merka#7144", "Falsite#3123", "dsad", "4fdsf", "mmeerrkkaa", "vmekrkaaaadsadasdas"], 1, ["Америка", "Китай", "Дания", "Германия", "Египет", "Индия"])

