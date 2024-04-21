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
INSERT INTO _migrations VALUES('20240101_122610_add_bookstats_status_distribution.sql');
INSERT INTO _migrations VALUES('20240118_154258_change_status_abbrev.sql');
INSERT INTO _migrations VALUES('20240113_215142_add_term_follow_parent_bool.sql');
INSERT INTO _migrations VALUES('20240125_drop_BkWordCount.sql');
INSERT INTO _migrations VALUES('20240125_drop_bookstats_wordcount.sql');
INSERT INTO _migrations VALUES('20240207_01_create_languagedicts.sql');
INSERT INTO _migrations VALUES('20240207_02_drop_old_language_fields.sql');
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
INSERT INTO statuses VALUES(98,'Ignored','I');
INSERT INTO statuses VALUES(99,'Well Known','W');
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
	"WoStatusChanged" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, WoSyncStatus INTEGER NOT NULL DEFAULT 0,
	FOREIGN KEY("WoLgID") REFERENCES "languages" ("LgID") ON UPDATE NO ACTION ON DELETE CASCADE
);
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
INSERT INTO texts VALUES(1,1,1,replace('مرحبا، كيف حالك ؟\nمرحبا, أنا بخير\nهل انت جديدٌ هنا؟ لم أراك من قبل\nانا طالب جديد.لقد وصلت البارحة\nانا محمد, تشرفت بلقائك\n\nشجرة الحياة\n\nتحكي هذه القصة عن ولد صغير يُدعى «يوسف»، يعيش مع أمه الأرملة الفقيرة، يساعدها ويحنو عليها ويحبها حبًا جمًا. وفي يوم من الأيام يصيب المرض أم يوسف ويشتد عليها، ولا يعرف يوسف ماذا يفعل لإنقاذها، فلا يجد أمامه سوى اللجوء إلى الجِنِّيَّة «وِداد» التي تدله على شجرة فيها الشفاء لأمه، هذه الشجرة تقع في أعلى الجبل المقابل لمنزلهم، وعلى يوسف أن يتسلق هذا الجبل ويواجه المخاطر من أجل أن يأتي لأمه بالدواء الموجود في أوراق هذه الشجرة، فهل سينجح يوسف في ذلك؟ وماذا ينتظره من مخاطر وأهوال؟','\n',char(10)),NULL,115);
INSERT INTO texts VALUES(2,2,1,'北冥有魚，其名為鯤。鯤之大，不知其幾千里也。化而為鳥，其名為鵬。鵬之背，不知其幾千里也；怒而飛，其翼若垂天之雲。是鳥也，海運則將徙於南冥。南冥者，天池也。齊諧者，志怪者也。諧之言曰：「鵬之徙於南冥也，水擊三千里，摶扶搖而上者九萬里，去以六月息者也。」野馬也，塵埃也，生物之以息相吹也。天之蒼蒼，其正色邪？其遠而無所至極邪？其視下也亦若是，則已矣。且夫水之積也不厚，則負大舟也無力。覆杯水於坳堂之上，則芥為之舟，置杯焉則膠，水淺而舟大也。風之積也不厚，則其負大翼也無力。故九萬里則風斯在下矣，而後乃今培風；背負青天而莫之夭閼者，而後乃今將圖南。',NULL,228);
INSERT INTO texts VALUES(3,2,2,'蜩與學鳩笑之曰：「我決起而飛，槍1榆、枋，時則不至而控於地而已矣，奚以之九萬里而南為？」適莽蒼者三湌而反，腹猶果然；適百里者宿舂糧；適千里者三月聚糧。之二蟲又何知！小知不及大知，小年不及大年。奚以知其然也？朝菌不知晦朔，蟪蛄不知春秋，此小年也。楚之南有冥靈者，以五百歲為春，五百歲為秋；上古有大椿者，以八千歲為春，八千歲為秋。而彭祖乃今以久特聞，眾人匹之，不亦悲乎！',NULL,154);
INSERT INTO texts VALUES(4,3,1,'V jedné rozpadlé chaloupce žil tatínek, maminka a jejich chlapec Tonda. Byli velmi chudí, do střechy jim teklo a často neměli ani na jídlo. Tonda, aby rodičům pomohl, pracoval jako pasáček ovcí. Ale i tak neměl ani na pořádné oblečení, chodil v roztrhaných kalhotách, do kabátku mu táhlo a jeho čepice vypadala stejně otrhaně jako zbytek oděvu. I přesto si každé ráno cestou na pastvu vesele pohvizdoval.',NULL,67);
INSERT INTO texts VALUES(5,4,1,replace('Welcome to Lute! This short guide should get you going.\n\nNavigation\nThis tutorial has multiple pages. At the top of the page is a slider to navigate forwards and backwards, or you can click the arrows at either end of the slider.\n\n1. The Basics\nAll of these words are blue because they are "unknown" - according to Lute, this is the first time you''re seeing these words.\nYou can click on a word, and create a definition. For example, click on this word: elephant.\nWhen the form pops up in the right-hand frame, a dictionary is loaded below. Copy-paste something from the dictionary into the translation, or make up your own, mark the status, add some tags if you want (eg, type "noun" in the tags field), and click save. From now on, every English text that you read that contains the word "elephant" will show the status. If you hover over any "elephant", you''ll see some information.\n\n1.1 Multiple dictionaries.\nLanguages can have multiple dictionaries, configured in the "Languages" link on the homepage. Each dictionary is shown as a small tab. For this demo, English has been configured with two dictionaries. The second dictionary will open a popup window. If you have many dictionaries, the extra ones will be shown in a small list box next to the tabs.\n\n1.2 Images\nLute can do a simple image search for terms. Next to the Sentences tab is a small image button.','\n',char(10)),NULL,242);
INSERT INTO texts VALUES(6,4,2,replace('If you click on it, you''ll see some happy elephants (if you clicked on elephant!). If you click on one of the images shown in the list, that image is saved in your data/userimages folder. When you hover over the word in the reading pane, that picture is included in the word hover. Try adding an image for your elephant by clicking on the term, clicking the image icon, and clicking a picture you like. Then hover over your elephant.\nNote: sometimes these images make _no sense_ -- it''s using Bing image search, and it does the best it can with the limited context it has.\nTo delete an image added to your term, click on it. Its border will change to red. Hit Delete or Backspace to delete it, and then save the term (you must save!).\n\n2. Multi-word Terms\nYou can create multi-word terms by clicking and dragging across multiple words, then release the mouse. Try creating a term for the phrase "the cat''s pyjamas", and add a translation and set the status.\n(A brief side note: Lute keeps track of where you are in any text. If you click the Home link above to leave this tutorial, and later click the Tutorial link from the Text listing, Lute will open the last page you were at.)\n\n3. Parent Terms\nSometimes it helps to associate terms with a "parent".','\n',char(10)),NULL,234);
INSERT INTO texts VALUES(7,4,3,replace('For example, the verb "to have" is conjugated in various forms as "I have a cold", "he has a dog", "they had dinner". First create a Term for "have". Then create a Term for "has", and in the Parent field start typing "have". Lute will show the existing Term "have" in the drop down, and if you select it, "has" will be associated with that on save, and when you hover over "has" you''ll see the parent''s information as well.\nIf you enter a non-existent Parent word, Lute will create a placeholder Term for that Parent, copying some content from your term. For example, try creating a Term for the word "dogs", associating it with the non-existent Term "dog". When you save "dogs", both will be updated.\nTerms can have multiple parents, too. Hit the Enter (or Return) key after each parent. For example, if you wanted to associate the Term "puppies" with both "puppy" and "dog", click on "puppies", and in the Parents text box type "puppy", hit Enter, type "dog", and hit Enter. Sometimes this is necessary: for example, in Spanish, "se sienta" can either be a conjugation of "sentirse" (to feel) or "sentarse" (to sit), depending on the context.\n\n4. Mark the remainder as "Well Known"\nWhen you''re done creating Terms on a page, you will likely still have a bunch of blue words, or "unknowns", left over, even though you really know these words.','\n',char(10)),NULL,242);
INSERT INTO texts VALUES(8,4,4,replace('You can set all of these to "Well Known" and move to the next page in one shot with the green checkmark at the bottom of the page. Try that now to see what happens, and then come back to this page using the arrows in the header to finish reading this page.\nThe ">" link moves to the next page as well, without setting the unknown terms to "Well Known." This can be useful if you''re reading quickly, without stopping to define every last term in detail.\nNote: both of these links also mark the page as "Read", which Lute uses when it searches for references to terms you create. There''s more on this in the tutorial follow-up, which you should read after this tutorial.\n\n5. Keyboard shortcuts\nThe "hamburger menu" next to the Lute logo at the top right of the reading screen opens up a small menu of items, including a link to some keyboard shortcuts. This section introduces a few of them.\n\n5.1 Updating Status\nIf you''ve worked through the tutorial, you''ll have noted that words are underlined in blue when you move the mouse over them. You can quickly change the status of the current word by hitting 1, 2, 3, 4, 5, w (for Well-Known), or i (for Ignore). Try hovering over the following words and hit the status buttons: apple, banana, cranberry, donut.\nIf you click on a word, it''s underlined in red, and the Term edit form is shown.','\n',char(10)),NULL,246);
INSERT INTO texts VALUES(9,4,5,replace('Before you switch over to the Term editing form, you can still update its status using the hotkeys above, or by using the up and down arrows. You can jump over to the edit form by hitting Tab, and then start editing.\nWhen a word has been clicked, it''s "active", so it keeps the focus. Hovering the mouse over other words won''t underline them in blue anymore, and hitting status update hotkeys (1 - 5, w, i) will only update the active word. To "un-click" a word underlined in red, click it again, or hit Escape or Return. Then you''ll be back in "Hover mode". In "Hover mode", the hotkeys 1-5, w, and i still update the status, but the arrow keys just scroll the window. Try clicking and un-clicking or Escaping any word in this paragraph to get a feel for it.\nNote that for the keyboard shortcuts to work, the reading pane (where the text is) must have the "focus". Click anywhere on the reading pane to re-establish focus.\n\n5.1 Bulk updates\nIf you hold down Shift and click a bunch of words, you can bulk update their statuses. This works for the up and down arrow keys as well.\n\n5.2 Arrow keys\nThe Right and Left arrow keys click the next and previous words. Hit Escape or Return to get back to "hover mode".\n\n5.3 Copying text\nWhen a word is hovered over or clicked, hit "c" to copy that word''s sentence to your clipboard.','\n',char(10)),NULL,248);
INSERT INTO texts VALUES(10,4,6,replace('Hit "C" to copy the word''s full paragraph (multiple sentences). You can also copy arbitrary sections of text by holding down the Shift key while highlighting the text with your mouse.\n\n6. Next steps\nAll done this text!\nLute keeps track of all of this in your database, so any time you create or import a new Book, all the info you''ve created is carried forward.\nThere''s a tutorial follow-up: go to the Home screen, and click the "Tutorial follow-up" in the table.','\n',char(10)),NULL,87);
INSERT INTO texts VALUES(11,5,1,replace('Hopefully you''ve gone through the Tutorial, and created some Terms.\nFrom the Tutorial, you''ve already told Lute that you know most of the words on this page. You can hover over words to see information about them, such as your information you might have added about dogs.\nThere are still a few blue words, which according to Lute are still "unknown" to you. You can process them like you did on the last text.\n(fyi - If a text has a spelling mikstaske, you can edit it by clicking the "hamburger menu" -- three lines -- in the top left corner of this screen, and click "Edit page". If you''d like, correct the mistake now, and resave this text.)\nNow we''ll do a brief spin through a few other things Lute does. You can read about them and other features in the manual too.\n\n1. The Menus\nIn case you missed it, on the Home screen there are some menu bar items on the top right. Go back there and hover over them to see what you can do. This is all demo data, so you can do what you want. (But don''t delete the tutorials until you''ve gone through them.)\n\n2. Term Sentences\nIn the "Term" edit form, you can click on the "Sentences" tab to see where that term or its relations have been used. Click on "elephant", and then click the Sentences tab to see where that term has been used.','\n',char(10)),NULL,245);
INSERT INTO texts VALUES(12,5,2,replace('You''re only shown sentences on pages that have been marked "Read", using the controls in the footer of the reading screen, i.e. the green checkmark or the ">". This ensures that you only see references that you have already seen before, so you don''t get overwhelmed with new vocabulary, and avoids spoilers of the material you''re reading.\n\n3. Archiving, Unarchiving, and Deleting Books\nWhen you''re done reading a book, you can Archive or Delete it.\nArchiving just removes the book from your book listing on the home screen, and you can unarchive at any time. The sentences for archived books are still available for searching with the Term "Sentences" link.\nOn the last page of every book, Lute shows a link for you to archive the book. You can also archive it from the Home screen by clicking on the "Archive" action (the image with the little down arrow) in the right-most column. To unarchive the text, go to Home, Book Archive, and click the "Unarchive" action (the little up arrow).\nDeleting a book completely removes it and its sentences.\nNeither archiving nor deleting touch any Terms you''ve created.\n\n4. Audio\nYou can add an audio file (mp3, wav, or ogg) to your books, so you can read along to an audio track. See the Lute manual for more notes on usage and tips.\n\n5. Themes and toggling highlighting\nLute has a few themes to make reading more pleasant.','\n',char(10)),NULL,242);
INSERT INTO texts VALUES(13,5,3,replace('From the "hamburger menu" on the reading screen you can switch to the next theme, or hit the hotkey (m). You can also toggle highlights, because sometimes they get distracting.\n\n===\n\nThose are the the core feature of Lute! There are some sample stories for other languages. Try those out or create your own.\nWhen you''re done with the demo, go back to the Home screen and click the link to clear out the database. Lute will delete all of the demo data, and you can get started. You''ll be prompted to create your first language, and then you can create your first book. Lute will then ask you to specify your backup preferences, and with that all done, you''ll be off and running.\nThere is a Lute Discord and manual as well -- see the "About" menu bar.\nI hope that you find Lute a fun tool to use for learning languages. Cheers and best wishes!','\n',char(10)),NULL,158);
INSERT INTO texts VALUES(14,6,1,replace('Il était une fois trois ours: un papa ours, une maman ours et un bébé ours. Ils habitaient tous ensemble dans une maison jaune au milieu d''une grande forêt.\n\nUn jour, Maman Ours prépara une grande marmite de porridge délicieux et fumant pour le petit déjeuner. Il était trop chaud pour pouvoir être mangé, alors les ours décidèrent d''aller se promener en attendant que le porridge refroidisse.','\n',char(10)),NULL,69);
INSERT INTO texts VALUES(15,7,1,replace('Es hatte ein Mann einen Esel, der schon lange Jahre die Säcke unverdrossen zur Mühle getragen hatte, dessen Kräfte aber nun zu Ende gingen, sodass er zur Arbeit immer untauglicher wurde. Da dachte der Herr daran, ihn aus dem Futter zu schaffen, aber der Esel merkte, dass kein guter Wind wehte, lief fort und machte sich auf den Weg nach Bremen; dort, meinte er, könnte er ja Stadtmusikant werden.\n\nAls er ein Weilchen fortgegangen war, fand er einen Jagdhund auf dem Weg liegen, der japste wie einer, der sich müde gelaufen hat. "Nun, was japst du so, Packan?" fragte der Esel. "Ach," sagte der Hund, "weil ich alt bin und jeden Tag schwächer werde, auch auf der Jagd nicht mehr fort kann, hat mich mein Herr wollen totschlagen, da hab ich Reißaus genommen; aber womit soll ich nun mein Brot verdienen?" - "Weißt du was?" sprach der Esel, "ich gehe nach Bremen und werde dort Stadtmusikant, geh mit und lass dich auch bei der Musik annehmen. Ich spiele die Laute, und du schlägst die Pauken.','\n',char(10)),NULL,174);
INSERT INTO texts VALUES(16,8,1,replace('Πέτρος: Γεια σου, Νίκη. Ο Πέτρος είμαι.\nΝίκη: Α, γεια σου Πέτρο. Τι κάνεις;\nΠέτρος: Μια χαρά. Σε παίρνω για να πάμε καμιά βόλτα αργότερα. Τι λες;\nΝίκη: Α, ωραία. Κι εγώ θέλω να βγω λίγο. Συνέχεια διαβάζω για τις εξετάσεις… κουράστηκα πια. Πού λες να πάμε;\nΠέτρος: Στη γνωστή καφετέρια στην πλατεία. Θα είναι και άλλα παιδιά από την τάξη μας εκεί.\nΝίκη: Ναι; Ποιοι θα είναι;\nΠέτρος: Ο Γιάννης, ο Αντρέας και η Ελπίδα.\nΝίκη: Ωραία. Θα πάτε και πουθενά αλλού μετά;\nΠέτρος: Ναι, λέμε να πάμε στον κινηματογράφο που είναι κοντά στην καφετέρια. Παίζει μια κωμωδία.\nΝίκη: Α, δεν μπορώ να καθίσω έξω μέχρι τόσο αργά. Πρέπει να γυρίσω σπίτι για να διαβάσω.\nΠέτρος: Έλα τώρα. Διαβάζεις αύριο…\nΝίκη: Όχι, όχι, αδύνατον. Είμαι πολύ πίσω στο διάβασμά μου.\nΠέτρος: Καλά, έλα μόνο στην καφετέρια τότε. Θα περάσω να σε πάρω γύρω στις έξι να πάμε μαζί. Εντάξει;\nΝίκη: Εντάξει. Γεια.\nΠέτρο: Τα λέμε. Γεια.','\n',char(10)),NULL,157);
INSERT INTO texts VALUES(17,9,1,'अनुच्छेद १(एक): सभी मनुष्य जन्म से स्वतन्त्र तथा मर्यादा और अधिकारों में समान होते हैं। वे तर्क और विवेक से सम्पन्न हैं तथा उन्हें भ्रातृत्व की भावना से परस्पर के प्रति कार्य करना चाहिए।',NULL,35);
INSERT INTO texts VALUES(18,10,1,replace('北風と太陽\n\n「おれの方が強い。」「いいや、ぼくの方が強い。」\n北風と太陽の声が聞こえます。二人はどちらの力が強いかでケンカをしているようです。\n「太陽が毎日元気だから、暑くてみんな困っているよ。おれが涼しい風を吹くと、みんな嬉しそうだ。」','\n',char(10)),NULL,64);
INSERT INTO texts VALUES(19,11,1,'Встреча с медведем может быть очень опасна. Русские люди любят ходить в лес и собирать грибы и ягоды. Они делают это с осторожностью, так как медведи тоже очень любят ягоды и могут напасть на человека. Медведь ест все: ягоды, рыбу, мясо и даже насекомых. Особенно он любит мед.',NULL,48);
INSERT INTO texts VALUES(20,12,1,replace('काशीनगरे एकः पण्डितः अस्ति । पण्डितसमीपम् एकः शिष्यः आगच्छति । शिष्यः वदति - "आचार्य!\nविद्याभ्यासार्थम् आगतः ।" पण्डितः शिष्यबुद्धिपरीक्षार्थं पृच्छति - "वत्स, देवः कुत्र अस्ति?" शिष्यः वदति -\n''गुरो! देवः कुत्र नास्ति? कृपया भवान् एव समाधानं वदतु ।" सन्तुष्टः गुरुः वदति - "दैवः सर्वत्र अस्ति । देवः\nसर्वव्यापी । त्वं बुद्धिमान ।अतः विद्याभ्यासार्थम् अत्रैव वस।"','\n',char(10)),NULL,45);
INSERT INTO texts VALUES(21,13,1,replace('Érase una vez un muchacho llamado Aladino que vivía en el lejano Oriente con su madre, en una casa sencilla y humilde. Tenían lo justo para vivir, así que cada día, Aladino recorría el centro de la ciudad en busca de algún alimento que llevarse a la boca.\n\nEn una ocasión paseaba entre los puestos de fruta del mercado, cuando se cruzó con un hombre muy extraño con pinta de extranjero. Aladino se quedó sorprendido al escuchar que le llamaba por su nombre.','\n',char(10)),NULL,83);
INSERT INTO texts VALUES(22,14,1,replace('Büyük ağaç eskiden aşılanmış ve her yıl güzel, iri, pembe şeftaliler verirmiş, insanın eline sığmazmış bu şeftaliler. Öyle güzelmişler ki insan yemeye kıyamazmış onları. Bahçıvan, bu büyük ağacı yabancı bir uzmanın kendi ülkesinden getirdiği bir tohumla aşıladığını söylermiş. Belli ki böyle masraf edilen bir ağaçta yetişen şeftaliler oldukça değerliymiş.\n\nİki ağacın da gövdelerine nazar değmesin diye birer nazarlık asılıymış.\n\nAğaçlardan küçük olanında her yıl bin tane çiçek açarmış ama bir tek şeftali bile yetişmezmiş üzerinde. Ya çiçekleri dökülürmüş, ya da ham şeftaliler kuruyup dallardan düşermiş. Bahçıvan küçük ağaç için elinden geleni yapmış ama değişen bir şey olmamış. Yıllar geçtikçe dalları ve yaprakları çoğalmış ama bir tek şeftali bile görünmemiş üzerinde.','\n',char(10)),NULL,110);
CREATE TABLE IF NOT EXISTS "settings" (
	"StKey" VARCHAR(40) NOT NULL,
        "StKeyType" TEXT NOT NULL,
	"StValue" TEXT NULL,
	PRIMARY KEY ("StKey")
);
INSERT INTO settings VALUES('IsDemoData','system','1');
CREATE TABLE IF NOT EXISTS "books" (
	"BkID" INTEGER NOT NULL  ,
	"BkLgID" INTEGER NOT NULL  ,
	"BkTitle" VARCHAR(200) NOT NULL  ,
	"BkSourceURI" VARCHAR(1000) NULL  ,
	"BkArchived" TINYINT NOT NULL DEFAULT '0' ,
	"BkCurrentTxID" INTEGER NOT NULL DEFAULT '0',
        BkAudioFilename TEXT NULL,
        BkAudioCurrentPos REAL NULL,
        BkAudioBookmarks TEXT NULL,
	PRIMARY KEY ("BkID"),
	FOREIGN KEY("BkLgID") REFERENCES "languages" ("LgID") ON UPDATE NO ACTION ON DELETE CASCADE
);
INSERT INTO books VALUES(1,1,'Examples',NULL,0,0,NULL,NULL,NULL);
INSERT INTO books VALUES(2,2,'逍遙遊',NULL,0,0,NULL,NULL,NULL);
INSERT INTO books VALUES(3,3,'Hrad Cimburk – Jak vzal vítr pasáčkovi čepici',NULL,0,0,NULL,NULL,NULL);
INSERT INTO books VALUES(4,4,'Tutorial',NULL,0,0,NULL,NULL,NULL);
INSERT INTO books VALUES(5,4,'Tutorial follow-up',NULL,0,0,NULL,NULL,NULL);
INSERT INTO books VALUES(6,5,'Boucles d’or et les trois ours',NULL,0,0,NULL,NULL,NULL);
INSERT INTO books VALUES(7,6,'Die Bremer Stadtmusikanten',NULL,0,0,NULL,NULL,NULL);
INSERT INTO books VALUES(8,7,'Γεια σου, Νίκη. Ο Πέτρος είμαι.',NULL,0,0,NULL,NULL,NULL);
INSERT INTO books VALUES(9,8,'Universal Declaration of Human Rights',NULL,0,0,NULL,NULL,NULL);
INSERT INTO books VALUES(10,9,'北風と太陽 - きたかぜたいよう',NULL,0,0,NULL,NULL,NULL);
INSERT INTO books VALUES(11,10,'медведь',NULL,0,0,NULL,NULL,NULL);
INSERT INTO books VALUES(12,11,'बुद्धिमान् शिष्यः',NULL,0,0,NULL,NULL,NULL);
INSERT INTO books VALUES(13,12,'Aladino y la lámpara maravillosa',NULL,0,0,NULL,NULL,NULL);
INSERT INTO books VALUES(14,13,'Büyük ağaç',NULL,0,0,NULL,NULL,NULL);
CREATE TABLE IF NOT EXISTS "bookstats" (
	"BkID" INTEGER NOT NULL  ,
	"distinctterms" INTEGER NULL  ,
	"distinctunknowns" INTEGER NULL  ,
	"unknownpercent" INTEGER NULL  ,
        status_distribution VARCHAR(100) NULL,
	PRIMARY KEY ("BkID"),
	FOREIGN KEY("BkID") REFERENCES "books" ("BkID") ON UPDATE NO ACTION ON DELETE CASCADE
);
INSERT INTO bookstats VALUES(1,100,100,100,'{"0": 100, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "98": 0, "99": 0}');
INSERT INTO bookstats VALUES(2,170,170,100,'{"0": 170, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "98": 0, "99": 0}');
INSERT INTO bookstats VALUES(3,57,57,100,'{"0": 57, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "98": 0, "99": 0}');
INSERT INTO bookstats VALUES(4,361,361,100,'{"0": 361, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "98": 0, "99": 0}');
INSERT INTO bookstats VALUES(5,247,247,100,'{"0": 247, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "98": 0, "99": 0}');
INSERT INTO bookstats VALUES(6,49,49,100,'{"0": 49, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "98": 0, "99": 0}');
INSERT INTO bookstats VALUES(7,120,120,100,'{"0": 120, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "98": 0, "99": 0}');
INSERT INTO bookstats VALUES(8,99,99,100,'{"0": 99, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "98": 0, "99": 0}');
INSERT INTO bookstats VALUES(9,30,30,100,'{"0": 30, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "98": 0, "99": 0}');
INSERT INTO bookstats VALUES(10,41,41,100,'{"0": 41, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "98": 0, "99": 0}');
INSERT INTO bookstats VALUES(11,40,40,100,'{"0": 40, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "98": 0, "99": 0}');
INSERT INTO bookstats VALUES(12,33,33,100,'{"0": 33, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "98": 0, "99": 0}');
INSERT INTO bookstats VALUES(13,63,63,100,'{"0": 63, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "98": 0, "99": 0}');
INSERT INTO bookstats VALUES(14,85,85,100,'{"0": 85, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "98": 0, "99": 0}');
CREATE TABLE languagedicts (
  "LdID" INTEGER NOT NULL,
  "LdLgID" INTEGER NOT NULL,
  "LdUseFor" VARCHAR(20) NOT NULL,
  "LdType" VARCHAR(20) NOT NULL,
  "LdDictURI" VARCHAR(200) NOT NULL,
  "LdIsActive" TINYINT NOT NULL DEFAULT 1,
  "LdSortOrder" INTEGER NOT NULL,
  PRIMARY KEY ("LdID"),
  FOREIGN KEY("LdLgID") REFERENCES "languages" ("LgID") ON UPDATE NO ACTION ON DELETE CASCADE
);
INSERT INTO languagedicts VALUES(1,1,'terms','embeddedhtml','https://www.arabicstudentsdictionary.com/search?q=###',1,1);
INSERT INTO languagedicts VALUES(2,1,'terms','popuphtml','https://translate.google.com/?hl=en&sl=ar&tl=en&text=###&op=translate',1,2);
INSERT INTO languagedicts VALUES(3,1,'sentences','popuphtml','https://translate.google.com/?hl=en&sl=ar&tl=en&text=###',1,3);
INSERT INTO languagedicts VALUES(4,2,'terms','embeddedhtml','https://www.archchinese.com/chinese_english_dictionary.html?find=###',1,1);
INSERT INTO languagedicts VALUES(5,2,'sentences','popuphtml','https://www.deepl.com/translator#ch/en/###',1,2);
INSERT INTO languagedicts VALUES(6,3,'terms','embeddedhtml','https://slovniky.lingea.cz/Anglicko-cesky/###',1,1);
INSERT INTO languagedicts VALUES(7,3,'terms','popuphtml','https://slovnik.seznam.cz/preklad/cesky_anglicky/###',1,2);
INSERT INTO languagedicts VALUES(8,3,'sentences','popuphtml','https://www.deepl.com/translator#cs/en/###',1,3);
INSERT INTO languagedicts VALUES(9,4,'terms','embeddedhtml','https://en.thefreedictionary.com/###',1,1);
INSERT INTO languagedicts VALUES(10,4,'terms','popuphtml','https://www.collinsdictionary.com/dictionary/english/###',1,2);
INSERT INTO languagedicts VALUES(11,4,'sentences','popuphtml','https://www.deepl.com/translator#en/en/###',1,3);
INSERT INTO languagedicts VALUES(12,5,'terms','embeddedhtml','https://fr.thefreedictionary.com/###',1,1);
INSERT INTO languagedicts VALUES(13,5,'sentences','popuphtml','https://www.deepl.com/translator#fr/en/###',1,2);
INSERT INTO languagedicts VALUES(14,6,'terms','embeddedhtml','https://de.thefreedictionary.com/###',1,1);
INSERT INTO languagedicts VALUES(15,6,'terms','embeddedhtml','https://www.wordreference.com/deen/###',1,2);
INSERT INTO languagedicts VALUES(16,6,'sentences','popuphtml','https://www.deepl.com/translator#de/en/###',1,3);
INSERT INTO languagedicts VALUES(17,7,'terms','embeddedhtml','https://www.wordreference.com/gren/###',1,1);
INSERT INTO languagedicts VALUES(18,7,'terms','embeddedhtml','https://en.wiktionary.org/wiki/###',1,2);
INSERT INTO languagedicts VALUES(19,7,'sentences','popuphtml','https://www.deepl.com/translator#el/en/###',1,3);
INSERT INTO languagedicts VALUES(20,8,'terms','embeddedhtml','https://www.boltidictionary.com/en/search?s=###',1,1);
INSERT INTO languagedicts VALUES(21,8,'terms','popuphtml','https://translate.google.com/?sl=hi&tl=en&text=###',1,2);
INSERT INTO languagedicts VALUES(22,8,'sentences','embeddedhtml','https://www.bing.com/translator/?from=hi&to=en&text=###',1,3);
INSERT INTO languagedicts VALUES(23,9,'terms','embeddedhtml','https://jisho.org/search/###',1,1);
INSERT INTO languagedicts VALUES(24,9,'sentences','popuphtml','https://www.deepl.com/translator#jp/en/###',1,2);
INSERT INTO languagedicts VALUES(25,10,'terms','embeddedhtml','https://www.dict.com/Russian-English/###',1,1);
INSERT INTO languagedicts VALUES(26,10,'terms','embeddedhtml','https://en.openrussian.org/?search=###',1,2);
INSERT INTO languagedicts VALUES(27,10,'sentences','popuphtml','https://www.deepl.com/translator#ru/en/###',1,3);
INSERT INTO languagedicts VALUES(28,11,'terms','embeddedhtml','https://dsal.uchicago.edu/cgi-bin/app/sanskrit_query.py?qs=###&searchhws=yes&matchtype=default',1,1);
INSERT INTO languagedicts VALUES(29,11,'terms','embeddedhtml','https://www.learnsanskrit.cc/translate?search=###&dir=se',1,2);
INSERT INTO languagedicts VALUES(30,11,'sentences','popuphtml','https://translate.google.com/?hl=en&sl=sa&tl=en&text=###&op=translate',1,3);
INSERT INTO languagedicts VALUES(31,12,'terms','embeddedhtml','https://es.thefreedictionary.com/###',1,1);
INSERT INTO languagedicts VALUES(32,12,'terms','popuphtml','https://www.wordreference.com/es/en/translation.asp?spen=###',1,2);
INSERT INTO languagedicts VALUES(33,12,'sentences','popuphtml','https://www.deepl.com/translator#es/en/###',1,3);
INSERT INTO languagedicts VALUES(34,13,'terms','embeddedhtml','https://www.wordreference.com/tren/###',1,1);
INSERT INTO languagedicts VALUES(35,13,'terms','embeddedhtml','https://tr.wiktionary.org/wiki/###',1,2);
INSERT INTO languagedicts VALUES(36,13,'sentences','popuphtml','https://www.deepl.com/translator#tr/en/###',1,3);
CREATE TABLE IF NOT EXISTS "languages" (
	"LgID" INTEGER NOT NULL  ,
	"LgName" VARCHAR(40) NOT NULL  ,
	"LgCharacterSubstitutions" VARCHAR(500) NOT NULL  ,
	"LgRegexpSplitSentences" VARCHAR(500) NOT NULL  ,
	"LgExceptionsSplitSentences" VARCHAR(500) NOT NULL  ,
	"LgRegexpWordCharacters" VARCHAR(500) NOT NULL  ,
	"LgRightToLeft" TINYINT NOT NULL  ,
	"LgShowRomanization" TINYINT NOT NULL DEFAULT '0' ,
	"LgParserType" VARCHAR(20) NOT NULL DEFAULT 'spacedel' ,
	PRIMARY KEY ("LgID")
);
INSERT INTO languages VALUES(1,'Arabic','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?؟۔‎','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','\u0600-\u06FF\uFE70-\uFEFC',1,1,'spacedel');
INSERT INTO languages VALUES(2,'Classical Chinese','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?。！？','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','一-龥',0,1,'classicalchinese');
INSERT INTO languages VALUES(3,'Czech','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','a-zA-ZÀ-ÖØ-öø-ȳáéíóúÁÉÍÓÚñÑ',0,1,'spacedel');
INSERT INTO languages VALUES(4,'English','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','a-zA-ZÀ-ÖØ-öø-ȳáéíóúÁÉÍÓÚñÑ',0,0,'spacedel');
INSERT INTO languages VALUES(5,'French','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','a-zA-ZÀ-ÖØ-öø-ȳáéíóúÁÉÍÓÚñÑ',0,0,'spacedel');
INSERT INTO languages VALUES(6,'German','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','a-zA-ZÀ-ÖØ-öø-ȳáéíóúÁÉÍÓÚñÑ\u200C\u200D',0,0,'spacedel');
INSERT INTO languages VALUES(7,'Greek','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?;','Mr.|Mrs.|Dr.|[A-Z].|κτλ.|κλπ.|π.χ.|λ.χ.|κ.ά|δηλ.|Κος.|Κ.|Κα.|μ.Χ.|ΥΓ.|μ.μ.|π.μ.|σελ.|κεφ.|βλ.|αι.','α-ωΑ-ΩάόήέώύίΊΏΈΉΌΆΎϊΪϋΫΐΰ',0,1,'spacedel');
INSERT INTO languages VALUES(8,'Hindi','´=''|`=''|’=''|‘=''|...=…|..=‥','.?!|।॥','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','a-zA-Z\u0900-\u0963\u0966-\u097F\u200C\u200D',0,1,'spacedel');
INSERT INTO languages VALUES(9,'Japanese','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?。？！','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','\p{Han}\p{Katakana}\p{Hiragana}',0,1,'japanese');
INSERT INTO languages VALUES(10,'Russian','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','А-Яа-яЁё',0,0,'spacedel');
INSERT INTO languages VALUES(11,'Sanskrit','´=''|`=''|’=''|‘=''|...=…|..=‥','.?!।॥','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','a-zA-Z\u0900-\u0963\u0966-\u097F',0,1,'spacedel');
INSERT INTO languages VALUES(12,'Spanish','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','a-zA-ZÀ-ÖØ-öø-ȳáéíóúÁÉÍÓÚñÑ',0,0,'spacedel');
INSERT INTO languages VALUES(13,'Turkish','´=''|`=''|’=''|‘=''|...=…|..=‥','.!?','Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.','a-zA-ZÀ-ÖØ-öø-ȳáéíóúÁÉÍÓÚñÑğĞıİöÖüÜşŞçÇ',0,1,'turkish');
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
CREATE UNIQUE INDEX "wordparent_pair" ON "wordparents" ("WpWoID", "WpParentWoID");
CREATE INDEX "BkLgID" ON "books" ("BkLgID");
CREATE UNIQUE INDEX "LgName" ON "languages" ("LgName");
CREATE TRIGGER trig_wordparents_after_insert_update_parent_WoStatus_if_following
-- created by db/schema/migrations_repeatable/trig_wordparents.sql
AFTER INSERT ON wordparents
BEGIN
    UPDATE words
    SET WoStatus = (
      select WoStatus from words where WoID = new.WpWoID
    )
    WHERE WoID = new.WpParentWoID
    AND 1 = (
      SELECT COUNT(*)
      FROM wordparents
      INNER JOIN words ON WoID = WpWoID
      WHERE WoSyncStatus = 1
      AND WoID = new.WpWoID
    );
END
;
CREATE TRIGGER trig_wordparents_after_delete_change_WoSyncStatus
-- created by db/schema/migrations_repeatable/trig_wordparents.sql
BEFORE DELETE ON wordparents
FOR EACH ROW
BEGIN
    UPDATE words
    SET WoSyncStatus = 0
    WHERE WoID IN
    (
      select WpWoID from wordparents
      where WpParentWoID = old.WpParentWoID
    );
END
;
CREATE TRIGGER trig_words_after_update_WoStatus_if_following_parent
-- created by db/schema/migrations_repeatable/trig_words.sql
AFTER UPDATE OF WoStatus, WoSyncStatus ON words
FOR EACH ROW
WHEN (old.WoStatus <> new.WoStatus or (old.WoSyncStatus = 0 and new.WoSyncStatus = 1))
BEGIN
    UPDATE words
    SET WoStatus = new.WoStatus
    WHERE WoID in (
      -- single parent children that are following this term.
      select WpWoID
      from wordparents
      inner join words on WoID = WpWoID
      where WoSyncStatus = 1
      and WpParentWoID = old.WoID
      group by WpWoID
      having count(*) = 1

      UNION

      -- The parent of this term,
      -- if this term has a single parent and has "follow parent"
      select WpParentWoID
      from wordparents
      inner join words on WoID = WpWoID
      where WoSyncStatus = 1
      and WoID = old.WoID
      group by WpWoID
      having count(*) = 1
    );
END
;
CREATE TRIGGER trig_words_update_WoStatusChanged
-- created by db/schema/migrations_repeatable/trig_words.sql
AFTER UPDATE OF WoStatus ON words
FOR EACH ROW
WHEN old.WoStatus <> new.WoStatus
BEGIN
    UPDATE words
    SET WoStatusChanged = CURRENT_TIMESTAMP
    WHERE WoID = NEW.WoID;
END
;
CREATE TRIGGER trig_words_update_WoCreated_if_no_longer_unknown
-- created by db/schema/migrations_repeatable/trig_words.sql
AFTER UPDATE OF WoStatus ON words
FOR EACH ROW
WHEN old.WoStatus <> new.WoStatus and old.WoStatus = 0
BEGIN
    UPDATE words
    SET WoCreated = CURRENT_TIMESTAMP
    WHERE WoID = NEW.WoID;
END
;
COMMIT;
