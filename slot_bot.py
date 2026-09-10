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
    return "Slot Machine Bot con Economia, Bombe e Reset è attivo!"


def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


def keep_alive():
    t = Thread(target=run)
    t.start()


# --- 2. CONFIGURAZIONE BOT DISCORD ---
intents = discord.Intents.default()
intents.message_content = True

# 🌟 RICORDATI DI METTERE IL TUO VERO ID DISCORD AL POSTO DI 1234567890
bot = commands.Bot(command_prefix="!", owner_id=1496572992426082556, intents=intents)

EMOJI_SLOT = ["🍒", "🍋", "🍇", "🔔", "💎", "7️⃣", "💣"]

# Dizionario per salvare i soldi degli utenti nella RAM
portafogli = {}


@bot.event
async def on_ready():
    print(f"Slot Machine con Economia Online! Acceduto come: {bot.user.name}")


# --- COMANDO PER CONTROLLARE IL PROPRIO SALDO ---
@bot.command(name="soldi")
async def controlla_soldi(ctx):
    user_id = ctx.author.id
    if user_id not in portafogli:
        portafogli[user_id] = 100  # 100 monete gratis di benvenuto

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


# --- 👑 COMANDO OWNER: AGGIUNGI SOLDI ---
@bot.command(name="add_soldi")
@commands.is_owner()
async def aggiungi_soldi(ctx, membro: discord.Member, cifra: int):
    if membro.id not in portafogli:
        portafogli[membro.id] = 100

    portafogli[membro.id] += cifra
    await ctx.send(
        f"👑 **OWNER ACTION:** Aggiunte **{cifra} monete** a {membro.mention}! Nuovo saldo: **{portafogli[membro.id]} monete**."
    )


# --- 👑 NUOVO COMANDO OWNER: RESETTA SOLDI ---
@bot.command(name="reset_soldi")
@commands.is_owner()  # <- Solo tu puoi usarlo!
async def resetta_soldi(ctx, membro: discord.Member):
    # Riporta il saldo a 100 monete
    portafogli[membro.id] = 100
    await ctx.send(
        f"🧹 **OWNER ACTION:** Il portafoglio di {membro.mention} è stato resettato! Saldo riportato a **100 monete**."
    )


# --- COMANDO SLOT CORRETTO MATEMATICAMENTE ---
@bot.command(name="slot")
@commands.cooldown(1, 5, commands.BucketType.user)
async def slot_machine(ctx, scommessa: str = None):
    user_id = ctx.author.id

    if scommessa is None:
        await ctx.send(
            f"❌ {ctx.author.mention}, devi specificare quanto vuoi scommettere! Esempio: `!slot 10`"
        )
        ctx.command.reset_cooldown(ctx)
        return

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

    if user_id not in portafogli:
        portafogli[user_id] = 100

    if portafogli[user_id] < cifra:
        await ctx.send(
            f"🚫 {ctx.author.mention}, non hai abbastanza monete! Il tuo saldo attuale è di **{portafogli[user_id]} monete**."
        )
        ctx.command.reset_cooldown(ctx)
        return

    portafogli[user_id] -= cifra

    # Estrazione casuale delle icone
    riga = [random.choice(EMOJI_SLOT) for _ in range(3)]
    risultato_visivo = f"**[ {riga[0]} | {riga[1]} | {riga[2]} ]**"

    # --- 💥 CONTROLLO TRIS DI BOMBE ---
    if riga[0] == "💣" and riga[1] == "💣" and riga[2] == "💣":
        portafogli[user_id] = 0  # Portafoglio azzerato per l'esplosione!
        await ctx.send(
            f"{risultato_visivo}\n💥 {ctx.author.mention} è esploso, forse è meglio cosi🤔?\n📉 Il tuo portafoglio è stato ridotto a **0 monete**!"
        )
        return

    # --- 🏆 CONTROLLO JACKPOT ---
    if riga[0] == riga[1] == riga[2]:
        vincita = cifra * 10
        portafogli[user_id] += vincita
        messaggio = f"🎉 {ctx.author.mention} HA VINTO IL JACKPOT! 🎉\n{risultato_visivo}\n💰 Hai vinto **{vincita} monete**! Nuovo saldo: **{portafogli[user_id]}**."
    else:
        messaggio = f"❌ {ctx.author.mention} Hai perso! Ritenta...\n{risultato_visivo}\n📉 Hai perso **{cifra} monete**. Saldo rimasto: **{portafogli[user_id]}**."

    await ctx.send(messaggio)


# --- GESTIONE ERRORI ---
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(
            f"⏳ {ctx.author.mention}, calmati! Devi aspettare ancora {error.retry_after:.1f} secondi."
        )
    elif isinstance(error, commands.NotOwner):
        await ctx.send(
            f"🚫 {ctx.author.mention}, ci hai provato! Questo comando può essere usato solo dal mio Creatore."
        )
    else:
        raise error


# --- 3. AVVIO ---
if __name__ == "__main__":
    keep_alive()
    token = os.getenv("DISCORD_TOKEN")
    if token:
        bot.run(token)
    else:
        print(
            "ERRORE: Non è stata trouvata la variabile d'ambiente DISCORD_TOKEN!"
        )
