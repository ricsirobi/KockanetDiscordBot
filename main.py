import os
import mysql.connector
from mysql.connector import errorcode
from mysql.connector import (connection)
import discord
from keep_alive import keep_alive
import urllib


#Adatbazis
def sqlQuery(insertstring):
  try:
    cnx = connection.MySQLConnection(user=os.environ['USER'], 
                                  password=os.environ['PASSWORD'],
                                  host=os.environ['HOST'],
                                  database='robi')
  except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
      print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
      print("Database does not exist")
    else:
      print(err)
  else:
    print("Connected to database")
    mycursor = cnx.cursor() 
    print(insertstring)
    mycursor.execute(insertstring)
    cnx.commit()#ezt kerestem fél órán át

    cnx.close()
    return True
  return False

def getprice(code):
  try:
    cnx = connection.MySQLConnection(user=os.environ['USER'], 
                                  password=os.environ['PASSWORD'],
                                  host=os.environ['HOST'],
                                  database='robi')
  except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
      print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
      print("Database does not exist")
    else:
      print(err)
  else:
    print("Sikeres csatlakozás az adatbázishoz")
    #ide írhatom a kódom
    mycursor = cnx.cursor()
    mycursor.execute("SELECT * FROM kockanet where code like \"" + code + "\"")
    myresult = mycursor.fetchall()
    price = 2
    thereis = False
    name = ""
    for x in myresult:
      print(x)
      price = x[1]
      name = x[3]
      updated = x[4]
      thereis = True
    cnx.close()
    return price, thereis,name, updated
  return "Sikertelen lekérdezés"

def kockanet_update():
    url = "https://kockanet.hu/!robi/nagyonkell.php"
    fp = urllib.request.urlopen(url)
    mybytes = fp.read()
    mystr = mybytes.decode("utf8")
    mysplit = "</div><div id=\'myDiv\'>"
    splitted = mystr.split(mysplit)
    print("Adatok törlése: " + str(sqlQuery("DELETE FROM kockanet WHERE 1")))
    for x in splitted:
      x = x.replace("</div>","").replace("<table class='table'><div id='myDiv'>","").replace("\n","").replace("<span id=\"dimSec\">","").replace("</span>","").replace("<div class=\"browseProductDescription\">","").replace("<br /><br class=\"Apple-interchange-newline\" />","").replace("<div id=\"short_description\">","").replace("\"","").replace("</table>","")
      temp = x.split("; ")
      #print("TEMP:" + str(temp))
      status = 0
      if temp[2] == "igen":
        status = 1
      insertString = "INSERT INTO kockanet(code, price, status, name, uploadedTime,k_id,jf_short,jf_long,jf_desc) VALUES (\""+temp[0].replace("\n","").replace(" ","")+"\",  "+temp[1]+",  "+str(status) +", \""+temp[3]+"\",now(),\""+temp[4]+"\",\""+temp[5]+"\",\""+temp[6]+"\",\""+temp[7]+"\");"
      print( "Adatfeltöltés: "+str(sqlQuery(insertString)))



#Discord
client = discord.Client()
@client.event
async def on_ready():
  print('Bejelentkezve mint: {0.user}'.
  format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return
  if message.content.startswith('!'):
    try:
      code = message.content.split('!',1)[1]
      print("{" + code + "}")
      ret = getprice(code) 
      price = ret[0]  
      thereis = ret[1]
      name = ret[2]
      updated = ret[3]
      print(updated)
      
    
      amount = price
      currency = "{:,.0f} Ft".format(amount).replace(","," ")
      await message.channel.send("```"+str(currency) + " --- "+code +": "+ name + " (Frissítve: "+str(updated)+") ```")
    except Exception: 
      await message.channel.send("```Nincs ilyen termékünk```")
  elif message.content.startswith('help'):
    await message.channel.send("```CSS\nParancsok:\n!##### -> vissza küldöm az árát és nevét \nUpdate||****|| -> A csillagok helyére írd be a jelszót és küldd el az üzenetet. Ha helyes a jelszó frissítem az adatokat és válaszolok ha kész.```")
  #print(message.author)
  elif message.content.startswith("Update||" + os.environ['UPDATEPASSWORD'] + "||"):
    await message.channel.send("Frissítés... (ez eltart egy darabig)")
    kockanet_update()
    await message.channel.send("Frissítés kész")

keep_alive()
client.run(os.getenv('TOKEN'))