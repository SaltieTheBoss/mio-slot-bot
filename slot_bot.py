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
    return "Casinò Arcade Bot è attivo!"


def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


def keep_alive():
    t = Thread(target=run)
    t.start()


# --- 2. CONFIGURAZIONE BOT DISCORD ---
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    owner_id=1496572992426082556,
    intents=intents,
    help_command=None,
)

EMOJI_SLOT = ["🍒", "🍋", "🍇", "🔔", "💎", "7️⃣", "💣"]
portafogli = {}


@bot.event
async def on_ready():
    print(f"Bot Online! Acceduto come: {bot.user.name}")


# --- 📜 MENU DEI COMANDI ---
@bot.command(name="menu")
async def mostra_menu(ctx):
    testo_menu = (
        "🎰 **MENU COMANDI CASINÒ ARCADE** 🎰\n\n"
        "🔴 **Comandi generali ed Economia:**\n"
        "• `!menu` - Mostra questa lista.\n"
        "• `!soldi` - Controlla quante monete hai.\n"
        "• `!daily` - Riscatta 50 monete gratis (una volta al giorno).\n"
        "• `!lavora` - Lavora per avere 100 monete (1% di chance di riceverne 10.000!).\n"
        "• `!classifica` - Mostra la Top 3 del server.\n\n"
        "🎮 **Minigiochi d'Azzardo:**\n"
        "• `!slot [cifra]` - Gioca alla slot machine (es: `!slot 10`).\n"
        "• `!coinflip [testa/croce] [cifra]` - Testa o croce (es: `!coinflip testa 20`).\n"
        "• `!rps [sasso/carta/forbice] [cifra]` - Carta, Forbice o Sasso.\n"
    )
    await ctx.send(testo_menu)


# --- PORTAFOGLIO ---
@bot.command(name="soldi")
async def controlla_soldi(ctx):
    user_id = ctx.author.id
    if user_id not in portafogli:
        portafogli[user_id] = 100
    await ctx.send(
        f"💰 {ctx.author.mention}, nel tuo portafoglio ci sono **{portafogli[user_id]} monete**!"
    )


# --- DAILY CONTROLLATO ---
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


# --- LAVORO CON COOLDOWN (30 MIN) ---
@bot.command(name="lavora")
@commands.cooldown(1, 1800, commands.BucketType.user)
async def lavora_per_monete(ctx):
    user_id = ctx.author.id
    if user_id not in portafogli:
        portafogli[user_id] = 100
    chance = random.randint(1, 100)
    if chance == 77:
        portafogli[user_id] += 10000
        await ctx.send(
            f"🍀 {ctx.author.mention} **COLPACCIO!** Bonus incredibile di **10.000 monete**!!! 💰 Saldo: **{portafogli[user_id]}**."
        )
    else:
        portafogli[user_id] += 100
        await ctx.send(
            f"💼 {ctx.author.mention}, hai guadagnato **100 monete**. Saldo: **{portafogli[user_id]} monete**."
        )


# --- CLASSIFICA ORDINATA ---
@bot.command(name="classifica")
async def mostra_classifica(ctx):
    if not portafogli:
        await ctx.send("📊 La classifica è ancora vuota!")
        return
    classifica_ordinata = sorted(
        portafogli.items(), key=lambda item: item[1], reverse=True
    )
    testo_classifica = "🏆 **TOP 3 DEI PIÙ RICCHI** 🏆\n\n"
    medaglie = ["🥇", "🥈", "🥉"]
    for i, (user_id, saldo) in enumerate(classifica_ordinata[:3]):
        try:
            utente = await bot.fetch_user(user_id)
            nome = utente.display_name
        except Exception:
            nome = f"Utente {user_id}"
        testo_classifica += f"{medaglie[i]} **{nome}** — {saldo} monete\n"
    await ctx.send(testo_classifica)


# --- MINIGIOCO: TESTA O CROCE ---
@bot.command(name="coinflip")
@commands.cooldown(1, 3, commands.BucketType.user)
async def coin_flip(ctx, scelta: str = None, scommessa: str = None):
    user_id = ctx.author.id
    if scelta is None or scommessa is None:
        await ctx.send(
            f"❌ Uso corretto: `!coinflip [testa/croce] [scommessa]`"
        )
        ctx.command.reset_cooldown(ctx)
        return
    scelta = scelta.lower()
    if scelta not in ["testa", "croce"]:
        ctx.command.reset_cooldown(ctx)
        return
    if not scommessa.isdigit():
        ctx.command.reset_cooldown(ctx)
        return
    cifra = int(scommessa)
    if cifra <= 0 or portafogli.get(user_id, 100) < cifra:
        ctx.command.reset_cooldown(ctx)
        return
    portafogli[user_id] = portafogli.get(user_id, 100) - cifra
    risultato = random.choice(["testa", "croce"])
    if scelta == risultato:  # 🛠️ CORRETTO QUI!
        portafogli[user_id] += cifra * 2
        await ctx.send(
            f"🪙 **COINFLIP:** È uscito **{risultato.upper()}**! 🎉 {ctx.author.mention} hai raddoppiato! Saldo: **{portafogli[user_id]}**."
        )
    else:
        await ctx.send(
            f"🪙 **COINFLIP:** È uscito **{risultato.upper()}**! ❌ {ctx.author.mention} hai perso. Saldo: **{portafogli[user_id]}**."
        )


# --- MINIGIOCO: CARTA FORBICE SASSO ---
@bot.command(name="rps")
@commands.cooldown(1, 3, commands.BucketType.user)
async def rock_paper_scissors(ctx, scelta: str = None, scommessa: str = None):
    user_id = ctx.author.id
    if scelta is None or scommessa is None:
        await ctx.send(
            f"❌ Uso corretto: `!rps [sasso/carta/forbice] [scommessa]`"
        )
        ctx.command.reset_cooldown(ctx)
        return
    scelta = scelta.lower()
    if scelta in ["forbice", "forbici"]:
        scelta = "forbice"
    if scelta not in ["sasso", "carta", "forbice"] or not scommessa.isdigit():
        ctx.command.reset_cooldown(ctx)
        return
    cifra = int(scommessa)
    if cifra <= 0 or portafogli.get(user_id, 100) < cifra:
        ctx.command.reset_cooldown(ctx)
        return
    portafogli[user_id] = portafogli.get(user_id, 100) - cifra
    mossa_bot = random.choice(["sasso", "carta", "forbice"])
    emojis = {"sasso": "🪨 Sasso", "carta": "📄 Carta", "forbice": "✂️ Forbice"}
    testo_base = f"Tu: **{emojis[scelta]}** VS Bot: **{emojis[mossa_bot]}**\n"
    if scelta == mossa_bot:
        portafogli[user_id] += cifra
        await ctx.send(f"{testo_base}🤝 **PAREGGIO!** Monete restituite.")
    elif (
        (scelta == "sasso" and mossa_bot == "forbice")
        or (scelta == "carta" and mossa_bot == "sasso")
        or (scelta == "forbice" and mossa_bot == "carta")
    ):
        portafogli[user_id] += cifra * 2
        await ctx.send(
            f"{testo_base}🎉 **HAI VINTO!** Nuovo saldo: **{portafogli[user_id]}**."
        )
    else:
        await ctx.send(
            f"{testo_base}❌ **HAI PERSO!** Il bot ti ha battuto. Hai perso **{cifra} monete**. Saldo: **{portafogli[user_id]}**."
        )


# --- COMANDO SLOT ORDINATO E CASUALE ---
@bot.command(name="slot")
@commands.cooldown(1, 5, commands.BucketType.user)
async def slot_machine(ctx, scommessa: str = None):
    user_id = ctx.author.id
    if scommessa is None or not scommessa.isdigit():
        await ctx.send(f"❌ Inserisci una cifra! Es: `!slot 10`")
        ctx.command.reset_cooldown(ctx)
        return
    cifra = int(scommessa)
    if cifra == 67:
        await ctx.send(f"🚪 {ctx.author.mention} **GET OUT**")
        ctx.command.reset_cooldown(ctx)
        return
    if cifra <= 0 or portafogli.get(user_id, 100) < cifra:
        ctx.command.reset_cooldown(ctx)
        return
    portafogli[user_id] = portafogli.get(user_id, 100) - cifra

    s1 = random.choice(EMOJI_SLOT)
    s2 = random.choice(EMOJI_SLOT)
    s3 = random.choice(EMOJI_SLOT)
    risultato_visivo = f"**[ {s1} | {s2} | {s3} ]**"

    if s1 == "💣" and s2 == "💣" and s3 == "💣":
        portafogli[user_id] = 0
        await ctx.send(
            f"{risultato_visivo}\n💥 {ctx.author.mention} è esploso! Il tuo portafoglio è a **0 monete**!"
        )
        return
    if s1 == s2 == s3:
        portafogli[user_id] += cifra * 10
        await ctx.send(
            f"🎉 **JACKPOT!** {risultato_visivo}\nHai vinto **{cifra*10} monete**! Saldo: **{portafogli[user_id]}**."
        )
    else:
        await ctx.send(
            f"❌ Hai perso! {risultato_visivo}\nHai perso **{cifra} monete**. Saldo: **{portafogli[user_id]}**."
        )


# --- 👑 COMANDI RISERVATI ALL'OWNER ---
@bot.command(name="add_soldi")
@commands.is_owner()
async def aggiungi_soldi(ctx, membro: discord.Member, cifra: int):
    portafogli[membro.id] = portafogli.get(membro.id, 100) + cifra
    await ctx.send(
        f"👑 **OWNER:** Aggiunte **{cifra} monete** a {membro.mention}."
    )


@bot.command(name="reset_soldi")
@commands.is_owner()
async def resettare_soldi(ctx, membro: discord.Member):
    portafogli[membro.id] = 100
    await ctx.send(f"🧹 **OWNER:** Il portafoglio di {membro.mention} è a 100.")


# --- GESTIONE ERRORI AVANZATA ---
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.CommandOnCooldown):
        sec = int(error.retry_after)
        ore = sec // 3600
        minuti = (sec % 3600) // 60
        secondi = sec % 60
        if ore > 0:
            tempo = f"{ore} ore, {minuti} min e {secondi} sec"
        elif minuti > 0:
            tempo = f"{minuti} min e {secondi} sec"
        else:
            tempo = f"{secondi} secondi"
        await ctx.send(f"⏳ {ctx.author.mention}, aspetta ancora **{tempo}**!")
    elif isinstance(error, commands.NotOwner):
        await ctx.send(
            f"🚫 {ctx.author.mention}, comando riservato al mio Creatore!"
        )
    else:
        raise error


# --- 3. AVVIO AUTOMATICO ---
if __name__ == "__main__":
    keep_alive()
    token = os.getenv("DISCORD_TOKEN")
    if token:
        bot.run(token)
