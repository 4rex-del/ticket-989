import discord
import os
from discord.ext import commands
from discord import utils, app_commands
import datetime, pytz

from myserver import server_on

tz = pytz.timezone('Asia/Bangkok')

channelid = "1412433107574849577"  # ไอดี log
channelCategory = "1411575398780764251"  # ไอดีหมวดหมู่
adminid = "1400471054295502849"  # ไอดีแอดมิน
owner_id = "1400471054295502849"  # ไอดีเจ้าของดิส


def now():
    now1 = datetime.datetime.now(tz)
    months = ["มกราคม","กุมภาพันธ์","มีนาคม","เมษายน","พฤษภาคม","มิถุนายน",
              "กรกฎาคม","สิงหาคม","กันยายน","ตุลาคม","พฤศจิกายน","ธันวาคม"]
    month_name = months[now1.month - 1]
    thai_year = now1.year
    time_str = now1.strftime('%H:%M:%S')
    return "%d %s %d %s" % (now1.day, month_name, thai_year, time_str)


class Message(discord.ui.Modal, title='Feedback'):
    def __init__(self):
        super().__init__(title='Ticket', timeout=None, custom_id='ticket_model_001')

    message = discord.ui.TextInput(
        label='ติดต่อแอดมิน',
        style=discord.TextStyle.long,
        placeholder='เขียนเรื่องที่ต้องการติดต่อ',
    )

    async def on_submit(self, interaction: discord.Interaction):
        message = self.message.value
        member = interaction.user
        category = discord.utils.get(member.guild.categories, id=int(channelCategory))
        ticket = utils.get(
            interaction.guild.text_channels,
            name=f"{interaction.user.name.lower().replace(' ', '-')}-{interaction.user.discriminator}"
        )

        if ticket is not None:
            embed = discord.Embed(
                title="แจ้งเตือน",
                description=f"คุณมี Ticket เปิดอยู่แล้วที่ {ticket.mention}!",
                color=0xfa0d0d
            )
            embed.set_footer(text=now())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                ),
                interaction.guild.me: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                ),
            }
            channel = await interaction.guild.create_text_channel(
                f"{interaction.user.name}-{interaction.user.discriminator}",
                overwrites=overwrites,
                category=category
            )
            embed1 = discord.Embed(
                title="ดำเนินการสำเร็จ",
                description=f"สร้างห้องสำเร็จ {channel.mention}",
                color=0x1BE51B
            )
            await interaction.response.send_message(embed=embed1, ephemeral=True)

            embed2 = discord.Embed(
                title="สร้างตั๋ว",
                description=f"{interaction.user.mention} แอดมิน <@{adminid}>\n```ติดต่อเรื่อง {message}```\nโปรดรอแอดมินมาตอบครับ",
                color=0xdddddd
            )
            embed2.set_image(
                url="https://cdn.discordapp.com/attachments/1166453203764789410/1176917209554092133/7cfef8409d92517cc9ab6a2ecf8730de.gif"
            )
            await channel.send(embed=embed2, view=Close_ticket())

            userid = interaction.user.id
            embed1 = discord.Embed(
                title="เปิด Ticket",
                description=f"เปิด Ticket โดย <@{userid}> ห้อง {channel.mention}",
                color=0x1BE51B
            )
            embed1.set_footer(text=now())
            channel1 = discord.utils.get(member.guild.channels, id=int(channelid))
            await channel1.send(embed=embed1)


class Create_ticket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        emoji="🎫",  # Unicode emoji
        label="สร้างตั๋ว",
        style=discord.ButtonStyle.green,
        custom_id="ticket_button_001"
    )
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(Message())


class Close_ticket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        emoji="❌",  # Unicode emoji
        label="ปิด Ticket",
        style=discord.ButtonStyle.red,
        custom_id="ticket_button_002"
    )
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user
        perms = interaction.channel.overwrites_for(member)
        perms.view_channel = False
        await interaction.channel.set_permissions(member, overwrite=perms)

        await interaction.response.send_message(view=Confirm_close_ticket())

        userid = interaction.user.id
        embed = discord.Embed(
            title="ปิด Ticket",
            description=f"ปิด Ticket โดย <@{userid}> ห้อง {interaction.channel.mention}",
            color=0xfa0d0d
        )
        embed.set_footer(text=now())
        channel = discord.utils.get(member.guild.channels, id=int(channelid))
        await channel.send(embed=embed)


class Confirm_close_ticket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        emoji="🗑️",  # Unicode emoji
        label="ลบ Ticket",
        style=discord.ButtonStyle.red,
        custom_id="ticket_button_003"
    )
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.channel.delete()
        userid = interaction.user.id
        embed = discord.Embed(
            title="ลบ Ticket",
            description=f"ลบ Ticket โดย <@{userid}>",
            color=0xfa0d0d
        )
        embed.set_footer(text=now())
        channel = discord.utils.get(interaction.guild.channels, id=int(channelid))
        await channel.send(embed=embed)


class MyBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix='!',
            help_command=None,
            case_insensitive=True,
            intents=intents,
        )

    async def on_ready(self) -> None:
        streaming = discord.Streaming(
            name="พร้อมใช้งาน💜",
            url="https://www.youtube.com/"
        )
        await self.change_presence(activity=streaming)
        print(f"✅ บอทออนไลน์แล้ว: {self.user}")
        try:
            synced = await self.tree.sync()
            print(f"✅ ซิง Slash Commands แล้ว {len(synced)} คำสั่ง")
        except Exception as e:
            print(f"❌ Sync error: {e}")

    async def setup_hook(self) -> None:
        self.add_view(Create_ticket())


bot = MyBot()


# ----------------- Slash Command /setup -----------------
@bot.tree.command(name="setup", description="ติดตั้งระบบตั๋วสอบถาม/ซื้อของ")
@app_commands.checks.has_permissions(administrator=True)
async def setup(interaction: discord.Interaction):
    embed = discord.Embed(
        title="สอบถาม / ซื้อของ",
        description="\n\nสำหรับ สอบถาม แจ้งปัญหา ซื้อของ\nเราจะปิด ticket ภายใน 30นาที หากไม่มีการตอบกลับจากลูกค้า\nกดเล่นแบนทันที",
        color=0xdddddd
    )
    embed.set_image(
        url='https://media.discordapp.net/attachments/1411575487096164522/1411580378254147704/1276_20250831121606.png'
    )
    embed.set_footer(text="BOT SEVER  © discord.gg/")
    await interaction.response.send_message(embed=embed, view=Create_ticket())

server_on()

bot.run(os.get('TOKEN'))