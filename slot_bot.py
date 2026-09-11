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
    return "Slot Machine Bot con Economia e Nuovi Giochi è attivo!"


def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


def keep_alive():
    t = Thread(target=run)
    t.start()


# --- 2. CONFIGURAZIONE BOT DISCORD ---
intents = discord.Intents.default()
intents.message_content = True

# 👑 IL TUO OWNER ID È STATO CONFIGURATO QUI PERFETTAMENTE
bot = commands.Bot(
    command_prefix="!",
    owner_id=1496572992426082556,
    intents=intents,
    help_command=None,
)

EMOJI_SLOT = ["🍒", "🍋", "🍇", "🔔", "💎", "7️⃣", "💣"]

# Dizionario per salvare i soldi degli utenti nella RAM
portafogli = {}


@bot.event
async def on_ready():
    print(f"Slot Machine con Economia Online! Acceduto come: {bot.user.name}")


# --- 📜 MENU DEI COMANDI AGGIORNATO CON I NUOVI GIOCHI ---
@bot.command(name="menu")
async def mostra_menu(ctx):
    testo_menu = (
        "🎰 **MENU COMANDI CASINÒ ARCADE** 🎰\n\n"
        "🔴 **Comandi generali ed Economia:**\n"
        "• `!menu` - Mostra questa lista di comandi.\n"
        "• `!soldi` - Controlla quante monete hai nel portafoglio.\n"
        "• `!daily` - Riscatta 50 monete gratis (una volta al giorno).\n"
        "• `!lavora` - Fai un turno di lavoro per avere 100 monete (1% di chance di riceverne 10.000!).\n"
        "• `!classifica` - Mostra la Top 3 dei più ricchi del server.\n\n"
        "🎮 **Minigiochi d'Azzardo:**\n"
        "• `!slot [cifra]` - Gioca alla slot machine (es: `!slot 10`).\n"
        "• `!coinflip [testa/croce] [cifra]` - Testa o croce (es: `!coinflip testa 20`).\n"
        "• `!rps [sasso/carta/forbice] [cifra]` - Carta, Forbice o Sasso (es: `!rps sasso 15`).\n\n"
        "👑 *I comandi amministrativi dell'Owner sono nascosti.*"
    )
    await ctx.send(testo_menu)


# --- COMANDO PER CONTROLLARE IL PROPRIO SALDO ---
@bot.command(name="soldi")
async def controlla_soldi(ctx):
    user_id = ctx.author.id
    if user_id not in portafogli:
        portafogli[user_id] = 100  # 100 monete gratis di benvenuto

    await ctx.send(
        f"💰 {ctx.author.mention}, nel tuo portafoglio ci sono **{portafogli[user_id]} monete**!"
    )


# --- ⏳ COMANDO DAILY (Uso limitato a 1 volta ogni 24 ore) ---
@bot.command(name="daily")
@commands.cooldown(1, 86400, commands.BucketType.user)
async def monete_giornaliere(ctx):
    user_id = ctx.author.id
    if user_id not in portafogli:
        portafogli[user_id] = 100

    portafogli[user_id] += 50
    await ctx.send(
        f"🎁 {ctx.author.mention}, hai riscattato **50 monete gratis**! Nuovo saldo: **{portafogli[user_id]} monete**."
    )


# --- 💼 COMANDO: LAVORA (Con cooldown di 30 minuti e 1% colpaccio) ---
@bot.command(name="lavora")
@commands.cooldown(1, 1800, commands.BucketType.user)
async def lavora_per_monete(ctx):
    user_id = ctx.author.id
    if user_id not in portafogli:
        portafogli[user_id] = 100

    chance = random.randint(1, 100)

    if chance == 77:
        guadagno = 10000
        portafogli[user_id] += guadagno
        await ctx.send(
            f"🍀 {ctx.author.mention} **COLPACCIO ASSURDO!** Hai lavorato così bene che il capo ti ha dato un bonus incredibile di **10.000 monete**!!! 💰 Nuovo saldo: **{portafogli[user_id]} monete**."
        )
    else:
        guadagno = 100
        portafogli[user_id] += guadagno
        await ctx.send(
            f"💼 {ctx.author.mention}, hai finito il tuo turno di lavoro! Hai guadagnato **100 monete**. Nuovo saldo: **{portafogli[user_id]} monete**."
        )


# --- 📊 COMANDO: CLASSIFICA DEI PIÙ RICCHI (TOP 3) ---
@bot.command(name="classifica")
async def mostra_classifica(ctx):
    if not portafogli:
        await ctx.send(
            "📊 La classifica è ancora vuota! Iniziate a giocare per comparire qui."
        )
        return

    classifica_ordinata = sorted(
        portafogli.items(), key=lambda item: item, reverse=True
    )

    testo_classifica = "🏆 **TOP 3 DEI PIÙ RICCHI** 🏆\n\n"
    medaglie = ["🥇", "🥈", "🥉"]

    for i, (user_id, saldo) in enumerate(classifica_ordinata[:3]):
        try:
            utente = await bot.fetch_user(user_id)
            nome = utente.display_name
        except Exception:
            nome = f"Utente Sconosciuto ({user_id})"

        testo_classifica += f"{medaglie[i]} **{nome}** — {saldo} monete\n"

    await ctx.send(testo_classifica)


# --- 🪙 NUOVO MINIGIOCO: TESTA O CROCE ---
@bot.command(name="coinflip")
@commands.cooldown(1, 3, commands.BucketType.user)
async def coin_flip(ctx, scelta: str = None, scommessa: str = None):
    user_id = ctx.author.id

    if scelta is None or scommessa is None:
        await ctx.send(
            f"❌ {ctx.author.mention}, uso corretto: `!coinflip [testa/croce] [scommessa]` (es: `!coinflip testa 20`)"
        )
        ctx.command.reset_cooldown(ctx)
        return

    scelta = scelta.lower()
    if scelta not in ["testa", "croce"]:
        await ctx.send(
            f"❌ {ctx.author.mention}, devi scegliere tra `testa` o `croce`!"
        )
        ctx.command.reset_cooldown(ctx)
        return

    if not scommessa.isdigit():
        await ctx.send(
            f"❌ {ctx.author.mention}, inserisci una scommessa valida!"
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
            f"🚫 {ctx.author.mention}, non hai abbastanza monete! Saldo: **{portafogli[user_id]}**."
        )
        ctx.command.reset_cooldown(ctx)
        return

    portafogli[user_id] -= cifra
    risultato = random.choice(["testa", "croce"])
    emoji_moneta = "🪙"

    if scelta == risultato:
        vincita = cifra * 2
        portafogli[user_id] += vincita
        await ctx.send(
            f"{emoji_moneta} **COINFLIP:** È uscito **{risultato.upper()}**!\n🎉 Grande {ctx.author.mention}, hai indovinato e raddoppiato! Guadagnate **{cifra} monete**. Saldo: **{portafogli[user_id]}**."
        )
    else:
        await ctx.send(
            f"{emoji_moneta} **COINFLIP:** È uscito **{risultato.upper()}**!\n❌ Mi dispiace {ctx.author.mention}, hai perso **{cifra} monete**. Saldo: **{portafogli[user_id]}**."
        )


# --- 🪨 NUOVO MINIGIOCO: CARTA FORBICE SASSO ---
@bot.command(name="rps")
@commands.cooldown(1, 3, commands.BucketType.user)
async def rock_paper_scissors(ctx, scelta: str = None, scommessa: str = None):
    user_id = ctx.author.id

    if scelta is None or scommessa is None:
        await ctx.send(
            f"❌ {ctx.author.mention}, uso corretto: `!rps [sasso/carta/forbice] [scommessa]`"
        )
        ctx.command.reset_cooldown(ctx)
        return

    scelta = scelta.lower()
    # Supportiamo anche i plurali per evitare errori degli utenti
    if scelta in ["forbice", "forbici"]:
        scelta = "forbice"

    if scelta not in ["sasso", "carta", "forbice"]:
        await ctx.send(
            f"❌ {ctx.author.mention}, scegli tra `sasso`, `carta` o `forbice`!"
        )
        ctx.command.reset_cooldown(ctx)
        return

    if not scommessa.isdigit():
        await ctx.send(
            f"❌ {ctx.author.mention}, inserisci una scommessa valida!"
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
            f"🚫 {ctx.author.mention}, non hai abbastanza monete! Saldo: **{portafogli[user_id]}**."
        )
        ctx.command.reset_cooldown(ctx)
        return

    portafogli[user_id] -= cifra

    mosse = ["sasso", "carta", "forbice"]
    emojis = {"sasso": "🪨 Sasso", "carta": "📄 Carta", "forbice": "✂️ Forbice"}
    mossa_bot = random.choice(mosse)

    testo_base = f"Tu: **{emojis[scelta]}** VS Bot: **{emojis[mossa_bot]}**\n"

    if scelta == mossa_bot:  # Pareggio
        portafogli[user_id] += cifra  # Restituisce i soldi scommessi
        await ctx.send(
            f"{testo_base}🤝 **PAREGGIO!** Le monete ti sono state restituite. Saldo: **{portafogli[user_id]}**."
        )
    elif (
        (scelta == "sasso" and mossa_bot == "forbice")
        or (scelta == "carta" and mossa_bot == "sasso")
        or (scelta == "forbice" and mossa_bot == "carta")
    ):  # Vittoria giocatore
        vincita = cifra * 2
        portafogli[user_id] += vincita
        await ctx.send(
            f"{testo_base}🎉 **HAI VINTO!** Hai raddoppiato la tua puntata guadagnando **{cifra} monete**! Saldo: **{portafogli[user_id]}**."
        )
    else:  # Sconfitta giocatore
        await ctx.send(
            f"{testo_base}❌ **HAI PERSO!** Il bot ti ha battuto. Hai perso **{cifra} monete**. Saldo: **{portafogli[user_id]}**."
        )


# --- COMANDO SLOT CORRETTO SENZA BUG ---
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
