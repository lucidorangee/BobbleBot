import os
import discord, random
import uuid
from dotenv import load_dotenv
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

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
gauth.SaveCredentialsFile("driveCredentials.txt")

drive = GoogleDrive(gauth)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

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

    elif message.content.startswith('$hello'):
        if(str(message.author.id) == os.getenv("ORANGE_ID")):
            await message.channel.send('Hello')    
        elif(str(message.author.id) == os.getenv('TWICESTAN_ID')):
            await message.channel.send('hi :3')
        else:    
            await message.channel.send('Hello~')

    elif message.content.startswith('$upload'):
        await uploadPhotos(message)    
    
    elif message.content.startswith('$show'):
        file_list = drive.ListFile({'q': "\'" +  os.getenv('DRIVE_FOLDER_ID') + "' in parents and trashed=false"}).GetList()
        index = random.randint(0, len(file_list) - 1)
        file6 = drive.CreateFile({'id': file_list[index]['id']})
        ext = file6['title'].lower()
        if ext.endswith('png'):
            ext = 'png'
        elif ext.endswith('jpg'):
            ext = 'jpg'
        elif ext.endswith('jpeg'):
            ext = 'jpeg'
        else:
            await message.channel.send(content='```ERROR HAS OCCURRED WHILE LOADING FILE; FILE NAME: ' + ext +'```')
            return
        
        file6.GetContentFile('temp.' + ext)
        file=discord.File('temp.' + ext)
        await message.channel.send(file=file, content='Tada! You rolled ' + str(index) + ' from 0 to ' + str(len(file_list) - 1) + "!")

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
        await message.channel.send('Uploaded!')

client.run(os.getenv('TOKEN_ID'))