import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
from gtts import gTTS
from datetime import datetime
import os
import asyncio
from keep_alive import keep_alive
from collections import deque
import pytz
import re
from datetime import datetime, timedelta
import random

queue = deque()
keep_alive()
ffmpegOptions = {'options': "-vn"}

os.system('clear')


class color():
    green = '\033[92m'
    pink = '\033[95m'
    red = '\33[91m'
    yellow = '\33[93m'
    blue = '\33[94m'
    gray = '\33[90m'
    reset = '\33[0m'
    bold = '\33[1m'
    italic = '\33[3m'
    unline = '\33[4m'


bot = commands.Bot(command_prefix='_', intents=discord.Intents.all())
bot.remove_command('help')
voice = None
playing = False


@bot.event
async def on_ready():
    print(
        f'{color.gray + color.bold}{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} {color.blue}CONSOLE{color.reset}  {color.pink}discord.on_ready{color.reset} Đã đăng nhập bot {color.bold}{bot.user}{color.reset}'
    )
    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Activity(
                                  type=discord.ActivityType.listening,
                                  name='Bích Phương\'s playlist'))


async def send_welcome_message(channel, message, color=0xFFFF00):
    try:
        embed = discord.Embed(description=message, color=color)
        await channel.send(embed=embed)
    except Exception as e:
        print(e)


@bot.event
async def on_voice_state_update(member, before, after):
    global voice
    if voice is None:
        return

    if len(voice.channel.members) > 1:
        if member == bot.user:
            await send_welcome_message(
                voice.channel,
                f" <:pinkdotlkn:1196832522319962193> Hello <a:zduoitrailkn:1227211088433512509><@{member.id}><a:zduoiphailkn:1227211085359091742> bạn vừa rơi vào phòng <#{after.channel.id}> <a:3Kellylkng:1192105215474798632> 𝑇𝑖𝑚𝑒 𝑡𝑜 𝑟𝑒𝑙𝑎𝑥 <:abrightheart:1170204306507563068>"
            )
            return

    if before.channel != after.channel:
        if after.channel is not None:  # Kiểm tra nếu phòng sau di chuyển không phải None
            if member.bot:  # Kiểm tra nếu thành viên mới tham gia là bot
                await send_bot_welcome_message(after.channel,
                                               member)  # Truyền thông tin bot
            else:
                await send_welcome_message(
                    after.channel,
                    f"<:pinkdotlkn:1196832522319962193> Hello  <a:zduoitrailkn:1227211088433512509> <@{member.id}> <a:zduoiphailkn:1227211085359091742>  bạn vừa rơi vào phòng <#{after.channel.id}><a:3Kellylkng:1192105215474798632> 𝑇𝑖𝑚𝑒 𝑡𝑜 𝑟𝑒𝑙𝑎𝑥  <:abrightheart:1170204306507563068>"
                )

        if before.channel is not None:  # Kiểm tra xem có phải là sự kiện rời khỏi phòng không
            if member == bot.user:
                return
            await send_welcome_message(
                before.channel,
                f" <:pinkdotlkn:1196832522319962193> {member.display_name} đã đi ngủ <:3kellysleep:1192450487295942717>",
                color=0xFF0000)


async def send_bot_welcome_message(channel, bot):
    try:
        bot_mention = bot.mention  # Lấy đề cập đến bot
        embed = discord.Embed(
            description=
            f"<:pinkdotlkn:1196832522319962193> Triệu hồi thành công {bot_mention}",
            color=0xFFFF00)
        await channel.send(embed=embed)
    except Exception as e:
        print(e)


@bot.command(name='join')
async def join(ctx):
    global voice

    if ctx.author.voice is None:
        await ctx.send('Tạo room voice chat đi bae ~')
        return

    if ctx.voice_client is not None:
        await ctx.voice_client.move_to(ctx.author.voice.channel)
    else:
        voice = await ctx.author.voice.channel.connect()


@bot.command(name='s')
async def s(ctx, *, arg: str):
    global voice, playing

    if not arg:
        return

    if ctx.message.author.voice is None:
        await ctx.send('Tạo room voicechat đê!')
        return

    if ctx.guild.voice_client is None:
        try:
            voice = await ctx.message.author.voice.channel.connect()
        except Exception as e:
            print('error', e)
            return
    elif ctx.guild.voice_client.channel != ctx.message.author.voice.channel:
        await ctx.send('Đang ở voice chat khác')
        return

    tts = gTTS(text=arg, lang='vi')
    tts.save('tts-audio.mp3')
    queue.append(('tts-audio.mp3', ctx))
    if not playing:
        await play_next()


async def play_next():
    global playing
    if queue:
        playing = True
        file, ctx = queue.popleft()
        voice.play(FFmpegPCMAudio(file),
                   after=lambda e: asyncio.run_coroutine_threadsafe(
                       play_next(), bot.loop))
        while voice.is_playing():
            await asyncio.sleep(1)
        os.remove(file)
        playing = False
    else:
        playing = False


@bot.event
async def on_message(message):
    # ID của phòng cần xóa tin nhắn
    target_channel_id = 1160783455706161243  # Thay thế bằng ID của phòng cần xóa tin nhắn

    # Kiểm tra nếu tin nhắn được gửi trong phòng voice chat cần xóa tin nhắn
    if message.channel.id == target_channel_id:
        # Xóa tin nhắn
        await message.delete()

    # Tiếp tục xử lý các sự kiện khác
    await bot.process_commands(message)


@bot.command(name='leave')
async def leave(ctx):
    global voice, playing

    if ctx.guild.voice_client is None:
        await ctx.send('Bot không ở trong room này')
        return

    if voice is not None and voice.is_playing():
        voice.stop()

    await ctx.guild.voice_client.disconnect()
    voice = None
    playing = False


@bot.event
async def on_guild_channel_create(channel):
    # Kiểm tra nếu kênh mới tạo là một phòng voice chat
    if isinstance(channel, discord.VoiceChannel):
        # Gửi trạng thái bot nhạc vào phòng voice chat mới tạo sau 3 giây
        await asyncio.sleep(3)
        await musicbot(channel)


async def musicbot(voice_channel):
    music_role_id = 1152916515591561239
    guild = voice_channel.guild

    music_members = [
        member for member in guild.members
        if any(role.id == music_role_id for role in member.roles)
    ]
    active_members = [
        member for member in voice_channel.members if member in music_members
    ]

    if not active_members:
        return

    total_active_bots = len(active_members)

    active_embed = discord.Embed(
        title="Thông tin bot nhạc<a:aPanheart2:1164812699482468422>",
        color=discord.Color.green())
    active_embed.add_field(name="Tổng số bot nhạc đang phát",
                           value=f"{total_active_bots}",
                           inline=False)
    active_embed.add_field(
        name=f"Phòng: {voice_channel.mention}",
        value=" ".join([member.display_name for member in active_members]),
        inline=False)

    # Gửi embed vào phòng voice chat mới tạo
    await voice_channel.send(embed=active_embed)


@bot.command(name='musicbot')
async def musicbot(ctx):
    music_role_id = 1152916515591561239
    voice_channels = ctx.guild.voice_channels

    if not voice_channels:
        await ctx.send("Không có bot nhạc nào đang hoạt động trong server")
        return

    active_music_bots = {}
    inactive_music_bots = set()
    error_music_bots = set()  # Danh sách bot không online

    music_members = [
        member for member in ctx.guild.members
        if any(role.id == music_role_id for role in member.roles)
    ]

    total_music_bots = len(music_members)
    total_active_bots = 0

    # Tạo danh sách bot lỗi và bot chưa được sử dụng
    for member in music_members:
        if member.status == discord.Status.offline:
            error_music_bots.add(
                member)  # Thêm bot không online vào danh sách bot lỗi
        elif member.voice:  # Kiểm tra bot đang ở trong phòng voice chat
            total_active_bots += 1
        else:
            inactive_music_bots.add(
                member
            )  # Thêm bot không đang hoạt động vào danh sách bot chưa được sử dụng

    active_embed = discord.Embed(
        title="Thông tin bot nhạc<a:aPanheart2:1164812699482468422>",
        color=discord.Color.red())
    active_embed.add_field(name="Tổng số bot nhạc đang phát",
                           value=f"{total_active_bots}/{total_music_bots}",
                           inline=False)
    for voice_channel in voice_channels:
        active_members = [
            member for member in voice_channel.members
            if member in music_members
        ]
        if active_members:
            bot_list = ""
            for bot in active_members:
                bot_list += f"{bot.display_name}\n"
            active_embed.add_field(
                name=f"Phòng: {voice_channel.mention}",
                value=bot_list,
                inline=False)  # Sử dụng voice_channel.mention để tag tên phòng

    # Tạo embed cho bot chưa được sử dụng
    inactive_embed = discord.Embed(
        title="Bot nhạc còn trống <a:aflash2:1160601026697641984>",
        color=discord.Color.green())
    for bot in inactive_music_bots:
        inactive_embed.add_field(
            name=bot.display_name, value="",
            inline=False)  # Đề cập đến bot chưa được sử dụng

    # Tạo embed cho bot lỗi
    error_embed = discord.Embed(
        title="Bot đang bảo trì <:cmlosed1:1187589874962944092>",
        color=discord.Color.yellow())
    for bot in error_music_bots:
        error_embed.add_field(name=bot.display_name, value="",
                              inline=False)  # Đề cập đến bot lỗi

    # Gửi các embed
    await ctx.send(embed=active_embed)
    await ctx.send(embed=inactive_embed)
    await ctx.send(embed=error_embed)


def parse_time(duration: str) -> int:
    minutes = 0
    match = re.match(r'(\d+)\s*(m|h|d)', duration)
    if match:
        value = int(match.group(1))
        unit = match.group(2)
        if unit == 'm':
            minutes = value
        elif unit == 'h':
            minutes = value * 60
        elif unit == 'd':
            minutes = value * 1440  # 1 ngày có 1440 phút

    return minutes


# Khai báo biến toàn cục để lưu trữ số lần giveaway đã tổ chức

giveaway_count = 0  # Khởi tạo biến giveaway_count


def create_start_embed(ctx, prize: str, duration: str, author: discord.User,
                       num_winners: int) -> discord.Embed:
    global giveaway_count  # Sử dụng biến toàn cục
    giveaway_count += 1  # Tăng giá trị của biến đếm

    # Chuyển múi giờ sang Hà Nội
    hanoi_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
    current_datetime = datetime.now(hanoi_timezone).strftime(
        "%d/%m/%Y %H:%M:%S"
    )  # Lấy ngày và giờ hiện tại và format theo dd/mm/yyyy HH:MM:SS

    title = f"<a:zduoitrailkn:1227211088433512509>__Giveaway Bắt Đầu__<a:zduoiphailkn:1227211085359091742>"
    start_embed = discord.Embed(title=title, color=discord.Color.yellow())

    # Truy cập vào URL của avatar người đăng và sử dụng nó làm thumbnail
    author_avatar_url = author.avatar.url if author.avatar else "https://discord.com/assets/dd4dbc0016779df1378e7812eabaa04d.png"
    start_embed.set_thumbnail(url=author_avatar_url)
    start_embed.set_footer(
        text=f"Mã số {giveaway_count} Giveaways  {(current_datetime)}",
        icon_url=author_avatar_url)
    # Thêm thông tin về giải thưởng, thời gian, số lượng người chiến thắng và ngày giờ hiện tại
    start_embed.description = f"<a:zcuplkn:1201121029863522405>Giải thưởng: {prize}\n<a:zletterlkn:1231863248543027240>Thời gian: {duration}\n<a:zspellbooklkn:1201122043916201994>Số lượng giải: {num_winners}\n <:zMeowlkn:1231863246697398302>Tổ chức bởi <@{author.id}>\n\n _Thả react  🎁  để tham gia_"

    return start_embed


def get_custom_emoji(ctx, emoji_name):
    guild = ctx.guild
    for emoji in guild.emojis:
        if emoji.name == emoji_name:
            return emoji
        return None


def create_end_embed(ctx, prize: str, winners_mentions: str) -> discord.Embed:
    global giveaway_count  # Sử dụng biến toàn cục

    # Chuyển múi giờ sang Hà Nội
    hanoi_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
    current_datetime = datetime.now(hanoi_timezone).strftime(
        "%d/%m/%Y %H:%M:%S"
    )  # Lấy ngày và giờ hiện tại và format theo dd/mm/yyyy HH:MM:SS

    end_embed = discord.Embed(
        title=
        "<a:zduoitrailkn:1227211088433512509>__Giveaway Kết Thúc__ <a:zduoiphailkn:1227211085359091742>",
        color=discord.Color.pink())

    # Thêm icon avatar người đăng trước chữ "Mã số Giveaways"
    author_avatar_url = ctx.author.avatar.url if ctx.author.avatar else "https://discord.com/assets/dd4dbc0016779df1378e7812eabaa04d.png"
    end_embed.set_thumbnail(url=author_avatar_url)
    end_embed.set_footer(
        text=f"Mã số {giveaway_count} giveaways  {(current_datetime)}",
        icon_url=author_avatar_url)

    # Thêm thông tin về giải thưởng và người thắng
    end_embed.description = f"<a:zcuplkn:1201121029863522405>Giải thưởng: {prize}\n<a:zcuplkn:1201121029863522405>Người thắng: {winners_mentions}\n <:zMeowlkn:1231863246697398302>Tổ chức bởi <@{ctx.author.id}>"
    end_embed.set_thumbnail(url=author_avatar_url)
    author_avatar_url = ctx.author.avatar.url if ctx.author.avatar else "https://discord.com/assets/dd4dbc0016779df1378e7812eabaa04d.png"

    return end_embed


async def announce_giveaway_in_voice_channels(ctx, prize, num_winners,
                                              duration):
    guild = ctx.guild
    voice_channels = guild.voice_channels

    for voice_channel in voice_channels:
        # Kiểm tra xem phòng voice chat có thành viên nào không
        if voice_channel.members:
            # Gửi thông báo về giveaway vào phòng voice chat
            await voice_channel.send(
                f"Hi mọi người, mình đang thử tính năng thông báo giveaways nên bot đi rải thông báo các phòng, mọi người thông cảm nha"
            )


@bot.command(name='ga')
async def ga(ctx, duration: str, num_winners: int, *, prize: str):
    global giveaway_running, countdown_task, start_message_id, end_time, winners, channel

    # Kiểm tra xem người gửi lệnh có role yêu cầu không
    required_role_id = 1231827110159716453
    if required_role_id not in [role.id for role in ctx.author.roles]:
        # Tạo embed màu đỏ cho thông báo
        error_embed = discord.Embed(
            description=
            f"Hello <a:zduoitrailkn:1227211088433512509> {ctx.author.mention} <a:zduoiphailkn:1227211085359091742> để tổ chức Giveaway vui lòng liên hệ <@389039417383452692> hoặc <@1080633133248032788> để được hướng dẫn bạn nha",
            color=discord.Color.red())
        # Gửi thông báo trong embed màu đỏ
        await ctx.send(embed=error_embed)
        return

    # Phân tích định dạng thời gian và tính toán số phút tương ứng
    minutes = parse_time(duration)
    if minutes == 0:
        return await ctx.send(
            "Vui lòng sử dụng đúng định dạng giờ m, h, d tương ứng với phút, giờ, ngày"
        )

    # Tính toán thời gian kết thúc của giveaway
    end_time = datetime.utcnow() + timedelta(minutes=minutes)

    # Lấy đối tượng kênh mong muốn
    channel = bot.get_channel(1227235826703007764)  # ID của kênh mong muốn

    # Tạo embed cho thông báo bắt đầu giveaway
    start_embed = create_start_embed(ctx, prize, duration, ctx.author,
                                     num_winners)

    # Gửi thông điệp giveaway đến kênh mong muốn và lấy tin nhắn đã gửi
    start_message = await channel.send(embed=start_embed)
    start_message_id = start_message.id  # Lưu ID của tin nhắn bắt đầu

    # Thêm emoji "🎉" vào tin nhắn đó
    await start_message.add_reaction("🎁")

    # Đợi đến khi thời gian kết thúc
    await asyncio.sleep(minutes * 60)

    try:
        # Lấy tin nhắn giveaway để kiểm tra người tham gia và chọn người chiến thắng
        message = await channel.fetch_message(start_message_id)
        reaction = discord.utils.get(message.reactions, emoji="🎁")

        # Xử lý việc kết thúc Giveaway và gửi embed chỉ vào kênh mong muốn
        await handle_giveaway_end(ctx, reaction, prize, num_winners, channel)

    except discord.errors.NotFound:
        await ctx.send("Tin nhắn bắt đầu giveaway không tồn tại.")


async def handle_giveaway_end(ctx, reaction, prize, num_winners, channel):
    if reaction:
        # Lấy số lượng phản ứng
        reaction_count = reaction.count - 1  # Loại bỏ phản ứng của bot
        if reaction_count < num_winners:
            await ctx.send(
                "Không đủ người tham gia để chọn số lượng người thắng đã chỉ định."
            )
        else:
            # Lặp qua generator để thu thập tất cả các người dùng phản ứng
            eligible_users = []
            async for user in reaction.users():
                if not user.bot:
                    eligible_users.append(user)

            # Chọn ngẫu nhiên số lượng người thắng giải
            winners = random.sample(eligible_users, num_winners)

            if winners:
                winners_mentions = ' '.join(
                    [winner.mention for winner in winners])
                end_embed = create_end_embed(ctx, prize, winners_mentions)
                # Gửi thông điệp kết thúc giveaway đến kênh mong muốn
                await channel.send(embed=end_embed)
            else:
                await ctx.send(":cry: Không có ai tham gia giveaway!\n")
    else:
        await ctx.send(":cry: Không có ai tham gia giveaway!\n")
    # Khai báo biến global để lưu thông tin của giveaway đang chạy


# Khởi tạo biến global
# Khởi tạo biến global
allowed_role_id = 1227235826703007764


@bot.command()
async def start_giveaway(ctx, duration: str, num_winners: int, *, prize: str):
    global giveaway_running, current_giveaway_info

    # Kiểm tra xem người gửi lệnh có role yêu cầu không
    if allowed_role_id not in [role.id for role in ctx.author.roles]:
        await ctx.send("Bạn không có quyền sử dụng lệnh này.")
        return

    # Gửi tin nhắn bắt đầu giveaway
    start_embed = create_start_embed(ctx, prize, duration, ctx.author,
                                     num_winners)
    start_message = await ctx.send(embed=start_embed)

    # Cập nhật thông tin giveaway đang chạy
    current_giveaway_info = {
        'duration': duration,
        'num_winners': num_winners,
        'prize': prize,
        'channel_id': ctx.channel.id,  # Sử dụng ID của kênh nơi lệnh được gửi
        'start_message_id': start_message.id  # Lưu ID của tin nhắn bắt đầu
    }

    # Cập nhật biến giveaway_running
    giveaway_running = True


intents = discord.Intents.default()
intents.messages = True
intents.members = True  # Enable the members intent

confession_channel_id = 1174673765871927346
log_channel_id = 1163074681046315148
reply_log_channel_id = 1240127905984549024


@bot.event
async def on_ready():
    print('Bot is ready')
    global confession_count
    confession_count = load_confession_count()
    print(f'Current confession count: {confession_count}')
INITIAL_CONFESSION_COUNT = 213
confession_threads = {}
confession_count = INITIAL_CONFESSION_COUNT
CONFESSION_COUNT_FILE = 'confession_count.txt'

def save_confession_count(count):
    with open(CONFESSION_COUNT_FILE, 'w') as file:
        file.write(str(count))

def load_confession_count():
    if os.path.exists(CONFESSION_COUNT_FILE):
        with open(CONFESSION_COUNT_FILE, 'r') as file:
            return int(file.read().strip())
    return 171  # Số confession bắt đầu từ 170
confession_channel_ids = [1153156079388205157, 1155081908103954503, 1153156755098968114, 1156927838113513614, 1153155832679235614]
emojis = [
    "<:zlikelkn:1240186553922224188>",
    "<a:zheartlkn:1240186551904895028>",
    "<a:zhahalkn:1240186556845785108>",
    "<a:zthuongthuonglkn:1240186558750134315>",
    "<a:sadlkn:1240186545953046559>",
    "<:zdislikelkn:1240186548981600336>"
]

async def add_reactions_with_retry(message, emojis, max_retries=5):
    for emoji in emojis:
        for attempt in range(max_retries):
            try:
                await message.add_reaction(emoji)
                await asyncio.sleep(1)  # Thêm thời gian chờ giữa các yêu cầu để tránh rate limit
                break  # Thoát khỏi vòng lặp nếu thành công
            except discord.errors.HTTPException as e:
                if e.status == 429:
                    retry_after = e.retry_after if hasattr(e, 'retry_after') else 2 ** attempt
                    await asyncio.sleep(retry_after)
                else:
                    print(f"Failed to add reaction: {emoji}. Error: {e}")
                    break

@bot.command(name='cfan')
async def cfan_command(ctx, *, confession_text):
    global confession_count
    confession_count += 1
    save_confession_count(confession_count)

    confession_channel = bot.get_channel(confession_channel_id)
    log_channel = bot.get_channel(log_channel_id)

    if confession_channel and log_channel:
        confession_color = random.randint(0, 0xFFFFFF)  # Tạo màu ngẫu nhiên
        confession_embed = discord.Embed(
            title=f" <a:zspellbooklkn:1201122043916201994> Chuyện của làng, lá thư số `#{confession_count}` <a:zletterlkn:1231863248543027240>",
            description="\u200B" + confession_text,
            color=confession_color
        )

        # Thêm thông tin "Được gửi bởi 1 lữ khách ven đường" vào footer của Embed
        confession_embed.set_footer(text="💖Gửi bởi lữ khách ven đường🍀 discord.gg/langkhongngu")

        # Gửi confess embed vào kênh confess
        confess_message = await confession_channel.send(embed=confession_embed)

        # Tạo chủ đề mới trong kênh confess
        topic = f"rep confess tại đây #{confession_count}"
        new_thread = await confess_message.create_thread(name=topic, auto_archive_duration=1440)

        # Xóa tin nhắn confess
        try:
            await ctx.message.delete()
        except discord.errors.NotFound:
            print("Tin nhắn không tồn tại hoặc đã bị xóa, không thể xóa tin nhắn này.")

        # Thả emoji vào tin nhắn confession
        await add_reactions_with_retry(confess_message, emojis)

        # Ghi lại ID của confession và thread trong log channel
        log_message = f"[Confession #{confession_count}] từ {ctx.author.name} ({ctx.author.id}) đã gửi: {confession_text} (Message ID: {confess_message.id}, Thread ID: {new_thread.id})"
        await log_channel.send(log_message)

    else:
        await ctx.send("Không tìm thấy kênh confession hoặc kênh log, vui lòng cài đặt lại đúng cách.")

@bot.command(name='cfs')
async def cfs_command(ctx, *, confession_text):
    global confession_count
    confession_count += 1

    save_confession_count(confession_count)  # Lưu số confession hiện tại vào tệp

    confession_channel = bot.get_channel(confession_channel_id)
    log_channel = bot.get_channel(log_channel_id)

    if confession_channel and log_channel:
        confession_color = random.randint(0, 0xFFFFFF)  # Tạo màu ngẫu nhiên

        # Tạo thông điệp confession với xuống dòng
        confession_message = f"Được gửi bởi: {ctx.author.mention}\n*{confession_text}*"

        # Tạo Embed confession với title giữ nguyên
        confession_embed = discord.Embed(
            title=f"<a:zspellbooklkn:1201122043916201994> Chuyện của làng, lá thư số `#{confession_count}` <a:zletterlkn:1231863248543027240>",
            description=confession_message,
            color=confession_color
        )

        # Thêm thông tin "được gửi bởi" vào footer của embed và icon tròn avatar
        author_avatar_url = ctx.author.avatar.url if ctx.author.avatar else "https://discord.com/assets/dd4dbc0016779df1378e7812eabaa04d.png"
        confession_embed.set_footer(text=f"discord.gg/langkhongngu ", icon_url=author_avatar_url)

        if ctx.author.avatar:
            confession_embed.set_thumbnail(url=ctx.author.avatar.url)

        # Gửi confession embed vào kênh confess
        confess_message = await confession_channel.send(embed=confession_embed)

        # Tạo chủ đề mới trong kênh confess
        topic = f"Rep confess #{confession_count} tại đây "
        new_thread = await confess_message.create_thread(name=topic, auto_archive_duration=1440)
        guide_embed = discord.Embed(
            description="Để rep ẩn danh vui lòng sử dụng lệnh _rcfs [ mã số ] [ nội dung ]",
            color=0xFF0000  # Màu đỏ
        )
        await new_thread.send(embed=guide_embed)
        # Xóa tin nhắn confess
        try:
            await ctx.message.delete()
        except discord.errors.NotFound:
            print("Tin nhắn không tồn tại hoặc đã bị xóa, không thể xóa tin nhắn này.")

        # Thả emoji vào tin nhắn confession
        await add_reactions_with_retry(confess_message, emojis)

        # Ghi lại ID của confession và thread trong log channel
        log_message = f"[Confession #{confession_count}] từ {ctx.author.name} ({ctx.author.id}) đã gửi: {confession_text} (Message ID: {confess_message.id}, Thread ID: {new_thread.id})"
        await log_channel.send(log_message)

    else:
        await ctx.send("Không tìm thấy kênh confession hoặc kênh log, vui lòng cài đặt lại đúng cách.")



@bot.command()
async def rcfs(ctx, confession_number: int, *, reply_text):
    confession_channel = bot.get_channel(confession_channel_id)
    log_channel = bot.get_channel(log_channel_id)
    reply_log_channel = bot.get_channel(reply_log_channel_id)

    if confession_channel and log_channel and reply_log_channel:
        # Tìm tin nhắn log chứa confession_number
        async for log_message in log_channel.history(limit=200):
            if f"[Confession #{confession_number}]" in log_message.content:
                # Lấy message ID và thread ID từ log message
                try:
                    parts = log_message.content.split('(Message ID: ')[1].split(', Thread ID: ')
                    message_id = int(parts[0])
                    thread_id = int(parts[1].split(')')[0])
                except (IndexError, ValueError):
                    await ctx.send(f"Không thể tìm thấy thông tin Message ID và Thread ID trong log cho confession #{confession_number}")
                    return

                thread = bot.get_channel(thread_id)
                if thread:
                    reply_embed = discord.Embed(
                        description=f"> <a:Zdomdomlkn:1235512517359308840> {reply_text}")

                    # Lấy thông tin người đăng bài từ tin nhắn log
                    try:
                        original_author_id = int(log_message.content.split(')')[0].split('(')[1])
                        original_author = await bot.fetch_user(original_author_id)
                    except (IndexError, ValueError):
                        await ctx.send(f"Không thể tìm thấy thông tin người đăng bài trong log cho confession #{confession_number}")
                        return

                    # Kiểm tra xem người dùng là người đăng bài gốc hay không
                    if ctx.author.id == original_author.id:
                        reply_embed.set_footer(text="Phản hồi bởi người đăng bài")
                    else:
                        reply_embed.set_footer(text="Phản hồi bởi người dân trong làng")

                    await thread.send(embed=reply_embed)

                    # Gửi phản hồi vào kênh reply_log_channel
                    await reply_log_channel.send(
                        f"{ctx.author.mention} vừa phản hồi confession #{confession_number} với nội dung: {reply_text}"
                    )

                    # Xóa tin nhắn rcfs của người dùng
                    try:
                        await ctx.message.delete()
                    except discord.errors.NotFound:
                        print("Tin nhắn không tồn tại hoặc đã bị xóa, không thể xóa tin nhắn này.")
                    return

        await ctx.send(f"Không tìm thấy confession #{confession_number} trong dữ liệu")
    else:
        await ctx.send("Không tìm thấy kênh confession, log hoặc kênh phản hồi, vui lòng cài đặt lại đúng cách.")


confession_channel_ids = [1153156079388205157, 1155081908103954503, 1153156755098968114, 1156927838113513614, 1153155832679235614]
@bot.event
async def on_message(message):
    if message.channel.id in confession_channel_ids:
        topic = f"Bình luận tại đây"
        new_thread = await message.create_thread(name=topic, auto_archive_duration=None)

    await bot.process_commands(message)



@bot.command(name='help')
async def help_command(ctx):
    # Tạo một embed Discord
    embed = discord.Embed(title="Bảng lệnh hướng dẫn sử dụng bot",
                          description="Dưới đây là danh sách các lệnh bot:",
                          color=0x00ff00)

    # Thêm các trường vào embed để hiển thị các lệnh và mô tả của chúng
    embed.add_field(name="<:pinkdotlkn:1196832522319962193> _s [nội dung]",
                    value="Chuyển văn bản thành giọng nói",
                    inline=False)
    embed.add_field(name="<:pinkdotlkn:1196832522319962193> _cfs [nội dung]",
                    value="Đăng câu chuyện công khai",
                    inline=False)
    embed.add_field(name="<:pinkdotlkn:1196832522319962193> _cfan [nội dung]",
                    value="Đăng câu chuyện ẩn danh",
                    inline=False)
    embed.add_field(name="<:pinkdotlkn:1196832522319962193> _rcfs [mã số] [nội dung]",
    value="Phản hồi ẩn danh",
    inline=False)
    embed.add_field(name="<:pinkdotlkn:1196832522319962193> _join",
                    value="Tham gia vào phòng thoại mà bạn đang ở",
                    inline=False)
    embed.add_field(name="<:pinkdotlkn:1196832522319962193> _leave",
                    value="Rời khỏi phòng thoại hiện tại.",
                    inline=False)
    embed.add_field(name="<:pinkdotlkn:1196832522319962193> _musicbot",
                    value="Kiểm tra tình trạng bot nhạc",
                    inline=False)

    # Gửi embed vào kênh của người gửi lệnh
    await ctx.send(embed=embed)


CHUI_FILE_PATH = 'cauchui.txt'
ALLOWED_ROLE_ID = 1241318523872219186

@bot.command()
async def chui(ctx, member: discord.Member):
    # Kiểm tra xem người gửi có role được phép không
    allowed_role = discord.utils.get(ctx.guild.roles, id=ALLOWED_ROLE_ID)
    if allowed_role not in ctx.author.roles:
        await ctx.send("Muốn chửi thuê á? Liên hệ admin đê.")
        return

    # Xóa tin nhắn chứa lệnh _chui
    await ctx.message.delete()

    # Đọc nội dung từ file chứa các câu chửi
    with open(CHUI_FILE_PATH, 'r', encoding='utf-8') as f:
        chui_lines = f.readlines()

    # Chọn ngẫu nhiên 10 câu chửi
    selected_chui = random.sample(chui_lines, min(len(chui_lines), 10))

    # Phản hồi với các câu chửi và @ người được tag
    for chui_msg in selected_chui:
        await ctx.send(f'{member.mention} {chui_msg.strip()}')
        await asyncio.sleep(2)  # Chờ 2 giây trước khi gửi câu chửi tiếp theo
@bot.command()
async def addchui(ctx, *, new_chui: str):
    # Kiểm tra xem người gửi có role được phép không
    allowed_role = discord.utils.get(ctx.guild.roles, id=ALLOWED_ROLE_ID)
    if allowed_role not in ctx.author.roles:
        await ctx.send("Bạn không có quyền thêm câu chửi.")
        return

    # Thêm câu chửi mới vào tệp cauchui.txt
    with open(CHUI_FILE_PATH, 'a', encoding='utf-8') as f:
        f.write(f'{new_chui}\n')

    await ctx.send("Câu chửi mới đã được thêm.")

@bot.command()
async def delchui(ctx, *, chui_to_remove: str):
    # Kiểm tra xem người gửi có role được phép không
    allowed_role = discord.utils.get(ctx.guild.roles, id=ALLOWED_ROLE_ID)
    if allowed_role not in ctx.author.roles:
        await ctx.send("Bạn không có quyền xóa câu chửi.")
        return

    # Đọc nội dung từ tệp cauchui.txt
    with open(CHUI_FILE_PATH, 'r', encoding='utf-8') as f:
        chui_lines = f.readlines()

    # Xóa câu chửi nếu tìm thấy
    new_chui_lines = [line for line in chui_lines if line.strip() != chui_to_remove]

    # Ghi lại nội dung mới vào tệp
    with open(CHUI_FILE_PATH, 'w', encoding='utf-8') as f:
        f.writelines(new_chui_lines)

    if len(new_chui_lines) == len(chui_lines):
        await ctx.send("Không tìm thấy câu chửi cần xóa.")
    else:
        await ctx.send("Câu chửi đã được xóa.")


bot.run(os.environ.get('TOKEN'))
