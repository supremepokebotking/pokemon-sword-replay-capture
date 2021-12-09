import re

pokemon_items_regex = '(None|Potion|Antidote|Burn Heal|Ice Heal|Awakening|Paralyze Heal|Full Restore|Max Potion|Hyper Potion|Super Potion|Full Heal|Revive|Max Revive|Fresh Water|Soda Pop|Lemonade|Moomoo Milk|Energy Powder|Energy Root|Heal Powder|Revival Herb|Ether|Max Ether|Elixir|Max Elixir|Lava Cookie|Berry Juice|Sacred Ash|HP Up|Protein|Iron|Carbos|Calcium|Rare Candy|PP Up|Zinc|PP Max|Old Gateau|Guard Spec.|Dire Hit|X Attack|X Defense|X Speed|X Accuracy|X Sp. Atk|X Sp. Def|Poké Doll|Fluffy Tail|Blue Flute|Yellow Flute|Red Flute|Black Flute|White Flute|Shoal Salt|Shoal Shell|Red Shard|Blue Shard|Yellow Shard|Green Shard|Super Repel|Max Repel|Escape Rope|Repel|Sun Stone|Moon Stone|Fire Stone|Thunder Stone|Water Stone|Leaf Stone|Tiny Mushroom|Big Mushroom|Pearl|Big Pearl|Stardust|Star Piece|Nugget|Heart Scale|Honey|Growth Mulch|Damp Mulch|Stable Mulch|Gooey Mulch|Root Fossil|Claw Fossil|Helix Fossil|Dome Fossil|Old Amber|Armor Fossil|Skull Fossil|Rare Bone|Shiny Stone|Dusk Stone|Dawn Stone|Oval Stone|Odd Keystone|Griseous Orb|Autograph|Douse Drive|Shock Drive|Burn Drive|Chill Drive|Pokémon Box Link|Medicine Pocket|TM Case|Candy Jar|Power-Up Pocket|Clothing Trunk|Catching Pocket|Battle Pocket|Sweet Heart|Adamant Orb|Lustrous Orb|Cheri Berry|Chesto Berry|Pecha Berry|Rawst Berry|Aspear Berry|Leppa Berry|Oran Berry|Persim Berry|Lum Berry|Sitrus Berry|Figy Berry|Wiki Berry|Mago Berry|Aguav Berry|Iapapa Berry|Razz Berry|Bluk Berry|Nanab Berry|Wepear Berry|Pinap Berry|Pomeg Berry|Kelpsy Berry|Qualot Berry|Hondew Berry|Grepa Berry|Tamato Berry|Cornn Berry|Magost Berry|Rabuta Berry|Nomel Berry|Spelon Berry|Pamtre Berry|Watmel Berry|Durin Berry|Belue Berry|Occa Berry|Passho Berry|Wacan Berry|Rindo Berry|Yache Berry|Chople Berry|Kebia Berry|Shuca Berry|Coba Berry|Payapa Berry|Tanga Berry|Charti Berry|Kasib Berry|Haban Berry|Colbur Berry|Babiri Berry|Chilan Berry|Liechi Berry|Ganlon Berry|Salac Berry|Petaya Berry|Apicot Berry|Lansat Berry|Starf Berry|Enigma Berry|Micle Berry|Custap Berry|Jaboca Berry|Rowap Berry|Bright Powder|White Herb|Macho Brace|Exp. Share|Quick Claw|Soothe Bell|Mental Herb|Choice Band|King\'s Rock|Silver Powder|Amulet Coin|Cleanse Tag|Soul Dew|Deep Sea Tooth|Deep Sea Scale|Smoke Ball|Everstone|Focus Band|Lucky Egg|Scope Lens|Metal Coat|Leftovers|Dragon Scale|Light Ball|Soft Sand|Hard Stone|Miracle Seed|Black Glasses|Black Belt|Magnet|Mystic Water|Sharp Beak|Poison Barb|Never-Melt Ice|Spell Tag|Twisted Spoon|Charcoal|Dragon Fang|Silk Scarf|Upgrade|Shell Bell|Sea Incense|Lax Incense|Lucky Punch|Metal Powder|Thick Club|Leek|Red Scarf|Blue Scarf|Pink Scarf|Green Scarf|Yellow Scarf|Wide Lens|Muscle Band|Wise Glasses|Expert Belt|Light Clay|Life Orb|Power Herb|Toxic Orb|Flame Orb|Quick Powder|Focus Sash|Zoom Lens|Metronome|Iron Ball|Lagging Tail|Destiny Knot|Black Sludge|Icy Rock|Smooth Rock|Heat Rock|Damp Rock|Grip Claw|Choice Scarf|Sticky Barb|Power Bracer|Power Belt|Power Lens|Power Band|Power Anklet|Power Weight|Shed Shell|Big Root|Choice Specs|Flame Plate|Splash Plate|Zap Plate|Meadow Plate|Icicle Plate|Fist Plate|Toxic Plate|Earth Plate|Sky Plate|Mind Plate|Insect Plate|Stone Plate|Spooky Plate|Draco Plate|Dread Plate|Iron Plate|Odd Incense|Rock Incense|Full Incense|Wave Incense|Rose Incense|Luck Incense|Pure Incense|Protector|Electirizer|Magmarizer|Dubious Disc|Reaper Cloth|Razor Claw|Razor Fang|Rotom Bike|Large Leek|Fancy Apple|Brittle Bones|Pungent Root|Rusted Sword|Rusted Shield|Love Sweet|Berry Sweet|Clover Sweet|Flower Sweet|Star Sweet|Ribbon Sweet|Sweet Apple|Tart Apple|Throat Spray|Eject Pack|Heavy-Duty Boots|Blunder Policy|Room Service|Utility Umbrella|Xtransceiver|Medal Box|DNA Splicers|Permit|Oval Charm|Shiny Charm|Plasma Card|Grubby Hanky|Colress Machine|Reveal Glass|Weakness Policy|Assault Vest|Holo Caster|Prof\'s Letter|Roller Skates|Pixie Plate|Ability Capsule|Whipped Dream|Sachet|Luminous Moss|Snowball|Safety Goggles|Rich Mulch|Surprise Mulch)'
pokemon_names_regex = '(Bulbasaur|Ivysaur|Venusaur|Charmander|Charmeleon|Charizard|Squirtle|Wartortle|Blastoise|Caterpie|Metapod|Butterfree|Weedle|Kakuna|Beedrill|Pidgey|Pidgeotto|Pidgeot|Rattata|Raticate|Spearow|Fearow|Ekans|Arbok|Pikachu|Raichu|Sandshrew|Sandslash|Nidoran♀|Nidorina|Nidoqueen|Nidoran♂|Nidorino|Nidoking|Clefairy|Clefable|Vulpix|Ninetales|Jigglypuff|Wigglytuff|Zubat|Golbat|Oddish|Gloom|Vileplume|Paras|Parasect|Venonat|Venomoth|Diglett|Dugtrio|Meowth|Persian|Psyduck|Golduck|Mankey|Primeape|Growlithe|Arcanine|Poliwag|Poliwhirl|Poliwrath|Abra|Kadabra|Alakazam|Machop|Machoke|Machamp|Bellsprout|Weepinbell|Victreebel|Tentacool|Tentacruel|Geodude|Graveler|Golem|Ponyta|Rapidash|Slowpoke|Slowbro|Magnemite|Magneton|Farfetch\'d|Doduo|Dodrio|Seel|Dewgong|Grimer|Muk|Shellder|Cloyster|Gastly|Haunter|Gengar|Onix|Drowzee|Hypno|Krabby|Kingler|Voltorb|Electrode|Exeggcute|Exeggutor|Cubone|Marowak|Hitmonlee|Hitmonchan|Lickitung|Koffing|Weezing|Rhyhorn|Rhydon|Chansey|Tangela|Kangaskhan|Horsea|Seadra|Goldeen|Seaking|Staryu|Starmie|Mr. Mime|Scyther|Jynx|Electabuzz|Magmar|Pinsir|Tauros|Magikarp|Gyarados|Lapras|Ditto|Eevee|Vaporeon|Jolteon|Flareon|Porygon|Omanyte|Omastar|Kabuto|Kabutops|Aerodactyl|Snorlax|Articuno|Zapdos|Moltres|Dratini|Dragonair|Dragonite|Mewtwo|Mew|Chikorita|Bayleef|Meganium|Cyndaquil|Quilava|Typhlosion|Totodile|Croconaw|Feraligatr|Sentret|Furret|Hoothoot|Noctowl|Ledyba|Ledian|Spinarak|Ariados|Crobat|Chinchou|Lanturn|Pichu|Cleffa|Igglybuff|Togepi|Togetic|Natu|Xatu|Mareep|Flaaffy|Ampharos|Bellossom|Marill|Azumarill|Sudowoodo|Politoed|Hoppip|Skiploom|Jumpluff|Aipom|Sunkern|Sunflora|Yanma|Wooper|Quagsire|Espeon|Umbreon|Murkrow|Slowking|Misdreavus|Unown|Wobbuffet|Girafarig|Pineco|Forretress|Dunsparce|Gligar|Steelix|Snubbull|Granbull|Qwilfish|Scizor|Shuckle|Heracross|Sneasel|Teddiursa|Ursaring|Slugma|Magcargo|Swinub|Piloswine|Corsola|Remoraid|Octillery|Delibird|Mantine|Skarmory|Houndour|Houndoom|Kingdra|Phanpy|Donphan|Porygon2|Stantler|Smeargle|Tyrogue|Hitmontop|Smoochum|Elekid|Magby|Miltank|Blissey|Raikou|Entei|Suicune|Larvitar|Pupitar|Tyranitar|Lugia|Ho-Oh|Celebi|Treecko|Grovyle|Sceptile|Torchic|Combusken|Blaziken|Mudkip|Marshtomp|Swampert|Poochyena|Mightyena|Zigzagoon|Linoone|Wurmple|Silcoon|Beautifly|Cascoon|Dustox|Lotad|Lombre|Ludicolo|Seedot|Nuzleaf|Shiftry|Taillow|Swellow|Wingull|Pelipper|Ralts|Kirlia|Gardevoir|Surskit|Masquerain|Shroomish|Breloom|Slakoth|Vigoroth|Slaking|Nincada|Ninjask|Shedinja|Whismur|Loudred|Exploud|Makuhita|Hariyama|Azurill|Nosepass|Skitty|Delcatty|Sableye|Mawile|Aron|Lairon|Aggron|Meditite|Medicham|Electrike|Manectric|Plusle|Minun|Volbeat|Illumise|Roselia|Gulpin|Swalot|Carvanha|Sharpedo|Wailmer|Wailord|Numel|Camerupt|Torkoal|Spoink|Grumpig|Spinda|Trapinch|Vibrava|Flygon|Cacnea|Cacturne|Swablu|Altaria|Zangoose|Seviper|Lunatone|Solrock|Barboach|Whiscash|Corphish|Crawdaunt|Baltoy|Claydol|Lileep|Cradily|Anorith|Armaldo|Feebas|Milotic|Castform|Kecleon|Shuppet|Banette|Duskull|Dusclops|Tropius|Chimecho|Absol|Wynaut|Snorunt|Glalie|Spheal|Sealeo|Walrein|Clamperl|Huntail|Gorebyss|Relicanth|Luvdisc|Bagon|Shelgon|Salamence|Beldum|Metang|Metagross|Regirock|Regice|Registeel|Latias|Latios|Kyogre|Groudon|Rayquaza|Jirachi|Deoxys|Turtwig|Grotle|Torterra|Chimchar|Monferno|Infernape|Piplup|Prinplup|Empoleon|Starly|Staravia|Staraptor|Bidoof|Bibarel|Kricketot|Kricketune|Shinx|Luxio|Luxray|Budew|Roserade|Cranidos|Rampardos|Shieldon|Bastiodon|Burmy|Wormadam|Mothim|Combee|Vespiquen|Pachirisu|Buizel|Floatzel|Cherubi|Cherrim|Shellos|Gastrodon|Ambipom|Drifloon|Drifblim|Buneary|Lopunny|Mismagius|Honchkrow|Glameow|Purugly|Chingling|Stunky|Skuntank|Bronzor|Bronzong|Bonsly|Mime Jr.|Happiny|Chatot|Spiritomb|Gible|Gabite|Garchomp|Munchlax|Riolu|Lucario|Hippopotas|Hippowdon|Skorupi|Drapion|Croagunk|Toxicroak|Carnivine|Finneon|Lumineon|Mantyke|Snover|Abomasnow|Weavile|Magnezone|Lickilicky|Rhyperior|Tangrowth|Electivire|Magmortar|Togekiss|Yanmega|Leafeon|Glaceon|Gliscor|Mamoswine|Porygon-Z|Gallade|Probopass|Dusknoir|Froslass|Rotom|Uxie|Mesprit|Azelf|Dialga|Palkia|Heatran|Regigigas|Giratina|Cresselia|Phione|Manaphy|Darkrai|Shaymin|Arceus|Victini|Snivy|Servine|Serperior|Tepig|Pignite|Emboar|Oshawott|Dewott|Samurott|Patrat|Watchog|Lillipup|Herdier|Stoutland|Purrloin|Liepard|Pansage|Simisage|Pansear|Simisear|Panpour|Simipour|Munna|Musharna|Pidove|Tranquill|Unfezant|Blitzle|Zebstrika|Roggenrola|Boldore|Gigalith|Woobat|Swoobat|Drilbur|Excadrill|Audino|Timburr|Gurdurr|Conkeldurr|Tympole|Palpitoad|Seismitoad|Throh|Sawk|Sewaddle|Swadloon|Leavanny|Venipede|Whirlipede|Scolipede|Cottonee|Whimsicott|Petilil|Lilligant|Basculin|Sandile|Krokorok|Krookodile|Darumaka|Darmanitan|Maractus|Dwebble|Crustle|Scraggy|Scrafty|Sigilyph|Yamask|Cofagrigus|Tirtouga|Carracosta|Archen|Archeops|Trubbish|Garbodor|Zorua|Zoroark|Minccino|Cinccino|Gothita|Gothorita|Gothitelle|Solosis|Duosion|Reuniclus|Ducklett|Swanna|Vanillite|Vanillish|Vanilluxe|Deerling|Sawsbuck|Emolga|Karrablast|Escavalier|Foongus|Amoonguss|Frillish|Jellicent|Alomomola|Joltik|Galvantula|Ferroseed|Ferrothorn|Klink|Klang|Klinklang|Tynamo|Eelektrik|Eelektross|Elgyem|Beheeyem|Litwick|Lampent|Chandelure|Axew|Fraxure|Haxorus|Cubchoo|Beartic|Cryogonal|Shelmet|Accelgor|Stunfisk|Mienfoo|Mienshao|Druddigon|Golett|Golurk|Pawniard|Bisharp|Bouffalant|Rufflet|Braviary|Vullaby|Mandibuzz|Heatmor|Durant|Deino|Zweilous|Hydreigon|Larvesta|Volcarona|Cobalion|Terrakion|Virizion|Tornadus|Thundurus|Reshiram|Zekrom|Landorus|Kyurem|Keldeo|Meloetta|Genesect|Chespin|Quilladin|Chesnaught|Fennekin|Braixen|Delphox|Froakie|Frogadier|Greninja|Bunnelby|Diggersby|Fletchling|Fletchinder|Talonflame|Scatterbug|Spewpa|Vivillon|Litleo|Pyroar|Flabébé|Floette|Florges|Skiddo|Gogoat|Pancham|Pangoro|Furfrou|Espurr|Meowstic|Honedge|Doublade|Aegislash|Spritzee|Aromatisse|Swirlix|Slurpuff|Inkay|Malamar|Binacle|Barbaracle|Skrelp|Dragalge|Clauncher|Clawitzer|Helioptile|Heliolisk|Tyrunt|Tyrantrum|Amaura|Aurorus|Sylveon|Hawlucha|Dedenne|Carbink|Goomy|Sliggoo|Goodra|Klefki|Phantump|Trevenant|Pumpkaboo|Gourgeist|Bergmite|Avalugg|Noibat|Noivern|Xerneas|Yveltal|Zygarde|Diancie|Hoopa|Volcanion|Rowlet|Dartrix|Decidueye|Litten|Torracat|Incineroar|Popplio|Brionne|Primarina|Pikipek|Trumbeak|Toucannon|Yungoos|Gumshoos|Grubbin|Charjabug|Vikavolt|Crabrawler|Crabominable|Oricorio|Cutiefly|Ribombee|Rockruff|Lycanroc|Wishiwashi|Mareanie|Toxapex|Mudbray|Mudsdale|Dewpider|Araquanid|Fomantis|Lurantis|Morelull|Shiinotic|Salandit|Salazzle|Stufful|Bewear|Bounsweet|Steenee|Tsareena|Comfey|Oranguru|Passimian|Wimpod|Golisopod|Sandygast|Palossand|Pyukumuku|Type: Null|Silvally|Minior|Komala|Turtonator|Togedemaru|Mimikyu|Bruxish|Drampa|Dhelmise|Jangmo-o|Hakamo-o|Kommo-o|Tapu Koko|Tapu Lele|Tapu Bulu|Tapu Fini|Cosmog|Cosmoem|Solgaleo|Lunala|Nihilego|Buzzwole|Pheromosa|Xurkitree|Celesteela|Kartana|Guzzlord|Necrozma|Magearna|Marshadow|Poipole|Naganadel|Stakataka|Blacephalon|Zeraora|Meltan|Melmetal|Grookey|Thwackey|Rillaboom|Scorbunny|Raboot|Cinderace|Sobble|Drizzile|Inteleon|Skwovet|Greedent|Rookidee|Corvisquire|Corviknight|Blipbug|Dottler|Orbeetle|Nickit|Thievul|Gossifleur|Eldegoss|Wooloo|Dubwool|Chewtle|Drednaw|Yamper|Boltund|Rolycoly|Carkol|Coalossal|Applin|Flapple|Appletun|Silicobra|Sandaconda|Cramorant|Arrokuda|Barraskewda|Toxel|Toxtricity|Sizzlipede|Centiskorch|Clobbopus|Grapploct|Sinistea|Polteageist|Hatenna|Hattrem|Hatterene|Impidimp|Morgrem|Grimmsnarl|Obstagoon|Perrserker|Cursola|Sirfetch\'d|Mr. Rime|Runerigus|Milcery|Alcremie|Falinks|Pincurchin|Snom|Frosmoth|Stonjourner|Eiscue|Indeedee|Morpeko|Cufant|Copperajah|Dracozolt|Arctozolt|Dracovish|Arctovish|Duraludon|Dreepy|Drakloak|Dragapult|Zacian|Zamazenta|Eternatus)'
#pokemon_names_regex = '(Bulbasaur|Ivysaur)'
pokemon_attacks_regex = '(Pound|Karate Chop|Double Slap|Comet Punch|Mega Punch|Pay Day|Fire Punch|Ice Punch|Thunder Punch|Scratch|Vise Grip|Guillotine|Razor Wind|Swords Dance|Cut|Gust|Wing Attack|Whirlwind|Fly|Bind|Slam|Vine Whip|Stomp|Double Kick|Mega Kick|Jump Kick|Rolling Kick|Sand Attack|Headbutt|Horn Attack|Fury Attack|Horn Drill|Tackle|Body Slam|Wrap|Take Down|Thrash|Double-Edge|Tail Whip|Poison Sting|Twineedle|Pin Missile|Leer|Bite|Growl|Roar|Sing|Supersonic|Sonic Boom|Disable|Acid|Ember|Flamethrower|Mist|Water Gun|Hydro Pump|Surf|Ice Beam|Blizzard|Psybeam|Bubble Beam|Aurora Beam|Hyper Beam|Peck|Drill Peck|Submission|Low Kick|Counter|Seismic Toss|Strength|Absorb|Mega Drain|Leech Seed|Growth|Razor Leaf|Solar Beam|Poison Powder|Stun Spore|Sleep Powder|Petal Dance|String Shot|Dragon Rage|Fire Spin|Thunder Shock|Thunderbolt|Thunder Wave|Thunder|Rock Throw|Earthquake|Fissure|Dig|Toxic|Confusion|Psychic|Hypnosis|Meditate|Agility|Quick Attack|Rage|Teleport|Night Shade|Mimic|Screech|Double Team|Recover|Harden|Minimize|Smokescreen|Confuse Ray|Withdraw|Defense Curl|Barrier|Light Screen|Haze|Reflect|Focus Energy|Bide|Metronome|Mirror Move|Self-Destruct|Egg Bomb|Lick|Smog|Sludge|Bone Club|Fire Blast|Waterfall|Clamp|Swift|Skull Bash|Spike Cannon|Constrict|Amnesia|Kinesis|Soft-Boiled|High Jump Kick|Glare|Dream Eater|Poison Gas|Barrage|Leech Life|Lovely Kiss|Sky Attack|Transform|Bubble|Dizzy Punch|Spore|Flash|Psywave|Splash|Acid Armor|Crabhammer|Explosion|Fury Swipes|Bonemerang|Rest|Rock Slide|Hyper Fang|Sharpen|Conversion|Tri Attack|Super Fang|Slash|Substitute|Struggle|Sketch|Triple Kick|Thief|Spider Web|Mind Reader|Nightmare|Flame Wheel|Snore|Curse|Flail|Conversion 2|Aeroblast|Cotton Spore|Reversal|Spite|Powder Snow|Protect|Mach Punch|Scary Face|Feint Attack|Sweet Kiss|Belly Drum|Sludge Bomb|Mud-Slap|Octazooka|Spikes|Zap Cannon|Foresight|Destiny Bond|Perish Song|Icy Wind|Detect|Bone Rush|Lock-On|Outrage|Sandstorm|Giga Drain|Endure|Charm|Rollout|False Swipe|Swagger|Milk Drink|Spark|Fury Cutter|Steel Wing|Mean Look|Attract|Sleep Talk|Heal Bell|Return|Present|Frustration|Safeguard|Pain Split|Sacred Fire|Magnitude|Dynamic Punch|Megahorn|Dragon Breath|Baton Pass|Encore|Pursuit|Rapid Spin|Sweet Scent|Iron Tail|Metal Claw|Vital Throw|Morning Sun|Synthesis|Moonlight|Hidden Power|Cross Chop|Twister|Rain Dance|Sunny Day|Crunch|Mirror Coat|Psych Up|Extreme Speed|Ancient Power|Shadow Ball|Future Sight|Rock Smash|Whirlpool|Beat Up|Fake Out|Uproar|Stockpile|Spit Up|Swallow|Heat Wave|Hail|Torment|Flatter|Will-O-Wisp|Memento|Facade|Focus Punch|Smelling Salts|Follow Me|Nature Power|Charge|Taunt|Helping Hand|Trick|Role Play|Wish|Assist|Ingrain|Superpower|Magic Coat|Recycle|Revenge|Brick Break|Yawn|Knock Off|Endeavor|Eruption|Skill Swap|Imprison|Refresh|Grudge|Snatch|Secret Power|Dive|Arm Thrust|Camouflage|Tail Glow|Luster Purge|Mist Ball|Feather Dance|Teeter Dance|Blaze Kick|Mud Sport|Ice Ball|Needle Arm|Slack Off|Hyper Voice|Poison Fang|Crush Claw|Blast Burn|Hydro Cannon|Meteor Mash|Astonish|Weather Ball|Aromatherapy|Fake Tears|Air Cutter|Overheat|Odor Sleuth|Rock Tomb|Silver Wind|Metal Sound|Grass Whistle|Tickle|Cosmic Power|Water Spout|Signal Beam|Shadow Punch|Extrasensory|Sky Uppercut|Sand Tomb|Sheer Cold|Muddy Water|Bullet Seed|Aerial Ace|Icicle Spear|Iron Defense|Block|Howl|Dragon Claw|Frenzy Plant|Bulk Up|Bounce|Mud Shot|Poison Tail|Covet|Volt Tackle|Magical Leaf|Water Sport|Calm Mind|Leaf Blade|Dragon Dance|Rock Blast|Shock Wave|Water Pulse|Doom Desire|Psycho Boost|Roost|Gravity|Miracle Eye|Wake-Up Slap|Hammer Arm|Gyro Ball|Healing Wish|Brine|Natural Gift|Feint|Pluck|Tailwind|Acupressure|Metal Burst|U-turn|Close Combat|Payback|Assurance|Embargo|Fling|Psycho Shift|Trump Card|Heal Block|Wring Out|Power Trick|Gastro Acid|Lucky Chant|Me First|Copycat|Power Swap|Guard Swap|Punishment|Last Resort|Worry Seed|Sucker Punch|Toxic Spikes|Heart Swap|Aqua Ring|Magnet Rise|Flare Blitz|Force Palm|Aura Sphere|Rock Polish|Poison Jab|Dark Pulse|Night Slash|Aqua Tail|Seed Bomb|Air Slash|X-Scissor|Bug Buzz|Dragon Pulse|Dragon Rush|Power Gem|Drain Punch|Vacuum Wave|Focus Blast|Energy Ball|Brave Bird|Earth Power|Switcheroo|Giga Impact|Nasty Plot|Bullet Punch|Avalanche|Ice Shard|Shadow Claw|Thunder Fang|Ice Fang|Fire Fang|Shadow Sneak|Mud Bomb|Psycho Cut|Zen Headbutt|Mirror Shot|Flash Cannon|Rock Climb|Defog|Trick Room|Draco Meteor|Discharge|Lava Plume|Leaf Storm|Power Whip|Rock Wrecker|Cross Poison|Gunk Shot|Iron Head|Magnet Bomb|Stone Edge|Captivate|Stealth Rock|Grass Knot|Chatter|Judgment|Bug Bite|Charge Beam|Wood Hammer|Aqua Jet|Attack Order|Defend Order|Heal Order|Head Smash|Double Hit|Roar of Time|Spacial Rend|Lunar Dance|Crush Grip|Magma Storm|Dark Void|Seed Flare|Ominous Wind|Shadow Force|Hone Claws|Wide Guard|Guard Split|Power Split|Wonder Room|Psyshock|Venoshock|Autotomize|Rage Powder|Telekinesis|Magic Room|Smack Down|Storm Throw|Flame Burst|Sludge Wave|Quiver Dance|Heavy Slam|Synchronoise|Electro Ball|Soak|Flame Charge|Coil|Low Sweep|Acid Spray|Foul Play|Simple Beam|Entrainment|After You|Round|Echoed Voice|Chip Away|Clear Smog|Stored Power|Quick Guard|Ally Switch|Scald|Shell Smash|Heal Pulse|Hex|Sky Drop|Shift Gear|Circle Throw|Incinerate|Quash|Acrobatics|Reflect Type|Retaliate|Final Gambit|Bestow|Inferno|Water Pledge|Fire Pledge|Grass Pledge|Volt Switch|Struggle Bug|Bulldoze|Frost Breath|Dragon Tail|Work Up|Electroweb|Wild Charge|Drill Run|Dual Chop|Heart Stamp|Horn Leech|Sacred Sword|Razor Shell|Heat Crash|Leaf Tornado|Steamroller|Cotton Guard|Night Daze|Psystrike|Tail Slap|Hurricane|Head Charge|Gear Grind|Searing Shot|Techno Blast|Relic Song|Secret Sword|Glaciate|Bolt Strike|Blue Flare|Fiery Dance|Freeze Shock|Ice Burn|Snarl|Icicle Crash|V-create|Fusion Flare|Fusion Bolt|Flying Press|Mat Block|Belch|Rototiller|Sticky Web|Fell Stinger|Phantom Force|Trick-or-Treat|Noble Roar|Ion Deluge|Parabolic Charge|Forest\'s Curse|Petal Blizzard|Freeze-Dry|Disarming Voice|Parting Shot|Topsy-Turvy|Draining Kiss|Crafty Shield|Flower Shield|Grassy Terrain|Misty Terrain|Electrify|Play Rough|Fairy Wind|Moonblast|Boomburst|Fairy Lock|King\'s Shield|Play Nice|Confide|Diamond Storm|Steam Eruption|Hyperspace Hole|Water Shuriken|Mystical Fire|Spiky Shield|Aromatic Mist|Eerie Impulse|Venom Drench|Powder|Geomancy|Magnetic Flux|Happy Hour|Electric Terrain|Dazzling Gleam|Celebrate|Hold Hands|Baby-Doll Eyes|Nuzzle|Hold Back|Infestation|Power-Up Punch|Oblivion Wing|Thousand Arrows|Thousand Waves|Land\'s Wrath|Light of Ruin|Origin Pulse|Precipice Blades|Dragon Ascent|Hyperspace Fury|Shore Up|First Impression|Baneful Bunker|Spirit Shackle|Darkest Lariat|Sparkling Aria|Ice Hammer|Floral Healing|High Horsepower|Strength Sap|Solar Blade|Leafage|Spotlight|Toxic Thread|Laser Focus|Gear Up|Throat Chop|Pollen Puff|Anchor Shot|Psychic Terrain|Lunge|Fire Lash|Power Trip|Burn Up|Speed Swap|Smart Strike|Purify|Revelation Dance|Core Enforcer|Trop Kick|Instruct|Beak Blast|Clanging Scales|Dragon Hammer|Brutal Swing|Aurora Veil|Shell Trap|Fleur Cannon|Psychic Fangs|Stomping Tantrum|Shadow Bone|Accelerock|Liquidation|Prismatic Laser|Spectral Thief|Sunsteel Strike|Moongeist Beam|Tearful Look|Zing Zap|Nature\'s Madness|Multi-Attack|Mind Blown|Plasma Fists|Photon Geyser|Zippy Zap|Splishy Splash|Floaty Fall|Pika Papow|Bouncy Bubble|Buzzy Buzz|Sizzly Slide|Glitzy Glow|Baddy Bad|Sappy Seed|Freezy Frost|Sparkly Swirl|Veevee Volley|Double Iron Bash|Max Guard|Dynamax Cannon|Snipe Shot|Jaw Lock|Stuff Cheeks|No Retreat|Tar Shot|Magic Powder|Dragon Darts|Teatime|Octolock|Bolt Beak|Fishious Rend|Court Change|Max Flare|Max Flutterby|Max Lightning|Max Strike|Max Knuckle|Max Phantasm|Max Hailstorm|Max Ooze|Max Geyser|Max Airstream|Max Starfall|Max Wyrmwind|Max Mindstorm|Max Rockfall|Max Quake|Max Darkness|Max Overgrowth|Max Steelspike|Clangorous Soul|Body Press|Decorate|Drum Beating|Snap Trap|Pyro Ball|Behemoth Blade|Behemoth Bash|Aura Wheel|Breaking Swipe|Branch Poke|Overdrive|Apple Acid|Grav Apple|Spirit Break|Strange Steam|Life Dew|Obstruct|False Surrender|Meteor Assault|Eternabeam|Steel Beam|G-Max Wildfire|G-Max Befuddle|G-Max Volt Crash|G-Max Gold Rush|G-Max Chi Strike|G-Max Terror|G-Max Resonance|G-Max Cuddle|G-Max Replenish|G-Max Malodor|G-Max Stonesurge|G-Max Wind Rage|G-Max Stun Shock|G-Max Finale|G-Max Depletion|G-Max Gravitas|G-Max Volcalith|G-Max Sandblast|G-Max Snooze|G-Max Tartness|G-Max Sweetness|G-Max Smite|G-Max Steelsurge|G-Max Meltdown|G-Max Foam Burst|G-Max Centiferno)'
pokemon_ability_regex = '(Stench|Drizzle|Speed Boost|Battle Armor|Sturdy|Damp|Limber|Sand Veil|Static|Volt Absorb|Water Absorb|Oblivious|Cloud Nine|Compound Eyes|Insomnia|Color Change|Immunity|Flash Fire|Shield Dust|Own Tempo|Suction Cups|Intimidate|Shadow Tag|Rough Skin|Wonder Guard|Levitate|Effect Spore|Synchronize|Clear Body|Natural Cure|Lightning Rod|Serene Grace|Swift Swim|Chlorophyll|Illuminate|Trace|Huge Power|Poison Point|Inner Focus|Magma Armor|Water Veil|Magnet Pull|Soundproof|Rain Dish|Sand Stream|Pressure|Thick Fat|Early Bird|Flame Body|Run Away|Keen Eye|Hyper Cutter|Pickup|Truant|Hustle|Cute Charm|Plus|Minus|Forecast|Sticky Hold|Shed Skin|Guts|Marvel Scale|Liquid Ooze|Overgrow|Blaze|Torrent|Swarm|Rock Head|Drought|Arena Trap|Vital Spirit|White Smoke|Pure Power|Shell Armor|Air Lock|Tangled Feet|Motor Drive|Rivalry|Steadfast|Snow Cloak|Gluttony|Anger Point|Unburden|Heatproof|Simple|Dry Skin|Download|Iron Fist|Poison Heal|Adaptability|Skill Link|Hydration|Solar Power|Quick Feet|Normalize|Sniper|Magic Guard|No Guard|Stall|Technician|Leaf Guard|Klutz|Mold Breaker|Super Luck|Aftermath|Anticipation|Forewarn|Unaware|Tinted Lens|Filter|Slow Start|Scrappy|Storm Drain|Ice Body|Solid Rock|Snow Warning|Honey Gather|Frisk|Reckless|Multitype|Flower Gift|Bad Dreams|Pickpocket|Sheer Force|Contrary|Unnerve|Defiant|Defeatist|Cursed Body|Healer|Friend Guard|Weak Armor|Heavy Metal|Light Metal|Multiscale|Toxic Boost|Flare Boost|Harvest|Telepathy|Moody|Overcoat|Poison Touch|Regenerator|Big Pecks|Sand Rush|Wonder Skin|Analytic|Illusion|Imposter|Infiltrator|Mummy|Moxie|Justified|Rattled|Magic Bounce|Sap Sipper|Prankster|Sand Force|Iron Barbs|Zen Mode|Victory Star|Turboblaze|Teravolt|Aroma Veil|Flower Veil|Cheek Pouch|Protean|Fur Coat|Magician|Bulletproof|Competitive|Strong Jaw|Refrigerate|Sweet Veil|Stance Change|Gale Wings|Mega Launcher|Grass Pelt|Symbiosis|Tough Claws|Pixilate|Gooey|Aerilate|Parental Bond|Dark Aura|Fairy Aura|Aura Break|Primordial Sea|Desolate Land|Delta Stream|Stamina|Wimp Out|Emergency Exit|Water Compaction|Merciless|Shields Down|Stakeout|Water Bubble|Steelworker|Berserk|Slush Rush|Long Reach|Liquid Voice|Triage|Galvanize|Surge Surfer|Schooling|Disguise|Battle Bond|Power Construct|Corrosion|Comatose|Queenly Majesty|Innards Out|Dancer|Battery|Fluffy|Dazzling|Soul-Heart|Tangling Hair|Receiver|Power of Alchemy|Beast Boost|RKS System|Electric Surge|Psychic Surge|Misty Surge|Grassy Surge|Full Metal Body|Shadow Shield|Prism Armor|Neuroforce|Intrepid Sword|Dauntless Shield|Libero|Ball Fetch|Cotton Down|Propeller Tail|Mirror Armor|Gulp Missile|Stalwart|Steam Engine|Punk Rock|Sand Spit|Ice Scales|Ripen|Ice Face|Power Spot|Mimicry|Screen Cleaner|Steely Spirit|Perish Body|Wandering Spirit|Gorilla Tactics|Neutralizing Gas|Pastel Veil|Hunger Switch)'
player_stats_insert = '^(?!(The wild|The opposing|.*\s.*\'s.*\'s)).*\'s '
enemy_stats_insert = '(The wild|The opposing|.*\s.*\'s)\s.*\'s '
registered_pokemon_names = set()
def construct_seen_pokemon_regex():
    if len(registered_pokemon_names) == 0:
        return pokemon_names_regex

    extension = '|'
    for pkmn_name in registered_pokemon_names:
        extension += ('%s|' % pkmn_name)
    extension += ')'
    # replace with construction once working
    return (pokemon_names_regex[:-1] + extension)

# WIN LOSE DRAW
#battle_ended_victory_regex = r'You defeated .*!'
end_battle_over_regex = '(You defeated .*|You lost to .*|The battle was canceled.)'
network_menu_can_see_nickname = 'In this battle, the opposing player can see your'
now_connected_to_the_internet = 'now connected to the internet'
communicating_regex = '^Communicating.*\.'
diconnect_ok_regex = 'OK'

first_number_regex = r'\d+'
last_number_regex = r'(\d+)(?!.*\d)'

pokemon_status_regex = '(BURNED)'
pokemon_element_regex = '(BUG|DARK|DRAGON|ELECTRIC|FAIRY|FIGHTING|FIRE|FLYING|GHOST|GRASS|GROUND|ICE|NORMAL|POISON|PSYCHIC|ROCK|STEEL|WATER)'

modifiable_stats = '(Attack|Defense|Sp. Atk|Sp. Def|Speed|accuracy|evasiveness)'

# Sendouts - singles
def get_player_single_pokemon_sentout():
    player_single_pokemon_sentout = r'Go! (.+?)!|You\'re in charge, (.+?)!|Go for it, (.+?)!|Just a little more! Hang in there, (.+?)!|Your opponent\'s weak! Get \'em, (.+?)!|Go on, (.+?)! I know you can do it!'# % (pokemon_names_regex, pokemon_names_regex, pokemon_names_regex, pokemon_names_regex, pokemon_names_regex, pokemon_names_regex)
    player_single_pokemon_sentout = r'Your opponen.* weak(l|!) Get .*em, (.{3,}?)(l|!)$|Go! (.{3,}?)(l|!)$|Yo.*re in charge.*(.{3,}?)(l|!)$|Go(l|!) (.{3,}?)(l|!)$|Go for it.*(.{3,}?)(l|!)$|Just a little more(l|!) Hang in there.* (.{3,}?)(l|!)$|Your opponen.*s weak(l|!) Get .*em.* (.{3,}?)(l|!)$|Go on.* (.{3,}?)(l|!) I know you can do it(!|l)$'# % (pokemon_names_regex, pokemon_names_regex, pokemon_names_regex, pokemon_names_regex, pokemon_names_regex, pokemon_names_regex)
    return player_single_pokemon_sentout

#Omitting any exclamations that appear before the pokemon's name
# This is so that all regexes have the same group ordering.
#Mainly affects just_a_little_regex and opponent_weak_regex
def get_player_single_pokemon_complete(message):
    go_regex = 'Go! (.{3,}?)(l|!)$'
    go_for_it_regex = 'Go for it.* (.{3,}?)(l|!)$'
    incharge_regex = 'Yo.*re in charge.* (.{3,}?)(l|!)$'
    just_a_little_regex = 'Just a little more.* Hang in there.* (.{3,}?)(l|!)$'
    opponent_weak_regex = 'Your opponen.* weak.* Get .*em.* (.{3,}?)(l|!)$'
    you_can_do_it_regex = 'Go on.* (.{3,}?)(l|!) I know you can do it(!|l)$'
    if re.search(go_regex, message):
        return go_regex
    if re.search(go_for_it_regex, message):
        return go_for_it_regex
    if re.search(incharge_regex, message):
        return incharge_regex
    if re.search(just_a_little_regex, message):
        return just_a_little_regex
    if re.search(opponent_weak_regex, message):
        return opponent_weak_regex
    if re.search(you_can_do_it_regex, message):
        return you_can_do_it_regex
    return None
def get_enemy_single_pokemon_sentout(pokemon_names_regex=pokemon_names_regex):
    enemy_single_pokemon_sentout = '.*\ssent out (.+?)!' #% (pokemon_names_regex)
    return enemy_single_pokemon_sentout
def get_wilder_encounters_appeared(pokemon_names_regex=pokemon_names_regex):
    pokemon_names_regex = '(.+?)'
    wilder_encounters_appeared = 'A very strong-looking %s appeared!|Whoa! A very strong-looking %s leaped out!|Oh! A very strong-looking %s appeared!|You encountered a very strong-looking %s!|Whoa! A very strong-looking %s leaped out!|A very strong-looking %s appeared!|You encountered a wild %s!|Whoa! A wild %s leaped out!|Oh! A wild %s appeared!|You encountered a wild %s!|Whoa! The %s you stepped on attacked!|%s appeared!|Whoa! A horde of %s appeared!' % (pokemon_names_regex, pokemon_names_regex, pokemon_names_regex, pokemon_names_regex, pokemon_names_regex, pokemon_names_regex, pokemon_names_regex, pokemon_names_regex, pokemon_names_regex, pokemon_names_regex, pokemon_names_regex, pokemon_names_regex, pokemon_names_regex)
    return wilder_encounters_appeared

# Sendouts - doubles
def get_player_doubles_pokemon_sentout(pokemon_names_regex=pokemon_names_regex):
    player_doubles_pokemon_sentout = 'Go! %s and %s!' % (pokemon_names_regex, pokemon_names_regex)
    return player_doubles_pokemon_sentout
def get_enemy_doubles_pokemon_sentout(pokemon_names_regex=pokemon_names_regex):
    enemy_doubles_pokemon_sentout = '.*\ssent out %s and %s!' % (pokemon_names_regex, pokemon_names_regex)
    return enemy_doubles_pokemon_sentout

#dragged out
def get_player_pokemon_dragged_out():
    player_pokemon_dragged_out = '^(?!(The wild|The opposing|.*\s.*\'s))(.+?) was dragged out' 
    return player_pokemon_dragged_out
def get_enemy_pokemon_dragged_out():
    enemy_pokemon_dragged_out = '^(The wild|The opposing|.*\'s)\s(.+?) was dragged out' 
    return enemy_pokemon_dragged_out

player_insert = '^(?!(The wild|Opposing|.*\s.*\'s))'
enemy_insert = '(The wild|Opposing|.*\s.*\'s)\s.*'

grassy_terrain = 'Grass grew to cover the battlefield!'
psychic_terrain = 'The battlefield got weird!'
electric_terrain = 'An electric current ran across the battlefield!'
misty_terrain = 'Mist swirled around the battlefield!'

grassy_terrain_end = 'The grass disappeared from the battlefield'
psychic_terrain_end = 'The weirdness disappeared from the battlefield!'
electric_terrain_end = 'The electricity disappeared from the battlefield'
misty_terrain_end = 'The mist disappeared from the battlefield'

terrain_start = '(The battlefield got weird!|Grass grew to cover the battlefield!|Mist swirled around the battlefield!|An electric current ran across the battlefield!)'
terrain_end = '(The weirdness disappeared from the battlefield!|The electricity disappeared from the battlefield.|The grass disappeared from the battlefield.|The mist disappeared from the battlefield.)'

rain_start = '(A heavy rain began to fall!|It\'s raining!)'
sun_start = '(The sunlight turned extremely harsh!|The sunlight is harsh!)'
sandstorm_start = '(The sandstorm is raging!)'
delta_storm_start = '(Mysterious strong winds are protecting Flying-type Pokémon!)'
hail_start = '(It\'s hailing!)'

rain_start_end = '(The heavy rain has lifted!|The rain stopped)'
sun_start_end = '(The extremely harsh sunlight faded.|The harsh sunlight faded.)'
sandstorm_start_end = '(The sandstorm subsided.)'
delta_storm_start_end = '(The mysterious strong winds have dissipated!)'
hail_start_end = '(The hail stopped.)'

weather_start = '(A heavy rain began to fall!|The sunlight turned extremely harsh!|Mysterious strong winds are protecting Flying-type Pokémon!|The sunlight is harsh!|It\'s raining!|The sandstorm is raging!|It\'s hailing!)'
weather_end = '(The heavy rain has lifted!|The extremely harsh sunlight faded.|The mysterious strong winds have dissipated!|The harsh sunlight faded.|The rain stopped.|The sandstorm subsided.|The hail stopped.|The effects of the weather disappeared.)'

# Trick resets choice
trick_regex = '(.{3,}?) switched items with its target(!|l)'

#Sticky web
sticky_web_player_side_start = 'A sticky web has been laid out on the ground around your team!'
sticky_web_enemy_side_start = 'A sticky web has been laid out on the ground around the opposing team!'
sticky_web_player_side_end  = 'The sticky web has disappeared from the ground around you!'
sticky_web_enemy_side_end   = 'The sticky web has disappeared from the ground around the opposing team!'

#Spikes
spikes_player_side_start = 'Spikes were scattered on the ground all around your team!'
spikes_enemy_side_start  = 'Spikes were scattered on the ground all around the opposing team!'
spikes_player_side_end   = 'The spikes disappeared from the ground around your team!'
spikes_enemy_side_end    = 'The spikes disappeared from the ground around the opposing team!'

#Toxic Spikes
toxic_spikes_player_side_start = 'Poison spikes were scattered on the ground all around your team!'
toxic_spikes_enemy_side_start  = 'Poison spikes were scattered on the ground all around the opposing team!'
toxic_spikes_player_side_end   = 'The poison spikes disappeared from the ground around your team!'
toxic_spikes_enemy_side_end    = 'The poison spikes disappeared from the ground around the opposing team!'

# Stealth Rocks
stealth_rocks_player_side_start = 'Pointed stones float in the air around your team!'
stealth_rocks_enemy_side_start  = 'Pointed stones float in the air around the opposing team!'
stealth_rocks_player_side_end   = 'The pointed stones disappeared from around your team!'
stealth_rocks_enemy_side_end    = 'The pointed stones disappeared from around the opposing team!'

#Encounters
def get_wild_encounter_regex(pokemon_names_regex=pokemon_names_regex):
    wild_encounter_regex = '(You encountered a wild %s!|Whoa! A wild %s leaped out!|Oh! A wild %s appeared!|You encountered a wild %s!|Whoa! The %s you stepped on attacked!|%s appeared!|Whoa! A horde of %s appeared!)'  % (pokemon_names_regex,pokemon_names_regex,pokemon_names_regex,pokemon_names_regex,pokemon_names_regex,pokemon_names_regex,pokemon_names_regex)
    return wild_encounter_regex
def get_strong_wild_encounter_regex(pokemon_names_regex=pokemon_names_regex):
    strong_wild_encounter_regex = '(A very strong-looking %s appeared!|Whoa! A very strong-looking %s leaped out!|Oh! A very strong-looking %s appeared!|You encountered a very strong-looking %s!|Whoa! A very strong-looking %s leaped out!|A very strong-looking %s appeared!)' % (pokemon_names_regex,pokemon_names_regex,pokemon_names_regex,pokemon_names_regex,pokemon_names_regex,pokemon_names_regex)
    return strong_wild_encounter_regex

# CANT messages
#move_cannot_be_used_choice = 'The %s only allows the use of %s.*' % (pokemon_items_regex, pokemon_attacks_regex)
move_cannot_be_used_choice = 'The %s only allows the ' % (pokemon_items_regex,)
move_cannot_be_used_status = 'The effects of the %s prevent status moves from being used!' % (pokemon_items_regex)
move_cannot_be_used_disabled = '%s is disabled!' % (pokemon_attacks_regex,)
move_cannot_be_used_encore = 'can only use %s' % (pokemon_attacks_regex,)
def get_move_cannot_taunt(pokemon_names_regex=pokemon_names_regex):
    move_cannot_taunt = '(%s can.*t use %s after the taunt!)' % (pokemon_names_regex, pokemon_attacks_regex)
    return move_cannot_taunt
def get_move_cannot_torment(pokemon_names_regex=pokemon_names_regex):
    move_cannot_torment = '(%s can.*t use the same move twice in a row due to the torment!)' % (pokemon_names_regex)
    return move_cannot_torment
def get_move_cannot_be_used(pokemon_names_regex=pokemon_names_regex):
    move_cannot_be_used = '(%s|%s|%s|%s|%s|%s)' % (get_move_cannot_taunt(pokemon_names_regex), get_move_cannot_torment(pokemon_names_regex),move_cannot_be_used_choice, move_cannot_be_used_status, move_cannot_be_used_disabled, move_cannot_be_used_encore)
    return move_cannot_be_used

# No Retreat
def get_player_no_retreat_start(pokemon_names_regex=pokemon_names_regex):
    player_no_retreat_start = '^(?!(The wild|The opposing|.*\'s\s))' + pokemon_names_regex +' can no longer escape because it used No Retreat!'
    return player_no_retreat_start
def get_enemy_no_retreat_start(pokemon_names_regex=pokemon_names_regex):
    enemy_no_retreat_start  = '((The wild|The opposing|.*\'s\s))' + pokemon_names_regex +' can no longer escape because it used No Retreat!'
    return enemy_no_retreat_start

def get_trick_room_start(pokemon_names_regex=pokemon_names_regex):
    trick_room_start = pokemon_names_regex +' twisted the dimensions!'
    return trick_room_start
trick_room_end   = 'The twisted dimensions returned to normal!'
wonder_room_start = 'It created a bizarre area in which Defense and Sp. Def stats are swapped!'
wonder_room_end   = 'Wonder Room wore off, and Defense and Sp. Def stats returned to normal!'
magic_room_start  = 'It created a bizarre area in which Pokémon\'s held items lose their effects!'
magic_room_end    = 'Magic Room wore off, and held items\' effects returned to normal!'

# Trick Room
def get_room_start_regex(pokemon_names_regex=pokemon_names_regex):
    room_start_regex = '(%s|%s|%s)' % (get_trick_room_start(pokemon_names_regex), wonder_room_start, magic_room_start)
    return room_start_regex
room_end_regex = '(%s|%s|%s)'   % (trick_room_end, wonder_room_end, magic_room_end)

# Reflect
reflect_player_side_start = 'Reflect made your team stronger against physical moves!'
reflect_enemy_side_start  = 'Reflect made the opposing team stronger against physical moves!'
reflect_player_side_end   = 'Your team\'s Reflect wore off!'
reflect_enemy_side_end    = 'The opposing team\'s Reflect wore off!'

#Light screen
light_screen_player_side_start = 'Light Screen made your team stronger against special moves!'
light_screen_enemy_side_start   = 'Light Screen made the opposing team stronger against special moves!'
light_screen_player_side_end  = 'Your team\'s Light Screen wore off!'
light_screen_enemy_side_end   = 'The opposing team\'s Light Screen wore off!'

#auraviel
aurora_veil_player_side_start = 'Aurora Veil made your team stronger against physical and special moves!'
aurora_veil_enemy_side_start  = 'Aurora Veil made the opposing team stronger against physical and special moves!'
aurora_veil_player_side_end   = 'Your team\'s Aurora Veil wore off!'
aurora_veil_enemy_side_end    = 'The opposing team\'s Aurora Veil wore off!'


# Safeguard
safeguard_player_side_start = 'Your team cloaked itself in a mystical veil!'
safeguard_enemy_side_start  = 'The opposing team cloaked itself in a mystical veil!'
safeguard_player_side_end   = 'Your team is no longer protected by Safeguard!'
safeguard_enemy_side_end    = 'The opposing team is no longer protected by Safeguard!'

# Prevents stats reduction   - mist
mist_player_side_start = 'Your team became shrouded in mist!'
mist_enemy_side_start  = 'The opposing team became shrouded in mist!'
mist_player_side_end   = 'Your team is no longer protected by mist!'
mist_enemy_side_end    = 'The opposing team is no longer protected by mist!'


# Tail wind
tailwind_player_side_start = 'The Tailwind blew from behind your team!'
tailwind_enemy_side_start  = 'The Tailwind blew from behind the opposing team!'
tailwind_player_side_end   = 'Your team\'s Tailwind petered out!'
tailwind_enemy_side_end    = 'The opposing team\'s Tailwind petered out!'

# Not in gen 8, prevents criticals
lucky_chant_player_side_start = 'Lucky Chant shielded your team from critical hits!'
lucky_chant_enemy_side_start  = 'Lucky Chant shielded the opposing team from critical hits!'
lucky_chant_player_side_end   = 'Your team\'s Lucky Chant wore off!'
lucky_chant_enemy_side_end    = 'The opposing team\'s Lucky Chant wore off!'

# Water Sport
water_start_regex = 'Fire\'s power was weakened!'
water_end_regex   = 'The effects of Water Sport have faded.'

#Mud Sport
mdusport_start_regex = 'Electricity\'s power was weakened!'
mdusport_end_regex   = 'The effects of Mud Sport have faded.'

#Gravity
gravity_start_regex = 'Gravity intensified!'
gravity_end_regex = 'Gravity returned to normal!'

# Neutralizing Gas
neutralizing_gas_start = 'Neutralizing gas filled the area!'
neutralizing_gas_end   = 'The effects of the neutralizing gas wore off!'

# Fainting
def get_fainted_player_regex(pokemon_names_regex=pokemon_names_regex):
    fainted_player_regex = '^(?!(The wild|The opposing|.*\'s\s))%s fainted' % (pokemon_names_regex)
    return fainted_player_regex
def get_fainted_enemy_regex(pokemon_names_regex=pokemon_names_regex):
    fainted_enemy_regex  = '((The wild|The opposing|.*\'s))\s%s fainted'    % (pokemon_names_regex)
    return fainted_enemy_regex

# Switchout - should clear active stats
def get_returned_to_player_regex(pokemon_names_regex=pokemon_names_regex):
    returned_to_player_regex = '(%s, switch out! Come back!|%s, come back!|%s, that’s enough! Come back!|OK, %s! Come back!|Good job, %s! Come back!)' % (pokemon_names_regex, pokemon_names_regex, pokemon_names_regex, pokemon_names_regex, pokemon_names_regex)
    return returned_to_player_regex
def get_returned_to_enemy_regex(pokemon_names_regex=pokemon_names_regex):
    returned_to_enemy_regex  = '(%s went back to.*!| withdrew %s!)'    % (pokemon_names_regex, pokemon_names_regex)
    return returned_to_enemy_regex

#Problem, needs custom logic to ensure not volt switch
#ロトム went back to Lou Ruil
#Volt Switch
def get_uturn_volt_switch_regex(trainer_name='Lou Rui'):
    uturn_volt_switch_regex  = ' went back to %s'    % (trainer_name)
    return uturn_volt_switch_regex

###### COMPLETE     ######


#player_stats_rose_regex = '.*'s (Attack|Defense|Sp. Atk|Sp. Def|Speed|accuracy|evasiveness)\srose!'

enemy_stats_rose_regex = enemy_stats_insert + modifiable_stats +'\srose!'
enemy_stats_rose_sharply_regex = enemy_stats_insert + modifiable_stats + '\srose sharply!'
enemy_stats_rose_drastically_regex = enemy_stats_insert + modifiable_stats + '\srose drastically!'
enemy_stats_fell_regex = enemy_stats_insert + modifiable_stats + '\sfell!'
enemy_stats_fell_harshly_regex = enemy_stats_insert + modifiable_stats + '\sharshly fell!'
enemy_stats_fell_severely_regex = enemy_stats_insert + modifiable_stats + '\sseverely fell!'

player_stats_rose_regex = player_stats_insert + modifiable_stats + '\srose!'
player_stats_rose_sharply_regex = player_stats_insert + modifiable_stats + '\srose sharply!'
player_stats_rose_drastically_regex = player_stats_insert + modifiable_stats + '\srose drastically!'
player_stats_fell_regex = player_stats_insert + modifiable_stats + '\sfell!'
player_stats_fell_harshly_regex = player_stats_insert + modifiable_stats + '\sharshly fell!'
player_stats_fell_severely_regex = player_stats_insert + modifiable_stats + '\sseverely fell!'


#Small reward/punishment
def get_player_stats_not_lowered_one_regex(pokemon_names_regex=pokemon_names_regex):
    player_stats_not_lowered_one_regex = '^(?!(The wild|The opposing|.*\s.*\'s.*\'s)).*' + pokemon_names_regex + '\'s stats were not lowered!'
    return player_stats_not_lowered_one_regex
def get_player_stats_not_lowered_two_regex(pokemon_names_regex=pokemon_names_regex):
    player_stats_not_lowered_two_regex = '^(?!(The wild|The opposing|.*\s.*\'s.*\'s)).*' + pokemon_names_regex + '\'s ' +modifiable_stats+ '\swas not lowered!'
    return player_stats_not_lowered_two_regex
def get_enemy_stats_not_lowered_one_regex(pokemon_names_regex=pokemon_names_regex):
    enemy_stats_not_lowered_one_regex = '(The wild|The opposing|.*\s.*\'s)\s' +pokemon_names_regex+ '\'s stats were not lowered!'
    return enemy_stats_not_lowered_one_regex
def get_enemy_stats_not_lowered_two_regex(pokemon_names_regex=pokemon_names_regex):
    enemy_stats_not_lowered_two_regex = '(The wild|The opposing|.*\s.*\'s)\s' +pokemon_names_regex+ '\'s ' + modifiable_stats + '\swas not lowered!'
    return enemy_stats_not_lowered_two_regex

#Update active stats
def get_player_stat_changes_removed_regex(pokemon_names_regex=pokemon_names_regex):
    player_stat_changes_removed_regex = '^(?!(The wild|The opposing|.*\s.*\'s.*\'s))' + pokemon_names_regex + '\'s stat changes were removed!'
    return player_stat_changes_removed_regex
def get_enemy_stat_changes_removed_regex(pokemon_names_regex=pokemon_names_regex):
    enemy_stat_changes_removed_regex = '(The wild|The opposing|.*\'s).' + pokemon_names_regex + '\'s stat changes were removed!'
    return enemy_stat_changes_removed_regex

# All stat changes eliminated
all_stats_eliminated_regex = 'All stat changes were eliminated!'

# base ability regex.  needs to be extended with full list of valid abilities.
def get_ability_revealed_regex(pokemon_names_regex=pokemon_names_regex):
    ability_revealed_regex = pokemon_names_regex+'s\s'+ pokemon_ability_regex
    return ability_revealed_regex

# critical hit
critical_regex = 'A critical hit!'

# Used move
def get_player_used_move_one_regex(pokemon_names_regex=pokemon_names_regex):
    player_used_move_one_regex = '^(?!(The wild\s|The opposing\s|.*\'s\s))' + pokemon_names_regex+' used '+pokemon_attacks_regex
    return player_used_move_one_regex
def get_enemy_used_move_one_regex(pokemon_names_regex=pokemon_names_regex):
    enemy_used_move_one_regex = '(The wild|The opposing|.*\'s) ' + pokemon_names_regex+' used '+pokemon_attacks_regex
    return enemy_used_move_one_regex


# FORME Changes
shields_down_deactivated = 'Shields Down deactivated!'
shields_down_activated   = 'Shields Down activated!'
disguise_busted = 'Its disguise served it as a decoy!'
blade_forme_change  = 'Changed to Blade Forme!'
shield_forme_change = 'Changed to Shield Forme!'

# Drowsy
def get_enemy_drowsy_regex(pokemon_names_regex=pokemon_names_regex):
    enemy_drowsy_regex = '^(The wild|The opposing|.*\'s)\s%s grew drowsy!' % (pokemon_names_regex)
    return enemy_drowsy_regex
def get_player_drowsy_regex(pokemon_names_regex=pokemon_names_regex):
    player_drowsy_regex = '^(?!(The wild|The opposing|.*\'s)).*%s' % (pokemon_names_regex)
    return player_drowsy_regex

# Cant
cant_confusion_regex = 'It hurt itself in its confusion!'
cant_paralysis_regex = 'is paralyzed! It may be unable to move!'

#Effective
attack_resisted_regex = 'It’s not very effective...'
attack_super_effective_regex = 'It’s super effective!'
def get_attack_immune_regex(pokemon_names_regex=pokemon_names_regex):   
    attack_immune_regex = 'It doesn’t affect.*%s' % (pokemon_names_regex)
    return attack_immune_regex

#Confusion
confusion_begin_regex = '(became confused!|became confused due to fatigue!)'
confusion_ended_regex = '(snapped out of its confusion!)'


# Status Changed
status_changed_regex = '(was poisoned!|was badly poisoned!|was badly poisoned by the|was cured of its poisoning!|was burned!|was burned by the |burn was healed!|was cured of paralysis!|is paralyzed! It may be unable to move!|was frozen solid!|thawed out!|melted the ice!|fell asleep!|woke up!)'
status_cured_regex = '(was cured of its poisoning!|burn was healed!|was cured of paralysis!|thawed out!|melted the ice!|woke up!)'


####  TESTING   ######

cinderace_enterex_example = 'Go on, Cinderace! I know you can do it!'
ability_example = 'Garbodor\'s Weak Armor'
critical_example = 'A critical hit!'
attack_example = 'Pikachu used Apple Acid!'
player_move_example = 'Pikachu used Apple Acid!'
enemy_move_example = 'Jim\'s Pichu used Apple Acid!'
player_stat_not_lowered_example_1 = 'Pikachu\'s stats were not lowered!'
player_stat_not_lowered_example_2 = 'Pikachu\'s accuracy was not lowered!'
enemy_stat_not_lowered_example_1 = 'The opposing Pikachu\'s stats were not lowered!'
enemy_stat_not_lowered_example_2 = 'The opposing Pikachu\'s Defense was not lowered!'
player_stat_changes_removed_example = 'Pikachu\'s stat changes were removed!'
enemy_stat_changes_removed_example = 'The opposing Pikachu\'s stat changes were removed!'
all_stats_eliminated_example = 'All stat changes were eliminated!'

enemy_stats_rose_example = 'The wild Pikachu\'s accuracy rose!'
enemy_stats_rose_sharply_example = 'The opposing Pikachu\'s accuracy rose sharply!'
enemy_stats_rose_drastically_example = 'The opposing Pikachu\'s accuracy rose drastically!'
enemy_stats_fell_example = 'The opposing Pikachu\'s accuracy fell!'
enemy_stats_fell_harshly_example = 'The opposing Pikachu\'s Sp. Def harshly fell!'
enemy_stats_fell_severely_example =  'The opposing Pikachu\'s Defense severely fell!'

player_stats_rose_example = 'Pikachu\'s accuracy rose!'
player_stats_rose_sharply_example = 'Pikachu\'s Attack rose sharply!'
player_stats_rose_drastically_example = 'Pikachu\'s Defense rose drastically!'
player_stats_fell_example = 'Pikachu\'s Attack fell!'
player_stats_fell_harshly_example = 'Pikachu\'s evasiveness harshly fell!'
player_stats_fell_severely_example =  'Pikachu\'s evasiveness severely fell!'

player_no_retreat_example = 'Pikachu can no longer escape because it used No Retreat!'
enemy_no_retreat_example  = 'Jim\'s Pikachu can no longer escape because it used No Retreat!'

print(re.search(get_player_no_retreat_start(), player_no_retreat_example))
print(re.search(get_enemy_no_retreat_start(), enemy_no_retreat_example))
print(re.search(get_ability_revealed_regex(), ability_example))
print(re.search(critical_regex, critical_example))
print(re.search(get_player_used_move_one_regex(), player_move_example))
print(re.search(get_enemy_used_move_one_regex(), enemy_move_example))
print(re.search(get_player_stats_not_lowered_one_regex(), player_stat_not_lowered_example_1))
print(re.search(get_player_stats_not_lowered_two_regex(), player_stat_not_lowered_example_2))
print(re.search(get_enemy_stats_not_lowered_one_regex(), enemy_stat_not_lowered_example_1))
print(re.search(get_enemy_stats_not_lowered_two_regex(), enemy_stat_not_lowered_example_2))
print(re.search(get_player_stat_changes_removed_regex(), player_stat_changes_removed_example))
print(re.search(get_enemy_stat_changes_removed_regex(), enemy_stat_changes_removed_example))
print(re.search(all_stats_eliminated_regex, all_stats_eliminated_example))

print(re.search(enemy_stats_rose_regex, enemy_stats_rose_example))
print(re.search(enemy_stats_rose_sharply_regex, enemy_stats_rose_sharply_example))
print(re.search(enemy_stats_rose_drastically_regex, enemy_stats_rose_drastically_example))
print(re.search(enemy_stats_fell_regex, enemy_stats_fell_example))
print(re.search(enemy_stats_fell_harshly_regex, enemy_stats_fell_harshly_example))
print(re.search(enemy_stats_fell_severely_regex, enemy_stats_fell_severely_example))

print(re.search(player_stats_rose_regex, player_stats_rose_example))
print(re.search(player_stats_rose_sharply_regex, player_stats_rose_sharply_example))
print(re.search(player_stats_rose_drastically_regex, player_stats_rose_drastically_example))
print(re.search(player_stats_fell_regex, player_stats_fell_example))
print(re.search(player_stats_fell_harshly_regex, player_stats_fell_harshly_example))
print(re.search(player_stats_fell_severely_regex, player_stats_fell_severely_example))


print(re.search(get_player_single_pokemon_sentout(), cinderace_enterex_example))


