#if !defined(MRFLAGS_H)
#define MRFLAGS_H

#include <string.h>

#if defined( __GNUC__ )
#include <sys/param.h>
#define _MAX_PATH MAXPATHLEN
#endif

/** Ütleb millisest moodulist (morf analüüsi/sünteesi) tulemus pärineb */
enum EMRFKUST
{
    /** (morf analüüsi/sünteesi) tulemus pärineb määratlemata moodulist */
    eMRF_XX,
    /** (morf analüüsi/sünteesi) tulemus pärineb analüüsimooduli põhisõnastikust */
    eMRF_AP,

    /** (morf analüüsi/sünteesi) tulemus pärineb analüüsimooduli lisasõnastikust */
    eMRF_AL,

    /** (morf analüüsi/sünteesi) tulemus pärineb analüüsimooduli oletajast */
    eMRF_AO,

    /** (morf analüüsi/sünteesi) tulemus pärineb sünteesimooduli põhisõnastikust */
    eMRF_SP,

    /** (morf analüüsi/sünteesi) tulemus pärineb sünteesimooduli  oletajast */
    eMRF_SO,

    /** tulemus on XML märgendit sisaldav string (MRFTULEMUSED_TMPL::s6na) */
    eTAG_XX,
};

/** Sõnastiku tüüp */
enum XFI_TYPE
{
    /** morf anal/sünteesi sõnastik */
    XFI_SPL,
    /** tesauruse sõnastik  */
    XFI_THS
};

class FSXSTRING;
#define FSCHAR_UNICODE

#if defined( FSCHAR_UNICODE ) // kasutame 16 bitist little endian UNICODE kooditabelit
#define FSxCHAR FSWCHAR
#define dctsizeofFSxCHAR 2
#define FSxSTR(str) FSWSTR(str)
#define CFSbaseSTRING  CFSWString
#define FSxSTRCMP(s1, s2) FSStrCmpW0(s1, s2)
#define FSxSTRCPY(s1, s1Len, s2) PFSStrCpy(s1, s1Len, s2)
#define FSxSTRCAT(s1, s2) FSStrCat(s1, s2)
#define FSxSTRLEN(s)      FSStrLen(s)
#else
#error Defineeri FSCHAR_UNICODE
#endif

//-----------------------------------------------------------------------------

/** Morf analüüsi/sünteesi väljundahela lüli lipud */
typedef enum
{
    //---tüübi järgi-----------------------------------------------------------
    /** 1.1 Tüübi järgi: lülis on täisarv */
    PRMS_SARV = (0x00000001),

    /** 1.2 Tüübi järgi: lülis on stringiklass @a (unicode või @a utf8) */
    PRMS_STRKLASS = (0x00000002),

    /** 1.4 Lülis on stringiklass @a (unicode või @a utf8) ja numbriline ID*/
    PRMS_STRID = (0x00000004),

    /** 1.8 Tüübi järgi: lülis on morf analüüsi tulemus @a (unicode või @a utf8) */
    PRMS_MRF = (0x00000008),

    //---tüübi ja sisu järgi---------------------------------------------------
    /** 2.1 Tüübi ja sisu järgi: lülis on morfitav|sünteesitav sõna vms */
    PRMS_SONA = (0x00000010 | PRMS_STRKLASS),

    /** 2.2 Tüübi ja sisu järgi: lülis on lausetajast sõne ja sõne-id */
    PRMS_SONAJAID = (0x00000020 | PRMS_STRID),

    /** 3.1 Sisu järgi: lülis on TAG */
    PRMS_TAG = (0x00000100),

    /** 3.2 Tüübi ja sisu järgi: lülis stringiklassi kujul TAG (va lõigu- ja lausemärgendid @a (unicode või @a utf8)
     * 
     * Siia hulka kuuluvad ka @a ignoreeeri märgendi sees olevad sõnad
     */
    PRMS_TAGSTR = (0x00000200 | PRMS_STRKLASS | PRMS_TAG),

    /** 3.4 Tüübi ja sisu järgi: lülis sõne algus/lõpupositsioon */
    PRMS_TAGSINT = (0x0000400 | PRMS_SARV | PRMS_TAG),

    /** 4.1 Tüübi ja sisu järgi: lülis stringiklassi kujul TAG lause algus @a (unicode või @a utf8) */
    PRMS_TAGBOS = (0x00001000 | PRMS_STRKLASS | PRMS_TAG),

    /** 4.2 Tüübi ja sisu järgi: lülis stringiklassi kujul TAG lause lõpp @a (unicode või @a utf8) */
    PRMS_TAGEOS  = (0x00002000 | PRMS_STRKLASS | PRMS_TAG),
        
    /** x.x Tüübi ja sisu järgi: lülis stringiklassi kujul TAG... */        
    PRMS_TAGBOP  = (0x00004000 | PRMS_STRKLASS | PRMS_TAG),
    PRMS_TAGEOP  = (0x00008000 | PRMS_STRKLASS | PRMS_TAG),        
    PRMS_TAGEOF  = (0x00010000 | PRMS_STRKLASS | PRMS_TAG),        
    PRMS_TAGPSEP = (0x00020000 | PRMS_STRKLASS | PRMS_TAG),
            
    /** 4.4 Tüübi ja sisu järgi: lülis lõigualgusTAG STRIDina @a (unicode või @a utf8) */
    PRMS_STRIDBOP = (0x00004000 | PRMS_STRID | PRMS_TAG),

    /** 4.8 Tüübi ja sisu järgi: lülis lõigulõpuTAG STRIDina @a (unicode või @a utf8)*/
    PRMS_STRIDEOP = (0x00008000 | PRMS_STRID | PRMS_TAG),

    /** 5.1 Tüübi ja sisu järgi: lülis stringiklassi kujul TAG faililõpp */
    PRMS_STRIDEOF = (0x00010000 | PRMS_STRID | PRMS_TAG),

    /** 5.2 Tüübi ja sisu järgi: lülis lõiguvaheTAG STRIDina */
    PRMS_STRIDPSEP = (0x00020000 | PRMS_STRID | PRMS_TAG),

    /** 5.4 Tüübi ja sisu järgi: lülis sõnavaheTAG STRIDina */
    PRMS_STRIDWSEP = (0x00040000 | PRMS_STRID | PRMS_TAG),
        
    /** 5.1 Lausevahetähis ühestajale
     *
     * Kleebime lause esimese sõna külge.
     * Seda kasutab ühestaja, kui on vaja lisada lause algusesse pärisnimeanalüüs
     * (lipp @a MF_LISAPNANAL). Vt funktsiooni @a bool @a AHEL2::SonaAlustabLauset()
     */
    PRMS_JUSTKUI_LAUSE_ALGUS = (0x00010000),

} LYLI_FLAGS;

/** Andmetüüp (sisend/väljund)ahela lüli käiva lipukombinatsiooni hoidmiseks
 *
 * Sisaldab kombinatsiooni loendiga ::LYLI_FLAGS määratud lippudest.
 */
typedef int LYLI_FLAGS_BASE_TYPE;

/** Tüüp morfimist tüüriva lipukombinatsiooni hoidmiseks */
typedef long long MRF_FLAGS_BASE_TYPE;

/** 00.1 \a +a algvorm väljundisse */
const MRF_FLAGS_BASE_TYPE MF_ALGV = 0x0000000000000001LL;
/** 00.2 \a +b väljundisse ainult lemmad */
const MRF_FLAGS_BASE_TYPE MF_LEMMA = 0x0000000000000002LL;
/** 00.4 \a +c kinni kahekohalise lipu all */
const MRF_FLAGS_BASE_TYPE MF_kinni004 = 0x0000000000000004LL;
/** 00.8 \a +d MF_LUBAMITMIKUO lubas mitmesõnaliste liitsõnade osasõnu eraldi kasutada; tegelikult alates 04.2015 seda kuskil ei kasutata */
const MRF_FLAGS_BASE_TYPE MF_vaba008 = 0x0000000000000008LL;
/** 01.1 \a +e lipukombinatsioon failinime laiendiks */
const MRF_FLAGS_BASE_TYPE MF_LIPUD2EXT = 0x0000000000000010LL;
/** 01.2 \a +f lubab mõnede tesauruses olevate sõnade nagu \a aukudega analüüsi iseseisvate lemmadena */
const MRF_FLAGS_BASE_TYPE MF_LUBATESA = 0x0000000000000020LL;
/** 01.4 \a +g süntees */
const MRF_FLAGS_BASE_TYPE MF_GENE = 0x0000000000000040LL;
/** 01.8 kinni help-lipu all */
const MRF_FLAGS_BASE_TYPE MF_kinni018 = 0x0000000000000080LL;
/** 02.1 \a +i liiga pikad sõnad loetakse valedeks */
const MRF_FLAGS_BASE_TYPE MF_PIKADVALED = 0x0000000000000100LL;
/** 02.2 \a +j lisa automaatselt pärisnimeanalüüsid */
const MRF_FLAGS_BASE_TYPE MF_LISAPNANAL = 0x0000000000000200LL;
/** 02.4 \a +k lisa häälduseks vajalikud märgid */
const MRF_FLAGS_BASE_TYPE MF_KR6NKSA = 0x0000000000000400LL;
/** 02.8 \a +l range lühendikontroll, muidu liberaalne */
const MRF_FLAGS_BASE_TYPE MF_LYHREZH = 0x0000000000000800LL;
/** 03.1 \a -m analüüs (mitte süntees)  */
const MRF_FLAGS_BASE_TYPE MF_MRF = 0x0000000000001000LL;
/** 03.2 \a +n range nimekontroll, muidu liberaalne */
const MRF_FLAGS_BASE_TYPE MF_NIMEREZH = 0x0000000000002000LL;
/** 03.4 \a +o pakub oletusi nende stringide kohta, mida sõnastikus pole */
const MRF_FLAGS_BASE_TYPE MF_OLETA = 0x0000000000004000LL;
/** 03.8 \a +p eristab liitsõnakomponente */
const MRF_FLAGS_BASE_TYPE MF_POOLITA = 0x0000000000008000LL;
/** 04.1 \a +q tulemus-struktuuri ühestajamärgendid lisaks */
const MRF_FLAGS_BASE_TYPE MF_YHMRG = 0x0000000000010000LL;
/** 04.2 \a +r kinni kahekohalise lipu all */
const MRF_FLAGS_BASE_TYPE MF_kinni042 = 0x0000000000020000LL;
/** 04.4 \a +s piirdub esimese sobiva anlüüsiga */
const MRF_FLAGS_BASE_TYPE MF_SPELL = 0x0000000000040000LL;
/** 04.8 \a +t ei luba tabusõnade nagu \a perse analüüsi */
const MRF_FLAGS_BASE_TYPE MF_EILUBATABU = 0x0000000000080000LL;
/** 05.1 \a +u ei tuleta liitsõnu; ainult need, mis sõnastikus (ka liitsõnad) */
const MRF_FLAGS_BASE_TYPE MF_EITULETALIIT = 0x0000000000100000LL;
/** 05.2 \a +v võta Sri Lanka kokku */
const MRF_FLAGS_BASE_TYPE MF_V0TAKOKKU = 0x0000000000200000LL;
/** 05.4 \a +w keelab rooma numbrite analüüsi */
const MRF_FLAGS_BASE_TYPE MF_ARAROOMA = 0x0000000000400000LL;
/**  05.8 \a +x loeb e-maili ja veebiaadresside sarnased stringid õigeteks (sõnaliigiks "Y" e. lühend) */
const MRF_FLAGS_BASE_TYPE MF_VEEBIAADRESS = 0x0000000000800000LL;
/** 06.1 \a +y ühesta analüüsid, eeldab lõigu-lausemärgendeid */
const MRF_FLAGS_BASE_TYPE MF_YHESTA = 0x0000000001000000LL;
/** 06.2 \a +z VABA */
const MRF_FLAGS_BASE_TYPE MF_vaba62 = 0x0000000002000000LL;
/** 06.4 \a +0 lisa väljundisse positsioonimärgendid */
const MRF_FLAGS_BASE_TYPE MF_INTPOS = 0x0000000004000000LL;
/** 06.8 \a +1 tulemus-string 1le reale kokku */
const MRF_FLAGS_BASE_TYPE MF_YHELE_REALE = 0x0000000008000000LL;
/** 07.1 \a +2 SGML-olemitega sisendi korral luba ampersandi väljaspool olemeid */
const MRF_FLAGS_BASE_TYPE MF_IGNORAMP = 0x0000000010000000LL;
/** 07.2 \a +3 Jäta morfimata/sünteesimata @a \<ignoreeri\> ja @a \</ignoreeri\> vahel olev tekst */
const MRF_FLAGS_BASE_TYPE MF_IGNOREBLK = 0x0000000020000000LL;
/** 07.4 \a +4 Jäta morfimata/sünteesimata sisend kujul <...> */
const MRF_FLAGS_BASE_TYPE MF_IGNORETAG = 0x0000000040000000LL;
/** 07.8 \a +5 UTF8/2baidiseUNICODE korral ByteOrderMark'i käsitlus */
const MRF_FLAGS_BASE_TYPE MF_BOM = 0x0000000080000000LL;
/** 08.1 \a +6 SGML olemites luba &#number; tüüpi asju */
const MRF_FLAGS_BASE_TYPE MF_AUTOSGML = 0x0000000100000000LL;
/** 08.2 \a +7 XML vormingus tekst sisse-välja */
const MRF_FLAGS_BASE_TYPE MF_XML = 0x0000000200000000LL;
/** 08.4 \a +8 sisendtekstis lõik real */
const MRF_FLAGS_BASE_TYPE MF_LOIKREAL = 0x0000000400000000LL;
/** 08.8 \a +9 Lausesta sisendtekst */
const MRF_FLAGS_BASE_TYPE MF_LAUSESTA = 0x0000000800000000LL;
/** 09.1 \a +, tulemus-struktuuris tõsta komage eraldet asjad lahku */
const MRF_FLAGS_BASE_TYPE MF_KOMA_LAHKU = 0x0000001000000000LL;
/** 09.2 \a -% VABA */
const MRF_FLAGS_BASE_TYPE MF_vaba092 = 0x0000002000000000LL;
/** 09.4       VABA */
const MRF_FLAGS_BASE_TYPE MF_vaba094 = 0x0000004000000000LL;
/** 09.8       VABA */
const MRF_FLAGS_BASE_TYPE MF_vaba098 = 0x0000008000000000LL;
/** 10.1 ühestajas ei kasuta mitmesusklasse */
const MRF_FLAGS_BASE_TYPE T3_MK_KASUTU = 0x0000010000000000LL;
/** 10.2 ühestajas ei kasuta leksikonist saadud tõenõosusi */
const MRF_FLAGS_BASE_TYPE T3_LEXPKASUTU = 0x0000020000000000LL;
/** 10.4 ühestaja andmefaili tegemisel lisame leksikoni morfist märgendeid */
const MRF_FLAGS_BASE_TYPE T3_LISA_LMM = 0x0000040000000000LL;
/** 10.8 et3.dct'i tegemisel iga mitteühesusklassi sees mitteühesuste summa==100%,
 *       ühestajas arvestame kõigupealt tehtud mitteühesusklassis märgendite
 *       abs esinemisarvu */
const MRF_FLAGS_BASE_TYPE T3_MK_JAOTUSB = 0x0000080000000000LL;
/** 11.1 ühestaja tüürimiseks */
const MRF_FLAGS_BASE_TYPE T3_vaba111 = 0x0000100000000000LL;
/** 11.2 ühestaja tüürimiseks */
const MRF_FLAGS_BASE_TYPE T3_vaba112 = 0x0000200000000000LL;
//                                            6543210987654321
//======tüüpilised kombinatsioonid
/** \a -M bitikombinatsioon (-ilapm) standardseks
 *        morf analüüsiks ilma tundmatute sõnade oletamiseta */
const MRF_FLAGS_BASE_TYPE MF_DFLT_MORFA = MF_MRF | MF_ALGV | MF_POOLITA |
                                MF_PIKADVALED | MF_LYHREZH | MF_VEEBIAADRESS |
                                MF_YHELE_REALE | MF_V0TAKOKKU;
/** \a -O või \a -MO bitikombinatsioon (-oapm) standardseks
 *                morf analüüsiks koos tundmatute sõnade oletamisega */
const MRF_FLAGS_BASE_TYPE MF_DFLT_OLETA = MF_MRF | MF_ALGV | MF_POOLITA |
                    MF_OLETA | MF_VEEBIAADRESS | MF_YHELE_REALE | MF_V0TAKOKKU;

#if defined(ETANA)
/** \a -Y bitikombinatsioon standardseks morf analüüsiks hilisemaks ühestamiseks sobilikul moel */
const MRF_FLAGS_BASE_TYPE MF_DFLT_MORFY = MF_YHESTA | MF_DFLT_OLETA | 
                    MF_LISAPNANAL|MF_YHELE_REALE|MF_KOMA_LAHKU | MF_V0TAKOKKU;
#else
/** \a -Y bitikombinatsioon standardseks morfitud sisendi ühestamiseks */
const MRF_FLAGS_BASE_TYPE MF_DFLT_MORFY = MF_YHESTA | 
                                                MF_YHELE_REALE|MF_KOMA_LAHKU;
#endif
/** \a -G bitikombinatsioon standardseks sünteesiks mitte-tesaurusele */
const MRF_FLAGS_BASE_TYPE MF_DFLT_GEN = MF_GENE | MF_V0TAKOKKU;
/** \a -GO bitikombinatsioon standardseks sünteesiks mitte-tesaurusele koos oletamisega */
const MRF_FLAGS_BASE_TYPE MF_DFLT_GENOLE = MF_GENE | MF_OLETA | MF_V0TAKOKKU;
/** \a -GT bitikombinatsioon standardseks sünteesiks tesaurusele */
const MRF_FLAGS_BASE_TYPE MF_DFLT_GENTES = MF_GENE | MF_EITULETALIIT |
                                                        MF_LUBATESA | MF_V0TAKOKKU;
/** \a -L bitikombinatsioon standardseks lemmatiseerimiseks ilma tundmatute sõnade oletamiseta */
const MRF_FLAGS_BASE_TYPE MF_DFLT_LEM = MF_LEMMA | MF_DFLT_MORFA;
/** \a -LO bitikombinatsioon standardseks lemmatiseerimiseks koos tundmatute sõnade oletamisega */
const MRF_FLAGS_BASE_TYPE MF_DFLT_LEMOLE = MF_LEMMA | MF_DFLT_OLETA;
/** \a -Q bitikombinatsioon standardseks oletajata morf analüüsiks, lisab rõhu, välte jms märgid */
const MRF_FLAGS_BASE_TYPE MF_DFLT_KR6NKSA = MF_MRF | MF_PIKADVALED | 
        MF_POOLITA | MF_KR6NKSA | MF_LYHREZH | MF_VEEBIAADRESS | MF_V0TAKOKKU;
/** \a -QO bitikombinatsioon standardseks oletajaga morf analüüsiks, lisab rõhu, välte jms märgid */
const MRF_FLAGS_BASE_TYPE MF_DFLT_OLETAKS = MF_MRF | MF_PIKADVALED | 
        MF_POOLITA | MF_KR6NKSA | MF_OLETA | MF_VEEBIAADRESS | MF_V0TAKOKKU;

const MRF_FLAGS_BASE_TYPE MF_DFLT_SPL = MF_PIKADVALED | MF_SPELL | MF_NIMEREZH |
                        MF_LYHREZH | MF_POOLITA | MF_LUBATESA | MF_VEEBIAADRESS;
const MRF_FLAGS_BASE_TYPE MF_DFLT_HYP = MF_PIKADVALED | MF_SPELL | MF_NIMEREZH | 
                        MF_LYHREZH | MF_POOLITA | MF_LUBATESA ;
const MRF_FLAGS_BASE_TYPE MF_DFLT_SUG = MF_PIKADVALED | MF_SPELL | MF_NIMEREZH | 
            MF_LYHREZH | MF_POOLITA | MF_LUBATESA | MF_ARAROOMA | MF_EILUBATABU;

/** gene tesaurusele */
const MRF_FLAGS_BASE_TYPE MF_DFLT_THES = MF_PIKADVALED | MF_ALGV | MF_LEMMA;

/** morf analüüsi jaoks legaalsed bitid */
const MRF_FLAGS_BASE_TYPE MF_MRF_OKFLAGS =
    MF_MRF | MF_YHESTA | MF_OLETA | 
    MF_ALGV | MF_LEMMA | MF_LIPUD2EXT | MF_LUBATESA | 
    MF_PIKADVALED | MF_LISAPNANAL | MF_KR6NKSA | MF_LYHREZH | MF_NIMEREZH |
    MF_POOLITA | MF_YHMRG | MF_SPELL | MF_EILUBATABU | MF_EITULETALIIT | MF_ARAROOMA | MF_VEEBIAADRESS |
    MF_YHELE_REALE | MF_IGNORAMP | MF_IGNOREBLK | MF_IGNORETAG |
    MF_BOM | MF_AUTOSGML | MF_XML | MF_KOMA_LAHKU | MF_V0TAKOKKU;

// Sünteesiga korral kasutatakse käsurealt saadud lipukmbinatsiooni 
// morfanalüsaatori väljakutsumisel lippude põhjana, 
// millele lisatakse teatavaid lippe 
// ja millest eemaldatakse teatavaid lippe.
/** morf sünteesi jaoks legaalsed bitid */
const MRF_FLAGS_BASE_TYPE MF_GEN_OKFLAGS =
    MF_GENE | MF_OLETA | MF_KR6NKSA | MF_YHELE_REALE | 
    MF_ALGV | MF_LEMMA | MF_LIPUD2EXT | MF_LUBATESA | 
    MF_PIKADVALED | MF_LYHREZH | MF_NIMEREZH | 
    MF_POOLITA | MF_SPELL | MF_EILUBATABU | MF_EITULETALIIT | MF_ARAROOMA | MF_VEEBIAADRESS |
    MF_IGNORAMP | MF_IGNOREBLK | MF_IGNORETAG |
    MF_BOM | MF_AUTOSGML | MF_XML | MF_KOMA_LAHKU | MF_V0TAKOKKU;

/** t3-ühestaja jaoks legaalsed bitid */
const MRF_FLAGS_BASE_TYPE MF_YHS_OKFLAGS = MF_YHESTA | MF_YHELE_REALE | 
        MF_KOMA_LAHKU | MF_IGNOREBLK | MF_XML | T3_MK_KASUTU | T3_LEXPKASUTU;

const MRF_FLAGS_BASE_TYPE LYHVALIK = MF_YHELE_REALE|MF_IGNOREBLK|MF_XML;


/** Klass morf analüsaatori ja süntesaatori lippude käitlemiseks */
class MRF_FLAGS
{
public:

    MRF_FLAGS(void)
    {
        InitClassVariables();
    }

    /**
     * @param[in] flagid
     * Viit muutujale, milles hoitakse kombinatsiooni
     * loendiga ::MORF_FLAGS määratletud lippudest
     *
     * @attention õiendab välise lipuga
     */
    MRF_FLAGS(MRF_FLAGS_BASE_TYPE *flagid)
    {
        InitClassVariables();
        Start(flagid);
    }

    /**
     * @param[in] flagid
     * Need lipud heisatakse.
     * Kombinatsioon loendiga ::MORF_FLAGS määratletud lippudest.
     * 
     * @attention õiendab lokaalse lipuga.
     */
    MRF_FLAGS(const MRF_FLAGS_BASE_TYPE flagid)
    {
        InitClassVariables();
        Start(flagid);
    }


    /**
     * @param flagid
     * Viit muutujale, milles hoitakse kombinatsiooni
     * loendiga ::MORF_FLAGS määratletud lippudest
     *
     * @attention õiendab välise lipuga
     */
    void Start(MRF_FLAGS_BASE_TYPE *flagid)
    {
        Stop();
        flags = flagid;
    }

    /**
     * @param[in] flagid
     * Need lipud heisatakse.
     * Kombinatsioon loendiga ::MORF_FLAGS määratletud lippudest.
     * 
     * @attention õiendab lokaalse lipuga.
     */
    void Start(const MRF_FLAGS_BASE_TYPE flagid)
    {
        Stop();
        localFlags = flagid;
    }

    /// .

    /** Uus lipukombinatsioon
     *
     * @param[in] flagid
     * Vanad lipud võetakse maha ja need lipud heisatakse.
     * Kombinatsioon loendiga ::MORF_FLAGS määratletud lippudest.
     */
    void Set(const MRF_FLAGS_BASE_TYPE flagid)
    {
        *flags = flagid;
    }

    /** Mis lipud heisatud
     * 
     * @param[in] mask
     * Tagastatakse ainult nende lippude seisund, mille kohal \a mask'i bitt
     * on üks. Vaikimisi kõik.
     * @return Vastav lipukombinatsioon
     */
    MRF_FLAGS_BASE_TYPE Get(const MRF_FLAGS_BASE_TYPE mask = ~0) const
    {
        return *flags & mask;
    }

    /// Viit lippe hoidvale muutujale.

    MRF_FLAGS_BASE_TYPE* GetPtr2Flags(void) const
    {
        return flags;
    }

    /** Lippude seadmiseks
     * 
     * @param[in] flag Kombinatsioon loendiga ::MORF_FLAGS määratletud lippudest
     * @param[in] on
     * <ul><li> \a ==0 Lipud võetakse maha
     *     <li> \a !=0 Lipud heisatakse lisaks olemasolevatele
     * </ul>
     */
    void OnOff(const MRF_FLAGS_BASE_TYPE flag, const int on)
    {
        if (on)
            On(flag);
        else
            Off(flag);
    }

    /// Heiskab lipu.

    /** Lisab lipud
     *
     * @param[in] flagid Need lipud heisatakse lisaks olemasolevatele.
     */
    void On(const MRF_FLAGS_BASE_TYPE flagid)
    {
        *flags |= flagid;
    }

    /** Lipp maha
     *
     * @param flagid Need lipud võetakse maha, ülejäänud jäävad endisesse seisu.
     */
    void Off(const MRF_FLAGS_BASE_TYPE flagid)
    {
        *flags &= ~flagid;
    }

    /** Kontrollib, kas lipud heisatud.
     *
     * @return @a 1 kui kõik argumendiga määratud lipud heisatud, muidu @a 0
     * @param[in] const MRF_FLAGS_BASE_TYPE @flagid
     * Nende lippude heisatust kontrollime.
     * Peab olema kombinatsioon loendiga ::MORF_FLAGS määratletud lippudest.
     */
    int Chk(const MRF_FLAGS_BASE_TYPE flagid) const
    {
        return (*flags & flagid) == flagid ? 1 : 0;
    }

    /** Kontrollib, kas lipud heisatud.
     *
     * @return @a true kui kõik argumendiga määratud lipud heisatud, muidu @a false.
     * @param[in] const MRF_FLAGS_BASE_TYPE @flagid
     * Nende lippude heisatust kontrollime.
     * Peab olema kombinatsioon loendiga ::MORF_FLAGS määratletud lippudest.
     */
    bool ChkB(const MRF_FLAGS_BASE_TYPE flagid) const
    {
        return (*flags & flagid) == flagid ? true : false;
    }


    /** Kontrollib, kas kasutatakse lokaalset lippu
     *
     * @return
     * <ul><li> @a ==true Kasutatakse klassisest lippu
     *     <li> @a ==false Klass kasutab väljaspoolt viida-abil etteantud lippu
     * </ul>
     */
    bool LippOnLokaalne(void) const
    {
        return flags == &localFlags ? true : false;
    }

    /** Copy-konstruktor
     *
     * @attention Kui argument @a mrfFlags kasutab välist lippu,
     * siis see klass hakkab kasutama viita samale välisele lipule.
     */
    MRF_FLAGS(const MRF_FLAGS& mrfFlags)
    {
        if (mrfFlags.LippOnLokaalne() == true)
            Start(mrfFlags.Get());
        else
            Start(mrfFlags.GetPtr2Flags());
    }

    /** Omistamisoperaator
     *
     * @attention Kui argument @a mrfFlags kasutab välist lippu,
     * siis see klass hakkab kasutama viita samale välisele lipule.
     */
    MRF_FLAGS & operator=(const MRF_FLAGS& mrfFlags)
    {
        if (this != &mrfFlags)
        {
            if (mrfFlags.LippOnLokaalne() == true)
                Start(mrfFlags.Get());
            else
                Start(mrfFlags.GetPtr2Flags());
        }
        return *this;
    }

    /** Taastab argumentideta konstruktori järgse seisu */
    void Stop()
    {
        InitClassVariables();
    }

private:

    void InitClassVariables(void)
    {
        localFlags = 0LL;
        flags = &localFlags;
    }

    MRF_FLAGS_BASE_TYPE *flags;
    MRF_FLAGS_BASE_TYPE localFlags;
};
#endif



