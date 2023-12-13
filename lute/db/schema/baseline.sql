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
INSERT INTO languages VALUES(9,'Russian','https://www.dict.com/Russian-English/###','https://en.openrussian.org/?search=###','*https://www.deepl.com/translator#ru/en/###','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','А-Яа-яЁё',0,0,0,0,'spacedel');
INSERT INTO languages VALUES(10,'Spanish','https://es.thefreedictionary.com/###','https://www.wordreference.com/es/en/translation.asp?spen=###','*https://www.deepl.com/translator#es/en/###','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','a-zA-ZÀ-ÖØ-öø-ȳáéíóúÁÉÍÓÚñÑ',0,0,0,0,'spacedel');
INSERT INTO languages VALUES(11,'Turkish','https://www.wordreference.com/tren/###','https://tr.wiktionary.org/###','*https://www.deepl.com/translator#tr/en/###','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','a-zA-ZÀ-ÖØ-öø-ȳáéíóúÁÉÍÓÚñÑğĞıİöÖüÜşŞçÇ',0,0,0,1,'turkish');
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
INSERT INTO bookstats VALUES(1,67,57,57,100);
INSERT INTO bookstats VALUES(2,382,170,170,100);
INSERT INTO bookstats VALUES(3,83,63,63,100);
INSERT INTO bookstats VALUES(4,48,40,40,100);
INSERT INTO bookstats VALUES(5,1161,357,357,100);
INSERT INTO bookstats VALUES(6,489,191,191,100);
INSERT INTO bookstats VALUES(7,157,99,99,100);
INSERT INTO bookstats VALUES(8,115,100,100,100);
INSERT INTO bookstats VALUES(9,110,85,85,100);
INSERT INTO bookstats VALUES(10,175,120,120,100);
INSERT INTO bookstats VALUES(11,69,49,49,100);
INSERT INTO bookstats VALUES(12,64,41,41,100);
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
INSERT INTO books VALUES(1,3,'Hrad Cimburk – Jak vzal vítr pasáčkovi čepici',NULL,0,0,67,NULL,NULL,NULL);
INSERT INTO books VALUES(2,2,'逍遙遊',NULL,0,0,382,NULL,NULL,NULL);
INSERT INTO books VALUES(3,10,'Aladino y la lámpara maravillosa',NULL,0,0,83,NULL,NULL,NULL);
INSERT INTO books VALUES(4,9,'медведь',NULL,0,0,48,NULL,NULL,NULL);
INSERT INTO books VALUES(5,4,'Tutorial',NULL,0,0,1161,NULL,NULL,NULL);
INSERT INTO books VALUES(6,4,'Tutorial follow-up',NULL,0,0,489,NULL,NULL,NULL);
INSERT INTO books VALUES(7,7,'Γεια σου, Νίκη. Ο Πέτρος είμαι.',NULL,0,0,157,NULL,NULL,NULL);
INSERT INTO books VALUES(8,1,'Examples',NULL,0,0,115,NULL,NULL,NULL);
INSERT INTO books VALUES(9,11,'Büyük ağaç',NULL,0,0,110,NULL,NULL,NULL);
INSERT INTO books VALUES(10,6,'Die Bremer Stadtmusikanten',NULL,0,0,175,NULL,NULL,NULL);
INSERT INTO books VALUES(11,5,'Boucles d’or et les trois ours',NULL,0,0,69,NULL,NULL,NULL);
INSERT INTO books VALUES(12,8,'北風と太陽 - きたかぜたいよう',NULL,0,0,64,NULL,NULL,NULL);
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
INSERT INTO texts VALUES(1,1,1,'V jedné rozpadlé chaloupce žil tatínek, maminka a jejich chlapec Tonda. Byli velmi chudí, do střechy jim teklo a často neměli ani na jídlo. Tonda, aby rodičům pomohl, pracoval jako pasáček ovcí. Ale i tak neměl ani na pořádné oblečení, chodil v roztrhaných kalhotách, do kabátku mu táhlo a jeho čepice vypadala stejně otrhaně jako zbytek oděvu. I přesto si každé ráno cestou na pastvu vesele pohvizdoval.',NULL,NULL);
INSERT INTO texts VALUES(2,2,1,'北冥有魚，其名為鯤。鯤之大，不知其幾千里也。化而為鳥，其名為鵬。鵬之背，不知其幾千里也；怒而飛，其翼若垂天之雲。是鳥也，海運則將徙於南冥。南冥者，天池也。齊諧者，志怪者也。諧之言曰：「鵬之徙於南冥也，水擊三千里，摶扶搖而上者九萬里，去以六月息者也。」野馬也，塵埃也，生物之以息相吹也。天之蒼蒼，其正色邪？其遠而無所至極邪？其視下也亦若是，則已矣。且夫水之積也不厚，則負大舟也無力。覆杯水於坳堂之上，則芥為之舟，置杯焉則膠，水淺而舟大也。風之積也不厚，則其負大翼也無力。故九萬里則風斯在下矣，而後乃今培風；背負青天而莫之夭閼者，而後乃今將圖南。',NULL,NULL);
INSERT INTO texts VALUES(3,2,2,'蜩與學鳩笑之曰：「我決起而飛，槍1榆、枋，時則不至而控於地而已矣，奚以之九萬里而南為？」適莽蒼者三湌而反，腹猶果然；適百里者宿舂糧；適千里者三月聚糧。之二蟲又何知！小知不及大知，小年不及大年。奚以知其然也？朝菌不知晦朔，蟪蛄不知春秋，此小年也。楚之南有冥靈者，以五百歲為春，五百歲為秋；上古有大椿者，以八千歲為春，八千歲為秋。而彭祖乃今以久特聞，眾人匹之，不亦悲乎！',NULL,NULL);
INSERT INTO texts VALUES(4,3,1,replace('Érase una vez un muchacho llamado Aladino que vivía en el lejano Oriente con su madre, en una casa sencilla y humilde. Tenían lo justo para vivir, así que cada día, Aladino recorría el centro de la ciudad en busca de algún alimento que llevarse a la boca.\n\nEn una ocasión paseaba entre los puestos de fruta del mercado, cuando se cruzó con un hombre muy extraño con pinta de extranjero. Aladino se quedó sorprendido al escuchar que le llamaba por su nombre.','\n',char(10)),NULL,NULL);
INSERT INTO texts VALUES(5,4,1,'Встреча с медведем может быть очень опасна. Русские люди любят ходить в лес и собирать грибы и ягоды. Они делают это с осторожностью, так как медведи тоже очень любят ягоды и могут напасть на человека. Медведь ест все: ягоды, рыбу, мясо и даже насекомых. Особенно он любит мед.',NULL,NULL);
INSERT INTO texts VALUES(6,5,1,replace('Welcome to Lute! This short guide should get you going.\n\nNavigation\n\nThis tutorial has multiple pages. Above the title are some arrows to navigate forwards and backwards. In longer texts, you can jump forward or back ten pages at a time as well.\n\n1. The Basics\n\nAll of these words are blue because they are "unknown" - according to Lute, this is the first time you''re seeing these words.\n\nYou can click on a word, and create a definition. For example, click on this word: elephant.\n\nWhen the form pops up in the right-hand frame, a dictionary is loaded below. Copy-paste something from the dictionary into the translation, or make up your own, mark the status, add some tags if you want (eg, type "noun" in the tags field), and click save. From now on, every English text that you read that contains the word "elephant" will show the status. If you hover over any "elephant", you''ll see some information.\n\n1.1 Multiple dictionaries.\n\nNext to the term is a small arrow, "Lookup". If you click on this repeatedly, Lute cycles through the dictionaries that you configure for the language in the "Languages" link on the homepage.\n\n1.2 Images\n\nFor this demo, English has been configured to do an image search for the second English dictionary, so if you click on the arrow, you''ll see some happy elephants (if you clicked on elephant!).','\n',char(10)),NULL,NULL);
INSERT INTO texts VALUES(7,5,2,replace('You can also click on the little "eye icon" next to the term, and it opens up a common image search URL.\n\nIn either case, if you click on one of the images shown in the list, that image is saved in your data/userimages folder. When you hover over the word in the reading pane, that picture is included in the word hover. Try adding an image for your elephant by clicking on the term, clicking the eye icon, and clicking a picture you like. Then hover over your elephant.\n\nNote: sometimes these images make _no sense_ -- it''s using Bing image search, and it does the best it can with the limited context it has.\n\n2. Multi-word Terms\n\nYou can create multi-word terms by clicking and dragging across multiple words, then release the mouse. Try creating a term for the phrase "the cat''s pyjamas", and add a translation and set the status.\n\n(A brief side note: Lute keeps track of where you are in any text. If you click the Home link above to leave this tutorial, and later click the Tutorial link from the Text listing, Lute will open the last page you were at.)\n\n3. Parent Terms\n\nSometimes it helps to associate terms with a "parent". For example, the verb "to have" is conjugated in various forms as "I have a cold", "he has a dog", "they had dinner". First create a Term for "have".','\n',char(10)),NULL,NULL);
INSERT INTO texts VALUES(8,5,3,replace('Then create a Term for "has", and in the Parent field start typing "have". Lute will show the existing Term "have" in the drop down, and if you select it, "has" will be associated with that on save, and when you hover over "has" you''ll see the parent''s information as well.\n\nIf you enter a non-existent Parent word, Lute will create a placeholder Term for that Parent, copying some content from your term. For example, try creating a Term for the word "dogs", associating it with the non-existent Term "dog". When you save "dogs", both will be updated.\n\nTerms can have multiple parents, too. Hit the Enter (or Return) key after each parent. For example, if you wanted to associate the Term "puppies" with both "puppy" and "dog", click on "puppies", and in the Parents text box type "puppy", hit Enter, type "dog", and hit Enter. Sometimes this is necessary: for example, in Spanish, "se sienta" can either be a conjugation of "sentirse" (to feel) or "sentarse" (to sit), depending on the context.\n\n4. Mark the remainder as "Well Known"\n\nWhen you''re done creating Terms on a page, you will likely still have a bunch of blue words, or "unknowns", left over, even though you really know these words. You can set all of these to "Well Known" in one shot with the green checkmark at the bottom of the page ("Mark rest as known"). Try that now to see what happens.','\n',char(10)),NULL,NULL);
INSERT INTO texts VALUES(9,5,4,replace('This button only affects words on the current page, so when you go to the next page, you''ll see that some words are still unknown.\n\nThere are other buttons at the bottom of the page. The green checkmark with the arrow sets the remaining unknowns on the current page, and also goes to the next page.\n\n5. Keyboard shortcuts\n\nThe small blue question mark in the header shows some keyboard shortcuts.\n\n5.1 Updating Status\n\nIf you''ve worked through the tutorial, you''ll have noted that words are underlined in blue when you move the mouse over them. You can quickly change the status of the current word by hitting 1, 2, 3, 4, 5, w (for Well-Known), or i (for Ignore). Try hovering over the following words and hit the status buttons: apple, banana, cranberry, donut.\n\nIf you click on a word, it''s underlined in red, and the Term edit form is shown. (Before you switch over to the Term editing form, you can still update its status.) You can jump over to the edit form by hitting Tab, and then start editing.\n\nWhen a word has been clicked, it''s "active", so it keeps the focus. Hovering the mouse over other words won''t underline them in blue anymore, and hitting status update hotkeys (1 - 5, w, i) will only update the active word. To "un-click" a word underlined in red, click it again, or hit Escape or Return. Then you''ll be back in "Hover mode".','\n',char(10)),NULL,NULL);
INSERT INTO texts VALUES(10,5,5,replace('Try clicking and un-clicking or Escaping any word in this paragraph to get a feel for it.\n\nNote that for the keyboard shortcuts to work, the reading pane (where the text is) must have the "focus". Click anywhere on the reading pane to re-establish focus.\n\n5.1 Bulk updates\n\nIf you hold down Shift and click a bunch of words, you can bulk update their statuses.\n\n5.2 Arrow keys\n\nThe Right and Left arrow keys click the next and previous words. Hit Escape or Return to get back to "hover mode".\n\n5.3 Copying text\n\nWhen a word is hovered over or clicked, hit "c" to copy that word''s sentence to your clipboard. Hit "C" to copy the word''s full paragraph (multiple sentences). You can also copy arbitrary sections of text by holding down the Shift key while highlighting the text with your mouse.\n\n6. Next steps\n\nAll done this text!\n\nLute keeps track of all of this in your database, so any time you create or import a new Book, all the info you''ve created is carried forward.\n\nThere''s a tutorial follow-up: go to the Home screen, and click the "Tutorial follow-up" in the table.','\n',char(10)),NULL,NULL);
INSERT INTO texts VALUES(11,6,1,replace('Hopefully you''ve gone through the Tutorial, and created some Terms.\n\nFrom the Tutorial, you''ve already told Lute that you know most of the words on this page. You can hover over words to see information about them, such as your information you might have added about dogs.\n\nThere are still a few blue words, which according to Lute are still "unknown" to you. You can process them like you did on the last text.\n\n(fyi - If a text has a spelling mikstaske, you can edit it by clicking the small Edit icon next to the title. If you''d like, correct the mistake now, and resave this text.)\n\n\nAppendix: A few other things\n\nA0. In case you missed it, on the Home screen there are some menu bar items on the top right. Go back there and hover over them to see what you can do. This is all demo data, so you can do what you want. (But don''t delete the tutorials until you''ve gone through them.)\n\nA1. Term sentences\n\nIn the "Term" edit form, you can click on the "Sentences" link to see where that term or its relations have been used. Click on "elephant", and then click the Sentences link shown to see where that term has been used.\n\nA2. Archiving, Unarchiving, and Deleting Texts\n\nWhen you''re done reading a text, you can either Archive it, or Delete it.','\n',char(10)),NULL,NULL);
INSERT INTO texts VALUES(12,6,2,replace('Archiving clears out the parsing data for a given text, but the text is still available and can be unarchived and re-read. The sentences are also available for searching with the Term "Sentences" link. Deletion completely removes a text, the parsing data, and its sentences. Neither archiving nor deleting touch any Terms you''ve created, it just clears out the texts.\n\nOn the last page of every book, Lute shows a link for you to archive the book. You can also delete it from the Home screen by clicking on the "Archive" action (the image with the little down arrow) in the right-most column.\n\nTo unarchive the text, go to Home, Text Archive, and click the "Unarchive" action (the little up arrow).\n\n\n\n===\n\nThose are the the core feature of Lute! There are some sample stories for other languages. Try those out or create your own.\n\nWhen you''re done with the demo, go back to the Home screen and click the link to clear out the database. Lute will delete all of the demo data, and you can get started. You''ll be prompted to create your first language, and then you can create your first book. Lute will then ask you to specify your backup preferences, and with that all done, you''ll be off and running.\n\nThere is a Lute Discord and Wiki as well -- see the "About" menu bar.\n\nI hope that you find Lute a fun tool to use for learning languages.','\n',char(10)),NULL,NULL);
INSERT INTO texts VALUES(13,6,3,'Cheers and best wishes!',NULL,NULL);
INSERT INTO texts VALUES(14,7,1,replace('Πέτρος: Γεια σου, Νίκη. Ο Πέτρος είμαι.\nΝίκη: Α, γεια σου Πέτρο. Τι κάνεις;\nΠέτρος: Μια χαρά. Σε παίρνω για να πάμε καμιά βόλτα αργότερα. Τι λες;\nΝίκη: Α, ωραία. Κι εγώ θέλω να βγω λίγο. Συνέχεια διαβάζω για τις εξετάσεις… κουράστηκα πια. Πού λες να πάμε;\nΠέτρος: Στη γνωστή καφετέρια στην πλατεία. Θα είναι και άλλα παιδιά από την τάξη μας εκεί.\nΝίκη: Ναι; Ποιοι θα είναι;\nΠέτρος: Ο Γιάννης, ο Αντρέας και η Ελπίδα.\nΝίκη: Ωραία. Θα πάτε και πουθενά αλλού μετά;\nΠέτρος: Ναι, λέμε να πάμε στον κινηματογράφο που είναι κοντά στην καφετέρια. Παίζει μια κωμωδία.\nΝίκη: Α, δεν μπορώ να καθίσω έξω μέχρι τόσο αργά. Πρέπει να γυρίσω σπίτι για να διαβάσω.\nΠέτρος: Έλα τώρα. Διαβάζεις αύριο…\nΝίκη: Όχι, όχι, αδύνατον. Είμαι πολύ πίσω στο διάβασμά μου.\nΠέτρος: Καλά, έλα μόνο στην καφετέρια τότε. Θα περάσω να σε πάρω γύρω στις έξι να πάμε μαζί. Εντάξει;\nΝίκη: Εντάξει. Γεια.\nΠέτρο: Τα λέμε. Γεια.','\n',char(10)),NULL,NULL);
INSERT INTO texts VALUES(15,8,1,replace('مرحبا، كيف حالك ؟\nمرحبا, أنا بخير\nهل انت جديدٌ هنا؟ لم أراك من قبل\nانا طالب جديد.لقد وصلت البارحة\nانا محمد, تشرفت بلقائك\n\nشجرة الحياة\n\nتحكي هذه القصة عن ولد صغير يُدعى «يوسف»، يعيش مع أمه الأرملة الفقيرة، يساعدها ويحنو عليها ويحبها حبًا جمًا. وفي يوم من الأيام يصيب المرض أم يوسف ويشتد عليها، ولا يعرف يوسف ماذا يفعل لإنقاذها، فلا يجد أمامه سوى اللجوء إلى الجِنِّيَّة «وِداد» التي تدله على شجرة فيها الشفاء لأمه، هذه الشجرة تقع في أعلى الجبل المقابل لمنزلهم، وعلى يوسف أن يتسلق هذا الجبل ويواجه المخاطر من أجل أن يأتي لأمه بالدواء الموجود في أوراق هذه الشجرة، فهل سينجح يوسف في ذلك؟ وماذا ينتظره من مخاطر وأهوال؟','\n',char(10)),NULL,NULL);
INSERT INTO texts VALUES(16,9,1,replace('Büyük ağaç eskiden aşılanmış ve her yıl güzel, iri, pembe şeftaliler verirmiş, insanın eline sığmazmış bu şeftaliler. Öyle güzelmişler ki insan yemeye kıyamazmış onları. Bahçıvan, bu büyük ağacı yabancı bir uzmanın kendi ülkesinden getirdiği bir tohumla aşıladığını söylermiş. Belli ki böyle masraf edilen bir ağaçta yetişen şeftaliler oldukça değerliymiş.\n\nİki ağacın da gövdelerine nazar değmesin diye birer nazarlık asılıymış.\n\nAğaçlardan küçük olanında her yıl bin tane çiçek açarmış ama bir tek şeftali bile yetişmezmiş üzerinde. Ya çiçekleri dökülürmüş, ya da ham şeftaliler kuruyup dallardan düşermiş. Bahçıvan küçük ağaç için elinden geleni yapmış ama değişen bir şey olmamış. Yıllar geçtikçe dalları ve yaprakları çoğalmış ama bir tek şeftali bile görünmemiş üzerinde.','\n',char(10)),NULL,NULL);
INSERT INTO texts VALUES(17,10,1,replace('Es hatte ein Mann einen Esel, der schon lange Jahre die Säcke unverdrossen zur Mühle getragen hatte, dessen Kräfte aber nun zu Ende gingen, so daß er zur Arbeit immer untauglicher ward. Da dachte der Herr daran, ihn aus dem Futter zu schaffen, aber der Esel merkte, daß kein guter Wind wehte, lief fort und machte sich auf den Weg nach Bremen; dort, meinte er, könnte er ja Stadtmusikant werden.\n\nAls er ein Weilchen fortgegangen war, fand er einen Jagdhund auf dem Wege liegen, der jappte wie einer, der sich müde gelaufen hat. "Nun, was jappst du so, Packan?" fragte der Esel. "Ach," sagte der Hund, "weil ich alt bin und jeden Tag schwächer werde, auch auf der Jagd nicht mehr fort kann, hat mich mein Herr wollen totschlagen, da hab ich Reißaus genommen; aber womit soll ich nun mein Brot verdienen?" - "Weißt du was?" sprach der Esel, "ich gehe nach Bremen und werde dort Stadtmusikant, geh mit und laß dich auch bei der Musik annehmen. Ich spiele die Laute und du schlägst die Pauken."','\n',char(10)),NULL,NULL);
INSERT INTO texts VALUES(18,11,1,replace('Il était une fois trois ours: un papa ours, une maman ours et un bébé ours. Ils habitaient tous ensemble dans une maison jaune au milieu d''une grande forêt.\n\nUn jour, Maman Ours prépara une grande marmite de porridge délicieux et fumant pour le petit déjeuner. Il était trop chaud pour pouvoir être mangé, alors les ours décidèrent d''aller se promener en attendant que le porridge refroidisse.','\n',char(10)),NULL,NULL);
INSERT INTO texts VALUES(19,12,1,replace('北風と太陽\n\n「おれの方が強い。」「いいや、ぼくの方が強い。」\n北風と太陽の声が聞こえます。二人はどちらの力が強いかでケンカをしているようです。\n「太陽が毎日元気だから、暑くてみんな困っているよ。おれが涼しい風を吹くと、みんな嬉しそうだ。」','\n',char(10)),NULL,NULL);
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
