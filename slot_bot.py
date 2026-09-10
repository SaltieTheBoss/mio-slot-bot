import os
import random
from threading import Thread
import discord
from discord.ext import commands
from flask import Flask

# --- 1. SERVER WEB INTEGRATO ANTI-LETARGO ---
app = Flask("")


@app.route("/")
def home():
    return "Slot Machine Bot con Economia è attivo!"


def run():
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

# --- DIZIONARIO PER SALVARE I SOLDI DEGLI UTENTI ---
# Struttura: { id_utente: saldo_monete }
portafogli = {}


@bot.event
async def on_ready():
    print(f"Slot Machine con Economia Online! Acceduto come: {bot.user.name}")


# --- COMANDO PER CONTROLLARE IL PROPRIO SALDO ---
@bot.command(name="soldi")
async def controlla_soldi(ctx):
    user_id = ctx.author.id
    # Se l'utente non è nel dizionario, gli regaliamo 100 monete di partenza
    if user_id not in portafogli:
        portafogli[user_id] = 100

    await ctx.send(
        f"💰 {ctx.author.mention}, nel tuo portafoglio ci sono **{portafogli[user_id]} monete**!"
    )


# --- COMANDO PER RICEVERE MONETE GRATIS ---
@bot.command(name="daily")
async def monete_giornaliere(ctx):
    user_id = ctx.author.id
    if user_id not in portafogli:
        portafogli[user_id] = 100

    portafogli[user_id] += 50
    await ctx.send(
        f"🎁 {ctx.author.mention}, hai riscattato **50 monete gratis**! Nuovo saldo: **{portafogli[user_id]} monete**."
    )


# --- COMANDO SLOT AGGIORNATO CON SCOMMESSA E COOLDOWN ---
@bot.command(name="slot")
@commands.cooldown(1, 5, commands.BucketType.user)
async def slot_machine(ctx, scommessa: str = None):
    user_id = ctx.author.id

    # 1. Controlla se l'utente ha inserito una scommessa
    if scommessa is None:
        await ctx.send(
            f"❌ {ctx.author.mention}, devi specificare quanto vuoi scommettere! Esempio: `!slot 10`"
        )
        ctx.command.reset_cooldown(ctx)  # Reset del cooldown se sbaglia comando
        return

    # 2. Controlla se la scommessa è un numero valido
    if not scommessa.isdigit():
        await ctx.send(
            f"❌ {ctx.author.mention}, inserisci un numero valido di monete!"
        )
        ctx.command.reset_cooldown(ctx)
        return

    cifra = int(scommessa)

    if cifra <= 0:
        await ctx.send(
            f"❌ {ctx.author.mention}, devi scommettere almeno 1 moneta!"
        )
        ctx.command.reset_cooldown(ctx)
        return

    # 3. Configura il portafoglio se è un nuovo utente
    if user_id not in portafogli:
        portafogli[user_id] = 100

    # 4. Controlla se l'utente ha abbastanza soldi
    if portafogli[user_id] < cifra:
        await ctx.send(
            f"🚫 {ctx.author.mention}, non hai abbastanza monete! Il tuo saldo attuale è di **{portafogli[user_id]} monete**."
        )
        ctx.command.reset_cooldown(ctx)
        return

    # 5. Scala i soldi della scommessa
    portafogli[user_id] -= cifra

    # 6. Estrazione della slot machine
    riga = [random.choice(EMOJI_SLOT) for _ in range(3)]
    risultato_visivo = f"**[ {riga[0]} | {riga[1]} | {riga[2]} ]**"

    # 7. Controllo vittoria (Jackpot con 3 uguali)
    if riga[0] == riga[1] == riga[2]:
        vincita = cifra * 10
        portafogli[user_id] += vincita
        messaggio = f"🎉 {ctx.author.mention} HA VINTO IL JACKPOT! 🎉\n{risultato_visivo}\n💰 Hai vinto **{vincita} monete**! Nuovo saldo: **{portafogli[user_id]}**."
    else:
        messaggio = f"❌ {ctx.author.mention} Hai perso! Ritenta...\n{risultato_visivo}\n📉 Hai perso **{cifra} monete**. Saldo rimasto: **{portafogli[user_id]}**."

    await ctx.send(messaggio)


# --- GESTIONE ERRORE COOLDOWN (CLIDDRA) ---
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(
            f"⏳ {ctx.author.mention}, calmati! Devi aspettare ancora {error.retry_after:.1f} secondi."
        )
    else:
        raise error


# --- 3. AVVIO IN BACKGROUND ---
if __name__ == "__main__":
    keep_alive()
    token = os.getenv("DISCORD_TOKEN")
    if token:
        bot.run(token)
    else:
        print(
            "ERRORE: Non è stata trovata la variabile d'ambiente DISCORD_TOKEN!"
        )
