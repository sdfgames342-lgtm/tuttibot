PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE jugadores (
    user_id INTEGER PRIMARY KEY,
    nombre TEXT,
    puntos_historicos INTEGER DEFAULT 0
, premium_status INTEGER DEFAULT 0, exp_date TEXT, sudo_level INTEGER DEFAULT 0, afinidad INTEGER DEFAULT 0);
INSERT INTO jugadores VALUES(1,'Juan',0,0,NULL,0,0);
INSERT INTO jugadores VALUES(2,'María',0,0,NULL,0,0);
INSERT INTO jugadores VALUES(3,'Pedro',0,0,NULL,0,0);
INSERT INTO jugadores VALUES(999,'Test',10,0,NULL,4,0);
INSERT INTO jugadores VALUES(200000,'J2000_0',0,0,NULL,0,0);
INSERT INTO jugadores VALUES(200001,'J2000_1',0,0,NULL,0,0);
INSERT INTO jugadores VALUES(200002,'J2000_2',539.94,0,NULL,0,0);
INSERT INTO jugadores VALUES(200003,'J2000_3',0,0,NULL,0,0);
INSERT INTO jugadores VALUES(200100,'J2001_0',0,0,NULL,0,0);
INSERT INTO jugadores VALUES(200101,'J2001_1',0,0,NULL,0,0);
INSERT INTO jugadores VALUES(200102,'J2001_2',540,0,NULL,0,0);
INSERT INTO jugadores VALUES(200103,'J2001_3',0,0,NULL,0,0);
INSERT INTO jugadores VALUES(200200,'J2002_0',0,0,NULL,0,0);
INSERT INTO jugadores VALUES(200201,'J2002_1',0,0,NULL,0,0);
INSERT INTO jugadores VALUES(200202,'J2002_2',540,0,NULL,0,0);
INSERT INTO jugadores VALUES(200203,'J2002_3',0,0,NULL,0,0);
INSERT INTO jugadores VALUES(200300,'J2003_0',0,0,NULL,0,0);
INSERT INTO jugadores VALUES(200301,'J2003_1',0,0,NULL,0,0);
INSERT INTO jugadores VALUES(200302,'J2003_2',540,0,NULL,0,0);
INSERT INTO jugadores VALUES(200303,'J2003_3',0,0,NULL,0,0);
INSERT INTO jugadores VALUES(200400,'J2004_0',0,0,NULL,0,0);
INSERT INTO jugadores VALUES(200401,'J2004_1',0,0,NULL,0,0);
INSERT INTO jugadores VALUES(200402,'J2004_2',540,0,NULL,0,0);
INSERT INTO jugadores VALUES(200403,'J2004_3',0,0,NULL,0,0);
INSERT INTO jugadores VALUES(444444,'Ana',0,0,NULL,0,0);
INSERT INTO jugadores VALUES(500000,'J5000_0',0,0,NULL,0,0);
INSERT INTO jugadores VALUES(500001,'J5000_1',0,0,NULL,0,0);
INSERT INTO jugadores VALUES(500002,'J5000_2',540,0,NULL,0,0);
INSERT INTO jugadores VALUES(500003,'J5000_3',0,0,NULL,0,0);
INSERT INTO jugadores VALUES(555555,'Luis',0,0,NULL,0,0);
INSERT INTO jugadores VALUES(666666,'Sara',0,0,NULL,0,0);
INSERT INTO jugadores VALUES(1915994931,'Luz🌷',0,0,NULL,0,2);
INSERT INTO jugadores VALUES(6318151422,'Не лаг а',0,0,NULL,0,2);
INSERT INTO jugadores VALUES(6696367651,'𝕰𝖑𝖎𝖟𝖆𝖇𝖊𝖙𝖍',0,0,NULL,0,0);
INSERT INTO jugadores VALUES(6950880640,'🥀ᥫ꯭꯭͓᭡꯭͓፝ ꯭⎯꯭̽𓆩꯭〭〬𓏲⃝⃝꯭🔥္ꪶꫀ𝘴ꪶꪗ˶‌⛧‌ٖٖٖ⃝🌸⃝۪۪۪۪࣭࣭ٜٜ⃡▒⃟꯭.ீ͜⛧‌',590,0,NULL,0,33);
INSERT INTO jugadores VALUES(7079185716,'⛧𝓨𝓪𝓶𝓲𝓵𝓲𝓽𝓪🦋',80,0,NULL,0,7);
INSERT INTO jugadores VALUES(7695397217,'✎√-1 ┊Polar',133,0,NULL,0,18);
INSERT INTO jugadores VALUES(8235511001,'Claarii✨',0,0,NULL,0,0);
INSERT INTO jugadores VALUES(8301313897,'⩘⩗​⚜╚»«[𝘕𝘦𝘰 - 𝘒𝘢𝘯𝘫𝘪]»«╝',1240,0,NULL,4,37);
INSERT INTO jugadores VALUES(8755665248,'•ㅤㅤ 𝐉𝐞𝐟𝐞𝐫𝐬𝐨𝐧',0,0,NULL,0,0);
CREATE TABLE respuestas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sala_id TEXT,
    ronda INTEGER,
    categoria TEXT,
    user_id INTEGER,
    texto TEXT,
    votos INTEGER DEFAULT 0
);
CREATE TABLE partidas (
    chat_id TEXT PRIMARY KEY,
    estado TEXT NOT NULL DEFAULT 'ESPERA',
    ronda INTEGER NOT NULL DEFAULT 1,
    categorias TEXT,
    letra TEXT DEFAULT '',
    inicio_epoch REAL,
    bloques_procesados INTEGER DEFAULT 0,
    jugadores TEXT,
    creador INTEGER,
    start_message_id INTEGER
);
CREATE TABLE log_eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    chat_id TEXT,
    user_id INTEGER,
    tipo_evento INTEGER,
    latencia_ms INTEGER,
    valor_extra REAL
);
CREATE TABLE frases_sizaña (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trigger_tipo TEXT,
            perfil_objetivo TEXT,
            texto TEXT,
            peso_irritacion INTEGER DEFAULT 3
        );
INSERT INTO "frases_sizaña" VALUES(15,'EMPATE','SOFISTA','El empate solo confirma que la mediocridad es el estándar de este grupo.',3);
INSERT INTO "frases_sizaña" VALUES(16,'EMPATE','SOFISTA','Ni siquiera tu imaginación elástica pudo romper la barrera del consenso. Triste, pero esperable.',3);
INSERT INTO "frases_sizaña" VALUES(17,'EMPATE','ALPHA','Hasta los titanes resbalan con piedras pequeñas. No dejes que un empate te recuerde que eres mortal.',3);
INSERT INTO "frases_sizaña" VALUES(18,'EMPATE','ALPHA','Tu corona sigue en la cabeza, pero hoy el vulgo te ha rozado. Inquietante, ¿no?',3);
INSERT INTO "frases_sizaña" VALUES(19,'EMPATE','ALPHA','Miren a {user}, compartiendo el trono como si no le importara. Qué democrático te has vuelto.',3);
INSERT INTO "frases_sizaña" VALUES(20,'MENTIRA_DETECTADA','SOFISTA','Análisis concluido: el intelecto de este espécimen ha tocado fondo. Procedan con la siguiente ronda antes de que la estupidez sea contagiosa.',4);
INSERT INTO "frases_sizaña" VALUES(21,'MENTIRA_DETECTADA','SOFISTA','Tu confianza es inversamente proporcional a tu precisión. Un caso de estudio para la psicología moderna.',4);
INSERT INTO "frases_sizaña" VALUES(22,'MENTIRA_DETECTADA','SOFISTA','{user}, hablas mucho para decir tan poco. Eres básicamente ruido blanco con pretensiones de intelecto.',4);
INSERT INTO "frases_sizaña" VALUES(23,'LENTITUD','ESCETICO','30 segundos de procesamiento para escribir eso. Me pregunto qué otras tareas básicas te resultan abrumadoras.',3);
INSERT INTO "frases_sizaña" VALUES(24,'LENTITUD','ESCETICO','La paciencia es una virtud, pero contigo se está convirtiendo en martirio.',3);
INSERT INTO "frases_sizaña" VALUES(25,'LENTITUD','LURKER','Observo tu silencio, {user}. Es la decisión más inteligente que has tomado hoy; al menos así no confirmas las sospechas sobre tu intelecto.',3);
INSERT INTO "frases_sizaña" VALUES(26,'LENTITUD','LURKER','¿Estás aquí como adorno o simplemente esperas que el conocimiento se te pegue por ósmosis? Muévete o conviértete en abono.',3);
INSERT INTO "frases_sizaña" VALUES(27,'CONFLICTO','SOFISTA','Ganaste, pero todos sabemos que fue por lástima del grupo, no por tu cerebro.',4);
INSERT INTO "frases_sizaña" VALUES(28,'CONFLICTO','ALPHA','El grupo te dio la victoria por inercia. Hasta un reloj roto acierta dos veces al día.',4);
INSERT INTO "frases_sizaña" VALUES(29,'CONFLICTO','ALPHA','Felicidades, {user}. Has logrado destacar en un grupo cuya capacidad cognitiva roza el cero absoluto. ¿Te sientes orgulloso de ser el rey de los mediocres?',4);
INSERT INTO "frases_sizaña" VALUES(30,'PALIZA','ALPHA','Qué exhibición tan aburrida de superioridad. Ni siquiera has dejado que los demás se diviertan.',3);
INSERT INTO "frases_sizaña" VALUES(31,'PALIZA','SOFISTA','Cuando ganas por tanto margen, la pregunta no es qué tan bueno eres, sino qué tan malos son los demás.',3);
INSERT INTO "frases_sizaña" VALUES(32,'PALIZA','ALPHA','Tu puntuación es alta, pero tu desesperación por atención es todavía mayor. Es fascinante cómo un poco de éxito digital te hace creer que tienes valor real.',4);
CREATE TABLE keys_activacion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_hash TEXT UNIQUE,
    usada INTEGER DEFAULT 0,
    generada_por INTEGER,
    fecha_generacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    expira DATETIME
);
INSERT INTO keys_activacion VALUES(1,'D316B6B063ADCC5D1BF0BCA086EDAD80',0,0,'2026-05-03 14:22:38','2026-05-04T11:22:38.099244');
INSERT INTO keys_activacion VALUES(2,'AF568F002719CF8549D62215014054FB',0,8301313897,'2026-05-04 00:23:25','2026-05-04T21:23:25.782520');
INSERT INTO keys_activacion VALUES(3,'8F8DE23710AEE06D1012319FFFC34D1F',0,8301313897,'2026-05-04 00:26:05','2026-05-04T21:26:05.301873');
INSERT INTO keys_activacion VALUES(4,'2FA0275CB325E5C2B1AF091356A82D4B',0,8301313897,'2026-05-04 02:29:57','2026-05-04T23:29:57.146596');
INSERT INTO keys_activacion VALUES(5,'9CF43B2E5A89E64CBFB720EACB825A59',0,8301313897,'2026-05-04 06:07:15','2026-05-05T03:07:15.482185');
INSERT INTO keys_activacion VALUES(6,'B8B9A0F8C710884380B3FF9D156C2DE0',0,8301313897,'2026-05-04 07:52:31','2026-05-05T04:52:31.329028');
INSERT INTO keys_activacion VALUES(7,'8F3EA47A7F4932E1ED1F89AE7D43F2BD',0,8301313897,'2026-05-04 09:31:40','2026-05-05T06:31:40.912719');
INSERT INTO keys_activacion VALUES(8,'5D1810C7FF1846117BBF00CF66D07088',0,8301313897,'2026-05-04 09:32:08','2026-05-05T06:32:08.233244');
INSERT INTO keys_activacion VALUES(9,'E9B9691B74E8EC924237AB583322C13C',0,8301313897,'2026-05-04 09:33:55','2026-05-05T06:33:55.103128');
INSERT INTO keys_activacion VALUES(10,'DDD559DC1E4BF967014C14F4CDBFF8D3',0,8301313897,'2026-05-04 13:11:21','2026-05-05T10:11:21.043494');
INSERT INTO keys_activacion VALUES(11,'838E4D71CF7AF16251AC91506E29C4A5',0,8301313897,'2026-05-04 22:11:24','2026-05-05T19:11:24.380978');
INSERT INTO keys_activacion VALUES(12,'E5748F5E175541665479985CE4C223D1',0,8301313897,'2026-05-04 22:12:56','2026-05-05T19:12:56.840706');
INSERT INTO keys_activacion VALUES(13,'B47ADDC7964B39C8E4C14BFB0648D938',0,8301313897,'2026-05-04 22:17:55','2026-05-05T19:17:55.981686');
INSERT INTO keys_activacion VALUES(14,'2E19D2DB55CCB5A562FE3296228F5F2E',0,8301313897,'2026-05-04 23:58:24','2026-05-05T20:58:24.940462');
INSERT INTO keys_activacion VALUES(15,'DFCD718FDBE44EACAE3DFCEC103DF1CE',1,8301313897,'2026-05-05 04:37:35','2026-05-06T01:37:35.744899');
INSERT INTO keys_activacion VALUES(16,'B1C27E5791D056D77252905FE0D61025',1,8301313897,'2026-05-05 04:39:19','2026-05-06T01:39:19.409332');
INSERT INTO keys_activacion VALUES(17,'6C946ADD8F8A43EB8A40B4D3DD38B496',1,8301313897,'2026-05-05 05:26:57','2026-05-06T02:26:57.152098');
INSERT INTO keys_activacion VALUES(18,'01498705DECCBEE17093A9DCCDCBAF9A',1,8301313897,'2026-05-05 05:51:15','2026-05-06T02:51:15.465064');
INSERT INTO keys_activacion VALUES(19,'D606B275492D8D37EA62B40ABA20BF92',1,8301313897,'2026-05-05 05:51:40','2026-05-06T02:51:40.898956');
INSERT INTO keys_activacion VALUES(20,'45976360C447CFC30EAA7B8DF541790A',0,8301313897,'2026-05-06 04:34:37','2026-05-07T01:34:37.113919');
INSERT INTO keys_activacion VALUES(21,'84390E430403132C66D7A30CACDED0F0',1,8301313897,'2026-05-06 04:51:21','2026-05-07T01:51:21.469957');
INSERT INTO keys_activacion VALUES(22,'CE15E975E835710103948020C41CD1CB',1,8301313897,'2026-05-06 05:00:06','2026-05-07T02:00:06.064870');
INSERT INTO keys_activacion VALUES(23,'E8D6DC1B960425E9E57BF41F0312AA24',0,8301313897,'2026-05-06 05:02:09','2026-05-07T02:02:09.025993');
INSERT INTO keys_activacion VALUES(24,'4071A9B7BB2ECC5310E6171E73C20EC1',0,8301313897,'2026-05-06 05:13:08','2026-05-07T02:13:08.954220');
INSERT INTO keys_activacion VALUES(25,'F5FE66AC6BA760C724CC59E18330C478',1,8301313897,'2026-05-06 05:18:39','2026-05-07T02:18:39.294539');
INSERT INTO keys_activacion VALUES(26,'A06BFFE581BB91B4D9452CCB55F380AA',1,8301313897,'2026-05-07 04:55:32','2026-05-08T01:55:32.959351');
CREATE TABLE config_bot (
    clave TEXT PRIMARY KEY,
    valor TEXT
);
INSERT INTO config_bot VALUES('test','1');
INSERT INTO config_bot VALUES('test_key','test_val');
INSERT INTO config_bot VALUES('canal_marketing','@Itsuki_garden');
INSERT INTO config_bot VALUES('canal_logs','-1003932342580');
INSERT INTO config_bot VALUES('img_start','AgACAgEAAxkBAAICzmn4WNMdbRJLPx8mK-LMsoLpvfUEAAKMDWsbJ3TBR0dNUULmeazJAQADAgADeAADOwQ');
INSERT INTO config_bot VALUES('img_about','AgACAgEAAxkBAAIC2Wn4ZYThHX_iuzWE_T51ry4EUaqrAAKSDWsbJ3TBR-XOS2XFaEbSAQADAgADeQADOwQ');
INSERT INTO config_bot VALUES('img_premium','AgACAgEAAxkBAAIC12n4ZYRtzay651IGCyHvGznln6K_AAKRDWsbJ3TBR5GEz0a2kF6HAQADAgADeQADOwQ');
INSERT INTO config_bot VALUES('lang_chat_-1003426922229','es');
INSERT INTO config_bot VALUES('lang_chat_-1002358380785','es');
INSERT INTO config_bot VALUES('lang_chat_-1003850468118','es');
INSERT INTO config_bot VALUES('lang_chat_-1002458905599','es');
INSERT INTO config_bot VALUES('lang_chat_-1003900442088','es');
INSERT INTO config_bot VALUES('img_help','AgACAgEAAyEFAATMQq71AAJttmn76qhIX35jesfUCaiJCgHIBNspAAIDDGsbruzhRzHtFbQh1BbrAQADAgADeQADOwQ');
INSERT INTO config_bot VALUES('book_blocked_-1003426922229','0');
INSERT INTO config_bot VALUES('exam_active_-1003426922229','1');
INSERT INTO config_bot VALUES('pin_message_id','92');
CREATE TABLE biblioteca_global (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT, pregunta TEXT, respuesta_key TEXT, idioma TEXT DEFAULT 'es', ultimo_grupo_id TEXT, estado TEXT DEFAULT 'LIBRE', asignado_epoch REAL);
CREATE TABLE ruleta_rusa_salas (chat_id TEXT PRIMARY KEY, activa INTEGER DEFAULT 0, pregunta TEXT, respuesta TEXT, inicio_epoch REAL);
CREATE TABLE duelo_traduccion_salas (chat_id TEXT PRIMARY KEY, activa INTEGER DEFAULT 0, frase TEXT, respuesta TEXT, inicio_epoch REAL);
INSERT INTO duelo_traduccion_salas VALUES('-1003426922229',0,'Estar en las nubes','to have one''s head in the clouds',1778136193.6738436);
CREATE TABLE contribuciones_grupo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    chat_id TEXT,
    puntos_aportados INTEGER DEFAULT 0,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES jugadores(user_id),
    FOREIGN KEY(chat_id) REFERENCES control_grupos(chat_id)
);
INSERT INTO contribuciones_grupo VALUES(1,7695397217,'-1003426922229',135,'2026-05-06 09:14:30');
CREATE TABLE repaso_lexico (
    user_id INTEGER,
    palabra_id INTEGER,
    nivel_dominio INTEGER DEFAULT 1,
    ultimo_repaso TIMESTAMP,
    proximo_repaso TIMESTAMP,
    PRIMARY KEY (user_id, palabra_id)
);
INSERT INTO repaso_lexico VALUES(8301313897,501,1,'2026-05-06 11:23:22.665659','2026-05-07 11:23:22.665686');
INSERT INTO repaso_lexico VALUES(8301313897,401,1,'2026-05-06 11:23:22.674669','2026-05-07 11:23:22.674680');
INSERT INTO repaso_lexico VALUES(8301313897,103,1,'2026-05-06 11:35:43.896075','2026-05-07 11:35:43.896087');
INSERT INTO repaso_lexico VALUES(8301313897,111,1,'2026-05-06 11:35:43.896453','2026-05-07 11:35:43.896472');
INSERT INTO repaso_lexico VALUES(8301313897,504,1,'2026-05-06 11:35:46.483875','2026-05-07 11:35:46.483888');
INSERT INTO repaso_lexico VALUES(8301313897,112,1,'2026-05-06 11:35:49.417356','2026-05-07 11:35:49.418001');
INSERT INTO repaso_lexico VALUES(8301313897,402,1,'2026-05-06 11:35:49.427165','2026-05-07 11:35:49.427181');
INSERT INTO repaso_lexico VALUES(8301313897,108,1,'2026-05-06 11:35:49.427387','2026-05-07 11:35:49.427401');
INSERT INTO repaso_lexico VALUES(8301313897,995,1,'2026-05-06 11:35:55.386612','2026-05-07 11:35:55.386621');
INSERT INTO repaso_lexico VALUES(8301313897,104,1,'2026-05-06 11:35:55.386751','2026-05-07 11:35:55.386760');
INSERT INTO repaso_lexico VALUES(8301313897,102,1,'2026-05-06 11:35:59.396563','2026-05-07 11:35:59.396589');
INSERT INTO repaso_lexico VALUES(8301313897,996,1,'2026-05-06 11:35:59.396933','2026-05-07 11:35:59.396942');
INSERT INTO repaso_lexico VALUES(8301313897,404,1,'2026-05-06 11:35:59.397071','2026-05-07 11:35:59.397079');
INSERT INTO repaso_lexico VALUES(8301313897,502,1,'2026-05-06 11:35:59.397203','2026-05-07 11:35:59.397212');
INSERT INTO repaso_lexico VALUES(8301313897,100,1,'2026-05-06 11:36:03.360797','2026-05-07 11:36:03.360824');
INSERT INTO repaso_lexico VALUES(8301313897,101,1,'2026-05-06 11:36:03.367164','2026-05-07 11:36:03.367192');
INSERT INTO repaso_lexico VALUES(8301313897,999,1,'2026-05-06 11:36:03.367981','2026-05-07 11:36:03.367992');
INSERT INTO repaso_lexico VALUES(8301313897,997,1,'2026-05-06 11:36:03.368160','2026-05-07 11:36:03.368171');
INSERT INTO repaso_lexico VALUES(8301313897,403,1,'2026-05-06 11:36:03.368570','2026-05-07 11:36:03.368594');
INSERT INTO repaso_lexico VALUES(8301313897,107,1,'2026-05-06 11:36:03.368804','2026-05-07 11:36:03.368819');
INSERT INTO repaso_lexico VALUES(8301313897,106,1,'2026-05-06 11:36:03.369026','2026-05-07 11:36:03.369043');
INSERT INTO repaso_lexico VALUES(8301313897,105,1,'2026-05-06 11:36:03.369393','2026-05-07 11:36:03.369415');
CREATE TABLE descargas_ytmusic (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES jugadores(user_id)
);
CREATE TABLE metricas_marketing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evento TEXT NOT NULL,
    user_id INTEGER,
    chat_id TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE stickers_cartas (
    nombre TEXT PRIMARY KEY,
    file_unique_id TEXT NOT NULL,
    emoji TEXT,
    set_name TEXT,
    metadata TEXT,
    creado_por INTEGER,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
, palo TEXT, rango TEXT, idioma TEXT DEFAULT 'frances', peso_truco INTEGER DEFAULT 0);
INSERT INTO stickers_cartas VALUES('as_diamantes','AgADTAEAArlrwVU','1⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:22:58','diamantes','as','frances',0);
INSERT INTO stickers_cartas VALUES('2_diamantes','AgADBgEAAmovyFU','2⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:23:56','diamantes','2','frances',0);
INSERT INTO stickers_cartas VALUES('3_diamantes','AgADlQEAAuvlwVU','3⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:24:08','diamantes','3','frances',0);
INSERT INTO stickers_cartas VALUES('4_diamantes','AgADwQEAAqDNwFU','4⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:24:19','diamantes','4','frances',0);
INSERT INTO stickers_cartas VALUES('5_diamantes','AgADmQEAApEgwVU','5⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:24:31','diamantes','5','frances',0);
INSERT INTO stickers_cartas VALUES('6_diamantes','AgADFwEAAvt_wVU','6⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:24:42','diamantes','6','frances',0);
INSERT INTO stickers_cartas VALUES('7_diamantes','AgADjQEAArJWwFU','7⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:24:54','diamantes','7','frances',0);
INSERT INTO stickers_cartas VALUES('8_diamantes','AgADXQEAAmtEwFU','8⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:25:05','diamantes','8','frances',0);
INSERT INTO stickers_cartas VALUES('9_diamantes','AgADNQEAAuQkwVU','9⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:25:22','diamantes','9','frances',0);
INSERT INTO stickers_cartas VALUES('10_diamantes','AgADUgEAAhlbwFU','🔟','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:25:34','diamantes','10','frances',0);
INSERT INTO stickers_cartas VALUES('sota_diamantes','AgADTQEAAnHCyVU','🤡','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:25:47','diamantes','sota','frances',0);
INSERT INTO stickers_cartas VALUES('caballo_diamantes','AgADuAEAArhlwFU','👸','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:25:58','diamantes','caballo','frances',0);
INSERT INTO stickers_cartas VALUES('rey_diamantes','AgADfgEAArn-wVU','🤴','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:26:12','diamantes','rey','frances',0);
INSERT INTO stickers_cartas VALUES('as_picas','AgADewEAAoCZwFU','1⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:27:24','picas','as','frances',0);
INSERT INTO stickers_cartas VALUES('2_picas','AgADdgEAAs-xwFU','2⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:27:39','picas','2','frances',0);
INSERT INTO stickers_cartas VALUES('3_picas','AgADiAEAAlr1wFU','3⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:27:50','picas','3','frances',0);
INSERT INTO stickers_cartas VALUES('4_picas','AgAD9QADkD_AVQ','4⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:28:02','picas','4','frances',0);
INSERT INTO stickers_cartas VALUES('5_picas','AgADtgEAAnl5wVU','5⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:28:10','picas','5','frances',0);
INSERT INTO stickers_cartas VALUES('6_picas','AgADwgEAAhMZyFU','6⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:28:25','picas','6','frances',0);
INSERT INTO stickers_cartas VALUES('7_picas','AgADXwEAAlcqwVU','7⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:28:35','picas','7','frances',0);
INSERT INTO stickers_cartas VALUES('8_picas','AgAD5gEAApGAwFU','8⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:28:45','picas','8','frances',0);
INSERT INTO stickers_cartas VALUES('9_picas','AgADTAEAAlTbwVU','9⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:29:00','picas','9','frances',0);
INSERT INTO stickers_cartas VALUES('10_picas','AgADfgEAAjEccVY','🔟','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:29:24','picas','10','frances',0);
INSERT INTO stickers_cartas VALUES('sota_picas','AgADgQEAAg1zwFU','🤡','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:29:36','picas','sota','frances',0);
INSERT INTO stickers_cartas VALUES('caballo_picas','AgADqQIAAomTwFU','👸','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:29:45','picas','caballo','frances',0);
INSERT INTO stickers_cartas VALUES('rey_picas','AgADpQEAAmtpwFU','🤴','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:29:55','picas','rey','frances',0);
INSERT INTO stickers_cartas VALUES('as_corazones','AgADigEAAvSIwFU','1⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:31:46','corazones','as','frances',0);
INSERT INTO stickers_cartas VALUES('2_corazones','AgADwAEAAri0wFU','2⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:32:08','corazones','2','frances',0);
INSERT INTO stickers_cartas VALUES('3_corazones','AgADkgEAAi3FwVU','3⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:32:23','corazones','3','frances',0);
INSERT INTO stickers_cartas VALUES('4_corazones','AgADnQEAAtIewFU','4⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:32:32','corazones','4','frances',0);
INSERT INTO stickers_cartas VALUES('5_corazones','AgAD9wADiiHBVQ','5⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:32:44','corazones','5','frances',0);
INSERT INTO stickers_cartas VALUES('6_corazones','AgADuQEAAi7fwVU','6⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:32:55','corazones','6','frances',0);
INSERT INTO stickers_cartas VALUES('7_corazones','AgADZAEAAtV9wVU','7⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:33:06','corazones','7','frances',0);
INSERT INTO stickers_cartas VALUES('8_corazones','AgADWAEAAk-6wVU','8⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:33:17','corazones','8','frances',0);
INSERT INTO stickers_cartas VALUES('9_corazones','AgADpAEAAoDywVU','9⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:33:27','corazones','9','frances',0);
INSERT INTO stickers_cartas VALUES('10_corazones','AgADEQEAAkFbwFU','🔟','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:33:37','corazones','10','frances',0);
INSERT INTO stickers_cartas VALUES('sota_corazones','AgADTwEAAuZ6wVU','🤡','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:33:49','corazones','sota','frances',0);
INSERT INTO stickers_cartas VALUES('caballo_corazones','AgADVwEAAhgewFU','👸','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:33:58','corazones','caballo','frances',0);
INSERT INTO stickers_cartas VALUES('rey_corazones','AgADGQEAAhRTwVU','🤴','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:34:09','corazones','rey','frances',0);
INSERT INTO stickers_cartas VALUES('as_treboles','AgADVgEAAk7KwFU','1⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:34:22','treboles','as','frances',0);
INSERT INTO stickers_cartas VALUES('2_treboles','AgAD7gADzD_AVQ','2⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:34:36','treboles','2','frances',0);
INSERT INTO stickers_cartas VALUES('3_treboles','AgADxAADjXXJVQ','3⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:34:45','treboles','3','frances',0);
INSERT INTO stickers_cartas VALUES('4_treboles','AgAD1QADdn3BVQ','4⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:34:56','treboles','4','frances',0);
INSERT INTO stickers_cartas VALUES('5_treboles','AgADQQEAAqyuwFU','5⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:35:05','treboles','5','frances',0);
INSERT INTO stickers_cartas VALUES('6_treboles','AgADLAEAAvSuwVU','6⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:35:13','treboles','6','frances',0);
INSERT INTO stickers_cartas VALUES('7_treboles','AgAD6QADmpzAVQ','7⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:35:24','treboles','7','frances',0);
INSERT INTO stickers_cartas VALUES('8_treboles','AgADZQEAAmsnwFU','8⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:35:35','treboles','8','frances',0);
INSERT INTO stickers_cartas VALUES('9_treboles','AgADHwEAAoPTwVU','9⃣','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:35:46','treboles','9','frances',0);
INSERT INTO stickers_cartas VALUES('10_treboles','AgADWAEAApCMwFU','🔟','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:36:03','treboles','10','frances',0);
INSERT INTO stickers_cartas VALUES('sota_treboles','AgADSgEAArVSwVU','🤡','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:36:11','treboles','sota','frances',0);
INSERT INTO stickers_cartas VALUES('caballo_treboles','AgADYwEAAtZUwVU','👸','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:36:20','treboles','caballo','frances',0);
INSERT INTO stickers_cartas VALUES('rey_treboles','AgADagEAArV1wFU','🤴','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:36:30','treboles','rey','frances',0);
INSERT INTO stickers_cartas VALUES('comodin','AgADRwEAAlPCwVU','🃏','PlayingCardsDeck',NULL,8301313897,'2026-05-09 01:36:42',NULL,NULL,'frances',0);
CREATE TABLE equivalencia_palos (
            id INTEGER PRIMARY KEY,
            frances TEXT UNIQUE,
            espanol TEXT UNIQUE
        );
INSERT INTO equivalencia_palos VALUES(1,'diamantes','oros');
INSERT INTO equivalencia_palos VALUES(2,'corazones','copas');
INSERT INTO equivalencia_palos VALUES(3,'picas','espadas');
INSERT INTO equivalencia_palos VALUES(4,'treboles','bastos');
CREATE TABLE equivalencia_rangos (
            id INTEGER PRIMARY KEY,
            frances TEXT UNIQUE,
            espanol TEXT UNIQUE
        );
INSERT INTO equivalencia_rangos VALUES(1,'as','as');
INSERT INTO equivalencia_rangos VALUES(2,'2','2');
INSERT INTO equivalencia_rangos VALUES(3,'3','3');
INSERT INTO equivalencia_rangos VALUES(4,'4','4');
INSERT INTO equivalencia_rangos VALUES(5,'5','5');
INSERT INTO equivalencia_rangos VALUES(6,'6','6');
INSERT INTO equivalencia_rangos VALUES(7,'7','7');
INSERT INTO equivalencia_rangos VALUES(8,'8','8');
INSERT INTO equivalencia_rangos VALUES(9,'9','9');
INSERT INTO equivalencia_rangos VALUES(10,'10','10');
INSERT INTO equivalencia_rangos VALUES(11,'j','sota');
INSERT INTO equivalencia_rangos VALUES(12,'q','caballo');
INSERT INTO equivalencia_rangos VALUES(13,'k','rey');
CREATE TABLE partidas_guerra (
    chat_id TEXT PRIMARY KEY,
    estado_json TEXT NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
PRAGMA writable_schema=ON;
CREATE TABLE IF NOT EXISTS sqlite_sequence(name,seq);
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('respuestas',477);
INSERT INTO sqlite_sequence VALUES('frases_sizaña',32);
INSERT INTO sqlite_sequence VALUES('keys_activacion',26);
INSERT INTO sqlite_sequence VALUES('contribuciones_grupo',1);
CREATE VIEW calculo_puntos AS
WITH MaxVotos AS (
    SELECT sala_id, ronda, categoria, MAX(votos) as max_votos
    FROM respuestas
    GROUP BY sala_id, ronda, categoria
),
Ganadores AS (
    SELECT r.sala_id, r.ronda, r.categoria, r.user_id, r.votos,
           (SELECT COUNT(*) FROM respuestas r2
            WHERE r2.sala_id = r.sala_id AND r2.ronda = r.ronda
              AND r2.categoria = r.categoria AND r2.votos = m.max_votos) as cant_ganadores
    FROM respuestas r
    JOIN MaxVotos m ON r.sala_id = m.sala_id AND r.ronda = m.ronda AND r.categoria = m.categoria
    WHERE r.votos = m.max_votos AND r.votos > 0
)
SELECT
    r.sala_id, r.ronda, r.categoria, r.user_id,
    CASE
        WHEN g.user_id IS NOT NULL THEN CAST(CEIL(10.0 / g.cant_ganadores) AS INTEGER)
        ELSE 0
    END as puntos_ganados
FROM respuestas r
LEFT JOIN Ganadores g ON r.sala_id = g.sala_id AND r.ronda = g.ronda
    AND r.categoria = g.categoria AND r.user_id = g.user_id;
CREATE INDEX idx_respuestas_sala_ronda_cat ON respuestas(sala_id, ronda, categoria);
CREATE INDEX idx_respuestas_votos ON respuestas(sala_id, ronda, categoria, votos);
CREATE INDEX idx_log_eventos_timestamp ON log_eventos(timestamp);
CREATE INDEX idx_log_eventos_tipo ON log_eventos(tipo_evento);
CREATE INDEX idx_descargas_user_fecha ON descargas_ytmusic(user_id, fecha_hora);
CREATE INDEX idx_respuestas_sala_ronda ON respuestas (sala_id, ronda);
CREATE INDEX idx_jugadores_user_id ON jugadores (user_id);
CREATE INDEX idx_partidas_estado ON partidas (estado);
PRAGMA writable_schema=OFF;
COMMIT;
