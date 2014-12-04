

#if !defined( CTULEM_H )
#define CTULEM_H

#include "post-fsc.h"
#include "mrflags.h"
#include "fsxstring.h"
#include "tmplptrsrtfnd.h"
#include "tloendid.h"
#include "viga.h"

class MRF2YH2MRF;

/** Klassimall ühe morf-analüüsivariandi hoidmiseks
 *
 * Mallipararameetrid:
 * <ol><li> S_TYYP @a S_TYYP on stringitüüp @a (FSXSTRING või @a PCFSAString)
 *     <li> C_TYYP @a C_TYYP on sümbolitüüp @a (FSWCHAR või @a char)
 * </ol>
 */
/*
 * näiteks:
   peeti
    peet+0 //_S_ adt, sg p, //
    pida+ti //_V_ ti, //

 */
template <class S_TYYP, class C_TYYP>
class MRFTUL_TMPL
{
public:
    /** Vajadusel suvaline muu tekstiline info */
    S_TYYP muuInf;

    /** Vajadusel ühestaja märgend */
    S_TYYP mrg1st;

    /**  Vajadusel lemma */
    S_TYYP lemma;

    /** Tüvi */
    S_TYYP tyvi;

    /** Lõpp */
    S_TYYP lopp;

    /** Liide @a ki või @a gi */
    S_TYYP kigi;

    /** Sõnaliigistring (st alati @a sl[1]==EOS) */
    S_TYYP sl;

    /** Vorm(id) */
    S_TYYP vormid;

    MRFTUL_TMPL(void)
    {
        InitClassVariables();
    }

    /** Copy-konstruktor, argument 2/4 baidine  unicode */
    MRFTUL_TMPL(const MRFTUL_TMPL<FSXSTRING, FSWCHAR>& mrfTul)
    {
        try
        {
            InitClassVariables();
            Start(mrfTul);
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** Copy-konstruktor, argument UTF8 */
    MRFTUL_TMPL(const MRFTUL_TMPL<PCFSAString, char>& mrfTul_utf8)
    {
        try
        {
            InitClassVariables();
            Start(mrfTul_utf8);
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** Konstruktor
     *
     * @param[in] _tyvi_ -- Tüvi
     * @param[in] _lopp_ -- Lõpp
     * @param[in] _kigi_ -- Liide @a ki või @a gi
     * @param[in] _sl_ -- Sõnaliigistring (sl[1]==0)
     * @param[in] _vormid_ -- Vorm(id)
     * @param[in] _muuInf_ -- Vajadusel suvaline muu tekstiline info
     * @param[in] _mrg1st_ -- Vajadusel ühestaja märgend
     * @param[in] _lemma_ -- Vajadusel lemma
     */
    MRFTUL_TMPL(const C_TYYP *_tyvi_, const C_TYYP *_lopp_, const C_TYYP *_kigi_,
                const C_TYYP *_sl_, const C_TYYP *_vormid_,
                const C_TYYP *_muuInf_ = NULL, const C_TYYP *_mrg1st_ = NULL,
                const C_TYYP *_lemma_ = NULL)
    {
        try
        {
            InitClassVariables();
            Start(_tyvi_, _lopp_, _kigi_, _sl_, _vormid_, _muuInf_, _mrg1st_, _lemma_);
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** Konstrueeri stringist
     *
     * @param[in] xstr -- Morf analüüs stringina
     */
    MRFTUL_TMPL(const S_TYYP* xstr)
    {
        try
        {
            InitClassVariables();
            Start(xstr);
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** Initsialiseerib
     *
     * @param[in] mrfTul -- Initsialiseerime unicode kodeeringus
     * analüüsiklassist
     */
    void Start(const MRFTUL_TMPL<FSXSTRING, FSWCHAR>& mrfTul)
    {
        Start((const FSWCHAR *) (mrfTul.tyvi),
              (const FSWCHAR *) (mrfTul.lopp), (const FSWCHAR *) (mrfTul.kigi),
              (const FSWCHAR *) (mrfTul.sl), (const FSWCHAR *) (mrfTul.vormid),
              (const FSWCHAR *) (mrfTul.muuInf), (const FSWCHAR *) (mrfTul.mrg1st),
              (const FSWCHAR *) (mrfTul.lemma));
    }

    /** Initsialiseerib
     *
     * @param[in] mrfTul -- Initsialiseerime utf8 kodeeringus analüüsiklassist
     */
    void Start(const MRFTUL_TMPL<PCFSAString, char>& mrfTul_utf8)
    {
        Start((const char *) (mrfTul_utf8.tyvi),
              (const char *) (mrfTul_utf8.lopp), (const char *) (mrfTul_utf8.kigi),
              (const char *) (mrfTul_utf8.sl), (const char *) (mrfTul_utf8.vormid),
              (const char *) (mrfTul_utf8.muuInf), (const char *) (mrfTul_utf8.mrg1st),
              (const char *) (mrfTul_utf8.lemma));
    }

    /** Initsialiseerib UNICODEis algosakestest
     *
     * @param[in] _tyvi_ -- Tüvi (ei tohi olla NULL viit)
     * @param[in] _lopp_ -- Lõpp (ei tohi olla NULL viit)
     * @param[in] _kigi_ -- Liide 'ki' või 'gi' (ei tohi olla NULL viit)
     * @param[in] _sl_ -- Sõnaliigistring (st alati sl[1]==0,
     *                    ei tohi olla NULL viit))
     * @param[in] _vormid_ -- Vorm(id) (ei tohi olla NULL viit)
     * @param[in] _muuInf_ -- Vajadusel suvaline muu tekstiline info
     * @param[in] _mrg1st_ -- Vajadusel ühestaja märgend
     * @param[in] _lemma_ --  Vajadusel lemma
     */
    void Start(const FSWCHAR *_tyvi_, const FSWCHAR *_lopp_,
               const FSWCHAR *_kigi_, const FSWCHAR *_sl_, const FSWCHAR *_vormid_,
               const FSWCHAR *_muuInf_ = NULL, const FSWCHAR *_mrg1st_ = NULL,
               const FSWCHAR *_lemma_ = NULL)
    {
        assert(_tyvi_ != NULL && _lopp_ != NULL &&
               _kigi_ != NULL && _sl_ != NULL && _vormid_ != NULL);
        if (_muuInf_ != NULL)
            muuInf = _muuInf_;
        else
            muuInf.Empty();
        if (_mrg1st_ != NULL)
            mrg1st = _mrg1st_;
        else
            mrg1st.Empty();
        if (_lemma_ != NULL)
            lemma = _lemma_;
        else
            lemma.Empty();
        tyvi = _tyvi_;
        lopp = _lopp_;
        kigi = _kigi_;
        sl = _sl_;
        vormid = _vormid_;
        assert(ClassInvariant());
    }

    /** Initsialiseerib UTF8s algosakestest
     *
     * @param[in] _tyvi_ -- Tüvi (ei tohi olla NULL viit)
     * @param[in] _lopp_ -- Lõpp (ei tohi olla NULL viit)
     * @param[in] _kigi_ -- Liide 'ki' või 'gi' (ei tohi olla NULL viit)
     * @param[in] _sl_ -- Sõnaliigistring (st alati sl[1]==0,
     *                    ei tohi olla NULL viit))
     * @param[in] _vormid_ -- Vorm(id) (ei tohi olla NULL viit)
     * @param[in] _muuInf_ -- Vajadusel suvaline muu tekstiline info
     * @param[in] _mrg1st_ -- Vajadusel ühestaja märgend
     * @param[in] _lemma_ --  Vajadusel lemma
     */
    void Start(const char *_tyvi_, const char *_lopp_,
               const char *_kigi_, const char *_sl_, const char *_vormid_,
               const char *_muuInf_ = NULL, const char *_mrg1st_ = NULL,
               const char *_lemma_ = NULL)
    {
        assert(_tyvi_ != NULL && _lopp_ != NULL &&
               _kigi_ != NULL && _sl_ != NULL && _vormid_ != NULL);
        if (_muuInf_ != NULL)
            muuInf = _muuInf_;
        else
            muuInf.Empty();

        if (_mrg1st_ != NULL)
            mrg1st = _mrg1st_;
        else
            mrg1st.Empty();

        if (_lemma_ != NULL)
            lemma = _lemma_;
        else
            lemma.Empty();

        tyvi = _tyvi_;
        lopp = _lopp_;
        kigi = _kigi_;
        sl = _sl_;
        vormid = _vormid_;
        assert(ClassInvariant());
    }

    void Start(const S_TYYP* analStr)
    {
        assert(analStr != NULL);
        if (Strng2Strct(analStr) == false)
            throw (VEAD(ERR_X_TYKK, ERR_MINGIJAMA, __FILE__, __LINE__));
        assert(ClassInvariant());
    }

    MRFTUL_TMPL & operator=(const MRFTUL_TMPL& mrfTul)
    {
        if (this != &mrfTul)
            Start(mrfTul);
        return *this;
    }

    bool EmptyClassInvariant(void) const
    {
        return
        lemma.GetLength() == 0 &&
            tyvi.GetLength() == 0 &&
            lopp.GetLength() == 0 &&
            kigi.GetLength() == 0 &&
            sl.GetLength() == 0 &&
            vormid.GetLength() == 0 &&
            muuInf.GetLength() == 0 &&
            mrg1st.GetLength() == 0 &&
            lemma.GetLength() == 0;
    }

    bool ClassInvariant(void) const
    {
        // vähemalt sõnaliik peab olema.
        // liitsõnade ja sidekriipsuga sõnade lõpukomponendi
        // analüüsimisel võib tekkida 0-pikkusega tüvi.
        // Hiljem väljundisse tuleb tüvi esikomponentidest
        return sl.GetLength() > 0;
    }

    /** Kirjete võrdlemiseks */
    int Compare(const MRFTUL_TMPL *rec, const int sortOrder = 0) const
    {
        FSUNUSED(sortOrder);
        assert(rec != 0);
        assert(ClassInvariant());
        assert(rec->ClassInvariant());
        int ret;
        if (
            (ret = lemma.Compare(&(rec->lemma))) != 0 ||
            (ret = tyvi.Compare(&(rec->tyvi))) != 0 ||
            (ret = lopp.Compare(&(rec->lopp))) != 0 ||
            (ret = kigi.Compare(&(rec->kigi))) != 0 ||
            (ret = sl.Compare(&(rec->sl))) != 0 ||
            (ret = vormid.Compare(&(rec->vormid))) != 0 ||
            (ret = mrg1st.Compare(&(rec->mrg1st))) != 0)
        {
            return ret;
        }
        return 0;
    }

    void Stop(void)
    {
        InitClassVariables();
        assert(EmptyClassInvariant());
    }

    //=== === ===

    /** Tükeldab morf analüüsistringi klassiks. */
    void Strng2Strct(const S_TYYP &analStr)
    {
        Stop();
        //          1     2       3   4
        // ....tüvi[+lõpp].//_S_[ vorm,[vorm,]].//.
        int pos1, pos2; // pos3, pos4;
        //C_TYYP sonaLiik[2];

        if (analStr[0] != (C_TYYP) ' ' ||
            analStr[1] != (C_TYYP) ' ' ||
            analStr[2] != (C_TYYP) ' ' ||
            analStr[3] != (C_TYYP) ' ')
            throw (VEAD(ERR_X_TYKK, ERR_NOMEM, __FILE__, __LINE__, NULL, 
            "Vigane analüüsistring (4 tühikut puudu)", (const C_TYYP *)analStr));
        if(analStr[4] == (C_TYYP) ' ')
            throw (VEAD(ERR_X_TYKK, ERR_NOMEM, __FILE__, __LINE__, NULL, 
            "Vigane analüüsistring (liiga palju alustavaid tühikuid)", 
                                                    (const C_TYYP *)analStr));
        if (analStr[4] == (C_TYYP) '#' &&
            analStr[5] == (C_TYYP) '#' &&
            analStr[6] == (C_TYYP) '#' &&
            analStr[7] == (C_TYYP) '#' &&
            analStr[8] == (C_TYYP) '\0')
            throw (VEAD(ERR_X_TYKK, ERR_NOMEM, __FILE__, __LINE__, NULL, 
            "Vigane analüüsistring (#### pole lubatud)", (const C_TYYP *)analStr));
        if (analStr[analStr.GetLength()-1] != (C_TYYP) '/' &&
                                analStr[analStr.GetLength()-2] != (C_TYYP) '/' &&
                                analStr[analStr.GetLength()-3] != (C_TYYP) ' ' )
            throw (VEAD(ERR_X_TYKK, ERR_NOMEM, __FILE__, __LINE__, NULL, 
            "Vigane analüüsistring (\" //\" lõpust puudu)", (const C_TYYP *)analStr));
        
        if ((pos2 = (int) analStr.Find(EritiSobiViit(C_TYYP, " //_"))) <= 0 ||
            pos2+8 > analStr.GetLength() || analStr[pos2+5] != (C_TYYP) '_' || 
                                            analStr[pos2+6] != (C_TYYP) ' ')
            throw (VEAD(ERR_X_TYKK, ERR_NOMEM, __FILE__, __LINE__, NULL, 
            "Vigane sõnaliigiosa", (const C_TYYP *)analStr));

        tyvi = analStr.Mid(4, pos2 - 4);
        lopp.Empty();
        if ((pos1 = (int) tyvi.ReverseFind((C_TYYP) '+')) > 0)
        {
            lopp = tyvi.Mid(pos1 + 1);
            tyvi.Delete(pos1, tyvi.GetLength() - pos1);
            if (lopp.Right(2) == EritiSobiViit(C_TYYP, "ki") ||
                lopp.Right(2) == EritiSobiViit(C_TYYP, "gi"))
            {
                kigi = lopp.Right(2);
                lopp = lopp.Left(lopp.GetLength() - 2);
            }            
        }
        sl = analStr[pos2 + 4];
        if (analStr[pos2+7] == (C_TYYP) '/' && analStr[pos2 + 8] == (C_TYYP) '/')
        {
            vormid.Empty();
            return;
        }
        if(analStr[analStr.GetLength()-4] != (C_TYYP) ',' )
            throw (VEAD(ERR_X_TYKK, ERR_NOMEM, __FILE__, __LINE__, NULL, 
            "Vormiosa lõpust puudub koma", (const C_TYYP *)analStr));            
        vormid = analStr.Mid(pos2+7, analStr.GetLength()-9-pos2);
    }

    /** Paneb morf analüüsi klassist väljundstringi kokku.
     * 
     * nt peet+0 //_S_ adt, sg p, //
     * Sõltuvalt lippudest, nt kas tahetakse algvormi või mitte 
     * @param[out] xstr -- siia kirjutame stringi kujul morf vanalüüsi
     * @param[in] mrfFlags
     */
    void Strct2Strng(S_TYYP *xstr, const MRF_FLAGS *mrfFlags) const
    {
        // mätsime kokku
        assert(ClassInvariant());

        if (mrfFlags->ChkB(MF_LEMMA) == true)
        {
            *xstr += lemma;
            return;
        }
        *xstr += tyvi;
        if (mrfFlags->ChkB(MF_SPELL) == true)
        {
            if (lopp != EritiSobiViit(C_TYYP, "0"))
                *xstr += lopp;
            if (kigi.GetLength() > 0)
                *xstr += kigi;
            return;
        }
        if (lopp.GetLength() > 0)
        {
            *xstr += EritiSobiViit(C_TYYP, "+");
            if (lopp == EritiSobiViit(C_TYYP, "0"))
            {
                if (kigi.GetLength() > 0)
                    *xstr += kigi;
                else
                    *xstr += lopp;
            }
            else
            {
                *xstr += lopp;
                *xstr += kigi;
            }
        }
        else
        {
            if (kigi.GetLength() > 0)
            {
                *xstr += EritiSobiViit(C_TYYP, "+");
                *xstr += kigi;
            }
        }
        *xstr += EritiSobiViit(C_TYYP, " ");
        if (mrfFlags->ChkB(MF_YHMRG) == true && mrg1st.GetLength() > 0)
        {
            *xstr += EritiSobiViit(C_TYYP, "//");
            *xstr += mrg1st;
        }
        *xstr += EritiSobiViit(C_TYYP, "//_");
        *xstr += sl + EritiSobiViit(C_TYYP, "_ ");
        *xstr += vormid;
        *xstr += EritiSobiViit(C_TYYP, "//");
    }

    /** Lisa analüüsile lemma. */
    void LeiaLemma(void)
    {
        // Heiki tegi 2003.11.04
        assert(ClassInvariant());
        if (lemma.GetLength() > 0)
            return; // lemma juba olemas 
        lemma = tyvi;
        if (sl == EritiSobiViit(C_TYYP, "V")) // sl == LIIK_VERB
        {
            if (tyvi.GetLength() == 2)
            {
                if (tyvi == EritiSobiViit(C_TYYP, "ei"))
                    return;
            }
            else
            {
                if (TaheHulgad::OnLopus(&(tyvi), EritiSobiViit(C_TYYP, "ei")) &&
                    (TaheHulgad::OnTaht(&tyvi, tyvi.GetLength() - 3) == false))
                    return;
            }
            if (tyvi == SobiViit<C_TYYP > ("\xC3\xA4ra", FSWSTR("\x00E4ra")) ||
                tyvi == SobiViit<C_TYYP > ("\xC3\xA4r", FSWSTR("\x00E4r")))
                return; // ei ja ära/ärge jms puhul ei tee midagi
            lemma += EritiSobiViit(C_TYYP, "ma");
        }
    }

    /** ei kasutata ... */
    void Strct2Tyvestrng(S_TYYP *xstr) const
    {
        // mätsime kokku
        assert(ClassInvariant());

        *xstr += tyvi;
        if (lopp.GetLength() > 0)
        {
            *xstr += EritiSobiViit(C_TYYP, "+");
            *xstr += lopp;
        }
    }

    /** lisab stringi morf. analüüsi tüvele ette */
    void LisaTyveleEtte(const C_TYYP *xstr)
    {
        tyvi.Insert(0, xstr);
    }

    /** võtab morf. analüüsi tüvel algusest maha
     *
     * @param[in] mitu --Nii palju võtab algusest maha
     */
    void VotaTyveltEest(const int mitu)
    {
        tyvi = tyvi.Mid(mitu);
    }

    /** Lisab stringi morf. analüüsi tüvele sappa. */
    void LisaTyveleTaha(const C_TYYP *xstr)
    {
        tyvi += xstr;
    }

    /** "kigi"-liite sättimiseks
     *
     * @param[in] xstr -- MRFTUL::kigi stringi uus väärtus
     */
    void LisaLopuleTaha(const C_TYYP *xstr)
    {
        kigi = xstr;
    };

    /** suurtähelisele sõnale hoopis pärisnime sõnaliik
     * 
     * kui näiteks S, A või G liiki sõna on suuretäheline, siis on ta pigem H liiki  
     * @param alg_sl_hulk -- sisendisse sobivad sõnaliigid
     */
    void TulemNimeks(const C_TYYP *alg_sl_hulk)
    {
        if (sl.FindOneOf(alg_sl_hulk) != -1)
        {
            if (sl.FindOneOf(EritiSobiViit(C_TYYP, "G")) != -1)// nt Inglise-Prantsuse
            {
                lopp = EritiSobiViit(C_TYYP, "0");
                vormid += EritiSobiViit(C_TYYP, "sg g, ");
            }
            sl = EritiSobiViit(C_TYYP, "H");
            TaheHulgad::AlgusSuureks(&tyvi);
        }
    }

    /** sh ja zh ümberkeeramiseks oletaja puhul */
    void ShZh2Susisev(void)
    {
        TaheHulgad::Susisev2ShZh(&tyvi);
    }

    /** sh ja zh ümberkeeramiseks oletaja puhul */
    void Susisev2ShZh(void)
    {
        TaheHulgad::ShZh2Susisev(&tyvi);
    }

private:

    void InitClassVariables(void)
    {
        muuInf.Empty();
        mrg1st.Empty();
        lemma.Empty();
        tyvi.Empty();
        lopp.Empty();
        kigi.Empty();
        sl.Empty();
        vormid.Empty();
    }
};

/** Klass ühe morf. analüüsi variandi hoidmiseks 2/4 baidises unicode-kodeeringus
 */
typedef MRFTUL_TMPL<FSXSTRING, FSWCHAR> MRFTUL;

/** Klass ühe morf. analüüsi variandi hoidmiseks utf8 kodeeringus
 */
typedef MRFTUL_TMPL<PCFSAString, char> MRFTUL_UTF8;

/** Klassimall ühe sisendsõnavormi kõigi analüüsivariantide ja muu seotud info hoidmiseks
 *
 * Mallipararameetrid:
 * <ol><li> @a S_TYYP on stringitüüp @a (FSWString või @a CFSAString)
 *     <li> @a C_TYYP on sümbolitüüp @a (FSWCHAR või @a char)
 * </ol>
 */
template <class S_TYYP, class C_TYYP>
class MRFTULEMUSED_TMPL : public TMPLPTRARRAYLIN<MRFTUL_TMPL<S_TYYP, C_TYYP>, MRFTUL_TMPL<S_TYYP, C_TYYP> >
{
public:

    /** Esialgne sisendsõnavorm */
    S_TYYP s6na;

    /** Näitab kui keeruliseks analüüs/süntees läks */
    int tagasiTasand;

    /** Analüüsi korral üheks vormiks kokkuvõetud sõnade arv */
    int mitmeS6naline;

    /** mitmesõnalise verbi sünteesi puhul, kui on teada, 
     * et osad peaksid olema pöördjärjestuses, võrreldes ma-vormiga
     * (nt mitte "sisse kukkus", vaid "kukkus sisse")
     * siis keeraYmber==true 
     *  */
    bool keeraYmber;

    /** Näitab millisest moodulist tulemus saadi */
    EMRFKUST eKustTulemused;
    
    

    MRFTULEMUSED_TMPL(void)
    {
        try
        {
            InitClassVariables();
            Start(5, 5);
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** Copy-konstruktor 2/4 baidises unicode-kodeeringus argumendist */
    MRFTULEMUSED_TMPL(const MRFTULEMUSED_TMPL<FSXSTRING, FSWCHAR>& mrfTulemused)
    {
        try
        {
            InitClassVariables();
            Start(5, 5);
            Start(mrfTulemused);
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** Copy-konstruktor utf8-kodeerinus argumendist */
    MRFTULEMUSED_TMPL(const MRFTULEMUSED_TMPL<PCFSAString, char>& mrfTulemused)
    {
        try
        {
            InitClassVariables();
            Start(5, 5);
            Start(mrfTulemused);
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** Initsialiseerime 2/4 baidises unicode-kodeeringus argumendist */
    void Start(const MRFTULEMUSED_TMPL<FSXSTRING, FSWCHAR>& mrfTulemused)
    {
        Stop();
        //s6na = sptr2cptr<FSWCHAR, FSXSTRING, C_TYYP > (mrfTulemused.s6na);
        s6na = mrfTulemused.s6na;
        tagasiTasand = mrfTulemused.tagasiTasand;
        mitmeS6naline = mrfTulemused.mitmeS6naline;
        keeraYmber = mrfTulemused.keeraYmber;
        eKustTulemused = mrfTulemused.eKustTulemused;
        for (int i = 0; i < mrfTulemused.idxLast; i++)
        {
            MRFTUL_TMPL<S_TYYP, C_TYYP>* ptr =
                TMPLPTRARRAYLIN<MRFTUL_TMPL<S_TYYP, C_TYYP>, MRFTUL_TMPL<S_TYYP, C_TYYP> >::AddPlaceHolder();
            ptr->Start(*(mrfTulemused[i]));
            //if((AddClone(*mrfTulemused[i]))==NULL)
            //    throw(VEAD(ERR_X_TYKK,ERR_NOMEM,__FILE__,__LINE__,"$Revision: 1291 $"));
        }
    }

    /** Initsialiseerime utf8-kodeerignus argumendist */
    void Start(const MRFTULEMUSED_TMPL<PCFSAString, char>& mrfTulemused)
    {
        Stop();
        s6na = mrfTulemused.s6na;
        tagasiTasand = mrfTulemused.tagasiTasand;
        mitmeS6naline = mrfTulemused.mitmeS6naline;
        keeraYmber = mrfTulemused.keeraYmber;
        eKustTulemused = mrfTulemused.eKustTulemused;
        for (int i = 0; i < mrfTulemused.idxLast; i++)
        {
            MRFTUL_TMPL<S_TYYP, C_TYYP>* ptr =
                TMPLPTRARRAYLIN<MRFTUL_TMPL<S_TYYP, C_TYYP>, MRFTUL_TMPL<S_TYYP, C_TYYP> >::AddPlaceHolder();
            ptr->Start(*(mrfTulemused[i]));
            //if((AddClone(*mrfTulemused[i]))==NULL)
            //    throw(VEAD(ERR_X_TYKK,ERR_NOMEM,__FILE__,__LINE__,"$Revision: 1291 $"));
        }
    }

    /** Seda ei peaks teised kasutama. */
    void Start(const int n, const int samm)
    {
        return TMPLPTRARRAYLIN<MRFTUL_TMPL<S_TYYP, C_TYYP>,
            MRFTUL_TMPL<S_TYYP, C_TYYP> >::Start(n, samm);
    }

    /** lisab morf analüüsi variantide massiivi ühe tühja elemendi
     * 
     * @param rec
     * @return Viit vastloofud kloonile
     */
    MRFTUL_TMPL<S_TYYP, C_TYYP> *AddClone(MRFTUL_TMPL<S_TYYP, C_TYYP> &rec)
    {
        return TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::AddClone(rec);
    }

    MRFTULEMUSED_TMPL & operator=(const MRFTULEMUSED_TMPL& mrfTulemused)
    {
        if (this != &mrfTulemused)
            Start(mrfTulemused);
        return *this;
    }

    /** morf analüüsi variantide massiivi kirjete võrdlemiseks */
    int Compare(const MRFTULEMUSED_TMPL *rec, const int sortOrder = 0) const
    {
        FSUNUSED(sortOrder);
        int ret;
        assert(rec != NULL);
        if ((ret = s6na.Compare(&(rec->s6na))) != 0 ||
            (ret = tagasiTasand - rec->tagasiTasand) != 0 ||
            (ret = mitmeS6naline - rec->mitmeS6naline) != 0)
            return ret;
        if ((ret = TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::idxLast - rec->idxLast) != 0)
            return ret;
        for (int i = 0; i < TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::idxLast; i++)
        {
            assert(operator[](i) != NULL);
            if ((ret = operator[](i)->Compare((*rec)[i])) != 0)
                return ret;
        }
        return 0;
    }

    /** Võtmega võrdlemiseks */
    int Compare(const S_TYYP *key, const int sortOrder = 0) const
    {
        FSUNUSED(sortOrder);
        assert(key != NULL);
        return s6na.Compare(key);
    }

    void Stop(void)
    {
        TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::DelAll();
        InitClassVariables();
    }

    /** Tõstame morf anal tulemused sappa */
    void Move2Tail(MRFTULEMUSED_TMPL<S_TYYP, C_TYYP> *mt)
    {
        if (mt->s6na.GetLength() > 0)
        {
            s6na = mt->s6na;
            mt->s6na.Empty();
        }
        TMPLPTRARRAYSRT<MRFTUL_TMPL<S_TYYP, C_TYYP> >::Move2Tail(mt);
    };

    /** Kopeerime morf anal tulemused sappa 
     *
     * ei kasutata kunagi...
     */
    void Copy2Tail(const MRFTUL_TMPL<S_TYYP, C_TYYP> *mt)
    {
        if (mt->s6na.GetLength() > 0)
        {
            s6na = mt->s6na;
        }
        TMPLPTRARRAYSRT<MRFTUL_TMPL<S_TYYP, C_TYYP> >::Copy2Tail(mt);
    };

    /** lisa morf analüüsidesse uus variant */
    MRFTUL_TMPL<S_TYYP, C_TYYP> *Add(const C_TYYP *_tyvi_,
                                     const C_TYYP *_lopp_, const C_TYYP *_kigi_, const C_TYYP *_sl_,
                                     const C_TYYP *_vormid_)
    {
        MRFTUL_TMPL<S_TYYP, C_TYYP> *rec =
            TMPLPTRARRAYLIN<MRFTUL_TMPL<S_TYYP, C_TYYP>, MRFTUL_TMPL<S_TYYP, C_TYYP> >::AddPlaceHolder();
        if (rec == NULL)
            throw (VEAD(ERR_X_TYKK, ERR_NOMEM, __FILE__, __LINE__));
        rec->Start(_tyvi_, _lopp_, _kigi_, _sl_, _vormid_);
        return rec;
    }

    //--> MRFTUL *Sort(void);         // tulemuste sortimine
    //--> MRFTUL *SortUniq(void);     // sort&uniq

    /** leia morf. analüüsidest variant, mis on täpselt selline, nagu me juba teame
     * 
     * ei kasutata kunagi...
     * @param _tyvi_ -- tüvi
     * @param _lopp_ -- lõpp
     * @param _kigi_ liide 'ki' või 'gi'
     * @param _sl_ -- Sõnaliigistring (st alati sl[1]=='\\0')
     * @param _vormid_ -- vorm(id)
     * @param idx -- *idx on vastava analüüsivariandi indeks (kui sellist leidus)
     * @return 
     * <ul><li> ==NULL -- ei leidnud analüüside hulgast sellist
     *     <li> !=NULL -- viit vastavale analüüsivariandile
     * </ul>
     */
    MRFTUL_TMPL<S_TYYP, C_TYYP> *Get(const C_TYYP *_tyvi_, const C_TYYP *_lopp_,
                                     const C_TYYP *_kigi_, const C_TYYP *_sl_, const C_TYYP *_vormid_,
                                     int *idx) const
    {
        MRFTUL_TMPL<S_TYYP, C_TYYP> *rec1, rec0(_tyvi_, _lopp_, _kigi_, _sl_, _vormid_);

        if ((rec1 = TMPLPTRARRAYLIN<MRFTUL_TMPL<S_TYYP, C_TYYP>,
            MRFTUL_TMPL<S_TYYP, C_TYYP> >::Get(&rec0, idx)) != NULL)
            return rec1;
        return NULL;
    }

    /** leia morf. analüüsidest sellist tüvelõppu, lõppu, sõnaliiki jms sisaldava variandi nr 
     * 
     * kasutatakse mõnede ad hoc lisatavate analüüsivariantide lisamisel selle kontrollimiseks, 
     * kas too ad hoc variant on juba lisatud
     * @param _tyveL6pp_ -- tüve lõpuosa
     * @param _kigi_ -- lõpp
     * @param _sl_ -- Sõnaliigistring (st alati sl[1]=='\\0')
     * @param _vormid_ -- vorm(id)
     * @param idx -- *idx on vastava analüüsivariandi indeks (kui sellist leidus)
     * @return
     * <ul><li> ==NULL -- ei leidnud analüüside hulgast sellist
     *     <li> !=NULL -- viit vastavale analüüsivariandile
     * </ul> 
     */
    MRFTUL_TMPL<S_TYYP, C_TYYP> *GetTL(const C_TYYP *_tyveL6pp_,
                                       const C_TYYP *_lopp_, const C_TYYP *_kigi_, const C_TYYP *_sl_,
                                       const C_TYYP *_vormid_, int *idx = NULL) const
    {
        const S_TYYP c_lopp_(_lopp_);
        const S_TYYP c_kigi_(_kigi_);
        const S_TYYP c_sl_(_sl_);
        const S_TYYP c_vormid_(_vormid_);

        for (int i = 0; i < TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::idxLast; i++)
        {
            if (TaheHulgad::OnLopus(&(TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::rec[i]->tyvi), _tyveL6pp_))
                if (TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::rec[i]->lopp.Compare(&c_lopp_) == 0)
                    if (TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::rec[i]->kigi.Compare(&c_kigi_) == 0)
                        if (TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::rec[i]->sl.Compare(&c_sl_) == 0)
                            if (TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::rec[i]->vormid.Compare(&c_vormid_) == 0)
                            {
                                if (idx != NULL)
                                    *idx = i;
                                return TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::rec[i];
                            }
        }
        if (idx != NULL)
            *idx = -1;
        return NULL;
    }

    /** leia morf. analüüsidest sellist tüve sisaldava variandi nr
     * 
     * @param _tyvi_ -- sellise tüve indeksit otsime
     * @return 
     * <ul><li> ==-1 -- sellist tüve polnud
     *     <li> >=0 -- esimese sellist tüve sisaldava analüüsi indeks
     */
    int Get_tyvi(const C_TYYP *_tyvi_) const
    {
        const S_TYYP str(_tyvi_);
        for (int i = 0; i < TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::idxLast; i++)
        {
            if (TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::rec[i]->tyvi.Compare(str) == 0)
                return i;
        }
        return -1;
    }

    /** leia morf. analüüsidest sellist lõppu sisaldava variandi nr
     * 
     * @param _tyvi_ -- sellise lõpu indeksit otsime
     * @return 
     * <ul><li> ==-1 -- sellist lõppu polnud
     *     <li> >=0 -- esimese sellist lõppu sisaldava analüüsi indeks
     */
    int Get_lopp(const C_TYYP *_lopp_) const
    {
        const S_TYYP str(_lopp_);
        for (int i = 0; i < TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::idxLast; i++)
        {
            if (TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::rec[i]->lopp.Compare(str) == 0)
                return i;
        }
        return -1;
    }

    /** leia morf. analüüsidest sellist sõnaliiki sisaldava variandi nr
     * 
     * @param _sl_ -- sellise sõnaliigi indeksit otsime
     * @return 
     * <ul><li> ==-1 -- sellist sõnaliiki polnud
     *     <li> >=0 -- esimese sellist sõnaliiki sisaldava analüüsi indeks
     */
    int Get_sl(const C_TYYP *_sl_) const
    {
        const S_TYYP str(_sl_);
        for (int i = 0; i < TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::idxLast; i++)
        {
            if (TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::rec[i]->sl.Compare(str) == 0)
                return i;
        }
        return -1;
    }

    /** leia morf. analüüsidest sellist gramm. kat. sisaldava variandi nr
     * 
     * kasutatakse juhul, kui on teada, milline oleks hea analüüs (nt sg n, ma),
     * ja tuleks kontrollida, kas tulemuste hulgas selline leidub
     * @param _vormid_ -- sellise vormi indeksit otsime
     * @return 
     * <ul><li> ==-1 -- sellist vormi polnud
     *     <li> >=0 -- esimese sellist vormi sisaldava analüüsi indeks
     */
    int Get_vormid(const C_TYYP *_vormid_) const
    {
        for (int i = 0; i < TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::idxLast; i++)
        {
            if (TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::rec[i]->vormid.Find(_vormid_) != -1)
                return i;
        }
        return -1;
    }

    /** lisab morf. analüüsi väljundis stringi kõigile tüvedele ette
     * 
     * kasutatakse tüüpiliselt sel juhul, kui sõnast on midagi eesotsast eemaldatud,
     * seejärel tagumine ots ära analüüsitud ja tuleks nüüd väljund tagasi kokku panna
     * @param xstr -- selle lisame kõigile tüvedele ette
     */
    void LisaTyvedeleEtte(const C_TYYP *xstr)
    {
        for (int i = 0; i < TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::idxLast; i++)
            TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::rec[i]->LisaTyveleEtte(xstr);
    }

    /** Kustuta kõigi tüvede eest etteantud arv tähti */
    void VotaTyvedeltEest(const int mitu)
    {
        for (int i = 0; i < TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::idxLast; i++)
            TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::rec[i]->VotaTyveltEest(mitu);
    }

    /** lisab stringi kõigile morf. analüüsi lõppudele taha 
     * 
     * kasutatakse ki/gi lisamiseks morf. analüüsi puhul, kui ta enne on analüüsi tegemiseks lõpust eemaldatud
     * @param xstr -- selle lisame kõigle lõppudele taha
     */
    void LisaLoppudeleTaha(const C_TYYP *xstr)
    {
        for (int i = 0; i < TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::idxLast; i++)
            TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::rec[i]->LisaLopuleTaha(xstr);
    }

    /** keera kõigi analüüsivariantide puhul tulemus pärisnimeks
     * 
     * @param xstr
     */
    void TulemidNimeks(const C_TYYP *xstr)
    {
        for (int i = 0; i < TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::idxLast; i++)
            TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::rec[i]->TulemNimeks(xstr);
    }

    /** keera kõigi analüüsivariantide puhul lemmad suure-algustäheliseks
     * 
     */
    void AlgusedSuureks(void)
    {
        for (int i = 0; i < TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::idxLast; i++)
            TaheHulgad::AlgusSuureks(&(TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::rec[i]->tyvi));
    }

    /** Teisendab susisevaid oletamise tarbeks */
    void ShZh2Susisev(void)
    {
        for (int i = 0; i < TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::idxLast; i++)
            TaheHulgad::ShZh2Susisev(&(TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::rec[i]->tyvi));
    }

    /** Teisendab susisevaid oletamise tarbeks */
    void Susisev2ShZh(void)
    {
        for (int i = 0; i < TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::idxLast; i++)
            TaheHulgad::Susisev2ShZh(&(TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::rec[i]->tyvi));
    }

    //--> MRFTUL *Get(MRFTUL *rec, int *idx);
    //--> void    Del(const int idx);

    /** Morf analüüsistruktuur vastavalt morfi lippudele stringiks
     * 
     * Sõltub ka lippudest, nt +1
     * tulemuse näide:
     * peeti
     *   peet+0 //_S_ adt, sg p, //
     *   pida+ti //_V_ ti, //
     *
     * @param xstr
     * @param mrfFlags
     */
    void Strct2Strng(S_TYYP *xstr, const MRF_FLAGS *mrfFlags)
    {
        S_TYYP vahe;
        if (mrfFlags->ChkB(MF_YHELE_REALE) == true)
            vahe = EritiSobiViit(C_TYYP, "    ");
        else
            vahe = EritiSobiViit(C_TYYP, "\n    ");

        xstr->Empty();
        *xstr += s6na;

        if (mrfFlags->ChkB(MF_KOMA_LAHKU) == true)
            StrctKomadLahku();
        if (on_tulem())
        {
            for (int i = 0; i < TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::idxLast; i++)
            {
                if (mrfFlags->ChkB(MF_LEMMA) == true)
                {
                    if (i > 0 && operator[](i)->lemma == operator[](i - 1)->lemma)
                        continue; //korduvaid pole mõtet anda
                }
                *xstr += vahe;
                TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::rec[i]->Strct2Strng(xstr, mrfFlags);
            }
        }
        else // ei saanud tulemust
        {
            *xstr += vahe;
            *xstr += EritiSobiViit(C_TYYP, "####");
        }
        *xstr += EritiSobiViit(C_TYYP, "\n");
    }

    /** Leiab kõigi analüüsivariantide lemmad */
    void LeiaLemmad(void)
    {
        if (on_tulem())
        {
            for (int i = 0; i < TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::idxLast; i++)
                TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::rec[i]->LeiaLemma();
        }
    }

    /** Lahutab stringi algosadeks ja paned morf analüüsiklassi
     * 
     * @param xstr
     * @return 
     */
    void Strng2Strct(const S_TYYP *xstr)
    {
        int pos1, pos2, pos3;
        //Kui pole reavahetust sees, eeldame, et analüüsid on ühele reale kokku tõstetud.
        //Muidu analüüsid eraldi reidadel.
        S_TYYP eraldaja;
        if (xstr->Find((C_TYYP) '\n') < 0)
            eraldaja = EritiSobiViit(C_TYYP, "    ");
        else
            eraldaja = EritiSobiViit(C_TYYP, "\n    ");

        const int eraldajaPikkus = (int) eraldaja.GetLength();

        if ((pos1 = (int) xstr->Find((const C_TYYP *) eraldaja)) < 0)
            throw (VEAD(ERR_X_TYKK, ERR_NOMEM, __FILE__, __LINE__, NULL, 
            "Vigane analüüsistring (4 tühikut puudu)", (const C_TYYP *)*xstr));
        tagasiTasand = 0;
        mitmeS6naline = 1;
        keeraYmber = false;
        s6na = xstr->Left(pos1);
        
        pos3=0;
        while((pos2=s6na.Find(FSWCHAR(' '),pos3))>pos3)
        {
            ++mitmeS6naline;
            pos3=pos2;
        }
        S_TYYP analStr(*xstr), analStr1;
        analStr.TrimLeft();
        analStr += eraldaja;

        MRFTUL_TMPL<S_TYYP, C_TYYP> cTul;
        if(xstr->Mid(pos1) == EritiSobiViit(C_TYYP, "    ####"))
        {
            // mõistataja oli võimetu, peame ise paugust midagi leiutama
            //  loodame et morfi sõnaliik 'T' annab ühestajamärgendi 'X'
            cTul.tyvi = s6na + EritiSobiViit(C_TYYP, "+0");
            cTul.sl = EritiSobiViit(C_TYYP, "T");
            AddClone(cTul);
            return;
        }
        while ((pos2 = (int) analStr.Find((const C_TYYP *) eraldaja, 
                                            pos1 + eraldajaPikkus)) > pos1)
        {
            analStr1 = analStr.Mid(pos1, pos2 - pos1);
            analStr1.TrimLeft(EritiSobiViit(C_TYYP, "\n"));
            cTul.Strng2Strct(analStr1);
            AddClone(cTul);
            pos1 = pos2;
        }
    }
    
    /** kriipsudega sõnade analüüsitulemuse "tüve" kokkupanek 
     * 
     * @param esiKomponendid
     * @param kriips
     * @param mrfFlags
     */
    void PlakerdaKokku(MRFTULEMUSED_TMPL *esiKomponendid, const C_TYYP *kriips,
                       const MRF_FLAGS *mrfFlags)
    {
        int i;
        // tõstame tüved kokku kriipsud vahele
        if ((*esiKomponendid)[0]->lopp != EritiSobiViit(C_TYYP, "0") &&
            (*esiKomponendid)[0]->lopp.GetLength() > 0)
        {
            if (!mrfFlags->Chk(MF_SPELL)) // spellimisel ei lisa mingit eristajat
                (*esiKomponendid)[0]->LisaTyveleTaha(EritiSobiViit(C_TYYP, "+"));
            (*esiKomponendid)[0]->LisaTyveleTaha((const C_TYYP *) ((*esiKomponendid)[0]->lopp));
        }
        (*esiKomponendid)[0]->LisaTyveleTaha(kriips);
        for (i = 1; i < esiKomponendid->idxLast; i++)
        {
            (*esiKomponendid)[0]->LisaTyveleTaha((const C_TYYP *) ((*esiKomponendid)[i]->tyvi));
            if ((*esiKomponendid)[i]->lopp != EritiSobiViit(C_TYYP, "0") &&
                (*esiKomponendid)[i]->lopp.GetLength() > 0)
            {
                if (!mrfFlags->Chk(MF_SPELL)) // spellimisel ei lisa mingit eristajat
                    (*esiKomponendid)[0]->LisaTyveleTaha(EritiSobiViit(C_TYYP, "+"));
                (*esiKomponendid)[0]->LisaTyveleTaha((const C_TYYP *) ((*esiKomponendid)[i]->lopp));
            }
            (*esiKomponendid)[0]->LisaTyveleTaha(kriips);
        }

        // pistame kõigile ette
        LisaTyvedeleEtte((const C_TYYP *) ((*esiKomponendid)[0]->tyvi));
    }

    /** Kas suutis analüüsida?
     *
     * @return
     * <ul><li> true -- vähemalt üks analüüsivariant olemas.
     *     <li> false -- ei ole ühtegi analüüsivarianti
     * </ul>
     */
    inline bool on_tulem(void) const
    {
        return TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::idxLast > 0 ? true : false;
    }

    /** Indeks analüüsivariandi viidaks */
    MRFTUL_TMPL<S_TYYP, C_TYYP> * operator[] (const int idx) const
    {
        return (idx >= 0 && idx < TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::idxLast) ? TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::rec[idx] : NULL;
    }

    /** Tükelda komadega analüüsid komadeta analüüsideks */
    void StrctKomadLahku(void)
    {
        int i, last = TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::idxLast;
        bool tykeldasin = false;
        for (i = 0; i < last; i++)
        {
            int pos1, pos2, pos3;
            MRFTUL_TMPL<S_TYYP, C_TYYP>* mrfTul = operator[](i);
            S_TYYP* vormid = &(mrfTul->vormid);
            pos1 = (int) vormid->Find(EritiSobiViit(C_TYYP, ", "));
            if (pos1 > 0)
            {
                for (pos2 = pos1;
                    (pos3 = (int) vormid->Find(EritiSobiViit(C_TYYP, ", "),
                                               pos2 + 2)) > 0; pos2 = pos3)
                {
                    MRFTUL_TMPL<S_TYYP, C_TYYP>* uusMrfTul =
                        TMPLPTRARRAY<MRFTUL_TMPL<S_TYYP, C_TYYP> >::AddPlaceHolder();
                    if (uusMrfTul == NULL)
                        throw (VEAD(ERR_X_TYKK, ERR_NOMEM, __FILE__, __LINE__));
                    uusMrfTul->muuInf = mrfTul->muuInf;
                    uusMrfTul->tyvi = mrfTul->tyvi;
                    uusMrfTul->lopp = mrfTul->lopp;
                    uusMrfTul->kigi = mrfTul->kigi;
                    uusMrfTul->sl = mrfTul->sl;
                    uusMrfTul->vormid = vormid->Mid(pos2 + 2, pos3 - pos2);
                }
                if ((tykeldasin = pos2 > pos1) == true) // oli midagi tükeldada
                    mrfTul->vormid = vormid->Left(pos1 + 2);
            }
        }
        if (tykeldasin)// kui tõstsin analüüse lahku, tuleb uuesti sortida
            TMPLPTRARRAYSRT<MRFTUL_TMPL<S_TYYP, C_TYYP> >::Sort();
    }

private:

    void InitClassVariables(void)
    {
        s6na.Empty();
        tagasiTasand = -1;
        mitmeS6naline = -1;
        keeraYmber = false;
        eKustTulemused = eMRF_XX;
    }
};

typedef MRFTULEMUSED_TMPL<FSXSTRING, FSWCHAR> MRFTULEMUSED;
typedef MRFTULEMUSED_TMPL<PCFSAString, char > MRFTULEMUSED_UTF8;

#endif // !defined( CTULEM_H )



