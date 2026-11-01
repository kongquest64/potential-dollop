"""Script + visual plan for:
"Why Hasn't Nintendo Died? Here's What Actually Keeps It Alive"

Structure mirrors the reference essay format: a historical cold open, a
provocative thesis question, a framework of the few factors that decide the
outcome, evidence for each, a synthesis, an honest look at weaknesses, and a
conclusion that answers the opening question.

Each scene: narration text + a visual spec. Visual items carry `s`, the index
of the narration sentence at which they appear on screen.
"""

SCENES = [
    # ---------------------------------------------------------------- COLD OPEN
    dict(
        id="open_crash",
        text=(
            "In 1983, the American video game industry collapsed. "
            "In just two years, home video game revenue fell by roughly ninety-seven percent. "
            "Retailers swore off games entirely. "
            "Atari, the company that had defined the medium, hauled truckloads of unsold cartridges "
            "to a landfill in the New Mexico desert and buried them."
        ),
        visual=dict(
            type="hero",
            kicker="U.S. HOME VIDEO GAME REVENUE · 1983 → 1985",
            big="−97%",
            sub="The crash that nearly ended the medium",
            s_big=1,
        ),
    ),
    dict(
        id="open_graveyard",
        text=(
            "Into that wreckage walked a century-old Japanese playing card company. "
            "Four decades later, look at who else was making game hardware back then. "
            "Atari. Coleco. Mattel. Magnavox. NEC. SNK. Panasonic. Sega. "
            "Every one of them is out of the console business. "
            "Nintendo is still here. "
            "And it isn't just surviving. "
            "Its last console sold more than a hundred and fifty million units, "
            "and its new one is the fastest-selling machine it has ever made."
        ),
        visual=dict(
            type="graveyard",
            names=["ATARI", "COLECO", "MATTEL", "MAGNAVOX", "NEC", "SNK", "PANASONIC", "SEGA"],
            s_names=2,
            s_strike=10,
            survivor="NINTENDO",
            s_survivor=11,
        ),
    ),
    dict(
        id="title",
        text=(
            "So here's a question that sounds strange, given all that success. "
            "Why hasn't Nintendo died? "
            "Because it really should have. Several times."
        ),
        visual=dict(
            type="title",
            title="Why Hasn't Nintendo Died?",
            sub="Here's what actually keeps it alive",
            s_sub=1,
        ),
    ),
    dict(
        id="near_deaths",
        text=(
            "The Virtual Boy, a red-and-black headache machine that sold well under a million units. "
            "The Nintendo 64, which bet on cartridges and lost Final Fantasy to Sony. "
            "The GameCube, which finished a distant third. "
            "The 3DS, whose launch went so badly its price was slashed within six months. "
            "And the Wii U, which sold just thirteen and a half million units, "
            "as Nintendo posted its first annual losses in decades. "
            "For a lot of companies, any one of those would have been fatal."
        ),
        visual=dict(
            type="timeline",
            heading="Five near-death experiences",
            items=[
                dict(year="1995", text="Virtual Boy — under 1M sold", s=0),
                dict(year="1996", text="N64 bets on cartridges, loses Final Fantasy", s=1),
                dict(year="2001", text="GameCube finishes a distant third", s=2),
                dict(year="2011", text="3DS price slashed within six months", s=3),
                dict(year="2012", text="Wii U: 13.56M sold, first losses in decades", s=4),
            ],
        ),
    ),
    dict(
        id="not_mario",
        text=(
            "The usual answer is: Mario. Great characters, great games. "
            "That's true, but it isn't enough. "
            "Sega had Sonic. Atari had the most famous brand in the world. "
            "Great games explain why Nintendo succeeds. They don't explain why it survives its failures. "
            "For that, you have to look at how the company is built. "
            "And when you do, four things stand out."
        ),
        visual=dict(
            type="list",
            heading="What actually decides it",
            numbered=True,
            items=[
                dict(text="A toy company's instincts", s=8),
                dict(text="Lateral thinking with withered technology", s=8),
                dict(text="Games are the product", s=8),
                dict(text="A fortress balance sheet", s=8),
            ],
            pre=dict(text="“It's Mario.” — true, but not sufficient", s=0),
        ),
    ),

    # ---------------------------------------------------------------- PART 1
    dict(
        id="p1_card",
        text="Part one. Nintendo is a toy company.",
        visual=dict(type="chapter", num="01", title="A Toy Company's Instincts", sub="Joy you can understand in seconds"),
    ),
    dict(
        id="p1_history",
        text=(
            "Nintendo was founded in Kyoto in 1889 by Fusajiro Yamauchi, to make hanafuda, hand-painted playing cards. "
            "For much of the twentieth century, it was a company searching for a second act. "
            "Under Fusajiro's great-grandson, Hiroshi Yamauchi, it tried a taxi service, instant rice, and, reportedly, love hotels. "
            "Almost none of it worked."
        ),
        visual=dict(
            type="timeline",
            heading="A company in search of a second act",
            items=[
                dict(year="1889", text="Founded in Kyoto to make hanafuda cards", s=0),
                dict(year="1949", text="Hiroshi Yamauchi takes over, aged 22", s=2),
                dict(year="1960s", text="Taxis, instant rice, love hotels…", s=2),
                dict(year="", text="Almost none of it works", s=3),
            ],
        ),
    ),
    dict(
        id="p1_ultrahand",
        text=(
            "What did work was toys. "
            "In 1966, a young maintenance engineer named Gunpei Yokoi built an extending grabber arm to amuse himself. "
            "Yamauchi saw it, and told him to turn it into a product. "
            "The Ultra Hand sold over a million units. "
            "Yokoi was moved into product development, and Nintendo quietly became a toy company."
        ),
        visual=dict(
            type="hero",
            kicker="1966 · GUNPEI YOKOI'S ULTRA HAND",
            big="1,000,000+",
            sub="A maintenance engineer's side project becomes a hit",
            s_big=3,
        ),
    ),
    dict(
        id="p1_yoyo",
        text=(
            "That matters more than it sounds. "
            "A toy company doesn't sell specifications. "
            "Nobody buys a yo-yo because of its processor. "
            "A toy has to be understood in seconds, and be fun in your hands. "
            "That instinct, fun first, explained by touch, runs straight through the NES, the Game Boy, the Wii Remote, and the Joy-Con."
        ),
        visual=dict(
            type="statement",
            text="Nobody buys a yo-yo because of its processor.",
            small="Fun first. Explained by touch.",
            s_text=2,
            s_small=3,
        ),
    ),
    dict(
        id="p1_rob",
        text=(
            "When Nintendo brought the NES to America after the crash, retailers wanted nothing to do with video games. "
            "So Nintendo didn't call it one. "
            "It was the Nintendo Entertainment System, and it came with a little plastic robot called R.O.B., "
            "so that wary stores would shelve it as a toy. "
            "It worked. The NES sold over sixty million units and revived the entire industry."
        ),
        visual=dict(
            type="hero",
            kicker="1985 · DISGUISED AS A TOY",
            big="61.9M",
            sub="NES consoles sold — and an industry revived",
            s_big=4,
        ),
    ),

    # ---------------------------------------------------------------- PART 2
    dict(
        id="p2_card",
        text="Part two. Lateral thinking with withered technology.",
        visual=dict(type="chapter", num="02", title="Lateral Thinking with Withered Technology", sub="Innovation without an arms race"),
    ),
    dict(
        id="p2_define",
        text=(
            "Yokoi eventually gave his philosophy a name. "
            "Lateral thinking with withered technology. "
            "Withered means mature: cheap, reliable, well understood. "
            "Lateral means using it in a way nobody expected. "
            "The Game and Watch came from Yokoi watching a bored businessman on a bullet train, fiddling with a calculator. "
            "Cheap screens, calculator chips, a simple game. It sold over forty million units."
        ),
        visual=dict(
            type="define",
            pairs=[
                dict(term="Withered", meaning="Mature, cheap, reliable, well understood", s=2),
                dict(term="Lateral", meaning="Used in a way nobody expected", s=3),
            ],
            footer="Game & Watch (1980): calculator parts → 40M+ sold",
            s_footer=6,
        ),
    ),
    dict(
        id="p2_gameboy",
        text=(
            "The Game Boy, in 1989, was the purest example. "
            "Its screen was a murky, greenish monochrome. "
            "Its rivals, the Atari Lynx and later the Sega Game Gear, had backlit color screens. "
            "They were more advanced in every way you could measure. "
            "They also ate through six double-A batteries in a few hours. "
            "The Game Boy ran for well over ten hours on four, cost less, and came with Tetris. "
            "With the Game Boy Color, it sold nearly a hundred and nineteen million units. "
            "The Lynx and the Game Gear are footnotes."
        ),
        visual=dict(
            type="versus",
            left=dict(title="Game Boy", lines=["Monochrome screen", "4 AA · 10+ hours", "Cheaper", "Tetris in the box"], s=1),
            right=dict(title="Lynx / Game Gear", lines=["Backlit color screens", "6 AA · a few hours", "More expensive", "More powerful"], s=2),
            verdict="Game Boy family: 118.7M sold",
            s_verdict=6,
            winner="left",
        ),
    ),
    dict(
        id="p2_wii_ds",
        text=(
            "The pattern keeps repeating. "
            "In the mid-2000s, Sony and Microsoft were racing toward high definition. "
            "Nintendo's Wii was barely more powerful than the GameCube. "
            "What it had was a motion controller your grandmother could understand in ten seconds. "
            "It sold more than a hundred million units, and turned up in retirement homes. "
            "The DS did the same for handhelds. Two screens, a stylus, and games like Brain Age that sold to people who had never called themselves gamers. "
            "A hundred and fifty-four million units."
        ),
        visual=dict(
            type="bars",
            title="Lateral thinking, in units sold (millions)",
            items=[
                dict(label="GameCube", value=21.74, s=2),
                dict(label="Wii", value=101.63, s=4, hl=True),
                dict(label="DS", value=154.02, s=7, hl=True),
            ],
            max=160,
        ),
    ),
    dict(
        id="p2_logic",
        text=(
            "The strategic logic is simple. "
            "If you compete on power, you're in a spending war with companies far bigger than you, "
            "and the winner is whoever can afford to lose money the longest. "
            "If you compete on a new way to play, there's nobody to outspend you, "
            "because nobody else is in that market."
        ),
        visual=dict(
            type="versus",
            left=dict(title="Compete on power", lines=["Spending war", "Bigger rivals", "Last to run out of cash wins"], s=1),
            right=dict(title="Compete on play", lines=["New kind of fun", "No one to outspend you", "A market of one"], s=2),
            verdict="Nintendo picks the fight nobody else is in",
            s_verdict=2,
            winner="right",
        ),
    ),

    # ---------------------------------------------------------------- PART 3
    dict(
        id="p3_card",
        text="Part three. The games are the product.",
        visual=dict(type="chapter", num="03", title="Games Are the Product", sub="Creativity treated as a craft"),
    ),
    dict(
        id="p3_miyamoto",
        text=(
            "At its core, Nintendo is a software company that happens to build the machines its software needs. "
            "Shigeru Miyamoto joined as a staff artist in 1977. "
            "One of his first big assignments was to rescue a warehouse of unsold arcade cabinets. "
            "The result was Donkey Kong, and its hero, a carpenter called Jumpman, would become Mario. "
            "Miyamoto's designs famously start from a feeling. "
            "His childhood memories of exploring the hills and caves around Kyoto became The Legend of Zelda."
        ),
        visual=dict(
            type="timeline",
            heading="Shigeru Miyamoto",
            items=[
                dict(year="1977", text="Joins Nintendo as a staff artist", s=1),
                dict(year="1981", text="Donkey Kong rescues unsold arcade cabinets", s=2),
                dict(year="1985", text="Jumpman becomes Mario: Super Mario Bros.", s=3),
                dict(year="1986", text="Childhood exploration becomes Zelda", s=5),
            ],
        ),
    ),
    dict(
        id="p3_quote",
        text=(
            "There's a line often attributed to him. "
            "A delayed game is eventually good, but a rushed game is forever bad. "
            "Whether or not he put it exactly that way, Nintendo behaves as if it believes it. "
            "Games slip, sometimes for years, until they feel right. "
            "Breath of the Wild was delayed repeatedly. So was its sequel. Both were hailed as instant classics."
        ),
        visual=dict(
            type="quote",
            text="A delayed game is eventually good, but a rushed game is forever bad.",
            by="Commonly attributed to Shigeru Miyamoto",
            s_text=1,
        ),
    ),
    dict(
        id="p3_together",
        text=(
            "And because Nintendo makes the hardware, it designs the two together. "
            "The Nintendo 64's analog stick was developed alongside Super Mario 64. "
            "The Wii Remote and Wii Sports grew up together. "
            "Competitors build a powerful box and invite the world to fill it. "
            "Nintendo builds a toy, and the game that explains it."
        ),
        visual=dict(
            type="statement",
            text="Competitors build a box and invite the world to fill it.",
            text2="Nintendo builds a toy — and the game that explains it.",
            s_text=3,
            s_text2=4,
        ),
    ),
    dict(
        id="p3_ip",
        text=(
            "Over decades, that produced the most valuable stable of characters in the industry. "
            "Mario. Zelda. Pokémon. Kirby. Animal Crossing. Smash Bros. "
            "Pokémon, which Nintendo co-owns, is the highest-grossing media franchise in history. "
            "Mario Kart 8 Deluxe has sold more than sixty million copies on a single console. "
            "And these games don't expire. "
            "Nintendo rarely discounts its own titles deeply, because a Mario game from six years ago still sells like a new release."
        ),
        visual=dict(
            type="list",
            heading="Characters that never expire",
            numbered=False,
            columns=2,
            items=[
                dict(text="Mario", s=1), dict(text="The Legend of Zelda", s=2),
                dict(text="Pokémon", s=3), dict(text="Kirby", s=4),
                dict(text="Animal Crossing", s=5), dict(text="Super Smash Bros.", s=6),
            ],
            footer="Mario Kart 8 Deluxe: 60M+ copies on one console",
            s_footer=7,
        ),
    ),
    dict(
        id="p3_survive",
        text=(
            "This is the part that makes failure survivable. "
            "When a Nintendo console flops, the people who bought it still got Mario Kart, Zelda, and Smash. "
            "And those franchises walk straight onto the next machine, with their fans right behind them."
        ),
        visual=dict(
            type="statement",
            text="Consoles come and go. The characters walk onto the next machine.",
            small="…and the fans follow them",
            s_text=1,
            s_small=2,
        ),
    ),

    # ---------------------------------------------------------------- PART 4
    dict(
        id="p4_card",
        text="Part four. The fortress.",
        visual=dict(type="chapter", num="04", title="A Fortress Balance Sheet", sub="The least glamorous reason it survives"),
    ),
    dict(
        id="p4_money",
        text=(
            "Which brings us to the least glamorous reason Nintendo survives, and maybe the most important. Money. "
            "Hiroshi Yamauchi ran Nintendo like a company that expected bad weather. "
            "Unlike its rivals, Nintendo has generally insisted that its hardware sell at a profit, or close to it, from early on. "
            "Sony and Microsoft can subsidize a console because they have other huge businesses. "
            "Nintendo doesn't. So every machine has to pay its own way. "
            "It also keeps an enormous pile of cash and essentially no debt. "
            "In good years, critics called that capital lazy. "
            "Then the Wii U happened, and the cash did exactly what it was there for. It bought time."
        ),
        visual=dict(
            type="list",
            heading="Built for bad weather",
            numbered=False,
            items=[
                dict(text="Hardware that pays its own way", s=3),
                dict(text="Huge cash reserves", s=7),
                dict(text="Essentially no debt", s=7),
                dict(text="Cash that buys time when a bet fails", s=9),
            ],
        ),
    ),
    dict(
        id="p4_handheld",
        text=(
            "Then there's the handheld safety net. "
            "For nearly three decades, Nintendo ran two separate hardware lines. "
            "When the home console stumbled, the handheld carried the company. "
            "The GameCube struggled, but the Game Boy Advance sold over eighty million units. "
            "The Wii U flopped, but the 3DS sold more than seventy-five million. "
            "There was always a second leg to stand on."
        ),
        visual=dict(
            type="bars",
            title="The second leg to stand on (units sold, millions)",
            items=[
                dict(label="GameCube", value=21.74, s=3),
                dict(label="Game Boy Advance", value=81.51, s=3, hl=True),
                dict(label="Wii U", value=13.56, s=4),
                dict(label="3DS", value=75.94, s=4, hl=True),
            ],
            max=90,
            legend=("Home console", "Handheld"),
        ),
    ),
    dict(
        id="p4_iwata",
        text=(
            "Leadership matters here too. "
            "In 2011, after the 3DS price cut, president Satoru Iwata cut his own salary in half. "
            "When investors later pushed for layoffs, he refused. "
            "His argument was that employees who fear being laid off will not make software that impresses people around the world. "
            "That kind of decision is only possible if the balance sheet gives you room to make it."
        ),
        visual=dict(
            type="quote",
            text="Employees who fear that they may be laid off will not be able to develop software titles that impress people around the world.",
            by="Satoru Iwata, paraphrased from a 2014 shareholder meeting",
            s_text=3,
        ),
    ),

    # ---------------------------------------------------------------- SYNTHESIS
    dict(
        id="p5_card",
        text="Now put all four together, and look at the Switch.",
        visual=dict(type="chapter", num="05", title="All Four at Once", sub="The Switch"),
    ),
    dict(
        id="p5_switch",
        text=(
            "By 2017, Nintendo was coming off the Wii U, its worst-selling home console. "
            "Smartphones were eating the casual market the DS once owned. "
            "Plenty of analysts said it was time to quit hardware and put Mario on the iPhone, the way Sega had gone software-only. "
            "Instead, Nintendo merged its two hardware lines into one. "
            "The Switch ran on an off-the-shelf mobile chip. Withered technology, again. "
            "It was a toy you understood in a second. Pick it up, take it with you, hand a Joy-Con to a friend. "
            "And it launched alongside Breath of the Wild, a game that had been allowed to take years."
        ),
        visual=dict(
            type="list",
            heading="The Switch, 2017",
            numbered=False,
            items=[
                dict(text="Toy instincts: pick it up, share a Joy-Con", s=6),
                dict(text="Withered tech: an off-the-shelf mobile chip", s=4),
                dict(text="Games first: Breath of the Wild at launch", s=8),
                dict(text="Fortress: two hardware lines merged into one", s=3),
            ],
        ),
    ),
    dict(
        id="p5_results",
        text=(
            "The Switch went on to sell more than a hundred and fifty million units, "
            "putting it in the same tier as the DS and the PlayStation 2 among the best-selling consoles ever. "
            "Its successor, the Switch 2, launched in June 2025 and sold three and a half million units in four days, "
            "the fastest start of any Nintendo hardware. "
            "The company that was told to give up on hardware built one of the most successful hardware businesses in history."
        ),
        visual=dict(
            type="bars",
            title="Nintendo hardware, lifetime units (millions)",
            items=[
                dict(label="Wii U", value=13.56, s=0),
                dict(label="GameCube", value=21.74, s=0),
                dict(label="N64", value=32.93, s=0),
                dict(label="SNES", value=49.10, s=0),
                dict(label="NES", value=61.91, s=0),
                dict(label="3DS", value=75.94, s=0),
                dict(label="Wii", value=101.63, s=0),
                dict(label="Game Boy / Color", value=118.69, s=0),
                dict(label="Switch", value=150.0, s=0, hl=True, plus=True),
                dict(label="DS", value=154.02, s=0),
            ],
            max=160,
            compact=True,
            footer="Switch 2 (June 2025): 3.5M in its first four days",
            s_footer=1,
        ),
    ),
    dict(
        id="p5_beyond",
        text=(
            "Nintendo has also learned to take its characters beyond games without giving them away. "
            "Theme parks with Universal. "
            "The Super Mario Bros. Movie in 2023, which grossed over a billion dollars worldwide. "
            "Each of those is, in the end, an advertisement for the games."
        ),
        visual=dict(
            type="hero",
            kicker="THE SUPER MARIO BROS. MOVIE · 2023",
            big="$1.3B+",
            sub="Worldwide box office: an advertisement for the games",
            s_big=2,
        ),
    ),

    # ---------------------------------------------------------------- WEAKNESSES
    dict(
        id="p6_weak",
        text=(
            "So is Nintendo invincible? No. "
            "Its model has real weaknesses. "
            "Every six or seven years, it bets the company on a brand new idea, and some of those ideas will be wrong. "
            "The same conservatism that protects it also makes it slow. Its online services have lagged behind for years. "
            "And its hard line on prices, emulation, and fan projects costs it real goodwill."
        ),
        visual=dict(
            type="list",
            heading="Not invincible",
            numbered=False,
            items=[
                dict(text="Bets the company on a new idea every cycle", s=3),
                dict(text="Conservative to the point of slow", s=4),
                dict(text="Online services that lag behind", s=5),
                dict(text="Hard line on prices and fan projects", s=6),
            ],
        ),
    ),
    dict(
        id="p6_compare",
        text=(
            "But compare the failure modes. "
            "Atari collapsed because it flooded the market with low-quality games and lost the trust of players. "
            "Sega burned through its cash and its customers' patience with too many machines in too few years, and couldn't absorb the Dreamcast. "
            "Most of the companies on that list died because one bad bet consumed everything."
        ),
        visual=dict(
            type="versus",
            left=dict(title="Atari", lines=["Flooded the market", "Lost players' trust", "Collapsed in 1983–84"], s=1),
            right=dict(title="Sega", lines=["Too many machines, too fast", "Ran out of cash", "Quit hardware in 2001"], s=2),
            verdict="One bad bet consumed everything",
            s_verdict=3,
            winner=None,
        ),
    ),

    # ---------------------------------------------------------------- CONCLUSION
    dict(
        id="c_answer",
        text=(
            "Nintendo is built so that a bad bet can't consume everything. "
            "Hardware that pays for itself. Cash that buys time. Characters that outlive any console. "
            "And a toy maker's instinct to find a new way to play, instead of fighting someone bigger on their terms."
        ),
        visual=dict(
            type="list",
            heading="What actually keeps it alive",
            numbered=True,
            items=[
                dict(text="Hardware that pays for itself", s=1),
                dict(text="Cash that buys time", s=2),
                dict(text="Characters that outlive any console", s=3),
                dict(text="A new way to play, not a bigger box", s=4),
            ],
        ),
    ),
    dict(
        id="c_final",
        text=(
            "That's the real answer. "
            "It isn't that Nintendo doesn't fail. It fails all the time. Loudly, publicly, and expensively. "
            "It's that the company is designed, very deliberately, to survive its failures long enough to reach the next idea. "
            "And every so often, the next idea is the Wii. Or the DS. Or the Switch."
        ),
        visual=dict(
            type="statement",
            text="Nintendo doesn't avoid failure.",
            text2="It's built to survive failure long enough to reach the next idea.",
            s_text=1,
            s_text2=4,
        ),
    ),
    dict(
        id="c_outro",
        text=(
            "A hundred and thirty-seven years after it started selling playing cards, "
            "Nintendo is still in the business of making something fun to hold in your hands. "
            "Everything else is just how it pays for the next one."
        ),
        visual=dict(
            type="title",
            title="1889 → today",
            sub="Still making something fun to hold in your hands",
            s_sub=1,
            end=True,
        ),
    ),
]
