import random

DESSERTS = [
   "달고나",
   "솜사탕",
   "찹쌀떡",
   "붕어빵",
   "꿀호떡",
   "딸기잼",
   "꿀사과",
   "바나나",
   "민들레",
   "강아지",
   "고양이",
   "별사탕",
   "구름빵",
   "파스텔",
   "무지개",
   "초록빛",
   "파랑새",
   "은하수",
   "보라빛",
   "바닐라",
   "풍선껌",
   "종이컵",
   "토끼풀",
   "별토끼",
   "다람쥐",
   "강낭콩"
]

def generate_nickname():
   base = random.choice(DESSERTS)
   number = str(random.randint(10, 99))
   return base + number