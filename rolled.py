# -*- coding: utf-8 -*-
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps
import random



def text_size(text, font):
    width = font.getmask(text).getbbox()[2]
    height = font.getmask(text).getbbox()[3]
    return (width, height)





size = [512, 152]
size_nick = [0, 120]

font = ImageFont.truetype("./civa.ttf", 28, encoding="unic")


def nick_roll(nick, nomer):
	nick = nick

	img = Image.open(f"./back/back_nick.jpg").convert("RGBA").resize((512, size_nick[1]))

	idraw = ImageDraw.Draw(img)

	font = ImageFont.truetype("arial.ttf", size=30)

	# рисуем по полям
	idraw.rectangle((0, 0, 511, size[1] - 1), outline=(0, 0, 0))

	idraw.text((10, 10), f"({nomer})", "black", font=font)  # номер игрока

	nicksize = 210


	font = ImageFont.truetype("Pon.ttf", size= round(40 - len(nick) / 7), encoding="UTF-8")
	#print(round(30 - len(nick) / 5))

	nicksize = 250 - (len(nick) * 7 - (round(len(nick) / 5) * 6))

	nicksize = 250 - (len(nick) - (len(nick)) // 2) * 22
	
	
	txt_width, txt_height = text_size(nick, font)

#	draw_text = ImageDraw.Draw(image)
	idraw.text((int(img.size[0]/2 - txt_width/2), int(img.size[1]/2 - txt_height/2) - 2), nick, font=font, fill=('#000000'))

	
	#idraw.text((nicksize, 45), nick, "black", font=font)  # никнейм
	return img


def nation_roll(country):
	count = 1

	img = Image.open(f"./back/back.jpg").convert("RGBA").resize((512, size[1]))
	#img = Image.open(f"./merka.jpg").convert("RGBA").resize((512, size[1]))
	idraw = ImageDraw.Draw(img)
	# иконки
	flag = Image.open(f"./nation/{country}/flag.png").resize((105, 105))
	leader = Image.open(f"./nation/{country}/leader.png").resize((105, 105))
	icon_1 = Image.open(f"./nation/{country}/unit_1.png").resize((80, 80))
	
	icon_2 = Image.open(f"./nation/{country}/unit_2.png")

	if icon_2.size[0] == 188:

		icon_2 = icon_2.resize((55, 55))

		icon_2.resize((icon_2.size[0] + 110, icon_2.size[1] + 110))
		width = 5
	else:
		width = 0
		icon_2 = icon_2.resize((80, 80))



	#font_country = ImageFont.truetype("arial.ttf", size=50)
	font_text = ImageFont.truetype("arial.ttf", size=25)

	# рисуем по полям
	idraw.rectangle((0, 0, 511, size[1] - 1), outline=(0, 0, 0))

	font_country = ImageFont.truetype("arial.ttf", size=65 - ((len(country)) // 2) * 5,encoding='UTF-8',)

	txt_width, txt_height = text_size(country, font_country)

#	draw_text = ImageDraw.Draw(image)
	idraw.text((int(img.size[0]/2 - txt_width/2) - 50, int(img.size[1]/2 - txt_height/2) - 4), country, font=font_country, fill=('#000000'))



#	if len(country) == 3:
#		idraw.text((150, 50), country, "black", font=font_country)
#	else:
	#	idraw.text((150 - (len(country) - (len(country)) // 2) * 11, 50), country, "black", font=font_country)
	'''if len(country) >= 10:
		font_country = ImageFont.truetype("arial.ttf", size=45)
		idraw.text((100, 50), country, "black", font=font_country)

	else:
		idraw.text((150, 50), country, "black", font=font_country)'''



	img.paste(flag, (400, size[1] - 133), flag)
	img.paste(leader, (310, size[1] - 130), leader)

	img.paste(icon_1, (7, size[1] - 155), icon_1)
	img.paste(icon_2, (7 + width * 2, size[1] - 80 + width), icon_2)
	


	return img


def roll_image(nick, count_nation, nomer, *country):
	country = list(country[0])
	user = nick_roll(nick, nomer)
	
	img = Image.new("RGBA", (512, user.size[1]+size[1]*(count_nation)), "white")
	idraw = ImageDraw.Draw(img)

	
	img.paste(user, (0, 0), user)


	for i in range(count_nation):
		roll_nation = nation_roll(country[i])
		img.paste(roll_nation, (0, user.size[1] + size[1] * (i)), roll_nation)

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
	print(size_nick)
	img = Image.new("RGBA", (width * 512, ((size[1] * count_nation + size_nick[1]) * lis)), "white")
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

	img.save("de.png")


roll(["merka#7144", "Проверим", "fsdfgds", "dsaf", "mefdsfmmsdfkdkgf", "дез"], 3, ['Америка','Голландия', 'Вавилон', 'Испания', 'Кельты', 'Австрия','Япония', 'Индонезия', 'Персия', 'Майя', 'Англия', 'Византия', 'Сонгай', 'Россия', 'Рим', 'Польша', 'Франция', 'Китай', 'Швеция', 'Карфаген', 'Греция', 'Индия', 'Сиам', 'Бразилия', 'Египет', 'Шошоны', 'Турция', 'Корея', 'Зулусы', 'Марокко', 'Аравия', 'Полинезия', 'Инки', 'Дания', 'Ассирия', 'Монголия', 'Ирокезы', 'Эфиопия', 'Ацтеки', 'Португалия', 'Германия'])


['Америка','Голландия', 'Вавилон', 'Испания', 'Кельты', 'Австрия','Япония', 'Индонезия', 'Персия', 'Майя', 'Англия', 'Византия', 'Сонгай', 'Россия', 'Рим', 'Польша', 'Франция', 'Китай', 'Швеция', 'Карфаген', 'Греция', 'Индия', 'Сиам', 'Бразилия', 'Египет', 'Шошоны', 'Турция', 'Корея', 'Зулусы', 'Марокко', 'Аравия', 'Полинезия', 'Инки', 'Дания', 'Ассирия', 'Монголия', 'Ирокезы', 'Эфиопия', 'Ацтеки', 'Португалия', 'Германия']

