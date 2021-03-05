from keep_alive import keep_alive
import os
import discord
import asyncio
from discord.ext import commands
from random import randint, choice
from datetime import datetime

# test update - ok!

names_reference = [
    '<:nohy:813552436312277042>', '<:mimitom:813490044018229268>',
    '<:jeee:813493670173999193>'
]

all_commands = {
    "-hi": "A greeting message",
    "-hello": "A greeting message",
    "-hey": "A greeting message",
    "-info": "Displays info about Iris",
    "-undress": " Plays the game Flaška",
    "-help":
    "`-help` - Shows all commands\n`-help <str>` - Shows a specified command",
    "-tictactoe":
    "`-tictactoe <@Member>` - Challenges a member to a game of tic-tac-toe!",
    "-place": "`-place <int>` - Places your mark on the specified position",
    "-clear":
    "`-clear` - Deletes the last message in chat\n`-clear <message ID>` - Deletes a message by it\'s ID'",
    "-purge": "`-purge <int> - Deletes a number of messages",
    "-time": "Tells the time",
    "-alarm":
    "`-alarm <HH:MM>` - Sets an alarm for a specified time\n`-alarm <HH:MM> <str>` - Sets a named alarm for a specified time",
    "-shutdown": "Shutdowns Iris (admin)",
    "-hangman": "Starts a game of hangman.",
    "-ltr": "`-ltr <char>` - Guess a letter in the game of hangman."
}

sorted_commands = list(map(list, all_commands.items()))
sorted_commands = sorted(sorted_commands, key=lambda x: x[0])

# Tic-Tac-Toe
winning_conditions = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7],
                      [2, 5, 8], [0, 4, 8], [2, 4, 6]]
player1 = ''
player2 = ''
turn = ''
gameOver = True
board = []
count: int

# Flaška
last = randint(0, 2)

client = commands.Bot(command_prefix='-', case_insensitive=True)
client.remove_command("help")


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name='-help'))
    print('\nI\'m in! {0}'.format(
        datetime.now().strftime('%H:%M:%S - %d/%m/%Y')))
    print(client.user)
    print()

    report = False
    if report:
        task = asyncio.create_task(update_version())
        await task

    # read saved alarms
    saved_alarms = read_file('mem_txt_files/alarms.txt').split('\n')
    if saved_alarms[0] == '': saved_alarms.pop()
    print('saved alarms: {}'.format(saved_alarms))

    alarm_tasks = []
    for alarm in saved_alarms:
        alarm_tasks.append(asyncio.create_task(set_alarm(*alarm.split('|'))))

    for task in alarm_tasks:
        await task


async def update_version():
    #update message, version...
    update_channels = [813182703981166632, 814069218957459456]

    v_number, v_counter, v_name = read_file('mem_txt_files/version.txt').split(
        ', ')
    v_number = int(v_number)
    v_counter = int(v_counter)
    while True:
        new_version = str(input('Is this a new version of Iris?: ')).lower()
        if new_version in ['1', 'y', 'yes', 'positive', 'ok']:
            v_counter = 0
            v_number += 1
            v_name = input('Enter version name: ')
            note = input('Name new features: ')
            note = 'It adds: ' + note
            break
        elif new_version in ['0', 'n', 'no', 'negative']:
            v_counter += 1
            note = str(input('Describe changes: '))
            note = 'Fixes, changes, etc.:  ' + note if note != '' else ''
            break
        else:
            break

    write_file('mem_txt_files/version.txt', ', '.join(
        (str(v_number), str(v_counter), str(v_name))))
    output = 'v{0}.{1} {2}'.format(str(v_number), str(v_counter), str(v_name))

    for channel in update_channels:
        channel = client.get_channel(channel)
        if new_version in ['1', 'y', 'yes', 'positive', 'ok']:
            await channel.send(embed=new_embed(
                title='Release News :newspaper:',
                description=
                '**{0}** has been finished and is now online.\n{1}\nType -help for more info!'
                .format(output, note)))
            await channel.send(embed=new_embed(
                title=
                ':sparkles: Oh, look at me, how shiny! :face_with_hand_over_mouth: :sparkles:\n',
                author=True,
                footer=False,
                timestamp=False))
        elif new_version in ['0', 'n', 'no', 'negative']:
            await channel.send(embed=new_embed(
                title=
                ':screwdriver:  Once again, Iris is back on-line! {} :tools:'.
                format(output),
                description=note))
    print(f'Version setting finished, {output}\n')


# NOTES functions
@client.command()
async def note(ctx, *new_note):
    new_note = ' '.join([note for note in new_note])
    print('new note: {}'.format(new_note))
    stored_notes = []

    try:
        stored_notes = read_file('mem_txt_files/notes.txt').split('\n')
        if stored_notes[0] == '': stored_notes.pop()
        print('stored notes: {}'.format(stored_notes))

    except FileNotFoundError:
        print('error - no such file')

    stored_notes.append(new_note)
    print('updated notes: {}'.format(stored_notes))

    i = 0
    output = ''
    save = ''
    for note in stored_notes:
        i += 1
        if i != len(stored_notes):
            save = save + note + '\n'
        else:
            save = save + note

        output = output + str(i) + ' - ' + note + '\n'

    write_file('mem_txt_files/notes.txt', save)

    await ctx.send('your notes:\n{}'.format(output))


@client.command()
async def notes(ctx):
    stored_notes = read_file('mem_txt_files/notes.txt').split('\n')

    output = ''
    i = 0
    for note in stored_notes:
        i += 1
        output = output + str(i) + ' - ' + note + '\n'

    await ctx.send('your notes:\n{}'.format(output))


@client.command()
async def delnote(ctx, *n_del_nums):
    f = open("mem_txt_files/notes.txt", "r")
    lines = [line.replace('\n', '') for line in f.readlines()]
    f.close()

    if len(n_del_nums) == 0:
        await ctx.send('Be sure to enter note indexes')
        return

    if len(lines) == 0:
        await ctx.send(
            'There are no notes - everything has already been deleted')
        return

    n_del_nums = list(n_del_nums)
    try:
        n_del_nums = [int(note_num.rstrip(',')) - 1 for note_num in n_del_nums]
    except ValueError:
        await ctx.send('Be sure to enter valid note indexes')
        return

    # delete line by index
    error_output = []
    for n_del_num in n_del_nums:
        if len(lines) - 1 < n_del_num or n_del_num < 0:
            print('invalid index found')
            error_output.append(n_del_num)

    for num in error_output:
        n_del_nums.remove(num)

    error_output = [str(num + 1) for num in error_output]

    if len(error_output) > 0:
        await ctx.send('No notes with indexes: {}'.format(
            ', '.join(error_output)))
        if len(n_del_nums) == 0:
            await ctx.send('Be sure to enter valid note indexes')
            return

    deleted_notes = []
    for num in sorted(n_del_nums, reverse=True):
        deleted_notes.append(lines[num])
        lines.pop(num)

    f = open("mem_txt_files/notes.txt", "w")
    for line in lines:
        if lines.index(line) != 0:
            f.write('\n' + line)
        else:
            f.write(line)
    f.close()

    await ctx.send('The following notes have been deleted: {}'.format(
        ', '.join(deleted_notes)))


# CHAT MANAGEMENT functions
@client.command()
async def clear(ctx, message_id=None):
    if message_id is None:
        await ctx.channel.purge(limit=2)
    else:
        msg = await ctx.channel.fetch_message(message_id)
        await msg.delete()
        await ctx.channel.purge(limit=1)


@client.command()
async def purge(ctx, amount: int = 10):
    if ctx.message.guild.id != 812837958226804737:
        await ctx.channel.purge(limit=amount + 1)
    else:
        await ctx.send(embed=new_embed(title='Your server does not support this function.'))
        await ctx.message.delete()


@client.command()
async def history(ctx, amount: int = 10):
    output = ''
    async for msg in ctx.channel.history(limit=amount):
        output += msg.content + '\n'
    await ctx.send(output)
    await ctx.message.delete()


# TIME functions
@client.command()
async def time(ctx):
    now = datetime.now()
    m_s = now.strftime("%M:%S")
    h = int(now.strftime("%H")) + 1
    h = h % 24
    now = str(h) + ":" + m_s
    await ctx.send(embed=new_embed(title="It is " + now +
                                   " - Get up and do something!"))
    await ctx.message.delete()


@client.command()
async def alarm(ctx, ring_time, *event_name):
    event = ' - ' + ' '.join([word for word in event_name
                              ]) if event_name != () else ''
    try:
        set_h, set_m = ring_time.split(':')
        if not 0 <= int(set_h) <= 23 or not 0 <= int(set_m) <= 59:
            raise ValueError
    except ValueError:
        await ctx.send('Be sure to enter a valid time <HH:MM>')
        await ctx.message.delete()
        return
    set_h = '0' + set_h if len(set_h) == 1 else set_h
    set_m = '0' + set_m if len(set_m) == 1 else set_m

    now = datetime.now()
    now_m = int(now.strftime("%M"))
    now_h = int(now.strftime("%H")) + 1
    now_h %= 24

    if int(set_h) * 60 + int(set_m) < now_h * 60 + now_m:
        delta_t = 24 * 60 - (now_h * 60 + now_m) + int(set_h) * 60 + int(set_m)
    else:
        delta_t = int(set_h) * 60 + int(set_m) - (now_h * 60 + now_m)

    save_alarm(set_h, set_m, event, ctx.channel.id, ctx.message.author.mention)
    alarm_task = asyncio.create_task(
        set_alarm(set_h, set_m, event, ctx.channel.id,
                  ctx.message.author.mention))

    await ctx.send(embed=new_embed(
        title='Alarm set to {0}:{1} {2}'.format(set_h, set_m, event),
        description='Remaining time: {0} hour(s) {1} minute(s)'.format(
            delta_t // 60, delta_t % 60),
        color=0x00ff11))
    await ctx.message.delete()

    await alarm_task


def save_alarm(set_h, set_m, event, channel_id, author_mention):
    new_alarm = '|'.join((str(set_h), str(set_m), str(event), str(channel_id),
                          str(author_mention)))

    saved_alarms = read_file('mem_txt_files/alarms.txt').split('\n')

    if saved_alarms[0] == '': saved_alarms.pop()
    print('saved alarms: {}'.format(saved_alarms))

    saved_alarms.append(new_alarm)
    print('alarm to be saved: {}'.format(new_alarm))

    save = ''
    i = 0
    for alarm in saved_alarms:
        i += 1
        if i != len(saved_alarms):
            save = save + alarm + '\n'
        else:
            save = save + alarm

    write_file('mem_txt_files/alarms.txt', save)


async def set_alarm(set_h, set_m, event, channel_id, author_mention):

    now = datetime.now()
    now_m = int(now.strftime("%M"))
    now_h = int(now.strftime("%H")) + 1
    now_h %= 24

    if int(set_h) * 60 + int(set_m) < (now_h * 60 + now_m):
        delta_t = 24 * 60 - (now_h * 60 + now_m) + int(set_h) * 60 + int(set_m)
    else:
        delta_t = int(set_h) * 60 + int(set_m) - (now_h * 60 + now_m)

    channel = client.get_channel(int(channel_id))
    print(
        'Alarm set to {0}:{1} {2}. Remaining time: {3} hour(s) {4} minute(s)'.
        format(set_h, set_m, event, delta_t // 60, delta_t % 60))
    await asyncio.sleep(int(delta_t * 60))
    print('done', channel)
    await channel.send(embed=new_embed(title='Alarm' + event,
                                       description='{0}:{1} - {2}'.format(
                                           set_h, set_m, author_mention),
                                       color=0xff0000))

    del_alarm = '|'.join((str(set_h), str(set_m), str(event), str(channel_id),
                          str(author_mention)))

    f = open("mem_txt_files/alarms.txt", "r")
    lines = [line.replace('\n', '') for line in f.readlines()]
    f.close()

    lines.remove(del_alarm)

    f = open("mem_txt_files/alarms.txt", "w")
    for line in lines:
        if lines.index(line) != 0:
            f.write('\n' + line)
        else:
            f.write(line)
    f.close()


@alarm.error
async def alarm_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send('Be sure to enter a time <HH:MM>')
        await ctx.message.delete()


# GAMES functions

# load words to choose from
with open('mem_txt_files/words.txt', 'r') as file:
    dictionary = [word.rstrip('\n') for word in file.readlines()]

drawings = [
    '', '''





=========''', '''
                |
                |
                |
                |
                |
=========''', '''
      +----+
       |        |
                |
                |
                |
                |
=========''', '''
      +----+
       |        |
      O       |
                |
                |
                |
=========''', '''
      +----+
       |        |
      O       |
       |        |
                |
                |
=========''', '''
      +----+
       |        |
      O       |
     /|        |
                |
                |
=========''', '''
      +----+
       |        |
      O       |
     /|\      |
                 |
                 |
=========''', '''
      +----+
       |        |
      O       |
     /|\      |
     /          |
                 |
=========''', '''
      +----+
       |        |
      O       |
     /|\      |
     / \      |
                 |
========='''
]

word = ''
game_state = 0
gameOver1 = True
guessed_letters = []


@client.command()
async def hangman(ctx):
    global word
    global game_state
    global guessed_letters
    global gameOver1

    if gameOver1:
        await ctx.send(f'Welcome to Hangman!\n{drawings[0]}')
        word = choice(dictionary)
        print(word)
        game_state = 0
        guessed_letters = []
        gameOver1 = False
    else:
        await ctx.send('Game in progress')

    await ctx.message.delete()


@client.command()
async def ltr(ctx, ltr):
    global word
    global game_state
    global guessed_letters
    global gameOver1

    if not gameOver1:
        if ltr.isalpha() and len(ltr) == 1:
            if ltr in guessed_letters:
                await ctx.send('Already used!')
            else:
                guessed_letters.append(ltr)

                display = word
                for char in display:
                    if char not in guessed_letters:
                        display = display.replace(char, '-')

                if ltr not in word:
                    game_state += 1
                    await ctx.send(f'Nope!{drawings[game_state]}')
                else:
                    await ctx.send('Yay!')
                await ctx.send('Word: ' + display + '\nUsed letters: ' + str(', '.joint(guessed_letters)))

                if '-' not in display or game_state == len(drawings) - 1:
                    if game_state == len(drawings) - 1:  # lost
                        await ctx.send(
                            f'Oh no, he\'s dead!\nThe word was: {word}')
                    else:
                        await ctx.send('Congratulations, you won!')
                    word = ''
                    game_state = 0
                    gameOver1 = True
                    guessed_letters = []
        else:
            await ctx.send('Please enter a single letter.')
    else:
        await ctx.send('No game in progress')

    await ctx.message.delete()


@ltr.error
async def ltr_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send('Please specify a letter.')
        await ctx.message.delete()


@client.command()
async def undress(ctx):
    names = kdo_koho()
    embed = new_embed(title='Flaška',
                      description='{0} is asking {1}'.format(
                          names[0], names[1]),
                      color=0x940096)
    embed.set_author(
        name='Iris\'s Games Repository',
        url=
        'https://discord.com/api/oauth2/authorize?client_id=813482693396398113&permissions=519232&scope=bot',
        icon_url='https://i.imgur.com/sDOZ6KF.jpg')
    embed.set_thumbnail(
        url=
        'https://media.istockphoto.com/photos/empty-bottle-from-transparent-glass-with-reflection-isolated-on-a-picture-id1033890540?s=612x612'
    )
    embed.set_footer(text='Choose your question carefully')
    await ctx.send(embed=embed)
    await ctx.message.delete()


@client.command()
async def tictactoe(ctx, pl2: discord.Member):
    global player1
    global player2
    global turn
    global gameOver
    global count

    if gameOver:
        global board
        board = [
            ':white_large_square:', ':white_large_square:',
            ':white_large_square:', ':white_large_square:',
            ':white_large_square:', ':white_large_square:',
            ':white_large_square:', ':white_large_square:',
            ':white_large_square:'
        ]
        turn = ''
        gameOver = False
        count = 0

        player1 = ctx.message.author
        player2 = pl2

        # print board
        line = ''
        for x in range(len(board)):
            if x == 2 or x == 5 or x == 8:
                line += ' ' + board[x]
                await ctx.send(line)
                line = ''
            else:
                line += ' ' + board[x]

        # who plays first
        if randint(1, 2) == 1:
            turn = player1
            await ctx.send('It\'s <@{0}>\'s turn.'.format(player1.id))
        else:
            turn = player2
            await ctx.send('It\'s <@{0}>\'s turn.'.format(player2.id))
    else:
        ctx.send('Game already in progress')


@tictactoe.error
async def tictactoe_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send('Please mention an opponent.')
    elif isinstance(error, discord.ext.commands.errors.BadArgument):
        await ctx.send(
            'Please make sure to mention players properly (ie. <@813482693396398113>)'
        )


@client.command()
async def place(ctx, pos: int):
    global turn
    global player1
    global player2
    global board
    global count
    global gameOver

    if not gameOver:
        mark = ''
        if turn == ctx.author or ctx.author == 'Kazouss#2819':
            if turn == player1 and count % 2 == 0:
                mark = ':regional_indicator_x:'
            elif turn == player2:
                mark = ':o2:'
            if 0 < pos < 10 and board[pos - 1] == ':white_large_square:':
                board[pos - 1] = mark
                count += 1

                # print board
                line = ''
                for x in range(len(board)):
                    if x == 2 or x == 5 or x == 8:
                        line += ' ' + board[x]
                        await ctx.send(line)
                        line = ''
                    else:
                        line += ' ' + board[x]

                check_winner(mark)
                if gameOver:
                    await ctx.send('{} wins!'.format(mark))
                elif count >= 9:
                    await ctx.send('It\'s a tie!')
                    gameOver = True
                else:
                    # switch turns
                    if turn == player1:
                        turn = player2
                        await ctx.send('It\'s <@{0}>\'s turn.'.format(
                            player2.id))
                    elif turn == player2:
                        turn = player1
                        await ctx.send('It\'s <@{0}>\'s turn.'.format(
                            player1.id))

            else:
                await ctx.send('Use a valid position')
        else:
            await ctx.send('Not your turn.')
    else:
        await ctx.send('Game is not active')
    await ctx.message.delete()


@place.error
async def place_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send('Please select a position you would like to mark.')
    elif isinstance(error, discord.ext.commands.errors.BadArgument):
        await ctx.send('Please make sure to enter an integer')


def check_winner(mark):
    global gameOver
    for condition in winning_conditions:
        if board[condition[0]] == mark and board[
                condition[1]] == mark and board[condition[2]] == mark:
            gameOver = True


# TEST functions
@client.command()
async def test(ctx, *seconds):
    print(ctx.message.author.mention)
    tasks = []
    for second in seconds:
        task = asyncio.create_task(sleep_parallel(ctx, second))
        tasks.append(task)

    for task in tasks:
        await task


async def sleep_parallel(ctx, seconds):
    print('sleeping at {}'.format(datetime.now().strftime('%S')))
    await ctx.send('sleeping at {}'.format(datetime.now().strftime('%H:%M:%S'))
                   )
    await asyncio.sleep(int(seconds))
    print('waking up at {}'.format(datetime.now().strftime('%S')))
    await ctx.send('waking up at {}'.format(
        datetime.now().strftime('%H:%M:%S')))


# IRIS CONVERSATION functions
# GREETING MESSAGES functions
@client.command()
async def hi(ctx):
    await ctx.send(embed=new_embed(title="Hi!"))


@client.command()
async def hey(ctx):
    await ctx.send(embed=new_embed(title="Hey!"))


@client.command()
async def hello(ctx):
    await ctx.send(embed=new_embed(title="Hello!"))


# IRIS HUMAN-LIKE SPEECH function
def is_me():
    def predicate(ctx):
        return ctx.bot.is_owner(ctx.author)
    return commands.check(predicate)


@client.command()
@is_me()
async def iris(ctx, *args):
    output = ''
    if args != ():
        for word in args:
            output += word + ' '
        await ctx.send(embed=new_embed(title=output, author=True, footer=False, timestamp=False))
    await ctx.message.delete()


# HELP & INFO
@client.command()
async def help(ctx, cmnd=None):
    if cmnd is not None and cmnd in all_commands:
        await ctx.send(embed=new_embed(
            title=cmnd, description=all_commands[cmnd], color=0xff9d00))
    else:
        await ctx.send(embed=new_embed(
            title='Available Commands',
            description='Here are all the commands you can use.',
            color=0xf1a82d,
            fields=sorted_commands))
    await ctx.message.delete()


@client.command()
async def info(ctx):
    file = open('mem_txt_files/information.txt', 'r')
    f_content = file.read()
    file.close()
    await ctx.send(f_content)
    await ctx.message.delete()


# TECHNICAL
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(embed=new_embed(title='{} is not a valid command. Better luck next time!'.format(ctx.message.content)))
        await ctx.message.delete()
        return
    if isinstance(error, commands.CheckFailure):
        await ctx.send(embed=new_embed(title='Don\'t mess with me'))
        await ctx.message.delete()
    raise error


@client.command()
async def shutdown(ctx):
    if await ctx.bot.is_owner(ctx.author):
        await ctx.send(embed=new_embed(title='Iris has been shut down'))
        await ctx.message.delete()
        await ctx.bot.logout()


def kdo_koho():
    global last
    names = names_reference.copy()

    names.pop(last)
    names.pop(randint(0, 1))

    return_list = names_reference[last], names[0]
    last = names_reference.index(names[0])
    return return_list


def new_embed(title,
              description=None,
              color=None,
              timestamp=True,
              footer=True,
              author=False,
              fields=None,
              fields_inline=False,
              thumbnail=False):
    embed = discord.Embed()
    embed.title = title
    if author:
        embed.set_author(name='Iris', url='https://discord.com/api/oauth2/authorize?client_id=813482693396398113&permissions=519232&scope=bot', icon_url='https://i.imgur.com/sDOZ6KF.jpg')
    embed.description = description if description is not None else None
    embed.color = color if color is not None else 0x004499
    if thumbnail is not False:
        embed.set_thumbnail(url=thumbnail)
    if type(footer) == str:
        embed.set_footer(text=footer)
    elif footer == True:
        embed.set_footer(text='Made by Iris\'s Kingdom')
    if timestamp:
        embed.timestamp = datetime.now()

    if type(fields) == dict:
        for field in fields:
            embed.add_field(name=field,
                            value=fields[field],
                            inline=fields_inline)
    elif type(fields) == list:
        for field in fields:
            embed.add_field(name=field[0],
                            value=field[1],
                            inline=fields_inline)

    return embed


def read_file(file_name):
    f = open(file_name, 'r')
    output = f.read()
    f.close()
    return output


def write_file(file_name, text):
    f = open(file_name, 'w')
    f.write(text)
    f.close()


keep_alive()
client.run(os.getenv('IRIS'))
