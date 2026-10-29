# Glossary - GetBackers Dakkanya: Jigoku no Scaramouche

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.
`tools/batches.py check` enforces: speaker labels (Characters rows) as `EN: `, honorifics after Characters names,
and the Avoid column. Rows: `JP forms (comma-separated) | EN | max | notes | Avoid`.

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics: kept, hyphenated (Ginji-san, Ban-chan). Name order: Western (Ban Mido, Ginji Amano).
- Romanisation source: official English (Tokyopop manga, English anime dub), else Hepburn without macrons.
- Credits: English.
- Register: casual modern English, mild swearing for Ban and thugs; villains formal. Sound effects: English
  onomatopoeia (WHAM!, Kyaaah!).
- Abbreviations: full names and terms everywhere (no "Asst.", "E-Key"); prefer engine changes over shortening.

## Style rules
- Speakers: `蛮「...」` -> `Ban: "..."`; `銀次：...` -> `Ginji: ...`. Multi-page quotes: `"` opens on the first page,
  closes on the last.
- Punctuation map: 「」 -> "...", 『』 -> '...' inside speech, "..." in narration, ……/・・・ -> ..., ！？ -> ?!,
  ～ -> ~ or a stretched word, （） -> ( ), 【】 -> [ ], full-width digits/letters -> ASCII.
- Voices: docs/style-reference.md. Plot, reveals: docs/synopsis.md (Scaramouche stays ungendered before step 235;
  Umakai's true identity before step 211; Sachiko is a ghost, step 94).

## Characters
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 美堂蛮 | Ban Mido |  | Official (Tokyopop/anime). Label 蛮. |  |
| 蛮 | Ban |  | Official (Tokyopop/anime). Label 蛮. |  |
| 天野銀次 | Ginji Amano |  | Official. Labels 銀次 and short 銀 (step 8) -> Ginji. |  |
| 銀次, 銀 | Ginji |  | Official. Labels 銀次 and short 銀 (step 8) -> Ginji. |  |
| たれ銀次 | Tare-Ginji |  | Battle label for Ginji's droopy chibi form (fan name "Tare-Ginji"). unsure: official dub name |  |
| 冬木士度 | Shido Fuyuki |  | Official. |  |
| 士度 | Shido |  | Official. |  |
| 風鳥院花月 | Kazuki Fuchoin |  | Official; game's own EN label KADSUKI, glossary uses Kazuki. |  |
| 花月 | Kazuki |  | Official; game's own EN label KADSUKI, glossary uses Kazuki. |  |
| 工藤卑弥呼 | Himiko Kudo |  | Official. |  |
| 卑弥呼 | Himiko |  | Official. |  |
| 赤屍蔵人 | Kurodo Akabane |  | Official. |  |
| 赤屍 | Akabane |  | Official. |  |
| ドクター・ジャッカル | Dr. Jackal |  | Akabane's alias (official). |  |
| レディ・ポイズン | Lady Poison |  | Himiko's alias (official). |  |
| ＨＥＶＮ | Hevn |  | Official spelling Hevn (not Heaven). |  |
| 波児（ポール）, 波児 | Paul |  | Paul Wan, HONKY TONK owner (official). Ruby gives ポール. |  |
| マスター | Paul |  | Speaker label for Paul ("Master" in-world). Use Paul for clarity; alt "Master". |  |
| 夏実 | Natsumi |  | Natsumi Mizuki (official); surname not in script. |  |
| マドカ | Madoka |  | Madoka Otowa (official); only mentioned. マドカお嬢様 = "Lady Madoka"/"Miss Madoka". |  |
| スカラムーシュ | Scaramouche |  | Main villain; secretly Asia Mandel, a WOMAN (reveal step 235-236). Keep ungendered before. |  |
| 地獄のスカラムーシュ | Scaramouche of Hell |  | Title/epithet; also game subtitle. unsure: alt "Hellish Scaramouche" |  |
| アーシア・マンデル | Asia Mandel |  | Scaramouche's real name. unsure: アーシア could be Aasia/Arcia/Ursia; Asia is the plain reading |  |
| アーシア | Asia |  | Scaramouche's real name. unsure: アーシア could be Aasia/Arcia/Ursia; Asia is the plain reading |  |
| 馬飼 | Umakai |  | Scaramouche's secretary; really Kudaru Hitoya (reveal step 211). |  |
| 疑獄行使 | Kudaru Hitoya |  | Ruby ひとや・くだる. Ura-Tocho spy, Shadow Assembly Speaker. Tone-deaf joke. |  |
| 疑獄 | Hitoya |  | Ruby ひとや・くだる. Ura-Tocho spy, Shadow Assembly Speaker. Tone-deaf joke. |  |
| 醜野丈夫 | Masurao Shikono |  | Ruby しこのますらお. Shadow Governor. Old-man speech. |  |
| 丈夫 | Masurao |  | Ruby しこのますらお. Shadow Governor. Old-man speech. |  |
| 醜野御楯 | Mitate Shikono |  | Ruby しこの・みたて. Vice Governor, Masurao's younger brother. |  |
| 御楯 | Mitate |  | Ruby しこの・みたて. Vice Governor, Masurao's younger brother. |  |
| 赤井太陽 | Terasu Akai |  | Ruby あかいてらす. Treasurer. |  |
| 赤井 | Akai |  | Ruby あかいてらす. Treasurer. |  |
| 青野月光 | Hikari Aono |  | Ruby あおの・ひかり. Administrative Commissioner. |  |
| 青野 | Aono |  | Ruby あおの・ひかり. Administrative Commissioner. |  |
| 黄田大地 | Daichi Kida |  | No ruby. unsure: reading of 黄田 (Kida/Kita/Oda); killed by Akabane in flashback |  |
| 黄田 | Kida |  | No ruby. unsure: reading of 黄田 (Kida/Kita/Oda); killed by Akabane in flashback |  |
| 玉井・アイリーン・沙恵見 | Saemi Eileen Tamai |  | Ura-Tocho receptionist. unsure: アイリーン = Eileen or Irene |  |
| 沙恵見 | Saemi |  | Ura-Tocho receptionist. unsure: アイリーン = Eileen or Irene |  |
| シュレッダー | Shredder |  | OA-OLDERS member (boss). |  |
| タイムコーダー | Time Coder |  | OA-OLDERS member; pun on time recorder (punch clock). |  |
| フクシャー | Copier |  | OA-OLDERS member; 複写 (copy) + -er. unsure: alt "Copyer" to keep -er pun |  |
| 山村 | Yamamura |  | Homeless old man in the park; Rika's father. Ginji calls him オッチャン (Pops). |  |
| 山村理香 | Rika Yamamura |  | Yamamura's daughter; label 女 before she gives her name (step 43-47). |  |
| 理香 | Rika |  | Yamamura's daughter; label 女 before she gives her name (step 43-47). |  |
| 組長 | Boss |  | Haraguro Kogyo yakuza boss (Kansai speech). |  |
| 若頭 | Underboss |  | Label; he is really 若頭代理補佐. |  |
| アニキ | Big Bro |  | The bully's big brother (Kansai). Also yakuza "Aniki" in 組員 lines -> "boss"/"bro". |  |
| 周 | Zhou |  | Chinese go-between with Scaramouche's money. unsure: Zhou vs Chou vs Shu (Hepburn) |  |
| 須玉サチ子 | Sachiko Sudama |  | Hospital client; ghost of the director's wife (twist step 94). |  |
| サチ子 | Sachiko |  | Hospital client; ghost of the director's wife (twist step 94). |  |
| 宇治田裕也 | Yuya Ujita |  | Ex-VOLTS; Dragonia trainee. |  |
| 裕也 | Yuya |  | Ex-VOLTS; Dragonia trainee. |  |
| 結城美恵 | Mie Yuki |  | Yuya's girlfriend. |  |
| 美恵 | Mie |  | Yuya's girlfriend. |  |
| 今里奈緒 | Nao Imazato |  | Patty's owner. |  |
| 奈緒 | Nao |  | Patty's owner. |  |
| パティ | Patty |  | White Briard dog. |  |
| パロ | Paro |  | Parrot at the pet shop. |  |
| 風間蜥蜴児 | Kimoji Kazama |  | Ruby かざまきもじ. Pet shop manager. |  |
| 風間 | Kazama |  | Ruby かざまきもじ. Pet shop manager. |  |
| 菱木竜童 | Ryudo Hishiki |  | Alias "Undead" (アンデッド). Anime character. |  |
| 菱木 | Hishiki |  | Alias "Undead" (アンデッド). Anime character. |  |
| 芹沢博史 | Hiroshi Serizawa |  | Fired Sazanami engineer. |  |
| 芹沢 | Serizawa |  | Fired Sazanami engineer. |  |
| 鹿山郁夫 | Ikuo Kayama |  | Ruby かやま・いくお. Sazanami vice-president. |  |
| 鹿山 | Kayama |  | Ruby かやま・いくお. Sazanami vice-president. |  |
| 耶柄庸介 | Yosuke Yagara |  | Ruby やがら・ようすけ. Enemy list writes 傭介 (typo). Sazanami military adviser. |  |
| 耶柄傭介, 耶柄 | Yagara |  | Ruby やがら・ようすけ. Enemy list writes 傭介 (typo). Sazanami military adviser. |  |
| 天子峰 | Teshimine |  | Takeru Teshimine (天子峰猛), Ginji's mentor in the Limitless Fortress (anime credits). |  |
| 青樹佑夜 | Yuya Aoki |  | Bonus cameo enemy = the manga's writer (official credit spelling). |  |
| 綾峰欄人 | Rando Ayamine |  | Bonus cameo enemy = the manga's artist (official credit spelling). |  |
| ？？？, ？？ | ??? |  | Mystery label/enemy. |  |
| ゾンビ | Zombie |  | Illusion during the bomb scene. |  |
| μベビー | Mu Baby |  | Mitate's pet, called Pochi. unsure: keep Greek "μ Baby" if font has it |  |
| ポチ | Pochi |  | Mitate's pet name (classic Japanese dog name). |  |
| α（アルファ） | Alpha |  | Enemy, "Silver-haired Devil". |  |
| β（ベータ） | Beta |  | Enemy, "Red-haired Demon". |  |
| ジャック | Jack |  | Sazanami android enemy. 改 -> Mk II throughout. |  |
| ジャック改 | Jack Mk II |  | Sazanami android enemy. 改 -> Mk II throughout. |  |
| ビット | Bit |  | Sazanami security robot enemy. |  |
| ビット改 | Bit Mk II |  | Sazanami security robot enemy. |  |
| ペット屋ジョー | Pet Shop Joe |  | Enemy; dog named Indigo. |  |
| ペット屋スネーク | Pet Shop Snake |  | Enemy; snake named Solid (Metal Gear joke). |  |
| マンジ兄弟Ａ | Manji Brother A |  | Enemy. |  |
| 怖いお兄さんＡ | Scary Dude A |  | Yakuza enemies A-D. |  |
| 美人看護婦Ａ | Pretty Nurse A |  | Hospital enemy (hallucination). |  |
| 主任看護婦Ａ | Head Nurse A |  | Hospital enemy. |  |
| マッドドクターＡ | Mad Doctor A |  | Hospital enemy. |  |
| ウサギロボ | Rabbit Robo |  | Enemy. |  |
| 旧型警備ロボット | Old Security Robot |  | Enemy. |  |
| 警備ロボット改 | Security Robot Mk II |  | Enemy ("3x normal performance"). |  |
| 裏都庁特殊部隊員 | Ura-Tocho Special Forces |  | Enemy. Check width. |  |
| ジャンクキッズＡ | Junk Kid A |  | Enemy; nicknames Strawberry, Chappy, Samba. |  |
| サザナミ社員 | Sazanami Employee |  | Enemy. |  |
| エージェント | Agent |  | Ura-Tocho agents; A' -> A'. |  |
| エージェントＡ | Agent A |  | Ura-Tocho agents; A' -> A'. |  |
| カラス | Crow |  | Enemy. |  |
| ハエ | Fly |  | Enemy. |  |
| 番犬 | Guard Dog |  | Enemy and label. |  |
| ヤマダ | Yamada |  | Sazanami employee who challenges you. |  |
| ササキ | Sasaki |  | Sazanami employee. |  |
| レイナ | Reina |  | Lost girl in the park. |  |
| マナ | Mana |  | Reina's little sister. |  |
| じゅんや | Junya |  | Park kid. |  |
| タカコママ | Takako's Mom |  | Park NPC. unsure: could be "Mama Takako" (Takako is the mother) |  |
| カズオパパ | Kazuo's Dad |  | Sazanami NPC; part of the Kazuo running joke. |  |
| かずお | Kazuo |  | Running joke name (dev in-joke). |  |
| キャスター | Newscaster |  | Label. |  |
| 声 | Voice |  | Label. |  |
| 女 | Woman |  | Label. |  |
| 男 | Man |  | Label. |  |
| 男ども | Guys |  | Label (Ban/Ginji/Shido together). |  |
| 一同 | All |  | Label. |  |
| ＧＢ | GetBackers |  | Label for Ban+Ginji together. |  |
| ギャル | Girl |  | Label, step 4. |  |
| コギャル | Teen Girl |  | Label (kogal). |  |
| 小学生 | Schoolboy |  | Label, the client kid in Act 1. |  |
| いじめっこ | Bully |  | Label. |  |
| 子供 | Kid |  | Label. |  |
| お母さん, 母親 | Mom |  | Label. |  |
| お爺さん, 爺, じいちゃん | Grandpa |  | Labels. お爺さん's "boo!" jokes. |  |
| お婆さん, ばあちゃん | Granny |  | Labels; お婆さん's 「はて、...」 questions. |  |
| 老人 | Old Man |  | Label. |  |
| オジサン | Old Guy |  | Label (homeless park men; "公園のオジサン"). Wants a bath. |  |
| 店員 | Clerk |  | Label (burger stand, pet shop). |  |
| ペット屋店員 | Pet Shop Clerk |  | Label. |  |
| 客 | Customer |  | Label. |  |
| 愛犬家 | Dog Lover |  | Label. |  |
| 警官 | Cop |  | Label. |  |
| 警備員 | Guard |  | Label; 警備員？ -> Guard? |  |
| 老警備員 | Old Guard |  | Label. |  |
| 組員 | Gangster |  | Label. |  |
| 相方 | Partner |  | Label. |  |
| 社員 | Employee |  | Label (Sazanami). |  |
| 局員 | Staffer |  | Label (Sazanami development office). |  |
| 会社員 | Office Worker |  | Label (station). |  |
| ＯＬ | Office Lady |  | Label. |  |
| 作業員 | Worker |  | Label. |  |
| オペレーター, オペレータ | Operator |  | Labels. |  |
| おばちゃん | Cleaning Lady |  | Label (Sazanami cleaner with the memo). |  |
| そうじのおばさん | Cleaning Lady |  | Label (station). |  |
| 売店のオバチャン | Kiosk Lady |  | Label. |  |
| 駅員 | Station Attendant |  | Label. |  |
| 職員 | Staffer |  | Label (Ura-Tocho). |  |
| 女職員 | Staffer |  | Label (Ura-Tocho, female). |  |
| 受付嬢 | Receptionist |  | Label (Saemi). |  |
| ジャンク・キッズ | Junk Kid |  | Label (singular member). |  |
| ドラゴニア会, ドラゴニア会構成員, ドラゴニア会員 | Dragonia Member |  | Labels. |  |
| 犬 | Dog |  | Label. |  |
| 猫 | Cat |  | Label. |  |

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 裏新宿 | Ura-Shinjuku |  | Keep "Ura-" for the station-line Urawa pun. unsure: alt "Shadow Shinjuku" |  |
| 裏都庁 | Ura-Tocho |  | Shadow city hall that runs the underworld. unsure: alt "Shadow City Hall"; pick one with 裏新宿 |  |
| 都知事室 | Governor's Office |  | Masurao's room, 30th floor. |  |
| 裏新宿中央公園 | Ura-Shinjuku Central Park |  | Location card. |  |
| 裏新宿西病院 | Ura-Shinjuku West Hospital |  | In 6-chome. |  |
| 裏新宿駅 | Ura-Shinjuku Station |  | Act 5; location card. |  |
| 裏渋谷 | Ura-Shibuya |  | Station destinations. |  |
| 裏池袋 | Ura-Ikebukuro |  | Station destinations. |  |
| 裏品川 | Ura-Shinagawa |  | Station destinations. |  |
| 裏上野 | Ura-Ueno |  | Station destinations. |  |
| 裏横浜 | Ura-Yokohama |  | Station destinations. |  |
| 裏和 | Urawa |  | Pun: 裏 + 和 = Urawa (浦和). |  |
| 新宿 | Shinjuku |  | Plain Shinjuku (新宿界隈). |  |
| 腹黒興業, 腹組興業 | Haraguro Kogyo |  | Yakuza outfit ("black-hearted"). 腹組 appears twice (typo). Location card 腹黒興業組長邸 = Haraguro Boss's Mansion. |  |
| ＨＯＮＫＹＴＯＮＫ | HONKY TONK |  | Official; location card is already EN. |  |
| 公園バーガー | Park Burger |  | Burger stand; 80 yen on weekdays. |  |
| キモジ’ｓペット店, キモジ’ｓペット | Kimoji's Pet Shop |  | Location card; Act 3. |  |
| サザナミ・コーポレーション | Sazanami Corporation |  | High-tech conglomerate; location card; Act 4. |  |
| サザナミ | Sazanami |  | High-tech conglomerate; location card; Act 4. |  |
| 無限城 | Limitless Fortress |  | Not in this script. unsure: official dub "Limitless Fortress" vs Tokyopop "Infinity Fortress" |  |

## Items
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 招き猫 | Maneki-neko |  | Giant beckoning-cat statue; party member label MANEKINEKO in game EN art. |  |
| リカバージュース（Ｓ） | Recovery Juice (S) |  | HP small/medium/full, one ally. |  |
| リカバージュース（Ｍ） | Recovery Juice (M) |  | HP small/medium/full, one ally. |  |
| リカバージュース（Ｌ） | Recovery Juice (L) |  | HP small/medium/full, one ally. |  |
| ゲンの特製ドリンク | Gen's Special Drink |  | All: Tension up. |  |
| 高麗エキス | Ginseng Extract |  | One: Tension up (高麗 = Korean ginseng). |  |
| 芍薬エキス | Peony Extract |  | One: Tension max. |  |
| ハンバーガー | Hamburger |  | All: HP small. |  |
| ビッグバーガー | Big Burger |  | All: HP medium. |  |
| ポイズンキュアー | Poison Cure |  | Cures poison. |  |
| パラライズキュアー | Paralysis Cure |  | Cures paralysis. |  |
| スタビライザー | Stabilizer |  | Cures confusion. |  |
| オールキュアー | All Cure |  | Cures everything. |  |
| ニュートライザー | Neutralizer |  | Restores stats. |  |
| 彼岸花の粉 | Spider Lily Powder |  | Revive with low HP. |  |
| 鬼百合の球根 | Tiger Lily Bulb |  | Revive with full HP. |  |
| 蓬莱の玉 | Horai Jewel |  | All: revive with full HP. |  |
| 激烈丹 | Fury Pill |  | Attack up. |  |
| 硬化散 | Hardening Powder |  | Defense up. |  |
| 疾風丸 | Gale Pill |  | Speed up. |  |
| 冴精湯 | Sharp Tonic |  | Evasion up. |  |
| 衰退丹 | Decline Pill |  | Attack down. |  |
| 弛緩散 | Slack Powder |  | Defense down. |  |
| 遅速丸 | Slow Pill |  | Speed down. |  |
| 鈍精湯 | Dull Tonic |  | Evasion down. |  |
| 休憩室の鍵 | Break Room Key |  | Act 1 mansion key item. |  |
| 倉庫の鍵 | Storeroom Key |  | Act 1 mansion key item. |  |
| 一般社員用ＩＤカード　１, ＩＤカード１ | Staff ID Card 1 |  | Also 2, 3. |  |
| 最高幹部用ＩＤカード | Executive ID Card |  | Sazanami top-floor access. |  |
| 電子キーＡ | Electronic Key A |  | A-E. |  |
| パンダの着ぐるみ | Panda Suit |  | Teaches Shido 熊猫擬. |  |
| 銀次と天子峰の写真 | Photo of Ginji and Teshimine |  | Teaches 雷帝降臨. unsure: see 天子峰 |  |
| 雷魂 | Thunder Soul |  | Key item. unsure: what it does / reading |  |
| ダミー | Dummy |  | Unused item slot. |  |
| 非常用携帯食料 | emergency rations |  | Field pickup, restores HP. |  |

## Terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ＯＡ―ＯＬＤＥＲＳ | OA-OLDERS |  | Office Automation + "olders"; the three old men. |  |
| 若頭代理補佐, わかがしらだいりほさ | Assistant Acting Underboss |  | Joke title; enemy list hiragana version in his enemy blurb. |  |
| ザコ若頭代理補佐 | Small-Fry Assistant Acting Underboss |  | Enemy name. Check width. |  |
| アンデッド | Undead |  | Hishiki's alias. |  |
| ザガッド | Zagad |  | Sazanami auto-tracking security robot. 第二形態 Second Form, 第三形態・Ｂモード Third Form B Mode, 最終形態・Ｆモード Final Form F Mode. |  |
| Ｂモード | B Mode |  | Zagad battle mode. |  |
| Ｆモード | F Mode |  | "F for Final and Phoenix" (step ~182). |  |
| ＳＣＫ－１号 | SCK-1 |  | Hypnotherapy machine boss. |  |
| 自動追尾防犯装置 | auto-tracking security system |  | Zagad's official description. |  |
| 自分 | Self |  | Target label "self". |  |
| 単 | One |  | Item target: one ally. "単：ＨＰ少回復" -> "One: ...". |  |
| 全 | All |  | Item target: all allies. |  |
| 味単 | Ally |  | Skill target: one ally. |  |
| 味全 | All allies |  | Skill target: all allies. |  |
| 敵単 | Foe |  | Skill target: one enemy. |  |
| 敵全 | All foes |  | Skill target: all enemies. |  |
| 敵全体 | All Enemies |  | Target menu. |  |
| 味方全体 | All Allies |  | Target menu. |  |
| 裏都知事 | Governor |  | Masurao. unsure: tie to 裏都庁 choice |  |
| 副知事, 副都知事 | Vice Governor |  | Mitate. |  |
| 裏都議会議長, 都議会長 | Assembly Speaker |  | Gigoku's title. |  |
| 出納長 | Treasurer |  | Akai. |  |
| 行政委員 | Administrative Commissioner |  | Aono. |  |
| 内政監視特別委員会, 内政監視委員会, 裏都庁内政監視委員会 | Internal Affairs Oversight Committee |  | Full name. |  |
| 内監委 | the Committee |  | Abbreviation. unsure: alt "IAOC" |  |
| 内監委五人衆, 五人衆 | the Committee Five |  | "The Five". |  |
| キモジ・グループ | Kimoji Group |  | Front company. |  |
| ＢＵＮ | BUN |  | Amusement company bought out. |  |
| ドラゴニア会 | Dragonia Society |  | Gang. unsure: alt "Dragonia Society" |  |
| ＶＯＬＴＳ | VOLTS |  | Ginji's former gang (official). |  |
| ジャンク・キッズ, ジャンクキッズ | Junk Kids |  | Kazuki's Ura-Shinjuku group here. |  |
| アルティメット | the Ultimate |  | Hishiki's former fighting circuit. |  |
| 奪還屋 | retrieval agent |  | GetBackers' trade. unsure: official uses "Retrieval Agency"/"retrievers"; 奪還屋さん -> "Mr. Retrievers" |  |
| 奪還 | retrieval |  | Verb 奪り還す -> take back; 奪還料 retrieval fee; 奪還率 success rate. |  |
| 運び屋 | Transporter |  | Himiko/Akabane trade (official dub). |  |
| 護り屋 | bodyguard |  | Hishiki's trade. unsure: official term |  |
| ＧｅｔＢａｃｋｅｒｓ | GetBackers |  | Official. |  |
| 『奪られたら奪り還せ』 | "If it's taken, take it back!" |  | Motto. unsure: check the official English motto wording |  |
| 悪夢（ユメ）は見れたかよ？, 悪夢（ゆめ）は見れたかい？, いいユメ、見れたかい？ | Enjoy your dream? |  | Ban's line after the Evil Eye, end card, post-game fad. unsure: official line; use one fixed version |  |
| 邪眼 | Evil Eye |  | Ban's power (Jagan); official. |  |
| イービル・アイ | Evil Eye |  | Same (EN in katakana). |  |
| 百獣擬態 | Beast Mimicry |  | Shido's art. |  |
| ビースト・マスター | Beast Master |  | Shido's epithet (official). |  |
| 風鳥院流絃術, 絃術 | Fuchoin-style string art |  | Kazuki's art. unsure: official "Fuchoin String Technique" |  |
| 雷帝 | Lightning Emperor |  | Ginji's awakened form (Raitei). unsure: official rendering |  |
| 雷帝降臨 | Lightning Emperor Descends |  | Ginji skill. |  |
| 雷帝モード | Lightning Emperor Mode |  | Skill effect. |  |
| ＨＯＧ | HOG |  | Hand Of God. |  |
| ＨＡＮＤ　ＯＦ　ＧＯＤ, 神の手 | Hand of God |  | What HOG stands for (revealed step 233). |  |
| 神の記述 | Divine Scripture |  | Legendary power of Asia's people. unsure: alt "Writ of God"/"God's Record" |  |
| 『神の手に近づく東方の若き戦士』 | "the young warriors of the East who draw near the Hand of God" |  | Prophecy part 1. |  |
| 『若き戦士、神の手と交わり、未来への扉を開かん……』 | "The young warriors shall join the Hand of God and open the door to the future..." |  | Prophecy part 2. |  |
| 『東方の栄し地にそれは潜む』 | "It hides in a thriving land of the East" |  | Clue in the family records. |  |
| 道士 | shaman |  | Asia's lineage (HEVN glosses as 巫女/シャーマン). |  |
| プラチナ奪還 | the Platinum job |  | Earlier failed job, mentioned once. |  |
| 電気ウナギ | electric eel |  | Nickname for Ginji. |  |
| サル回し, 猿マワシ | monkey trainer |  | Ban's name for Shido. unsure: official dub insult |  |
| ヤクビョーガミ女 | jinx |  | Ban's name for Hevn. |  |
| ツケ | tab |  | Running joke at HONKY TONK. |  |
| 蛇咬 | Snake Bite |  | Ban skill (official Snake Bite). |  |
| 蛇締 | Snake Squeeze |  | Ban skill. |  |
| 蛇毒 | Snake Venom |  | Ban skill. |  |
| 蛇足 | Snake Legs |  | Ban skill; pun (蛇足 = needless extra). |  |
| 蛇舌 | Snake Tongue |  | Ban skill. |  |
| 蛇睨 | Snake Glare |  | Ban skill. |  |
| 蛇牙 | Snake Fang |  | Ban skill. |  |
| 蛇呑 | Snake Swallow |  | Ban skill. |  |
| プラズマ | Plasma |  | Ginji skill. |  |
| 雷光波 | Lightning Wave |  | Ginji skill. |  |
| 電撃 | Electric Shock |  | Ginji skill. |  |
| 蓄電 | Charge Up |  | Ginji skill. |  |
| 落雷 | Thunderbolt |  | Ginji skill. |  |
| 雷鳴 | Thunderclap |  | Ginji skill. |  |
| 散雷弾 | Scatter Bolt |  | Ginji skill. |  |
| 猫擬 | Cat Mimic |  | Shido skill (百獣擬態 猫擬). |  |
| 猿擬 | Monkey Mimic |  | Shido skill. |  |
| 燕擬 | Swallow Mimic |  | Shido skill. |  |
| 餓狼擬 | Wolf Mimic |  | Shido skill (starving wolf). |  |
| 鹿王擬 | Deer King Mimic |  | Shido skill. |  |
| 狂熊擬 | Mad Bear Mimic |  | Shido skill. |  |
| 獅子王擬 | Lion King Mimic |  | Shido skill. |  |
| 熊猫擬, 熊猫疑 | Panda Mimic |  | Shido skill; 熊猫疑 in learn message is a typo. |  |
| 絃結界 | String Barrier |  | Kazuki skill. |  |
| 絃呪縛 | String Bind |  | Kazuki skill. |  |
| 繭玉の盾 | Cocoon Shield |  | Kazuki skill. |  |
| 流水の刃 | Flowing Blade |  | Kazuki skill. |  |
| 暗禁閉の戒 | Dark Seal |  | Kazuki skill. unsure: reading/meaning |  |
| 降雨の槍 | Rain Spears |  | Kazuki skill. |  |
| 渦潮の陣 | Whirlpool Array |  | Kazuki skill. |  |
| 虚空絃舞 | Void String Dance |  | Kazuki skill. |  |
| 解毒香 | Antidote Perfume |  | Himiko skill. |  |
| 回復香 | Healing Perfume |  | Himiko skill. |  |
| 時限香 | Timer Perfume |  | Himiko skill. unsure: effect name |  |
| 火炎香 | Flame Perfume |  | Himiko skill. |  |
| 極楽香 | Bliss Perfume |  | Himiko skill. |  |
| 加速香 | Haste Perfume |  | Himiko skill. |  |
| 退化香 | Regression Perfume |  | Himiko skill. |  |
| 腐食香 | Corrosion Perfume |  | Himiko skill. |  |
| 赤い雨 | Red Rain |  | Akabane skill. |  |
| 赤い剣 | Red Sword |  | Akabane skill. |  |
| 赤い十字架 | Red Cross |  | Akabane skill. |  |
| 血の契約 | Blood Contract |  | Akabane skill. |  |
| 時限爆弾 | time bomb |  | Sazanami bombs. |  |
| ＨＰ | HP |  | Stat. |  |
| 気力 | Tension |  | Ties to battle label TEN; 気合を溜めます = "Build tension". unsure: check stat in-game |  |
| 攻撃力 | Attack |  | Label ATK. |  |
| 防御力 | Defense |  | Label DEF. |  |
| 素早さ | Speed |  | Label SPD. |  |
| 回避率 | Evasion |  | Label EVD. |  |
| 能力値, 全パラメータ | stats |  | 能力値復帰 = restore stats; 全パラメータダウン = all stats down. |  |
| 毒 | Poison |  | Status. |  |
| マヒ | Paralysis |  | Status. |  |
| 混乱 | Confusion |  | Status. |  |
| 眠り | Sleep |  | Status. |  |
| 即死 | instant death |  | Attack property. |  |
| ステータス異常 | status ailments |  | Skill description. |  |
| 戦闘不能 | KO |  | "戦闘不能から全快復帰" = revive from KO at full HP. |  |
| 瀕死 | near death |  | "瀕死で復帰" = revive with low HP. |  |
| 結界 | barrier |  | "防御力アップ＋結界" = Defense up + barrier. |  |
| 後列可 | hits back row |  | Skill description tag. |  |
| 相性 | Affinity |  | Pause-menu label already AFFINITY. |  |
| 特殊技 | Special Skills |  | Menu. |  |
| 特殊攻撃 | Special Attack |  | Battle command help. |  |
| 経験値 | EXP |  | "の経験値を得た" = gained EXP. |  |
| レベルアップ | Level Up |  | "%sがレベルアップ！" |  |
| セーブ | Save |  | Save menu. |  |
| ボーナスステージ | Bonus Stage |  | Title BONUS mode. |  |
| 負けたボス戦をもう一度だけ戦います | Refight a lost boss battle once |  | REVENGE mode help. |  |
| 少年マガジン | Weekly Shonen Magazine |  | Running joke (always sold out); GetBackers' magazine. |  |
| マガジン | Magazine |  | Running joke (always sold out); GetBackers' magazine. |  |
| 開発中！ | Under development! |  | Debug leftover strings. |  |

## Decisions from earlier batches
- all: US spelling. Scaramouche ungendered (no he/she, no "sir") before step 235; "she" after.
- all: Ginji -> Yamamura オッチャン = "Pops"; Ban says "old man". 奪還率 = "success rate".
- all: generic labels (notes "Label") are not names: お客様/お爺さん/駅員さん take no honorific (customer, Grandpa).
- b001: enemy letter series follow the A row (Agent B-E, Agent A'/B'/C', Scary Dude B-D, Junk Kid B/C, Manji
  Brother B); Electronic Key B-E; Staff ID Card 2/3; Zagad forms: Second Form / Third Form - B Mode / Fourth Form -
  B Mode / Final Form - F Mode; インディゴ君 Indigo-kun, ソリッド君 Solid-kun; 裏新宿爆走隊 Ura-Shinjuku Speed Squad.
- b001: α（アルファ） 0x2F0E0 = "Alpha" (the α is a letter there, not {br}). 赤毛の鬼神 = "The red-haired demon".
- b005: ドラゴニア会 in text = "Dragonia Society" (speaker label "Dragonia Member"); ジェッカー Jecker; クリちゃん Kuri-chan.
- b013: ペスちゃん = Pesu-chan (Hepburn); ゲッシ印 Gnaw-Brand; 裏都庁総務部/会計部 Ura-Tocho General Affairs / Accounting
  Department.
- b021: マドカお嬢様 Miss Madoka; Paro (parrot) speaks in ALL CAPS broken English.
- b029: 兄上 = Brother (Mitate to Masurao); カヅっちゃん Kazu-chan; 遊びの時間は終わり = "Playtime is over."
- b033: クス (Akabane's giggle) = "Heh."; いい悪夢（ゆめ）見れたかよ = the fixed "Enjoy your dream?".
