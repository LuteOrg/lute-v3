PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "_migrations" (
	"filename" VARCHAR(255) NOT NULL  ,
	PRIMARY KEY ("filename")
);
INSERT INTO _migrations VALUES('20230409_224327_load_statuses.sql');
INSERT INTO _migrations VALUES('20230414_225828_add_texttokens_TokTextLC.sql');
INSERT INTO _migrations VALUES('20230428_224656_create_wordflashmessages_table.sql');
INSERT INTO _migrations VALUES('20230518_190000_remove_old_words_fields.sql');
INSERT INTO _migrations VALUES('20230519_194627_add_TxDateRead.sql');
INSERT INTO _migrations VALUES('20230621_010000_drop_texttags_table.sql');
INSERT INTO _migrations VALUES('20230621_224416_fk_01_booktags.sql');
INSERT INTO _migrations VALUES('20230621_224416_fk_02_wordtags.sql');
INSERT INTO _migrations VALUES('20230621_224416_fk_03_sentences.sql');
INSERT INTO _migrations VALUES('20230621_224416_fk_04_texttokens.sql');
INSERT INTO _migrations VALUES('20230621_224416_fk_05_texts.sql');
INSERT INTO _migrations VALUES('20230621_224416_fk_06_bookstats.sql');
INSERT INTO _migrations VALUES('20230621_224416_fk_07_termimages.sql');
INSERT INTO _migrations VALUES('20230621_224416_fk_08_wordflashmessages.sql');
INSERT INTO _migrations VALUES('20230621_224416_fk_09_wordparents.sql');
INSERT INTO _migrations VALUES('20230621_224416_fk_10_words.sql');
INSERT INTO _migrations VALUES('20230621_224416_fk_11_books.sql');
INSERT INTO _migrations VALUES('20230623_234104_drop_TxTitle.sql');
INSERT INTO _migrations VALUES('20230624_182104_drop_index_TxBkIDTxOrder.sql');
INSERT INTO _migrations VALUES('20230818_201200_add_BkWordCount.sql');
INSERT INTO _migrations VALUES('20230819_044107_drop_texttokens.sql');
INSERT INTO _migrations VALUES('20230819_050036_vacuum.sql');
INSERT INTO _migrations VALUES('20230827_052154_allow_multiple_word_parents.sql');
CREATE TABLE IF NOT EXISTS "languages" (
	"LgID" INTEGER NOT NULL  ,
	"LgName" VARCHAR(40) NOT NULL  ,
	"LgDict1URI" VARCHAR(200) NOT NULL  ,
	"LgDict2URI" VARCHAR(200) NULL  ,
	"LgGoogleTranslateURI" VARCHAR(200) NULL  ,
	"LgCharacterSubstitutions" VARCHAR(500) NOT NULL  ,
	"LgRegexpSplitSentences" VARCHAR(500) NOT NULL  ,
	"LgExceptionsSplitSentences" VARCHAR(500) NOT NULL  ,
	"LgRegexpWordCharacters" VARCHAR(500) NOT NULL  ,
	"LgRemoveSpaces" TINYINT NOT NULL  ,
	"LgSplitEachChar" TINYINT NOT NULL  ,
	"LgRightToLeft" TINYINT NOT NULL  ,
	"LgShowRomanization" TINYINT NOT NULL DEFAULT '0' ,
	"LgParserType" VARCHAR(20) NOT NULL DEFAULT 'spacedel' ,
	PRIMARY KEY ("LgID")
);
INSERT INTO languages VALUES(1,'English','https://en.thefreedictionary.com/###','https://www.bing.com/images/search?q=###&form=HDRSC2&first=1&tsc=ImageHoverTitle','*https://www.deepl.com/translator#en/en/###','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','a-zA-ZÀ-ÖØ-öø-ȳáéíóúÁÉÍÓÚñÑ',0,0,0,0,'spacedel');
INSERT INTO languages VALUES(2,'French','https://fr.thefreedictionary.com/###','https://www.bing.com/images/search?q=###&form=HDRSC2&first=1&tsc=ImageHoverTitle','*https://www.deepl.com/translator#fr/en/###','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','a-zA-ZÀ-ÖØ-öø-ȳáéíóúÁÉÍÓÚñÑ',0,0,0,0,'spacedel');
INSERT INTO languages VALUES(3,'Spanish','https://es.thefreedictionary.com/###','https://www.bing.com/images/search?q=###&form=HDRSC2&first=1&tsc=ImageHoverTitle','*https://www.deepl.com/translator#es/en/###','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','a-zA-ZÀ-ÖØ-öø-ȳáéíóúÁÉÍÓÚñÑ',0,0,0,0,'spacedel');
INSERT INTO languages VALUES(4,'German','https://de.thefreedictionary.com/###','https://www.wordreference.com/deen/###','*https://www.deepl.com/translator#de/en/###','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','a-zA-ZÀ-ÖØ-öø-ȳáéíóúÁÉÍÓÚñÑ',0,0,0,0,'spacedel');
INSERT INTO languages VALUES(5,'Greek','https://www.wordreference.com/gren/###','https://en.wiktionary.org/wiki/###','*https://www.deepl.com/translator#el/en/###','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','a-zA-ZÀ-ÖØ-öø-ȳͰ-Ͽἀ-ῼ',0,0,0,1,'spacedel');
INSERT INTO languages VALUES(6,'Classical Chinese','https://ctext.org/dictionary.pl?if=en&char=###','https://www.bing.com/images/search?q=###&form=HDRSC2&first=1&tsc=ImageHoverTitle','*https://www.deepl.com/translator#ch/en/###','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?。！？','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','一-龥',1,0,0,1,'classicalchinese');
INSERT INTO languages VALUES(7,'Arabic','https://www.arabicstudentsdictionary.com/search?q=###','*https://translate.google.com/?hl=es&sl=ar&tl=en&text=###&op=translate','*https://translate.google.com/?hl=es&sl=ar&tl=en&text=###','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?؟۔‎','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','\x{0600}-\x{06FF}\x{FE70}-\x{FEFC}',0,0,1,0,'spacedel');
INSERT INTO languages VALUES(8,'Japanese','https://jisho.org/search/###','https://www.bing.com/images/search?q=###&form=HDRSC2&first=1&tsc=ImageHoverTitle','*https://www.deepl.com/translator#jp/en/###','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?。？！','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','\p{Han}\p{Katakana}\p{Hiragana}',1,0,0,1,'japanese');
CREATE TABLE IF NOT EXISTS "settings" (
	"StKey" VARCHAR(40) NOT NULL  ,
	"StValue" VARCHAR(40) NULL  ,
	PRIMARY KEY ("StKey")
);
CREATE TABLE IF NOT EXISTS "statuses" (
	"StID" INTEGER NOT NULL  ,
	"StText" VARCHAR(20) NOT NULL  ,
	"StAbbreviation" VARCHAR(5) NOT NULL  ,
	PRIMARY KEY ("StID")
);
INSERT INTO statuses VALUES(0,'Unknown','?');
INSERT INTO statuses VALUES(1,'New (1)','1');
INSERT INTO statuses VALUES(2,'New (2)','2');
INSERT INTO statuses VALUES(3,'Learning (3)','3');
INSERT INTO statuses VALUES(4,'Learning (4)','4');
INSERT INTO statuses VALUES(5,'Learned','5');
INSERT INTO statuses VALUES(98,'Ignored','Ign');
INSERT INTO statuses VALUES(99,'Well Known','WKn');
CREATE TABLE IF NOT EXISTS "tags" (
	"TgID" INTEGER NOT NULL  ,
	"TgText" VARCHAR(20) NOT NULL  ,
	"TgComment" VARCHAR(200) NOT NULL DEFAULT '' ,
	PRIMARY KEY ("TgID")
);
CREATE TABLE IF NOT EXISTS "tags2" (
	"T2ID" INTEGER NOT NULL  ,
	"T2Text" VARCHAR(20) NOT NULL  ,
	"T2Comment" VARCHAR(200) NOT NULL DEFAULT '' ,
	PRIMARY KEY ("T2ID")
);
CREATE TABLE IF NOT EXISTS "booktags" (
	"BtBkID" INTEGER NOT NULL  ,
	"BtT2ID" INTEGER NOT NULL  ,
	PRIMARY KEY ("BtBkID", "BtT2ID"),
	FOREIGN KEY("BtT2ID") REFERENCES "tags2" ("T2ID") ON UPDATE NO ACTION ON DELETE CASCADE,
	FOREIGN KEY("BtBkID") REFERENCES "books" ("BkID") ON UPDATE NO ACTION ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "wordtags" (
	"WtWoID" INTEGER NOT NULL  ,
	"WtTgID" INTEGER NOT NULL  ,
	PRIMARY KEY ("WtWoID", "WtTgID"),
	FOREIGN KEY("WtWoID") REFERENCES "words" ("WoID") ON UPDATE NO ACTION ON DELETE CASCADE,
	FOREIGN KEY("WtTgID") REFERENCES "tags" ("TgID") ON UPDATE NO ACTION ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "sentences" (
	"SeID" INTEGER NOT NULL  ,
	"SeTxID" INTEGER NOT NULL  ,
	"SeOrder" SMALLINT NOT NULL  ,
	"SeText" TEXT NULL  ,
	PRIMARY KEY ("SeID"),
	FOREIGN KEY("SeTxID") REFERENCES "texts" ("TxID") ON UPDATE NO ACTION ON DELETE CASCADE
);
INSERT INTO sentences VALUES(1,1,1,'​Welcome​ ​to​ ​Lute​!​');
INSERT INTO sentences VALUES(2,1,2,'​This​ ​short​ ​guide​ ​should​ ​get​ ​you​ ​going​.​');
INSERT INTO sentences VALUES(3,1,3,'​¶​');
INSERT INTO sentences VALUES(4,1,4,'​¶​');
INSERT INTO sentences VALUES(5,1,5,'​Navigation​¶​');
INSERT INTO sentences VALUES(6,1,6,'​¶​');
INSERT INTO sentences VALUES(7,1,7,'​This​ ​tutorial​ ​has​ ​multiple​ ​pages​.​');
INSERT INTO sentences VALUES(8,1,8,'​Above​ ​the​ ​title​ ​are​ ​some​ ​arrows​ ​to​ ​navigate​ ​forwards​ ​and​ ​backwards​.​');
INSERT INTO sentences VALUES(9,1,9,'​In​ ​longer​ ​texts​, ​you​ ​can​ ​jump​ ​forward​ ​or​ ​back​ ​ten​ ​pages​ ​at​ ​a​ ​time​ ​as​ ​well​.​');
INSERT INTO sentences VALUES(10,1,10,'​¶​');
INSERT INTO sentences VALUES(11,1,11,'​¶​');
INSERT INTO sentences VALUES(12,1,12,'​1.​');
INSERT INTO sentences VALUES(13,1,13,'​The​ ​Basics​¶​');
INSERT INTO sentences VALUES(14,1,14,'​¶​');
INSERT INTO sentences VALUES(15,1,15,'​All​ ​of​ ​these​ ​words​ ​are​ ​blue​ ​because​ ​they​ ​are​ "​unknown​" - ​according​ ​to​ ​Lute​, ​this​ ​is​ ​the​ ​first​ ​time​ ​you​''​re​ ​seeing​ ​these​ ​words​.​');
INSERT INTO sentences VALUES(16,1,16,'​¶​');
INSERT INTO sentences VALUES(17,1,17,'​¶​');
INSERT INTO sentences VALUES(18,1,18,'​You​ ​can​ ​click​ ​on​ ​a​ ​word​, ​and​ ​create​ ​a​ ​definition​.​');
INSERT INTO sentences VALUES(19,1,19,'​For​ ​example​, ​click​ ​on​ ​this​ ​word​: ​elephant​.​');
INSERT INTO sentences VALUES(20,1,20,'​¶​');
INSERT INTO sentences VALUES(21,1,21,'​¶​');
INSERT INTO sentences VALUES(22,1,22,'​When​ ​the​ ​form​ ​pops​ ​up​ ​in​ ​the​ ​right​-​hand​ ​frame​, ​a​ ​dictionary​ ​is​ ​loaded​ ​below​.​');
INSERT INTO sentences VALUES(23,1,23,'​Copy​-​paste​ ​something​ ​from​ ​the​ ​dictionary​ ​into​ ​the​ ​translation​, ​or​ ​make​ ​up​ ​your​ ​own​, ​mark​ ​the​ ​status​, ​add​ ​some​ ​tags​ ​if​ ​you​ ​want​ (​eg​, ​type​ "​noun​" ​in​ ​the​ ​tags​ ​field​), ​and​ ​click​ ​save​.​');
INSERT INTO sentences VALUES(24,1,24,'​From​ ​now​ ​on​, ​every​ ​English​ ​text​ ​that​ ​you​ ​read​ ​that​ ​contains​ ​the​ ​word​ "​elephant​" ​will​ ​show​ ​the​ ​status​.​');
INSERT INTO sentences VALUES(25,1,25,'​If​ ​you​ ​hover​ ​over​ ​any​ "​elephant​", ​you​''​ll​ ​see​ ​some​ ​information​.​');
INSERT INTO sentences VALUES(26,1,26,'​¶​');
INSERT INTO sentences VALUES(27,1,27,'​¶​');
INSERT INTO sentences VALUES(28,1,28,'​1.1​');
INSERT INTO sentences VALUES(29,1,29,'​Multiple​ ​dictionaries​.​');
INSERT INTO sentences VALUES(30,1,30,'​¶​');
INSERT INTO sentences VALUES(31,1,31,'​¶​');
INSERT INTO sentences VALUES(32,1,32,'​Next​ ​to​ ​the​ ​term​ ​is​ ​a​ ​small​ ​arrow​, "​Lookup​".​');
INSERT INTO sentences VALUES(33,1,33,'​If​ ​you​ ​click​ ​on​ ​this​ ​repeatedly​, ​Lute​ ​cycles​ ​through​ ​the​ ​dictionaries​ ​that​ ​you​ ​configure​ ​for​ ​the​ ​language​ ​in​ ​the​ "​Languages​" ​link​ ​on​ ​the​ ​homepage​.​');
INSERT INTO sentences VALUES(34,1,34,'​¶​');
INSERT INTO sentences VALUES(35,1,35,'​¶​');
INSERT INTO sentences VALUES(36,1,36,'​1.2​');
INSERT INTO sentences VALUES(37,1,37,'​Images​¶​');
INSERT INTO sentences VALUES(38,1,38,'​¶​');
INSERT INTO sentences VALUES(39,1,39,'​For​ ​this​ ​demo​, ​English​ ​has​ ​been​ ​configured​ ​to​ ​do​ ​an​ ​image​ ​search​ ​for​ ​the​ ​second​ ​English​ ​dictinary​, ​so​ ​if​ ​you​ ​click​ ​on​ ​the​ ​arrow​, ​you​''​ll​ ​see​ ​some​ ​happy​ ​elephants​ (​if​ ​you​ ​clicked​ ​on​ ​elephant​!).​');
INSERT INTO sentences VALUES(40,2,1,'​You​ ​can​ ​also​ ​click​ ​on​ ​the​ ​little​ "​eye​ ​icon​" ​next​ ​to​ ​the​ ​term​, ​and​ ​it​ ​opens​ ​up​ ​a​ ​common​ ​image​ ​search​ ​URL​.​');
INSERT INTO sentences VALUES(41,2,2,'​¶​');
INSERT INTO sentences VALUES(42,2,3,'​¶​');
INSERT INTO sentences VALUES(43,2,4,'​In​ ​either​ ​case​, ​if​ ​you​ ​click​ ​on​ ​one​ ​of​ ​the​ ​images​ ​shown​ ​in​ ​the​ ​list​, ​that​ ​image​ ​is​ ​saved​ ​in​ ​your​ ​public​/​media​/​images​ ​folder​.​');
INSERT INTO sentences VALUES(44,2,5,'​When​ ​you​ ​hover​ ​over​ ​the​ ​word​ ​in​ ​the​ ​reading​ ​pane​, ​that​ ​picture​ ​is​ ​included​ ​in​ ​the​ ​word​ ​hover​.​');
INSERT INTO sentences VALUES(45,2,6,'​Try​ ​adding​ ​an​ ​image​ ​for​ ​your​ ​elephant​ ​by​ ​clicking​ ​on​ ​the​ ​term​, ​clicking​ ​the​ ​eye​ ​icon​, ​and​ ​clicking​ ​a​ ​picture​ ​you​ ​like​.​');
INSERT INTO sentences VALUES(46,2,7,'​Then​ ​hover​ ​over​ ​your​ ​elephant​.​');
INSERT INTO sentences VALUES(47,2,8,'​¶​');
INSERT INTO sentences VALUES(48,2,9,'​¶​');
INSERT INTO sentences VALUES(49,2,10,'​Note​: ​sometimes​ ​these​ ​images​ ​make​ _​no​ ​sense​_ -- ​it​''​s​ ​using​ ​Bing​ ​image​ ​search​, ​and​ ​it​ ​does​ ​the​ ​best​ ​it​ ​can​ ​with​ ​the​ ​limited​ ​context​ ​it​ ​has​.​');
INSERT INTO sentences VALUES(50,2,11,'​¶​');
INSERT INTO sentences VALUES(51,2,12,'​¶​');
INSERT INTO sentences VALUES(52,2,13,'​2.​');
INSERT INTO sentences VALUES(53,2,14,'​Multi​-​word​ ​Terms​¶​');
INSERT INTO sentences VALUES(54,2,15,'​¶​');
INSERT INTO sentences VALUES(55,2,16,'​You​ ​can​ ​create​ ​multi​-​word​ ​terms​ ​by​ ​clicking​ ​and​ ​dragging​ ​across​ ​multiple​ ​words​, ​then​ ​release​ ​the​ ​mouse​.​');
INSERT INTO sentences VALUES(56,2,17,'​Try​ ​creating​ ​a​ ​term​ ​for​ ​the​ ​phrase​ "​the​ ​cat​''​s​ ​pyjamas​", ​and​ ​add​ ​a​ ​translation​ ​and​ ​set​ ​the​ ​status​.​');
INSERT INTO sentences VALUES(57,2,18,'​¶​');
INSERT INTO sentences VALUES(58,2,19,'​¶​');
INSERT INTO sentences VALUES(59,2,20,'​(​A​ ​brief​ ​side​ ​note​: ​Lute​ ​keeps​ ​track​ ​of​ ​where​ ​you​ ​are​ ​in​ ​any​ ​text​.​');
INSERT INTO sentences VALUES(60,2,21,'​If​ ​you​ ​click​ ​the​ ​Home​ ​link​ ​above​ ​to​ ​leave​ ​this​ ​tutorial​, ​and​ ​later​ ​click​ ​the​ ​Tutorial​ ​link​ ​from​ ​the​ ​Text​ ​listing​, ​Lute​ ​will​ ​open​ ​the​ ​last​ ​page​ ​you​ ​were​ ​at​.)​');
INSERT INTO sentences VALUES(61,2,22,'​¶​');
INSERT INTO sentences VALUES(62,2,23,'​¶​');
INSERT INTO sentences VALUES(63,2,24,'​3.​');
INSERT INTO sentences VALUES(64,2,25,'​Parent​ ​Terms​¶​');
INSERT INTO sentences VALUES(65,2,26,'​¶​');
INSERT INTO sentences VALUES(66,2,27,'​Sometimes​ ​it​ ​helps​ ​to​ ​associate​ ​terms​ ​with​ ​a​ "​parent​".​');
INSERT INTO sentences VALUES(67,2,28,'​For​ ​example​, ​the​ ​verb​ "​to​ ​have​" ​is​ ​conjugated​ ​in​ ​various​ ​forms​ ​as​ "​I​ ​have​ ​a​ ​cold​", "​he​ ​has​ ​a​ ​dog​", "​they​ ​had​ ​dinner​".​');
INSERT INTO sentences VALUES(68,2,29,'​First​ ​create​ ​a​ ​Term​ ​for​ "​have​".​');
INSERT INTO sentences VALUES(69,3,1,'​Then​ ​create​ ​a​ ​Term​ ​for​ "​has​", ​and​ ​in​ ​the​ ​Parent​ ​field​ ​start​ ​typing​ "​have​".​');
INSERT INTO sentences VALUES(70,3,2,'​Lute​ ​will​ ​show​ ​the​ ​existing​ ​Term​ "​have​" ​in​ ​the​ ​drop​ ​down​, ​and​ ​if​ ​you​ ​select​ ​it​, "​has​" ​will​ ​be​ ​associated​ ​with​ ​that​ ​on​ ​save​, ​and​ ​when​ ​you​ ​hover​ ​over​ "​has​" ​you​''​ll​ ​see​ ​the​ ​parent​''​s​ ​information​ ​as​ ​well​.​');
INSERT INTO sentences VALUES(71,3,3,'​¶​');
INSERT INTO sentences VALUES(72,3,4,'​¶​');
INSERT INTO sentences VALUES(73,3,5,'​If​ ​you​ ​enter​ ​a​ ​non​-​existent​ ​Parent​ ​word​, ​Lute​ ​will​ ​create​ ​a​ ​placeholder​ ​Term​ ​for​ ​that​ ​Parent​, ​copying​ ​some​ ​content​ ​from​ ​your​ ​term​.​');
INSERT INTO sentences VALUES(74,3,6,'​For​ ​example​, ​try​ ​creating​ ​a​ ​Term​ ​for​ ​the​ ​word​ "​dogs​", ​associating​ ​it​ ​with​ ​the​ ​non​-​existent​ ​Term​ "​dog​".​');
INSERT INTO sentences VALUES(75,3,7,'​When​ ​you​ ​save​ "​dogs​", ​both​ ​will​ ​be​ ​updated​.​');
INSERT INTO sentences VALUES(76,3,8,'​¶​');
INSERT INTO sentences VALUES(77,3,9,'​¶​');
INSERT INTO sentences VALUES(78,3,10,'​Terms​ ​can​ ​have​ ​multiple​ ​parents​, ​too​.​');
INSERT INTO sentences VALUES(79,3,11,'​Hit​ ​the​ ​Enter​ (​or​ ​Return​) ​key​ ​after​ ​each​ ​parent​.​');
INSERT INTO sentences VALUES(80,3,12,'​For​ ​example​, ​if​ ​you​ ​wanted​ ​to​ ​associate​ ​the​ ​Term​ "​puppies​" ​with​ ​both​ "​puppy​" ​and​ "​dog​", ​click​ ​on​ "​puppies​", ​and​ ​in​ ​the​ ​Parents​ ​text​ ​box​ ​type​ "​puppy​", ​hit​ ​Enter​, ​type​ "​dog​", ​and​ ​hit​ ​Enter​.​');
INSERT INTO sentences VALUES(81,3,13,'​Sometimes​ ​this​ ​is​ ​necessary​: ​for​ ​example​, ​in​ ​Spanish​, "​se​ ​sienta​" ​can​ ​either​ ​be​ ​a​ ​conjugation​ ​of​ "​sentirse​" (​to​ ​feel​) ​or​ "​sentarse​" (​to​ ​sit​), ​depending​ ​on​ ​the​ ​context​.​');
INSERT INTO sentences VALUES(82,3,14,'​¶​');
INSERT INTO sentences VALUES(83,3,15,'​¶​');
INSERT INTO sentences VALUES(84,3,16,'​4.​');
INSERT INTO sentences VALUES(85,3,17,'​Mark​ ​the​ ​remainder​ ​as​ "​Well​ ​Known​"​¶​');
INSERT INTO sentences VALUES(86,3,18,'​¶​');
INSERT INTO sentences VALUES(87,3,19,'​When​ ​you​''​re​ ​done​ ​creating​ ​Terms​ ​on​ ​a​ ​page​, ​you​ ​will​ ​likely​ ​still​ ​have​ ​a​ ​bunch​ ​of​ ​blue​ ​words​, ​or​ "​unknowns​", ​left​ ​over​, ​even​ ​though​ ​you​ ​really​ ​know​ ​these​ ​words​.​');
INSERT INTO sentences VALUES(88,3,20,'​You​ ​can​ ​set​ ​all​ ​of​ ​these​ ​to​ "​Well​ ​Known​" ​in​ ​one​ ​shot​ ​with​ ​the​ ​green​ ​checkmark​ ​at​ ​the​ ​bottom​ ​of​ ​the​ ​page​ ("​Mark​ ​rest​ ​as​ ​known​").​');
INSERT INTO sentences VALUES(89,3,21,'​Try​ ​that​ ​now​ ​to​ ​see​ ​what​ ​happens​.​');
INSERT INTO sentences VALUES(90,4,1,'​This​ ​button​ ​only​ ​affects​ ​words​ ​on​ ​the​ ​current​ ​page​, ​so​ ​when​ ​you​ ​go​ ​to​ ​the​ ​next​ ​page​, ​you​''​ll​ ​see​ ​that​ ​some​ ​words​ ​are​ ​still​ ​unknown​.​');
INSERT INTO sentences VALUES(91,4,2,'​¶​');
INSERT INTO sentences VALUES(92,4,3,'​¶​');
INSERT INTO sentences VALUES(93,4,4,'​There​ ​are​ ​other​ ​buttons​ ​at​ ​the​ ​bottom​ ​of​ ​the​ ​page​.​');
INSERT INTO sentences VALUES(94,4,5,'​The​ ​green​ ​checkmark​ ​with​ ​the​ ​arrow​ ​sets​ ​the​ ​remaining​ ​unknowns​ ​on​ ​the​ ​current​ ​page​, ​and​ ​also​ ​goes​ ​to​ ​the​ ​next​ ​page​.​');
INSERT INTO sentences VALUES(95,4,6,'​¶​');
INSERT INTO sentences VALUES(96,4,7,'​¶​');
INSERT INTO sentences VALUES(97,4,8,'​5.​');
INSERT INTO sentences VALUES(98,4,9,'​Keyboard​ ​shortcuts​¶​');
INSERT INTO sentences VALUES(99,4,10,'​¶​');
INSERT INTO sentences VALUES(100,4,11,'​The​ ​small​ ​blue​ ​question​ ​mark​ ​in​ ​the​ ​header​ ​shows​ ​some​ ​keyboard​ ​shortcuts​.​');
INSERT INTO sentences VALUES(101,4,12,'​¶​');
INSERT INTO sentences VALUES(102,4,13,'​¶​');
INSERT INTO sentences VALUES(103,4,14,'​5.1​');
INSERT INTO sentences VALUES(104,4,15,'​Updating​ ​Status​¶​');
INSERT INTO sentences VALUES(105,4,16,'​¶​');
INSERT INTO sentences VALUES(106,4,17,'​If​ ​you​''​ve​ ​worked​ ​through​ ​the​ ​tutorial​, ​you​''​ll​ ​have​ ​noted​ ​that​ ​words​ ​are​ ​underlined​ ​in​ ​blue​ ​when​ ​you​ ​move​ ​the​ ​mouse​ ​over​ ​them​.​');
INSERT INTO sentences VALUES(107,4,18,'​You​ ​can​ ​quickly​ ​change​ ​the​ ​status​ ​of​ ​the​ ​current​ ​word​ ​by​ ​hitting​ 1, 2, 3, 4, 5, ​w​ (​for​ ​Well​-​Known​), ​or​ ​i​ (​for​ ​Ignore​).​');
INSERT INTO sentences VALUES(108,4,19,'​Try​ ​hovering​ ​over​ ​the​ ​following​ ​words​ ​and​ ​hit​ ​the​ ​status​ ​buttons​: ​apple​, ​banana​, ​cranberry​, ​donut​.​');
INSERT INTO sentences VALUES(109,4,20,'​¶​');
INSERT INTO sentences VALUES(110,4,21,'​¶​');
INSERT INTO sentences VALUES(111,4,22,'​If​ ​you​ ​click​ ​on​ ​a​ ​word​, ​it​''​s​ ​underlined​ ​in​ ​red​, ​and​ ​the​ ​Term​ ​edit​ ​form​ ​is​ ​shown​. (​');
INSERT INTO sentences VALUES(112,4,23,'​Before​ ​you​ ​switch​ ​over​ ​to​ ​the​ ​Term​ ​editing​ ​form​, ​you​ ​can​ ​still​ ​update​ ​its​ ​status​.)​');
INSERT INTO sentences VALUES(113,4,24,'​You​ ​can​ ​jump​ ​over​ ​to​ ​the​ ​edit​ ​form​ ​by​ ​hitting​ ​Tab​, ​and​ ​then​ ​start​ ​editing​.​');
INSERT INTO sentences VALUES(114,4,25,'​¶​');
INSERT INTO sentences VALUES(115,4,26,'​¶​');
INSERT INTO sentences VALUES(116,4,27,'​When​ ​a​ ​word​ ​has​ ​been​ ​clicked​, ​it​''​s​ "​active​", ​so​ ​it​ ​keeps​ ​the​ ​focus​.​');
INSERT INTO sentences VALUES(117,4,28,'​Hovering​ ​the​ ​mouse​ ​over​ ​other​ ​words​ ​won​''​t​ ​underline​ ​them​ ​in​ ​blue​ ​anymore​, ​and​ ​hitting​ ​status​ ​update​ ​hotkeys​ (1 - 5, ​w​, ​i​) ​will​ ​only​ ​update​ ​the​ ​active​ ​word​.​');
INSERT INTO sentences VALUES(118,4,29,'​To​ "​un​-​click​" ​a​ ​word​ ​underlined​ ​in​ ​red​, ​click​ ​it​ ​again​, ​or​ ​hit​ ​Escape​ ​or​ ​Return​.​');
INSERT INTO sentences VALUES(119,4,30,'​Then​ ​you​''​ll​ ​be​ ​back​ ​in​ "​Hover​ ​mode​".​');
INSERT INTO sentences VALUES(120,5,1,'​Try​ ​clicking​ ​and​ ​un​-​clicking​ ​or​ ​Escaping​ ​any​ ​word​ ​in​ ​this​ ​paragraph​ ​to​ ​get​ ​a​ ​feel​ ​for​ ​it​.​');
INSERT INTO sentences VALUES(121,5,2,'​¶​');
INSERT INTO sentences VALUES(122,5,3,'​¶​');
INSERT INTO sentences VALUES(123,5,4,'​Note​ ​that​ ​for​ ​the​ ​keyboard​ ​shortcuts​ ​to​ ​work​, ​the​ ​reading​ ​pane​ (​where​ ​the​ ​text​ ​is​) ​must​ ​have​ ​the​ "​focus​".​');
INSERT INTO sentences VALUES(124,5,5,'​Click​ ​anywhere​ ​on​ ​the​ ​reading​ ​pane​ ​to​ ​re​-​establish​ ​focus​.​');
INSERT INTO sentences VALUES(125,5,6,'​¶​');
INSERT INTO sentences VALUES(126,5,7,'​¶​');
INSERT INTO sentences VALUES(127,5,8,'​5.1​');
INSERT INTO sentences VALUES(128,5,9,'​Bulk​ ​updates​¶​');
INSERT INTO sentences VALUES(129,5,10,'​¶​');
INSERT INTO sentences VALUES(130,5,11,'​If​ ​you​ ​hold​ ​down​ ​Shift​ ​and​ ​click​ ​a​ ​bunch​ ​of​ ​words​, ​you​ ​can​ ​bulk​ ​update​ ​their​ ​statuses​.​');
INSERT INTO sentences VALUES(131,5,12,'​¶​');
INSERT INTO sentences VALUES(132,5,13,'​¶​');
INSERT INTO sentences VALUES(133,5,14,'​5.2​');
INSERT INTO sentences VALUES(134,5,15,'​Arrow​ ​keys​¶​');
INSERT INTO sentences VALUES(135,5,16,'​¶​');
INSERT INTO sentences VALUES(136,5,17,'​The​ ​Right​ ​and​ ​Left​ ​arrow​ ​keys​ ​click​ ​the​ ​next​ ​and​ ​previous​ ​words​.​');
INSERT INTO sentences VALUES(137,5,18,'​Hit​ ​Escape​ ​or​ ​Return​ ​to​ ​get​ ​back​ ​to​ "​hover​ ​mode​".​');
INSERT INTO sentences VALUES(138,5,19,'​¶​');
INSERT INTO sentences VALUES(139,5,20,'​¶​');
INSERT INTO sentences VALUES(140,5,21,'​5.3​');
INSERT INTO sentences VALUES(141,5,22,'​Copying​ ​text​¶​');
INSERT INTO sentences VALUES(142,5,23,'​¶​');
INSERT INTO sentences VALUES(143,5,24,'​When​ ​a​ ​word​ ​is​ ​hovered​ ​over​ ​or​ ​clicked​, ​hit​ "​c​" ​to​ ​copy​ ​that​ ​word​''​s​ ​sentence​ ​to​ ​your​ ​clipboard​.​');
INSERT INTO sentences VALUES(144,5,25,'​Hit​ "​C​" ​to​ ​copy​ ​the​ ​word​''​s​ ​full​ ​paragraph​ (​multiple​ ​sentences​).​');
INSERT INTO sentences VALUES(145,5,26,'​You​ ​can​ ​also​ ​copy​ ​arbitrary​ ​sections​ ​of​ ​text​ ​by​ ​holding​ ​down​ ​the​ ​Shift​ ​key​ ​while​ ​highlighting​ ​the​ ​text​ ​with​ ​your​ ​mouse​.​');
INSERT INTO sentences VALUES(146,5,27,'​¶​');
INSERT INTO sentences VALUES(147,5,28,'​¶​');
INSERT INTO sentences VALUES(148,5,29,'​6.​');
INSERT INTO sentences VALUES(149,5,30,'​Next​ ​steps​¶​');
INSERT INTO sentences VALUES(150,5,31,'​¶​');
INSERT INTO sentences VALUES(151,5,32,'​All​ ​done​ ​this​ ​text​!​');
INSERT INTO sentences VALUES(152,5,33,'​¶​');
INSERT INTO sentences VALUES(153,5,34,'​¶​');
INSERT INTO sentences VALUES(154,5,35,'​Lute​ ​keeps​ ​track​ ​of​ ​all​ ​of​ ​this​ ​in​ ​your​ ​database​, ​so​ ​any​ ​time​ ​you​ ​create​ ​or​ ​import​ ​a​ ​new​ ​Book​, ​all​ ​the​ ​info​ ​you​''​ve​ ​created​ ​is​ ​carried​ ​forward​.​');
INSERT INTO sentences VALUES(155,5,36,'​¶​');
INSERT INTO sentences VALUES(156,5,37,'​¶​');
INSERT INTO sentences VALUES(157,5,38,'​There​''​s​ ​a​ ​tutorial​ ​follow​-​up​: ​go​ ​to​ ​the​ ​Home​ ​screen​, ​and​ ​click​ ​the​ "​Tutorial​ ​follow​-​up​" ​in​ ​the​ ​table​.​');
INSERT INTO sentences VALUES(158,6,1,'​Hopefully​ ​you​''​ve​ ​gone​ ​through​ ​the​ ​Tutorial​, ​and​ ​created​ ​some​ ​Terms​.​');
INSERT INTO sentences VALUES(159,6,2,'​¶​');
INSERT INTO sentences VALUES(160,6,3,'​¶​');
INSERT INTO sentences VALUES(161,6,4,'​From​ ​the​ ​Tutorial​, ​you​''​ve​ ​already​ ​told​ ​Lute​ ​that​ ​you​ ​know​ ​most​ ​of​ ​the​ ​words​ ​on​ ​this​ ​page​.​');
INSERT INTO sentences VALUES(162,6,5,'​You​ ​can​ ​hover​ ​over​ ​words​ ​to​ ​see​ ​information​ ​about​ ​them​, ​such​ ​as​ ​your​ ​information​ ​you​ ​might​ ​have​ ​added​ ​about​ ​dogs​.​');
INSERT INTO sentences VALUES(163,6,6,'​¶​');
INSERT INTO sentences VALUES(164,6,7,'​¶​');
INSERT INTO sentences VALUES(165,6,8,'​There​ ​are​ ​still​ ​a​ ​few​ ​blue​ ​words​, ​which​ ​according​ ​to​ ​Lute​ ​are​ ​still​ "​unknown​" ​to​ ​you​.​');
INSERT INTO sentences VALUES(166,6,9,'​You​ ​can​ ​process​ ​them​ ​like​ ​you​ ​did​ ​on​ ​the​ ​last​ ​text​.​');
INSERT INTO sentences VALUES(167,6,10,'​¶​');
INSERT INTO sentences VALUES(168,6,11,'​¶​');
INSERT INTO sentences VALUES(169,6,12,'​(​fyi​ - ​If​ ​a​ ​text​ ​has​ ​a​ ​spelling​ ​mikstaske​, ​you​ ​can​ ​edit​ ​it​ ​by​ ​clicking​ ​the​ ​small​ ​Edit​ ​icon​ ​next​ ​to​ ​the​ ​title​.​');
INSERT INTO sentences VALUES(170,6,13,'​If​ ​you​''​d​ ​like​, ​correct​ ​the​ ​mistake​ ​now​, ​and​ ​resave​ ​this​ ​text​.)​');
INSERT INTO sentences VALUES(171,6,14,'​¶​');
INSERT INTO sentences VALUES(172,6,15,'​¶​');
INSERT INTO sentences VALUES(173,6,16,'​¶​');
INSERT INTO sentences VALUES(174,6,17,'​Appendix​: ​A​ ​few​ ​other​ ​things​ ​Lute​ ​does​¶​');
INSERT INTO sentences VALUES(175,6,18,'​¶​');
INSERT INTO sentences VALUES(176,6,19,'​A​1.​');
INSERT INTO sentences VALUES(177,6,20,'​Term​ ​sentences​¶​');
INSERT INTO sentences VALUES(178,6,21,'​¶​');
INSERT INTO sentences VALUES(179,6,22,'​In​ ​the​ "​Term​" ​edit​ ​form​, ​you​ ​can​ ​click​ ​on​ ​the​ "​Sentences​" ​link​ ​to​ ​see​ ​where​ ​that​ ​term​ ​or​ ​its​ ​relations​ ​have​ ​been​ ​used​.​');
INSERT INTO sentences VALUES(180,6,23,'​Click​ ​on​ "​elephant​", ​and​ ​then​ ​click​ ​the​ ​Sentences​ ​link​ ​shown​ ​to​ ​see​ ​where​ ​that​ ​term​ ​has​ ​been​ ​used​.​');
INSERT INTO sentences VALUES(181,6,24,'​¶​');
INSERT INTO sentences VALUES(182,6,25,'​¶​');
INSERT INTO sentences VALUES(183,6,26,'​A​2.​');
INSERT INTO sentences VALUES(184,6,27,'​Archiving​, ​Unarchiving​, ​and​ ​Deleting​ ​Texts​¶​');
INSERT INTO sentences VALUES(185,6,28,'​¶​');
INSERT INTO sentences VALUES(186,6,29,'​When​ ​you​''​re​ ​done​ ​reading​ ​a​ ​text​, ​you​ ​can​ ​either​ ​Archive​ ​it​, ​or​ ​Delete​ ​it​.​');
INSERT INTO sentences VALUES(187,6,30,'​Archiving​ ​clears​ ​out​ ​the​ ​parsing​ ​data​ ​for​ ​a​ ​given​ ​text​, ​but​ ​the​ ​text​ ​is​ ​still​ ​available​ ​and​ ​can​ ​be​ ​unarchived​ ​and​ ​re​-​read​.​');
INSERT INTO sentences VALUES(188,6,31,'​The​ ​sentences​ ​are​ ​also​ ​available​ ​for​ ​searching​ ​with​ ​the​ ​Term​ "​Sentences​" ​link​.​');
INSERT INTO sentences VALUES(189,6,32,'​Deletion​ ​completely​ ​removes​ ​a​ ​text​, ​the​ ​parsing​ ​data​, ​and​ ​its​ ​sentences​.​');
INSERT INTO sentences VALUES(190,6,33,'​Neither​ ​archiving​ ​nor​ ​deleting​ ​touch​ ​any​ ​Terms​ ​you​''​ve​ ​created​, ​it​ ​just​ ​clears​ ​out​ ​the​ ​texts​.​');
INSERT INTO sentences VALUES(191,7,1,'​On​ ​the​ ​last​ ​page​ ​of​ ​every​ ​book​, ​Lute​ ​shows​ ​a​ ​link​ ​for​ ​you​ ​to​ ​archive​ ​the​ ​book​.​');
INSERT INTO sentences VALUES(192,7,2,'​You​ ​can​ ​also​ ​delete​ ​it​ ​from​ ​the​ ​Home​ ​screen​ ​by​ ​clicking​ ​on​ ​the​ "​Archive​" ​action​ (​the​ ​image​ ​with​ ​the​ ​little​ ​down​ ​arrow​) ​in​ ​the​ ​right​-​most​ ​column​.​');
INSERT INTO sentences VALUES(193,7,3,'​¶​');
INSERT INTO sentences VALUES(194,7,4,'​¶​');
INSERT INTO sentences VALUES(195,7,5,'​To​ ​unarchive​ ​the​ ​text​, ​go​ ​to​ ​Home​, ​Text​ ​Archive​, ​and​ ​click​ ​the​ "​Unarchive​" ​action​ (​the​ ​little​ ​up​ ​arrow​).​');
INSERT INTO sentences VALUES(196,7,6,'​¶​');
INSERT INTO sentences VALUES(197,7,7,'​¶​');
INSERT INTO sentences VALUES(198,7,8,'​¶​');
INSERT INTO sentences VALUES(199,7,9,'​¶​');
INSERT INTO sentences VALUES(200,7,10,'​===​¶​');
INSERT INTO sentences VALUES(201,7,11,'​¶​');
INSERT INTO sentences VALUES(202,7,12,'​Those​ ​are​ ​the​ ​the​ ​core​ ​feature​ ​of​ ​Lute​!​');
INSERT INTO sentences VALUES(203,7,13,'​There​ ​are​ ​some​ ​sample​ ​stories​ ​for​ ​other​ ​languages​.​');
INSERT INTO sentences VALUES(204,7,14,'​Try​ ​those​ ​out​ ​or​ ​create​ ​your​ ​own​.​');
INSERT INTO sentences VALUES(205,7,15,'​¶​');
INSERT INTO sentences VALUES(206,7,16,'​¶​');
INSERT INTO sentences VALUES(207,7,17,'​When​ ​you​''​re​ ​done​ ​with​ ​the​ ​demo​, ​go​ ​back​ ​to​ ​the​ ​Home​ ​screen​ ​and​ ​click​ ​the​ ​link​ ​to​ ​clear​ ​out​ ​the​ ​database​.​');
INSERT INTO sentences VALUES(208,7,18,'​Lute​ ​will​ ​delete​ ​all​ ​of​ ​the​ ​demo​ ​data​, ​and​ ​you​ ​can​ ​get​ ​started​.​');
INSERT INTO sentences VALUES(209,7,19,'​¶​');
INSERT INTO sentences VALUES(210,7,20,'​¶​');
INSERT INTO sentences VALUES(211,7,21,'​There​ ​is​ ​a​ ​Lute​ ​Discord​ ​and​ ​Wiki​ ​as​ ​well​ -- ​see​ ​the​ ​GitHub​ ​repository​ ​for​ ​links​.​');
INSERT INTO sentences VALUES(212,7,22,'​¶​');
INSERT INTO sentences VALUES(213,7,23,'​¶​');
INSERT INTO sentences VALUES(214,7,24,'​I​ ​hope​ ​that​ ​you​ ​find​ ​Lute​ ​a​ ​fun​ ​tool​ ​to​ ​use​ ​for​ ​learning​ ​languages​.​');
INSERT INTO sentences VALUES(215,7,25,'​Cheers​ ​and​ ​best​ ​wishes​!​');
INSERT INTO sentences VALUES(216,8,1,'​Érase​ ​una​ ​vez​ ​un​ ​muchacho​ ​llamado​ ​Aladino​ ​que​ ​vivía​ ​en​ ​el​ ​lejano​ ​Oriente​ ​con​ ​su​ ​madre​, ​en​ ​una​ ​casa​ ​sencilla​ ​y​ ​humilde​.​');
INSERT INTO sentences VALUES(217,8,2,'​Tenían​ ​lo​ ​justo​ ​para​ ​vivir​, ​así​ ​que​ ​cada​ ​día​, ​Aladino​ ​recorría​ ​el​ ​centro​ ​de​ ​la​ ​ciudad​ ​en​ ​busca​ ​de​ ​algún​ ​alimento​ ​que​ ​llevarse​ ​a​ ​la​ ​boca​.​');
INSERT INTO sentences VALUES(218,8,3,'​¶​');
INSERT INTO sentences VALUES(219,8,4,'​¶​');
INSERT INTO sentences VALUES(220,8,5,'​En​ ​una​ ​ocasión​ ​paseaba​ ​entre​ ​los​ ​puestos​ ​de​ ​fruta​ ​del​ ​mercado​, ​cuando​ ​se​ ​cruzó​ ​con​ ​un​ ​hombre​ ​muy​ ​extraño​ ​con​ ​pinta​ ​de​ ​extranjero​.​');
INSERT INTO sentences VALUES(221,8,6,'​Aladino​ ​se​ ​quedó​ ​sorprendido​ ​al​ ​escuchar​ ​que​ ​le​ ​llamaba​ ​por​ ​su​ ​nombre​.​');
INSERT INTO sentences VALUES(222,9,1,'​Il​ ​était​ ​une​ ​fois​ ​trois​ ​ours​: ​un​ ​papa​ ​ours​, ​une​ ​maman​ ​ours​ ​et​ ​un​ ​bébé​ ​ours​.​');
INSERT INTO sentences VALUES(223,9,2,'​Ils​ ​habitaient​ ​tous​ ​ensemble​ ​dans​ ​une​ ​maison​ ​jaune​ ​au​ ​milieu​ ​d​''​une​ ​grande​ ​forêt​.​');
INSERT INTO sentences VALUES(224,9,3,'​¶​');
INSERT INTO sentences VALUES(225,9,4,'​¶​');
INSERT INTO sentences VALUES(226,9,5,'​Un​ ​jour​, ​Maman​ ​Ours​ ​prépara​ ​une​ ​grande​ ​marmite​ ​de​ ​porridge​ ​délicieux​ ​et​ ​fumant​ ​pour​ ​le​ ​petit​ ​déjeuner​.​');
INSERT INTO sentences VALUES(227,9,6,'​Il​ ​était​ ​trop​ ​chaud​ ​pour​ ​pouvoir​ ​être​ ​mangé​, ​alors​ ​les​ ​ours​ ​décidèrent​ ​d​''​aller​ ​se​ ​promener​ ​en​ ​attendant​ ​que​ ​le​ ​porridge​ ​refroidisse​.​');
INSERT INTO sentences VALUES(228,10,1,'​Es​ ​hatte​ ​ein​ ​Mann​ ​einen​ ​Esel​, ​der​ ​schon​ ​lange​ ​Jahre​ ​die​ ​Säcke​ ​unverdrossen​ ​zur​ ​Mühle​ ​getragen​ ​hatte​, ​dessen​ ​Kräfte​ ​aber​ ​nun​ ​zu​ ​Ende​ ​gingen​, ​so​ ​daß​ ​er​ ​zur​ ​Arbeit​ ​immer​ ​untauglicher​ ​ward​.​');
INSERT INTO sentences VALUES(229,10,2,'​Da​ ​dachte​ ​der​ ​Herr​ ​daran​, ​ihn​ ​aus​ ​dem​ ​Futter​ ​zu​ ​schaffen​, ​aber​ ​der​ ​Esel​ ​merkte​, ​daß​ ​kein​ ​guter​ ​Wind​ ​wehte​, ​lief​ ​fort​ ​und​ ​machte​ ​sich​ ​auf​ ​den​ ​Weg​ ​nach​ ​Bremen​; ​dort​, ​meinte​ ​er​, ​könnte​ ​er​ ​ja​ ​Stadtmusikant​ ​werden​.​');
INSERT INTO sentences VALUES(230,10,3,'​¶​');
INSERT INTO sentences VALUES(231,10,4,'​¶​');
INSERT INTO sentences VALUES(232,10,5,'​Als​ ​er​ ​ein​ ​Weilchen​ ​fortgegangen​ ​war​, ​fand​ ​er​ ​einen​ ​Jagdhund​ ​auf​ ​dem​ ​Wege​ ​liegen​, ​der​ ​jappte​ ​wie​ ​einer​, ​der​ ​sich​ ​müde​ ​gelaufen​ ​hat​. "​');
INSERT INTO sentences VALUES(233,10,6,'​Nun​, ​was​ ​jappst​ ​du​ ​so​, ​Packan​?"​');
INSERT INTO sentences VALUES(234,10,7,'​fragte​ ​der​ ​Esel​. "​');
INSERT INTO sentences VALUES(235,10,8,'​Ach​," ​sagte​ ​der​ ​Hund​, "​weil​ ​ich​ ​alt​ ​bin​ ​und​ ​jeden​ ​Tag​ ​schwächer​ ​werde​, ​auch​ ​auf​ ​der​ ​Jagd​ ​nicht​ ​mehr​ ​fort​ ​kann​, ​hat​ ​mich​ ​mein​ ​Herr​ ​wollen​ ​totschlagen​, ​da​ ​hab​ ​ich​ ​Reißaus​ ​genommen​; ​aber​ ​womit​ ​soll​ ​ich​ ​nun​ ​mein​ ​Brot​ ​verdienen​?" - "​');
INSERT INTO sentences VALUES(236,10,9,'​Weißt​ ​du​ ​was​?"​');
INSERT INTO sentences VALUES(237,10,10,'​sprach​ ​der​ ​Esel​, "​ich​ ​gehe​ ​nach​ ​Bremen​ ​und​ ​werde​ ​dort​ ​Stadtmusikant​, ​geh​ ​mit​ ​und​ ​laß​ ​dich​ ​auch​ ​bei​ ​der​ ​Musik​ ​annehmen​.​');
INSERT INTO sentences VALUES(238,10,11,'​Ich​ ​spiele​ ​die​ ​Laute​ ​und​ ​du​ ​schlägst​ ​die​ ​Pauken​."​');
INSERT INTO sentences VALUES(239,11,1,'​Πέτρος​: ​Γεια​ ​σου​, ​Νίκη​.​');
INSERT INTO sentences VALUES(240,11,2,'​Ο​ ​Πέτρος​ ​είμαι​.​');
INSERT INTO sentences VALUES(241,11,3,'​¶​');
INSERT INTO sentences VALUES(242,11,4,'​Νίκη​: ​Α​, ​γεια​ ​σου​ ​Πέτρο​.​');
INSERT INTO sentences VALUES(243,11,5,'​Τι​ ​κάνεις​;​¶​');
INSERT INTO sentences VALUES(244,11,6,'​Πέτρος​: ​Μια​ ​χαρά​.​');
INSERT INTO sentences VALUES(245,11,7,'​Σε​ ​παίρνω​ ​για​ ​να​ ​πάμε​ ​καμιά​ ​βόλτα​ ​αργότερα​.​');
INSERT INTO sentences VALUES(246,11,8,'​Τι​ ​λες​;​¶​');
INSERT INTO sentences VALUES(247,11,9,'​Νίκη​: ​Α​, ​ωραία​.​');
INSERT INTO sentences VALUES(248,11,10,'​Κι​ ​εγώ​ ​θέλω​ ​να​ ​βγω​ ​λίγο​.​');
INSERT INTO sentences VALUES(249,11,11,'​Συνέχεια​ ​διαβάζω​ ​για​ ​τις​ ​εξετάσεις​… ​κουράστηκα​ ​πια​.​');
INSERT INTO sentences VALUES(250,11,12,'​Πού​ ​λες​ ​να​ ​πάμε​;​¶​');
INSERT INTO sentences VALUES(251,11,13,'​Πέτρος​: ​Στη​ ​γνωστή​ ​καφετέρια​ ​στην​ ​πλατεία​.​');
INSERT INTO sentences VALUES(252,11,14,'​Θα​ ​είναι​ ​και​ ​άλλα​ ​παιδιά​ ​από​ ​την​ ​τάξη​ ​μας​ ​εκεί​.​');
INSERT INTO sentences VALUES(253,11,15,'​¶​');
INSERT INTO sentences VALUES(254,11,16,'​Νίκη​: ​Ναι​; ​Ποιοι​ ​θα​ ​είναι​;​¶​');
INSERT INTO sentences VALUES(255,11,17,'​Πέτρος​: ​Ο​ ​Γιάννης​, ​ο​ ​Αντρέας​ ​και​ ​η​ ​Ελπίδα​.​');
INSERT INTO sentences VALUES(256,11,18,'​¶​');
INSERT INTO sentences VALUES(257,11,19,'​Νίκη​: ​Ωραία​.​');
INSERT INTO sentences VALUES(258,11,20,'​Θα​ ​πάτε​ ​και​ ​πουθενά​ ​αλλού​ ​μετά​;​¶​');
INSERT INTO sentences VALUES(259,11,21,'​Πέτρος​: ​Ναι​, ​λέμε​ ​να​ ​πάμε​ ​στον​ ​κινηματογράφο​ ​που​ ​είναι​ ​κοντά​ ​στην​ ​καφετέρια​.​');
INSERT INTO sentences VALUES(260,11,22,'​Παίζει​ ​μια​ ​κωμωδία​.​');
INSERT INTO sentences VALUES(261,11,23,'​¶​');
INSERT INTO sentences VALUES(262,11,24,'​Νίκη​: ​Α​, ​δεν​ ​μπορώ​ ​να​ ​καθίσω​ ​έξω​ ​μέχρι​ ​τόσο​ ​αργά​.​');
INSERT INTO sentences VALUES(263,11,25,'​Πρέπει​ ​να​ ​γυρίσω​ ​σπίτι​ ​για​ ​να​ ​διαβάσω​.​');
INSERT INTO sentences VALUES(264,11,26,'​¶​');
INSERT INTO sentences VALUES(265,11,27,'​Πέτρος​: ​Έλα​ ​τώρα​.​');
INSERT INTO sentences VALUES(266,11,28,'​Διαβάζεις​ ​αύριο​…​¶​');
INSERT INTO sentences VALUES(267,11,29,'​Νίκη​: ​Όχι​, ​όχι​, ​αδύνατον​.​');
INSERT INTO sentences VALUES(268,11,30,'​Είμαι​ ​πολύ​ ​πίσω​ ​στο​ ​διάβασμά​ ​μου​.​');
INSERT INTO sentences VALUES(269,11,31,'​¶​');
INSERT INTO sentences VALUES(270,11,32,'​Πέτρος​: ​Καλά​, ​έλα​ ​μόνο​ ​στην​ ​καφετέρια​ ​τότε​.​');
INSERT INTO sentences VALUES(271,11,33,'​Θα​ ​περάσω​ ​να​ ​σε​ ​πάρω​ ​γύρω​ ​στις​ ​έξι​ ​να​ ​πάμε​ ​μαζί​.​');
INSERT INTO sentences VALUES(272,11,34,'​Εντάξει​;​¶​');
INSERT INTO sentences VALUES(273,11,35,'​Νίκη​: ​Εντάξει​.​');
INSERT INTO sentences VALUES(274,11,36,'​Γεια​.​');
INSERT INTO sentences VALUES(275,11,37,'​¶​');
INSERT INTO sentences VALUES(276,11,38,'​Πέτρο​: ​Τα​ ​λέμε​.​');
INSERT INTO sentences VALUES(277,11,39,'​Γεια​.​');
INSERT INTO sentences VALUES(278,12,1,'​北​冥​有​魚​，​其​名​為​鯤​。​');
INSERT INTO sentences VALUES(279,12,2,'​鯤​之​大​，​不​知​其​幾​千​里​也​。​');
INSERT INTO sentences VALUES(280,12,3,'​化​而​為​鳥​，​其​名​為​鵬​。​');
INSERT INTO sentences VALUES(281,12,4,'​鵬​之​背​，​不​知​其​幾​千​里​也​；​怒​而​飛​，​其​翼​若​垂​天​之​雲​。​');
INSERT INTO sentences VALUES(282,12,5,'​是​鳥​也​，​海​運​則​將​徙​於​南​冥​。​');
INSERT INTO sentences VALUES(283,12,6,'​南​冥​者​，​天​池​也​。​');
INSERT INTO sentences VALUES(284,12,7,'​齊​諧​者​，​志​怪​者​也​。​');
INSERT INTO sentences VALUES(285,12,8,'​諧​之​言​曰​：​「​鵬​之​徙​於​南​冥​也​，​水​擊​三​千​里​，​摶​扶​搖​而​上​者​九​萬​里​，​去​以​六​月​息​者​也​。​');
INSERT INTO sentences VALUES(286,12,9,'​」​野​馬​也​，​塵​埃​也​，​生​物​之​以​息​相​吹​也​。​');
INSERT INTO sentences VALUES(287,12,10,'​天​之​蒼​蒼​，​其​正​色​邪​？​');
INSERT INTO sentences VALUES(288,12,11,'​其​遠​而​無​所​至​極​邪​？​');
INSERT INTO sentences VALUES(289,12,12,'​其​視​下​也​亦​若​是​，​則​已​矣​。​');
INSERT INTO sentences VALUES(290,12,13,'​且​夫​水​之​積​也​不​厚​，​則​負​大​舟​也​無​力​。​');
INSERT INTO sentences VALUES(291,12,14,'​覆​杯​水​於​坳​堂​之​上​，​則​芥​為​之​舟​，​置​杯​焉​則​膠​，​水​淺​而​舟​大​也​。​');
INSERT INTO sentences VALUES(292,12,15,'​風​之​積​也​不​厚​，​則​其​負​大​翼​也​無​力​。​');
INSERT INTO sentences VALUES(293,12,16,'​故​九​萬​里​則​風​斯​在​下​矣​，​而​後​乃​今​培​風​；​背​負​青​天​而​莫​之​夭​閼​者​，​而​後​乃​今​將​圖​南​。​');
INSERT INTO sentences VALUES(294,13,1,'​蜩​與​學​鳩​笑​之​曰​：​「​我​決​起​而​飛​，​槍​1​榆​、​枋​，​時​則​不​至​而​控​於​地​而​已​矣​，​奚​以​之​九​萬​里​而​南​為​？​');
INSERT INTO sentences VALUES(295,13,2,'​」​適​莽​蒼​者​三​湌​而​反​，​腹​猶​果​然​；​適​百​里​者​宿​舂​糧​；​適​千​里​者​三​月​聚​糧​。​');
INSERT INTO sentences VALUES(296,13,3,'​之​二​蟲​又​何​知​！​');
INSERT INTO sentences VALUES(297,13,4,'​小​知​不​及​大​知​，​小​年​不​及​大​年​。​');
INSERT INTO sentences VALUES(298,13,5,'​奚​以​知​其​然​也​？​');
INSERT INTO sentences VALUES(299,13,6,'​朝​菌​不​知​晦​朔​，​蟪​蛄​不​知​春​秋​，​此​小​年​也​。​');
INSERT INTO sentences VALUES(300,13,7,'​楚​之​南​有​冥​靈​者​，​以​五​百​歲​為​春​，​五​百​歲​為​秋​；​上​古​有​大​椿​者​，​以​八​千​歲​為​春​，​八​千​歲​為​秋​。​');
INSERT INTO sentences VALUES(301,13,8,'​而​彭​祖​乃​今​以​久​特​聞​，​眾​人​匹​之​，​不​亦​悲​乎​！​');
INSERT INTO sentences VALUES(302,14,1,'​مرحبا،​ ​كيف​ ​حالك​ ​؟​¶​');
INSERT INTO sentences VALUES(303,14,2,'​مرحبا​, ​أنا​ ​بخير​¶​');
INSERT INTO sentences VALUES(304,14,3,'​هل​ ​انت​ ​جديدٌ​ ​هنا؟​ ​لم​ ​أراك​ ​من​ ​قبل​¶​');
INSERT INTO sentences VALUES(305,14,4,'​انا​ ​طالب​ ​جديد​.​');
INSERT INTO sentences VALUES(306,14,5,'​لقد​ ​وصلت​ ​البارحة​¶​');
INSERT INTO sentences VALUES(307,14,6,'​انا​ ​محمد​, ​تشرفت​ ​بلقائك​¶​');
INSERT INTO sentences VALUES(308,14,7,'​¶​');
INSERT INTO sentences VALUES(309,14,8,'​شجرة​ ​الحياة​¶​');
INSERT INTO sentences VALUES(310,14,9,'​¶​');
INSERT INTO sentences VALUES(311,14,10,'​تحكي​ ​هذه​ ​القصة​ ​عن​ ​ولد​ ​صغير​ ​يُدعى​ «​يوسف​»​،​ ​يعيش​ ​مع​ ​أمه​ ​الأرملة​ ​الفقيرة،​ ​يساعدها​ ​ويحنو​ ​عليها​ ​ويحبها​ ​حبًا​ ​جمًا​.​');
INSERT INTO sentences VALUES(312,15,1,'​北風​と​太陽​¶​');
INSERT INTO sentences VALUES(313,15,2,'​¶​');
INSERT INTO sentences VALUES(314,15,3,'​「​おれ​の​方​が​強い​。​');
INSERT INTO sentences VALUES(315,15,4,'​」​「​いい​や​、​ぼく​の​方​が​強い​。​');
INSERT INTO sentences VALUES(316,15,5,'​」​¶​');
INSERT INTO sentences VALUES(317,15,6,'​北風​と​太陽​の​声​が​聞こえ​ます​。​');
INSERT INTO sentences VALUES(318,15,7,'​二​人​は​どちら​の​力​が​強い​か​で​ケンカ​を​し​て​いる​よう​です​。​');
INSERT INTO sentences VALUES(319,15,8,'​¶​');
INSERT INTO sentences VALUES(320,15,9,'​「​太陽​が​毎日​元気​だ​から​、​暑く​て​みんな​困っ​て​いる​よ​。​');
INSERT INTO sentences VALUES(321,15,10,'​おれ​が​涼しい​風​を​吹く​と​、​みんな​嬉し​そう​だ​。​');
INSERT INTO sentences VALUES(322,15,11,'​」​¶​');
CREATE TABLE IF NOT EXISTS "texts" (
	"TxID" INTEGER NOT NULL  ,
	"TxBkID" INTEGER NOT NULL  ,
	"TxOrder" INTEGER NOT NULL  ,
	"TxLgID" INTEGER NOT NULL  ,
	"TxText" TEXT NOT NULL  ,
	"TxAudioURI" VARCHAR(200) NULL  ,
	"TxSourceURI" VARCHAR(1000) NULL  ,
	"TxArchived" TINYINT NOT NULL DEFAULT '0' , TxReadDate datetime null,
	PRIMARY KEY ("TxID"),
	FOREIGN KEY("TxBkID") REFERENCES "books" ("BkID") ON UPDATE NO ACTION ON DELETE CASCADE,
	FOREIGN KEY("TxLgID") REFERENCES "languages" ("LgID") ON UPDATE NO ACTION ON DELETE CASCADE
);
INSERT INTO texts VALUES(1,1,1,1,replace('Welcome to Lute!  This short guide should get you going.\n\nNavigation\n\nThis tutorial has multiple pages.  Above the title are some arrows to navigate forwards and backwards.  In longer texts, you can jump forward or back ten pages at a time as well.\n\n1. The Basics\n\nAll of these words are blue because they are "unknown" - according to Lute, this is the first time you''re seeing these words.\n\nYou can click on a word, and create a definition.  For example, click on this word: elephant.\n\nWhen the form pops up in the right-hand frame, a dictionary is loaded below.  Copy-paste something from the dictionary into the translation, or make up your own, mark the status, add some tags if you want (eg, type "noun" in the tags field), and click save.  From now on, every English text that you read that contains the word "elephant" will show the status.  If you hover over any "elephant", you''ll see some information.\n\n1.1 Multiple dictionaries.\n\nNext to the term is a small arrow, "Lookup".  If you click on this repeatedly, Lute cycles through the dictionaries that you configure for the language in the "Languages" link on the homepage.\n\n1.2 Images\n\nFor this demo, English has been configured to do an image search for the second English dictinary, so if you click on the arrow, you''ll see some happy elephants (if you clicked on elephant!).','\n',char(10)),NULL,NULL,0,NULL);
INSERT INTO texts VALUES(2,1,2,1,replace('You can also click on the little "eye icon" next to the term, and it opens up a common image search URL.\n\nIn either case, if you click on one of the images shown in the list, that image is saved in your public/media/images folder.  When you hover over the word in the reading pane, that picture is included in the word hover.  Try adding an image for your elephant by clicking on the term, clicking the eye icon, and clicking a picture you like.  Then hover over your elephant.\n\nNote: sometimes these images make _no sense_ -- it''s using Bing image search, and it does the best it can with the limited context it has.\n\n2. Multi-word Terms\n\nYou can create multi-word terms by clicking and dragging across multiple words, then release the mouse.  Try creating a term for the phrase "the cat''s pyjamas", and add a translation and set the status.\n\n(A brief side note: Lute keeps track of where you are in any text.  If you click the Home link above to leave this tutorial, and later click the Tutorial link from the Text listing, Lute will open the last page you were at.)\n\n3. Parent Terms\n\nSometimes it helps to associate terms with a "parent".  For example, the verb "to have" is conjugated in various forms as "I have a cold", "he has a dog", "they had dinner".  First create a Term for "have".','\n',char(10)),NULL,NULL,0,NULL);
INSERT INTO texts VALUES(3,1,3,1,replace('Then create a Term for "has", and in the Parent field start typing "have".  Lute will show the existing Term "have" in the drop down, and if you select it, "has" will be associated with that on save, and when you hover over "has" you''ll see the parent''s information as well.\n\nIf you enter a non-existent Parent word, Lute will create a placeholder Term for that Parent, copying some content from your term.  For example, try creating a Term for the word "dogs", associating it with the non-existent Term "dog".  When you save "dogs", both will be updated.\n\nTerms can have multiple parents, too.  Hit the Enter (or Return) key after each parent.  For example, if you wanted to associate the Term "puppies" with both "puppy" and "dog", click on "puppies", and in the Parents text box type "puppy", hit Enter, type "dog", and hit Enter.  Sometimes this is necessary: for example, in Spanish, "se sienta" can either be a conjugation of "sentirse" (to feel) or "sentarse" (to sit), depending on the context.\n\n4. Mark the remainder as "Well Known"\n\nWhen you''re done creating Terms on a page, you will likely still have a bunch of blue words, or "unknowns", left over, even though you really know these words.  You can set all of these to "Well Known" in one shot with the green checkmark at the bottom of the page ("Mark rest as known").  Try that now to see what happens.','\n',char(10)),NULL,NULL,0,NULL);
INSERT INTO texts VALUES(4,1,4,1,replace('This button only affects words on the current page, so when you go to the next page, you''ll see that some words are still unknown.\n\nThere are other buttons at the bottom of the page.  The green checkmark with the arrow sets the remaining unknowns on the current page, and also goes to the next page.\n\n5. Keyboard shortcuts\n\nThe small blue question mark in the header shows some keyboard shortcuts.\n\n5.1 Updating Status\n\nIf you''ve worked through the tutorial, you''ll have noted that words are underlined in blue when you move the mouse over them.  You can quickly change the status of the current word by hitting 1, 2, 3, 4, 5, w (for Well-Known), or i (for Ignore).  Try hovering over the following words and hit the status buttons: apple, banana, cranberry, donut.\n\nIf you click on a word, it''s underlined in red, and the Term edit form is shown.  (Before you switch over to the Term editing form, you can still update its status.)  You can jump over to the edit form by hitting Tab, and then start editing.\n\nWhen a word has been clicked, it''s "active", so it keeps the focus.  Hovering the mouse over other words won''t underline them in blue anymore, and hitting status update hotkeys (1 - 5, w, i) will only update the active word.  To "un-click" a word underlined in red, click it again, or hit Escape or Return.  Then you''ll be back in "Hover mode".','\n',char(10)),NULL,NULL,0,NULL);
INSERT INTO texts VALUES(5,1,5,1,replace('Try clicking and un-clicking or Escaping any word in this paragraph to get a feel for it.\n\nNote that for the keyboard shortcuts to work, the reading pane (where the text is) must have the "focus".  Click anywhere on the reading pane to re-establish focus.\n\n5.1 Bulk updates\n\nIf you hold down Shift and click a bunch of words, you can bulk update their statuses.\n\n5.2 Arrow keys\n\nThe Right and Left arrow keys click the next and previous words.  Hit Escape or Return to get back to "hover mode".\n\n5.3 Copying text\n\nWhen a word is hovered over or clicked, hit "c" to copy that word''s sentence to your clipboard.  Hit "C" to copy the word''s full paragraph (multiple sentences).  You can also copy arbitrary sections of text by holding down the Shift key while highlighting the text with your mouse.\n\n6. Next steps\n\nAll done this text!\n\nLute keeps track of all of this in your database, so any time you create or import a new Book, all the info you''ve created is carried forward.\n\nThere''s a tutorial follow-up: go to the Home screen, and click the "Tutorial follow-up" in the table.','\n',char(10)),NULL,NULL,0,NULL);
INSERT INTO texts VALUES(6,2,1,1,replace('Hopefully you''ve gone through the Tutorial, and created some Terms.\n\nFrom the Tutorial, you''ve already told Lute that you know most of the words on this page.  You can hover over words to see information about them, such as your information you might have added about dogs.\n\nThere are still a few blue words, which according to Lute are still "unknown" to you.  You can process them like you did on the last text.\n\n(fyi - If a text has a spelling mikstaske, you can edit it by clicking the small Edit icon next to the title.  If you''d like, correct the mistake now, and resave this text.)\n\n\nAppendix: A few other things Lute does\n\nA1. Term sentences\n\nIn the "Term" edit form, you can click on the "Sentences" link to see where that term or its relations have been used.  Click on "elephant", and then click the Sentences link shown to see where that term has been used.\n\nA2. Archiving, Unarchiving, and Deleting Texts\n\nWhen you''re done reading a text, you can either Archive it, or Delete it.  Archiving clears out the parsing data for a given text, but the text is still available and can be unarchived and re-read.  The sentences are also available for searching with the Term "Sentences" link.  Deletion completely removes a text, the parsing data, and its sentences.  Neither archiving nor deleting touch any Terms you''ve created, it just clears out the texts.','\n',char(10)),NULL,NULL,0,NULL);
INSERT INTO texts VALUES(7,2,2,1,replace('On the last page of every book, Lute shows a link for you to archive the book.  You can also delete it from the Home screen by clicking on the "Archive" action (the image with the little down arrow) in the right-most column.\n\nTo unarchive the text, go to Home, Text Archive, and click the "Unarchive" action (the little up arrow).\n\n\n\n===\n\nThose are the the core feature of Lute!  There are some sample stories for other languages.  Try those out or create your own.\n\nWhen you''re done with the demo, go back to the Home screen and click the link to clear out the database.  Lute will delete all of the demo data, and you can get started.\n\nThere is a Lute Discord and Wiki as well -- see the GitHub repository for links.\n\nI hope that you find Lute a fun tool to use for learning languages.  Cheers and best wishes!','\n',char(10)),NULL,NULL,0,NULL);
INSERT INTO texts VALUES(8,3,1,3,replace('Érase una vez un muchacho llamado Aladino que vivía en el lejano Oriente con su madre, en una casa sencilla y humilde. Tenían lo justo para vivir, así que cada día, Aladino recorría el centro de la ciudad en busca de algún alimento que llevarse a la boca.\n\nEn una ocasión paseaba entre los puestos de fruta del mercado, cuando se cruzó con un hombre muy extraño con pinta de extranjero. Aladino se quedó sorprendido al escuchar que le llamaba por su nombre.','\n',char(10)),NULL,NULL,0,NULL);
INSERT INTO texts VALUES(9,4,1,2,replace('Il était une fois trois ours: un papa ours, une maman ours et un bébé ours. Ils habitaient tous ensemble dans une maison jaune au milieu d''une grande forêt.\n\nUn jour, Maman Ours prépara une grande marmite de porridge délicieux et fumant pour le petit déjeuner. Il était trop chaud pour pouvoir être mangé, alors les ours décidèrent d''aller se promener en attendant que le porridge refroidisse.','\n',char(10)),NULL,NULL,0,NULL);
INSERT INTO texts VALUES(10,5,1,4,replace('Es hatte ein Mann einen Esel, der schon lange Jahre die Säcke unverdrossen zur Mühle getragen hatte, dessen Kräfte aber nun zu Ende gingen, so daß er zur Arbeit immer untauglicher ward. Da dachte der Herr daran, ihn aus dem Futter zu schaffen, aber der Esel merkte, daß kein guter Wind wehte, lief fort und machte sich auf den Weg nach Bremen; dort, meinte er, könnte er ja Stadtmusikant werden.\n\nAls er ein Weilchen fortgegangen war, fand er einen Jagdhund auf dem Wege liegen, der jappte wie einer, der sich müde gelaufen hat. "Nun, was jappst du so, Packan?" fragte der Esel. "Ach," sagte der Hund, "weil ich alt bin und jeden Tag schwächer werde, auch auf der Jagd nicht mehr fort kann, hat mich mein Herr wollen totschlagen, da hab ich Reißaus genommen; aber womit soll ich nun mein Brot verdienen?" - "Weißt du was?" sprach der Esel, "ich gehe nach Bremen und werde dort Stadtmusikant, geh mit und laß dich auch bei der Musik annehmen. Ich spiele die Laute und du schlägst die Pauken."','\n',char(10)),NULL,NULL,0,NULL);
INSERT INTO texts VALUES(11,6,1,5,replace('Πέτρος: Γεια σου, Νίκη. Ο Πέτρος είμαι.\nΝίκη: Α, γεια σου Πέτρο. Τι κάνεις;\nΠέτρος: Μια χαρά. Σε παίρνω για να πάμε καμιά βόλτα αργότερα. Τι λες;\nΝίκη: Α, ωραία. Κι εγώ θέλω να βγω λίγο. Συνέχεια διαβάζω για τις εξετάσεις… κουράστηκα πια. Πού λες να πάμε;\nΠέτρος: Στη γνωστή καφετέρια στην πλατεία. Θα είναι και άλλα παιδιά από την τάξη μας εκεί.\nΝίκη: Ναι; Ποιοι θα είναι;\nΠέτρος: Ο Γιάννης, ο Αντρέας και η Ελπίδα.\nΝίκη: Ωραία. Θα πάτε και πουθενά αλλού μετά;\nΠέτρος: Ναι, λέμε να πάμε στον κινηματογράφο που είναι κοντά στην καφετέρια. Παίζει μια κωμωδία.\nΝίκη: Α, δεν μπορώ να καθίσω έξω μέχρι τόσο αργά. Πρέπει να γυρίσω σπίτι για να διαβάσω.\nΠέτρος: Έλα τώρα. Διαβάζεις αύριο…\nΝίκη: Όχι, όχι, αδύνατον. Είμαι πολύ πίσω στο διάβασμά μου.\nΠέτρος: Καλά, έλα μόνο στην καφετέρια τότε. Θα περάσω να σε πάρω γύρω στις έξι να πάμε μαζί. Εντάξει;\nΝίκη: Εντάξει. Γεια.\nΠέτρο: Τα λέμε. Γεια.','\n',char(10)),NULL,NULL,0,NULL);
INSERT INTO texts VALUES(12,7,1,6,'北冥有魚，其名為鯤。鯤之大，不知其幾千里也。化而為鳥，其名為鵬。鵬之背，不知其幾千里也；怒而飛，其翼若垂天之雲。是鳥也，海運則將徙於南冥。南冥者，天池也。齊諧者，志怪者也。諧之言曰：「鵬之徙於南冥也，水擊三千里，摶扶搖而上者九萬里，去以六月息者也。」野馬也，塵埃也，生物之以息相吹也。天之蒼蒼，其正色邪？其遠而無所至極邪？其視下也亦若是，則已矣。且夫水之積也不厚，則負大舟也無力。覆杯水於坳堂之上，則芥為之舟，置杯焉則膠，水淺而舟大也。風之積也不厚，則其負大翼也無力。故九萬里則風斯在下矣，而後乃今培風；背負青天而莫之夭閼者，而後乃今將圖南。',NULL,NULL,0,NULL);
INSERT INTO texts VALUES(13,7,2,6,'蜩與學鳩笑之曰：「我決起而飛，槍1榆、枋，時則不至而控於地而已矣，奚以之九萬里而南為？」適莽蒼者三湌而反，腹猶果然；適百里者宿舂糧；適千里者三月聚糧。之二蟲又何知！小知不及大知，小年不及大年。奚以知其然也？朝菌不知晦朔，蟪蛄不知春秋，此小年也。楚之南有冥靈者，以五百歲為春，五百歲為秋；上古有大椿者，以八千歲為春，八千歲為秋。而彭祖乃今以久特聞，眾人匹之，不亦悲乎！',NULL,NULL,0,NULL);
INSERT INTO texts VALUES(14,8,1,7,replace('مرحبا، كيف حالك ؟\nمرحبا, أنا بخير\nهل انت جديدٌ هنا؟ لم أراك من قبل\nانا طالب جديد.لقد وصلت البارحة\nانا محمد, تشرفت بلقائك\n\nشجرة الحياة\n\nتحكي هذه القصة عن ولد صغير يُدعى «يوسف»، يعيش مع أمه الأرملة الفقيرة، يساعدها ويحنو عليها ويحبها حبًا جمًا. وفي يوم من الأيام يصيب المرض أم يوسف ويشتد عليها، ولا يعرف يوسف ماذا يفعل لإنقاذها، فلا يجد أمامه سوى اللجوء إلى الجِنِّيَّة «وِداد» التي تدله على شجرة فيها الشفاء لأمه، هذه الشجرة تقع في أعلى الجبل المقابل لمنزلهم، وعلى يوسف أن يتسلق هذا الجبل ويواجه المخاطر من أجل أن يأتي لأمه بالدواء الموجود في أوراق هذه الشجرة، فهل سينجح يوسف في ذلك؟ وماذا ينتظره من مخاطر وأهوال؟','\n',char(10)),NULL,NULL,0,NULL);
INSERT INTO texts VALUES(15,9,1,8,replace('北風と太陽\n\n「おれの方が強い。」「いいや、ぼくの方が強い。」\n北風と太陽の声が聞こえます。二人はどちらの力が強いかでケンカをしているようです。\n「太陽が毎日元気だから、暑くてみんな困っているよ。おれが涼しい風を吹くと、みんな嬉しそうだ。」','\n',char(10)),NULL,NULL,0,NULL);
CREATE TABLE IF NOT EXISTS "bookstats" (
	"BkID" INTEGER NOT NULL  ,
	"wordcount" INTEGER NULL  ,
	"distinctterms" INTEGER NULL  ,
	"distinctunknowns" INTEGER NULL  ,
	"unknownpercent" INTEGER NULL  ,
	PRIMARY KEY ("BkID"),
	FOREIGN KEY("BkID") REFERENCES "books" ("BkID") ON UPDATE NO ACTION ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "wordimages" (
	"WiID" INTEGER NOT NULL  ,
	"WiWoID" INTEGER NOT NULL  ,
	"WiSource" VARCHAR(500) NOT NULL  ,
	PRIMARY KEY ("WiID"),
	FOREIGN KEY("WiWoID") REFERENCES "words" ("WoID") ON UPDATE NO ACTION ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "wordflashmessages" (
  "WfID" INTEGER NOT NULL,
  "WfWoID" INTEGER NOT NULL,
  "WfMessage" VARCHAR(200) NOT NULL,
  PRIMARY KEY ("WfID"),
  FOREIGN KEY("WfWoID") REFERENCES "words" ("WoID") ON UPDATE NO ACTION ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "words" (
	"WoID" INTEGER NOT NULL PRIMARY KEY ,
	"WoLgID" INTEGER NOT NULL  ,
	"WoText" VARCHAR(250) NOT NULL  ,
	"WoTextLC" VARCHAR(250) NOT NULL  ,
	"WoStatus" TINYINT NOT NULL  ,
	"WoTranslation" VARCHAR(500) NULL  ,
	"WoRomanization" VARCHAR(100) NULL  ,
	"WoTokenCount" TINYINT NOT NULL DEFAULT '0' ,
	"WoCreated" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ,
	"WoStatusChanged" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY("WoLgID") REFERENCES "languages" ("LgID") ON UPDATE NO ACTION ON DELETE CASCADE
);
INSERT INTO words VALUES(1,1,'your​ ​local​ ​environment​ ​file','your​ ​local​ ​environment​ ​file',3,'This is ".env", your personal file in the project root folder :-)',NULL,7,'2023-09-29 20:20:05','2023-09-29 20:20:05');
CREATE TABLE IF NOT EXISTS "books" (
	"BkID" INTEGER NOT NULL  ,
	"BkLgID" INTEGER NOT NULL  ,
	"BkTitle" VARCHAR(200) NOT NULL  ,
	"BkSourceURI" VARCHAR(1000) NULL  ,
	"BkArchived" TINYINT NOT NULL DEFAULT '0' ,
	"BkCurrentTxID" INTEGER NOT NULL DEFAULT '0' , BkWordCount INT,
	PRIMARY KEY ("BkID"),
	FOREIGN KEY("BkLgID") REFERENCES "languages" ("LgID") ON UPDATE NO ACTION ON DELETE CASCADE
);
INSERT INTO books VALUES(1,1,'Tutorial',NULL,0,0,1162);
INSERT INTO books VALUES(2,1,'Tutorial follow-up',NULL,0,0,397);
INSERT INTO books VALUES(3,3,'Aladino y la lámpara maravillosa',NULL,0,0,83);
INSERT INTO books VALUES(4,2,'Boucles d’or et les trois ours',NULL,0,0,69);
INSERT INTO books VALUES(5,4,'Die Bremer Stadtmusikanten',NULL,0,0,175);
INSERT INTO books VALUES(6,5,'Γεια σου, Νίκη. Ο Πέτρος είμαι.',NULL,0,0,157);
INSERT INTO books VALUES(7,6,'逍遙遊',NULL,0,0,382);
INSERT INTO books VALUES(8,7,'Misc examples',NULL,0,0,115);
INSERT INTO books VALUES(9,8,'北風と太陽 - きたかぜたいよう',NULL,0,0,64);
CREATE TABLE IF NOT EXISTS "wordparents" (
	"WpWoID" INTEGER NOT NULL  ,
	"WpParentWoID" INTEGER NOT NULL  ,
	FOREIGN KEY("WpParentWoID") REFERENCES "words" ("WoID") ON UPDATE NO ACTION ON DELETE CASCADE,
	FOREIGN KEY("WpWoID") REFERENCES "words" ("WoID") ON UPDATE NO ACTION ON DELETE CASCADE
);
CREATE UNIQUE INDEX "LgName" ON "languages" ("LgName");
CREATE UNIQUE INDEX "TgText" ON "tags" ("TgText");
CREATE UNIQUE INDEX "T2Text" ON "tags2" ("T2Text");
CREATE INDEX "BtT2ID" ON "booktags" ("BtT2ID");
CREATE INDEX "WtTgID" ON "wordtags" ("WtTgID");
CREATE INDEX "SeOrder" ON "sentences" ("SeOrder");
CREATE INDEX "SeTxID" ON "sentences" ("SeTxID");
CREATE INDEX "WiWoID" ON "wordimages" ("WiWoID");
CREATE INDEX "WoLgID" ON "words" ("WoLgID");
CREATE INDEX "WoStatus" ON "words" ("WoStatus");
CREATE INDEX "WoStatusChanged" ON "words" ("WoStatusChanged");
CREATE INDEX "WoTextLC" ON "words" ("WoTextLC");
CREATE UNIQUE INDEX "WoTextLCLgID" ON "words" ("WoTextLC", "WoLgID");
CREATE INDEX "WoTokenCount" ON "words" ("WoTokenCount");
CREATE INDEX "BkLgID" ON "books" ("BkLgID");
CREATE UNIQUE INDEX "wordparent_pair" ON "wordparents" ("WpWoID", "WpParentWoID");
CREATE TRIGGER trig_words_update_WoStatusChanged
AFTER UPDATE OF WoStatus ON words
FOR EACH ROW
WHEN old.WoStatus <> new.WoStatus
BEGIN
    UPDATE words
    SET WoStatusChanged = CURRENT_TIMESTAMP
    WHERE WoID = NEW.WoID;
END;
COMMIT;
