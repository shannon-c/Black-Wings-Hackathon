import discord
import os
from discord.ext import commands
from collections import defaultdict
from discord.utils import get
import random
import string

users_warning = defaultdict(int)

powerfulWomen_link = ["https://motivationalspeakersagency.co.uk/news/50-women-who-are-changing-the-world-today", "https://www.forbes.com/power-women/list/", "https://www.nationalgeographic.com/culture/2019/10/why-the-future-should-be-female-feature/", "https://www.usatoday.com/story/money/2019/03/16/inventions-you-have-women-inventors-thank-these-50-things/39158677/"]

negatives = ["dont", "cannot", "not", "no"]

status = "go"

################## ML preprocessing ######################
from gensim.parsing.preprocessing import remove_stopwords
import joblib
vectorizer = joblib.load("vectorizer.pkl")
model = joblib.load("anti_sexist_model.pkl")

def preprocess(text):
  """
  remove stopwords, whitespace, and make the sentence lowercase, tokenize
  """
  text = text.lower()
  text = text.replace('[^\w\s]',' ')
  text = text.replace('\s\s+', ' ')
  text = text.translate(str.maketrans('', '', string.punctuation))
  text = remove_stopwords(text)
  tokenized_text = text.split()
  print(text)
  text = vectorizer.transform(tokenized_text)
  
  return text


##########################################################

################# Chatbot training #######################
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

my_bot = ChatBot(name='PyBot', logic_adapters = [{
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': 'I am sorry, but I do not understand.',
            'maximum_similarity_threshold': 0.90
        }])

list_trainer = ListTrainer(my_bot)
list_trainer.train(
    [
    #  intro
     "hi", "Hello", 
     "hello", "Hello!", 
     'who are you', 'I am a discord bot that promote women empowerment and support https://media.giphy.com/media/AhgTQq3PvpvpXixbiD/giphy.gif',
    #  get help (crime-related)
     'where can i get women support', 'You are not alone. Here are some of your options https://www.womensaid.org.uk/ and https://www.bwss.org/support/', 
     'i am harassed', 'You are not alone. Here are some of your options if you’re experiencing harrasement https://stopstreetharassment.org/our-work/nationalshhotline/',
     'i experience violence', 'You are not alone, help is on the way. Here are some of your options if you are experiencing domestic violence https://www.womensaid.org.uk/ and https://avda-tx.org/',
     'i experience harrasment', 'You are not alone.Help is on the way. Here are some of your options if you are experiencing sexual harrasment https://www.victimsupport.org.uk/crime-info/types-crime/sexual-harassment and https://au.reachout.com/articles/sexual-assault-support',
    #  self improvement
     'i want to excercise', 'Try some pushups. Up and down! https://media.giphy.com/media/3ohhwElB92YQv0igda/giphy.gif',
     'do you have exercise recommendations?', 'Stretch your legs! https://media.giphy.com/media/J6Vhh4HWrTAxWjw2co/giphy.gif', 
     'i want to get healthier', 'Stretch your legs! https://media.giphy.com/media/J6Vhh4HWrTAxWjw2co/giphy.gif',
     'how can I get healthier?', 'Stretch your legs! https://media.giphy.com/media/J6Vhh4HWrTAxWjw2co/giphy.gif',
    #  mental health support (discrimination)
     'i am not worthy of love', 'You are beautiful as always, and I am here for you. https://media.giphy.com/media/3o7btREha9GkGtgJKo/giphy.gif',
     'it is a bad day. i need some encouragement', 'https://media.giphy.com/media/3o7btREha9GkGtgJKo/giphy.gif',
     'i am sad', 'I have no words... But I want you to know I love you and am here for you. https://media.giphy.com/media/2UIcmK4pn7rYNLRboG/giphy.gif',
     'i am feeling down', 'I have no words... But I want you to know I love you and am here for you. https://media.giphy.com/media/2UIcmK4pn7rYNLRboG/giphy.gif',
     'i am stressed.', 'Hey! Are you okay? What is the problem? School, work, relationships? I am all ears. https://media.discordapp.net/attachments/803257943645880323/805302433390788648/giphy_5.gif',
     'everything has been so messed up.', 'Hey! Are you okay? What is the problem? School, work, relationships? I am all ears. https://media.discordapp.net/attachments/803257943645880323/805302433390788648/giphy_5.gif',
     'it is not getting better',  'Things have a way of working themselves out. I will always be there for you. <3',
     ])


##########################################################


# class MyClient(discord.Client):

#   async def on_ready(self):
#       print('Logged on as', self.user)

#   async def on_message(self, message):
#       word_list = ['sexual', 'sexist', 'violence', 'abuse', 'weak', 'racist', 'racism', 'harassment']

#       # don't respond to ourselves
#       if message.author == self.user:
#           return

#       messageContent = message.content
#       if len(messageContent) > 0:
#           for word in word_list:
#               if word in messageContent:
#                   await message.channel.send('Do not say that!')

# client = MyClient()
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print('Logged in as' + bot.user.name)


@bot.event
async def on_member_join(member):
  print("A user joined your server!")
  await member.send("Welcome to the server https://media.giphy.com/media/AhgTQq3PvpvpXixbiD/giphy.gif \n Please adhere to the community guidelines: No sexist comments.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
      return

    mssg_author = message.author.id
    
    response = my_bot.get_response(message.content)
    print(response)
    default_res = my_bot.get_response("Light up!!!")
    if response.text!= default_res.text:
      await message.channel.send(response)

    processed_mssg = preprocess(message.content)
    print(model.predict(processed_mssg))
    prediction = model.predict(processed_mssg).tolist()
    if len(prediction)>2 and (prediction.count(1)>=len(prediction)/2):
      print(prediction.count(1))
      print(len(prediction)//2)
      users_warning[mssg_author] += 1
      global status
      status = "go"
      for negative in negatives:
       if negative in message.content:
         status = "no"
         return status
      
      if (status == "go"):
        print(mssg_author)
        await message.channel.send('Warning:  ' + str(users_warning[mssg_author]) + '\nThat could be a gender discrimination, try reading this article on powerful women \n'+ powerfulWomen_link[random.randint(0,len(powerfulWomen_link))-1])
        if users_warning[mssg_author]>5:
          target = await bot.fetch_user("784665364469907467")
          user = await bot.fetch_user(mssg_author)
          await target.send("User " + user.name + " has more than 5 warnings, and has posed threats to the channel.\n Suggested Actions: !kick @userid or !ban @userid.")
        return status
      
      #await message.channel.send('Hey that is not true and rude, try reading this article on powerful women '+ powerfulWomen_link[random.randint(0,len(powerfulWomen_link))-1])


 
    # if message.content.startswith('hello'):
    #   await message.channel.send('Hello!')
    # if message.content.startswith('I am harrased'):
    #   await message.channel.send('You are not alone. Here are some of your options if you’re experiencing harrasement https://stopstreetharassment.org/our-work/nationalshhotline/')
    # if message.content.startswith('excercise'):
    #   await message.channel.send('Try some pushups. Up and down! https://media.giphy.com/media/3ohhwElB92YQv0igda/giphy.gif')
    # if message.content.startswith('compliment me'):
    #   await message.channel.send('https://media.giphy.com/media/3o7btREha9GkGtgJKo/giphy.gif')
    # if message.content.startswith('Who are you'):
    #   await message.channel.send('I am a discord bot that promote women empowerment and support https://media.giphy.com/media/AhgTQq3PvpvpXixbiD/giphy.gif')
    # if message.content.startswith('where can i get women support'):
    #   await message.channel.send('You are not alone. Here are some of your options https://www.womensaid.org.uk/ and https://www.bwss.org/support/')
    # if message.content.startswith('excercise recommendations'):
    #   await message.channel.send('Stretch your legs! https://media.giphy.com/media/J6Vhh4HWrTAxWjw2co/giphy.gif')
    # if message.content.startswith('i experience sexual harrasment'):
    #   await message.channel.send('You are not alone.Help is on the way. Here are some of your options if you are experiencing sexual harrasment https://www.victimsupport.org.uk/crime-info/types-crime/sexual-harassment and https://au.reachout.com/articles/sexual-assault-support')
    # if message.content.startswith('i am sad'):
    #   await message.channel.send('I have no words... But I want you to know I love you and am here for you. https://media.giphy.com/media/2UIcmK4pn7rYNLRboG/giphy.gif')
    # if message.content.startswith('quote'):
    #   await message.channel.send('https://media.giphy.com/media/cbbfhBEtLpIFvq2PUj/giphy.gif')
    # if message.content.startswith('i experience domestic violence'):
    #   await message.channel.send('You are not alone, help is on the way. Here are some of your options if you are experiencing domestic violence https://www.womensaid.org.uk/ and https://avda-tx.org/') 
    # if message.content.startswith('i am stressed. Everything is going bad'):
    #   await message.channel.send('Hey! Are you okay? You sound stressed. What is the problem? School, work, relationships? https://media.discordapp.net/attachments/803257943645880323/805302433390788648/giphy_5.gif')

    word_list = ['sexual', 'sexist', 'violence', 'abuse', 'weak', 'racist', 'racism', 'harassment']

    messageContent = message.content
    if len(messageContent) > 0:
        for word in word_list:
            if word in messageContent:
                await message.channel.send('Do not say that!')
    
    if message.content.startswith('where can i get education recources'):
      await message.channel.send('Here is a good website to learn various subjects https://www.khanacademy.org/')
      
    # if message.content.startswith('Women are useless'):
    #   await message.channel.send('That is not true, here are some women that are influencing the world https://motivationalspeakersagency.co.uk/news/50-women-who-are-changing-the-world-today')
    if message.content.startswith('i am looking for a job'):
      await message.channel.send('Based on your request, here are some useful links https://careers.google.com/jobs/results/')
    if message.content.startswith("I want to learn coding"):
          await message.channel.send('Here is a free course for you https://www.w3schools.com/ https://www.freecodecamp.org/')
    
    await bot.process_commands(message)




# test if command is working (command: !ping)
@bot.command()
async def ping(ctx):
	await ctx.channel.send("pong")

# kick command
@bot.command()
async def kick(ctx, member : discord.Member, *, reason=None):
  await member.kick(reason=reason)
  await ctx.send(f'User {member} has been kicked.')

# ban command
@bot.command()
async def ban(ctx, member : discord.Member, *, reason=None):
  await member.ban(reason=reason)




bot.run(os.getenv ('TOKEN') )
