
#if !defined( TMPLPTRSRTFND_H )
#define TMPLPTRSRTFND_H

/// @file tmplptrsrtfnd.h
/// @brief Klasssid dünaamilise viitade massiivi käitlemiseks
///
/// Klassid võimaldavad tekitada dünaamiliselt suurendatavat viitade massiivi.
/// Selliseid massiive saab kirjete järgi järjestada, neist saab  
/// (lineaarselt või kahendotsimisega) leida võtit sisaldava(id) kirje(id).

#include <assert.h>
#include "viga.h"

/** Minimaalne klass viida ümber, et garanteerida destruktoriga viida vabastamine
 *
 * Klassimalli parameetriks on viida tüüp.
 * Copy-konsturktor ja omistamisoperaator on illegaalne.
 */
template<typename T>
class VIIDAKEST
{
public:
    /** Viit */
    T* ptr;
    
    VIIDAKEST(void) : ptr(NULL)
    {
        
    }
    
    VIIDAKEST(T *p) : ptr (p)
    {
    }
    
    ~VIIDAKEST(void)
    {
        delete ptr;
    }
    
    /*T& operator=(T &p) 
    {
        if(ptr!=p)
        {
            delete ptr;
            ptr=p;
        }
        return *ptr;
    }*/
    

private:
    VIIDAKEST(const VIIDAKEST& viidaKest)
    {
        assert(false);
    }   

    VIIDAKEST& operator=(const VIIDAKEST& viidaKest) 
    {
        assert(false);
        return this;
    }
};
//---------------------------------------------------------------------------

/** Vahetab omavahel kaks viita
 * 
 * Klassimalli parameetrid
 * <ul><li> @a PTR viida tüüp </ul>
 * @param a
 * @param b
 */
template <class PTR>
void FsPtrSwap(PTR** a, PTR** b)
{
    assert(a != NULL && *a != NULL && b != NULL && *b != NULL);
    PTR* tmp = *a;
    *a = *b;
    *b = tmp;
}

//---------------------------------------------------------------------------

/** Viitade massii quicksortimiseks
 * 
 * Klassimalli parameetrid
 * <ul><li> @a REC järjestatavate kirjete tüüp </ul>
 */
template <class REC>
class TMPLPTRQSRT
{
public:
    /** Quicksordib viitade (=kirjete) massiivi
     * 
     * @param @a base viit viitade massiivile
     * @param @a num viitade massiivi pikkus
     * @param @a sortOrder järjestmisviisi määrav REC::Compare() funktsiooni parameeter
     */
    void PtrSrt(REC** base, const unsigned num, const int sortOrder = 0);

private:
    void PtrShrtSrt(REC** lo, REC** hi, const int sortOrder);
    
    /** klassikud peavad seda heaks suuruseks */
    const static unsigned int MAXTYKK = 8;
};

//realisatsioon, private:
template <class REC>
void TMPLPTRQSRT<REC>::PtrShrtSrt(REC** lo, REC** hi, const int sortOrder)
{
    REC** p;
    REC** max;

    while (hi > lo)
    {
        max = lo;
        for (p = lo + 1; p <= hi; p += 1)
        {
            assert(*p != NULL && *max != NULL);
            if ((*p)->Compare(*max, sortOrder) > 0)
            {
                max = p;
            }
        }
        FsPtrSwap(max, hi);
        hi -= 1;
    }
}

//realisatsioon, public:
template <class REC>
void TMPLPTRQSRT<REC>::PtrSrt(REC** base, const unsigned num, const int sortOrder)
{
    assert(base != NULL && num >= 0);
    REC** lo;
    REC** hi;
    REC** mid;
    REC** loguy;
    REC** higuy;
    unsigned int size;
    REC** lostk[30];
    REC** histk[30];
    int stkptr;

    if (num < 2)
        return;
    stkptr = 0;
    lo = base;
    hi = base + num - 1;
recurse:
    //size = hi - lo + 1; 
    size = (unsigned int) (hi - lo) + 1;
    if (size <= MAXTYKK)
    {
        PtrShrtSrt(lo, hi, sortOrder);
    }
    else
    {
        mid = lo + (size / 2) * 1;
        FsPtrSwap(mid, lo);
        loguy = lo;
        higuy = hi + 1;
        for (;;)
        {
            do
            {
                loguy += 1;
            }
            while (loguy <= hi && (*loguy)->Compare(*lo, sortOrder) <= 0);
            do
            {
                higuy -= 1;
            }
            while (higuy > lo && (*higuy)->Compare(*lo, sortOrder) >= 0);
            if (higuy < loguy)
                break;
            FsPtrSwap(loguy, higuy);
        }
        FsPtrSwap(lo, higuy);
        if (higuy - 1 - lo >= hi - loguy)
        {
            if (lo + 1 < higuy)
            {
                lostk[stkptr] = lo;
                histk[stkptr] = higuy - 1;
                ++stkptr;
            }
            if (loguy < hi)
            {
                lo = loguy;
                goto recurse;
            }
        }
        else
        {
            if (loguy < hi)
            {
                lostk[stkptr] = loguy;
                histk[stkptr] = hi;
                ++stkptr;
            }
            if (lo + 1 < higuy)
            {
                hi = higuy - 1;
                goto recurse;
            }
        }
    }
    --stkptr;
    if (stkptr >= 0)
    {
        lo = lostk[stkptr];
        hi = histk[stkptr];
        goto recurse;
    }
    else
        return;
}

//---------------------------------------------------------------------------

/** Funktsioon lineaarseks otsimiseks unikaalsete võtmetega viitade massiivist
 */
template <class REC, class KEY>
class TMPLPTRSEARCHLIN
{
public:

    /** Lineaarseks otsimiseks unikaalsete võtmetega viitade (=kirjete) massiivist.
     *
     * @param[in] rec Viit kirje-viitade massiivile.
     * @param[in] len Kirjeviitade massiivi pikkus.
     * @param[in] key Viit võtmele. Sellise võtmega kirjet otsime.
     * @param[out] idx Vaikimisi @a NULL-viit.
     * Kui pole @a NULL-viit siis @a -1 kui sellise võtmega kirjet polnud,
     * muidu leitud kirje indeks viitade massiivis
     * @param[in] sortOrder Võrdlusfunktsiooni parameetriks
     * @return On @a NULL kui sellise võtmega kirjet polnud,
     * muidu võtmele vastava kirje viit.
     */
    REC* LSearch(REC** rec, const int len, const KEY* key,
                            int* idx = NULL, const int sortOrder = 0) const
    {
        assert((rec == NULL && len == 0) || (rec != NULL && len >= 0)); //TODO:: asenda throw-ga
        if (rec == NULL || key == NULL)
        {
            if (idx)
                *idx = -1;
            return NULL; // polnud
        }
        for (int k = 0; k < len; k++)
        {
            if (rec[k]->Compare(key, sortOrder) == 0)
            {
                if (idx)
                    *idx = k;
                return rec[k];
            }
        }
        if (idx)
            *idx = -1;
        return NULL; // polnud
    }
};

/** Funktsioon kahendotsimiseks unikaalsete/korduvate võtmetega viitade massiivist
 * 
 * Klassimalli parameetrid:
 * <ul><li> REC -- kirje tüüp
 *     <li> KEY -- võtme tüüp
 * </ul>
 */
template <class REC, class KEY>
class TMPLPTRSEARCHBIN
{
public:
    /** Kahendotsib unikaalsete võtmetega järjestatud (viitade=kirjete) massiivist.
     *
     * Klassimalli parameetrid:
     * <ul><li> REC -- kirje tüüp
     *     <li> KEY -- võtme tüüp
     * </ul>
     *  @param[in] rec Viit kirje-viitade massiivile.
     * @param[in] len Kirjeviitade massiivi pikkus.
     * @param[in] key Viit võtmele. Sellise võtmega kirjet otsime.
     * @param[out] idx idx Vaikimisi @a NULL-viit.
     * Kui pole @a NULL-viit siis võtmele vastava kirjeviida indeks massivis
     * või kui vastavat kirjet polnud, siis mitmendaks tuleks lisada
     * @param sortOrder
     * @return On @a NULL kui sellise võtmega kirjet polnud,
     * muidu võtmele vastava kirje viit.
     */
    REC *BSearch(REC** rec, const int len, const KEY *key,
                 int* idx = NULL, const int sortOrder = 0) const
    {
        assert((rec == NULL && len == 0) || (rec != NULL && len >= 0)); //TODO:: asenda throw-ga
        if (rec == NULL || key == NULL)
        {
            if (idx)
                *idx = -1;
            return NULL; // polnud
        }
        int v = 0,
            p = len - 1,
            k = (p - v) / 2,
            n;
        // Otsime kahendtabelist.
        while (v <= p)
        {
            n = rec[k]->Compare(key, sortOrder);
            if (n > 0)
            {
                p = k - 1; // võti < kahendtabeli jooksvast võtmest
            }
            else if (n < 0)
            {
                v = k + 1; // võti > kahendtabeli jooksvast võtmest
            }
            else
            {
                if (idx) // n == 0 st oli kahendtabelis.
                    *idx = k; // võti == kahendtabeli jooksva võtmega
                return rec[k]; // I find it ;)  juhhei!
            }
            k = v + (p - v) / 2;
        }
        // Polnud kahendtabelis.
        if (idx)
            *idx = v; // niimitmendaks tuleks tuleks lisada
        return NULL; // Not found >:(
    }

    /** Leiab indeksite vahemiku, kuhu jäävad korduvate võtmetaga järjestatud
     * massiivis võtmele vastavad kirjed
     * 
     * Klassimalli parameetrid:
     * <ul><li> REC -- kirje tüüp
     *     <li> KEY -- võtme tüüp
     * </ul>
     * @param[in] rec Viit kirje-viitade massiivile.
     * @param[in] len Kirjeviitade massiivi pikkus.
     * @param[in] key Viit võtmele. Sellise võtmega kirjet otsime.
     * @param first esimese võtmele vastava kirje endeks või -1
     * @param last viimase võtmele vastava kirje indeks või -1
     * @param sortOrder
     * @return @a false - sellise võtmega kirjet polnud, true - oli vähemalt
     * üks sellise kirjega võti
     */
    bool BSearchDup(REC** rec, const int len, const KEY *key,
                    int& first, int& last, const int sortOrder = 0) const
    {
        int crnt;
        REC* recPtr = TMPLPTRSEARCHBIN<REC, KEY>::BSearch(rec, len, key,
                                                          &crnt, sortOrder);
        if (recPtr == NULL) // polnud võtmele vastavaid kirjeid
        {
            first = last = -1;
            return false;
        }
        // laiame esimese võtmele vastava kirje indeksi
        first = crnt;
        while (first > 0 && rec[first - 1]->Compare(key, sortOrder) == 0)
            --first;
        // leiame viimase võtmele vastava kirje indeksi + 1
        last = crnt;
        while (++last < len && rec[last]->Compare(key, sortOrder) == 0)
            ++last;
        
        return true;
    }
};
   

/** Funktsioonid kahendotsimiseks korduvate võtmetega viitade massiivist
 *
 * Esimene kirje leidmiseks tuleb kasutada funktsiooni BSearchFirst(),
 * järgnevad saab leida BSearchNext() abil.
 */
template <class REC, class KEY>
class TMPLPTRSEARCHBINDUP : public TMPLPTRSEARCHBIN<REC, KEY>
{
public:

    TMPLPTRSEARCHBINDUP(void) : _rec_(NULL), _len_(-1)
    {
    };

    /** Leiab korduvate võtmetega järjestatud (viitade=kirjete)
     * massiivist @a esimese võtmele vastava kirje viida.
     *
     * @param[in] rec Viit kirje-viitade massiivile
     * @param[in] len Kirjeviitade massiivi pikkus
     * @param[in] key Viit võtmele. Sellise võtmega kirjet otsime.
     * @param[out] idx Vaikimisi @a NULL-viit.
     * Kui pole @a NULL-viit siis @a -1 kui sellise võtmega kirjet polnud,
     * muidu leitud kirje indeks viitade massiivis
     * @param[in] sortOrder Võrdlusfunktsiooni parameetriks (vaikimisi @a 0)
     * @return On @a NULL kui sellise võtmega kirjet polnud,
     * muidu võtmele vastava kirje viit.
     */
    REC* BSearchFirst(REC** rec,const int len, const KEY *key, 
                                int* idx = NULL, const int _sortOrder_ = 0)
    {
        sortOrder = _sortOrder_;
        _rec_ = rec;
        _len_ = len;
        REC* recPtr = TMPLPTRSEARCHBIN<REC, KEY>::BSearch(_rec_, _len_, key, 
                                                          &crntIdx, sortOrder);
        if (recPtr == NULL)
        {
            crntIdx = -1;
            if (idx)
                *idx = -1;
            return NULL;
        }
        //while(crntIdx > 0 && recPtr->Compare(rec[crntIdx-1])==0)
        while (crntIdx > 0 && rec[crntIdx - 1]->Compare(key, sortOrder) == 0)
            crntIdx--;
        if (idx)
            *idx = crntIdx;
        return rec[crntIdx]; // esimese viit tagasi
    }

    /** Leiab korduvate võtmetega järjestatud (viitade=kirjete) massiivist
     * järgmise võtmele vastava kirje viida.
     * 
     * @param[in] key Viit võtmele. Sellise võtmega kirjet otsime.
     * @attention See peab olema sama võti, mida kasutati BSearchFirst() funktsioonis.
     * @param[out] idx Vaikimisi @a NULL-viit.
     * Kui pole @a NULL-viit siis @a -1 kui sellise võtmega kirjet polnud,
     * @return On @a NULL kui sellise võtmega kirjet polnud,
     * muidu võtmele vastava kirje viit.
     */
    REC* BSearchNext(const KEY* key, int* idx = NULL)
    {
        assert((_rec_ == NULL && _len_ == 0) || (_rec_ != NULL && _len_ >= 0)); //TODO:: asenda throw-ga
        if (_rec_ == NULL || key == NULL || crntIdx < 0)
        {
            if (idx)
                *idx = -1;
            return NULL; // polnud
        }
        assert(_rec_[crntIdx] != NULL);
        if (++crntIdx < _len_ && _rec_[crntIdx]->Compare(key, sortOrder) == 0)
        {
            if (idx)
                *idx = crntIdx;
            return _rec_[crntIdx]; // oli sama võtmega, mis eelmine
        }
        crntIdx = -1;
        if (idx)
            *idx = -1;
        return NULL;
    }

    bool EmptyClassInvariant(void) const
    {
        return _rec_ == NULL && _len_ == -1;
    };

    bool ClassInvariant(void) const
    {
        return (_rec_ == NULL && _len_ == -1) || (_rec_ != NULL && _len_ >= 0);
    };

private:
    /** Kirjveviitade massiiv */
    REC**_rec_;

    /** Kirjeviitade massiivi pikkus */
    int _len_;

    /** Jooksev indeks BSearchNext() funktsiooni tarbeks */
    int crntIdx; ///< jooksev indeks BSearchNext() funktsiooni tarbeks
    int sortOrder;

    /** Illegaalne */
    TMPLPTRSEARCHBINDUP(TMPLPTRSEARCHBINDUP&)
    {
        assert(false);
    }

    /** Illegaalne */
    TMPLPTRSEARCHBINDUP & operator=(const TMPLPTRSEARCHBINDUP&)
    {
        assert(false);
        return *this;
    }
};

//---------------------------------------------------------------------------

/**  Klass dünaamilise viitade massiivi käsitlemiseks.
 *
 * Klass võimaldab indeksi järgi kirjeid lisada, kustutada ja otsida.
 * Kirjel peavad olema defineeritud funktsioonid REC::Start(const REC &rec)
 * ja REC::REC(void)
 */
template <class REC>
class TMPLPTRARRAY
{
public:
    /** 2in1 - argumentideta ja argumentidetega konstruktor
     *
     * @param[in] _idxMax_ Viitade massivi esialgne suurus.
     * @param[in] _idxStep_ Sellise sammuga kasvatame viitade massiivi,
     * kui vabast ruumist puudu tuleb.
     */
    TMPLPTRARRAY(const int _idxMax_ = 0, const int _idxStep_ = 0)
    {
        try
        {
            InitClassVariables();
            Start(_idxMax_, _idxStep_);
        }
        catch(...)
        {
            Stop();
            throw;
        }
    };

    /** Initsialisserimiseks peale argumentideta konstruktorit.
     *
     * @throw Kui mingi jama.
     * @param[in] _idxMax_ Viitade massivi esialgne suurus.
     * @param[in] _idxStep_ Sellise sammuga kasvatame viitade massiivi,
     * kui vabast ruumist puudu tuleb.
     */
    void Start(const int _idxMax_, const int _idxStep_);

    /** Indeks kirje viidaks.
     *
     * @param idx Otsitava kirje indeks.
     * @return Vastava indeksiga kirje viita massiivist, muidu @a NULL
     */
    REC * operator[] (const int idx) const
    {
        return (idx >= 0 && idx < idxLast) ? rec[idx] : NULL;
    };

    /** Lisab klooni massiivi.
     *
     * @param rec Kloonib tabelisse sellise kirje, st massiivi lisatatakse kirje @a koopia.
     * @param idx Niimitmendaks lisame, vaikimisi lõppu (~0)
     * @return Tekitatud klooni viit (pole kunagi NULL)
     */
    REC *AddClone(const REC &rec,const int idx = ~0);

    /** Lisab massiivi 'tühja' kirje (kohahoidja).
     *
     * @param[in] idx Niimitmendaks lisame, vaikimisi lõppu (~0)
     * @return Viit loodud 'kohahoidjale'.
     * @throw VEAD, ....
     */
    REC* AddPlaceHolder(const int idx = ~0);

    /** Lisab kirjeviida
     *
     * @attention Vajadusel suurendab sammu võtta massiivi pikkust, 
     * et viit ära mahuks. Kui massiivi suurendamine ebaõnnestus (throw),
     * siis viidale kutustakse välja destuktor.    
     * @param[in] pRec Viit lisatavale kirjele.
     * Ei tohi olla viit staatilistele andmetele, sest vabastatakse destruktoris.
     * @param idx Niimitmendaks lisame, vaikimisi lõppu (~0)
     * @return Viit lisatud kirjele.
     */
    REC* AddPtr(REC* pRec,const int idx = ~0);

    /** Lisab kloonimise teel kirjed massiivi sappa.
     *
     * Sappa lisatud kirjate järjekord muutub
     *  (esimene viimaseks, teine eelviimaseks jne)
     * @param[in] Kloonitavate kirjete massiiv.
     * @throw VEAD, ....
     */
    void Copy2Tail(const TMPLPTRARRAY<REC>* array);

    /** Tõstab kirjeviidad ümber ühest massiivist teise sappa.
     *
     * Sappa tõstetud kirjate järjekord muutub
     * (esimene viimaseks, teine eelviimaseks jne)
     * @param[in] array Ümbertõstetavate viitade massiiv.
     * @throw VEAD, ...
     */
    void Move2Tail(TMPLPTRARRAY<REC>* array);

    /** Kustutab kirje massiivist
     *
     * @return Kui kustutas @a true, kui sellise indeksiga kirjet polnud @a false
     * @param[in] idx Niimitmendaks kustutame, vaikimisi viimase (~0)
     * @param[in] ptrOnly Vaikmisi @a false, kustutab massiivist viida ja vabastab mälu.
     * Kui @a true, siis kustutab ainult massiivist viida.
     */
    bool Del(const int idx = ~0,const bool ptrOnly = false);

    /** Kustutab massiivist kõik kirjed
     *
     * @param[in] ptrOnly Vaikimisi @a false vabastab mälu ka.
     * Kui  @a true jätab viidatava mälu vabastamata.
     */
    void DelAll( const bool ptrOnly = false);

    /** Suurendab etteantud sammu võrra viitade massiivi pikkust */
    void InCrease(void);

    // bool DeCrease(void); // ==true:lõikas paraja(ma)ks; ==false: ei saanud lühendatatud

    ~TMPLPTRARRAY(void)
    {
        Stop();
    }; // assert( !ClassInvriant() );


    /** Argumentidega konstruktori ja Start() järgne invariant */
    bool ClassInvariant(void) const;

    /** Argumentideta konstruktori ja Stop()  järgne invariant */
    bool EmptyClassInvariant(void) const;

    /** Viit viitade massiivi algusele */
    REC** rec;
    
    /** Sellise sammuga kasvatame vajadusel massiivi suuremaks */
    int idxStep;
    
    /** Hetkel mahub massiivi maksimaalselt niipalju viitasid */
    int idxMax;
    
    /** Niipalju on hetkel massiivis tegelikult viitasid */
    int idxLast;

    /** Vabastab mälu ja taastab argumentideta konstruktori järgse seisu */
    void Stop(void);
private:

    void InitClassVariables(void)
    {
        rec = NULL;
        idxStep = idxMax = idxLast = 0;
    }

    // Need on illegaliseed-{{

    TMPLPTRARRAY(TMPLPTRARRAY&)
    {
        assert(false);
    }

    TMPLPTRARRAY & operator=(const TMPLPTRARRAY&)
    {
        assert(false);
        return *this;
    }
    // }}-Need on illegaliseed

};

template <class REC>
void TMPLPTRARRAY<REC>::Start(const int _idxMax_, const int _idxStep_)
{
    Stop();
    if (_idxMax_ > 0) // argumentidega konstruktor
    {
        if ((rec = (REC **) calloc(_idxMax_, (sizeof (REC *)))) == NULL)
        {
            throw VEAD(ERR_X_TYKK, ERR_NOMEM, __FILE__, __LINE__);
        }
        idxMax = _idxMax_;
        idxLast = 0;
        assert(ClassInvariant());
    }
    idxStep = _idxStep_;
    assert(idxStep >= 0); // argumentideta konstruktor
}

template <class REC>
REC* TMPLPTRARRAY<REC>::AddClone(const REC& rec, const int idx)
{
    REC* pRec = AddPlaceHolder(idx);
    pRec->Start(rec);
    return pRec;
}

template <class REC>
REC* TMPLPTRARRAY<REC>::AddPlaceHolder(const int idx)
{
    return AddPtr(new REC, idx);
}

// private
template <class REC>
REC* TMPLPTRARRAY<REC>::AddPtr(REC* pRec,const int idx)
{
    assert(idx <= idxLast);
    assert(ClassInvariant() || EmptyClassInvariant());
    if (pRec == NULL)
        throw VEAD(ERR_X_TYKK, ERR_NOMEM, __FILE__, __LINE__);
    if (idxLast >= idxMax)
    {
        VIIDAKEST<REC> kest(pRec);
        InCrease();
        kest.ptr=NULL;    
    }
    if (idx == ~0)
    {
        rec[idxLast++] = pRec;
        return pRec;
    }
    else
    {
        memmove(rec + idx + 1, rec + idx, (idxLast - idx) * sizeof (REC*));
        idxLast++;
        rec[idx] = pRec;
    }
    assert(ClassInvariant());
    return pRec;
}

template <class REC>
void TMPLPTRARRAY<REC>::Copy2Tail(const TMPLPTRARRAY<REC>* array)
{
    int i;
    while ((i = array->idxLast - 1) >= 0)
        TMPLPTRARRAY<REC>::AddClone(*(array->rec[i]));
}

template <class REC>
void TMPLPTRARRAY<REC>::Move2Tail(
                                  TMPLPTRARRAY<REC>* array)
{
    int i;
    while ((i = array->idxLast - 1) >= 0)
    {
        TMPLPTRARRAY<REC>::AddPtr(array->rec[i]);
        array->Del(i, true); // kustutame vanast massiivist ainult viida
    }
}

template <class REC>
bool TMPLPTRARRAY<REC>::Del(const int idx, const bool ptrOnly)
{
    assert(ClassInvariant());
    if (idxLast == 0)
        return false; // juba tühjaks tehtud
    if (idx != ~0 && idx >= idxLast)
        return false; // piiridest väljas

    if (idx == ~0 || idx + 1 == idxLast) // kustutame viimase
    {
        --idxLast;
        if (ptrOnly == false)
            delete rec[idxLast];
        assert(ClassInvariant());
        rec[idxLast] = NULL;
        return true;
    }
    if (ptrOnly == false)
        delete rec[idx]; // kustutame esimese/keskelt
    idxLast--;
    memmove(rec + idx, rec + idx + 1, sizeof (REC*)*(idxLast - idx));
    rec[idxLast] = NULL;
    assert(ClassInvariant());
    return true;
}

template <class REC>
void TMPLPTRARRAY<REC>::DelAll(const bool ptrOnly) // vaikimisi kustutame kirje ka
{
    while (Del(~0, ptrOnly) == true)
        ;
}

template <class REC>
void TMPLPTRARRAY<REC>::InCrease(void)
{
    assert(ClassInvariant() || EmptyClassInvariant());
    assert(idxStep > 0); // peab olema kasvatatav
    REC** tmp;

    if (rec == NULL)
    {
        assert(idxMax == 0);
        tmp = (REC**) malloc(sizeof (REC*) * idxStep);
    }
    else
    {
        tmp = (REC**) realloc(rec, sizeof (REC*) * (idxMax + idxStep));
    }
    if (tmp == NULL)
        throw VEAD(ERR_X_TYKK, ERR_NOMEM, __FILE__, __LINE__);
    rec = tmp;
    idxMax += idxStep;

    assert(ClassInvariant());
}

template <class REC>
void TMPLPTRARRAY<REC>::Stop(void)
{
    for (int i = 0; i < idxLast; i++)
    {
        if (rec[i])
            delete rec[i];
    }
    if (rec)
        free(rec);
    InitClassVariables();
    assert(EmptyClassInvariant());
}

template <class REC>
bool TMPLPTRARRAY<REC>::ClassInvariant(void) const
{
    bool ret =
        //(rec != NULL && idxStep >= 0 && idxMax > 0 && idxLast >=0 && idxLast <= idxMax);
        (rec != NULL && idxMax > 0 && idxLast >= 0 && idxStep >= 0 && idxMax >= idxLast) ||
        (rec == NULL && idxMax == 0 && idxLast == 0 && idxStep >= 0);
    return ret;
}

template <class REC>
bool TMPLPTRARRAY<REC>::EmptyClassInvariant(void) const
{
    return
    (rec == NULL && idxStep == 0 && idxMax == 0 && idxLast == 0);
}

//---------------------------------------------------------------------------

/** Klass sorditava dünaamiline viitade massiivi käsitlemiseks
 * 
 * Klassimalli parameeter 
 * <ul><li> @a REC -- kirje tüüp </ul>
 * 
 * Klass võimaldab:
 * <ul><li> indeksi järgi - lisada, kustutada, otsida.
 *     <li> massiivi - kirjete järgi järjestada ja kustutada korduvad järjestikused kirjed.
 * </ul>
 * Kirjel peavad olema defineeritud funktsioonid:
 * <ul><li> kirjega võrdlemiseks meetod int REC::Compare(const REC *rec)
 *     <li> kirje kloonimiseks (copy-konstruktor): void REC::Start(const REC &rec)
 *     <li> argumentideta konstrukor REC::REC(void)
 * </ul>
 * @n Näiteks:
 * @code
 * class EXAMPLE {
 *   int key;  // võti
 *   int data; // info
 *   EXAMPLE(void) { key=data=0; }
 *   bool Start(const EXAMPLE& rec) { key=rec.key; data=rec.data; return true; }
 *   int Compare(const KEY *keyPtr) { assert(keyPtr!=NULL); return key - *keyPtr; }
 *   int Compare(const REC *recPtr) { 
 *     assert(recPtr!=NULL);
 *     int cmpRes=Compare(&(recPtr->key)); // kõigepealt võtmeid
 *     if(cmpRes==0) // võrdsete võtmete korral muid asju
 *       cmpRes=data-recPtr->data;
 *     return cmpRes;
 *     }
 *   };
 * @endcode
 */
template <class REC>
class TMPLPTRARRAYSRT : public TMPLPTRARRAY<REC>, public TMPLPTRQSRT<REC>
{
public:

    /** 2in1 - argumentideta ja argumentidetega konstruktor
     * 
     * @param _idxMax_ -- Viitadev massivi algsuurus (vaikimisi 0)
     * @param _idxStep_ -- Viitade massiiv kasvab sellise sammuga (vaikimisi 0)
     */
    TMPLPTRARRAYSRT(const int _idxMax_ = 0, const int _idxStep_ = 0)
    : TMPLPTRARRAY<REC>(_idxMax_, _idxStep_)
    {
    };

    /** Quicksordib kirjed.
     */
    void Sort(const int sortOrder = 0)
    {
        assert(TMPLPTRARRAY<REC>::ClassInvariant());
        TMPLPTRQSRT<REC>::PtrSrt(TMPLPTRARRAY<REC>::rec, TMPLPTRARRAY<REC>::idxLast, sortOrder);
    };
    
    /** Kustutab järjestikused korused
     * 
     * @param @a sortOrder -- vaikimisi 0
     */
    void Uniq(const int sortOrder = 0);

    /** Quicksordib kirjed ja kustutab korduvad kirjed
     *
     * @param sortOrder Vaikimisi 0
     */
    void SortUniq(const int sortOrder = 0);

    /** Argumentideta konstruktori abil starditud klassi invariant */
    bool EmptyClassInvariant(void) const
    {
        return TMPLPTRARRAY<REC>::EmptyClassInvariant();
    }

    /** Argumentidega starditud klassi invariant */
    bool ClassInvariant(void) const
    {
        return TMPLPTRARRAY<REC>::ClassInvariant();
    }

private:
    /// Illegaalne

    TMPLPTRARRAYSRT(TMPLPTRARRAYSRT&)
    {
        assert(false);
    }

    /// Illegaalne

    TMPLPTRARRAYSRT & operator=(const TMPLPTRARRAYSRT&)
    {
        assert(false);
        return *this;
    }
};

template <class REC>
void TMPLPTRARRAYSRT<REC>::Uniq(const int sortOrder)
{
    for (int i = TMPLPTRARRAY<REC>::idxLast - 1; i > 0; i--)
    {
        int j;
        for (j = i; j > 0 &&
            TMPLPTRARRAY<REC>::rec[i]->Compare(TMPLPTRARRAY<REC>::rec[j - 1], sortOrder) == 0;)
        {
            delete TMPLPTRARRAY<REC>::rec[--j];
        }
        if (j < i)
        {
            memmove(TMPLPTRARRAY<REC>::rec + j,
                    TMPLPTRARRAY<REC>::rec + i, sizeof (REC*)*(TMPLPTRARRAY<REC>::idxLast - i));
            TMPLPTRARRAY<REC>::idxLast -= i - j;
            i = j;
        }
    }
    //for(int x=0; x<TMPLPTRARRAY<REC>::idxLast-2; x++)
    //{
    //assert(TMPLPTRARRAY<REC>::rec[x]->Compare(TMPLPTRARRAY<REC>::rec[x+1])!=0);
    //}
}

template <class REC>
void TMPLPTRARRAYSRT<REC>::SortUniq(const int sortOrder)
{
    Sort(sortOrder);
    Uniq(sortOrder);
}

//---------------------------------------------------------------------------

/** Klass lineaarselt otsitava ja sorditava unikaalsete võtmetega
 * dünaamilise viitade massiivi massiivi käsitlemiseks.
 *
 * Klassimalli parameeter 
 * <ul><li> @a REC -- kirje tüüp 
 *     <li> @a KEY -- võtme tüüp
 * </ul>
 * 
 * Klass võimaldab:
 * <ul><li> indeksi järgi - lisada, kustutada, otsida.
 *     <li> massiivi - kirjete järgi järjestada ja kustutada korduvad järjestikused kirjed.
 *     <li> Võtme järgi - lineaarselt otsides leida sobiva kirje indeks või viit
 * </ul>
 * 
 * Kirjel peavad olema defineeritud funktsioonid:
 * <ul><li> võtmega võrdlemiseks meetod int REC::Compare(const KEY *key)
 *     <li> kirjete võrdlemiseks meetod int REC::Compare(const REC *rec)
 *     <li> kirje kloonimiseks (copy-konstruktor) meetod: void REC::Start(const REC &rec)
 *     <li> argumentideta konstrukor REC::REC(void)
 * </ul>
 * 
 * Näiteks:
 * @code
 * class EXAMPLE {
 *   int key;  // võti
 *   int data; // info
 *   EXAMPLE(void) { key=data=0; }
 *   bool Start(const EXAMPLE& rec) { key=rec.key; data=rec.data; return true; }
 *   int Compare(const KEY *keyPtr) { assert(keyPtr!=NULL); return key - *keyPtr; }
 *   int Compare(const REC *recPtr) { 
 *     assert(recPtr!=NULL);
 *     int cmpRes=Compare(&(recPtr->key)); // kõigepealt võtmeid
 *     if(cmpRes==0) // võrdsete võtmete korral muid asju
 *       cmpRes=data-recPtr->data;
 *     return cmpRes;
 *     }
 *   };
 * @endcode
 */
template <class REC, class KEY>
class TMPLPTRARRAYLIN : public TMPLPTRARRAYSRT<REC>, public TMPLPTRSEARCHLIN<REC, KEY>
{
public:
    /** 2in1 - argumentideta ja argumentidetega konstruktor
     * 
     * @param _idxMax_ -- Viitadev massivi algsuurus (vaikimisi 0)
     * @param _idxStep_ -- Viitade massiiv kasvab sellise sammuga (vaikimisi 0)
     */
    TMPLPTRARRAYLIN(const int _idxMax_ = 0, const int _idxStep_ = 0) : 
                                TMPLPTRARRAYSRT<REC>(_idxMax_, _idxStep_)
    {
    };

    /** Leiab lineaarselt otsides võtme järgi kirje indeksi ja viida
     * 
     * @param @a key -- otsitav võti
     * @param idx Vaikimisi NULL
     * @param sortOrder
     * @return 
     * <ul><li> NULL -- sellist polnud, *idx==-1
     *     <li> viit leitud kirjele, *idx on leitud kirje indeks viitade massiivis
     * </ul>
     */
    REC* Get(const KEY* key, int* idx = NULL, const int sortOrder = 0) const
    {
        return TMPLPTRSEARCHLIN<REC, KEY>::LSearch(TMPLPTRARRAYSRT<REC>::rec, 
                            TMPLPTRARRAYSRT<REC>::idxLast,key, idx, sortOrder);
    };

    /** Võti massiivi indeksina
     * 
     * @param key -- selle järgi otsime
     * @return Kirje viit, kui selline oli, muidu NULL
     */
    REC * operator[] (const KEY* key) const
    {
        int idx;
        return TMPLPTRSEARCHLIN<REC, KEY>::LSearch(TMPLPTRARRAY<REC>::rec, 
                TMPLPTRARRAY<REC>::idxLast, key, &idx) == true ? 
                                        TMPLPTRARRAY<REC>::rec[idx] : NULL;
    }

    /** Argumentideta konstruktori abil starditud klassi invariant */
    bool EmptyClassInvariant(void) const
    {
        return TMPLPTRARRAYSRT<REC>::EmptyClassInvariant();
    }

    /** Argumentidega starditud klassi invariant */
    bool ClassInvariant(void) const
    {
        return TMPLPTRARRAYSRT<REC>::ClassInvariant();
    }
private:
    /// Illegaalne

    TMPLPTRARRAYLIN(TMPLPTRARRAYLIN&)
    {
        assert(false);
    }

    /// Illegaalne

    TMPLPTRARRAYLIN & operator=(const TMPLPTRARRAYLIN&)
    {
        assert(false);
        return *this;
    }
};

//---------------------------------------------------------------------------

/// @brief Klass kahendotsitava unikaalsete võtmetega dünaamilise
/// viitade massiivi massiivi käsitlemiseks.
//
/// Klass võimaldab:
/// - indeksi järgi:
///     -# lisada,
///     -# kustutada,
///     -# otsida.
/// - massiivi:
///     -# kirjete järgi järjestada
///     -# kustutada korduvad järjestikused kirjed.
/// - võtme järgi kahendotsides leida sobiva võtmega:
///     -# kirje indeks
///     -# kirje viit
///
/// Kirjel peavad olema defineeritud funktsioonid:
/// - võtmega võrdlemiseks: \a int \a REC::Compare(const KEY *key)
/// - kirjega võrdlemiseks: \a int \a REC::Compare(const REC *rec)
/// - kirje kloonimiseks (sisuliselt copy-konstruktor): \a bool \a REC::Start(const REC &rec)
/// - argumentideta konstrukor:     \a REC::REC(void)
/// @n Näiteks:
/// @code
/// class EXAMPLE
///   {
///   int key;  // võti
///   int data; // info
///   EXAMPLE(void) { key=data=0; }
///   bool Start(const EXAMPLE& rec) { key=rec.key; data=rec.data; return true; }
///   int Compare(const KEY* keyPtr) { assert(keyPtr!=NULL); return key - *keyPtr; }
///   int Compare(const REC* recPtr) 
///     { 
///     assert(recPtr!=NULL);
///     int cmpRes=Compare(&(recPtr->key)); // kõigepealt võtmeid
///     if(cmpRes==0) // võrdsete võtmete korral muid asju
///       cmpRes=data-recPtr->data;
///     return cmpRes;
///     }
///   };
/// @endcode

template <class REC, class KEY>
class TMPLPTRARRAYBIN : public TMPLPTRARRAYSRT<REC>, TMPLPTRSEARCHBIN<REC, KEY>
{
public:

    TMPLPTRARRAYBIN(const int _idxMax_ = 0, const int _idxStep_ = 0) : 
                                TMPLPTRARRAYSRT<REC>(_idxMax_, _idxStep_)
    {
    };

    
    /** Leiab kahendotsides võtme järgi kirje indeksi ja viida
     * 
     * @return 
     * <ul><li> @a ==NULL polnud sellise võtmega kirjet. Et säiliks 
     * kirjete järjestus, lisa uus kirje kohale @a *idx
     *     <li> @a !=NULL viit vastava võtmega kirjele massiivis. @a *idx on
     * vastava kirje indeks massiivis
     * </ul> 
     * @param key Võti, seda otsime
     * @param idx Vaikimisi NULL-viit
     * @param sortOrder Vaikimisi 0
     */
    REC* Get(const KEY* key, int* idx = NULL, const int sortOrder = 0) const
    {
        return TMPLPTRSEARCHBIN<REC, KEY>::BSearch(TMPLPTRARRAY<REC>::rec,
                              TMPLPTRARRAY<REC>::idxLast, key, idx, sortOrder);
    };
    
    /** Leiab indeksite vahemiku järjestatud massiivis, kuhu jäävad etteantud
     * võtmega kirjed
     * 
     * @param key -- otsitav võti
     * @param first -- esimese võtmele vastav kirje indeks, -1 kui võtmele 
     * vastavaid kirjeid polnud
     * @param last -- viimase võtmele vastava kirje indeks+1, -1 kui võtmele 
     * vastavaid kirjeid polnud 
     * @param sortOrder -- vaikimisi 0
     * @return @a false - sellise võtmega kirjeid polnud, @a true - leidis 
     * vähemalt ühe kirjele vastava võtme
     */
    bool Get(const KEY* key, int& first, int& last, const int sortOrder = 0) const
    {
        return TMPLPTRSEARCHBIN<REC, KEY>::BSearchDup(TMPLPTRARRAY<REC>::rec, 
                    TMPLPTRARRAY<REC>::idxLast, key, first, last, sortOrder);
    }
    
    /**  Leiab kahendotsides võtme järgi kirje indeksi
     *
     * @param key Viit kahendotsitavale võtmele.
     * @param sortOrder Vaikimisi @a 0.
     * @return On @a -1 kui võtit ei leitud, muidu kirje indeks massiivis.
     */
    int GetIdx(const KEY* key, const int sortOrder = 0) const
    {
        int idx;
        return TMPLPTRSEARCHBIN<REC, KEY>::BSearch(TMPLPTRARRAY<REC>::rec,
           TMPLPTRARRAY<REC>::idxLast, key, &idx, sortOrder) == NULL ? -1 : idx;
    };

    /** Leiab kahendotsides võtme viida järgi kirje viida
     *
     * @param key Viit kahendotsitavale võtmele.
     * @return On @a NULL kui sellist võtit ei leidunud,
     * muidu võtmele vastava kirje viit
     */
    REC * operator[] (const KEY* key) const
    {
        return TMPLPTRSEARCHBIN<REC, KEY>::BSearch(TMPLPTRARRAY<REC>::rec,
                                       TMPLPTRARRAY<REC>::idxLast, key, NULL);
    };

    /** Leiab indeksi järgi kirje viida
     *
     * @param idx Otsitava kirje indeks viitade massiivis
     * @return On @a NULL kui sellist võtit ei leidunud,
     * muidu võtmele vastava kirje viit
     */
    REC * operator[] (const int idx) const
    {
        return idx >= 0 && idx < TMPLPTRARRAY<REC>::idxLast ? TMPLPTRARRAY<REC>::rec[idx] : NULL;
    };

    bool EmptyClassInvariant(void) const
    {
        return TMPLPTRARRAYSRT<REC>::EmptyClassInvariant();
    }

    bool ClassInvariant(void) const
    {
        return TMPLPTRARRAYSRT<REC>::ClassInvariant();
    }
private:
    // Need on illegaliseed-{{

    TMPLPTRARRAYBIN(TMPLPTRARRAYBIN&)
    {
        assert(false);
    }

    TMPLPTRARRAYBIN & operator=(const TMPLPTRARRAYBIN&)
    {
        assert(false);
        return *this;
    }
    // }}-Need on illegaliseed

};

//---------------------------------------------------------------------------

/// \brief Klass kahendotsitava korduvate võtmetega dünaamilise
/// viitade massiivi massiivi käsitlemiseks.
//
/// Klass võimaldab:
/// - indeksi järgi:
///     -# lisada,
///     -# kustutada,
///     -# otsida.
/// - massiivi:
///     -# kirjete järgi järjestada
///     -# kustutada korduvad järjestikused kirjed.
/// - võtme järgi kahendotsides leida sobiva võtmega:
///     -# kirje indeks
///     -# kirje viit
///
/// Kirjel peavad olema defineeritud funktsioonid:
/// - võtmega võrdlemiseks: \a int \a REC::Compare(const KEY *key)
/// - kirjega võrdlemiseks: \a int \a REC::Compare(const REC *rec)
/// - kirje kloonimiseks (sisuliselt copy-konstruktor): \a bool \a REC::Start(const REC &rec)
/// - argumentideta konstrukor:     \a REC::REC(void)
/// @n Näiteks:
/// @code
/// class EXAMPLE
///   {
///   int key;  // võti
///   int data; // info
///   EXAMPLE(void) { key=data=0; }
///   bool Start(const EXAMPLE& rec) { key=rec.key; data=rec.data; return true; }
///   int Compare(const KEY* keyPtr) { assert(keyPtr!=NULL); return key - *keyPtr; }
///   int Compare(const REC* recPtr) 
///     { 
///     assert(recPtr!=NULL);
///     int cmpRes=Compare(&(recPtr->key)); // kõigepealt võtmeid
///     if(cmpRes==0) // võrdsete võtmete korral muid asju
///       cmpRes=data-recPtr->data;
///     return cmpRes;
///     }
///   };
/// @endcode

template <class REC, class KEY>
class TMPLPTRARRAYBINDUP : public TMPLPTRARRAYSRT<REC>, public TMPLPTRSEARCHBINDUP<REC, KEY>
{
public:
    TMPLPTRARRAYBINDUP(const int _idxMax_ = 0, const int _idxStep_ = 0) : 
                                    TMPLPTRARRAYSRT<REC>(_idxMax_, _idxStep_)
    {
        keyPtr = NULL;
    }

    /** Leiab korduvate võtmetega järjestatud massiivist
     * esimese võtmele vastava kirje viida.
     *
     * @return
     * <ul><li> !=NULL -- Viit esimesele soovitud võtmega kirjele.
     *     <li> ==NULL -- Sellise võtmega kirjet polnud.
     */
    REC* Get(const KEY* key, const int sortOrder = 0)
    {
        keyPtr = key;
        return TMPLPTRSEARCHBINDUP<REC, KEY>::BSearchFirst(TMPLPTRARRAY<REC>::rec, 
                            TMPLPTRARRAY<REC>::idxLast, key, NULL, sortOrder);
    }

    /// @brief Leiab korduvate võtmetega järjestatud massiivist
    /// \b järgmise võtmele vastava kirje.
    //
    /// @return
    /// - \a !=NULL Viit järjekordsele soovitud võtmega kirjele.
    /// - \a ==NULL Pole rohkem sellise võtmega kirjeid.

    REC* GetNext(
                 const KEY *key
                 ///< Otsitava kirje võti.
                 ///< @attention Peab olema sama võti,
                 ///< mida kasutati Get() funktsioonis.
                 )
    {
        return TMPLPTRSEARCHBINDUP<REC, KEY>::BSearchNext(key, NULL);
    }

    /// @brief Leiab korduvate võtmetega järjestatud massiivist
    /// \b järgmise võtmele vastava kirje.
    //
    /// @return
    /// - \a !=NULL Viit järjekordsele soovitud võtmega kirjele.
    /// - \a ==NULL Pole rohkem sellise võtmega kirjeid.

    REC* GetNext(void)
    {
        return TMPLPTRSEARCHBINDUP<REC, KEY>::BSearchNext(keyPtr, NULL);
    }

    /// Argumentideta konstruktori abil starditud klassi invariant
    //
    /// @return
    /// - @a ==true OK
    /// - @a ==false Mingi jama

    bool EmptyClassInvariant(void) const
    {
        return TMPLPTRARRAYSRT<REC>::EmptyClassInvariant();
    }

    /// Argumentidega starditud klassi invariant
    //
    /// @return
    /// - @a ==true OK
    /// - @a ==false Mingi jama

    bool ClassInvariant(void) const
    {
        return TMPLPTRARRAYSRT<REC>::ClassInvariant() && TMPLPTRSEARCHBINDUP<REC, KEY>::ClassInvariant();
    }
private:
    const KEY* keyPtr;
    // Need on illegaliseed-{{

    TMPLPTRARRAYBINDUP(TMPLPTRARRAYBINDUP&)
    {
        assert(false);
    }

    TMPLPTRARRAYBINDUP & operator=(const TMPLPTRARRAYBINDUP&)
    {
        assert(false);
        return *this;
    }
    // }}-Need on illegaliseed
};

//---------------------------------------------------------

/// Klass kahendotsitav massiiviga, säilitab sortimiseelsed indeksid
//
/// Klass võimaldab:
/// - kirjeid \b sortimiseelse indeksi järgi:
///     -# lisada,
///     -# kustutada,
///     -# otsida.
/// - massiivi:
///     -# kirjete järgi järjestada
///     -# kustutada korduvad järjestikused kirjed.
/// - võtme järgi kahendotsides leida sobiva võtmega:
///     -# kirje \b sortimiseelse indeksi
///     -# kirje viit
///
/// Kirjel peavad olema defineeritud funktsioonid:
/// - võtmega võrdlemiseks: \a int \a REC::Compare(const KEY *key)
/// - kirjega võrdlemiseks: \a int \a REC::Compare(const REC *rec)
/// - kirje kloonimiseks (sisuliselt copy-konstruktor): \a bool \a REC::Start(const REC &rec)
/// - argumentideta konstrukor:     \a REC::REC(void)
/// @n Näiteks:
/// @code
/// class EXAMPLE
///   {
///   int key;  // võti
///   int data; // info
///   EXAMPLE(void) { key=data=0; }
///   bool Start(const EXAMPLE& rec) { key=rec.key; data=rec.data; return true; }
///   int Compare(const KEY *keyPtr) { assert(keyPtr!=NULL); return key - *keyPtr; }
///   int Compare(const REC *recPtr) 
///     { 
///     assert(recPtr!=NULL);
///     int cmpRes=Compare(&(recPtr->key)); // kõigepealt võtmeid
///     if(cmpRes==0) // võrdsete võtmete korral muid asju
///       cmpRes=data-recPtr->data;
///     return cmpRes;
///     }
///   };
/// @endcode

template <class REC, class KEY>
class TMPLPTRARRAYBIN2 : public TMPLPTRARRAYBIN<REC, KEY>
{
public:
    /// Argumentideta konstruktor

    TMPLPTRARRAYBIN2(void)
    {
        preSortOrder = NULL;
        postIdx2preIdx = NULL;
    }

    ~TMPLPTRARRAYBIN2(void)
    {
        if (preSortOrder)
            delete [] preSortOrder;
        if (postIdx2preIdx)
            delete [] postIdx2preIdx;
    }

    /// Järjestab massiivi elementide (=kirjete) järgi
    //
    /// Kirjetel säilivad järjestamise eelsed indeksid.
    /// @throw
    /// VEAD, ...

    void Sort(const int sortOrder = 0)
    {
        if (preSortOrder != NULL)
        {
            delete [] preSortOrder;
            preSortOrder = NULL;
        }
        if (postIdx2preIdx)
        {
            delete [] postIdx2preIdx;
            postIdx2preIdx = NULL;
        }
        preSortOrder = new REC* [TMPLPTRARRAY<REC>::idxLast];
        int i;
        for (i = 0; i < TMPLPTRARRAY<REC>::idxLast; i++)
        {
            preSortOrder[i] = TMPLPTRARRAYBIN<REC, KEY>::operator[](i);
        }
        TMPLPTRARRAYBIN<REC, KEY>::Sort(sortOrder);
        postIdx2preIdx = new int [TMPLPTRARRAY<REC>::idxLast];
        int j;
        for (i = 0; i < TMPLPTRARRAY<REC>::idxLast; i++)
        {
            for (j = 0; j < TMPLPTRARRAY<REC>::idxLast; j++)
            {
                postIdx2preIdx[i] = -1;
                if (TMPLPTRARRAY<REC>::rec[i] == preSortOrder[j])
                {
                    postIdx2preIdx[i] = j;
                    break;
                }
            }
            assert(j < TMPLPTRARRAY<REC>::idxLast);
        }
    }

    /// Kirje (järjestamiseelne) indeks kirje viidaks
    //
    /// @return
    /// - \a !=NULL Viit n�utud indeksiga kirjele.
    /// - \a ==NULL Sellise indeksiga kirjet polnud.

    REC * operator[](
        const int idx ///< Otsitava kirje indeks.
        ) const
    {
        return (preSortOrder != NULL && idx >= 0 && idx < TMPLPTRARRAY<REC>::idxLast)
            ? preSortOrder[idx] : NULL;
    }

    /// Võti kirje viidaks ja (järjestamiseelseks) indeksiks
    //
    /// @return
    /// - \a !=NULL: sobiva võtmega kirje viit, \a *idx on kirje
    /// (järjestamise eelne) indeks.
    /// - \a ==NULL: sellise võtmega kirjet polnud

    REC* Get(
             const KEY* key, ///< Otsitava kirje võti
             int* idx = NULL,
             ///< Kui \a idx==NULL, siis seda parameetrit ignoreerime. @n
             ///< Kui \a idx!=0 ja sellise võtmega kirje leidus,
             ///< siis \a *idx on võrdne selle kirje sortimiseelse indeksiga.
             const int sortOrder = 0
             ) const
    {
        REC* pRec = NULL;

        pRec = TMPLPTRARRAYBIN<REC, KEY>::Get(key, idx, sortOrder);
        if (pRec && idx)
        {
            *idx = PostIdx2preIdx(*idx);
        }
        return pRec;
    };

    /// Võti kirje (järjestamiseelseks) indeksiks.
    //
    /// @return
    /// - \a >=0 Kirje (järjestamise eelne) indeks.
    /// - \a ==-1 Sellise võtmega kirjet polnud.

    int GetIdx(
               const KEY* key, ///< Otsitava kirje võti.
               const int sortOrder = 0
               ) const
    {
        int idx;
        REC* rec = TMPLPTRARRAYBIN<REC, KEY>::Get(key, &idx, sortOrder);
        return rec == NULL ? -1 : PostIdx2preIdx(idx);
    };

    /// Argumentideta konstruktori abil starditud klassi invariant
    //
    /// @return
    /// - @a ==true OK
    /// - @a ==false Mingi jama

    bool EmptyClassInvariant(void) const
    {
        return TMPLPTRARRAYBIN<REC, KEY>::EmptyClassInvariant();
    }

    /// Argumentidega starditud klassi invariant
    //
    /// @return
    /// - @a ==true OK
    /// - @a ==false Mingi jama

    bool ClassInvariant(void) const
    {
        return TMPLPTRARRAYBIN<REC, KEY>::ClassInvariant();
    }
private:
    REC** preSortOrder;
    int* postIdx2preIdx;

    int PostIdx2preIdx(const int idx) const
    {
        return postIdx2preIdx[idx];
    }
    // Need on illegaliseed-{{

    TMPLPTRARRAYBIN2(TMPLPTRARRAYBIN2&)
    {
        assert(false);
    }

    TMPLPTRARRAYBIN2 & operator=(const TMPLPTRARRAYBIN2&)
    {
        assert(false);
        return *this;
    }
    // }}-Need on illegaliseed
};

//---------------------------------------------------------------------------

/** Kahe võtmega kirjete massiiv, esimese järgi lineaarselt, teise järgi kahendotsitav
 * 
 * @attention Kehendotsimine toimub unikalsete võtmetega massiivist.
 * Klassimalli parameetrid:
 * <ul><li> @a REC massiivi elemendit tüüp
 *     <li> @a KEY4LSEARCH võti massiivist lineaarseks otsimiseks
 *     <li> @a KEY4BSEARCH võti massiivist kahendaotsimiseks
 * </ul>
 */
template <typename REC, typename KEY4LSEARCH, typename KEY4BSEARCH>
class TMPLPTRARRAYLINBIN : 
                            public TMPLPTRARRAYSRT<REC>,
                            public TMPLPTRSEARCHLIN<REC, KEY4LSEARCH>,
                            public TMPLPTRSEARCHBIN<REC, KEY4BSEARCH>
{
public:

    /** Konstruktor
     *
     * @param[in] idxMax Viitade massiivi algne suurus (vaikimisi @a 0).
     * @param[in] idxStep Vajadusel suureneb viitade massiiv sellise sammuga
     * (vaikimisi @a 0).
     * Kui @a 0 siis pole dünaamiliselt suurendatav.
     */
    TMPLPTRARRAYLINBIN(const int idxMax = 0, const int idxStep = 0)
    //: TMPLPTRARRAYSRT<REC>(idxMax, idxStep)
    {
        InitClassVariables();
        TMPLPTRARRAYSRT<REC>(idxMax, idxStep);
    }

    /** Leiab kahendotsides võtmele vastava kirje viida (ja indeksi)
     *
     * @param[in] key4bsearch Viit võtmele, mille järgi kahendotsitakse
     * @param[out] idx Vaikimisi  @a NULL-viit. Kui on @a NULL-viit,
     * siis seda parameetrit ignoreeritakse.
     * Muidu võtmele vastava kirje indeks või mitmendaks tuleks lisada,
     * et säiliks kirjete järjestatus.
     * @param sortOrder Vaikimisi @a 0, ignoreerime
     * @return On @a NULL kui võtmele vastavat kirjet polnud,
     * muidu viit vastavale kirjele.
     */
    REC* Get(const KEY4BSEARCH* key4bsearch, int* idx = NULL,
             const int sortOrder = 0) const
    {
        return TMPLPTRSEARCHBIN<REC, KEY4BSEARCH>::BSearch(TMPLPTRARRAY<REC>::rec,
                        TMPLPTRARRAY<REC>::idxLast, key4bsearch, idx, sortOrder);
    }

    /** Võtme järgi kahendotsimine
     *
     * @param[in] key4bsearch Viit kahendotsitavle võtmele
     * @return On @a NULL kui võtmele vastavat kirjet polnud,
     * muidu viit vastavale kirjele.
     */
    REC* operator[](const KEY4BSEARCH* key4bsearch) const
    {
        return Get(key4bsearch);
    }

    /** Leiab lineaarselt otsides võtmele vastava kirje viida (ja indeksi)
     *
     * @param[in] key4lsearch Viit võtmele, mille järgi lineaarselt otsitakse
     * @param[out] idx Vaikimisi  @a NULL-viit. Kui on @a NULL-viit,
     * siis seda parameetrit ignoreeritakse.
     * Muidu võtmele vastava kirje indeks või mitmendaks tuleks lisada,
     * et säiliks kirjete järjestatus.
     * @param sortOrder Vaikimisi @a 0, ignoreerime
     * @return On @a NULL kui võtmele vastavat kirjet polnud,
     * muidu viit vastavale kirjele.
     */
    REC* Get(const KEY4LSEARCH* key4lsearch, int* idx = NULL,
             const int sortOrder = 0) const
    {
        return TMPLPTRSEARCHLIN<REC, KEY4LSEARCH>::LSearch(TMPLPTRARRAY<REC>::rec,
                        TMPLPTRARRAY<REC>::idxLast, key4lsearch, idx, sortOrder);
    }

    /** Võtme järgi lineaarne otsimine
     *
     * @param[in] key4lsearch Viit kahendotsitavle võtmele
     * @return On @a NULL kui võtmele vastavat kirjet polnud,
     * muidu viit vastavale kirjele.
     */
    REC* operator[](const KEY4LSEARCH* key4lsearch) const
    {
        return Get(key4lsearch);
    }
    
private:
    void InitClassVariables(void)
    {
        
    }
    
    /** Copy-construktor on antud juhul illegaalne
     */
    TMPLPTRARRAYLINBIN(const TMPLPTRARRAYLINBIN*)
    {
        assert(false);
    }

    /** Omistamisoperaator on antud juhul illegaalne
     */
    TMPLPTRARRAYLINBIN& operator=(const TMPLPTRARRAYLINBIN*)
    {
        assert(false);
        return *this;
    }
};

#endif


