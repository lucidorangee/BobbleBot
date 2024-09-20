import os
import discord, random
from discord.ext import commands, tasks
import uuid
from dotenv import load_dotenv
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import pillow_heif
from PIL import Image
import asyncio
from datetime import datetime, timezone


load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

gauth = GoogleAuth()

gauth.LoadCredentialsFile("driveCredentials.txt")

if gauth.credentials is None:
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    gauth.Refresh()
else:
    gauth.Authorize()

drive = GoogleDrive(gauth)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    channel = await client.fetch_channel('1197804901082877994')
    await channel.send("Channel Check")
    msg1.start()

@tasks.loop(hours=168)
async def msg1():
    channel_id = int(os.getenv('WEEKLY_MESSAGE_CHANNEL_ID'))
    channel = await client.fetch_channel(channel_id)
    message = await channel.send("Weekly Bubble!")
    await showPhoto(message)

@msg1.before_loop
async def before_msg1():
    for _ in range( (60*60*24*7) // 30):  # loop
        if datetime.today().weekday() == 3 and datetime.now(timezone.utc).hour == 9+12 and datetime.now(timezone.utc).minute == 44:  # 24 hour format
            print('It is time')
            return
        await asyncio.sleep(30)


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if isinstance(message.channel,discord.DMChannel):
        if(str(message.author.id) == os.getenv('TWICESTAN_ID')):
            if(message.attachments == []):
                await message.channel.send("Hello Maxi! :3\nI don't have any chat functions, sorry!\nBut if you attach any photos, I will keep them to show the 44s!")
            else:
                await uploadPhotos(message)
        else:
            await message.channel.send("This is a DM from " + str(message.author.id))

    elif message.content.startswith('$time'):
        await message.channel.send(("Current time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    elif message.content.startswith('$hello'):
        if(str(message.author.id) == os.getenv("ORANGE_ID")):
            await message.channel.send('Hello')    
        elif(str(message.author.id) == os.getenv('TWICESTAN_ID')):
            await message.channel.send('hi :3')
        elif(str(message.author.id) == os.getenv('CHU_ID')):
            await message.channel.send('안녕~ :3')
        elif(str(message.author.id) == os.getenv('RACCOON_ID')):
            await message.channel.send('Hi racmid...')
        elif(str(message.author.id) == os.getenv('MACHI_ID')):
            await message.channel.send('Machister!')
        elif(str(message.author.id) == os.getenv('LINE_ID')):
            await message.channel.send('Whooo?')
        elif(str(message.author.id) == os.getenv('MIKU_ID')):
            await message.channel.send('Mikuster!')
        elif(str(message.author.id) == os.getenv('MISO_ID')):
            await message.channel.send('Misomer~')
        elif(str(message.author.id) == os.getenv('DAISUKI_ID')):
            await message.channel.send('Daister~')
        else:    
            await message.channel.send('Hello~')

    elif message.content.startswith('$upload'):
        if(str(message.author.id) == os.getenv('TWICESTAN_ID')):
            await uploadPhotos(message)
        else:
            await message.channel.send('Sorry, my drive is only for Bubble :c')
    
    elif message.content.startswith('$random'):
        if str(message.author.id) != os.getenv('TWICESTAN_ID') and str(message.author.id) != os.getenv('ORANGE_ID'):
            await message.channel.send("Only thing I show you is no mercy! :D")
            return

        await showPhoto(message)

async def showPhoto(message):
    file_list = drive.ListFile({'q': "\'" +  os.getenv('DRIVE_FOLDER_ID') + "' in parents and trashed=false"}).GetList()
    index = random.randint(0, len(file_list) - 1)
    file6 = drive.CreateFile({'id': file_list[index]['id']})
    ext = file6['title'].lower()
    if ext.endswith('png'):
        ext = 'png'
        file6.GetContentFile('temp.' + ext)
    elif ext.endswith('jpg'):
        ext = 'jpg'
        file6.GetContentFile('temp.' + ext)
    elif ext.endswith('jpeg'):
        ext = 'jpeg'
        file6.GetContentFile('temp.' + ext)
    elif ext.endswith('heic'):
        pillow_heif.register_heif_opener()
        file6.GetContentFile('temp.heic')
        img = Image.open('temp.heic')
        img.save('temp.png', format('png'))
        os.remove('temp.heic')
        ext = 'png'
    else:
        await message.channel.send(content='```ERROR HAS OCCURRED WHILE LOADING FILE; FILE NAME: ' + ext +'```')
        return
    
    file=discord.File('temp.' + ext)
    await message.channel.send(file=file, content='Tada! You rolled ' + str(index) + ' from 0 to ' + str(len(file_list) - 1) + "!")
    os.remove("temp." + ext)

async def uploadPhotos(message):
    if message.attachments == []:
            return
        
    file_list = drive.ListFile({'q': ("\'" + os.getenv('DRIVE_FOLDER_ID') + "' in parents and trashed=false")}).GetList()
    for attachment in message.attachments:
        ext = ""
        if attachment.filename.lower().endswith('png'):
            ext = "png"
        elif attachment.filename.lower().endswith('jpg'):
            ext = "jpg"
        elif attachment.filename.lower().endswith('jpeg'):
            ext = "jpeg"
        elif attachment.filename.lower().endswith('heic'):
            ext = "heic"
        else:
            await message.channel.send("the url is " + str(attachment.filename.lower()))
            continue

        await attachment.save(fp=("temp." + ext))
        await message.channel.send('Downloaded!')

        id = str(uuid.uuid4()) + "." + ext
        while any(file['title'] == id for file in file_list):
            id = str(uuid.uuid4()) + "." + ext
        

        metadata = {
            'parents': [
                {"id": os.getenv('DRIVE_FOLDER_ID')}
            ],
            'title': id,
            'mimeType': ('image/' + ext)
        }

        file = drive.CreateFile(metadata)
        file.SetContentFile("temp." + ext)
        file.Upload()
        os.remove("temp." + ext)
        await message.channel.send('Uploaded!')

client.run(os.getenv('TOKEN_ID'))