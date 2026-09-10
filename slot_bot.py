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
    return "Slot Machine Bot con Economia Completa è attivo!"


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


# --- 📜 NUOVO COMANDO: MENU DEI COMANDI ---
@bot.command(name="menu")
async def mostra_menu(ctx):
    testo_menu = (
        "🎰 **MENU COMANDI SLOT MACHINE** 🎰\n\n"
        "🔴 **Comandi per tutti i giocatori:**\n"
        "• `!menu` - Mostra questa lista di comandi.\n"
        "• `!soldi` - Controlla quante monete hai nel portafoglio.\n"
        "• `!daily` - Riscatta 50 monete gratis (una volta al giorno).\n"
        "• `!slot [cifra]` - Gioca alla slot machine (es: `!slot 10`).\n"
        "• `!classifica` - Mostra la classifica dei più ricchi del server.\n\n"
        "👑 *I comandi da Amministratore (!add_soldi, !reset_soldi) sono nascosti e utilizzabili solo dall'Owner.*"
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


# --- ⏳ COMANDO DAILY AGGIORNATO (Uso limitato a 1 volta ogni 24 ore) ---
@bot.command(name="daily")
@commands.cooldown(1, 86400, commands.BucketType.user)  # 86400 secondi = 24 ore
async def monete_giornaliere(ctx):
    user_id = ctx.author.id
    if user_id not in portafogli:
        portafogli[user_id] = 100

    portafogli[user_id] += 50
    await ctx.send(
        f"🎁 {ctx.author.mention}, hai riscattato **50 monete gratis**! Nuovo saldo: **{portafogli[user_id]} monete**."
    )


# --- 📊 NUOVO COMANDO: CLASSIFICA DEI PIÙ RICCHI ---
@bot.command(name="classifica")
async def mostra_classifica(ctx):
    if not portafogli:
        await ctx.send(
            "📊 La classifica è ancora vuota! Iniziate a giocare per comparire qui."
        )
        return

    # Ordina il dizionario dal più ricco al più povero
    classifica_ordinata = sorted(
        portafogli.items(), key=lambda item: item[1], reverse=True
    )

    testo_classifica = "🏆 **CLASSIFICA DEI PIÙ RICCHI** 🏆\n\n"

    # Mostra i primi 5 utenti (o meno se ce ne sono meno di 5)
    for i, (user_id, saldo) in enumerate(classifica_ordinata[:5], start=1):
        membro = ctx.guild.get_member(user_id)
        nome = membro.display_name if membro else f"Utente {user_id}"

        # Assegna delle medaglie speciali ai primi 3 posti
        if i == 1:
            medaglia = "🥇"
        elif i == 2:
            medaglia = "🥈"
        elif i == 3:
            medaglia = "🥉"
        else:
            medaglia = f"**#{i}**"

        testo_classifica += f"{medaglia} **{nome}** — {saldo} monete\n"

    await ctx.send(testo_classifica)


# --- 👑 COMANDO OWNER: AGGIUNGI SOLDI ---
@bot.command(name="add_soldi")
@commands.is_owner()
async def aggiungi_soldi(ctx, membro: discord.Member, cifra: int):
    if membro.id not in portafogli:
        portafogli[membro.id] = 100

    membro_id = membro.id
    portafogli[membro_id] += cifra
    await ctx.send(
        f"👑 **OWNER ACTION:** Aggiunte **{cifra} monete** a {membro.mention}! Nuovo saldo: **{portafogli[membro_id]} monete**."
    )


# --- 👑 COMANDO OWNER: RESETTA SOLDI ---
@bot.command(name="reset_soldi")
@commands.is_owner()
async def resetta_soldi(ctx, membro: discord.Member):
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
        portafogli[user_id] = 0
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


# --- GESTIONE ERRORI AVANZATA ---
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        # Calcoliamo le ore, minuti e secondi rimasti per il cooldown
        secondi_rimasti = int(error.retry_after)
        ore = secondi_rimasti // 3600
        minuti = (secondi_rimasti % 3600) // 60
        secondi = secondi_rimasti % 60

        if ore > 0:
            tempo_testo = f"{ore} ore, {minuti} minuti e {secondi} secondi"
        elif minuti > 0:
            tempo_testo = f"{minuti} minuti e {secondi} secondi"
        else:
            tempo_testo = f"{secondi:.1f} secondi"

        await ctx.send(
            f"⏳ {ctx.author.mention}, devi aspettare ancora **{tempo_testo}** prima di poter riutilizzare questo comando!"
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
            "ERRORE: Non è stata trovata la variabile d'ambiente DISCORD_TOKEN!"
        )
