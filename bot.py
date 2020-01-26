from Yowsup.connectionmanager import YowsupConnectionManager
import json,base64,threading,time,urllib,HTMLParser

class MainBot():
	def __init__(self,user,passwd):
		self.con = YowsupConnectionManager()
		self.con.setAutoPong(True)
		self.signalsInterface = self.con.getSignalsInterface()
		self.methodsInterface = self.con.getMethodsInterface()
		self.signalsInterface.registerListener("message_received", self.onMessageReceived)
		self.signalsInterface.registerListener("auth_success", self.onAuthSuccess)
		self.signalsInterface.registerListener("auth_fail", self.onAuthFailed)
		self.signalsInterface.registerListener("disconnected", self.onDisconnected)
		self.signalsInterface.registerListener("receipt_messageDelivered", self.onMessageDelivered)
		self.methodsInterface.call("auth_login", (user, base64.b64decode(passwd)))
		self.running = True

	def onAuthSuccess(self,args):
		print("Auth True")
		self.methodsInterface.call("ready")

	def onAuthFailed(self,args):
		print("Auth False")
		self.running = False

	def onDisconnected(self,args):
		print("Connection Terminated")
		self.running = False

	def onMessageDelivered(self,jid,messageId):
		print("Message Delivered")

	def onMessageReceived(self, messageId, jid, messageContent, timestamp, wantsReceipt, pushName, isBroadcast):
		time.sleep(0.2)
		self.methodsInterface.call("message_ack", (jid, messageId))
		time.sleep(0.2)
		self.react(jid,messageContent)

	def react(self,jid,messageContent):
		messageContent = messageContent.upper()
		text = messageContent.split()
		if ('HI' in text) or ('SUP' in text) or ('HELLO' in text):
			self.methodsInterface.call("message_send", (jid, "Hello Im WABot Alpha"))
		elif (('LOL' in text) or ('BYE' in text)):
			self.methodsInterface.call("message_send", (jid, "hmmm..."))
		elif (('OK' in text) or('THANKS' in text)):
			self.methodsInterface.call("message_send", (jid, "Your Welcome, anything else"))
		elif ('HITME' in text) or (('HIT' in text) and ('ME' in text)):
			self.methodsInterface.call("message_send", (jid, self.action_send_quote()))
		elif ((('CHUCK' in text) or ('NORRIS' in text)) and (('JOKE' in text) or ('JOKES' in text))):
			self.methodsInterface.call("message_send", (jid, self.action_send_norris()))
		else:
			self.methodsInterface.call("message_send", (jid, self.do_a_search(text)))

	def action_send_quote(self):
		try:
			data = urllib.urlopen("http://www.iheartquotes.com/api/v1/random?source=joel_on_software+paul_graham+prog_style").read()
			e = data.split('\n')
			txt = '\n'.join(e[0:len(e)-2])
			return str(self.uscape(txt))
		except:
			return "cannot hit you, for now"

	def action_send_norris(self):
		try:
			data = urllib.urlopen("http://api.icndb.com/jokes/random/").read()
			joke = json.loads(data)
			return str(self.uscape(joke['value']['joke']).encode('utf8'))
		except:
			return "Norris killed the server"

	def do_a_search(self,text): 
		try:
			q = '+'.join(text)
			data = urllib.urlopen("http://api.duckduckgo.com/?q="+q+"&format=json&pretty=1&no_redirect=1").read()
			result = json.loads(data)
			if not (result["RelatedTopics"][0]["Text"]==""):
				return str(self.uscape("Lets Seee.... \n" + (result["AbstractText"]).encode('utf8')))
			else:
				return "Hmmmmm, Nothing to say"	
		except:
			return "Hmmmmm, Not in the mood"

	def uscape(self,text):
		try:
			return HTMLParser.HTMLParser().unescape(text)
		except:
			return text	

raw_credentials = open('login.json').read()
credentials = json.loads(raw_credentials)
mb = MainBot(credentials["phone"],credentials["password"])

while True:
        if not mb.running:
        	time.sleep(1)
        	mb = None
        	mb = MainBot(credentials["phone"],credentials["password"])