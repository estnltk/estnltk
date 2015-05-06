#if !defined(T3COMMON_H)
#define T3COMMON_H

#include <stdio.h> //dbout vajab seda, muu mitte

#include <math.h>
#include <float.h>
#include <assert.h>

#include "ahel2.h"
#include "post-fsc.h"
#include "fsxstring.h"
#include "tmplarray.h"
#include "mrflags.h"
#include "etmrf.h"

#include "dctmetainf.h"

#define UKAPROB float
#define UKALOG(ukaProb) logf(ukaProb)
#define UKAPROBMAX FLT_MAX // DBL_MAX

#define SONA_ON_HARULDANE 1
#define LISATUDHARVESINEMINE 1 //vt t3lexpre.cpp/LexFromCooked()

//=========================================================

/** Mitmesusklass */
class MKLASS
{
public:

    /** Mitmesusklassi element */
    struct MKELEM
    {
        /** ühestamismärgendi indeks */
        int tagIdx;
        /** ühestamismärgendi tõenäosus */
        UKAPROB tagProb;
    } *tagIdxProb;

    /** mitmesusklassi pikkus */
    int n;

    MKLASS(void)
    {
        InitClassVariables();
    }

    /**
     * 
     * @param _n_ Mitmesusklassi pikkus
     */
    MKLASS(const int _n_)
    {
        try
        {
            InitClassVariables();
            Start(_n_);
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** Copy-konstruktor */
    MKLASS(const MKLASS& mk)
    {
        try
        {
            InitClassVariables();
            Start(mk);
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** Argumentideta konstruktori järgseks initsialiseerimiseks
     * 
     * @param _n_ Mitmesusklassi pikkus
     */
    void Start(const int _n_)
    {
        tagIdxProb = new MKELEM[_n_];
        n = _n_;
    }

    /** Argumentideta konstruktori järgseks initsialiseerimiseks */
    void Start(const MKLASS& mk)
    {
        Start(mk.n);
        memmove(tagIdxProb, mk.tagIdxProb, n * sizeof (MKELEM));
    }

    /** Võrdle jooksvat kirjet etteantud kirjega, järjestamiseks */
    int Compare(const MKLASS* mk, const int placeHolder = 0) const
    {
        int ret;
        if ((ret = n - mk->n) != 0)
            return ret;
        assert(n == mk->n);
        for (int i = 0; i < n; i++)
        {
            if ((ret = tagIdxProb[i].tagIdx - mk->tagIdxProb[i].tagIdx) != 0)
                return ret;
            //if(tagIdxProb[i].tagProb < mk->tagIdxProb[i].tagProb)
            //    return -1;
            //if(tagIdxProb[i].tagProb > mk->tagIdxProb[i].tagProb)
            //    return  1;
        }
        // kirjed on võrdsed, kui nad koosnevad samadest ühestajamärgenditest
        // tõenäosused ei puhu siinkohal pilli
        assert(false);
        return 0;
    }

    /** Võrdle jooksva kirje võtit etteantud võtmega, kahendotsimiseks */
    int Compare(const TMPLPTRARRAYBIN<BASIC_TYPE_WITH_CMP<int>, int>* intArr,
                const int placeHolder = 0) const
    {
        int ret;
        if ((ret = n - intArr->idxLast) != 0)
            return ret;
        for (int i = 0; i < n; i++)
        {
            if ((ret = tagIdxProb[i].tagIdx - ((*intArr)[i])->obj) != 0)
                return ret;
        }
        return 0;
    }

    void Stop(void)
    {
        if (tagIdxProb != NULL)
            delete [] tagIdxProb;
        InitClassVariables();
    }

    ~MKLASS(void)
    {
        Stop();
    }

private:

    void InitClassVariables(void)
    {
        tagIdxProb = NULL;
        n = -1;
    }

};

//=========================================================

/** Klass ühe sõnaga seotud info käitlemiseks ühestaja leksikonis */
class LEXINF
{
public:
    /** Sõnavorm */
    CFSAString str;
    /** Massiivi tagIdxProb pikkus */
    int n;

    /**  Massiiv (märgendi indeks+tõenäosus)*/
    struct LEXINFEL
    {
        /** ühestamismärgendi indeks */
        int tagIdx;
        /** ühestamismärgenid tõenäosus */
        UKAPROB tagProb;
    } *tagIdxProb;

    LEXINF(void)
    {
        InitClassVariables();
        assert(EmptyClassInvariant());
    }

    /** Võtmete võrdlemiseks */
    int Compare(const CFSAString* key, const int placeHolder = 0) const
    {
        return str.Compare((const char*) *key);
    }

    /** Kirjete võrdlemiseks */
    int Compare(const LEXINF* rec, const int placeHolder = 0) const
    {
        int ret;

        if ((ret = str.Compare((const char*) (rec->str))) != 0)
            return ret;
        if ((ret = n - rec->n) != 0)
            return ret; // eri pikkusega massiivid
        for (int i = 0; i < n; i++)
        {
            // sama pikkasid massiive võrdleme elementhaaval
            if ((ret = tagIdxProb[i].tagIdx - rec->tagIdxProb[i].tagIdx) == 0)
                return ret;
            if (tagIdxProb[i].tagProb < rec->tagIdxProb[i].tagProb)
                return -1;
            if (tagIdxProb[i].tagProb > rec->tagIdxProb[i].tagProb)
                return 1;
        }
        return 0;
    }

    void Stop(void)
    {
        if (tagIdxProb != NULL)
            delete [] tagIdxProb;
        InitClassVariables();
    }

    void InitClassVariables(void)
    {
        str.Empty();
        n = 0;
        tagIdxProb = NULL;
    }

    bool EmptyClassInvariant(void)
    {
        return
        str.GetLength() == 0 &&
            n == 0 &&
            tagIdxProb == NULL;
    }

    bool ClassInvariant(void)
    {
        return
        str.GetLength() > 0 &&
            n > 0 &&
            tagIdxProb != NULL;
    }

    ~LEXINF(void)
    {
        Stop();
    }

private:

    /** Omistamisoperaator on illegaalne */
    LEXINF & operator=(const LEXINF&)
    {
        assert(false);
        return *this;
    }

    /** Copy-konstruktor on illegaalne */
    LEXINF(const LEXINF&)
    {
        assert(false);
    }
};

//=========================================================

/** Trigrammidel põhinev ühestaja, sisendiks morfitud lauset sisaldav UTF8 ahel */
class ET3UTF8AHEL
{
public:

    ET3UTF8AHEL(void)
    {
        InitClassVariables();
    }

    /** Argumentidega konstruktor
     * 
     * @param _flags_  Lipud
     * @param dct  Ühestaja andmefail
     */
    ET3UTF8AHEL(const MRF_FLAGS_BASE_TYPE _flags_,
           const CFSFileName& dct)
    {
        try
        {
            InitClassVariables();
            Start(_flags_, dct);
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** Argumentideta konstruktori järgseks initsialiseerimiseks
     * 
     * @param _flags_  Lipud
     * @param dct  Ühestaja andmefail
     */
    void Start(const MRF_FLAGS_BASE_TYPE _flags_,
               const CFSFileName& dct);

    /**  Lippude sättimiseks
     * 
     * @param _flags_ -- uus lippude kombinatsioon
     */
    void SetFlags(const MRF_FLAGS_BASE_TYPE _flags_)
    {
        flags.Set(_flags_);
    }
    
    /** Lause ühestamisks
     * 
     * @param analyysid UTF8 vormingus ahel morfitud sisendlause ja TAGidega
     */
    void Run(AHEL2_UTF8& analyysid);

    void Stop(void);

    /** statistika: korpuse baasil tehtud sõnastikust */
    int lexCntK;
    /** statistika: morfi põhisõnastikust */
    int lexCntP;
    /** statistika: morfi oletajast */
    int lexCntO;
    /** statistika: morfi lisasõnastikust */
    int lexCntL;

    /** statistika: Mitmesusklass leksikonis olevast vormist */
    int mkLexiVormist;
    /** statistika: Mitmesusklass leksikonis olevate märgendiklasside baasil */
    int mkLexiBaasil;
    /** statistika: Mitmesusklass morfist võrdsete tõenäosustega */
    int mkKoikVordsed;
    /** statistika: Mitmesusklass morfist, tõenäosust arvutame märgendite esinemisarvu pealt */
    int mkTagiSag;

    /** lipp: Ignoreeri vorme mille sagedus sagedustabelis sellega &gt;= */
    int mitmesusKlassidesIgnoreeeri;
    /** lipp: alati @a false, vana katsega soetud. @a true -- Morfist saadud mitmesuklassile lexikoni põhjal tõenäosused */
    bool mitmesusKlassKasutu;
    /** lipp: alati @a false, vana katsega soetud. @a true -- Ei kasuta leksikonis olevaid märgendite tõenäosusi */
    bool lexProbKasutu;

    bool EmptyClassInvariant(void)
    {
        return
        mitmesusKlassidesIgnoreeeri == SONA_ON_HARULDANE &&
            mitmesusKlassKasutu == false &&
            lexProbKasutu == false &&
            lexCntK == 0 &&
            lexCntP == 0 &&
            lexCntO == 0 &&
            lexCntL == 0 &&
            mkLexiVormist == 0 &&
            mkLexiBaasil == 0 &&
            mkKoikVordsed == 0 &&
            mkTagiSag == 0 &&
            tags.EmptyClassInvariant() == true &&
            meta.EmptyClassInvariant() == true &&
            tabel.EmptyClassInvariant() == true &&
            lexArr.EmptyClassInvariant() == true &&
            mKlassid.EmptyClassInvariant() == true;
    }

    bool ClassInvariant(void)
    {
        bool ret =
            mitmesusKlassidesIgnoreeeri >= SONA_ON_HARULDANE &&
            lexCntK >= 0 &&
            lexCntP >= 0 &&
            lexCntO >= 0 &&
            lexCntL >= 0 &&
            mkLexiVormist >= 0 &&
            mkLexiBaasil >= 0 &&
            mkKoikVordsed >= 0 &&
            mkTagiSag >= 0 &&
            tags.ClassInvariant() == true &&
            meta.ClassInvariant() == true &&
            tabel.ClassInvariant() == true &&
            lexArr.ClassInvariant() == true &&
            mKlassid.ClassInvariant() == true;
        return ret;
    }

    ~ET3UTF8AHEL(void)
    {
        Stop();
    }
    
protected:
    /** Morfi ja ühestaja lipud */
    MRF_FLAGS flags;    

private:

    /** ühestamismärgendite loend */
    TMPLPTRARRAYBIN<PCFSAString, CFSAString> tags;
    /** Ühestamismärgendite esinemisarvud treeningkorpuses */
    SA1<int> gramm1;
    /** Ühestaja andmefailiga seotud metainf */
    DCTMETASTRCT meta;
    /** n-grammide tabel */
    SA3<UKAPROB> tabel;
    /** Massiiv leksikoni hoidmiseks mälus */
    TMPLPTRARRAYBIN<LEXINF, CFSAString> lexArr;
    /** Mitmesusklassid */
    TMPLPTRARRAYBIN<MKLASS, TMPLPTRARRAYBIN<BASIC_TYPE_WITH_CMP<int>, int> > mKlassid;

    void InitClassVariables(void)
    {
        mitmesusKlassidesIgnoreeeri = SONA_ON_HARULDANE;
        mitmesusKlassKasutu = false;
        lexProbKasutu = false;

        lexCntK = lexCntP = lexCntO = lexCntL = 0;
        mkLexiVormist = mkLexiBaasil = mkKoikVordsed = mkTagiSag = 0;
    }

    void DBLexJaMorf(const MRFTULEMUSED_UTF8* m, const LEXINF* lexInf);
};

//--------------------------------------------------------------------------


/**
 * 
 * <ul><li><b>MF_YHESTA</b> lipp kohustuslik
 *     <li><b> MF_XML </b> lipp
 *     <ul><li><b>  pole </b>
 *         <ul><li> Sisendis ei tohi olla sõnaga kokkukleepunud XML märgendeid
 *             <li> Lisa Set1-funktsiooniga lause jagu lülisid ja siis korja
 *                  Flush-funktsiooniga tulemus välja
 *         </ul>
 *         <li><b> on </b>
 *         <ul><li> XMLis märgendatud laused kohustuslikud
 *             <li> Lisa Set1-funktsiooniga lülisid ja kui Set1-funktsioonist
 *                  tuli tagasi @a true, korja Flush-funktsiooniga tulemus välja
 *         </li>
 *     </ul>
 * </ul>
 * 
 * <ul><li> sisendmagasini tohib panna korraga ainult 1 lause
 * <ul>
 */
class ET3 : public ET3UTF8AHEL
{
public:
    ET3(void)
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
    
    ET3(const MRF_FLAGS_BASE_TYPE flags, const CFSFileName& dctT3)
    {
        try
        {
            InitClassVariables();
            Start(flags, dctT3);
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** Initsialiseerimiseks
     * 
     * @param flags Lipud
     * @param dctMain Morfi põhisõnastik
     * @param dctUser Morfi kasutajasõnastik (kui "", siis pole kasutusel)
     * @param dctT3 Ühestaja sõnastik
     */
    void Start(const MRF_FLAGS_BASE_TYPE flags, const CFSFileName& dctT3);
    
    /** Ühestaja sisendahelasse (morfi poolt ignoreeritava) metainfo lisamiseks
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
        ahelMyh.LisaSappa<T>(tag, lFlags);
    }
    
    bool Set1(LYLI &lyli); 
    
    /** Sisendahelasse LYLI_UTF8 koopia
     * 
     * @param lyli
     * @return 
     * <ul><li> true -- hakka lylisid väljavõtma
     *     <li> false -- kogu veel sisendit
     * </ul>
     */
    bool Set1(LYLI_UTF8 &lyli);
    
    /** Sisendahelasse LYLI_UTF8 viit
     * 
     * @param pLyli -- selle vabastamisega hakkab see klass ise tegelema!
     * @return 
     * <ul><li> true -- hakka lylisid väljavõtma
     *     <li> false -- kogu veel sisendit
     * </ul>
     */
    bool Set1(LYLI_UTF8 *pLyli);
    
    /** Väljundahelast järjekordne lüli (ühestatud analüüs või TAG)
     * 
     * @attetntion
     * <ul><li> Saadud viida vabastamine on viida saaja kohustus!
     *     <li> Jätab mitmesõnasliste väljendite analüüsiks vajaliku varu.
     * </ul>
     * @return
     * <ul><li> @a !=NULL Viit infot sisaldavale lülile
     *     <li> @a ==NULL Pole midagi tagasi anda
     * </ul>
     */
    LYLI *Flush(void);

    
    /** Väljundahelast järjekordse lüli koopia (ühestatud analüüs või TAG)
     * 
     * @attention  Sobib sünteesis, morfis, ühestamises
     *  
     * @param[out] lyli
     *
     * @return
     * <ul><li> true -- Järjekordne lüli
     *     <li> false -- Pole midagi tagasi anda
     * </ul>
     */
    bool Flush(LYLI& lyli);      
    
    /** 
     * 
     * @return Ühestatud lause väljundahelas
     */
    bool JubaYhestatud(void)
    {
        return jubaYhestatud;
    }
    
    /** Tühjendab sisend/väljundahelad */
    void Clr(void);

    /** Programmikoodi versioon SVNist */
    //const char* GetVerProg(void);

    /** Tagab destruktoris reserveeritud mälu vabastamise ja failide sulgemise
     * 
     * @attention Mitte kassutada väljaspool destruktorit  
     */
    void Stop(void);    
    
    ~ET3(void)
    {
        ET3::Stop();
    }

    bool EmptyClassInvariant(void)
    {
        return jubaYhestatud==false && lauses==false && 
                                            ahelMyh.EmptyClassInvariant();
    }
    
    bool ClassInvariant(void)
    {
        return ahelMyh.EmptyClassInvariant();
    }    
    
private:
    bool lauses;
    bool jubaYhestatud;  
    
    /** ühestaja väljundahel */
    AHEL2_UTF8 ahelMyh;    
    
    bool ArvestaLauseKonteksti(LYLI_UTF8 &lyli);
    
    void Yhesta(void);
    
    void InitClassVariables(void)
    {
        jubaYhestatud=false;
        lauses=false;
    }

};



//--------------------------------------------------------------------------
#if defined ( defETSYANYH )
/** Morfitud sisendahela stat-ühestamine */
class ETSYANYH
{
public:
    ETSYANYH(void)
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
    
    /** Argmumentidega konstruktor
     * 
     * @param flags Lipud
     * @param dctMain Morfi põhisõnastik
     * @param dctUser Morfi kasutajasõnastik (kui "", siis pole kasutusel)
     * @param dctT3 Ühestaja sõnastik
     */
    ETSYANYH(const MRF_FLAGS_BASE_TYPE flags,
           const CFSFileName& dctMain, const CFSFileName& dctUser,
           const CFSFileName& dctT3)
    {
        try
        {
            InitClassVariables();
            Start(flags, dctMain, dctUser, dctT3);
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** Initsialiseerimiseks
     * 
     * @param flags Lipud
     * @param dctMain Morfi põhisõnastik
     * @param dctUser Morfi kasutajasõnastik (kui "", siis pole kasutusel)
     * @param dctT3 Ühestaja sõnastik
     */
    void Start(const MRF_FLAGS_BASE_TYPE flags,
               const CFSFileName& dctMain, const CFSFileName& dctUser,
               const CFSFileName& dctT3);

    /** Määrab morf analüüsi "põhjalikkuse"
     *
     * @param[in] maxTasanand Vaikimisi "tavalise" morf analüüsi
     * tegemiseks sobilik 100
     */
    void SetMaxTasand(const int maxTasand = 100)
    {
        mrf.SetMaxTasand(maxTasand);
    }
    
    /** Morfi/ühestaja lippude sättimiseks
     * 
     * Kui lipp @a MF_YHESTA on püsti, lisatakse alati
     * ka @a MF_YHMRG lipp
     */
    void SetFlags(const MRF_FLAGS_BASE_TYPE mFlags);
    
    /** Mis lipud heisatud
     * 
     * @param[in] mask
     * Tagastatakse ainult nende lippude seisund, mille kohal @a mask'i bitt
     * on üks. Vaikimisi kõik.
     * @return Vastav lipukombinatsioon
     */    
    MRF_FLAGS_BASE_TYPE GetFlags(const MRF_FLAGS_BASE_TYPE mask = ~0) const
    {
        return mrf.mrfFlags->Get(mask);
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
        return mrf.mrfFlags->ChkB(flagid);
    }
    
    /** Lisab sisendahelasse stringi (rea)
     * 
     * @param wstr
     * @return 
     * <ul><li> true -- sisendis on mitmesõnaliste morfimiseks piisavalt sõnu
     *     <li> false -- sisendis pole mitmesõnaliste morfimiseks piisavat
     * sõnade varu
     */
    bool Set(const FSXSTRING &wstr);

    /** Lisab sisendahelasse ühe sõna 
     * 
     * @param wstr
     * @return 
     * <ul><li> true -- sisendis on mitmesõnaliste morfimiseks piisavalt sõnu
     *     <li> false -- sisendis pole mitmesõnaliste morfimiseks piisavat
     * sõnade varu
     */
    bool Set1(const FSXSTRING &wstr);
    
    /** Sisendahelasse LYLI koopia
     * 
     * @param lyli
     * @return 
     * <ul><li> true -- hakka lylisid väljavõtma
     *     <li> false -- kogu veel sisendit
     * </ul>
     */
    bool Set1(LYLI &lyli);
    
    /** Sisendahelasse LYLI viit
     * 
     * @param pLyli -- selle vabastamisega hakkab see klass ise tegelema!
     * @return 
     * <ul><li> true -- hakka lylisid väljavõtma
     *     <li> false -- kogu veel sisendit
     * </ul>
     */
    bool Set1(LYLI *pLyli);
    
    /** Lisab sisendahelasse TAGi
     * 
     * Malliparameeter @a T kuulub hulka {int, FSXSTRING, PCFSAString,
     * STRID, STRID_UTF8}.
     * @param tag
     * @param lFlags
     */
    template <typename T>
    void Tag(const T &tag, const LYLI_FLAGS_BASE_TYPE lFlags)
    {
        mrf.Tag<T > (tag, lFlags);
    }

    /** Lisab sisendahelasse TAGi */
    void TagLyli(const LYLI &tag)
    {
        mrf.TagLyli(tag);
    }
    
    /** Väljundahelast järjekordne lüli (morf süntees/analüüs või TAG)
     * 
     * <ul><li> Kasutada ainult morf analüüsi ja sünteesi väljundi saamiseks
     *     <li> Saadud viida vabastamine on viida saaja kohustus!
     *     <li> Morf analüüsi korral jätab mitmesõnasliste väljendite 
     *          analüüsiks vajaliku sõnade varu.
     * </ul>
     * @return
     * <ul><li> !=NULL -- Viit järjekordsele lülile
     *     <li> ==NULL -- Kogu sisendid juurde
     * <ul> 
     */
    LYLI* Get(void);

    /** Väljundahelast järjekordse lüli koopia (morf süntees/analüüs või TAG)
     * 
     * <ul><li> Kasutada ainult morf analüüsi ja sünteesi väljundi saamiseks
     *     <li> Morf analüüsi korral jätab mitmesõnasliste väljendite 
     *          analüüsiks vajaliku sõnade varu.
     * </ul>
     * @param lyli
     * @return
     * <ul><li> true -- Järjekordne lüli
     *     <li> false -- Kogu sisendid juurde
     * </ul>
     */
    bool Get(LYLI& lyli);

    /** Morf analüüsi/sünteesi tulemus väljundahelasse @a ahelMrf
     * 
     * @attention Ainult morf analüüsi ja sünteesi väljundi saamiseks
     * @return 
     * <ul><li> @a true -- Saime midagi morfi väljundahelasse @a ahelMrf
     *     <li> @a false -- Kogu morfi sisend käideldud
     * </ul>
     */
    bool RunMrf(void);

    /** Väljundahelast järjekordne lüli (morf süntees/analüüs/ühestaja või TAG)
     * 
     * @attetntion
     * <ul><li> Saadud viida vabastamine on viida saaja kohustus!
     *     <li> Jätab mitmesõnasliste väljendite analüüsiks vajaliku varu.
     * </ul>
     * @return
     * <ul><li> @a !=NULL Viit infot sisaldavale lülile
     *     <li> @a ==NULL Pole midagi tagasi anda
     * </ul>
     */
    LYLI* Flush(bool lubaPoolikutLauset=false);

    /** Väljundahelast järjekordse lüli koopia (morf süntees/analüüs/ühestaja või TAG)
     * 
     * @attention  Sobib sünteesis, morfis, ühestamises
     *  
     * @param[out] lyli
     *
     * @return
     * <ul><li> @a ==true Järjekordne lüli
     *     <li> @a ==false Pole midagi tagasi anda
     * </ul>
     */
    bool Flush(LYLI& lyli);

    /** Tühjendab sisend/väljundahelad */
    void Clr(void);

    /** Programmikoodi versioon SVNist */
    const char* GetVerProg(void)
    {
        return mrf.GetVerProg();
    }
    
    /** Tagab destruktoris reserveeritud mälu vabastamise ja failide sulgemise
     * 
     * @attention Mitte kassutada väljaspool destruktorit  
     */
    void Stop(void);    
    
    ~ETSYANYH(void)
    {
        Stop();
    }

    /** Morfi väljundahel, mis läheb ühestaja sisendiks */
    AHEL2 ahelMrf;

protected:    
    ET3 myh;
private:
    /** morf analüsaatori ja süntesaatori mootor */
    //ETMRFAS mrf;
    /** ühestaja mootor */


    /** ühestaja väljundahel */
    AHEL2 ahelMyh;

    void InitClassVariables(void)
    {

    }

};
#endif
#endif





