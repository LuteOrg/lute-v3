-- ------------------------------------------
-- Baseline db with demo data.
-- Migrations tracked in _migrations, settings reset.
-- Generated from 'inv db.export.baseline'
-- ------------------------------------------

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
INSERT INTO _migrations VALUES('20231018_211236_remove_excess_texts_fields.sql');
INSERT INTO _migrations VALUES('20231029_092851_create_migration_settings.sql');
INSERT INTO _migrations VALUES('20231101_203811_modify_settings_schema.sql');
INSERT INTO _migrations VALUES('20231130_141236_add_TxWordCount.sql');
INSERT INTO _migrations VALUES('20231210_103924_add_book_audio_fields.sql');
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
INSERT INTO languages VALUES(1,'Arabic','https://www.arabicstudentsdictionary.com/search?q=###','*https://translate.google.com/?hl=es&sl=ar&tl=en&text=###&op=translate','*https://translate.google.com/?hl=es&sl=ar&tl=en&text=###','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?؟۔‎','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','\u0600-\u06FF\uFE70-\uFEFC',0,0,1,1,'spacedel');
INSERT INTO languages VALUES(2,'Classical Chinese','https://ctext.org/dictionary.pl?if=en&char=###','https://www.bing.com/images/search?q=###&form=HDRSC2&first=1&tsc=ImageHoverTitle','*https://www.deepl.com/translator#ch/en/###','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?。！？','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','一-龥',0,0,0,1,'classicalchinese');
INSERT INTO languages VALUES(3,'Czech','https://slovniky.lingea.cz/Anglicko-cesky/###','https://slovnik.seznam.cz/preklad/cesky_anglicky/###','https://www.deepl.com/translator#cs/en/###','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','a-zA-ZÀ-ÖØ-öø-ȳáéíóúÁÉÍÓÚñÑ',0,0,0,1,'spacedel');
INSERT INTO languages VALUES(4,'English','https://en.thefreedictionary.com/###','https://www.bing.com/images/search?q=###&form=HDRSC2&first=1&tsc=ImageHoverTitle','*https://www.deepl.com/translator#en/en/###','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','a-zA-ZÀ-ÖØ-öø-ȳáéíóúÁÉÍÓÚñÑ',0,0,0,0,'spacedel');
INSERT INTO languages VALUES(5,'French','https://fr.thefreedictionary.com/###','https://www.bing.com/images/search?q=###&form=HDRSC2&first=1&tsc=ImageHoverTitle','*https://www.deepl.com/translator#fr/en/###','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','a-zA-ZÀ-ÖØ-öø-ȳáéíóúÁÉÍÓÚñÑ',0,0,0,0,'spacedel');
INSERT INTO languages VALUES(6,'German','https://de.thefreedictionary.com/###','https://www.wordreference.com/deen/###','*https://www.deepl.com/translator#de/en/###','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','a-zA-ZÀ-ÖØ-öø-ȳáéíóúÁÉÍÓÚñÑ',0,0,0,0,'spacedel');
INSERT INTO languages VALUES(7,'Greek','https://www.wordreference.com/gren/###','https://en.wiktionary.org/wiki/###','*https://www.deepl.com/translator#el/en/###','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?;','Mr.|Mrs.|Dr.|[A-Z].|κτλ.|κλπ.|π.χ.|λ.χ.|κ.ά|δηλ.|Κος.|Κ.|Κα.|μ.Χ.|ΥΓ.|μ.μ.|π.μ.|σελ.|κεφ.|βλ.|αι.','α-ωΑ-ΩάόήέώύίΊΏΈΉΌΆΎϊΪϋΫΐΰ',0,0,0,1,'spacedel');
INSERT INTO languages VALUES(8,'Japanese','https://jisho.org/search/###','https://www.bing.com/images/search?q=###&form=HDRSC2&first=1&tsc=ImageHoverTitle','*https://www.deepl.com/translator#jp/en/###','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?。？！','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','\p{Han}\p{Katakana}\p{Hiragana}',0,0,0,1,'japanese');
INSERT INTO languages VALUES(9,'Modern Chinese','https://chinese.yabla.com/chinese-english-pinyin-dictionary.php?define=###','https://www.bing.com/images/search?q=###&form=HDRSC2&first=1&tsc=ImageHoverTitle','*https://www.deepl.com/translator#ch/en/###','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?。！？','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','一-龥',0,0,0,1,'modernchinese');
INSERT INTO languages VALUES(10,'Russian','https://www.dict.com/Russian-English/###','https://en.openrussian.org/?search=###','*https://www.deepl.com/translator#ru/en/###','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','А-Яа-яЁё',0,0,0,0,'spacedel');
INSERT INTO languages VALUES(11,'Spanish','https://es.thefreedictionary.com/###','https://www.wordreference.com/es/en/translation.asp?spen=###','*https://www.deepl.com/translator#es/en/###','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','a-zA-ZÀ-ÖØ-öø-ȳáéíóúÁÉÍÓÚñÑ',0,0,0,0,'spacedel');
INSERT INTO languages VALUES(12,'Turkish','https://www.wordreference.com/tren/###','https://tr.wiktionary.org/###','*https://www.deepl.com/translator#tr/en/###','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','a-zA-ZÀ-ÖØ-öø-ȳáéíóúÁÉÍÓÚñÑğĞıİöÖüÜşŞçÇ',0,0,0,1,'turkish');
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
CREATE TABLE IF NOT EXISTS "bookstats" (
	"BkID" INTEGER NOT NULL  ,
	"wordcount" INTEGER NULL  ,
	"distinctterms" INTEGER NULL  ,
	"distinctunknowns" INTEGER NULL  ,
	"unknownpercent" INTEGER NULL  ,
	PRIMARY KEY ("BkID"),
	FOREIGN KEY("BkID") REFERENCES "books" ("BkID") ON UPDATE NO ACTION ON DELETE CASCADE
);
INSERT INTO bookstats VALUES(1,382,170,170,100);
INSERT INTO bookstats VALUES(2,110,85,85,100);
INSERT INTO bookstats VALUES(3,175,120,120,100);
INSERT INTO bookstats VALUES(4,600,337,337,100);
INSERT INTO bookstats VALUES(5,69,49,49,100);
INSERT INTO bookstats VALUES(6,48,40,40,100);
INSERT INTO bookstats VALUES(7,157,99,99,100);
INSERT INTO bookstats VALUES(8,83,63,63,100);
INSERT INTO bookstats VALUES(9,646,246,246,100);
INSERT INTO bookstats VALUES(10,115,100,100,100);
INSERT INTO bookstats VALUES(11,64,41,41,100);
INSERT INTO bookstats VALUES(12,1242,371,371,100);
INSERT INTO bookstats VALUES(13,67,57,57,100);
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
CREATE TABLE IF NOT EXISTS "books" (
	"BkID" INTEGER NOT NULL  ,
	"BkLgID" INTEGER NOT NULL  ,
	"BkTitle" VARCHAR(200) NOT NULL  ,
	"BkSourceURI" VARCHAR(1000) NULL  ,
	"BkArchived" TINYINT NOT NULL DEFAULT '0' ,
	"BkCurrentTxID" INTEGER NOT NULL DEFAULT '0' , BkWordCount INT, BkAudioFilename TEXT NULL, BkAudioCurrentPos REAL NULL, BkAudioBookmarks TEXT NULL,
	PRIMARY KEY ("BkID"),
	FOREIGN KEY("BkLgID") REFERENCES "languages" ("LgID") ON UPDATE NO ACTION ON DELETE CASCADE
);
INSERT INTO books VALUES(1,2,'逍遙遊',NULL,0,0,382,NULL,NULL,NULL);
INSERT INTO books VALUES(2,12,'Büyük ağaç',NULL,0,0,110,NULL,NULL,NULL);
INSERT INTO books VALUES(3,6,'Die Bremer Stadtmusikanten',NULL,0,0,175,NULL,NULL,NULL);
INSERT INTO books VALUES(4,9,'珍珠鸟',NULL,0,0,600,NULL,NULL,NULL);
INSERT INTO books VALUES(5,5,'Boucles d’or et les trois ours',NULL,0,0,69,NULL,NULL,NULL);
INSERT INTO books VALUES(6,10,'медведь',NULL,0,0,48,NULL,NULL,NULL);
INSERT INTO books VALUES(7,7,'Γεια σου, Νίκη. Ο Πέτρος είμαι.',NULL,0,0,157,NULL,NULL,NULL);
INSERT INTO books VALUES(8,11,'Aladino y la lámpara maravillosa',NULL,0,0,83,NULL,NULL,NULL);
INSERT INTO books VALUES(9,4,'Tutorial follow-up',NULL,0,0,646,NULL,NULL,NULL);
INSERT INTO books VALUES(10,1,'Examples',NULL,0,0,115,NULL,NULL,NULL);
INSERT INTO books VALUES(11,8,'北風と太陽 - きたかぜたいよう',NULL,0,0,64,NULL,NULL,NULL);
INSERT INTO books VALUES(12,4,'Tutorial',NULL,0,0,1242,NULL,NULL,NULL);
INSERT INTO books VALUES(13,3,'Hrad Cimburk – Jak vzal vítr pasáčkovi čepici',NULL,0,0,67,NULL,NULL,NULL);
CREATE TABLE IF NOT EXISTS "wordparents" (
	"WpWoID" INTEGER NOT NULL  ,
	"WpParentWoID" INTEGER NOT NULL  ,
	FOREIGN KEY("WpParentWoID") REFERENCES "words" ("WoID") ON UPDATE NO ACTION ON DELETE CASCADE,
	FOREIGN KEY("WpWoID") REFERENCES "words" ("WoID") ON UPDATE NO ACTION ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "texts" (
	"TxID" INTEGER NOT NULL  ,
	"TxBkID" INTEGER NOT NULL  ,
	"TxOrder" INTEGER NOT NULL  ,
        "TxText" TEXT NOT NULL  ,
	TxReadDate datetime null, TxWordCount INTEGER null,
	PRIMARY KEY ("TxID"),
	FOREIGN KEY("TxBkID") REFERENCES "books" ("BkID") ON UPDATE NO ACTION ON DELETE CASCADE
);
INSERT INTO texts VALUES(1,1,1,'北冥有魚，其名為鯤。鯤之大，不知其幾千里也。化而為鳥，其名為鵬。鵬之背，不知其幾千里也；怒而飛，其翼若垂天之雲。是鳥也，海運則將徙於南冥。南冥者，天池也。齊諧者，志怪者也。諧之言曰：「鵬之徙於南冥也，水擊三千里，摶扶搖而上者九萬里，去以六月息者也。」野馬也，塵埃也，生物之以息相吹也。天之蒼蒼，其正色邪？其遠而無所至極邪？其視下也亦若是，則已矣。且夫水之積也不厚，則負大舟也無力。覆杯水於坳堂之上，則芥為之舟，置杯焉則膠，水淺而舟大也。風之積也不厚，則其負大翼也無力。故九萬里則風斯在下矣，而後乃今培風；背負青天而莫之夭閼者，而後乃今將圖南。',NULL,NULL);
INSERT INTO texts VALUES(2,1,2,'蜩與學鳩笑之曰：「我決起而飛，槍1榆、枋，時則不至而控於地而已矣，奚以之九萬里而南為？」適莽蒼者三湌而反，腹猶果然；適百里者宿舂糧；適千里者三月聚糧。之二蟲又何知！小知不及大知，小年不及大年。奚以知其然也？朝菌不知晦朔，蟪蛄不知春秋，此小年也。楚之南有冥靈者，以五百歲為春，五百歲為秋；上古有大椿者，以八千歲為春，八千歲為秋。而彭祖乃今以久特聞，眾人匹之，不亦悲乎！',NULL,NULL);
INSERT INTO texts VALUES(3,2,1,replace('Büyük ağaç eskiden aşılanmış ve her yıl güzel, iri, pembe şeftaliler verirmiş, insanın eline sığmazmış bu şeftaliler. Öyle güzelmişler ki insan yemeye kıyamazmış onları. Bahçıvan, bu büyük ağacı yabancı bir uzmanın kendi ülkesinden getirdiği bir tohumla aşıladığını söylermiş. Belli ki böyle masraf edilen bir ağaçta yetişen şeftaliler oldukça değerliymiş.\n\nİki ağacın da gövdelerine nazar değmesin diye birer nazarlık asılıymış.\n\nAğaçlardan küçük olanında her yıl bin tane çiçek açarmış ama bir tek şeftali bile yetişmezmiş üzerinde. Ya çiçekleri dökülürmüş, ya da ham şeftaliler kuruyup dallardan düşermiş. Bahçıvan küçük ağaç için elinden geleni yapmış ama değişen bir şey olmamış. Yıllar geçtikçe dalları ve yaprakları çoğalmış ama bir tek şeftali bile görünmemiş üzerinde.','\n',char(10)),NULL,NULL);
INSERT INTO texts VALUES(4,3,1,replace('Es hatte ein Mann einen Esel, der schon lange Jahre die Säcke unverdrossen zur Mühle getragen hatte, dessen Kräfte aber nun zu Ende gingen, so daß er zur Arbeit immer untauglicher ward. Da dachte der Herr daran, ihn aus dem Futter zu schaffen, aber der Esel merkte, daß kein guter Wind wehte, lief fort und machte sich auf den Weg nach Bremen; dort, meinte er, könnte er ja Stadtmusikant werden.\n\nAls er ein Weilchen fortgegangen war, fand er einen Jagdhund auf dem Wege liegen, der jappte wie einer, der sich müde gelaufen hat. "Nun, was jappst du so, Packan?" fragte der Esel. "Ach," sagte der Hund, "weil ich alt bin und jeden Tag schwächer werde, auch auf der Jagd nicht mehr fort kann, hat mich mein Herr wollen totschlagen, da hab ich Reißaus genommen; aber womit soll ich nun mein Brot verdienen?" - "Weißt du was?" sprach der Esel, "ich gehe nach Bremen und werde dort Stadtmusikant, geh mit und laß dich auch bei der Musik annehmen. Ich spiele die Laute und du schlägst die Pauken."','\n',char(10)),NULL,NULL);
INSERT INTO texts VALUES(5,4,1,replace('珍珠鸟\n冯骥才\n\n真好！朋友送我一对珍珠鸟，我把它们养在一个竹条编的笼子里。笼子里有一团干草，那是小鸟又舒适又温暖的巢。\n\n有人说，这是一种害怕人的鸟。\n\n我把笼子挂在窗前。那儿有一盆茂盛的法国吊兰。我让吊兰的长满绿叶的藤蔓覆盖在鸟笼上，珍珠鸟就像躲进幽深的丛林一样安全，从中传出的笛儿般又细又亮的叫声，也就格外轻松自在了。\n\n阳光射进窗来，把吊兰的一串串小叶照得如同碧玉。小鸟的影子就在这中间隐约闪动，看不完整，有时连笼子也看不出，却见它们可爱的鲜红小嘴儿从绿叶中伸出来。\n\n我很少扒开叶蔓瞧它们，它们便渐渐敢伸出小脑袋瞅瞅我。我们就这样一点点熟悉了。\n\n三个月后，那一团愈发繁茂的藤蔓里边，发出一种尖细又娇嫩的叫声。我猜到，是它们有了雏儿。我呢？决不掀开叶片往里看，连添食加水时也不睁大好奇的眼睛去惊动它们。过不多久，忽然有一个小脑袋从叶间探出来。正是它们的雏儿！','\n',char(10)),NULL,NULL);
INSERT INTO texts VALUES(6,4,2,replace('这个小家伙能轻易地由笼子里钻出身。瞧，多么像它的母亲：红嘴红脚，灰蓝色的毛，只是后背还没有生出珍珠似的圆圆的白点。它好肥，整个身子好像一个蓬松的球儿。\n\n起先，这小家伙只在笼子四周活动，随后就在屋里飞来飞去，一会儿落在柜顶上，一会儿神气十足地站在书架上，啄着书背上那些大文豪的名字；一会儿把灯绳撞得来回摇动，跟着又跳到画框上去了。只要大鸟在笼子里叫一声，它立即飞回笼里去。\n\n我不管它。就是打开窗子，它最多只在窗框上站一会儿，决不飞出去。\n\n渐渐地，它胆子大了，有时落在我的书桌上。\n\n它先是离我较远，见我不去伤害它，便一点点挨近，然后蹦到我的杯子上，低下头来喝茶，再偏过脸瞧瞧我的反应。我只是微微一笑，依旧写东西，它就放开胆子跑到稿纸上，绕着我的笔尖蹦来蹦去，跳动的小红爪子在纸上发出嚓嚓的响声。','\n',char(10)),NULL,NULL);
INSERT INTO texts VALUES(7,4,3,replace('我不动声色地写，默默享受着这小家伙亲近的情意。这样，它完全放心了。索性用那涂了蜡似的、角质的小红嘴，“嗒嗒”啄着我颤动的笔尖。我用手摸一摸它细腻的绒毛，它也不怕，反而友好地啄两下我的手指。\n\n白天，它这样淘气地陪伴我；天色暗下来，它就在父母的再三呼唤中，飞向笼子，扭动滚圆的身子，挤开那些绿叶钻进去。\n\n有一天，我伏案写作时，它居然落到我的肩上。我手中的笔不觉停了，生怕吓跑它。过了一会儿，扭头看看，这小家伙竟扒在我的肩头上睡着了，银灰色的眼皮盖住眼睛，小红脚刚好给胸脯上长长的绒毛盖住。我轻轻抬一抬肩，它没醒，睡得好熟！还咂咂嘴，难道在做梦？\n\n我笔尖一动，写下一时的感受：\n\n信赖，往往创造出美好的境界。','\n',char(10)),NULL,NULL);
INSERT INTO texts VALUES(8,5,1,replace('Il était une fois trois ours: un papa ours, une maman ours et un bébé ours. Ils habitaient tous ensemble dans une maison jaune au milieu d''une grande forêt.\n\nUn jour, Maman Ours prépara une grande marmite de porridge délicieux et fumant pour le petit déjeuner. Il était trop chaud pour pouvoir être mangé, alors les ours décidèrent d''aller se promener en attendant que le porridge refroidisse.','\n',char(10)),NULL,NULL);
INSERT INTO texts VALUES(9,6,1,'Встреча с медведем может быть очень опасна. Русские люди любят ходить в лес и собирать грибы и ягоды. Они делают это с осторожностью, так как медведи тоже очень любят ягоды и могут напасть на человека. Медведь ест все: ягоды, рыбу, мясо и даже насекомых. Особенно он любит мед.',NULL,NULL);
INSERT INTO texts VALUES(10,7,1,replace('Πέτρος: Γεια σου, Νίκη. Ο Πέτρος είμαι.\nΝίκη: Α, γεια σου Πέτρο. Τι κάνεις;\nΠέτρος: Μια χαρά. Σε παίρνω για να πάμε καμιά βόλτα αργότερα. Τι λες;\nΝίκη: Α, ωραία. Κι εγώ θέλω να βγω λίγο. Συνέχεια διαβάζω για τις εξετάσεις… κουράστηκα πια. Πού λες να πάμε;\nΠέτρος: Στη γνωστή καφετέρια στην πλατεία. Θα είναι και άλλα παιδιά από την τάξη μας εκεί.\nΝίκη: Ναι; Ποιοι θα είναι;\nΠέτρος: Ο Γιάννης, ο Αντρέας και η Ελπίδα.\nΝίκη: Ωραία. Θα πάτε και πουθενά αλλού μετά;\nΠέτρος: Ναι, λέμε να πάμε στον κινηματογράφο που είναι κοντά στην καφετέρια. Παίζει μια κωμωδία.\nΝίκη: Α, δεν μπορώ να καθίσω έξω μέχρι τόσο αργά. Πρέπει να γυρίσω σπίτι για να διαβάσω.\nΠέτρος: Έλα τώρα. Διαβάζεις αύριο…\nΝίκη: Όχι, όχι, αδύνατον. Είμαι πολύ πίσω στο διάβασμά μου.\nΠέτρος: Καλά, έλα μόνο στην καφετέρια τότε. Θα περάσω να σε πάρω γύρω στις έξι να πάμε μαζί. Εντάξει;\nΝίκη: Εντάξει. Γεια.\nΠέτρο: Τα λέμε. Γεια.','\n',char(10)),NULL,NULL);
INSERT INTO texts VALUES(11,8,1,replace('Érase una vez un muchacho llamado Aladino que vivía en el lejano Oriente con su madre, en una casa sencilla y humilde. Tenían lo justo para vivir, así que cada día, Aladino recorría el centro de la ciudad en busca de algún alimento que llevarse a la boca.\n\nEn una ocasión paseaba entre los puestos de fruta del mercado, cuando se cruzó con un hombre muy extraño con pinta de extranjero. Aladino se quedó sorprendido al escuchar que le llamaba por su nombre.','\n',char(10)),NULL,NULL);
INSERT INTO texts VALUES(12,9,1,replace('Hopefully you''ve gone through the Tutorial, and created some Terms.\n\nFrom the Tutorial, you''ve already told Lute that you know most of the words on this page. You can hover over words to see information about them, such as your information you might have added about dogs.\n\nThere are still a few blue words, which according to Lute are still "unknown" to you. You can process them like you did on the last text.\n\n(fyi - If a text has a spelling mikstaske, you can edit it by clicking the "hamburger menu" -- three lines -- in the top left corner of this screen, and click "Edit page". If you''d like, correct the mistake now, and resave this text.)\n\nNow we''ll do a brief spin through a few other things Lute does. You can read about them and other features in the manual too.\n\n1. The Menus\n\nIn case you missed it, on the Home screen there are some menu bar items on the top right. Go back there and hover over them to see what you can do. This is all demo data, so you can do what you want. (But don''t delete the tutorials until you''ve gone through them.)\n\n2. Term Sentences\n\nIn the "Term" edit form, you can click on the "Sentences" link to see where that term or its relations have been used. Click on "elephant", and then click the Sentences link shown to see where that term has been used.','\n',char(10)),NULL,NULL);
INSERT INTO texts VALUES(13,9,2,replace('You''re only shown sentences on pages that have been marked "Read", using the controls in the footer of the reading screen, i.e. the green checkmark or the ">". This ensures that you only see references that you have already seen before, so you don''t get overwhelmed with new vocabulary, and avoids spoilers of the material you''re reading.\n\n3. Archiving, Unarchiving, and Deleting Books\n\nWhen you''re done reading a book, you can Archive or Delete it.\n\nArchiving just removes the book from your book listing on the home screen, and you can unarchive at any time. The sentences for archived books are still available for searching with the Term "Sentences" link.\n\nOn the last page of every book, Lute shows a link for you to archive the book. You can also archive it from the Home screen by clicking on the "Archive" action (the image with the little down arrow) in the right-most column. To unarchive the text, go to Home, Book Archive, and click the "Unarchive" action (the little up arrow).\n\nDeleting a book completely removes it and its sentences.\n\nNeither archiving nor deleting touch any Terms you''ve created.\n\n4. Audio\n\nYou can add an audio file (mp3, wav, or ogg) to your books, so you can read along to an audio track. See the Lute manual for more notes on usage and tips.\n\n5. Themes and toggling highlighting\n\nLute has a few themes to make reading more pleasant.','\n',char(10)),NULL,NULL);
INSERT INTO texts VALUES(14,9,3,replace('From the "hamburger menu" on the reading screen you can switch to the next theme, or hit the hotkey (m). You can also toggle highlights, because sometimes they get distracting.\n\n===\n\nThose are the the core feature of Lute! There are some sample stories for other languages. Try those out or create your own.\n\nWhen you''re done with the demo, go back to the Home screen and click the link to clear out the database. Lute will delete all of the demo data, and you can get started. You''ll be prompted to create your first language, and then you can create your first book. Lute will then ask you to specify your backup preferences, and with that all done, you''ll be off and running.\n\nThere is a Lute Discord and manual as well -- see the "About" menu bar.\n\nI hope that you find Lute a fun tool to use for learning languages. Cheers and best wishes!','\n',char(10)),NULL,NULL);
INSERT INTO texts VALUES(15,10,1,replace('مرحبا، كيف حالك ؟\nمرحبا, أنا بخير\nهل انت جديدٌ هنا؟ لم أراك من قبل\nانا طالب جديد.لقد وصلت البارحة\nانا محمد, تشرفت بلقائك\n\nشجرة الحياة\n\nتحكي هذه القصة عن ولد صغير يُدعى «يوسف»، يعيش مع أمه الأرملة الفقيرة، يساعدها ويحنو عليها ويحبها حبًا جمًا. وفي يوم من الأيام يصيب المرض أم يوسف ويشتد عليها، ولا يعرف يوسف ماذا يفعل لإنقاذها، فلا يجد أمامه سوى اللجوء إلى الجِنِّيَّة «وِداد» التي تدله على شجرة فيها الشفاء لأمه، هذه الشجرة تقع في أعلى الجبل المقابل لمنزلهم، وعلى يوسف أن يتسلق هذا الجبل ويواجه المخاطر من أجل أن يأتي لأمه بالدواء الموجود في أوراق هذه الشجرة، فهل سينجح يوسف في ذلك؟ وماذا ينتظره من مخاطر وأهوال؟','\n',char(10)),NULL,NULL);
INSERT INTO texts VALUES(16,11,1,replace('北風と太陽\n\n「おれの方が強い。」「いいや、ぼくの方が強い。」\n北風と太陽の声が聞こえます。二人はどちらの力が強いかでケンカをしているようです。\n「太陽が毎日元気だから、暑くてみんな困っているよ。おれが涼しい風を吹くと、みんな嬉しそうだ。」','\n',char(10)),NULL,NULL);
INSERT INTO texts VALUES(17,12,1,replace('Welcome to Lute! This short guide should get you going.\n\nNavigation\n\nThis tutorial has multiple pages. Above the title are some arrows to navigate forwards and backwards. In longer texts, you can jump forward or back ten pages at a time as well.\n\n1. The Basics\n\nAll of these words are blue because they are "unknown" - according to Lute, this is the first time you''re seeing these words.\n\nYou can click on a word, and create a definition. For example, click on this word: elephant.\n\nWhen the form pops up in the right-hand frame, a dictionary is loaded below. Copy-paste something from the dictionary into the translation, or make up your own, mark the status, add some tags if you want (eg, type "noun" in the tags field), and click save. From now on, every English text that you read that contains the word "elephant" will show the status. If you hover over any "elephant", you''ll see some information.\n\n1.1 Multiple dictionaries.\n\nNext to the term is a small arrow, "Lookup". If you click on this repeatedly, Lute cycles through the dictionaries that you configure for the language in the "Languages" link on the homepage.\n\n1.2 Images\n\nFor this demo, English has been configured to do an image search for the second English dictionary, so if you click on the arrow, you''ll see some happy elephants (if you clicked on elephant!).','\n',char(10)),NULL,NULL);
INSERT INTO texts VALUES(18,12,2,replace('You can also click on the little "eye icon" next to the term, and it opens up a common image search URL.\n\nIn either case, if you click on one of the images shown in the list, that image is saved in your data/userimages folder. When you hover over the word in the reading pane, that picture is included in the word hover. Try adding an image for your elephant by clicking on the term, clicking the eye icon, and clicking a picture you like. Then hover over your elephant.\n\nNote: sometimes these images make _no sense_ -- it''s using Bing image search, and it does the best it can with the limited context it has.\n\n2. Multi-word Terms\n\nYou can create multi-word terms by clicking and dragging across multiple words, then release the mouse. Try creating a term for the phrase "the cat''s pyjamas", and add a translation and set the status.\n\n(A brief side note: Lute keeps track of where you are in any text. If you click the Home link above to leave this tutorial, and later click the Tutorial link from the Text listing, Lute will open the last page you were at.)\n\n3. Parent Terms\n\nSometimes it helps to associate terms with a "parent". For example, the verb "to have" is conjugated in various forms as "I have a cold", "he has a dog", "they had dinner". First create a Term for "have".','\n',char(10)),NULL,NULL);
INSERT INTO texts VALUES(19,12,3,replace('Then create a Term for "has", and in the Parent field start typing "have". Lute will show the existing Term "have" in the drop down, and if you select it, "has" will be associated with that on save, and when you hover over "has" you''ll see the parent''s information as well.\n\nIf you enter a non-existent Parent word, Lute will create a placeholder Term for that Parent, copying some content from your term. For example, try creating a Term for the word "dogs", associating it with the non-existent Term "dog". When you save "dogs", both will be updated.\n\nTerms can have multiple parents, too. Hit the Enter (or Return) key after each parent. For example, if you wanted to associate the Term "puppies" with both "puppy" and "dog", click on "puppies", and in the Parents text box type "puppy", hit Enter, type "dog", and hit Enter. Sometimes this is necessary: for example, in Spanish, "se sienta" can either be a conjugation of "sentirse" (to feel) or "sentarse" (to sit), depending on the context.\n\n4. Mark the remainder as "Well Known"\n\nWhen you''re done creating Terms on a page, you will likely still have a bunch of blue words, or "unknowns", left over, even though you really know these words. You can set all of these to "Well Known" and move to the next page in one shot with the green checkmark at the bottom of the page.','\n',char(10)),NULL,NULL);
INSERT INTO texts VALUES(20,12,4,replace('Try that now to see what happens, and then come back to this page using the arrows in the header to finish reading this page.\n\nThe ">" link moves to the next page as well, without setting the unknown terms to "Well Known." This can be useful if you''re reading quickly, without stopping to define every last term in detail.\n\nNote: both of these links also mark the page as "Read", which Lute uses when it searches for references to terms you create. There''s more on this in the tutorial follow-up, which you should read after this tutorial.\n\n5. Keyboard shortcuts\n\nThe small blue question mark in the header shows some keyboard shortcuts.\n\n5.1 Updating Status\n\nIf you''ve worked through the tutorial, you''ll have noted that words are underlined in blue when you move the mouse over them. You can quickly change the status of the current word by hitting 1, 2, 3, 4, 5, w (for Well-Known), or i (for Ignore). Try hovering over the following words and hit the status buttons: apple, banana, cranberry, donut.\n\nIf you click on a word, it''s underlined in red, and the Term edit form is shown. Before you switch over to the Term editing form, you can still update its status using the hotkeys above, or by using the up and down arrows. You can jump over to the edit form by hitting Tab, and then start editing.\n\nWhen a word has been clicked, it''s "active", so it keeps the focus.','\n',char(10)),NULL,NULL);
INSERT INTO texts VALUES(21,12,5,replace('Hovering the mouse over other words won''t underline them in blue anymore, and hitting status update hotkeys (1 - 5, w, i) will only update the active word. To "un-click" a word underlined in red, click it again, or hit Escape or Return. Then you''ll be back in "Hover mode". In "Hover mode", the hotkeys 1-5, w, and i still update the status, but the arrow keys just scroll the window. Try clicking and un-clicking or Escaping any word in this paragraph to get a feel for it.\n\nNote that for the keyboard shortcuts to work, the reading pane (where the text is) must have the "focus". Click anywhere on the reading pane to re-establish focus.\n\n5.1 Bulk updates\n\nIf you hold down Shift and click a bunch of words, you can bulk update their statuses. This works for the up and down arrow keys as well.\n\n5.2 Arrow keys\n\nThe Right and Left arrow keys click the next and previous words. Hit Escape or Return to get back to "hover mode".\n\n5.3 Copying text\n\nWhen a word is hovered over or clicked, hit "c" to copy that word''s sentence to your clipboard. Hit "C" to copy the word''s full paragraph (multiple sentences). You can also copy arbitrary sections of text by holding down the Shift key while highlighting the text with your mouse.\n\n6. Next steps\n\nAll done this text!','\n',char(10)),NULL,NULL);
INSERT INTO texts VALUES(22,12,6,replace('Lute keeps track of all of this in your database, so any time you create or import a new Book, all the info you''ve created is carried forward.\n\nThere''s a tutorial follow-up: go to the Home screen, and click the "Tutorial follow-up" in the table.','\n',char(10)),NULL,NULL);
INSERT INTO texts VALUES(23,13,1,'V jedné rozpadlé chaloupce žil tatínek, maminka a jejich chlapec Tonda. Byli velmi chudí, do střechy jim teklo a často neměli ani na jídlo. Tonda, aby rodičům pomohl, pracoval jako pasáček ovcí. Ale i tak neměl ani na pořádné oblečení, chodil v roztrhaných kalhotách, do kabátku mu táhlo a jeho čepice vypadala stejně otrhaně jako zbytek oděvu. I přesto si každé ráno cestou na pastvu vesele pohvizdoval.',NULL,NULL);
CREATE TABLE IF NOT EXISTS "settings" (
	"StKey" VARCHAR(40) NOT NULL,
        "StKeyType" TEXT NOT NULL,
	"StValue" TEXT NULL,
	PRIMARY KEY ("StKey")
);
INSERT INTO settings VALUES('IsDemoData','system','1');
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
