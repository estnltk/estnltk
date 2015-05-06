#if !defined(AHEL2_H)
#define AHEL2_H

#include "post-fsc.h"
#include "ctulem.h"

/** Klassimall stringi ja täisarvulise id hoidmiseks
 *
 * Malliparameeter @a S_TYYP kuulub hulka {FSXSTRING, CFSWString}.
 * Sellistest elementidest tehtud massiiv järjestub
 * ja on kahendotsitav stringide järgi.
 */
template <typename S_TYYP>
class TSTRID
{
public:
    /** sõnaklassi numbriline id */
    int id;

    /** numbrilisele id-le vastav string. Selle järgi kahendotsitav */
    S_TYYP str;

    TSTRID(void)
    {
        InitClassVariables();
    }

    TSTRID(const TSTRID<PCFSAString>& rec)
    {
        InitClassVariables();
        Start(rec);
    }

    TSTRID(const TSTRID<FSXSTRING>& rec)
    {
        InitClassVariables();
        Start(rec);
    }

    TSTRID(const S_TYYP &_str_, const int _id_)
    {
        try
        {
            InitClassVariables();
            Start(_str_, _id_);
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    TSTRID & operator=(const TSTRID<PCFSAString>& rec)
    {
        if (((const void*) &rec) != ((const void*) this))
        {
            this->id = rec.id;
            str = rec.str;
        }
        assert(ClassInvariant());
        return *this;
    }

    TSTRID & operator=(const TSTRID<FSXSTRING>& rec)
    {
        if (((const void*) &rec) != ((const void*) this))
        {
            this->id = rec.id;
            str = rec.str;
        }
        assert(ClassInvariant());
        return *this;
    }

    /** Argumentideta konstruktori järgseks initsialiseerimiseks */
    void Start(const TSTRID<PCFSAString>& rec)
    {
        *this = operator=(rec);
        assert(ClassInvariant());
    }

    /** Argumentideta konstruktori järgseks initsialiseerimiseks */
    void Start(const TSTRID<FSXSTRING>& rec)
    {
        *this = operator=(rec);
        assert(ClassInvariant());
    }

    /** Võtmega @a str võrdlemine
     *
     * @param[in] key Võrreldava võtme viit
     * @param sortOrder Vaikimisi 0, pole kasutusel
     * @return
     * <ul><li> @a >0 kui *this > *key
     *     <li> @a ==0 kui *this == *key
     *     <li> @a &lt;0 kui *this &lt; *key
     * </ul>
     */
    int Compare(const S_TYYP* key, const int sortOrder = 0) const
    {
        FSUNUSED(sortOrder);
        assert(key != NULL);
        return str.Compare(*key);
    }

    /** Võtmega @a id võrdlemine
     *
     * @param[in] key Võrreldava võtme viit
     * @param sortOrder Vaikimisi 0, pole kasutusel
     * @return
     * <ul><li> @a >0 kui *this > *key
     *     <li> @a ==0 kui *this == *key
     *     <li> @a &lt;0 kui *this &lt; *key
     * </ul>
     */
    int Compare(const int* key, const int sortOrder = 0) const
    {
        FSUNUSED(sortOrder);
        assert(key != NULL);
        return id - *key;
    }

    /** Kirjete võrdlemine . kõigepealt @a str ja siis @a id järgi
     *
     * @param[in] key Võrreldava kirje viit
     * @param sortOrder Vaikimisi 0, pole kasutusel
     * @return
     * <ul><li> @a >0 kui *this > *key
     *     <li> @a ==0 kui *this == *key
     *     <li> @a &lt;0 kui *this &lt; *key
     * </ul>
     */
    int Compare(const TSTRID* rec, const int sortOrder = 0) const
    {
        FSUNUSED(sortOrder);
        assert(rec != NULL);
        int ret;

        if ((ret = str.Compare(rec->str)) == 0)
            ret = id - rec->id;
        return ret;
    }

    /** Taastab argumentideta kontruktori järgse seisu */
    void Stop(void)
    {
        InitClassVariables();
    }
private:

    void InitClassVariables(void)
    {
        this->id = -1;
        str.Empty();
    }

    bool ClassInvariant(void) const
    {
        return str.GetLength() > 0;
    }
};

typedef TSTRID<FSXSTRING> STRID;
typedef TSTRID<PCFSAString> STRID_UTF8;

//--------------------------------------------------------------

typedef enum
{
    A2_ALGUSEST,
    A2_JOOKSVAST,
    A2_L6PUST,
} A2_POS;

#define A2_SUVALINE_LYLI (~0)

/** Mall morf analüüsi, märgendi vms metainfo esitamiseks
 *
 * Mallipararameetrid:
 * <ul><li> Esimene @a S_TYYP on stringitüüp @a (FSXSTRING või @a PCFSAString)
 *     <li> Teine @a C_TYYP on sümbolitüüp @a (FSWCHAR või @a char)
 * </ul>
 */
template <typename S_TYYP, typename C_TYYP>
union LYLI_INF_TMPL
{
    /** Täisarvu kujul metainfo */
    int arv;

    /** Viit stringi kujul metainfole */
    S_TYYP* pStr;

    /** Viit stringile ja tema täisarvulisele IDle*/
    TSTRID<S_TYYP> *strid;

    /** Viit morf analüüsile */
    MRFTULEMUSED_TMPL<S_TYYP, C_TYYP>* pMrfAnal;
};

typedef LYLI_INF_TMPL<FSXSTRING, FSWCHAR> LYLI_INF;
typedef LYLI_INF_TMPL<PCFSAString, char > LYLI_INF_UTF8;

/** Klassimall sisend/väljundahela lüli (morf anal/tag) hoidmiseks)
 *
 * Mallipararameetrid:
 * <ul><li> Esimene @a S_TYYP on stringitüüp @a (FSXSTRING või @a PCFSAString)
 *     <li> Teine @a C_TYYP on sümbolitüüp @a (FSWCHAR või @a char)
 * </ul>
 */
template <typename S_TYYP, typename C_TYYP>
class LYLI_TMPL
{
public:
    /** Jooksva lüli kohta käivad lipud
     *
     * Kombinatsioon ::LYLI_FLAGS loendiga määratud lippidest.
     * Määratleb muuhulgas selle, mis tüüpi viita hoitakakse LYLI::ptr väljal
     */
    LYLI_FLAGS_BASE_TYPE lipp;

    /** Lüliga seotud info */
    LYLI_INF_TMPL<S_TYYP, C_TYYP> ptr;

    LYLI_TMPL(void)
    {
        InitClassVariables();
    }

    // ==konstruktorid==

    /** vt Start-funktsiooni */
    LYLI_TMPL(const int sArv, const LYLI_FLAGS_BASE_TYPE _lipp_ = PRMS_TAGSINT)
    {
        try
        {
            InitClassVariables();
            Start(sArv, _lipp_);
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** vt Start-funktsiooni */
    LYLI_TMPL(const FSXSTRING &str, const LYLI_FLAGS_BASE_TYPE _lipp_ = PRMS_SONA)
    {
        try
        {
            InitClassVariables();
            Start(str, _lipp_);
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** vt Start-funktsiooni */
    LYLI_TMPL(const FSWCHAR *str, const LYLI_FLAGS_BASE_TYPE _lipp_ = PRMS_SONA)
    {
        try
        {
            InitClassVariables();
            Start(str, _lipp_);
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** vt Start-funktsiooni */
    LYLI_TMPL(const PCFSAString &str, const LYLI_FLAGS_BASE_TYPE _lipp_ = PRMS_SONA)
    {
        try
        {
            InitClassVariables();
            Start(str, _lipp_);
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** vt Start-funktsiooni */
    LYLI_TMPL(const char *str, const LYLI_FLAGS_BASE_TYPE _lipp_ = PRMS_SONA)
    {
        try
        {
            InitClassVariables();
            Start(str, _lipp_);
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    LYLI_TMPL(const STRID &strid, const LYLI_FLAGS_BASE_TYPE _lipp_ = PRMS_SONAJAID)
    {
        try
        {
            InitClassVariables();
            Start(strid, _lipp_);

        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    LYLI_TMPL(const STRID_UTF8 &strid, const LYLI_FLAGS_BASE_TYPE _lipp_ = PRMS_SONAJAID)
    {
        try
        {
            InitClassVariables();
            Start(strid, _lipp_);

        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** Vt Start-funktsiooni */
    LYLI_TMPL(const MRFTULEMUSED &mrfAnal, const LYLI_FLAGS_BASE_TYPE _lipp_ = PRMS_MRF)
    {
        try
        {
            InitClassVariables();
            Start(mrfAnal, _lipp_);
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** Vt Start-funktsiooni */
    LYLI_TMPL(const MRFTULEMUSED_UTF8 &mrfAnal, const LYLI_FLAGS_BASE_TYPE _lipp_ = PRMS_MRF)
    {
        try
        {
            InitClassVariables();
            Start(mrfAnal, _lipp_);
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** Copy-konstruktor -- allikas LYLI(unicode) */
    LYLI_TMPL(const LYLI_TMPL<FSXSTRING, FSWCHAR> &lyli)
    {
        try
        {
            InitClassVariables();
            Start(lyli);
            assert(ClassInvariant());
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** Copy-konstruktor -- allikas LYLI_UTF8 */
    LYLI_TMPL(const LYLI_TMPL<PCFSAString, char> &lyli)
    {
        try
        {
            InitClassVariables();
            Start(lyli);
            assert(ClassInvariant());
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    // ==Start-funktsioonid==

    /** Lülisse täisarvu sisaldav TAG
     *
     * @param[in] sArv
     * @param[in] _lipp_ Vaikimisi @a PRMS_TAGSINT
     */
    void Start(const int sArv, const LYLI_FLAGS_BASE_TYPE _lipp_ = PRMS_TAGSINT)
    {
        Stop();
        assert((_lipp_ & PRMS_SARV) == PRMS_SARV);
        lipp = _lipp_;
        ptr.arv = sArv;
    }

    /** Lülisse UNICODE stringiklassist sõna (koopia)
     *
     * @param[in] str
     * @param[in] _lipp_ Vaikimisi @a PRMS_SONA
     */
    void Start(const FSXSTRING &str, const LYLI_FLAGS_BASE_TYPE _lipp_ = PRMS_SONA)
    {
        Stop();
        assert((_lipp_ & PRMS_STRKLASS) == PRMS_STRKLASS);
        lipp = _lipp_;
        ptr.pStr = new S_TYYP(str);
    }

    /** Lülisse UNICODE stringiviidast sõna (koopia)
     *
     * @param[in] str
     * @param[in] _lipp_ Vaikimisi @a PRMS_SONA
     */
    void Start(const FSWCHAR *str, const LYLI_FLAGS_BASE_TYPE _lipp_ = PRMS_SONA)
    {
        Stop();
        assert((_lipp_ & PRMS_STRKLASS) == PRMS_STRKLASS);
        lipp = _lipp_;
        ptr.pStr = new S_TYYP(str);
    }

    /** Lülisse UTF8 stringiklassist sõna (koopia)
     *
     * @param[in] str
     * @param[in] _lipp_ Vaikimisi @a PRMS_SONA
     */
    void Start(const PCFSAString &str, const LYLI_FLAGS_BASE_TYPE _lipp_ = PRMS_SONA)
    {
        Stop();
        assert((_lipp_ & PRMS_STRKLASS) == PRMS_STRKLASS);
        lipp = _lipp_;
        ptr.pStr = new S_TYYP(str);
    }

    /** Lülisse UTF8 stringiviidast sõna (koopia)
     *
     * @param[in] str
     * @param[in] _lipp_ Vaikimisi @a PRMS_SONA
     */
    void Start(const char *str, const LYLI_FLAGS_BASE_TYPE _lipp_ = PRMS_SONA)
    {
        Stop();
        assert((_lipp_ & PRMS_STRKLASS) == PRMS_STRKLASS);
        lipp = _lipp_;
        ptr.pStr = new S_TYYP(str);
    }

    /** Lülisse UNICODE stringiklassi ja numbrilist IDed sisaldav TAG (koopia)
     *
     * @param[in] strid
     * @param[in] _lipp_ Vaikimisi @a PRMS_SONAJAID
     */
    void Start(const STRID &strid, const LYLI_FLAGS_BASE_TYPE _lipp_ = PRMS_SONAJAID)
    {
        Stop();
        assert((_lipp_ & PRMS_STRID) == PRMS_STRID);
        lipp = _lipp_;
        ptr.strid = new TSTRID<S_TYYP > (strid);
    }

    /** Lülisse UTF8 stringiklassi ja numbrilist IDed sisaldav TAG (koopia)
     *
     * @param[in] strid
     * @param[in] _lipp_ Vaikimisi @a PRMS_SONAJAID
     */
    void Start(const STRID_UTF8 &strid, const LYLI_FLAGS_BASE_TYPE _lipp_ = PRMS_SONAJAID)
    {
        Stop();
        assert((_lipp_ & PRMS_STRID) == PRMS_STRID);
        lipp = _lipp_;
        ptr.strid = new TSTRID<S_TYYP > (strid);
    }

    /** Lülisse UNICODEis morfi tulemus
     *
     * @param[in] mrfTul
     * @param[in] _lipp_ Vaikimisi @a PRMS_MRF
     */
    void Start(const MRFTULEMUSED &mrfTul, const LYLI_FLAGS_BASE_TYPE _lipp_ = PRMS_MRF)
    {
        Stop();
        assert((_lipp_ & PRMS_MRF) == PRMS_MRF);
        lipp = _lipp_;
        ptr.pMrfAnal = new MRFTULEMUSED_TMPL<S_TYYP, C_TYYP > (mrfTul);
    }

    /** Lülisse UTF8sas morfi tulemus
     *
     * @param[in] mrfTul
     * @param[in] _lipp_ Vaikimisi @a PRMS_MRF
     */
    void Start(const MRFTULEMUSED_UTF8 &mrfTul, const LYLI_FLAGS_BASE_TYPE _lipp_ = PRMS_MRF)
    {
        Stop();
        assert((_lipp_ & PRMS_MRF) == PRMS_MRF);
        lipp = _lipp_;
        ptr.pMrfAnal = new MRFTULEMUSED_TMPL<S_TYYP, C_TYYP > (mrfTul);
    }

    /** Copy-konstruktor -- allikas LYLI(unicode) */
    void Start(const LYLI_TMPL<FSXSTRING, FSWCHAR> &lyli)
    {
        Stop();
        if ((lyli.lipp & PRMS_SARV) == PRMS_SARV)
        {
            Start(lyli.ptr.arv, lyli.lipp);
            return;
        }
        if ((lyli.lipp & PRMS_STRKLASS) == PRMS_STRKLASS)
        {
            Start(*lyli.ptr.pStr, lyli.lipp);
            return;
        }
        if ((lyli.lipp & PRMS_STRID) == PRMS_STRID)
        {
            Start(*lyli.ptr.strid, lyli.lipp);
            return;
        }
        if ((lyli.lipp & PRMS_MRF) == PRMS_MRF)
        {
            Start(*lyli.ptr.pMrfAnal, lyli.lipp);
            return;
        }
        assert(false);
    }

    /** Copy-konstruktor -- allikas LYLI_UTF8 */
    void Start(const LYLI_TMPL<PCFSAString, char> &lyli)
    {
        Stop();
        if ((lyli.lipp & PRMS_SARV) == PRMS_SARV)
        {
            Start(lyli.ptr.arv, lyli.lipp);
            return;
        }
        if ((lyli.lipp & PRMS_STRKLASS) == PRMS_STRKLASS)
        {
            Start(*lyli.ptr.pStr, lyli.lipp);
            return;
        }
        if ((lyli.lipp & PRMS_STRID) == PRMS_STRID)
        {
            Start(*lyli.ptr.strid, lyli.lipp);
            return;
        }
        if ((lyli.lipp & PRMS_MRF) == PRMS_MRF)
        {
            Start(*lyli.ptr.pMrfAnal, lyli.lipp);
            return;
        }
        assert(false);
    }

    //-----

    /// Omistamisoperaator

    LYLI_TMPL & operator=(const LYLI_TMPL<FSXSTRING, FSWCHAR> &lyli)
    {
        if (((const void*) this) != ((const void *) &lyli))
            Start(lyli);
        return *this;
    }

    LYLI_TMPL & operator=(const LYLI_TMPL<PCFSAString, char>& lyli)
    {
        if (((const void*) this) != ((const void *) &lyli))
            Start(lyli);
        return *this;
    }

    //--------------------------------------

    /** Taastab argumentideta konstruktori järgse seisu */
    void Stop(void)
    {
        if ((lipp & PRMS_SARV) == PRMS_SARV)
            ; // pole midagi teha
        else if ((lipp & PRMS_STRKLASS) == PRMS_STRKLASS)
            delete ptr.pStr;
        else if ((lipp & PRMS_STRID) == PRMS_STRID)
            delete ptr.strid;
        else if ((lipp & PRMS_MRF) == PRMS_MRF)
            delete ptr.pMrfAnal;
        else
            assert(EmptyClassInvariant());
        InitClassVariables();
        assert(EmptyClassInvariant());
    }

    ~LYLI_TMPL(void)
    {
        Stop();
    }

    bool ClassInvariant(void)
    {
        if ((lipp & PRMS_SARV) == PRMS_SARV)
            return true;
        if ((lipp & PRMS_STRKLASS) == PRMS_STRKLASS)
            return ptr.pStr != NULL;
        if ((lipp & PRMS_STRID) == PRMS_STRID)
            return ptr.strid != NULL;
        if ((lipp & PRMS_MRF) == PRMS_MRF)
            return ptr.pMrfAnal != NULL;
        return false;
    }

    bool EmptyClassInvariant(void)
    {
        return lipp == 0;
    }

private:

    void InitClassVariables(void)
    {
        lipp = 0;
    }

};

typedef LYLI_TMPL<FSXSTRING, FSWCHAR> LYLI;
typedef LYLI_TMPL<PCFSAString, char > LYLI_UTF8;

/** Klassimall sisend/väljundahela käitlemiseks
 *
 * Mallipararameetrid:
 * <ul><li> Esimene @a S_TYYP on stringitüüp @a (FSXSTRING või @a PCFSAString)
 *     <li> Teine @a C_TYYP on sümbolitüüp @a (FSWCHAR või @a char)
 * </ul>
 */
template <typename S_TYYP, typename C_TYYP>
class AHEL2_TMPL : public TMPLPTRARRAY<LYLI_TMPL<S_TYYP, C_TYYP> >
{
public:
    /** Jooksva ahela kohta käiv lipp, pole hetkel kasutusel */
    int ahelaLipp;

    AHEL2_TMPL(void)
    {
        try
        {
            InitClassVariables();
            assert(EmptyClassInvariant());
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    ~AHEL2_TMPL(void)
    {
        Stop();
    }

    void Stop(void)
    {
        ahelaLipp = 0;
        TMPLPTRARRAY<LYLI_TMPL<S_TYYP, C_TYYP> >::Stop();
        InitClassVariables();
        assert(EmptyClassInvariant());
    }

    /** Võtab ahelast välja indeksile vastava lüli ja tagastab selle viida
     *
     * @attention Viida saaja peab korraldama viidaga seotud mälu vabastamise
     * @param[in] idx -- Lüli indeks absoluutarvestuses (vaikimisi @a 0)
     * @return
     * <ul><li> @a !=NULL -- viit lülile
     *     <li> @a ==NULL -- ahel tühi
     * </ul>
     */
    LYLI_TMPL<S_TYYP, C_TYYP> *LyliPtrOut(int idx = 0)
    {
        if (TMPLPTRARRAY<LYLI_TMPL<S_TYYP, C_TYYP> >::idxLast == 0)
            return NULL;
        LYLI_TMPL<S_TYYP, C_TYYP> *tmp = TMPLPTRARRAY<LYLI_TMPL<S_TYYP, C_TYYP> >::rec[idx];
        TMPLPTRARRAY<LYLI_TMPL<S_TYYP, C_TYYP> >::Del(idx, true);
        return tmp;
    }

    /** Võtab ahelast välja indeksile lüli ja tagastab selle koopia
     *
     * @attention Ahelas olnud lüliga seotud mälu vabastatakse
     * @param[out] lyli
     * @param[in] idx -- Lüli indeks absoluutarvestuses (vaikimisi @a 0)
     * @return
     * <ul><li> @a ==true -- tagastas lüli koopia
     *     <li> @a ==false -- ahel tühi
     * </ul>
     */
    bool LyliCopyOut(LYLI_TMPL<S_TYYP, C_TYYP>& lyli, int idx = 0)
    {
        if (TMPLPTRARRAY<LYLI_TMPL<S_TYYP, C_TYYP> >::idxLast == 0)
            return false;
        lyli = *(TMPLPTRARRAY<LYLI_TMPL<S_TYYP, C_TYYP> >::rec[idx]);
        TMPLPTRARRAY<LYLI_TMPL<S_TYYP, C_TYYP> >::Del(idx, false);
        return true;
    }

    /** Ahelast viit etteantud parameetritega lülile, lüli jääb ahelasse
     *
     * @param[in] n -- Niimitmendat sobivate lippudega lüli otsime (vaikimisi @a 0)
     * @param[in] lipuMask -- Vaatame ainult sellise lipukombinatsiooniga lülisid (vaikimisi @a PRMS_SONA)
     * @param[out] pIdx
     * <ul><li> @a ==NULL -- Ei kasuta seda parameetrit
     *     <li> @a !=NULL
     *     <ul><li> @a *pIdx >=0 -- Etteantud tingimustele vastavat lüli indeks kõigi lülide arvestuses
     *         <li> @a *pidx == -1 -- Etteantud tingimustele vastavat lüli polnud ahelas
     *     </ul>
     * </ul>
     * @return
     * <ul><li> @a !=NULL -- Etteantud tingimustele vastavat lüli viit
     *     <li> @a ==NULL -- Etteantud tingimustele vastavat lüli polnud ahelas
     */
    LYLI_TMPL<S_TYYP, C_TYYP> *Lyli(const int n = 0,
        const LYLI_FLAGS_BASE_TYPE lipuMask = PRMS_SONA, int *pIdx = NULL)
    {
        LYLI_TMPL<S_TYYP, C_TYYP> *pLyli;
        int i, algus, cnt;
        if (pIdx)
            *pIdx = -1;
        algus = 0;
        if (n >= 0) // kammime lõpupoole
        {
            for (cnt = 0, i = algus; i < TMPLPTRARRAY<LYLI_TMPL<S_TYYP, C_TYYP> >::idxLast; i++)
            {
                pLyli = TMPLPTRARRAY<LYLI_TMPL<S_TYYP, C_TYYP> >::rec[i];
                if (lipuMask != A2_SUVALINE_LYLI)
                { // suvaline lüli ei sobi, kontrollime kas vastab lipule
                    if ((pLyli->lipp & lipuMask) != lipuMask)
                        continue; // vale lipp, ei lähe arvesse
                }
                if (cnt < n)
                {
                    cnt++;
                    continue;
                }
                assert(cnt == n);
                if (pIdx)
                    *pIdx = i;
                return pLyli;
            }
            return NULL; // etepoole kammimist ei ole veel
        }
        assert(n >= 0);
        return NULL;
    }

    /** 
     * 
     * @param abs
     * @param suht
     * @param lipuMask
     * @param pIdx
     * @return 
     */
     LYLI_TMPL<S_TYYP, C_TYYP> *LyliN(const int abs, const int suht,
            const LYLI_FLAGS_BASE_TYPE lipuMask = PRMS_SONA, int *pIdx = NULL)
    {
        assert(suht!=0);
        assert(lipuMask!=A2_SUVALINE_LYLI);
     
        LYLI_TMPL<S_TYYP, C_TYYP> *pLyli;
        int samm = suht>0 ? 1 : -1; // vaatame järgmisi/eelmisi
        int n = suht*samm; //abs väärtus
        int indeks;
        
        int cnt=0;
        for(int pos=abs+samm; (pLyli=Lyli(pos, A2_SUVALINE_LYLI, &indeks))!=NULL; 
                                                                pos += samm)
        {
            if((pLyli->lipp & lipuMask)==lipuMask && ++cnt >= n)
            {
                if(pIdx!=NULL)
                    *pIdx=pos;
                return pLyli;
            }
        }
        if (pIdx)
            *pIdx = -1;   
        return NULL;
    }   
    
    
    /** Annab stringi kandvast lülist stringi algusviida */
    const C_TYYP *LyliInf0(const int n = 0,
                           const LYLI_FLAGS_BASE_TYPE lipuMask = PRMS_SONA, int *pIdx = NULL)
    {
        assert((lipuMask & PRMS_STRKLASS) == PRMS_STRKLASS);
        LYLI_INF_TMPL<S_TYYP, C_TYYP>* ptr = LyliInf(n, lipuMask, pIdx);
        if (ptr == NULL)
            return EritiSobiViit(C_TYYP, "");
        return (const C_TYYP *) *(ptr->pStr);
    }

    /** Annab lülist viida lüli-infole */
    LYLI_INF_TMPL<S_TYYP, C_TYYP> *LyliInf(const int n = 0,
                                           const LYLI_FLAGS_BASE_TYPE lipuMask = PRMS_SONA, int *pIdx = NULL)
    {
        LYLI_TMPL<S_TYYP, C_TYYP> *pLyli = Lyli(n, lipuMask, pIdx);
        return pLyli == NULL ? NULL : &(pLyli->ptr);
    }

    /** Funktsioonimall etteantud tüüpi infoga lüli lisamiseks
     * 
     * Malliparameeter T kuulub hulka {int, S_TYYP, TSTRID<S_TYYP>, 
     * MRFTULEMUSED_TMPL<S_TYYP, C_TYYP>}
     * @param[in] t -- Lülisse selle koopia
     * @param[in] _lipp_ -- Lüli lipud
     */
    template <typename T>
    void LisaSappa(const T &t, const LYLI_FLAGS_BASE_TYPE _lipp_)
    {
        LYLI_TMPL<S_TYYP, C_TYYP> *pLyli = TMPLPTRARRAY<LYLI_TMPL<S_TYYP, C_TYYP> >::AddPlaceHolder(); // lisame sappa
        try
        {
            pLyli->Start(t, _lipp_); // initsialiseerime
        }
        catch (...)
        {
            TMPLPTRARRAY<LYLI_TMPL<S_TYYP, C_TYYP> >::Del(); // nässus, kustutame
            throw;
        }
    }

    /** Lisab sappa lüli koopia
     * 
     * @param lyli Selles koopia sappa
     */
    void LisaSappaKoopia(const LYLI_TMPL<S_TYYP, C_TYYP> &lyli)
    {
        LYLI_TMPL<S_TYYP, C_TYYP> *pLyli = TMPLPTRARRAY<LYLI_TMPL<S_TYYP, C_TYYP> >::AddPlaceHolder(); // lisame sappa
        try
        {
            pLyli->Start(lyli); // initsialiseerime
        }
        catch (...)
        {
            TMPLPTRARRAY<LYLI_TMPL<S_TYYP, C_TYYP> >::Del(); // nässus, kustutame
            throw;
        }
    }    
    
    
    /** Sõna ahelas sappa
     *
     * @param pStr
     * @param _lipp_
     * @param id
     */
    void LisaSonaSappa(const C_TYYP *pStr,
                       const LYLI_FLAGS_BASE_TYPE _lipp_ = PRMS_SONA,
                       const int id = -1)
    {
        LYLI_TMPL<S_TYYP, C_TYYP> *pLyli = TMPLPTRARRAY<LYLI_TMPL<S_TYYP, C_TYYP> >::AddPlaceHolder(); // lisame sappa
        try
        {
            pLyli->Start(pStr, _lipp_, id); // initsialiseerime
        }
        catch (...)
        {
            TMPLPTRARRAY<LYLI_TMPL<S_TYYP, C_TYYP> >::Del(); // nässus, kustutame
            throw;
        }
    }

    bool EmptyClassInvariant(void) const
    {
        return
            ahelaLipp == 0;
    }
    
    bool ClassInvariant(void) const
    {
        return
            TMPLPTRARRAY<LYLI_TMPL<S_TYYP, C_TYYP> >::ClassInvariant();
    }
    
private:

    void InitClassVariables(void)
    {
        ahelaLipp = 0;
        TMPLPTRARRAY<LYLI_TMPL<S_TYYP, C_TYYP> >::Start(0, 10);
    }    
    
    // Need kuulutame illegaalseteks-{{

    /// Illegaalne

    AHEL2_TMPL(const AHEL2_TMPL&)
    {
        assert(false);
    }

    /// illegaalne

    AHEL2_TMPL & operator=(const AHEL2_TMPL&)
    {
        assert(false);
        return *this;
    }
    // }}-Need kuulutame illegaalseteks
};

typedef AHEL2_TMPL<FSXSTRING, FSWCHAR> AHEL2;
typedef AHEL2_TMPL<PCFSAString, char > AHEL2_UTF8;





#endif
