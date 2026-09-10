import os
import random
from threading import Thread
import discord
from discord.ext import commands
from flask import Flask

# --- 1. CONFIGURAZIONE SERVER WEB ANTI-LETARGO ---
app = Flask("")


@app.route("/")
def home():
    return "Slot Machine Bot è online e attivo!"


def run():
    # Render assegna automaticamente una porta, la leggiamo da qui
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


def keep_alive():
    t = Thread(target=run)
    t.start()


# --- 2. CONFIGURAZIONE BOT DISCORD ---
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

EMOJI_SLOT = ["🍒", "🍋", "🍇", "🔔", "💎", "7️⃣"]


@bot.event
async def on_ready():
    print(f"Slot Machine Online! Acceduto come: {bot.user.name}")


@bot.command(name="slot")
async def slot_machine(ctx):
    riga = [random.choice(EMOJI_SLOT) for _ in range(3)]
    risultato_visivo = f"**[ {riga[0]} | {riga[1]} | {riga[2]} ]**"

    if riga[0] == riga[1] == riga[2]:
        messaggio = f"🎉 {ctx.author.mention} HA VINTO IL JACKPOT! 🎉\n{risultato_visivo}"
    else:
        messaggio = f"❌ {ctx.author.mention} Hai perso! Ritenta...\n{risultato_visivo}"

    await ctx.send(messaggio)


# --- 3. AVVIO IN BACKGROUND ---
if __name__ == "__main__":
    # Avviamo il server web Flask prima del bot
    keep_alive()

    # Legge il token in modo sicuro dalle impostazioni di Render
    token = os.getenv("DISCORD_TOKEN")

    if token:
        bot.run(token)
    else:
        print(
            "ERRORE: Non è stata trovata la variabile d'ambiente DISCORD_TOKEN!"
        )