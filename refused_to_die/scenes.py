"""Nintendo: The Company That Refused to Die — scene plan.

Narration follows the production brief's script. Changes from the brief:
  * Sales figures updated to Nintendo's latest disclosure (six months ended
    September 30, 2026, released November 5, 2026), as the brief instructs.
  * "135 years" -> "137 years" (founded 1889; it is now 2026).

Visual cues (`s`) are a sentence index or, preferably, a substring of the
sentence at which the element should appear.
Build:  python3 ../nintendo_video/build.py --project .
"""

SLUG = "nintendo_the_company_that_refused_to_die"
OUT_SUBDIR = "refused_to_die"
SERIES = "NINTENDO: THE COMPANY THAT REFUSED TO DIE"
MUSIC = "arc"
RATE = "+4%"
SENT_GAP = 0.28
SCENE_GAP = 0.72

CH = 2.3  # silent chapter-card hold (visual + musical reset)


def chapter(id_, num, title, sub, mood, label="CHAPTER", hud=None, chapter_name=None, bg=None):
    sc = dict(id=id_, text="", hold=CH, mood=mood,
              chapter=chapter_name or title,
              visual=dict(type="chapter", num=num, title=title, sub=sub, label=label,
                          hud=hud or f"{num} · {title.upper()}"))
    if bg:
        sc["bg"] = bg
    return sc


SCENES = [
    # ================================================================ 0 · COLD OPEN
    dict(
        id="open_exhibits", mood="open", bg="dark", chapter="The survivors", hud="THE SURVIVORS",
        text=(
            "Video games are an industry that eats its kings. "
            "Atari defined the home console—and collapsed. "
            "Sega challenged the world—and left the hardware business. "
            "Entire generations of studios, machines, and billion-dollar strategies have arrived, dominated, and disappeared."
        ),
        visual=dict(
            type="exhibits", heading="An industry that eats its kings", s_heading=0,
            items=[
                dict(title="Atari", caption="Defined the home console. Collapsed.", s="Atari defined"),
                dict(title="Sega", caption="Challenged the world. Left hardware in 2001.", s="Sega challenged"),
                dict(title="The next big thing", caption="Arrived, dominated, disappeared.", s="Entire generations"),
            ],
        ),
        sfx=[("Atari defined", "boot"), ("Sega challenged", "boot"), ("Entire generations", "boot")],
    ),
    dict(
        id="open_survived", bg="dark",
        text=(
            "But one company keeps coming back. "
            "It survived the crash of the American games market. "
            "It survived Sony. It survived Microsoft. "
            "It survived its own worst console. "
            "And it did this while routinely selling less powerful hardware than everyone else."
        ),
        visual=dict(
            type="list", heading="One company keeps coming back", check=True,
            items=[
                dict(text="The crash of the American games market", s="crash"),
                dict(text="Sony", s="survived Sony"),
                dict(text="Microsoft", s="survived Microsoft"),
                dict(text="Its own worst console", s="worst console"),
            ],
            footer="…usually with less powerful hardware", s_footer="less powerful",
        ),
    ),
    dict(
        id="open_1889", bg="dark",
        text=(
            "Nintendo began in 1889, making playing cards in Kyoto. "
            "More than a century later, it remains one of the most important entertainment companies on Earth."
        ),
        visual=dict(type="hero", kicker="KYOTO · HANAFUDA PLAYING CARDS", big="1889",
                    sub="Still one of the most important entertainment companies on Earth", s_big=0),
    ),
    dict(
        id="open_question", bg="dark",
        text=(
            "The obvious question is how. "
            "The better question is: what does Nintendo understand about play that its competitors keep forgetting?"
        ),
        visual=dict(type="statement", text="The obvious question: how?",
                    text2="The better question: what does Nintendo understand about play that its competitors keep forgetting?",
                    s_text=0, s_text2=1),
    ),
    dict(
        id="title", text="", hold=4.2, mood="playful",
        visual=dict(type="title", title="Nintendo: The Company That Refused to Die", sub="What it understands about play", s_sub=None),
    ),

    # ================================================================ 1 · THE PARADOX
    dict(
        id="paradox_rail", chapter="The Nintendo paradox", hud="THE NINTENDO PARADOX",
        text=(
            "Nintendo's history is often told as a parade of beloved things: Mario, Zelda, Pokémon, the Game Boy, the Wii, the Switch. "
            "That is true. "
            "It is also incomplete."
        ),
        visual=dict(
            type="rail", heading="A parade of beloved things",
            nodes=[
                dict(year="1889", label="Hanafuda cards", s=0),
                dict(year="1983", label="Famicom", s=0),
                dict(year="1989", label="Game Boy", s=0),
                dict(year="2006", label="Wii", s=0),
                dict(year="2012", label="Wii U", s=0),
                dict(year="2017", label="Switch", s=0),
                dict(year="2025", label="Switch 2", s=0),
            ],
            footer="True — and incomplete", s_footer="incomplete",
        ),
    ),
    dict(
        id="paradox_wrong",
        text=(
            "Nintendo has spent much of its life making decisions that looked wrong at the time. "
            "The Game Boy's screen was monochrome when color competitors already existed. "
            "The Wii ignored the high-definition arms race. "
            "The Switch launched with mobile-class hardware into a world of 4K consoles."
        ),
        visual=dict(
            type="list", heading="Decisions that looked wrong at the time",
            items=[
                dict(text="Game Boy — monochrome, when color rivals existed", s="Game Boy's screen"),
                dict(text="Wii — ignored the high-definition arms race", s="The Wii ignored"),
                dict(text="Switch — mobile-class chips in a 4K world", s="The Switch launched"),
            ],
        ),
    ),
    dict(
        id="paradox_failed",
        text=(
            "And Nintendo has failed—badly. "
            "The Virtual Boy was abandoned. "
            "The GameCube finished behind its main rivals. "
            "The Wii U sold only 13.56 million units."
        ),
        visual=dict(
            type="timeline", heading="And it has failed — badly",
            items=[
                dict(year="1995", text="Virtual Boy — abandoned", s="Virtual Boy"),
                dict(year="2001", text="GameCube — behind its main rivals", s="GameCube"),
                dict(year="2012", text="Wii U — 13.56M units, lifetime", s="Wii U sold"),
            ],
        ),
    ),
    dict(
        id="paradox_numbers",
        text=(
            "Yet by September 2026, the original Switch family had sold more than 157 million systems. "
            "Switch 2 sold almost 20 million in its first fiscal year. "
            "Nintendo's financial year ending March 2026 produced 2.31 trillion yen in net sales."
        ),
        visual=dict(
            type="cards",
            items=[
                dict(big="157.2M", label="Switch family hardware", note="as of Sept 30, 2026", s=0),
                dict(big="19.86M", label="Switch 2 in its first fiscal year", note="FY ended March 2026", s=1, hl=True),
                dict(big="¥2.313T", label="Net sales", note="FY ended March 2026", s=2),
            ],
        ),
    ),
    dict(
        id="paradox_thesis",
        text=(
            "This is not a story of uninterrupted genius. "
            "It is a story about a company with an unusually effective way of recovering from being wrong."
        ),
        visual=dict(type="statement", text="Not a story of uninterrupted genius.",
                    text2="A company with an unusually effective way of recovering from being wrong.", s_text=0, s_text2=1),
    ),

    # ================================================================ 2 · PRINCIPLE ONE
    chapter("ch_action", "01", "Nintendo Sells an Action", "Start with what the player does", "playful",
            label="PRINCIPLE ONE", hud="PRINCIPLE 01 · NINTENDO SELLS AN ACTION", chapter_name="Nintendo sells an action"),
    dict(
        id="action_split",
        text=(
            "Most technology companies begin with a machine. "
            "Nintendo often begins with an action."
        ),
        visual=dict(
            type="versus",
            left=dict(title="A machine", lines=["Faster processor", "More memory", "Higher resolution", "A longer spec sheet"], s=0),
            right=dict(title="An action", lines=["Draw on a second screen", "Swing a remote", "Lift it off the TV", "Hand over a controller"], s=1),
            verdict="Nintendo begins with what your hands do", s_verdict=1, winner="right",
        ),
    ),
    dict(
        id="action_whatif",
        text=(
            "What if a game continued in your pocket? "
            "What if you aimed by moving your hand? "
            "What if two people could play by splitting one controller? "
            "What if a console could follow you from the television to the train without ending the game? "
            "That distinction sounds small. "
            "It changes everything."
        ),
        visual=dict(
            type="list", heading="What if…",
            items=[
                dict(text="…a game continued in your pocket?", s=0),
                dict(text="…you aimed by moving your hand?", s=1),
                dict(text="…two people split one controller?", s=2),
                dict(text="…a console followed you from TV to train?", s=3),
            ],
            footer="A small distinction that changes everything", s_footer="changes everything",
        ),
    ),
    dict(
        id="action_toy",
        text=(
            "When Nintendo entered electronic toys, its great advantage was not semiconductor expertise. "
            "It was the mentality of a toy maker: the product had to explain itself through play."
        ),
        visual=dict(type="statement", text="The product had to explain itself through play.",
                    small="The mentality of a toy maker — not semiconductor expertise", s_text=1, s_small=1),
    ),
    dict(
        id="action_gw_dk",
        text=(
            "The Game & Watch did not ask people to imagine a portable computer. "
            "It put one tiny game in a pocket. "
            "Donkey Kong did not sell processing power. "
            "It gave players a story they could understand in seconds: a carpenter, a captive, a giant ape, and a ladder."
        ),
        visual=dict(
            type="timeline", heading="Understood in seconds",
            items=[
                dict(year="1980", text="Game & Watch — one tiny game in a pocket", s="one tiny game"),
                dict(year="1981", text="Donkey Kong — carpenter, captive, ape, ladder", s="story they could understand"),
            ],
        ),
    ),
    dict(
        id="action_readable",
        text=(
            "Shigeru Miyamoto's great contribution was not merely inventing characters. "
            "It was making mechanics readable. "
            "Mario's jump, Link's sword, the ink in Splatoon—each tells the player what the world is for."
        ),
        visual=dict(
            type="list", heading="Readable mechanics",
            pre=dict(text="Shigeru Miyamoto's real contribution", s=0),
            items=[
                dict(text="Mario's jump", s=2),
                dict(text="Link's sword", s=2),
                dict(text="The ink in Splatoon", s=2),
            ],
            footer="Each tells the player what the world is for", s_footer=2,
        ),
    ),
    dict(
        id="action_integrated",
        text=(
            "Nintendo calls much of this “integrated hardware and software.” "
            "But the corporate phrase hides the magic. "
            "A Nintendo machine is strongest when one physical gesture and one digital response feel inseparable."
        ),
        visual=dict(
            type="flow", kicker="“INTEGRATED HARDWARE AND SOFTWARE”", bidir=True,
            nodes=[dict(text="One physical gesture", s=2), dict(text="One digital response", s=2, hl=True)],
            footer="Strongest when they feel inseparable", s_footer=2,
        ),
    ),
    dict(
        id="action_why",
        text=(
            "The DS had two screens because Nintendo wanted new kinds of attention. "
            "The Wii had motion controls because it wanted new kinds of players. "
            "The Switch had rails, a kickstand, and detachable controllers because it wanted play to move between rooms and people."
        ),
        visual=dict(
            type="chain", heading="The hardware follows the action",
            rows=[
                dict(a="DS · two screens", b="New kinds of attention", s=0),
                dict(a="Wii · motion controls", b="New kinds of players", s=1),
                dict(a="Switch · rails, kickstand, detachable controllers", b="Play that moves between rooms and people", s=2),
            ],
        ),
    ),
    dict(
        id="action_question",
        text=(
            "Competitors asked: how much more can the box do? "
            "Nintendo asked: what can the player do now that they could not do before?"
        ),
        visual=dict(type="statement", text="Competitors: how much more can the box do?",
                    text2="Nintendo: what can the player do now that they could not do before?", s_text=0, s_text2=1),
    ),

    # ================================================================ 3 · PRINCIPLE TWO
    chapter("ch_lateral", "02", "Lateral Thinking with Withered Technology", "Old parts, new behavior", "playful",
            label="PRINCIPLE TWO", hud="PRINCIPLE 02 · LATERAL THINKING", chapter_name="Lateral thinking"),
    dict(
        id="lateral_define",
        text=(
            "This philosophy has a name, associated with legendary Nintendo designer Gunpei Yokoi: lateral thinking with withered technology. "
            "Use mature, inexpensive, well-understood technology—and combine it in a way nobody expects."
        ),
        visual=dict(
            type="define", byline="— a philosophy associated with Gunpei Yokoi",
            pairs=[
                dict(term="Withered", meaning="Mature, inexpensive, well understood", s=1),
                dict(term="Lateral", meaning="Combined in a way nobody expects", s=1),
            ],
        ),
    ),
    dict(
        id="lateral_gameboy",
        text=(
            "The original Game Boy is the perfect example. "
            "In 1989, it was not the most advanced handheld. "
            "Its screen had no color. "
            "It looked almost stubbornly old-fashioned. "
            "But older technology meant lower cost, longer battery life, and hardware Nintendo understood. "
            "Then Tetris turned those limitations into a mass-market machine."
        ),
        visual=dict(
            type="versus",
            left=dict(title="What it gave up", lines=["Color", "The newest screen tech", "Looking advanced"], s="not the most advanced"),
            right=dict(title="What it gained", lines=["Lower cost", "Longer battery life", "Hardware it understood", "Tetris"], s="older technology meant"),
            verdict="Game Boy, 1989: limitations → a mass-market machine", s_verdict="Tetris", winner="right",
        ),
    ),
    dict(
        id="lateral_wii",
        text=(
            "The Wii repeated the trick. "
            "Sony and Microsoft competed over high-definition graphics and expensive processors. "
            "Nintendo used modest hardware and a motion-sensitive remote that looked familiar to anyone who had used a television. "
            "The result was not merely a cheaper console. "
            "It was an invitation. "
            "Parents, grandparents, and people who would never memorize twelve buttons could understand bowling before the first ball left their hand."
        ),
        visual=dict(
            type="versus",
            left=dict(title="Sony & Microsoft", lines=["High-definition graphics", "Expensive processors", "More buttons"], s="Sony and Microsoft"),
            right=dict(title="Wii", lines=["Modest hardware", "A remote anyone recognizes", "Bowling, understood instantly"], s="Nintendo used modest"),
            verdict="Not a cheaper console — an invitation", s_verdict="invitation", winner="right",
        ),
    ),
    dict(
        id="lateral_power",
        text=(
            "This is why judging Nintendo by technical specifications so often misses the point. "
            "Power is useful, but power is easily copied and eventually becomes ordinary. "
            "A new behavior is harder. "
            "It requires hardware, software, interface, price, and timing to land together."
        ),
        visual=dict(
            type="list", heading="A new behavior is harder to copy", numbered=True, columns=2,
            pre=dict(text="Power is easily copied — and eventually ordinary", s="Power is useful"),
            items=[
                dict(text="Hardware", s=3), dict(text="Software", s=3), dict(text="Interface", s=3),
                dict(text="Price", s=3), dict(text="Timing", s=3),
            ],
            footer="All five have to land together", s_footer=3,
        ),
    ),
    dict(
        id="lateral_recombine",
        text=(
            "Nintendo's innovation is rarely invention from nothing. "
            "It is recombination: old components, rearranged around a fresh human experience."
        ),
        visual=dict(
            type="chain", heading="Recombination, not invention", blueprint=True,
            rows=[
                dict(a="Calculator LCD", b="Game & Watch", s=0),
                dict(a="Monochrome screen", b="Game Boy", s=0),
                dict(a="Commodity motion sensors", b="Wii Remote", s=1),
                dict(a="Tablet components", b="Switch", s=1),
            ],
        ),
    ),

    # ================================================================ 4 · PRINCIPLE THREE
    chapter("ch_memory", "03", "Characters Are Memory Machines", "Carrying a moment across time", "playful",
            label="PRINCIPLE THREE", hud="PRINCIPLE 03 · CHARACTERS ARE MEMORY MACHINES", chapter_name="Characters as memory machines"),
    dict(
        id="memory_moment",
        text="Hardware creates a moment. Characters carry that moment across time.",
        visual=dict(type="statement", text="Hardware creates a moment.", text2="Characters carry that moment across time.",
                    s_text=0, s_text2=1),
    ),
    dict(
        id="memory_mario",
        text=(
            "Mario is not valuable only because people recognize his face. "
            "Mario is a memory machine. "
            "For one generation, he is the first secret block in Super Mario Bros. "
            "For another, the castle in Mario 64. "
            "For another, a family argument on Rainbow Road."
        ),
        visual=dict(
            type="timeline", heading="Mario is a memory machine",
            items=[
                dict(year="1985", text="The first secret block — Super Mario Bros.", s="first secret block"),
                dict(year="1996", text="The castle — Super Mario 64", s="castle"),
                dict(year="Today", text="A family argument on Rainbow Road", s="Rainbow Road"),
            ],
        ),
    ),
    dict(
        id="memory_forms",
        text=(
            "Nintendo's franchises survive because they are consistent in feeling but flexible in form. "
            "Zelda can be a top-down puzzle, a 3D adventure, a motion-control experiment, or an open world built around physics and improvisation. "
            "Mario can be a platformer, a racing game, a party game, a role-playing game, or a film. "
            "The character remains familiar. "
            "The activity changes."
        ),
        visual=dict(
            type="versus",
            left=dict(title="Zelda", lines=["Top-down puzzle", "3D adventure", "Motion-control experiment", "Physics-driven open world"], s="Zelda can be"),
            right=dict(title="Mario", lines=["Platformer", "Racing & party games", "Role-playing games", "A film"], s="Mario can be"),
            verdict="Consistent in feeling. Flexible in form.", s_verdict="remains familiar", winner=None,
        ),
    ),
    dict(
        id="memory_compound",
        text=(
            "That balance compounds. "
            "Each successful game sells the next one. "
            "Each console arrives with a library of emotional associations already waiting for it. "
            "Parents who once received a Game Boy can give their children a Switch without needing the brand explained."
        ),
        visual=dict(
            type="flow", heading="The balance compounds", loop=True,
            nodes=[
                dict(text="A great game", s=1), dict(text="A lasting memory", s=1),
                dict(text="Trust in the next one", s=2), dict(text="A new console", s=2, hl=True),
            ],
            footer="Game Boy kid → Switch parent", s_footer="Parents who once",
        ),
    ),
    dict(
        id="memory_ip",
        text=(
            "This is also why Nintendo protects its intellectual property so aggressively. "
            "The legal posture can feel severe. "
            "But strategically, the company is guarding the continuity between generations—the belief that a Mario experience will still feel like Mario."
        ),
        visual=dict(type="statement", text="Guarding the continuity between generations.",
                    small="A Mario experience must still feel like Mario", s_text=2, s_small=2),
    ),
    dict(
        id="memory_beyond",
        text=(
            "And the loop now extends beyond consoles: films, theme parks, stores, museums, and merchandise create more doors into the same worlds. "
            "Nintendo is no longer using games to support hardware alone. "
            "It is using hardware, games, and physical experiences to keep a universe of characters culturally alive."
        ),
        visual=dict(
            type="list", heading="More doors into the same worlds", columns=2,
            items=[
                dict(text="Films", s=0), dict(text="Theme parks", s=0), dict(text="Stores", s=0),
                dict(text="A museum", s=0), dict(text="Merchandise", s=0), dict(text="Games & hardware", s=1),
            ],
            footer="Keeping a universe of characters culturally alive", s_footer=2,
        ),
    ),

    # ================================================================ 5 · THE WII U CRASH
    chapter("ch_crash", "04", "The Crash: Wii U", "When the action is not clear", "thin",
            hud="THE WII U CRASH", chapter_name="The Wii U crash", bg="cool"),
    dict(
        id="crash_why", bg="cool",
        text=(
            "But this system can fail when the action is not clear. "
            "The Wii U had a controller with a screen. "
            "It offered asymmetric multiplayer, off-TV play, and clever ideas. "
            "But the name sounded like an accessory for the Wii. "
            "The marketing struggled to explain why the second screen mattered. "
            "Third-party support weakened. "
            "Software arrived too slowly."
        ),
        visual=dict(
            type="list", heading="When the action is not clear",
            pre=dict(text="Clever ideas: asymmetric multiplayer, off-TV play", s="asymmetric"),
            items=[
                dict(text="A name that sounded like an accessory", s="the name sounded"),
                dict(text="A second screen nobody could explain", s="marketing struggled"),
                dict(text="Weakening third-party support", s="Third-party"),
                dict(text="Software that arrived too slowly", s="Software arrived"),
            ],
        ),
    ),
    dict(
        id="crash_swing", bg="cool",
        text="The Wii had been understood in a single swing. The Wii U required a paragraph.",
        visual=dict(type="statement", text="The Wii was understood in a single swing.", text2="The Wii U required a paragraph.",
                    s_text=0, s_text2=1),
    ),
    dict(
        id="crash_number", bg="cool",
        text=(
            "It became Nintendo's worst-selling home console, with 13.56 million units. "
            "In the fiscal year ending March 2014, Nintendo reported an operating loss."
        ),
        visual=dict(type="hero", kicker="WII U · LIFETIME HARDWARE UNITS", big="13.56M",
                    sub="Worst-selling Nintendo home console · operating loss, FY ending March 2014", s_big=0),
    ),
    dict(
        id="crash_rail", bg="cool",
        text=(
            "This is the point where a conventional technology company might retreat toward the industry standard: "
            "build a more powerful box, copy the successful interface, compete on familiar terms. "
            "Nintendo did something more revealing. "
            "It kept the core insight and discarded the confusing product."
        ),
        visual=dict(
            type="rail", heading="The line breaks",
            nodes=[
                dict(year="1983", label="Famicom", s=0),
                dict(year="1989", label="Game Boy", s=0),
                dict(year="2006", label="Wii", s=0),
                dict(year="2012", label="Wii U", s=0, value="13.56M"),
                dict(year="?", label="Retreat to the standard?", s=0, dim=True),
            ],
            break_after=3,
            footer="Keep the insight. Discard the product.", s_footer="kept the core insight",
        ),
    ),
    dict(
        id="crash_keep", bg="cool",
        text=(
            "Off-TV play had been useful. "
            "A personal screen near the television had been useful. "
            "Local multiplayer built around unusual controllers had been useful. "
            "The problem was that these ideas were trapped in a machine that could not leave the room."
        ),
        visual=dict(
            type="list", heading="The insights worth keeping", check=True,
            items=[
                dict(text="Off-TV play", s=0),
                dict(text="A personal screen near the television", s=1),
                dict(text="Local multiplayer around unusual controllers", s=2),
            ],
            footer="…trapped in a machine that could not leave the room", s_footer=3,
        ),
    ),
    dict(
        id="crash_room", bg="cool",
        text="So Nintendo removed the room.",
        visual=dict(type="statement", text="So Nintendo removed the room.", s_text=0),
    ),

    # ================================================================ 6 · THE SWITCH RECOVERY
    chapter("ch_recovery", "05", "The Recovery: Switch", "The Wii U's best idea, completed", "warm",
            hud="THE SWITCH RECOVERY", chapter_name="The Switch recovery"),
    dict(
        id="recovery_morph",
        text=(
            "The Switch was not a rejection of the Wii U. "
            "It was the Wii U's best idea, completed. "
            "One screen. "
            "Two detachable controllers. "
            "A dock that made the transition to television almost invisible. "
            "And a reveal trailer that explained the entire product without a technical lecture."
        ),
        visual=dict(
            type="morph", s_morph="best idea", s_detach="Two detachable",
            labels=[
                dict(text="One screen", s="One screen"),
                dict(text="Detachable controllers", s="Two detachable"),
                dict(text="An invisible dock", s="A dock"),
                dict(text="A self-explaining trailer", s="reveal trailer"),
            ],
        ),
    ),
    dict(
        id="recovery_journey",
        text=(
            "Play at home. "
            "Lift the console. "
            "Keep playing. "
            "Share a controller. "
            "Play together."
        ),
        visual=dict(
            type="journey",
            stations=[
                dict(label="Play at home", sub="docked to the TV", s=0),
                dict(label="Lift the console", s=1),
                dict(label="Keep playing", sub="train, park, airport", s=2),
                dict(label="Share a controller", s=3),
                dict(label="Play together", s=4),
            ],
        ),
    ),
    dict(
        id="recovery_unify",
        text=(
            "The machine unified Nintendo's handheld and home-console development. "
            "Instead of splitting major games between two platforms, Nintendo could concentrate its software on one."
        ),
        visual=dict(
            type="flow", heading="Two hardware lines become one",
            nodes=[
                dict(text="Handheld development", s=0), dict(text="Home-console development", s=0),
                dict(text="One platform", s=0, hl=True), dict(text="Every major game in one place", s=1),
            ],
        ),
    ),
    dict(
        id="recovery_games",
        text=(
            "Then came the crucial part: the games. "
            "The Legend of Zelda: Breath of the Wild made the launch feel like a new beginning. "
            "Mario Kart 8 Deluxe turned an overlooked Wii U game into one of the best-selling games in Nintendo's history. "
            "Animal Crossing: New Horizons arrived at the exact moment millions of people needed a gentle place to be together."
        ),
        visual=dict(
            type="timeline", heading="Then came the games",
            items=[
                dict(year="2017", text="Breath of the Wild — a new beginning", s="Breath of the Wild"),
                dict(year="2017", text="Mario Kart 8 Deluxe — a Wii U game, reborn", s="Mario Kart 8"),
                dict(year="2020", text="Animal Crossing — a gentle place to be together", s="Animal Crossing"),
            ],
        ),
    ),
    dict(
        id="recovery_proposition",
        text=(
            "The Switch did not win because it had the best graphics. "
            "It won because the proposition remained useful for years: "
            "this is your console, your handheld, and sometimes the thing you hand to the person beside you."
        ),
        visual=dict(type="statement", text="Your console. Your handheld.",
                    text2="And sometimes the thing you hand to the person beside you.", s_text=1, s_text2=1),
    ),
    dict(
        id="recovery_numbers",
        text=(
            "By September 2026, Switch hardware sales had passed 157 million, "
            "with nearly 1.6 billion software units sold."
        ),
        visual=dict(
            type="cards", heading="Nintendo Switch, life to date",
            items=[
                dict(big="157.20M", label="Hardware units", note="as of Sept 30, 2026", s=0, hl=True),
                dict(big="1.594B", label="Software units", note="as of Sept 30, 2026", s=0),
            ],
        ),
    ),
    dict(
        id="recovery_rail",
        text=(
            "That recovery—from 13.56 million Wii U systems to more than 157 million Switch systems—is not evidence that Nintendo never makes mistakes. "
            "It is evidence that Nintendo knows how to salvage an insight from a mistake."
        ),
        visual=dict(
            type="rail", heading="The line reconnects",
            nodes=[
                dict(year="1983", label="Famicom", s=0),
                dict(year="1989", label="Game Boy", s=0),
                dict(year="2006", label="Wii", s=0),
                dict(year="2012", label="Wii U", s=0, value="13.56M"),
                dict(year="2017", label="Switch", s=0, value="157.2M", gold=True),
                dict(year="2025", label="Switch 2", s=0),
            ],
            break_after=3, s_reconnect=1,
            footer="Salvage the insight from the mistake", s_footer=1,
        ),
    ),

    # ================================================================ 7 · JOY AS STRATEGY
    chapter("ch_joy", "06", "Joy Is a Business Strategy", "Delight as a system of feedback", "playful",
            hud="JOY AS A BUSINESS STRATEGY", chapter_name="Joy as a business strategy"),
    dict(
        id="joy_delight",
        text=(
            "There is another reason Nintendo survives, and it is harder to place in a spreadsheet. "
            "Nintendo designs for delight. "
            "Not happiness as branding. "
            "Delight as a system of feedback: the sound of a coin, the pause before a chest opens, the tiny animation that rewards curiosity, "
            "the possibility that a piano might secretly be a character with teeth."
        ),
        visual=dict(
            type="flow", heading="Delight as a system", loop=True,
            nodes=[
                dict(text="Anticipation", s="system of feedback"), dict(text="Action", s="system of feedback"),
                dict(text="Feedback", s="system of feedback", hl=True), dict(text="Surprise", s="system of feedback"),
            ],
            footer="A coin's sound · a chest's pause · a piano with teeth", s_footer="system of feedback",
        ),
    ),
    dict(
        id="joy_value",
        text=(
            "These details have economic value. "
            "A game built around spectacle can become dated when better spectacle arrives. "
            "A game built around a satisfying jump, a readable rule, or the pleasure of discovery can remain playable for decades."
        ),
        visual=dict(
            type="versus",
            left=dict(title="Built on spectacle", lines=["Dazzles at launch", "Dated by better spectacle"], s=1),
            right=dict(title="Built on feel", lines=["A satisfying jump", "A readable rule", "The joy of discovery", "Playable for decades"], s=2),
            verdict="Details with economic value", s_verdict=2, winner="right",
        ),
    ),
    dict(
        id="joy_polish",
        text=(
            "Nintendo's best software is polished around the player's body and attention. "
            "Controls are tested until they disappear. "
            "Levels teach without stopping to announce the lesson. "
            "Failure is often funny enough to make another attempt feel inviting."
        ),
        visual=dict(
            type="list", heading="Polished around the player",
            items=[
                dict(text="Controls tested until they disappear", s=1),
                dict(text="Levels that teach without announcing the lesson", s=2),
                dict(text="Failure funny enough to try again", s=3),
            ],
        ),
    ),
    dict(
        id="joy_everyone",
        text=(
            "That accessibility expands the audience without necessarily flattening the design. "
            "A child can finish a lap in Mario Kart. "
            "An expert can spend years mastering its lines. "
            "A newcomer can wander through Hyrule. "
            "A speedrunner can bend its physics into a different game entirely."
        ),
        visual=dict(
            type="cards", heading="Wide audience, deep design", height=380,
            items=[
                dict(big="Child", label="Finishes a lap in Mario Kart", s=1),
                dict(big="Expert", label="Spends years mastering the lines", s=2),
                dict(big="Newcomer", label="Wanders through Hyrule", s=3),
                dict(big="Speedrunner", label="Bends the physics into a new game", s=4, hl=True),
            ],
        ),
    ),
    dict(
        id="joy_constraint",
        text=(
            "“Fun for everyone” is easy to dismiss as a slogan. "
            "At Nintendo, it is closer to an engineering constraint."
        ),
        visual=dict(type="statement", text="“Fun for everyone” sounds like a slogan.",
                    text2="At Nintendo, it is closer to an engineering constraint.", s_text=0, s_text2=1),
    ),

    # ================================================================ 8 · NOT MAGIC
    chapter("ch_notmagic", "07", "Nintendo Is Not Magic", "The uncomfortable truth", "neutral",
            hud="NINTENDO IS NOT MAGIC", chapter_name="Nintendo is not magic", bg="cool"),
    dict(
        id="notmagic_flaws", bg="cool",
        text=(
            "None of this makes Nintendo infallible—or universally benevolent. "
            "Its online services have often lagged behind competitors. "
            "Its approach to preservation can make older games difficult to access legally. "
            "Hardware experiments create casualties. "
            "Fans and creators have criticized its litigation and strict control of its work. "
            "And even beloved products can carry frustrating design flaws."
        ),
        visual=dict(
            type="list", heading="Not infallible — or universally benevolent",
            items=[
                dict(text="Online services that lag behind", s="online services"),
                dict(text="Older games hard to access legally", s="preservation"),
                dict(text="Hardware experiments with casualties", s="casualties"),
                dict(text="Criticized litigation and strict control", s="litigation"),
                dict(text="Design flaws in beloved products", s="design flaws"),
            ],
        ),
    ),
    dict(
        id="notmagic_volatility", bg="cool",
        text=(
            "Nintendo's strategy also produces volatility. "
            "When an unusual machine connects, it can expand the market. "
            "When it does not, there is no safe middle. "
            "The same independence that creates the Wii can create the Wii U."
        ),
        visual=dict(
            type="versus",
            left=dict(title="When it connects", lines=["Expands the market", "e.g. the Wii"], s=1),
            right=dict(title="When it doesn't", lines=["No safe middle", "e.g. the Wii U"], s=2),
            verdict="The same independence creates both", s_verdict=3, winner=None,
        ),
    ),
    dict(
        id="notmagic_industry", bg="cool",
        text=(
            "And the industry is changing. "
            "Development costs are rising. "
            "Mobile games compete for every idle minute. "
            "Younger players gather inside persistent platforms that behave less like individual games and more like social spaces."
        ),
        visual=dict(
            type="list", heading="A changing industry",
            items=[
                dict(text="Rising development costs", s=1),
                dict(text="Mobile games competing for every idle minute", s=2),
                dict(text="Persistent platforms that act like social spaces", s=3),
            ],
        ),
    ),
    dict(
        id="notmagic_nostalgia", bg="cool",
        text=(
            "Nintendo cannot survive on nostalgia alone. "
            "Nostalgia is powerful, but it is a diminishing resource if a new generation does not form memories of its own. "
            "The real test of each Nintendo platform is therefore not whether old players return. "
            "It is whether new players find an experience they will still care about twenty years from now."
        ),
        visual=dict(type="statement", text="Nostalgia is a diminishing resource.",
                    text2="The real test: will new players still care twenty years from now?", s_text=1, s_text2=3),
    ),

    # ================================================================ 9 · WHY COMPETITORS DISAPPEAR
    chapter("ch_competitors", "08", "Why Competitors Disappear", "Three advantages that reinforce one another", "neutral",
            hud="WHY COMPETITORS DISAPPEAR", chapter_name="Why competitors disappear"),
    dict(
        id="comp_decay",
        text=(
            "So why has Nintendo endured where competitors shrank or disappeared? "
            "Because most advantages in technology decay. "
            "The fastest processor becomes cheap. "
            "A manufacturing edge becomes standard. "
            "A distribution channel gets replaced. "
            "A hit game is copied."
        ),
        visual=dict(
            type="list", heading="Most advantages in technology decay", decay=True,
            items=[
                dict(text="The fastest processor → becomes cheap", s=2),
                dict(text="A manufacturing edge → becomes standard", s=3),
                dict(text="A distribution channel → gets replaced", s=4),
                dict(text="A hit game → is copied", s=5),
            ],
        ),
    ),
    dict(
        id="comp_rings", mood="warm",
        text=(
            "Nintendo built three advantages that reinforce one another. "
            "First, a design culture that searches for new forms of play. "
            "Second, control over the hardware and software needed to deliver them. "
            "Third, characters that make each new experiment feel familiar enough to try."
        ),
        visual=dict(
            type="rings", center="N",
            rings=[
                dict(title="Design culture", sub="searching for new forms of play", s=1),
                dict(title="Hardware + software", sub="control of the whole experience", s=2),
                dict(title="Characters", sub="familiar enough to try", s=3),
            ],
        ),
    ),
    dict(
        id="comp_remove",
        text=(
            "Remove any one of these and the system weakens. "
            "Strange hardware without great software becomes a gimmick. "
            "Great software without control of the platform becomes dependent on somebody else's rules. "
            "Famous characters without reinvention become museum pieces."
        ),
        visual=dict(
            type="chain", heading="Remove any one, and the system weakens",
            rows=[
                dict(a="Strange hardware, no great software", b="A gimmick", s=1),
                dict(a="Great software, no platform", b="Somebody else's rules", s=2),
                dict(a="Famous characters, no reinvention", b="Museum pieces", s=3),
            ],
        ),
    ),
    dict(
        id="comp_all",
        text=(
            "Nintendo has all three—and more than a century of institutional memory about what happens when a toy stops being fun."
        ),
        visual=dict(type="statement", text="All three.",
                    text2="Plus more than a century of memory about what happens when a toy stops being fun.", s_text=0, s_text2=0),
    ),

    # ================================================================ 10 · THE OLDEST LESSON
    chapter("ch_lesson", "09", "The Oldest Lesson", "From paper and ink", "close",
            hud="THE OLDEST LESSON", chapter_name="The oldest lesson"),
    dict(
        id="lesson_cards",
        text=(
            "Nintendo began with paper, ink, and a deck of cards. "
            "That origin matters—not because playing cards predicted video games, but because they taught the company its oldest lesson."
        ),
        visual=dict(type="cardmorph", s_shift=1, left="1889 · paper, ink, cards", right="Today · screens and controllers"),
    ),
    dict(
        id="lesson_object",
        text=(
            "The object is not the entertainment. "
            "The entertainment is what happens between people, rules, imagination, and surprise."
        ),
        visual=dict(type="statement", text="The object is not the entertainment.",
                    text2="The entertainment is what happens between people, rules, imagination, and surprise.", s_text=0, s_text2=1),
    ),
    dict(
        id="lesson_change",
        text=(
            "Consoles change. Screens change. Business models change. "
            "The industry repeatedly mistakes those changes for the point. "
            "Nintendo's history suggests something simpler."
        ),
        visual=dict(
            type="list", heading="What changes", decay=True,
            items=[dict(text="Consoles", s=0), dict(text="Screens", s=1), dict(text="Business models", s=2)],
            footer="…mistaken, again and again, for the point", s_footer=3,
        ),
    ),
    dict(
        id="lesson_moment",
        text=(
            "Technology matters most when it disappears into a moment: "
            "a perfectly timed jump, a discovery you were not supposed to find, a race lost by one blue shell, "
            "a controller handed to someone who was only watching."
        ),
        visual=dict(
            type="list", heading="Technology that disappears into a moment",
            items=[
                dict(text="A perfectly timed jump", s=0),
                dict(text="A discovery you were not supposed to find", s=0),
                dict(text="A race lost by one blue shell", s=0),
                dict(text="A controller handed to someone who was only watching", s=0),
            ],
        ),
    ),
    dict(
        id="lesson_why",
        text=(
            "That is why Nintendo can look outdated and arrive early. "
            "Why it can fail dramatically and return stronger. "
            "Why a company founded in 1889 can still make the future feel playful."
        ),
        visual=dict(
            type="list", heading="That is why",
            items=[
                dict(text="It can look outdated — and arrive early", s=0),
                dict(text="It can fail dramatically — and return stronger", s=1),
                dict(text="A company from 1889 still makes the future feel playful", s=2),
            ],
        ),
    ),
    dict(
        id="lesson_final",
        text=(
            "Nintendo does not endure because it always knows what comes next. "
            "It endures because, when the industry forgets why people play, Nintendo has spent 137 years remembering."
        ),
        visual=dict(type="statement", text="Not because it always knows what comes next.",
                    text2="Because when the industry forgets why people play, Nintendo has spent 137 years remembering.",
                    s_text=0, s_text2=1),
    ),
    dict(
        id="end_card", text="", hold=6.0, bg="title",
        visual=dict(type="title", title="The technology changes.", sub="The play remains.", s_sub=None),
        sfx=[("end", "click")],
    ),
]

DESCRIPTION = """
Nintendo began in 1889 making playing cards. It survived the console crash, the rise of Sony and Microsoft, the failure of the Wii U, and more than a century of changing technology. This film asks how—and argues that Nintendo's real advantage is not hardware power, but a design system built around new forms of play, carefully renewed characters, and the ability to learn from failure.
"""

DESCRIPTION_SOURCES = """
Sources (Nintendo corporate history, sales data, annual reports, and earnings materials):
• Company history — https://www.nintendo.co.jp/corporate/en/history/
• Dedicated video game sales units — https://www.nintendo.co.jp/ir/en/finance/hard_soft/number.html
• Earnings release, six months ended Sept 30, 2026 (Switch 157.20M hardware / 1,593.87M software life-to-date) — https://www.nintendo.co.jp/ir/pdf/2026/261105_3e.pdf
• Earnings release, fiscal year ended March 31, 2026 (net sales ¥2,313.0B; Switch 2 19.86M units) — https://www.nintendo.co.jp/ir/pdf/2026/260508e.pdf
• FY2026 results briefing Q&A — https://www.nintendo.co.jp/ir/pdf/2026/260511e.pdf
• Annual reports & historical data — https://www.nintendo.co.jp/ir/en/library/annual/
Sales figures are Nintendo-reported sell-in unless noted.
"""
