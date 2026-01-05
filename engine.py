import time
import random
import json
import os
import uuid

# File in cui verranno salvati i dati di gioco (reputazione, messaggi ignorati, ecc.)
STATE_FILE = "chat_state.json"

# Numero massimo di messaggi ignorati prima del game over
MAX_IGNORED = 5  

# ==============================
# Lista utenti / nomi
# ==============================
USER_NAMES = [
    # 🇮🇹 Italiani
    "Luca","Marco","Giulia","Sara","Alessio","Marta","Davide","Chiara",
    "Leonardo","Anna","Federico","Sofia","Giorgio","Elena","Matteo",
    "Francesca","Riccardo","Ilaria","Simone","Valentina","Andrea",
    "Beatrice","Tommaso","Noemi","Pietro","Arianna","Gabriele",
    "Niccolò","Alessandra","Filippo","Camilla","Emanuele","Greta",

    # 🌍 Stranieri
    "John","Emily","Michael","Sarah","Alex","Chris","Jessica","Daniel",
    "Emma","Oliver","Noah","Liam","Sophia","Isabella","Lucas","Mia",
    "Ethan","Ava","Benjamin","Charlotte","James","Amelia",
    "Oscar","Hugo","Leo","Nina","Eva","Lars","Ivan","Mikhail",
    "Yuki","Akira","Sakura","Ken","Hana","Luis","Carlos","Mateo",
    "Diego","Valeria","Camilo","Andrés","Sergio",

    # ✂️ Diminutivi / soprannomi
    "Ale","Fra","Vale","Simo","Gio","Fede","Ricky","Pitty","Nico",
    "Lory","Eli","Matti","Dani","Sofy","Ste","TommY","Bibi",
    "Andy","Pippo","Mimi","Cami","Lulu","Nene","Kiki","Tata",

    # 🤪 Buffi / ironici
    "Boh","Anonimo","ZioPino","LaFra","MegaAle","SirLuca",
    "MisterX","User123","NoName","RandomGuy","ChatBotino",
    "PingPong","Pasticcio","Caffè","Banana","GattoTriste",
    "Fuffa","Biscotto","Patata","Spaghetti","Pingu","Blob",
    "PolloSupremo","ZebraConfusa","Tostapane","WifiDebole"
]

# ==============================
# Lista messaggi
# ==============================
MESSAGES = [
    # 🇮🇹 Neutri / quotidiani
    "Ehi, ci sei?",
    "Che fai?",
    "Hai visto il messaggio?",
    "Rispondi quando puoi",
    "Tutto ok?",
    "Parliamo dopo?",
    "Che ne pensi?",
    "Hai 2 minuti?",
    "Ti disturbo?",
    "Quando puoi fammi sapere",

    # 😐 Insistenti / passivo-aggressivi
    "Sei sparito",
    "Mi sembri distante",
    "Sto aspettando una tua risposta 😐",
    "Ti ho scritto prima…",
    "Forse non hai visto il messaggio",
    "Ok, capisco…",
    "Va bene così allora",
    "Immagino tu sia occupato",

    # 😟 Ansia / preoccupazione
    "È successo qualcosa?",
    "Mi stai facendo preoccupare",
    "Dimmi solo se va tutto bene",
    "Spero di non averti infastidito",
    "Va tutto bene, vero?",
    "Mi fai sapere qualcosa?",
    "Sono un po’ in ansia 😟",

    # 😄 Leggeri / ironici
    "Oh oh, linea persa? 😅",
    "😂😂😂",
    "Ehm… risposta in arrivo?",
    "Knock knock 👀",
    "Ti sei addormentato?",
    "Messaggio fantasma 👻",
    "Risposta telepatica in arrivo?",

    # 🇬🇧 English – casual
    "Hey, are you there?",
    "What are you up to?",
    "Did you see my message?",
    "Reply when you can",
    "Everything ok?",
    "Got a minute?",
    "Let me know",
    "We can talk later",

    # 🇬🇧 English – pressure / awkward
    "You went quiet",
    "Still waiting for your reply",
    "Just checking in",
    "Hope I’m not bothering you",
    "Guess you’re busy",
    "Did I say something wrong?",
    "I’ll wait then…",

    # 🤖 Meta / da bot (divertenti per il gioco)
    "Sistema: risposta in attesa…",
    "Ping.",
    "Ancora silenzio 🤖",
    "Timeout imminente ⏳",
    "Connessione emotiva debole",
]

# Timeout e difficoltà
MIN_TIMEOUT = 12
MAX_TIMEOUT = 28
LEVEL_UP_EVERY = 5
MAX_LEVEL = 10

# ==============================
# Classe principale del motore di chat
# ==============================
class ChatEngine:
    def __init__(self):
        # Dizionario utenti con reputazione e messaggi ignorati
        self.users = {}

        # Lista dei messaggi attivi
        self.active_messages = []

        # Flag gioco in esecuzione
        self.running = True
        self.paused = False

        # Livello di difficoltà e contatori
        self.level = 1
        self.total_answers = 0
        self.ignored_total = 0

        # Carica dati salvati e aggiorna la difficoltà iniziale
        self.load_state()
        self.update_difficulty()

    # =======================
    # Salvataggio / caricamento dati
    # =======================
    def load_state(self):
        """Carica dati da file JSON se esistono"""
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r") as f:
                    data = json.load(f)
                self.users = data.get("users", {})
                self.total_answers = data.get("total_answers", 0)
                self.ignored_total = data.get("ignored_total", 0)
            except:
                self.users = {}
        else:
            self.users = {}

        # Assicura che ogni utente abbia tutti i campi necessari
        for u in self.users:
            self.users[u].setdefault("reputation", 0)
            self.users[u].setdefault("ignored", 0)
            self.users[u].setdefault("patience", random.choice([0.8,1.0,1.3]))

    def save_state(self):
        """Salva dati di gioco su JSON"""
        data = {
            "users": self.users,
            "total_answers": self.total_answers,
            "ignored_total": self.ignored_total
        }
        with open(STATE_FILE,"w") as f:
            json.dump(data,f,indent=4)

    def reset_state(self):
        """Resetta completamente lo stato del gioco"""
        self.users = {}
        self.active_messages = []
        self.total_answers = 0
        self.ignored_total = 0
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)

    # =======================
    # Livello e difficoltà
    # =======================
    def update_difficulty(self):
        """Aggiorna il livello e intervalli di timeout in base alle risposte date"""
        self.level = min(1 + self.total_answers // LEVEL_UP_EVERY, MAX_LEVEL)
        self.cur_min_timeout = max(5, MIN_TIMEOUT - self.level)
        self.cur_max_timeout = max(8, MAX_TIMEOUT - self.level*2)
        self.message_interval = max(0.7, 3 - self.level*0.25)

    # =======================
    # Gestione messaggi
    # =======================
    def generate_user(self):
        """Sceglie un utente casuale e lo registra se non esiste"""
        user = random.choice(USER_NAMES)
        if user not in self.users:
            self.users[user] = {
                "reputation": 0,
                "ignored": 0,
                "patience": random.choice([0.8,1.0,1.3])
            }
        return user

    def spawn_message(self):
        """Crea un nuovo messaggio da un utente casuale"""
        user = self.generate_user()
        msg_id = str(uuid.uuid4())[:6]
        timeout = int(random.randint(self.cur_min_timeout, self.cur_max_timeout) * self.users[user]["patience"])
        msg = {
            "id": msg_id,
            "user": user,
            "text": random.choice(MESSAGES),
            "time_created": time.time(),
            "timeout": timeout,
            "time_left": timeout,
            "replies": []
        }
        self.active_messages.append(msg)
        return msg

    # =======================
    # Aggiornamento timer / rimozione messaggi scaduti
    # =======================
    def tick(self):
        """Aggiorna il tempo rimanente dei messaggi e rimuove quelli scaduti"""
        now = time.time()
        removed = []
        for msg in self.active_messages:
            elapsed = now - msg["time_created"]
            msg["time_left"] = max(0, int(msg["timeout"] - elapsed))
            if elapsed >= msg["timeout"]:
                removed.append(msg)

        for msg in removed:
            self.active_messages.remove(msg)
            # Incrementa contatori per game over
            self.users[msg["user"]]["ignored"] += 1
            self.ignored_total += 1

    # =======================
    # Risposta ai messaggi
    # =======================
    def answer_message(self, idx, reply_text):
        """Risponde al messaggio selezionato e aggiorna reputazione"""
        if idx < 0 or idx >= len(self.active_messages):
            return False, None
        msg = self.active_messages[idx]
        msg["replies"].append({"from":"Tu", "text": reply_text})
        user = msg["user"]
        self.users[user]["reputation"] += 1
        self.users[user]["ignored"] = 0
        self.total_answers += 1
        self.update_difficulty()
        # Rimuove il messaggio dopo risposta
        self.active_messages.pop(idx)
        return True, user

    # =======================
    # Controllo game over
    # =======================
    def check_game_over(self):
        """Ritorna True se il numero totale di messaggi ignorati supera il limite"""
        return self.ignored_total >= MAX_IGNORED

    # =======================
    # Statistiche
    # =======================
    def get_stats(self):
        """Ritorna informazioni sugli utenti (reputazione e messaggi ignorati)"""
        return self.users
