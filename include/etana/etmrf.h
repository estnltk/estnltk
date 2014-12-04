
#if !defined( ETMRFA_H )
#define ETMRFA_H

#include "mrf-mrf.h"

/** Klass morf analüsaatori kasutajasõnastiku käitlemiseks.
 *
 * Kasutajasõnastikku otsitakse keskonnamuutujas PATH loetletud kataloogidest.
 * Kataloogide loendit vaadatakse läbi vasakult paremale võetakse esimene
 * ettejuhtunud kasutajasõnastik. Igast kataloogist otsitakse kõikepealt
 * faili et.usr.dct (peab oleme Win Baltic kodeeringus), selle puudumisel faili
 * et.usr.dct.utf8 (peab olema UTF8 kodeeringus) ja selle puudumisel faili
 * et.usr.dct.uc (peab olema 2 baidises UNICODE kodeeringus). Kui vaatlusaluses
 * kataloogis ühtegi nimetatud abisõnastikufaili polnud vaadakse järgmisesse
 * loendis olevasse kataloogi. Kui ühestki PATHis loetletud kataloogidest
 * abisõnastikku ei leitud, aetakse ilma läbi.
 *
 * Abisõnastikus ridasid kujul "^[ ]*$" (white space-idest koosnev rida) ja
 * "^# [^ ].*$" (kommentaar) ignoreeritakse.
 * Ülejäänud read peavad olema samasugusel kujul, nagu on morf anaüsaatori
 * ührealine väljundkuju.
 * Kasutajasõnastik ei pea olema mingil moel järjestatud.
 * Korduvate märksõnade puhul pole määratud millist varainti kasutatakse.
 */
class MRFAUDCT : public TMPLPTRARRAYBIN<MRFTULEMUSED, FSXSTRING> // vt etmrfa.cpp
{
public:

    MRFAUDCT(void)
    {
        InitClassVariables();
        assert(EmptyClassInvariant()); // Siin peab see kehtima
    }

    /** Argumentidega konstruktor
     *
     * @param[in] dctFileName
     * Kasutajasõnastikku sisaldava faili (path)name.
     * See fail peab eksisteerima ja sisaldama korrektse formaadiga
     * abisõnastikku.
     * Abisõnastiku nimi määrab tema kodeeringu:
     * <ul><li> et.usr.dct (peab oleme Win Baltic kodeeringus)
     *     <li> et.usr.dct.utf8 (peab olema UTF8 kodeeringus)
     *     <li> et.usr.dct.uc (peab olema 2 baidises UNICODE kodeeringus)
     * </ul>
     *
     * Abisõnastikus ridasid kujul "^[ ]*$" (white space-idest koosnev rida) ja
     * "^# [^ ].*$" (kommentaar) ignoreeritakse.
     * Ülejäänud read peavad olema samasugusel kujul, nagu on morf anaüsaatori
     * ührealine väljundkuju.
     * Kasutajasõnastik ei pea olema mingil moel järjestatud.
     * Korduvate märksõnade puhul pole määratud millist varainti kasutatakse.
     */
    MRFAUDCT(const CFSFileName &dctFileName)
    {
        try
        {
            InitClassVariables();
            Start(dctFileName);
            assert(ClassInvariant());
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** Argumentidega konstruktor
     *
     * @param[in] dctFileName
     * Kasutajasõnastikku sisaldava faili (path)name.
     * See fail peab eksisteerima ja sisaldama korrektse formaadiga
     * abisõnastikku.
     * Abisõnastiku nimi määrab tema kodeeringu:
     * <ul><li> et.usr.dct (peab oleme Win Baltic kodeeringus)
     *     <li> et.usr.dct.utf8 (peab olema UTF8 kodeeringus)
     *     <li> et.usr.dct.uc (peab olema 2 baidises UNICODE kodeeringus)
     * </ul>
     *
     * Abisõnastikus ridasid kujul "^[ ]*$" (white space-idest koosnev rida) ja
     * "^# [^ ].*$" (kommentaar) ignoreeritakse.
     * Ülejäänud read peavad olema samasugusel kujul, nagu on morf anaüsaatori
     * ührealine väljundkuju.
     * Kasutajasõnastik ei pea olema mingil moel järjestatud.
     * Korduvate märksõnade puhul pole määratud millist varianti kasutatakse.
     */
    void Start(const CFSFileName &dctFileName);

    /** Viib klassi argumentide konstrukori järgsesse seisu */
    void Stop(void)
    {
        /// Vabastab klassi poolt töö käigus või konstruktoris reserveeritud mälu
        if (TMPLPTRARRAYBIN<MRFTULEMUSED, FSXSTRING>::EmptyClassInvariant() == false)
        {
            TMPLPTRARRAYBIN<MRFTULEMUSED, FSXSTRING>::Stop();
        }
        InitClassVariables();
        assert(EmptyClassInvariant()); // Siinkohal peab see kehtima
    }

    bool EmptyClassInvariant(void)
    {
        return TMPLPTRARRAYBIN<MRFTULEMUSED, FSXSTRING>::EmptyClassInvariant();
    }

    bool ClassInvariant(void)
    {
        return TMPLPTRARRAYBIN<MRFTULEMUSED, FSXSTRING>::ClassInvariant();
    }

    /** Kontrollib, kas sõna oli kasutajasõnastikus.
     *
     * @return @a true Kui sisendsõna oli kasutajasõnastikus, muidu @a false
     *
     * @param[in] const FSXSTRING* @sisse
     * Sisendsõna (võib sisaldada märgendeid ja olemeid)
     * @param[in] const FSXSTRING* @sissePuhastatud
     * Kasutajasõnastikust otsitav sõna. Märgendid jms vajadusel eelnevalt eemaldatud.
     * @param[out] MRFTULEMUSED* @pMorfAnal
     * Analüüs, kui otsitav sõna oli kasutajasõnestikus
     */
    bool chkmin(const FSXSTRING* sisse, const FSXSTRING* sissePuhastatud,
                MRFTULEMUSED* pMorfAnal);

private:

    void InitClassVariables(void)
    {
    }

    /** Illegaalne */
    MRFAUDCT(const MRFAUDCT&)
    {
        assert(false);
    }

    /** Illegaalne */
    MRFAUDCT & operator=(const MRFAUDCT&)
    {
        assert(false);
        return *this;
    }
};

/** Klass morf analüüsi tegemiseks
 * 
 * Kui tahta väljundit kasutada hiljem morf analüüsi sisendina, tuleb
 * <ul><li> Kasutada <b>MF_YHESTA</b> lipppu
 *     <li> Sisendisse lisada lause algus- ja lõpumärgendid
 *     <li> Väljapool märgendatud lauset, kasutada ainult <b>TAG</b>isid
 * <ul>  
 * 
 * Lipp <b>MF_YHESTA</b> ei ühesta väljundit, kuid lisab sinna infot, 
 * mida ühestaja vajab.
 */
class ETMRFA : public MORF0, public MRF2YH2MRF, protected MRFAUDCT
{
public:

    ETMRFA(void)
    {
        try
        {
            InitClassVariables();
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** Argumentidega konstruktor
     *
     * Otsib üles vajalikud andmefailid ja initsialiseerib
     * morf analüsaatori
     * @param[in] path Semikooloniga (Windowsis) või kooloniga (Linux)
     * eraldatud kataloogide loend. Sealt otsitakse andmefaile.
     * @param[in] flags Lipud
     */
    ETMRFA(const CFSString &path, const MRF_FLAGS_BASE_TYPE flags)
    {
        try
        {
            InitClassVariables();
            Start(path, flags);
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** Argumentidega konstruktor
     *
     * Avab vajalikud andmefailid ja initsialiseerib
     * morf analüsaatori
     * @param[in] flags Lipud
     * @param[in] dctMain Põhisõnastik
     * @param[in] dctUser Kasutajasõnastik (kui "", siis pole kasutusel)
     */
    ETMRFA(const MRF_FLAGS_BASE_TYPE flags,
           const CFSFileName& dctMain, const CFSFileName& dctUser)
    {
        try
        {
            InitClassVariables();
            Start(flags, dctMain, dctUser);
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** Argumentideta konstruktori järgseks initsialiseerimiseks
     *
     * Otsib üles vajalikud andmefailid ja initsialiseerib
     * morf analüsaatori
     * @param[in] path Semikooloniga (Windowsis) või kooloniga (Linux)
     * eraldatud kataloogide loend. Sealt otsitakse andmefaile.
     * @param[in] flags Lipud
     */
    void Start(const CFSString &path, const MRF_FLAGS_BASE_TYPE flags);

    /** Argumentideta konstruktori järgseks initsialiseerimiseks
     *
     * Avab vajalikud andmefailid ja initsialiseerib
     * morf analüsaatori
     * @param[in] flags Lipud
     * @param[in] dctMain Põhisõnastik
     * @param[in] dctUser Kasutajasõnastik (kui "", siis pole kasutusel)
     */
    void Start(const MRF_FLAGS_BASE_TYPE flags,
               const CFSFileName& dctMain, const CFSFileName& dctUser);

    /** Määrab morf analüüsi "põhjalikkuse"
     *
     * @param[in] maxTasanand Vaikimisi "tavalise" morf analüüsi
     * tegemiseks sobilik 100
     */
    void SetMaxTasand(const int maxTasand = 100);
    
    void SetFlags(const MRF_FLAGS_BASE_TYPE flags)
    {
        mrfFlags->Set(flags);
    }

    /** Mis lipud heisatud
     * 
     * @param[in] mask
     * Tagastatakse ainult nende lippude seisund, mille kohal @a mask'i bitt
     * on üks. Vaikimisi kõik.
     * @return Vastav lipukombinatsioon
     */    
    MRF_FLAGS_BASE_TYPE GetFlags(const MRF_FLAGS_BASE_TYPE mask = ~0) const
    {
        return mrfFlags->Get(mask);
    }    
    
     /** Kontrollib, kas lipud heisatud.
     *
     * @return @a true kui kõik argumendiga määratud lipud heisatud, muidu @a false.
     * @param[in] const MRF_FLAGS_BASE_TYPE @flagid
     * Nende lippude heisatust kontrollime.
     * Peab olema kombinatsioon loendiga ::MORF_FLAGS määratletud lippudest.
     */
    bool ChkFlags(const MRF_FLAGS_BASE_TYPE flagid) const
    {
        return mrfFlags->ChkB(flagid);
    }    
    
    
    /** @a Tee @a ümber - Lisab sisendahelas olevas lauses sobivatele sõnadele 
     * lipu @a PRMS_JUSTKUI_LAUSE_ALGUS
     * 
     * Kutsutakse välja morfist kui lipp ütleb, et kavatseme hiljem 
     * ühestama hakata.
     * Saab ette lause jagu morf 
     * analüüsimata sõnu
     */
    void MargistaJustkuiLauseAlgused(AHEL2 &ahel, int lauseAlgusIdx=0);

    /** Lisab vajadusel pärisnimeanalüüse
     * 
     * Töötab lause peal peale morf analüüsi 
     * ja @a MargistaJustkuiLauseAlgused() funktsiooni ňing enne ühestamist.

     * @param[in] lauseAlgusIdx
     */
    void LisaPNimeAnalyysid(AHEL2 &ahel, int lauseAlgusIdx=0);


    /** Lisab vajadusel pärisnimeanalüüsi
     * 
     * Töötab 1 morf analüüsi peal 
     * 
     * @param[in] lyli
     */
    void LisaPNimeAnalyys(LYLI &lyli);
    
    /** Tükeldab sisendrea morfitavateks tükkideks ja lisab sisendpuhvrisse
     *
     * Võib sisaldada mitut @a white @a space'ga eraldatud sõna.
     * Hekseldab stringi sõnadeks ja annab saadud sõnad ette
     * funktsioonile @a ETMRFA::Set1(). @n
     * XMLis sisendi korral hoiab tühikut sisaldavad märgendid ühes tükis.
     *
     * @return
     * <ul><li> @a true -- sisendpuhvris tulemuse väljavõtmiseks küllalt sõnu
     *     <li> @a false -- sisendpuhvrisse tuleks veel sõnu lisada
     * </ul>
     * @param[in] buf Sisendstring
     */
    bool Set(const FSXSTRING &buf);

    /** Lisab järjekordse sõna sisendpuhvrisse.
     *
     * @param[in] wstr -- Sisendpuhvrisse lisatav sõna.
     * @return
     * <ul><li> @a true -- sisendpuhvris mitmesõnaliste analüüsiks piisav varu
     *     <li> @a false -- sisendpuhvrisse tuleks veel sõnu lisada
     * </ul>
     */
    bool Set1(const FSXSTRING &wstr);
    
    /** Lisab sisendahelasse etteantud lüli koopia
     * 
     * @param lyli -- selle LYLI koopia läheb sisendpuhvrisse
     * <ul><li> @a true -- sisendpuhvris mitmesõnaliste analüüsiks piisav varu
     *     <li> @a false -- sisendpuhvrisse tuleks veel sõnu lisada
     * </ul> 
     */
    bool Set1(LYLI &lyli);
    
    /** 
     * @param pLyli -- see LYLIviit läheb sisendpuhvrisse. Vabastatakse 
     * destruktoris!
     * <ul><li> @a true -- sisendpuhvris mitmesõnaliste analüüsiks piisav varu
     *     <li> @a false -- sisendpuhvrisse tuleks veel sõnu lisada
     * </ul>      
     */
    bool Set1(LYLI *pLyli);
    
    /** Morfi sisendahelasse (morfi poolt ignoreeritava) metainfo lisamiseks
     *
     * Malliparameeter @a T kuulub hulka {int, FSXSTRING, PCFSAString,
     * STRID, STRID_UTF8}.
     * @param tag
     * @param lFlags Peab vastama parameetri @a tag tüübile,
     * vt @a mrflags.h/LYLI_FLAGS.
     * Näiteks @a Tag<int>(intpos,PRMS_TAGSINT);
     */
    template <typename T>
    void Tag(const T &tag, const LYLI_FLAGS_BASE_TYPE lFlags)
    {
        assert(ClassInvariant());
        assert((lFlags & PRMS_TAG) == PRMS_TAG);
        a.LisaSappa<T > (tag, lFlags);
        assert(ClassInvariant());
    }
    
    void TagLyli(const LYLI &tag)
    {
        assert(ClassInvariant());
        assert((tag.lipp & PRMS_TAG) == PRMS_TAG);
        a.LisaSappaKoopia(tag);
        assert(ClassInvariant());
    }   

    /** Järjekordne lyli morfi väljundahelast
     *
     * @attention
     * <ul><li> Saadud viit tuleb vabastada @a (delete)
     *     <li> Jätab ahelasse teatava mitmesõnaliste käsitlemiseks vajaliku
     *          varu lülisid
     * </ul>
     */
    LYLI *Get(void);

    /** Järjekordne lüli morfi väljundahelast
     *
     * Ammutab väljundahela täitsa tühjaks
     */
    LYLI *Flush(void);

    LYLI *GetMrf(void);
    LYLI *FlushMrf(void);    
 
    LYLI *GetYhh(void);
    LYLI *FlushYhh(bool lubaPoolikutLauset=false);       
    
    /** Väljundist järjekordne lüli morf analüüsi tulemusega või TAG
     *
     * @attention Saadud viit tuleb vabastada @a (delete)
     * @param[out] lyli
     * @return
     * <ul><li> @a ==true Järjekordne lüli
     *     <li> @a ==NULL Pole midagi tagasi anda
     */
    bool Get(LYLI& lyli)
    {
        VIIDAKEST<LYLI> kest(Get());
        if(kest.ptr==NULL)
            return false;
        lyli=*kest.ptr;
        return true;
    }

    /** Väljundist järjekordne lüli morf analüüsi tulemusega või TAG
     *
     * @param[out] lyli
     *
     * @return
     * <ul><li> @a ==true Järjekordne lüli
     *     <li> @a ==NULL Pole midagi tagasi anda
     */
    bool Flush(LYLI& lyli)
    {
        VIIDAKEST<LYLI> kest(Flush());
        if(kest.ptr==NULL)
            return false;
        lyli = *kest.ptr;
        return true;        
    }

    /** Kustutab kõik sisend- ja väljundahelas olevad lülid */
    void Clr(void);

    /** Lähtekoodi versioon SVNi mõttes */
    const char* GetVerProg(void);

    /** Taastab argumentideta konstruktori järgse seisu */
    void Stop(void);

    bool EmptyClassInvariant(void);

    bool ClassInvariant(void);

    /** Morf analüüsi tüürivad lipud */
    MRF_FLAGS *mrfFlags;

    ~ETMRFA(void);

    /** Morfi ahel */
    AHEL2 a;
    
    /** Ühestajale sobivaks mugandatud morf väljund */
    AHEL2 yhh;

protected:
    /** Sisendis lausemärgendite sees */
    bool sisendisLausePooleli;
    
    /** Väljundis lausemärgendite sees */
    bool valjundisLausePooleli;
    
    /** @a Analüüsimist ootavate sõnade arv FIFOs */
    int nSona;

    /** Jooksva tööjärjega ignoreeritavate sõnade blokis */
    bool ignoreBlokis;

    /** Kontrollib, kas parameetriks antud stringi ei ole märgend
     *
     * @return:
     * <ul><li> @a true -- ei ole märgend ja igmore-blokis olev tekst
     *     <li> @a false -- (ainult) märgend(id) või igmore-blokis olev tekst
     * </ul>
     * @param wstr -- Seda stringi kontrollime
     * @param tagId -- Märgendi tüüp
     */
    LYLI_FLAGS SisendStrId(const CFSWString &wstr);
    
    void ArvestaValjundisLauseKonteksti();
    

private:
    int maxTasand;
    //LYLI *retLyliPtr;

    void InitClassVariables(void)
    {
        a.Start(0, 10);
        mrfFlags = NULL;
        mrfFlags = &(LISAKR6NKSUD1::mrfFlags);
        mrfFlags->Set(MF_IGNOREBLK); //TODO::see koht vajab kõpitsemist
        ignoreBlokis = false;
        //retLyliPtr = NULL;
        nSona = 0;
        maxTasand = 100;
        sisendisLausePooleli=false;
        valjundisLausePooleli=false;
    }

    ETMRFA(const ETMRFA&)
    {
        assert(false);
    }

    ETMRFA & operator=(const ETMRFA&)
    {
        assert(false);
        return *this;
    }
};

/** Klass morf. analüüsi ja sünteesi tegemiseks. */
class ETMRFAS // vt mrf-gen.cpp
: public ETMRFA
{
public:

    ETMRFAS(void)
    {
        try
        {
            InitClassVariables();
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** Argumentidega konstruktor
     *
     * Otsib üles vajalikud andmefailid ja initsialiseerib
     * morf analüsaatori
     * @param[in] path Semikooloniga (Windowsis) või kooloniga (Linux)
     * eraldatud kataloogide loend. Sealt otsitakse andmefaile.
     * @param[in] flags Lipud
     */
    ETMRFAS(const CFSString &path, const MRF_FLAGS_BASE_TYPE flags)
    {
        try
        {
            InitClassVariables();
            Start(path, flags);
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** Argumentidega konstruktor
     *
     * Avab vajalikud andmefailid ja initsialiseerib
     * morf analüsaatori
     * @param[in] flags Lipud
     * @param[in] dctMain Põhisõnastik
     * @param[in] dctUser Kasutajasõnastik (kui "", siis pole kasutusel)
     */
    ETMRFAS(const MRF_FLAGS_BASE_TYPE flags,
            const CFSFileName& dctMain, const CFSFileName& dctUser)
    {
        try
        {
            InitClassVariables();
            Start(flags, dctMain, dctUser);
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** Tükeldab sisendrea ja lisab sisendpuhvrisse
     *
     * <ul>
     * <li>
     * Analüüsi korral võib sisaldada mitut @a white @a space'ga eraldatud sõna.
     * Hekseldab stringi sõnadeks ja annab saadud sõnad ette
     * funktsioonile @a ETMRFA::Set1(). @n
     * XMLis sisendi korral hoiab tühikut sisaldavad märgendid ühes tükis.
     * <li>
     * Sünteesi korral peab sisendstring olema kujul @n
     * @a tüvi @a //_sl_ vormid//kigi
     * </ul>
     *
     * @return
     * <ul><li> @a true -- sisendpuhvris tulemuse väljavõtmiseks küllalt sõnu
     *     <li> @a false -- sisendpuhvrisse tuleks veel sõnu lisada
     * </ul>
     * @param[in] buf Sisendstring
     */
    bool Set(const FSXSTRING &wstr);

    /** Lisab sisendpuhvrisse
     * <ul>
     * <li>
     * Analüüsi korral ei tohi sisaldada tühikut (üks sõna korraga)
     * <li>
     * Sünteesi korral peab sisendstring olema kujul @n
     * @a tüvi @a //_sl_ vormid//kigi
     * </ul>
     *
     * @return
     * <ul><li> @a true -- sisendpuhvris tulemuse väljavõtmiseks küllalt sõnu
     *     <li> @a false -- sisendpuhvrisse tuleks veel sõnu lisada
     * </ul>
     * @param[in] buf Sisendstring
     */
    bool Set1(const FSXSTRING &wstr);

    
    /** Lisab sisendahelasse etteantud lüli koopia
     * 
     * @param lyli -- selle LYLI koopia läheb sisendpuhvrisse
     * <ul><li> @a true -- sisendpuhvris mitmesõnaliste analüüsiks piisav varu
     *     <li> @a false -- sisendpuhvrisse tuleks veel sõnu lisada
     * </ul> 
     */
    bool Set1(LYLI &lyli);
    
    /** 
     * @param pLyli -- see LYLIviit läheb sisendpuhvrisse. Vabastatakse 
     * destruktoris!
     * <ul><li> @a true -- sisendpuhvris mitmesõnaliste analüüsiks piisav varu
     *     <li> @a false -- sisendpuhvrisse tuleks veel sõnu lisada
     * </ul>      
     */
    bool Set1(LYLI *pLyli);    
    
    /** TAGi lisamiseks sisendahelasse
     *
     *
     * @param tag
     * @param lFlags
     */
    template <typename T>
    void Tag(const T &tag, const LYLI_FLAGS_BASE_TYPE lFlags)
    {
        assert((lFlags & PRMS_TAG) == PRMS_TAG);
        if (mrfFlags->ChkB(MF_GENE) == false)
            ETMRFA::Tag<T > (tag, lFlags); //analüüsi ahelasse TAG
        else
            aGene.LisaSappa<T > (tag, lFlags); //sünteesi ahelasse TAG
    }

    void TagLyli(const LYLI &tag)
    {
        assert(ClassInvariant());
        assert((tag.lipp & PRMS_TAG) == PRMS_TAG);
        if (mrfFlags->ChkB(MF_GENE) == false)
            ETMRFA::TagLyli(tag);
        else
            aGene.LisaSappaKoopia(tag);
        assert(ClassInvariant());
    }     
    
    /** Väljundist järjekordne lüli morf analüüs/sünteesi tulemusega või TAG
     *
     * @attetntion
     * <ul><li> Saadud viida vabastamine on viida saaja kohustus!
     *     <li> Jätab mitmesõnasliste väljendite analüüsiks vajaliku varu.
     * </ul>
     * @return
     * <ul><li> @a !=NULL Viit infot sisaldavale lülile
     *     <li> @a ==NULL Pole midagi tagasi anda
     */
    LYLI* Get(void);

    /** Väljundist järjekordne lüli morf analüüs/sünteesi tulemusega või TAG
     *
     * @attetntion Saadud viida vabastamine on viida saaja kohustus!
     *
     * @return
     * <ul><li> @a !=NULL Viit infot sisaldavale lülile
     *     <li> @a ==NULL Pole midagi tagasi anda
     */
    LYLI* Flush(void);

    /** Väljundist järjekordne lüli morf analüüs/sünteesi tulemusega või TAG
     *
     * @attention Jätab mitmesõnasliste väljendite analüüsiks vajaliku varu.
     * @param[out] lyli
     * @return
     * <ul><li> @a ==true Järjekordne lüli
     *     <li> @a ==NULL Pole midagi tagasi anda
     */
    bool Get(LYLI& lyli)
    {
        VIIDAKEST<LYLI> kest(Get());
        if(kest.ptr==NULL)
            return false;
        lyli = *kest.ptr;
        return true;        
    }

    /** Väljundist järjekordne lüli morf analüüs/sünteesi tulemusega või TAG
     *
     * @param[out] lyli
     *
     * @return
     * <ul><li> @a ==true Järjekordne lüli
     *     <li> @a ==NULL Pole midagi tagasi anda
     */
    bool Flush(LYLI& lyli)
    {
        VIIDAKEST<LYLI> kest(Flush());
        if(kest.ptr==NULL)
            return false;
        lyli = *kest.ptr;
        return true;
    }

    /** Kustutab kogu sisend- ja väljundpuhvris oleva info. */
    void Clr(void);
    
    //const char* GetVerProg(void);

    /** Morf süntees
     * 
     * @param valja -- sünteesi tulemus
     * @param sisse -- sünteesi sisend
     * <ul><li> sisse.lemma -- mis sõnast tuleb vorme sünteesida
     *      <li> sisse.sl -- mis sõnaliikidesse kuuluvaid sõnu tahetakse, 
     *            "*" korral kõikvõimalikud sõnaliigid
     *      <li> sisse.vormid -- mis vorme tahetakse,
     *            "*" korral kõikvõimalikud vormid
     *      <li> sisse.kigi -- ki/gi, kui seda peaks sünteesima, muidu ""
     * </ul>
     * @param naidis -- sünteesitava paradigma näidissõna (nt palgi või palga),
     *         "" kui sellega ei pea arvestama
     * @return 
     * <ul><li> @a false -- sünteesi õnnestumist ei maksa kontrollidagi
     *      <li> @a true -- süntees õnnestus või ei õnnestunud
     *  </ul>
    */
    bool Synt(MRFTULEMUSED &valja, const MRFTUL &sisse, const FSXSTRING naidis);

    /** sünteesib nõutud vormid, ei arvesta magasini pandud TAGisid
     * 
     * @param valja         - siia pannakse tulemused
     * @param pGeneSona     - mis sõnast tuleb vorme sünteesida
     * @param pGeneLiik     - mis sõnaliikidesse kuuluvaid sõnu tahetakse
     * @param pGeneVormid   - mis vorme tahetakse
     * @param pGeneKigi     - ki/gi, kui seda peaks sünteesima
     * @return 
      * <ul><li> @a false -- sünteesi õnnestumist ei maksa kontrollidagi
     *      <li> @a true -- süntees õnnestus või ei õnnestunud
     *  </ul>
    */
    //bool Synt1(MRFTULEMUSED &valja, const FSXSTRING *pGeneSona,
    //           const FSXSTRING *pGeneLiik, const FSXSTRING *pGeneVormid,
    //           const FSXSTRING *pGeneKigi);


    /** sünteesib nõutud vormid, ei arvesta magasini pandud TAGisid
     * 
     * kui anda sisse ka näidissõna, siis sünteesib ainult need vormid, mis
     * on näidissõnaga samas paradigmas; nt ainult palgi või palga vormid 
     * @param valja         - siia pannakse tulemused
     * @param pGeneSona     - mis sõnast tuleb vorme sünteesida
     * @param pnaidis       - sünteesitava paradigma näidissõna (nt palgi või palga)
     * @param pGeneLiik     - mis sõnaliikidesse kuuluvaid sõnu tahetakse
     * @param pGeneVormid   - mis vorme tahetakse
     * @param pGeneKigi     - ki/gi, kui seda peaks sünteesima
     * @return 
      * <ul><li> @a false -- sünteesi õnnestumist ei maksa kontrollidagi
     *      <li> @a true -- süntees õnnestus või ei õnnestunud
     *  </ul>
    */
    bool SyntDetailne(MRFTULEMUSED &valja, 
        const FSXSTRING *pGeneSona, const FSXSTRING *pnaidis,
        const FSXSTRING *pGeneLiik, const FSXSTRING *pGeneVormid,
        const FSXSTRING *pGeneKigi);

    void Stop(void)
    {
        /*if (retGeneLyliPtr != NULL)
        {
            delete retGeneLyliPtr;
            retGeneLyliPtr = NULL;
        }*/
        adHocString.Empty();
        geneStr.Empty();
        aGene.Stop();
        //lyli.Stop();
        ETMRFA::Stop();
    }

protected:
    /** sünteesi kõik vormid, mida tahetakse
     * 
     * @param pValja        - siia pannakse tulemused
     * @param pMrfTul       - sünteesitava sõna morf. analüüsi tulemused
     * @param pGeneLiik     - mis sõnaliikidesse kuuluvaid sõnu tahetakse
     * @param pGeneVormid   - mis vorme tahetakse
     * @param pGeneKigi     - ki/gi, kui seda peaks sünteesima
     * @return 
     * <ul><li> @a false -- sünteesi õnnestumist ei maksa kontrollidagi
     *      <li> @a true -- süntees õnnestus või ei õnnestunud
     *  </ul>
     */
    bool Gene2(MRFTULEMUSED *pValja, MRFTULEMUSED *pMrfTul,
               const FSXSTRING *pGeneLiik, const FSXSTRING *pGeneVormid,
               const FSXSTRING *pGeneKigi);

    /** sünteesi kõik vormid, mida tahetakse ja mis on kooskõlas näidisega
     * 
     * @param pValja        - siia pannakse tulemused
     * @param pMrfTul       - sünteesitava sõna morf. analüüsi tulemused
     * @param pnaidis       - näidis-sõna 
     * @param pGeneLiik     - mis sõnaliikidesse kuuluvaid sõnu tahetakse
     * @param pGeneVormid   - mis vorme tahetakse
     * @param pGeneKigi     - ki/gi, kui seda peaks sünteesima
     * @return 
     * <ul><li> @a false -- sünteesi õnnestumist ei maksa kontrollidagi
     *      <li> @a true -- süntees õnnestus või ei õnnestunud
     *  </ul>
     */
    bool Gene2Detailne(MRFTULEMUSED *pValja, MRFTULEMUSED *pMrfTul,
               const FSXSTRING *pnaidis,
               const FSXSTRING *pGeneLiik, const FSXSTRING *pGeneVormid,
               const FSXSTRING *pGeneKigi);

    /** sünteesi grammatilistele kategooriatele vastavad sõnavormid
     * 
     * genereerib kõik küsitud vormid, mis etteantud algvormist saab teha;
     * sõnastikupõhine süntees
     * @param pValja        - siia pannakse tulemused
     * @param gPrf          - käib tüve ette
     * @param gTyviAlgne    - tüvi, mida otsitakse leksikonist
     * @param sl            - mis sõnaliikidesse kuuluvaid sõnu tahetakse
     * @param geneVormid    - mis vorme tahetakse
     * @param algv_lopp,    - 0, -ma või -d
     * @param algv_vorm,    - sg_g, sg_n, ma või pl_n
     * @param pGeneKigi     - ki/gi, kui seda peaks sünteesima
     * @return 
     * <ul><li> @a false -- sünteesi õnnestumist ei maksa kontrollidagi
     *      <li> @a true -- süntees õnnestus või ei õnnestunud
     *  </ul>
     */
    bool GeneMTV(MRFTULEMUSED *pValja, FSXSTRING *gPrf, const FSXSTRING *gTyvi,
                 /*const FSXSTRING *gSl,*/ const FSXSTRING *sl, const FSXSTRING *geneVormid,
                 const int algv_lopp, const int algv_vorm, const FSXSTRING *pGeneKigi);

    /** sünteesi grammatilistele kategooriatele vastavad sõnavormid
     * 
     * genereerib kõik küsitud vormid, mis etteantud algvormist saab teha
     * ja mis on kooskõlas näidisega;
     * sõnastikupõhine süntees
     * @param pValja        - siia pannakse tulemused
     * @param gPrf          - käib tüve ette
     * @param gTyviAlgne    - tüvi, mida otsitakse leksikonist
     * @param pnaidis       - näidis-sõna 
     * @param sl            - mis sõnaliikidesse kuuluvaid sõnu tahetakse
     * @param geneVormid    - mis vorme tahetakse
     * @param algv_lopp,    - 0, -ma või -d
     * @param algv_vorm,    - sg_g, sg_n, ma või pl_n
     * @param pGeneKigi     - ki/gi, kui seda peaks sünteesima
     * @return 
     * <ul><li> @a false -- sünteesi õnnestumist ei maksa kontrollidagi
     *      <li> @a true -- süntees õnnestus või ei õnnestunud
     *  </ul>
     */
    bool GeneMTVDetailne(MRFTULEMUSED *pValja, FSXSTRING *gPrf, const FSXSTRING *gTyvi,
                 const FSXSTRING *pnaidis, const FSXSTRING *sl, const FSXSTRING *geneVormid,
                 const int algv_lopp, const int algv_vorm, const FSXSTRING *pGeneKigi);

    /** sünteesi grammatilistele kategooriatele vastavad sõnavormid
     * 
     * genereerib kõik küsitud vormid, mis etteantud algvormist saab teha;
     * tsükeldab üle tüvevariantide ja kutsub igaühe puhul välja GeneL
     * @param pValja        - siia pannakse tulemused
     * @param gPrf          - käib tüve ette
     * @param gTyvi         - algvormi tüvi morf analüüsijast (nt piksel)
     * @param sl            - mis sõnaliiki kuuluvaid sonu tahetakse
     * @param tyveinf       - kõik tüvega seotud info, mis sõnastikust on leitud
     * @param geneVormid    - mis vorme tahetakse
     * @param pGeneKigi     - ki/gi, kui seda peaks sünteesima
     * @return 
     * <ul><li> @a false -- sünteesi õnnestumist ei maksa kontrollidagi
     *      <li> @a true -- süntees õnnestus või ei õnnestunud
     *  </ul>
     */
    bool GeneTL(MRFTULEMUSED *pValja, const FSXSTRING *gPrf,
                const FSXSTRING *gTyvi, const FSxCHAR sl, TYVE_INF *tyveinf,
                const FSXSTRING *geneVormid, const FSXSTRING *pGeneKigi);

    /** sünteesi grammatilistele kategooriatele vastavad sõnavormid
     * 
     * genereerib kõik küsitud vormid, mis etteantud algvormist saab teha;
     * tsükeldab üle tüvevariantide ja kutsub igaühe puhul välja GeneL
     * @param pValja        - siia pannakse tulemused
     * @param naidise_dptr  - näidise tüvega seotud info sõnastikus
     * @param mitu_naidise_homon - näidise homonüüme sõnastikus 
     * @param gPrf          - käib tüve ette
     * @param gTyvi         - algvormi tüvi morf analüüsijast (nt piksel)
     * @param sl            - mis sõnaliiki kuuluvaid sonu tahetakse
     * @param tyveinf       - kõik tüvega seotud info, mis sõnastikust on leitud
     * @param geneVormid    - mis vorme tahetakse
     * @param pGeneKigi     - ki/gi, kui seda peaks sünteesima
     * @return 
     * <ul><li> @a false -- sünteesi õnnestumist ei maksa kontrollidagi
     *      <li> @a true -- süntees õnnestus või ei õnnestunud
     *  </ul>
     */
    bool GeneTLDetailne(MRFTULEMUSED *pValja, const TYVE_INF *naidise_dptr,
                const int mitu_naidise_homon, const FSXSTRING *gPrf,
                const FSXSTRING *gTyvi, const FSxCHAR sl, TYVE_INF *tyveinf,
                const FSXSTRING *geneVormid, const FSXSTRING *pGeneKigi);
    
    /** sünteesi grammatilistele kategooriatele vastavad sõnavormid
     * 
     * genereerib kõik küsitud vormid, mis talle etteantud tüvest saab teha;
     * ja mis on kooskõlas näidisega;
     * tsükeldab üle grammatiliste kategooriate ja kutsub igaühe puhul välja GeneL1
     * @param pValja        - siia pannakse tulemused
     * @param gPrf          - käib tüve ette
     * @param gTyvi         - tüvi morf analüüsijast
     * @param sl            - mis sõnaliiki kuuluvaid sonu tahetakse
     * @param lgNr          - lõpugrupi nr; lõpugruppi kuuluvad kõik ühe tüve lõpud
     * @param geneVormid    - mis vorme tahetakse
     * @param pGeneKigi     - ki/gi, kui seda peaks sünteesima
     * @return 
     * <ul><li> @a false -- sünteesi õnnestumist ei maksa kontrollidagi
     *      <li> @a true -- süntees õnnestus või ei õnnestunud
     *  </ul>
     */
    bool GeneL(MRFTULEMUSED *pValja, const FSXSTRING *gPrf,
               const FSXSTRING *gTyvi, const FSxCHAR sl, const int lgNr,
               const FSXSTRING *geneVormid, const FSXSTRING *pGeneKigi);

    /** sünteesi ühele grammatilisele kategooriale vastav sõnavorm
     * 
     * seda kasutab ainult GeneL
     * @param pValja        - siia pannakse tulemused
     * @param gPrf          - käib tüve ette
     * @param gTyvi         - tüvi morf analüüsijast
     * @param sl            - mis sõnaliiki kuuluvaid sonu tahetakse
     * @param lgNr          - lõpugrupi nr; lõpugruppi kuuluvad kõik ühe tüve lõpud
     * @param geneVorm      - mis vormi tahetakse
     * @param pGeneKigi     - ki/gi, kui seda peaks sünteesima
     * @return 
     * <ul><li> @a false -- sünteesi õnnestumist ei maksa kontrollidagi
     *      <li> @a true -- süntees õnnestus või ei õnnestunud
     *  </ul>
     */
    bool GeneL1(MRFTULEMUSED *pValja, const FSXSTRING *gPrf,
                const FSXSTRING *gTyvi, const FSxCHAR sl, const int lgNr,
                const FSXSTRING *geneVorm, const FSXSTRING *pGeneKigi);

    /** sünteesi sufiksi alusel
     * 
     * @param pValja        - siia pannakse tulemused
     * @param gPrf          - käib tüve ette
     * @param gSuffiks      - suffiks morf analüüsija väljundist
     * @param sl            - mis sõnaliiki kuuluvaid sonu tahetakse
     * @param geneVormid    - mis vorme tahetakse
     * @param algv_lopp     - 0, -ma voi -d
     * @param algv_vorm     - sg_g, sg_n, ma või pl_n
     * @param pGeneKigi     - ki/gi, kui seda peaks sünteesima
     * @return              
     * <ul><li> @a false -- sünteesi õnnestumist ei maksa kontrollidagi
     *      <li> @a true -- süntees õnnestus või ei õnnestunud
     *  </ul>
    */
    bool GeneSTV(MRFTULEMUSED *pValja, const FSXSTRING *gPrf,
                 const FSXSTRING *gSuffiks, /*const FSXSTRING *gSufSl,*/ const FSXSTRING *sl,
                 const FSXSTRING *geneVormid, 
                 const int algv_lopp, const int algv_vorm, const FSXSTRING *pGeneKigi);

    /** süntees oletades
     * 
     * s.t. leksikoni abil pole see sõna anlüüsitav
     * 
     * @param pValja        - siia pannakse väljund
     * @param pMrfTul       - analüüsi oletamis-tulemus
     * @param pGeneLiik     - mis sõnaliiki kuuluvaid sõnu tahetakse
     * @param pGeneVormid   - mis vorme tahetakse
     * @param pGeneKigi     - ki/gi, mis peaks sõnale lõppu minema
     * @return 
     * <ul><li> @a false -- sünteesi õnnestumist ei maksa kontrollidagi
     *      <li> @a true -- süntees õnnestus või ei õnnestunud     */
    bool ArvaGene2(MRFTULEMUSED *pValja, MRFTULEMUSED *pMrfTul,
                   const FSXSTRING *pGeneLiik, const FSXSTRING *pGeneVormid,
                   const FSXSTRING *pGeneKigi);

private:

    void InitClassVariables()
    {
        //retGeneLyliPtr = NULL;
    }

    AHEL2 aGene;
    FSXSTRING adHocString, geneStr;

    /** selle kaudu annab süntesaator tulemuse väja */
    //LYLI* retGeneLyliPtr;

    ETMRFAS(const ETMRFAS&)
    {
        assert(false);
    }

    ETMRFAS & operator=(const ETMRFAS&)
    {
        assert(false);
        return *this;
    }
};


#endif
