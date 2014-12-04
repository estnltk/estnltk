
#include "mrf2yh2mrf.h"

static  MRF2YH_LOEND mrf2yhPunktuatsioon[] = 
    {
        {FSWSTR("\""),  FSWSTR("WIQ")},
        {FSWSTR("\213"),FSWSTR("WIQ")}, // jutukas (tegelt alustav)
        {FSWSTR("\233"),FSWSTR("WIQ")}, // jutukas (tegelt lõpetav)
        {FSWSTR("\x00AB"),FSWSTR("WIQ")}, // jutukas "laquo" <<
        {FSWSTR("\x00BB"),FSWSTR("WIQ")}, // jutukas "raquo" >>
        {FSWSTR("\x2018"),FSWSTR("WIQ")}, // jutukas "lsquo" ülaind 6
        {FSWSTR("\x2019"),FSWSTR("WIQ")}, // jutukas "rsquo" ülaind 9
        {FSWSTR("\x201C"),FSWSTR("WIQ")}, // jutukas "ldquo" ülaind 66
        {FSWSTR("\x201D"),FSWSTR("WIQ")}, // jutukas "rdquo" ülaind 99
        {FSWSTR("\x201E"),FSWSTR("WIQ")}, // jutukas "bdquo" alaind 99
        {FSWSTR("\x2039"),FSWSTR("WIQ")}, // jutukas "lsaquo" <
        {FSWSTR("\x203A"),FSWSTR("WIQ")}, // jutukas "rsaquo" >
        {FSWSTR("\x0022"),FSWSTR("WIQ")}, // jutukas "quot"
        {FSWSTR("\x201B"),FSWSTR("WIQ")}, // jutukas ülaind tagurpidi 9
        {FSWSTR("\x2032"),FSWSTR("WIQ")}, // jutukas prim
        {FSWSTR("\x2033"),FSWSTR("WIQ")}, // jutukas topelprim
        {FSWSTR(":"),   FSWSTR("WIL")},
        {FSWSTR(";"),   FSWSTR("WIM")},
        {FSWSTR(","),   FSWSTR("WIC")},
        {FSWSTR("."),   FSWSTR("WCP")},
        {FSWSTR("?"),   FSWSTR("WCU")},
        {FSWSTR("!"),   FSWSTR("WCX")},
        {FSWSTR("-"),   FSWSTR("WID")},
        {FSWSTR("("),   FSWSTR("WOB")},
        {FSWSTR("["),   FSWSTR("WOB")},
        {FSWSTR("{"),   FSWSTR("WOB")},
        {FSWSTR("}"),   FSWSTR("WCB")},
        {FSWSTR("]"),   FSWSTR("WCB")},
        {FSWSTR(")"),   FSWSTR("WCB")},
        {FSWSTR("/"),   FSWSTR("WIA")},
        {FSWSTR("--"),  FSWSTR("WID")},
        {FSWSTR(".."),  FSWSTR("WIE")},
        {FSWSTR("..."), FSWSTR("WIE")},
   };

static  MRF2YH_LOEND mrf2yhSona[]=
    {
        //{"&hellip;"),  FSWSTR("WIE"},
        //{"&mdash;"),  FSWSTR("WID"},
        //neid ei kasutata, aga tegelt oleks mo'ttekas - 
        //lause alguses muud vo'imalust kui see ma'rgend pole
        //{FSWSTR("Ega"),             FSWSTR("RR")},
        //{FSWSTR("Vahel"),           FSWSTR("RRK")},
        //{FSWSTR("Vaid"),            FSWSTR("RR")},
        {FSWSTR("aga"),             FSWSTR("CCJA")},
        //{FSWSTR("algul"),           FSWSTR("RRK")}, hjk 03.03.2008
        //{FSWSTR("ainult"),          FSWSTR("RRM")}, hjk 03.03.2008
        {FSWSTR("elluj\xE4\xE4nud"),FSWSTR("NCSN")},
        {FSWSTR("hoopis"),          FSWSTR("RRM")},
        {FSWSTR("iial"),            FSWSTR("RRM")},
        {FSWSTR("ilmaj\xE4\xE4nud"),FSWSTR("NCSN")},
        {FSWSTR("ja"),              FSWSTR("CCJA")},
        {FSWSTR("justkui"),         FSWSTR("CSRR")},
        {FSWSTR("j\xE4lle"),        FSWSTR("RRM")},
        {FSWSTR("kas"),             FSWSTR("RRY")},
        {FSWSTR("koju"),            FSWSTR("NCSA")},
        //{FSWSTR("kord"),            FSWSTR("NCSN")}, hjk 03.03.2008
        {FSWSTR("kuhu"),            FSWSTR("RRY")},
        {FSWSTR("kui"),             FSWSTR("CSRR")},
        {FSWSTR("kuidas"),          FSWSTR("RRY")},
        {FSWSTR("kuigi"),           FSWSTR("CSRR")},
        {FSWSTR("kunagi"),          FSWSTR("RRM")},
        {FSWSTR("kus"),             FSWSTR("RRY")},
        {FSWSTR("maha"),            FSWSTR("RRM")},
        {FSWSTR("miks"),            FSWSTR("RRY")},
        {FSWSTR("millal"),          FSWSTR("RRY")},
        {FSWSTR("nagu"),            FSWSTR("CSRR")},
        {FSWSTR("nii"),             FSWSTR("RRM")},
        {FSWSTR("ning"),            FSWSTR("CCJA")},
        {FSWSTR("n\xFC\xFC\x64"),      FSWSTR("RRM")}, // nüüd
        {FSWSTR("oli"),             FSWSTR("VOLI")},
        {FSWSTR("on"),              FSWSTR("VON")},
        {FSWSTR("otsekui"),         FSWSTR("CSRR")},
        //{FSWSTR("parem"),           FSWSTR("ASN")},
        {FSWSTR("peaaegu"),         FSWSTR("RRM")},
        {FSWSTR("praegu"),          FSWSTR("RRM")},
        {FSWSTR("rohkem"),          FSWSTR("RRM")},
        //{FSWSTR("ta"),              FSWSTR("PP3SN")},
        {FSWSTR("t\xE4iesti"),      FSWSTR("RRM")},
        {FSWSTR("uuesti"),          FSWSTR("RRM")},
        {FSWSTR("v\xE4ga"),         FSWSTR("RRM")},
	//{FSWSTR("v\xF5idud"),       FSWSTR("NCSN")},
        {FSWSTR("\xFCldse"),        FSWSTR("RRM")},
        {FSWSTR("\xFClej\xF4\xF4nud"), FSWSTR("VMAZ")},
        {FSWSTR("\xFCles"),         FSWSTR("RRM")},
        {FSWSTR("\xE4kki"),         FSWSTR("RRM")}
    };

static  MRF2YH_LOEND mrf2yhRr[]=
    {  
        {FSWSTR("-vastast"),           FSWSTR("RRK") },
        {FSWSTR("aina"),               FSWSTR("RRO") },
        {FSWSTR("ainult"),             FSWSTR("RRM")}, //hjk 03.03.2008
        {FSWSTR("alasti"),             FSWSTR("ASXRR") },
        {FSWSTR("algul"),              FSWSTR("RRK") },
        {FSWSTR("all"),                FSWSTR("RRK") },
        {FSWSTR("alla"),               FSWSTR("RRK") },
        {FSWSTR("allagi"),             FSWSTR("RRK") },
        {FSWSTR("allapoole"),          FSWSTR("RRK") },
        {FSWSTR("allpool"),            FSWSTR("RRK") },
        {FSWSTR("alt"),                FSWSTR("RRK") },
        {FSWSTR("altpoolt"),           FSWSTR("RRK") },
        {FSWSTR("arvatavasti"),        FSWSTR("RRO") },
        {FSWSTR("asemele"),            FSWSTR("RRK") },
        {FSWSTR("edasi"),              FSWSTR("RRK") },
        {FSWSTR("eel"),                FSWSTR("RRK") },
        {FSWSTR("eelk\xF5ige"),        FSWSTR("RRO") },
        {FSWSTR("ees"),                FSWSTR("RRK") },
        {FSWSTR("eespool"),            FSWSTR("RRK") },
        {FSWSTR("eest"),               FSWSTR("RRK") },
        {FSWSTR("eestpoolt"),          FSWSTR("RRK") },
        {FSWSTR("ehk"),                FSWSTR("RRO") },
        {FSWSTR("enne"),               FSWSTR("RRK") },
        {FSWSTR("ette"),               FSWSTR("RRK") },
        {FSWSTR("ettegi"),             FSWSTR("RRK") },
        {FSWSTR("ettepoole"),          FSWSTR("RRK") },
        {FSWSTR("heaks"),              FSWSTR("RRK") },
        {FSWSTR("hoolimata"),          FSWSTR("RRK") },
        {FSWSTR("hoopis"),             FSWSTR("RRO") },
        {FSWSTR("hulgas"),             FSWSTR("RRK") },
        {FSWSTR("iganes"),             FSWSTR("RRO") },
        {FSWSTR("igatahes"),           FSWSTR("RRO") },
        {FSWSTR("ilma"),               FSWSTR("RRK") },
        {FSWSTR("isegi"),              FSWSTR("RRO") },
        {FSWSTR("jaoks"),              FSWSTR("RRK") },
        {FSWSTR("ju"),                 FSWSTR("RRO") },
        {FSWSTR("just"),               FSWSTR("RRO") },
        {FSWSTR("juurde"),             FSWSTR("RRK") },
        {FSWSTR("juures"),             FSWSTR("RRK") },
        {FSWSTR("j\xE4rel"),           FSWSTR("RRK") },
        {FSWSTR("j\xE4rele"),          FSWSTR("RRK") },
        {FSWSTR("j\xE4rgi"),           FSWSTR("RRK") },
        {FSWSTR("ka"),                 FSWSTR("RRO") },
        {FSWSTR("kaasas"),             FSWSTR("RRK") },
        {FSWSTR("kahjuks"),            FSWSTR("RRO") },
        {FSWSTR("kallal"),             FSWSTR("RRK") },
        {FSWSTR("kallale"),            FSWSTR("RRK") },
        {FSWSTR("kannul"),             FSWSTR("RRK") },
        {FSWSTR("kanti"),              FSWSTR("RRK") },
        {FSWSTR("kasv\xF5i"),          FSWSTR("RRO") },
        {FSWSTR("keskel"),             FSWSTR("RRK") },
        {FSWSTR("keskele"),            FSWSTR("RRK") },
        {FSWSTR("kindlasti"),          FSWSTR("RRO") },
        {FSWSTR("kiuste"),             FSWSTR("RRK") },
        {FSWSTR("koguni"),             FSWSTR("RRO") },
        {FSWSTR("kohal"),              FSWSTR("RRK") },
        {FSWSTR("kohale"),             FSWSTR("RRK") },
        {FSWSTR("koos"),               FSWSTR("RRK") },
        {FSWSTR("korral"),             FSWSTR("RRK") },
        {FSWSTR("k\xFClge"),           FSWSTR("RRK") },
        {FSWSTR("k\xFCljes"),          FSWSTR("RRK") },
        {FSWSTR("k\xFCljest"),         FSWSTR("RRK") },
        {FSWSTR("k\xFCllap"),          FSWSTR("RRO") },
        {FSWSTR("k\xFC\xFCsi"),        FSWSTR("RRK") },
        {FSWSTR("k\xF5rval"),          FSWSTR("RRK") },
        {FSWSTR("k\xF5rvale"),         FSWSTR("RRK") },
        {FSWSTR("k\xF5rvalt"),         FSWSTR("RRK") },
        {FSWSTR("las"),                FSWSTR("RRO") },
        {FSWSTR("lausa"),              FSWSTR("RRO") },
        {FSWSTR("ligi"),               FSWSTR("RRK") },
        {FSWSTR("l\xE4\x62i"),            FSWSTR("RRK") }, // läbi
        {FSWSTR("l\xE4hedal"),         FSWSTR("RRK") },
        {FSWSTR("l\xE4hedale"),        FSWSTR("RRK") },
        {FSWSTR("l\xE4hedalt"),        FSWSTR("RRK") },
        {FSWSTR("muide"),              FSWSTR("RRO") },
        {FSWSTR("muidu"),              FSWSTR("RRO") },
        {FSWSTR("muidugi"),            FSWSTR("RRO") },
        {FSWSTR("m\xF6\xF6\x64\x61"),        FSWSTR("RRK") }, // mõõda
        {FSWSTR("nimelt"),             FSWSTR("RRO") },
        {FSWSTR("n\xE4htavasti"),      FSWSTR("RRO") },
        {FSWSTR("ometi"),              FSWSTR("RRO") },
        {FSWSTR("otsa"),               FSWSTR("RRK") },
        {FSWSTR("otsas"),              FSWSTR("RRK") },
        {FSWSTR("peal"),               FSWSTR("RRK") },
        {FSWSTR("peale"),              FSWSTR("RRK") },
        {FSWSTR("pealt"),              FSWSTR("RRK") },
        {FSWSTR("pihta"),              FSWSTR("RRK") },
        {FSWSTR("pingul"),             FSWSTR("ASXRR") },
        {FSWSTR("poolt"),              FSWSTR("RRK") },
        {FSWSTR("p\xE4rast"),          FSWSTR("RRK") },
        {FSWSTR("p\xE4ris"),           FSWSTR("ASXRR") },
        {FSWSTR("ringi"),              FSWSTR("RRK") },
        {FSWSTR("salkus"),             FSWSTR("ASXRR") },
        {FSWSTR("sees"),               FSWSTR("RRK") },
        {FSWSTR("seespool"),           FSWSTR("RRK") },
        {FSWSTR("seest"),              FSWSTR("RRK") },
        {FSWSTR("seestpoolt"),         FSWSTR("RRK") },
        {FSWSTR("siis"),               FSWSTR("RRO") },
        {FSWSTR("sinnapoole"),         FSWSTR("RRK") },
        {FSWSTR("sisse"),              FSWSTR("RRK") },
        {FSWSTR("sissepoole"),         FSWSTR("RRK") },
        {FSWSTR("taga"),               FSWSTR("RRK") },
        {FSWSTR("tagant"),             FSWSTR("RRK") },
        {FSWSTR("tagapool"),           FSWSTR("RRK") },
        {FSWSTR("tagasi"),             FSWSTR("RRK") },
        {FSWSTR("taha"),               FSWSTR("RRK") },
        {FSWSTR("tahapoole"),          FSWSTR("RRK") },
        {FSWSTR("takka"),              FSWSTR("RRK") },
        {FSWSTR("tarvis"),             FSWSTR("RRK") },
        {FSWSTR("teel"),               FSWSTR("RRK") },
        {FSWSTR("teispool"),           FSWSTR("RRK") },
        {FSWSTR("t\xE4is"),            FSWSTR("ASXRR") },
        {FSWSTR("t\xF5en\xE4oliselt"), FSWSTR("RRO") },
        {FSWSTR("t\xF5epoolest"),      FSWSTR("RRO") },
        {FSWSTR("t\xF5\x65sti"),          FSWSTR("RRO") }, // täesti
        {FSWSTR("t\xF5ttu"),           FSWSTR("RRK") },
        //{FSWSTR("vaat"),               FSWSTR("RRO") }, hjk 03.03.2008
        {FSWSTR("vaatamata"),          FSWSTR("RRK") },
        {FSWSTR("vaevalt"),            FSWSTR("RRO") },
        {FSWSTR("vahel"),              FSWSTR("RRK") },
        {FSWSTR("vahele"),             FSWSTR("RRK") },
        {FSWSTR("vahelt"),             FSWSTR("RRK") },
        {FSWSTR("vahest"),             FSWSTR("RRO") },
        {FSWSTR("valmis"),             FSWSTR("ASXRR") },
        {FSWSTR("vastas"),             FSWSTR("RRK") },
        {FSWSTR("vastavalt"),          FSWSTR("RRK") },
        {FSWSTR("vastu"),              FSWSTR("RRK") },
        {FSWSTR("vist"),               FSWSTR("RRO") },
        {FSWSTR("vististi"),           FSWSTR("RRO") },
        {FSWSTR("v\xE4ljapoole"),      FSWSTR("RRK") },
        {FSWSTR("v\xE4ljaspool"),      FSWSTR("RRK") },
        {FSWSTR("v\xE4ljastpoolt"),    FSWSTR("RRK") },
        {FSWSTR("v\xE4\xE4rt"),        FSWSTR("ASXRR") },
        {FSWSTR("v\xF5ib-olla"),       FSWSTR("RRO") },
        {FSWSTR("v\xF5idu"),           FSWSTR("RRK") },
        {FSWSTR("\xFChes"),            FSWSTR("RRK") },
        {FSWSTR("\xFCheski"),          FSWSTR("RRK") },
        {FSWSTR("\xFCksnes"),          FSWSTR("RRO") },
        {FSWSTR("\xFCle"),             FSWSTR("RRK") },
        {FSWSTR("\xFCles-alla"),       FSWSTR("RRK") },
        {FSWSTR("\xFCmber"),           FSWSTR("RRK") },
        {FSWSTR("\xFCmbert"),          FSWSTR("RRK") },
        {FSWSTR("\xE4ra"),             FSWSTR("RRA") },
        {FSWSTR("\xF5ige"),            FSWSTR("RRO") },
        {FSWSTR("\xF5igupoolest"),     FSWSTR("RRO") },
        // suurtähelistel pole mõtet, 
        // sest string eelnevalt väiketäheliseks teisendatud
        //{FSWSTR("\232hes"),            FSWSTR("RRK") },
        //{FSWSTR("\232ksnes"),          FSWSTR("RRO") },
        //{FSWSTR("\232le"),             FSWSTR("RRK") },
        //{FSWSTR("\232mber"),           FSWSTR("RRK") },
        //{FSWSTR("\345ige"),            FSWSTR("RRO") },
        //{FSWSTR("\345igupoolest"),     FSWSTR("RRO") },
    };

static  MRF2YH_LOEND mrf2yhYksTeine[]=
    {
    {FSWSTR("\xFCks"),      FSWSTR("YK") },
	{FSWSTR("teine"),      FSWSTR("TEINE") },

	};

static  MRF2YH_LOEND mrf2yhAse[]=
    {
        {FSWSTR("mina"),       FSWSTR("PP1") },
        {FSWSTR("sina"),       FSWSTR("PP2") },
        {FSWSTR("tema"),       FSWSTR("PP3") },
	};


static  MRF2YH_LOEND mrf2yhKaands[]=
    {
	    { FSWSTR("ab"),	    FSWSTR("S")  },
	    { FSWSTR("abl"),	FSWSTR("SA") },
	    { FSWSTR("ad"),	    FSWSTR("SA") },
	    { FSWSTR("adt"),	FSWSTR("SA") },
	    { FSWSTR("all"),	FSWSTR("SA") },
	    { FSWSTR("el"),	    FSWSTR("SA") },
	    { FSWSTR("es"),	    FSWSTR("S")  },
	    { FSWSTR("g"),	    FSWSTR("SG") },
	    { FSWSTR("ill"),	FSWSTR("SA") },
	    { FSWSTR("in"),	    FSWSTR("SA") },
	    { FSWSTR("kom"),	FSWSTR("S")  },
	    { FSWSTR("n"),	    FSWSTR("SN") },
	    { FSWSTR("p"),	    FSWSTR("S1") },
	    { FSWSTR("ter"),	FSWSTR("S")  },
	    { FSWSTR("tr"),     FSWSTR("S")  },
    };

static  MRF2YH_LOEND mrf2yhPoords[]=
    {
	    { FSWSTR("b"),	        FSWSTR("3")   },
	    { FSWSTR("d"),	        FSWSTR("2")   },
	    { FSWSTR("da"),	        FSWSTR("D")   },
	    { FSWSTR("des"),	    FSWSTR("G")   },
	    { FSWSTR("ge"),	        FSWSTR("K")   },
	    { FSWSTR("gem"),	    FSWSTR("K")   },
	    { FSWSTR("gu"),	        FSWSTR("3")   },
	    { FSWSTR("ks"),	        FSWSTR("S")   },
	    { FSWSTR("ksid"),	    FSWSTR("S")   },
	    { FSWSTR("ksime"),	    FSWSTR("S")   },
	    { FSWSTR("ksin"),	    FSWSTR("S")   },
	    { FSWSTR("ksite"),	    FSWSTR("S")   },
	    { FSWSTR("ma"),	        FSWSTR("M")   },
	    { FSWSTR("maks"),	    FSWSTR("G")   },
	    { FSWSTR("mas"),	    FSWSTR("M")   },
	    { FSWSTR("mast"),	    FSWSTR("M")   },
	    { FSWSTR("mata"),	    FSWSTR("ASS") },
	    { FSWSTR("me"),	        FSWSTR("1")   },
	    { FSWSTR("n"),	        FSWSTR("1")   },
	    { FSWSTR("neg"),	    FSWSTR("E")   },
	    { FSWSTR("neg ge"),	    FSWSTR("S")   },
	    { FSWSTR("neg gem"),	FSWSTR("S")   },
	    { FSWSTR("neg gu"), 	FSWSTR("S")   },
	    { FSWSTR("neg ks"),	    FSWSTR("S")   },
	    { FSWSTR("neg me"),	    FSWSTR("S")   },
	    { FSWSTR("neg nud"),	FSWSTR("AS")  },
	    { FSWSTR("neg nuks"),   FSWSTR("S")   },
	    { FSWSTR("neg o"),	    FSWSTR("K")   }, //FSWSTR("pole"; aga _V_ neg o@VMU@&auml;ra
	    { FSWSTR("neg tud"),    FSWSTR("AA")  },
	    { FSWSTR("neg vat"),    FSWSTR("Q")   },
	    { FSWSTR("nud"),	    FSWSTR("AS")  },
	    { FSWSTR("nuks"),	    FSWSTR("S")   },
	    { FSWSTR("nuksid"),	    FSWSTR("S")   },
	    { FSWSTR("nuksime"),    FSWSTR("S")   },
	    { FSWSTR("nuksin"),	    FSWSTR("S")   },
	    { FSWSTR("nuksite"),    FSWSTR("S")   },
	    { FSWSTR("nuvat"),	    FSWSTR("Q")   },
	    { FSWSTR("o"),	        FSWSTR("K")   },
	    { FSWSTR("s"),	        FSWSTR("3")   },
        { FSWSTR("sid"),	    FSWSTR("3ja2")}, // SID_VARIANDID
	    { FSWSTR("sime"),	    FSWSTR("1")   },
	    { FSWSTR("sin"),	    FSWSTR("1")   },
	    { FSWSTR("site"),	    FSWSTR("2")   }, //SITE_VARIANT
	    { FSWSTR("ta"),	        FSWSTR("N")   },
	    { FSWSTR("tagu"),	    FSWSTR("P")   },
	    { FSWSTR("taks"),	    FSWSTR("P")   },
	    { FSWSTR("takse"),	    FSWSTR("P")   },
	    { FSWSTR("tama"),	    FSWSTR("M")   },
	    { FSWSTR("tav"),	    FSWSTR("AP")  },
	    { FSWSTR("tavat"),	    FSWSTR("Q")   },
	    { FSWSTR("te"),	        FSWSTR("2")   },
	    { FSWSTR("ti"),	        FSWSTR("P")   },
	    { FSWSTR("tud"),	    FSWSTR("AS")  },
	    { FSWSTR("tuks"),	    FSWSTR("P")   },
	    { FSWSTR("tuvat"),	    FSWSTR("Q")   },
	    { FSWSTR("v"),	        FSWSTR("AP")  },
	    { FSWSTR("vad"),	    FSWSTR("3")   },
	    { FSWSTR("vat"),	    FSWSTR("Q")   },
    };

// käändsõnad ja 
// muutumatud DXIG -> RR RR II ASG 
static  MRF2YH_LOEND mrf2yhNoomTags[]=
    {
	    { FSWSTR("A"),	    FSWSTR("A")   },
	    { FSWSTR("C"),	    FSWSTR("A")   },
	    { FSWSTR("U"),	    FSWSTR("A")   },
	    { FSWSTR("S"),	    FSWSTR("NC")  },
	    { FSWSTR("H"),	    FSWSTR("NP")  },
	    { FSWSTR("N"),	    FSWSTR("MC")  },
	    { FSWSTR("O"),	    FSWSTR("MO")  },
	    { FSWSTR("P"),	    FSWSTR("P")   },
	    { FSWSTR("Y"),	    FSWSTR("Y")   },    
	    { FSWSTR("D"),	    FSWSTR("RR")   },    
	    { FSWSTR("X"),	    FSWSTR("RR")   },    
	    { FSWSTR("I"),	    FSWSTR("II")   },    
	    { FSWSTR("G"),	    FSWSTR("ASG")   },    
    };

static  MRF2YH_LOEND mrf2yhAsxrr[]=
    { 
        { FSWSTR("alasti"),	    FSWSTR("ASXRR") },
        { FSWSTR("pingul"),	    FSWSTR("ASXRR") },
        { FSWSTR("p\xE4ris"),	FSWSTR("ASXRR") },
        { FSWSTR("salkus"),	    FSWSTR("ASXRR") },
        { FSWSTR("t\xE4is"),	FSWSTR("ASXRR") },
        { FSWSTR("valmis"),	    FSWSTR("ASXRR") },
        { FSWSTR("v\xE4\xE4rt"),FSWSTR("ASXRR") },
    };

static  MRF2YH_LOEND mrf2yhSidec[]=
    {
        // "ja"),  FSWSTR("ning"),  FSWSTR("aga"),  
        // on CCJA juba massiivis sona_ym[]
        { FSWSTR("ega"),	    FSWSTR("CC")  },
        { FSWSTR("ehk"),	    FSWSTR("CC")  },
        { FSWSTR("elik"),	    FSWSTR("CC")  },
        { FSWSTR("ent"),	    FSWSTR("CC")  },
        { FSWSTR("kuid"),	    FSWSTR("CC")  },
        { FSWSTR("vaid"),	    FSWSTR("CCA") },
        { FSWSTR("v\xF5i"),	    FSWSTR("CC")  },
        { FSWSTR("&"),	    FSWSTR("CC")  },
        { FSWSTR("ja/v\xF5i"),	    FSWSTR("CC")  },
    };

static  MRF2YH_LOEND2 mrf2yhEesJaTaga[]=
    {
        { FSWSTR("alla"),           FSWSTR("ST"),   FSWSTR("SPGP") } ,
	   // { FSWSTR("allapoole"),      FSWSTR("STA"),  FSWSTR("SP") } ,
       // { FSWSTR("allpool"),        FSWSTR("STA"),  FSWSTR("SP") } ,
       // { FSWSTR("eespool"),        FSWSTR("STA"),  FSWSTR("SP") } ,
       // { FSWSTR("hommikupoole"),   FSWSTR("STA"),  FSWSTR("SP") } ,
        { FSWSTR("alates"),         FSWSTR("STA"),  FSWSTR("SPA") } , /* uus */
        { FSWSTR("hoolimata"),      FSWSTR("STA"),  FSWSTR("SPA") } , /* uus */
        { FSWSTR("koos"),           FSWSTR("STA"),  FSWSTR("SPA") } ,
        { FSWSTR("ligi"),           FSWSTR("ST"),   FSWSTR("SPGP") } ,
        { FSWSTR("l\xE4\x62i"),        FSWSTR("STGE"), FSWSTR("SPG") } , // läbi hjk 03.03.2008
        { FSWSTR("m\xF6\xF6\x64\x61"),    FSWSTR("STP"),  FSWSTR("SP") } , // mõõda
        { FSWSTR("peale"),          FSWSTR("STGE"), FSWSTR("SPGP") } ,
       // { FSWSTR("pealpool"),       FSWSTR("STA"),  FSWSTR("SP") } ,
        { FSWSTR("pealt"),          FSWSTR("ST"),   FSWSTR("SP") } ,
        { FSWSTR("p\xE4rast"),      FSWSTR("ST"),   FSWSTR("SP") } ,
       // { FSWSTR("seespool"),       FSWSTR("STA"),  FSWSTR("SP") } , /* uus */
        { FSWSTR("seoses"),         FSWSTR("STA"),  FSWSTR("SPA") } , /* uus */
       // { FSWSTR("siiapoole"),      FSWSTR("STA"),  FSWSTR("SP") } ,
       // { FSWSTR("sissepoole"),     FSWSTR("STA"),  FSWSTR("SP") } , /* uus */
       // { FSWSTR("tagapool"),       FSWSTR("STA"),  FSWSTR("SP") } ,
        { FSWSTR("t\xFCkkis"),      FSWSTR("ST"),   FSWSTR("SP") } ,
        { FSWSTR("vastu"),          FSWSTR("ST"),   FSWSTR("SP") } ,
        { FSWSTR("\xFCle"),         FSWSTR("ST"),   FSWSTR("SPG") } ,
        { FSWSTR("\xFCmber"),       FSWSTR("ST"),   FSWSTR("SPG") } ,
        { FSWSTR("\xFCmbert"),      FSWSTR("ST"),   FSWSTR("SPG") } ,
        { FSWSTR("vaatamata"),      FSWSTR("STA"),  FSWSTR("SPA") } , /* uus */
        { FSWSTR("vastavalt"),      FSWSTR("STA"),  FSWSTR("SPA") } , /* uus */
       // { FSWSTR("v\204ljapoole"),  FSWSTR("STA"),  FSWSTR("SP") } ,
	   // { FSWSTR("v\204ljaspool"),  FSWSTR("STA"),  FSWSTR("SP") } ,
       // { FSWSTR("\201lalpool"),    FSWSTR("STA"),  FSWSTR("SP") } ,
       // { FSWSTR("\201levalpool"),  FSWSTR("STA"),  FSWSTR("SP") } ,
       // { FSWSTR("\223htupoole"),   FSWSTR("STA"),  FSWSTR("SP") } ,
    };

static  MRF2YH_LOEND mrf2yhEesVoiTaga[]=
    {
        { FSWSTR("enne"),       FSWSTR("SP") } , 
        { FSWSTR("ilma"),       FSWSTR("SP") } , 
        { FSWSTR("keset"),      FSWSTR("SP") } , 
        { FSWSTR("kesk"),       FSWSTR("SP") } , 
        { FSWSTR("kuni"),       FSWSTR("SPA") } , 
        { FSWSTR("pidi"),       FSWSTR("STP") } ,
        { FSWSTR("piki"),       FSWSTR("SP") } , 
        { FSWSTR("saadik"),     FSWSTR("STA") } ,
        { FSWSTR("tagasi"),     FSWSTR("STP") } ,
        { FSWSTR("teispool"),   FSWSTR("SP") } , 
        { FSWSTR("t\xE4nu"),    FSWSTR("SPA") } ,
        { FSWSTR("\xFChes"),    FSWSTR("SPA") } ,    
    };

extern "C"
    {                           // kirjete sortimiseks 
    int CmpRecMRF2YH_LOEND(     // kirjete võrdlemine
        const void* p1, 
        const void* p2)
        {
        const MRF2YH_LOEND *p_rec1=(const MRF2YH_LOEND*)p1;
        const MRF2YH_LOEND *p_rec2=(const MRF2YH_LOEND*)p2;

        return FSStrCmp(p_rec1->p_key, p_rec2->p_key);
        }
                                // kahendotsimiseks
    int CmpKeyMRF2YH_LOEND(     // võtme võrdlemine kirje võtmega
        const void* pk, const void* pr)
        {
        const FSWCHAR *p_key=(const FSWCHAR*)pk;
        const MRF2YH_LOEND *p_rec=(const MRF2YH_LOEND*)pr;

        return FSStrCmp(p_key, p_rec->p_key);
        }
                                // kirjete sortimiseks 
    int CmpRecMRF2YH_LOEND2(    // kirjete võrdlemine
        const void* p1, 
        const void* p2)
        {
        const MRF2YH_LOEND2 *p_rec1=(const MRF2YH_LOEND2*)p1;
        const MRF2YH_LOEND2 *p_rec2=(const MRF2YH_LOEND2*)p2;

        return FSStrCmp(p_rec1->p_key, p_rec2->p_key);
        }
                                // kahendotsimiseks
    int CmpKeyMRF2YH_LOEND2(    // võtme võrdlemine kirje võtmega
        const void* pk, const void* pr)
        {
        const FSWCHAR *p_key=(const FSWCHAR*)pk;
        const MRF2YH_LOEND2 *p_rec=(const MRF2YH_LOEND2*)pr;

        return FSStrCmp(p_key, p_rec->p_key);
        }
    }


void MRF2YH2MRF::InitClassVariables(void)
	{
    muut1=FSWSTR("DXIG");
    verb_v_adj=FSWSTR("VA");
    yks_v_teine_sonaliik=FSWSTR("NOP");
    sid_variandid=FSWSTR("3ja2");
    punktuatsioon.Start(
        mrf2yhPunktuatsioon,
        sizeof(mrf2yhPunktuatsioon)/sizeof(MRF2YH_LOEND),
        CmpRecMRF2YH_LOEND, // võrdleb(kirje, kirje)
        CmpKeyMRF2YH_LOEND, // võrdleb(võti, kirje)
        true);              // sordib viitade massiivi koopia
    sona.Start(
        mrf2yhSona,
        sizeof(mrf2yhSona)/sizeof(MRF2YH_LOEND),
        CmpRecMRF2YH_LOEND, // võrdleb(kirje, kirje)
        CmpKeyMRF2YH_LOEND, // võrdleb(võti, kirje)
        true);              // sordib viitade massiivi koopia
    rr.Start(
        mrf2yhRr,
        sizeof(mrf2yhRr)/sizeof(MRF2YH_LOEND),
        CmpRecMRF2YH_LOEND, // võrdleb(kirje, kirje)
        CmpKeyMRF2YH_LOEND, // võrdleb(võti, kirje)
        true);              // sordib viitade massiivi koopia
    yksTeine.Start(
        mrf2yhYksTeine,
        sizeof(mrf2yhYksTeine)/sizeof(MRF2YH_LOEND),
        CmpRecMRF2YH_LOEND, // võrdleb(kirje, kirje)
        CmpKeyMRF2YH_LOEND, // võrdleb(võti, kirje)
        true);              // sordib viitade massiivi koopia
    kaanded.Start(
        mrf2yhKaands,
        sizeof(mrf2yhKaands)/sizeof(MRF2YH_LOEND),
        CmpRecMRF2YH_LOEND, // võrdleb(kirje, kirje)
        CmpKeyMRF2YH_LOEND, // võrdleb(võti, kirje)
        true);
    poorded.Start(
        mrf2yhPoords,
        sizeof(mrf2yhPoords)/sizeof(MRF2YH_LOEND),
        CmpRecMRF2YH_LOEND, // võrdleb(kirje, kirje)
        CmpKeyMRF2YH_LOEND, // võrdleb(võti, kirje)
        true);
    ase.Start(
        mrf2yhAse,
        sizeof(mrf2yhAse)/sizeof(MRF2YH_LOEND),
        CmpRecMRF2YH_LOEND, // võrdleb(kirje, kirje)
        CmpKeyMRF2YH_LOEND, // võrdleb(võti, kirje)
        true);
    noomTags.Start(
        mrf2yhNoomTags,
        sizeof(mrf2yhNoomTags)/sizeof(MRF2YH_LOEND),
        CmpRecMRF2YH_LOEND, // võrdleb(kirje, kirje)
        CmpKeyMRF2YH_LOEND, // võrdleb(võti, kirje)
        true);
    asxrr.Start(
        mrf2yhAsxrr,
        sizeof(mrf2yhAsxrr)/sizeof(MRF2YH_LOEND),
        CmpRecMRF2YH_LOEND, // võrdleb(kirje, kirje)
        CmpKeyMRF2YH_LOEND, // võrdleb(võti, kirje)
        true);
    sidec.Start(
        mrf2yhSidec,
        sizeof(mrf2yhSidec)/sizeof(MRF2YH_LOEND),
        CmpRecMRF2YH_LOEND, // võrdleb(kirje, kirje)
        CmpKeyMRF2YH_LOEND, // võrdleb(võti, kirje)
        true);

    eesJaTaga.Start(
        mrf2yhEesJaTaga,
        sizeof(mrf2yhEesJaTaga)/sizeof(MRF2YH_LOEND2),
        CmpRecMRF2YH_LOEND2, // võrdleb(kirje, kirje)
        CmpKeyMRF2YH_LOEND2, // võrdleb(võti, kirje)
        true);
    eesVoiTaga.Start(
        mrf2yhEesVoiTaga,
        sizeof(mrf2yhEesVoiTaga)/sizeof(MRF2YH_LOEND),
        CmpRecMRF2YH_LOEND, // võrdleb(kirje, kirje)
        CmpKeyMRF2YH_LOEND, // võrdleb(võti, kirje)
        true);
    }

void MRF2YH2MRF::FsTags2YmmTags(
    MRFTULEMUSED* p_mTulemused) const
    {
    assert(ClassInvariant());

    p_mTulemused->StrctKomadLahku();    // Koma sisaldavad vormid tõstame lahku
    int i;
    FSXSTRING xstr=p_mTulemused->s6na;
    xstr.MakeLower();
    TaheHulgad::AsendaMitu(&xstr, TaheHulgad::uni_kriipsud, TaheHulgad::amor_kriipsud);
    if(p_mTulemused->on_tulem()==false)
        {
        // tundmatu, isegi mõistataja ei sõõnud või ei mõistatatudki
        // mrf2yh2.cpp/mrf2yh21() 66-92
        MRFTUL* p_mTul=p_mTulemused->AddPlaceHolder();
        if(p_mTul==NULL)
            {
            throw(VEAD(ERR_X_TYKK,ERR_NOMEM,__FILE__,__LINE__,"$Revision: 1145 $"));
            }
        p_mTul->tyvi=xstr;
        p_mTul->sl=FSWSTR("Z");
        MRF2YH_LOEND* p_rec;
        p_rec=punktuatsioon.Get((FSWCHAR*)(const FSWCHAR*)xstr);
        if(p_rec!= NULL)
            {
            //p_mTul->lopp=FSWSTR("0"); // näib, et pole vajalik
            p_mTul->mrg1st=p_rec->p_yhTag;
            return;
            }
        // tundmatu mittepunktuatsioon saab
        // ainult ühestamismägendi "X"
        p_mTul->mrg1st=FSWSTR("X");
        return;
        }
	int idxLastEnne=p_mTulemused->idxLast;
    for(i=0; i<idxLastEnne; i++)
        {
		FSXSTRING yhmarg1;
		FSXSTRING yhmarg2;
		FSXSTRING yhmarg3;
		MRFTUL *tmpPtr=NULL;

        FsTags2YmmTags(&xstr,(*p_mTulemused)[i], 
						yhmarg1, yhmarg2, yhmarg3);
		assert(yhmarg1.GetLength() > 0);
		if(yhmarg2.GetLength() > 0)
			{
			// Lisa sappa sellise ühestajamärgendiga analüüsivariant
			tmpPtr=p_mTulemused->AddClone(*((*p_mTulemused)[i]));
			if(tmpPtr==NULL)
                {
                throw(VEAD(ERR_X_TYKK,ERR_NOMEM,__FILE__,__LINE__,"$Revision: 1145 $"));
                }
			tmpPtr->mrg1st = yhmarg2;
			if(yhmarg3.GetLength() > 0)
				{
				// Lisa sappa sellise ühestajamärgendiga analüüsivariant
				tmpPtr=p_mTulemused->AddClone(*((*p_mTulemused)[i]));
				if(tmpPtr==NULL)
                    {
                    throw(VEAD(ERR_X_TYKK,ERR_NOMEM,__FILE__,__LINE__,"$Revision: 1145 $"));
                    }
				tmpPtr->mrg1st = yhmarg3;
				}
			}
		// yhmarg1 --> i-ndasse analüüsivarianti
		(*p_mTulemused)[i]->mrg1st = yhmarg1;
        }
    }

void MRF2YH2MRF::FsTags2YmmTags(
	const FSXSTRING* p_sona,
	MRFTUL* p_mTul,
	FSXSTRING& yhmarg1,
	FSXSTRING& yhmarg2,
	FSXSTRING& yhmarg3	
	) const
    {
	FSUNUSED(yhmarg3);
    MRF2YH_LOEND* p_rec;
    const FSWCHAR* p_yTag;

    // punktuatsioon --> ühestajamärgendiks
    if(p_mTul->sl==FSWSTR("Z")) // sõnaliik oli punktuatsioon
        {
        p_rec=punktuatsioon.Get((FSWCHAR*)(const FSWCHAR*)*p_sona);
        if(p_rec!= NULL)        // oli meie punktuatsiooni loendis
            {            
            //p_mTul->mrg1st=p_rec->p_yhTag;
			yhmarg1=p_rec->p_yhTag;
            return;
            }
        // p_rec==NULL -- polnud loendis...
		else // vt kas esimene m�rk oli loendis 
			{
			FSXSTRING algustht = p_sona->Left(1);
			p_rec=punktuatsioon.Get((FSWCHAR*)(const FSWCHAR*)algustht);
			if(p_rec!= NULL)        // oli meie punktuatsiooni loendis
				{            
				//p_mTul->mrg1st=p_rec->p_yhTag;
				yhmarg1=p_rec->p_yhTag;
				return;
				}
			}
        // p_rec==NULL -- polnud loendis...
        //p_mTul->mrg1st=FSWSTR("WIE");   //...vaikimisi see
        //p_mTul->mrg1st=FSWSTR("X");   //...vaikimisi see
		yhmarg1=FSWSTR("X");   //...vaikimisi see
        return;
        }
    // sõna --> ühestajamärgendiks

    // if(sonaliik != "H")
    if(p_mTul->sl[0]!=(FSWCHAR)'H')
    {
        p_rec=sona.Get((FSWCHAR*)(const FSWCHAR*)*p_sona);
        if(p_rec!= NULL)    // oli meie sõnade loendis
            {
            //p_mTul->mrg1st=p_rec->p_yhTag;
            yhmarg1=p_rec->p_yhTag;
            return;
            }
    }
    // endif

    // sõnaliik + sõna --> ühestajamärgendiks
    // DXIG -> RR RR II ASG t��tlus
    if(muut1.Find(p_mTul->sl[0]) >= 0) // sõnaliik oli 'muut1' loendis
        {
        p_rec=rr.Get((FSWCHAR*)(const FSWCHAR*)*p_sona);
        if(p_rec!= NULL)    // 
            {            
            //p_mTul->mrg1st=p_rec->p_yhTag;
			yhmarg1=p_rec->p_yhTag;
            return;
            }
        // p_rec==NULL -- polnud loendis...
		if((p_rec=noomTags.Get((FSWCHAR*)(const FSWCHAR*)(p_mTul->sl)))!=NULL)
			{                              // märgendi 1. pool
			//p_mTul->mrg1st=p_rec->p_yhTag; // tuleneb sõnaliigist
			yhmarg1=p_rec->p_yhTag;
			return;
			}

		//p_mTul->mrg1st=FSWSTR("RR");    //...vaikimisi see VALE!!!!
        // return;
        }
    // sõnaliik + sõnalõpp --> ühestajamärgendiks
    // nud-tud-dud lõpulised V, A -> VMAZ (partitsiip)
    if(verb_v_adj.Find(p_mTul->sl[0]) >= 0) // sõnaliik oli 'verb_v_adj' loendis
        {
        // kas sõna "[ntd]ud" lõpuline
        if(TaheHulgad::OnLopus(p_sona, FSWSTR("nud"))==true ||
           TaheHulgad::OnLopus(p_sona, FSWSTR("tud"))==true ||
           TaheHulgad::OnLopus(p_sona, FSWSTR("dud"))==true )
            {
            //p_mTul->mrg1st=FSWSTR("VMAZ");
			yhmarg1=FSWSTR("VMAZ");
            return; //??
            }
        //return; //??
        }
    // sõnaliik + sõnalõpp --> ühestajamärgendiks
    // nud-tud lõpulised S -> VMAZ (partitsiip)
    //   if(p_mTul->sl[0] == (FSWCHAR)'S') 
    //       {
    //       // kas sõna "[nt]ud" lõpuline
    //      if(TaheHulgad::OnLopus(p_sona, FSWSTR("nud"))==true ||
    //          TaheHulgad::OnLopus(p_sona, FSWSTR("tud"))==true )
    //          {
    //          p_mTul->mrg1st=FSWSTR("VMAZ");
    //          return; //??
    //          }
    //      // return; //??
    //      }
    // yks ja teine -> YKS* ja TEINE*
    if(yks_v_teine_sonaliik.Find(p_mTul->sl[0]) >= 0) // sõnaliik oli 'yks_v_teine_sonaliik' loendis
        {
        //p_rec=yksTeine.Get((FSWCHAR*)(const FSWCHAR*)*p_sona);
        p_rec=yksTeine.Get((FSWCHAR*)(const FSWCHAR*)p_mTul->tyvi);
        if(p_rec!= NULL)        // oli  loendis
            {                               // märgendi 1. pool
            //p_mTul->mrg1st=p_rec->p_yhTag;  // tuleneb sõnast
			yhmarg1=p_rec->p_yhTag;
            p_yTag=Kaane(&(p_mTul->vormid));
            if(p_yTag==NULL) // seda ei tohiks olla
                {
                //p_mTul->mrg1st=FSWSTR("PSX"); // TUNDMATU_P_YM
				yhmarg1=FSWSTR("PSX"); // TUNDMATU_P_YM
                return;
                }
            //p_mTul->mrg1st +=p_yTag;        // märgendi 2. pool,
			yhmarg1 += p_yTag;        // märgendi 2. pool,
            return;                         // tuleneb käändevormist
            }
        // p_rec==NULL -- polnud loendis, ei tee midagi
        }
    //  P -> PP1 PP2 PP3 juhtumi tõõtlus
    if(p_mTul->sl[0] == (FSWCHAR)'P')
        {
        //p_rec=ase.Get((FSWCHAR*)(const FSWCHAR*)*p_sona);
		p_rec=ase.Get((FSWCHAR*)(const FSWCHAR*)p_mTul->tyvi);
        if(p_rec!= NULL)     
            {                               // märgendi 1. pool
            //p_mTul->mrg1st=p_rec->p_yhTag;  // tuleneb sõnast
            yhmarg1=p_rec->p_yhTag;
			p_yTag=Kaane(&(p_mTul->vormid));
            if(p_yTag==NULL) // seda ei tohiks olla
                {
                //p_mTul->mrg1st=FSWSTR("PSX"); // TUNDMATU_P_YM
				yhmarg1=FSWSTR("PSX"); // TUNDMATU_P_YM
                return;                       
                }                           // märgendi 2. pool,
            //p_mTul->mrg1st +=  p_yTag;      // tuleneb käädevormist
			yhmarg1 +=  p_yTag;      // tuleneb käädevormist
            if(*p_sona == FSWSTR("tema") && yhmarg1==FSWSTR("PP3SG")) // väga kole!!!
                {
                // mõhh???
                //p_mTul->mrg1st=FSWSTR("M");
				//yhmarg1=FSWSTR("PP3SN"); HJK 23.11.2004 prooviks ikka ühestada...
                return;
                }
            return;
            }
        // p_rec==NULL -- polnud loendis, ei tee midagi
        }
    // ACUSHNOPY -> A, A, A, NC, NP, MC, MO, P, Y töötlus
    if((p_rec=noomTags.Get((FSWCHAR*)(const FSWCHAR*)(p_mTul->sl)))!=NULL)
        {                              // märgendi 1. pool
        //p_mTul->mrg1st=p_rec->p_yhTag; // tuleneb sõnaliigist
		yhmarg1=p_rec->p_yhTag; // tuleneb sõnaliigist
        p_yTag=Kaane(&(p_mTul->vormid));
        if(p_yTag==NULL)
            {
            if(p_mTul->sl==FSWSTR("A"))
                {
                //
                MRF2YH_LOEND* p_rec2;
                if((p_rec2=asxrr.Get((FSWCHAR*)(const FSWCHAR*)
                                                (p_mTul->sl)))!=NULL)
                    {
                    //p_mTul->mrg1st=p_rec2->p_yhTag; // ASXRR asemele
					yhmarg1=p_rec2->p_yhTag; // ASXRR asemele
                    return;
                    }
                //p_mTul->mrg1st += FSWSTR("SX"); // MUUTUMATU_NOOMENI_TUNNUS
				yhmarg1 += FSWSTR("SX"); // MUUTUMATU_NOOMENI_TUNNUS
                return;                         // sappa juurde
                }
            if(TaheHulgad::OnLopus(&yhmarg1, FSWSTR("NP"))==true)
                {
                // et ei tekiks NPSX keerame ...NP --> ...NC
                //p_mTul->mrg1st.Delete(p_mTul->mrg1st.GetLength()-1);
                if(p_mTul->mrg1st.GetLength()>0) //TV071109
				    yhmarg1.Delete(p_mTul->mrg1st.GetLength()-1);
                //p_mTul->mrg1st += FSWSTR("C");
				yhmarg1 += FSWSTR("C");
                }
            //p_mTul->mrg1st += FSWSTR("SX"); // MUUTUMATU_NOOMENI_TUNNUS
			yhmarg1 += FSWSTR("SX"); // MUUTUMATU_NOOMENI_TUNNUS
            return;                         // sappa juurde
            }
        //p_mTul->mrg1st += p_yTag; // märgendi 2. pool
		yhmarg1 += p_yTag; // märgendi 2. pool
        return;                   // tulenb käändevormist        
        }
    // J -> CS ja CC töötlus
    if(p_mTul->sl[0] == (FSWCHAR)'J')
        {
        p_rec=sidec.Get((FSWCHAR*)(const FSWCHAR*)*p_sona);
        if(p_rec!= NULL)     
            {                               
            //p_mTul->mrg1st=p_rec->p_yhTag;  
			yhmarg1=p_rec->p_yhTag; 
            return;
            }
        //p_mTul->mrg1st=FSWSTR("CS");
		yhmarg1=FSWSTR("CS");
        return;
        }
    // K -> SP ja ST töötlus
    if(p_mTul->sl[0] == (FSWCHAR)'K')
        {
        // TODO::
        Kaas2Yh(p_sona, yhmarg1, yhmarg2);
        //       if(p_yTag==NULL) // seda ei tohiks olla
        //           {
        //           p_mTul->mrg1st=FSWSTR("ST");
        //           return;
        //           }
        //p_mTul->mrg1st=p_yTag;
        return;
        }
    // V -> VM töötlus
    if(p_mTul->sl[0] == (FSWCHAR)'V')
        {
        //p_mTul->mrg1st=FSWSTR("VM"); // VERBI_YM
		yhmarg1=FSWSTR("VM"); // VERBI_YM
        p_yTag=Poore(&(p_mTul->vormid));
        if(p_yTag==NULL)
            {
            //p_mTul->mrg1st += FSWSTR("S"); // MUUTUMATU_VERBI_TUNNUS
			yhmarg1 += FSWSTR("S"); // MUUTUMATU_VERBI_TUNNUS
            return;
            }
        if(sid_variandid==p_yTag)
            {
            // siin toimub veel midagi segast
            //p_mTul->mrg1st += FSWSTR("3"); // YM_MA_VAHE
			yhmarg2 = yhmarg1;
			yhmarg1 += FSWSTR("2"); // YM_MA_VAHE
			yhmarg2 += FSWSTR("3"); // YM_MA_VAHE
            return;
            }
        //p_mTul->mrg1st += p_yTag;
		yhmarg1 += p_yTag;
        return;
        }
    assert(false);
    //p_mTul->mrg1st=FSWSTR("X"); // TUNDMATU_LOOM
	yhmarg1=FSWSTR("X"); // TUNDMATU_LOOM
    }

const FSWCHAR* MRF2YH2MRF::Kaane( // välja ühestajamärgend
    const FSXSTRING* p_vorm) const
    {
    MRF2YH_LOEND* p_rec;
    FSXSTRING vorm = *p_vorm;
    vorm.TrimRight(FSWSTR(", "));

    int nihe=0;
    if(TaheHulgad::OnAlguses(&vorm, FSWSTR("sg "))==true ||
                    TaheHulgad::OnAlguses(&vorm, FSWSTR("pl "))==true)
        {
        nihe += 3;
        }
    if(vorm[nihe]==(FSWCHAR)0 || vorm[nihe]==(FSWCHAR)'?')
        {
        return NULL; //TUNDMATU_P_YM
        }
    p_rec=kaanded.Get((FSWCHAR*)(const FSWCHAR*)vorm+nihe); // tabelist mrf2yhKaands
    if(p_rec!=NULL) // igaks juhuks; peaks alati olema tõene
        {
        return p_rec->p_yhTag;
        }
    return NULL; //TUNDMATU_P_YM
    }

const FSWCHAR* MRF2YH2MRF::Poore( // välja ühestajamärgend
    const FSXSTRING* p_vorm) const
    {
    MRF2YH_LOEND* p_rec;
    FSXSTRING vorm = *p_vorm;
    vorm.TrimRight(FSWSTR(", "));

    if(vorm[0]==(FSWCHAR)0 || vorm[0]==(FSWCHAR)'?')
        {
        return NULL;
        }
    p_rec=poorded.Get((FSWCHAR*)(const FSWCHAR*)vorm);
    if(p_rec!=NULL)
        {
        return p_rec->p_yhTag;
        }
    return NULL;
    }

// välja ühestajamärgendid (1 kuni 2); kaassõna võib olla nii ees- kui tagasõna
void MRF2YH2MRF::Kaas2Yh( 
    const FSXSTRING* p_sona,
    FSXSTRING& p_lisa1,
    FSXSTRING& p_lisa2) const
    {
    MRF2YH_LOEND*  p_rec;
    MRF2YH_LOEND2* p_rec2;
    FSXSTRING tmp;

    p_rec2=eesJaTaga.Get((FSWCHAR*)(const FSWCHAR*)*p_sona);
    if(p_rec2)
        { 
        // 
        p_lisa1 =p_rec2->p_Tag1;
        //
        p_lisa2 =p_rec2->p_Tag2;
		return;
        }
    p_rec=eesVoiTaga.Get((FSWCHAR*)(const FSWCHAR*)*p_sona);
    if(p_rec)
		{
		p_lisa1 = p_rec->p_yhTag;
        return;
		}
	if (p_sona->GetLength() > 5)
		{
		if (TaheHulgad::OnLopus(p_sona, FSWSTR("poole")) || 
			TaheHulgad::OnLopus(p_sona, FSWSTR("pool")) ||
			TaheHulgad::OnLopus(p_sona, FSWSTR("poolt")))
			{
			p_lisa1 = FSWSTR("SP");
			return;
			}
		}
    // tavaliselt on tagasõna
	p_lisa1 = FSWSTR("ST");
    return;
    }

