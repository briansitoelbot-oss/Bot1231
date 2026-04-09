import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio
from database import (
    get_or_create_user, get_user, update_balance, set_balance,
    get_code, create_code, update_code, use_code
)
from config import ADMIN_ROLE_ID, TOKEN
from keep_alive import keep_alive
keep_alive()
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

ALLOWED_CHANNEL_ID = 1490094481998090452

def channel_check(interaction: discord.Interaction):
    return interaction.channel_id == ALLOWED_CHANNEL_ID

def has_admin_role(interaction: discord.Interaction) -> bool:
    if interaction.user.guild_permissions.administrator:
        return True
    for role in interaction.user.roles:
        if role.id == ADMIN_ROLE_ID:
            return True
    return False

async def setup_user(interaction: discord.Interaction):
    user_id = interaction.user.id
    get_or_create_user(user_id)

def create_embed(title, description, color=discord.Color.blue()):
    return discord.Embed(title=title, description=description, color=color)

def create_error_embed(description):
    return create_embed("Error", description, discord.Color.red())

def create_success_embed(description):
    return create_embed("Exito", description, discord.Color.green())

def channel_check():
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.channel_id != ALLOWED_CHANNEL_ID:
            await interaction.response.send_message("Este comando no está disponible en este canal.", ephemeral=True)
            return False
        return True
    return app_commands.check(predicate)

def has_admin_role(interaction: discord.Interaction) -> bool:
    if interaction.user.guild_permissions.administrator:
        return True
    for role in interaction.user.roles:
        if role.id == ADMIN_ROLE_ID:
            return True
    return False

async def setup_user(interaction: discord.Interaction):
    user_id = interaction.user.id
    get_or_create_user(user_id)

def create_embed(title, description, color=discord.Color.blue()):
    return discord.Embed(title=title, description=description, color=color)

def create_error_embed(description):
    return create_embed("Error", description, discord.Color.red())

def create_success_embed(description):
    return create_embed("Exito", description, discord.Color.green())

@bot.tree.command(name="bal", description="Muestra tu balance actual")
@channel_check()
async def bal(interaction: discord.Interaction):
    balance = get_user(interaction.user.id)[0]
    embed = create_embed("💰 Balance", f"**{interaction.user.name}**, tu balance es de `{balance}` monedas")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="addmoney", description="Añadir dinero a un usuario")
@app_commands.describe(user="Usuario", amount="Cantidad")
@channel_check()
async def addmoney(interaction: discord.Interaction, user: discord.User, amount: int):
    if not has_admin_role(interaction):
        embed = create_error_embed("No tienes permiso para usar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if amount <= 0:
        embed = create_error_embed("La cantidad debe ser mayor a 0.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    get_or_create_user(user.id)
    update_balance(user.id, amount)
    embed = create_success_embed(f"Se han añadido `{amount}` monedas a {user.name}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="removemoney", description="Quitar dinero a un usuario")
@app_commands.describe(user="Usuario", amount="Cantidad")
@channel_check()
async def removemoney(interaction: discord.Interaction, user: discord.User, amount: int):
    if not has_admin_role(interaction):
        embed = create_error_embed("No tienes permiso para usar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if amount <= 0:
        embed = create_error_embed("La cantidad debe ser mayor a 0.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    get_or_create_user(user.id)
    current_balance = get_user(user.id)[0]
    if current_balance < amount:
        embed = create_error_embed(f"El usuario solo tiene `{current_balance}` monedas.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    update_balance(user.id, -amount)
    embed = create_success_embed(f"Se han quitado `{amount}` monedas a {user.name}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="createcode", description="Crear un código inactivo")
@app_commands.describe(code="Código", value="Valor del código")
@channel_check()
async def createcode(interaction: discord.Interaction, code: str, value: int):
    if not has_admin_role(interaction):
        embed = create_error_embed("No tienes permiso para usar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if value <= 0:
        embed = create_error_embed("El valor debe ser mayor a 0.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    existing = get_code(code)
    if existing:
        embed = create_error_embed("El código ya existe.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    create_code(code, value)
    embed = create_success_embed(f"Código `{code}` creado con valor `{value}`. Estado: INACTIVO")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="codeactivate", description="Activar un código")
@app_commands.describe(code="Código a activar")
@channel_check()
async def codeactivate(interaction: discord.Interaction, code: str):
    if not has_admin_role(interaction):
        embed = create_error_embed("No tienes permiso para usar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    code_data = get_code(code)
    if not code_data:
        embed = create_error_embed("El código no existe.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if code_data['active']:
        embed = create_error_embed("El código ya está activo.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    update_code(code, active=True)
    embed = create_success_embed(f"Código `{code}` activado correctamente")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="setcodevalue", description="Cambiar el valor de un código")
@app_commands.describe(code="Código", value="Nuevo valor")
@channel_check()
async def setcodevalue(interaction: discord.Interaction, code: str, value: int):
    if not has_admin_role(interaction):
        embed = create_error_embed("No tienes permiso para usar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if value <= 0:
        embed = create_error_embed("El valor debe ser mayor a 0.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    code_data = get_code(code)
    if not code_data:
        embed = create_error_embed("El código no existe.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    update_code(code, value=value)
    embed = create_success_embed(f"El valor del código `{code}` ahora es `{value}`")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="disablecode", description="Desactivar un código")
@app_commands.describe(code="Código a desactivar")
@channel_check()
async def disablecode(interaction: discord.Interaction, code: str):
    if not has_admin_role(interaction):
        embed = create_error_embed("No tienes permiso para usar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    code_data = get_code(code)
    if not code_data:
        embed = create_error_embed("El código no existe.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if not code_data['active']:
        embed = create_error_embed("El código ya está inactivo.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    update_code(code, active=False)
    embed = create_success_embed(f"Código `{code}` desactivado correctamente")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="code", description="Canjear un código")
@app_commands.describe(code="Código a canjear")
@channel_check()
async def redeem_code(interaction: discord.Interaction, code: str):
    await setup_user(interaction)
    
    code_data = get_code(code)
    if not code_data:
        embed = create_error_embed("El código no existe.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if not code_data['active']:
        embed = create_error_embed("El código está inactivo.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if interaction.user.id in code_data['used_by']:
        embed = create_error_embed("Ya has canjeado este código antes.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    use_code(code, interaction.user.id)
    update_balance(interaction.user.id, code_data['value'])
    
    embed = create_success_embed(f"¡Has canjeado el código! Has recibido `{code_data['value']}` monedas")
    await interaction.response.send_message(embed=embed)

def calculate_hand(hand):
    total = 0
    aces = 0
    for card in hand:
        rank = card[:-1]
        if rank in ['J', 'Q', 'K']:
            total += 10
        elif rank == 'A':
            aces += 1
            total += 11
        else:
            total += int(rank)
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total

def create_deck():
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    suits = ['S', 'H', 'D', 'C']
    deck = [f"{rank}{suit}" for rank in ranks for suit in suits]
    random.shuffle(deck)
    return deck

@bot.tree.command(name="blackjack", description="Jugar Blackjack")
@channel_check()
@app_commands.describe(bet="Apuesta")
async def blackjack(interaction: discord.Interaction, bet: int):
    try:
        await setup_user(interaction)
        balance = get_user(interaction.user.id)[0]
        
        if bet <= 0:
            embed = create_error_embed("La apuesta debe ser mayor a 0.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if bet > balance:
            embed = create_error_embed(f"No tienes suficiente dinero. Tu balance: {balance}")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        deck = create_deck()
        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]
        
        player_total = calculate_hand(player_hand)
        dealer_total = calculate_hand(dealer_hand)
        
        view = BlackjackView(interaction.user.id, bet, player_hand, dealer_hand, deck, player_total, dealer_total)
        embed = create_embed("Blackjack", f"Tu: {player_total} | Dealer: {dealer_hand[0]}")
        await interaction.response.send_message(embed=embed, view=view)
    except Exception as e:
        print(f"Error in blackjack: {e}")
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

class BlackjackView(discord.ui.View):
    def __init__(self, user_id, bet, player_hand, dealer_hand, deck, player_total, dealer_total):
        super().__init__()
        self.user_id = user_id
        self.bet = bet
        self.player_hand = player_hand
        self.dealer_hand = dealer_hand
        self.deck = deck
        self.player_total = player_total
        self.dealer_total = dealer_total

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.green, custom_id="bj_hit")
    async def hit(self, interaction: discord.Interaction, button: discord.Button):
        self.player_hand.append(self.deck.pop())
        self.player_total = calculate_hand(self.player_hand)
        
        if self.player_total > 21:
            update_balance(self.user_id, -self.bet)
            embed = create_embed("Blackjack - PERDISTE", f"Tu: {self.player_total} | Dealer: {self.dealer_total}\nPerdiste {self.bet}")
            await interaction.response.edit_message(embed=embed, view=None)
        else:
            embed = create_embed("Blackjack", f"Tu: {self.player_total} | Dealer: {self.dealer_hand[0]}")
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.red, custom_id="bj_stand")
    async def stand(self, interaction: discord.Interaction, button: discord.Button):
        while self.dealer_total < 17:
            self.dealer_hand.append(self.deck.pop())
            self.dealer_total = calculate_hand(self.dealer_hand)
        
        if self.dealer_total > 21:
            update_balance(self.user_id, self.bet)
            embed = create_embed("Blackjack - GANASTE", f"Tu: {self.player_total} | Dealer: {self.dealer_total}\nGanaste {self.bet}")
        elif self.player_total > self.dealer_total:
            update_balance(self.user_id, self.bet)
            embed = create_embed("Blackjack - GANASTE", f"Tu: {self.player_total} | Dealer: {self.dealer_total}\nGanaste {self.bet}")
        elif self.player_total < self.dealer_total:
            update_balance(self.user_id, -self.bet)
            embed = create_embed("Blackjack - PERDISTE", f"Tu: {self.player_total} | Dealer: {self.dealer_total}\nPerdiste {self.bet}")
        else:
            embed = create_embed("Blackjack - EMPATE", f"Tu: {self.player_total} | Dealer: {self.dealer_total}\nEmpate")
        
        await interaction.response.edit_message(embed=embed, view=None)

@bot.tree.command(name="coinflip", description="Jugar Cara o Cruz")
@channel_check()
@app_commands.describe(bet="Apuesta", choice="Elección")
@app_commands.choices(choice=[
    app_commands.Choice(name="Cara", value="heads"),
    app_commands.Choice(name="Cruz", value="tails")
])
async def coinflip(interaction: discord.Interaction, bet: int, choice: str):
    await setup_user(interaction)
    balance = get_user(interaction.user.id)[0]
    
    if bet <= 0:
        embed = create_error_embed("La apuesta debe ser mayor a 0.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if bet > balance:
        embed = create_error_embed(f"No tienes suficiente dinero. Tu balance: `{balance}`")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    result = random.choice(["heads", "tails"])
    choice_name = "Cara" if choice == "heads" else "Cruz"
    result_name = "Cara" if result == "heads" else "Cruz"
    
    if choice == result:
        update_balance(interaction.user.id, bet)
        embed = create_embed("🪙 Coinflip - ¡GANASTE!", f"Elegiste: **{choice_name}**\nResultado: **{result_name}**\n\n¡Ganaste `{bet}` monedas!")
    else:
        update_balance(interaction.user.id, -bet)
        embed = create_embed("🪙 Coinflip - PERDISTE", f"Elegiste: **{choice_name}**\nResultado: **{result_name}**\n\nPerdiste `{bet}` monedas.")
    
    await interaction.response.send_message(embed=embed)

MINES_CONFIG = {
    "mines": 3,
    "grid_size": 4
}

class MinesButton(discord.ui.Button):
    def __init__(self, row, col, callback):
        super().__init__(label="❓", style=discord.ButtonStyle.secondary, row=row)
        self.row = row
        self.col = col
        self.callback = callback

    async def callback(self, interaction):
        pass

class MinesView(discord.ui.View):
    def __init__(self, user_id, bet, grid, revealed, mines_positions, multiplier):
        super().__init__()
        self.user_id = user_id
        self.bet = bet
        self.grid = grid
        self.revealed = revealed
        self.mines_positions = mines_positions
        self.multiplier = multiplier

def calculate_mines_multiplier(safe_count, total_cells=16, mines=3):
    base_multiplier = 1.0
    for i in range(safe_count):
        base_multiplier *= (total_cells - mines - i) / (total_cells - i)
    return round((1 / base_multiplier) * 0.95, 2)

@bot.tree.command(name="mines", description="Jugar Minas")
@channel_check()
@app_commands.describe(bet="Apuesta", mines="Numero de minas (1-11)")
async def mines(interaction: discord.Interaction, bet: int, mines: int = 3):
    try:
        await setup_user(interaction)
        balance = get_user(interaction.user.id)[0]
        
        if bet <= 0:
            embed = create_error_embed("La apuesta debe ser mayor a 0.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if mines < 1 or mines > 11:
            embed = create_error_embed("Las minas deben ser entre 1 y 11.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        grid_size = 3
        
        mines_positions = set()
        attempts = 0
        while len(mines_positions) < mines and attempts < 100:
            row = random.randint(0, 2)
            col = random.randint(0, 3)
            mines_positions.add((row, col))
            attempts += 1
        
        game = {
            "bet": bet,
            "mines": mines_positions,
            "revealed": set(),
            "multiplier": 1.0,
            "active": True
        }
        
        view = MinesGameView(interaction.user.id, game, grid_size, mines)
        embed = create_embed("Minas", f"Apuesta: {bet} | Minas: {mines}/11 | Multiplicador: x1.00")
        await interaction.response.send_message(embed=embed, view=view)
    except Exception as e:
        print(f"Error in mines: {e}")
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

class MinesGameView(discord.ui.View):
    def __init__(self, user_id, game, grid_size, mines_count):
        super().__init__()
        self.user_id = user_id
        self.game = game
        self.grid_size = grid_size
        self.mines_count = mines_count
        self.buttons = {}
    
    @discord.ui.button(label="?", style=discord.ButtonStyle.secondary, custom_id="m0")
    async def b0(self, interaction, button): await self.handle(interaction, button, 0)
    
    @discord.ui.button(label="?", style=discord.ButtonStyle.secondary, custom_id="m1")
    async def b1(self, interaction, button): await self.handle(interaction, button, 1)
    
    @discord.ui.button(label="?", style=discord.ButtonStyle.secondary, custom_id="m2")
    async def b2(self, interaction, button): await self.handle(interaction, button, 2)
    
    @discord.ui.button(label="?", style=discord.ButtonStyle.secondary, custom_id="m3")
    async def b3(self, interaction, button): await self.handle(interaction, button, 3)
    
    @discord.ui.button(label="?", style=discord.ButtonStyle.secondary, custom_id="m4")
    async def b4(self, interaction, button): await self.handle(interaction, button, 4)
    
    @discord.ui.button(label="?", style=discord.ButtonStyle.secondary, custom_id="m5")
    async def b5(self, interaction, button): await self.handle(interaction, button, 5)
    
    @discord.ui.button(label="?", style=discord.ButtonStyle.secondary, custom_id="m6")
    async def b6(self, interaction, button): await self.handle(interaction, button, 6)
    
    @discord.ui.button(label="?", style=discord.ButtonStyle.secondary, custom_id="m7")
    async def b7(self, interaction, button): await self.handle(interaction, button, 7)
    
    @discord.ui.button(label="?", style=discord.ButtonStyle.secondary, custom_id="m8")
    async def b8(self, interaction, button): await self.handle(interaction, button, 8)
    
    @discord.ui.button(label="?", style=discord.ButtonStyle.secondary, custom_id="m9")
    async def b9(self, interaction, button): await self.handle(interaction, button, 9)
    
    @discord.ui.button(label="?", style=discord.ButtonStyle.secondary, custom_id="m10")
    async def b10(self, interaction, button): await self.handle(interaction, button, 10)
    
    @discord.ui.button(label="?", style=discord.ButtonStyle.secondary, custom_id="m11")
    async def b11(self, interaction, button): await self.handle(interaction, button, 11)
    
    @discord.ui.button(label="Cash Out", style=discord.ButtonStyle.red, custom_id="cashout")
    async def cashout(self, interaction, button):
        if not self.game["active"]:
            await interaction.response.send_message("Game over", ephemeral=True)
            return
        self.game["active"] = False
        winnings = int(self.game["bet"] * self.game["multiplier"])
        update_balance(self.user_id, winnings)
        embed = create_embed("Minas - CASH OUT", f"Ganaste {winnings} monedas")
        await interaction.response.edit_message(embed=embed, view=None)

    async def handle(self, interaction, button, index):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("No puedes usar esto", ephemeral=True)
            return
        
        if not self.game["active"]:
            await interaction.response.send_message("Game over", ephemeral=True)
            return
        
        if index in self.game["revealed"]:
            await interaction.response.send_message("Ya seleccionado", ephemeral=True)
            return
        
        self.game["revealed"].add(index)
        row = index // 4
        col = index % 4
        
        if (row, col) in self.game["mines"]:
            self.game["active"] = False
            update_balance(self.user_id, -self.game["bet"])
            
            for i in range(12):
                r = i // 4
                c = i % 4
            self.game["active"] = False
            update_balance(self.user_id, -self.game["bet"])
            
            for i in range(12):
                r = i // 4
                c = i % 4
                btn = self.children[i]
                if (r, c) in self.game["mines"]:
                    btn.emoji = "💣"
                    btn.style = discord.ButtonStyle.danger
                else:
                    btn.emoji = "💎"
                    btn.style = discord.ButtonStyle.success
                btn.disabled = True
            
            button.emoji = "💣"
            button.style = discord.ButtonStyle.danger
            
            for child in self.children:
                if hasattr(child, 'custom_id') and child.custom_id == "cashout":
                    child.disabled = True
            
            embed = create_embed("Minas - PERDISTE", f"Perdiste {self.game['bet']} monedas")
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            safe_count = len(self.game["revealed"])
            self.game["multiplier"] = calculate_mines_multiplier(safe_count, 12, self.mines_count)
            button.emoji = "💎"
            button.style = discord.ButtonStyle.success
            button.disabled = True
            
            if safe_count >= 12 - self.mines_count:
                self.game["active"] = False
                winnings = int(self.game["bet"] * self.game["multiplier"])
                update_balance(self.user_id, winnings)
                embed = create_embed("Minas - GANASTE", f"Ganaste {winnings} monedas")
                await interaction.response.edit_message(embed=embed, view=None)
            else:
                embed = create_embed("Minas", f"Multiplicador: x{self.game['multiplier']:.2f}")
                await interaction.response.edit_message(embed=embed, view=self)

@bot.tree.command(name="carrera", description="Carrera de caballos")
@channel_check()
@app_commands.describe(bet="Apuesta", horse="Número del caballo (1-8)")
async def carrera(interaction: discord.Interaction, bet: int, horse: int):
    await setup_user(interaction)
    balance = get_user(interaction.user.id)[0]
    
    if bet <= 0:
        embed = create_error_embed("La apuesta debe ser mayor a 0.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if bet > balance:
        embed = create_error_embed(f"No tienes suficiente dinero. Tu balance: `{balance}`")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if horse < 1 or horse > 8:
        embed = create_error_embed("El caballo debe estar entre 1 y 8.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    horses = ["🐎", "🦄", "🐴", "🦓", "🐎", "🦄", "🐴", "🦓"]
    positions = [0] * 8
    track_length = 10
    
    embed = create_embed("🏇 Carrera de Caballos", "La carrera está comenzando...")
    await interaction.response.send_message(embed=embed)
    
    winner = None
    while winner is None:
        await asyncio.sleep(1)
        
        for i in range(8):
            if random.random() < 0.6:
                positions[i] += 1
        
        for i in range(8):
            if positions[i] >= track_length:
                winner = i + 1
                break
        
        track_display = "```\n"
        for i in range(8):
            track_display += f"Caballo {i+1}: {'▶' * positions[i]} {horses[i]}\n"
        track_display += "```"
        
        embed = create_embed("🏇 Carrera de Caballos", track_display)
        await interaction.edit_original_response(embed=embed)
    
    if winner == horse:
        winnings = bet * 7
        update_balance(interaction.user.id, bet * 7)
        embed = create_embed("🏇 Carrera - ¡GANASTE!", f"¡Tu caballo (#{horse}) ganó!\n\nGanaste `{winnings}` monedas")
    else:
        update_balance(interaction.user.id, -bet)
        embed = create_embed("🏇 Carrera - PERDISTE", f"El caballo #{winner} ganó\n\nPerdiste `{bet}` monedas")
    
    await interaction.edit_original_response(embed=embed)

@bot.event
async def on_ready():
    print(f"Bot connected: {bot.user}")
    await bot.tree.sync()
    print("Commands synced")
    print(f"Guilds: {len(bot.guilds)}")

if __name__ == "__main__":
    from database import init_db
    init_db()
    bot.run(TOKEN)
