
#if !defined( TMPLARRAY_H )
#define TMPLARRAY_H


// 2003 detsember   - algus D[123]ARRAY, SA[123]

/// @defgroup TMPLARRAY Staatiline 1-3 mõõtmeline klasside massiiv.
/// Võimaldab käsitleda ühemõõtmelist massivi kahe või kolmemõõtmelisena.
//@{

#include <assert.h>
#include <stdlib.h>

/// @file tmplarray.h
/// @brief Klasssid üüe, kahe ja kolmemõõtmelise fix pikkusega massiivi käitlemiseks.
//
/// Klassid ühe, kahe ja kolmemõõtmeliste massivide elementidele
/// mugavaks indeksi(te) kaudu ligipääsemiseks.

//-----------------------------------------------------

/// @defgroup DIM1 ühemõõtmeline staatiline massiiv.
/// @ingroup TMPLARRAY
//@{

/** Klass ühemõõtmelise massivi indeksi teisendamiseks ühemõõtmelise massiivi indeksiks.
 *
 * See klass on suuresti ainult selleks, et teha ühemõõtmelise
 * massiivi käitlemine samasuguseks kahe- ja kolmõõtmelise
 * massiivi käitlemisega.
 */
class D1ARRAY
{
public:
    /** Indeksi max suurus+1
     */
    int maxIdx1;

    D1ARRAY(void)
    {
        InitClassVariables();
    }

    /** Argumentidega konstruktor
     *
     * @param[in] _maxIdx1_ Indeksi max suurus+1
     */
    D1ARRAY(const int _maxIdx1_)
    {
        InitClassVariables();
        Start(_maxIdx1_);
    }

    /** Argumentideta konstruktori järgseks initsialiseerimiseks
     *
     * @param[in] _maxIdx1_ Indeksi max suurus+1
     */
    void Start(const int _maxIdx1_)
    {
        maxIdx1 = _maxIdx1_;
        assert(ClassInvariant());
    }

    /**  Ühemõõtmelise massiivi indeks ühemõõtmelise massiivi indeksiks
     *
     * @attention Ei kontrolli, kas indeks jääb lubatud piiridesse.
     * Seda tuleks vajadusel eraldi kontrollida @a bool @a
     * D1ARRAY::CheckIndexRange() funktsiooniga
     * @param[in] idx1 Indeks (peab olema -1 &lt; indeks &lt; @a D1ARRAY::maxIdx1)
     * @return Funktsiooni väärtuseks on argument @a idx1
     */
    inline int Index(const int idx1) const
    {
        return idx1;
    }

    bool EmptyClassInvariant(void) const
    {
        return (maxIdx1 == 0);
    }

    bool ClassInvariant(void) const
    {
        return (maxIdx1 > 0);
    }

    /** Kontrollib, kas indeks jääb lubatud piiridesse
     *
     * @param[in] idx1 Kontrollitav indeks (-1 &lt; @a idx1 &lt @a D1ARRAY::maxIdx1)
     * @return @a true kui -1 &lt; @a idx1 &lt @a D1ARRAY::maxIdx1, muidu @a false
     */
    bool CheckIndexRange(const int idx1) const
    {
        return (idx1 >= 0) &&
            (idx1 < maxIdx1);
    }

    D1ARRAY(const D1ARRAY& d1array)
    {
        *this = operator=(d1array);
    }

    D1ARRAY & operator=(const D1ARRAY& d1array)
    {
        if (this != &d1array)
            maxIdx1 = d1array.maxIdx1;
        return *this;
    }
    
    void Stop(void)
    {
        InitClassVariables();
        assert(EmptyClassInvariant());
    }

private:

    void InitClassVariables(void)
    {
        maxIdx1 = 0;
    }
};

/** Ühemõõtmeline massiiiv indeksi järgi elemendi leidmiseks
 *
 * @attention Malliparameetril @a ELEM peab olema defineeritud omistamisoperaator
 */
template <class ELEM>
class SA1 : public D1ARRAY
{
public:

    /** Tekitab tühja massiivi
     *
     * Argumentideta konstruktori korral tuleb järgmisena
     * sellest klassist väljakutsuda SA1::Start() funktsioon.
     *
     * Argumentideta konstruktor õnnestub
     * alati.
     */
    SA1(void)
    {
        InitClassVariables();
        assert(EmptyClassInvariant());
    }

    /** Tekitab ettenatud pikkusega massiivi
     *
     * @param[in] _maxIdx1_ Indeksi max suurus+1
     * @throw kui polnud piisavalt vaba mälu
     */
    SA1(const int _maxIdx1_)
    {
        try
        {
            InitClassVariables();
            Start(_maxIdx1_);
            assert(ClassInvariant());
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** Tekitab etteantud pikkusega initsialiseeritud elementidega massiivi
     *
     * @param[in] initValue Massiivi elementode algväärtus
     * @param[in] _maxIdx1_ Indeksi max suurus+1
     * @throw kui polnud piisavalt vaba mälu
     */
    SA1(const ELEM& initValue, const int _maxIdx1_)
    {
        try
        {
            InitClassVariables();
            Start(initValue, _maxIdx1_);
            assert(ClassInvariant());
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** Argumentideta konstruktori järgselt tekitab ettenatud pikkusega massiivi
     *
     * @param[in] _maxIdx1_ Indeksi max suurus+1
     * @throw kui polnud piisavalt vaba mälu
     */
    void Start(const int _maxIdx1_)
    {
        D1ARRAY::Start(_maxIdx1_);
        ptr = new ELEM[Index(_maxIdx1_)];
        assert(ClassInvariant());
    }

    /** Argumentideta konstruktori järgselt tekitab etteantud pikkusega 
     * initsialiseeritud elementidega massiivi
     *
     * @param[in] initValue Massiivi elementode algväärtus
     * @param[in] _maxIdx1_ Indeksi max suurus+1
     * @throw kui polnud piisavalt vaba mälu
     */
    void Start(const ELEM& initValue, const int _maxIdx1_)
    {
        Start(_maxIdx1_);
        int i;
        for (i = 0; i < maxIdx1; i++)
            Obj(i) = initValue;
        assert(ClassInvariant());
    }

    /** Indeksi järgi massiivi element.
     *
     * @attention Ei kontrolli, kas indeks jääb lubatud piiridesse.
     * Seda tuleks vajadusel eraldi kontrollida
     * \a bool \a D1ARRAY::CheckIndexRange() funktsiooniga.
     * @param[in] idx1 Massiivi elemendi indeks
     * @return Massiivi vastava indeksiga element
     */
    ELEM& Obj(const int idx1) const
    {
        assert(ClassInvariant());
        assert(CheckIndexRange(idx1));
        return ptr[Index(idx1)];
    }

    /** Indeksi järgi massiivi elemendi viit
     *
     * @attention Ei kontrolli, kas indeks jääb lubatud piiridesse.
     * Seda tuleks vajadusel eraldi kontrollida
     * \a bool \a D1ARRAY::CheckIndexRange() funktsiooniga.
     * @param idx1 Massiivi elemendi indeks
     * @return Massiivi vastava indeksiga elemendi viit
     */
    ELEM* Ptr(const int idx1) const
    {
        assert(ClassInvariant());
        assert(CheckIndexRange(idx1));
        return ptr + Index(idx1);
    }

    void Stop(void)
    {
        delete [] ptr;
        D1ARRAY::Stop();
        InitClassVariables();
        assert(EmptyClassInvariant());
    }

    ~SA1(void)
    {
        Stop();
    }

    bool EmptyClassInvariant(void) const
    {
        return (D1ARRAY::EmptyClassInvariant() && ptr == NULL);
    }

    /** Klassi invariant.
     *
     * @return On @a true, kui klassi muutujad omavahel kooskõlas,
     * muidu @a false.
     */
    bool ClassInvariant(void) const
    {
        return (D1ARRAY::ClassInvariant() && ptr != NULL);
    }

    SA1(const SA1& sa1)
    {
        *this = operator=(sa1);
    }

    SA1 & operator=(const SA1& sa1)
    {
        if (this != &sa1)
        {
            Stop();
            Start(sa1.maxIdx1);
            for (int i = 0; i < maxIdx1; i++)
                ptr[i] = sa1.Obj(i);
        }
        return *this;
    }

private:
    ELEM* ptr;

    void InitClassVariables(void)
    {
        ptr = NULL;
    }

};

//@} // end of  @defgroup DIM1

/// @defgroup DIM2 Kahemõõtmeline staatiline massiiv
/// @ingroup TMPLARRAY
//@{


//------------------------------------------------------

/** Klass kahemõõtmelise massiivi indeksite teisendamiseks ühemõõtmelise indeksiks
 *
 * Teisendab kaks indeksit (rida, veerg) vastavaks indeksiks
 * ühemõõtmelises massiivis.
 */
class D2ARRAY
{
public:
    /** Esimese indeksi max suurus+1
     */
    int maxIdx1;

    /** Teise indeksi max suurus+1
     */
    int maxIdx2;

    D2ARRAY(void)
    {
        InitClassVariables();
        assert(EmptyClassInvariant());
    }

    /** Argumentidega konstruktor
     *
     * @param[in] _maxIdx1_ - Esimese indeksi max suurus+1
     * @param[in] _maxIdx2_ - Teise indeksi max suurus+1
     */
    D2ARRAY(const int _maxIdx1_, const int _maxIdx2_)
    {
        InitClassVariables();
        Start(_maxIdx1_, _maxIdx2_);
        assert(ClassInvariant());
    }

    /** Initsialiseerimiseks peale argumentideta konstruktorit
     *
     * @param[in] _maxIdx1_ - Esimese indeksi max suurus+1
     * @param[in] _maxIdx2_ - Teise indeksi max suurus+1
     */
    void Start(const int _maxIdx1_, const int _maxIdx2_)
    {
        maxIdx1 = _maxIdx1_;
        maxIdx2 = _maxIdx2_;
        assert(ClassInvariant());
    }

    /** Arvutab kahemõõtmelise massiivi indeksite järgi ühemõõtmelises massiivi indeksi
     *
     * @param idx1 - Kahemõõtmelise massiivi esimene indeks (rea nr)
     * @param idx2 - Kahemõõtmelise massiivi teine indeks (veeru nr)
     * @return Vastav ühemõõtmelise massiivi indeks
     * @attention Ei kontrolli, kas etteantud indeksid jäävadlubatud piiridesse
     */
    int Index(const int idx1, const int idx2) const
    {
        return (idx1 * maxIdx2 + idx2);
    }

    bool EmptyClassInvariant(void) const
    {
        return (maxIdx1 == 0 && maxIdx2 == 0);
    }

    bool ClassInvariant(void) const
    {
        return (maxIdx1 > 0 && maxIdx2 > 0);
    }

    /** Kontrollib, kas indeksid jäävad lubatud piiridesse.
     *
     * @param[in] idx1 - Kahemõõtmelise massiivi esimene indeks (rea nr)
     * @param[in] idx2 - Kahemõõtmelise massiivi teine indeks (veeru nr)
     * @return @a true kui indeksid jäid lubatud piiridesse, muidu @a false
     */
    bool CheckIndexRange(const int idx1, const int idx2) const
    {
        return (idx1 >= 0 && idx2 >= 0) &&
            (idx1 < maxIdx1 && idx2 < maxIdx2);
    }

    D2ARRAY(const D2ARRAY& d2a)
    {
        *this = operator=(d2a);
    }

    D2ARRAY & operator=(const D2ARRAY& d2a)
    {
        maxIdx1 = d2a.maxIdx1;
        maxIdx2 = d2a.maxIdx2;
        return *this;
    }

    void Stop(void)
    {
        InitClassVariables();
        assert(EmptyClassInvariant());
    }
    
private:

    void InitClassVariables(void)
    {
        maxIdx1 = maxIdx2 = 0;
    }
};

/** Klass kahemõõtmelise massiivi indeksite järgi ühemõõtmelisest massiivist elemendi leidmiseks
 * 
 * Template'i parameetriks oleval tüübil @a ELEM peab olema
 * defineeritud omistamioperaator.
 */
template <typename ELEM>
class SA2 : public D2ARRAY
{
public:

    SA2(void) // void-konstruktor
    {
        InitClassVariables();
        assert(EmptyClassInvariant());
    }

    /** Argumentidega konstruktor
     *
     * @param[in] _maxIdx1_ - Esimese indeksi max suurus+1
     * @param[in] _maxIdx2_ - Teise indeksi max suurus+1
     */
    SA2(const int _maxIdx1_, const int _maxIdx2_)
    {
        try
        {
            InitClassVariables();
            Start(_maxIdx1_, _maxIdx2_);
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
     * @param[in] initValue - Massiivi elementide algväärtus.
     * @attention Massiivi elemendil peab olema deklareeritud omistamisoperaator.
     * @param[in] _maxIdx1_ - Esimese indeksi max suurus+1
     * @param[in] _maxIdx2_ - Teise indeksi max suurus+1
     */
    SA2(const ELEM& initValue, const int _maxIdx1_, const int _maxIdx2_)
    {
        try
        {
            InitClassVariables();
            Start(initValue, _maxIdx1_, _maxIdx2_);
            assert(ClassInvariant());
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** Initsialiseerib klassi peale argumentideta konstruktorit.
     *
     * @attention Massiivi elemendil peab olema deklareeritud omistamisoperaator.
     * @param[in] _maxIdx1_ - Esimese indeksi max suurus+1
     * @param[in] _maxIdx2_ - Teise indeksi max suurus+1
     */
    void Start(const int _maxIdx1_, const int _maxIdx2_)
    {
        assert(EmptyClassInvariant());
        D2ARRAY::Start(_maxIdx1_, _maxIdx2_);
        ptr = new ELEM[Index(_maxIdx1_, _maxIdx2_)];
        assert(ClassInvariant());
    }

    /** Initsialiseerib klassi peale argumentideta konstruktorit.
     *
     * @param[in] initValue - Massiivi elementide algväärtus.
     * @attention Massiivi elemendil peab olema deklareeritud omistamisoperaator.
     * @param[in] _maxIdx1_ - Esimese indeksi max suurus+1
     * @param[in] _maxIdx2_ - Teise indeksi max suurus+1
     */
    void Start(const ELEM& initValue, const int _maxIdx1_, const int _maxIdx2_)
    {
        SA2::Start(_maxIdx1_, _maxIdx2_);
        int i, j;
        for (i = 0; i < maxIdx1; i++)
        {
            for (j = 0; j < maxIdx2; j++)
                Obj(i, j) = initValue;
        }
        assert(ClassInvariant());
    }

    /** Kahemõõtmelise massiivi indeksite järgi ühemõõtmelisest massivist elemendi leidmine
     *
     * @attention Seda, kas indeksid jäävad lubatud piiridesse kontrollitakse @a assert()-iga
     * @param[in] idx1 - Esimene indeks (-1 &lt; idx1 &lt; D2ARRAY::maxIdx1)
     * @param[in] idx2 - Teine indeks   (-1 &lt; idx2 &lt; D2ARRAY::maxIdx2)
     * @return Indeksitele vastav massiivi element
     */
    ELEM& Obj(const int idx1, const int idx2) const
    {
        assert(ClassInvariant());
        assert(CheckIndexRange(idx1, idx2));
        return ptr[Index(idx1, idx2)];
    }

    /** Kahemõõtmelise massiivi indeksite järgi ühemõõtmelisest massivist elemendi viida leidmine
     * 
     * @attention Seda, kas indeksid jäävad lubatud piiridesse kontrollitakse @a assert()-iga
     * @param[in] idx1 - Esimene indeks (-1 &lt; idx1 &lt; D2ARRAY::maxIdx1)
     * @param[in] idx2 - Teine indeks   (-1 &lt; idx2 &lt; D2ARRAY::maxIdx2)
     * @return Indeksitele vastav massiivi elemendi viit
     */
    ELEM* Ptr(const int idx1, const int idx2) const
    {
        assert(ClassInvariant());
        assert(CheckIndexRange(idx1, idx2));
        return ptr + Index(idx1, idx2);
    }

    /** Taastab argumentideta konstruktori järgse olukorra
     */
    void Stop(void)
    {
        delete [] ptr;
        D2ARRAY::Stop();
        InitClassVariables();
        assert(EmptyClassInvariant());
    }

    ~SA2(void)
    {
        Stop();
    }

    bool EmptyClassInvariant(void) const
    {
        return (D2ARRAY::EmptyClassInvariant() && ptr == NULL);
    }

    bool ClassInvariant(void) const
    {
        return (D2ARRAY::ClassInvariant() && ptr != NULL);
    }

    SA2(const SA2& s2a)
    {
        *this = operator=(s2a);
    }

    SA2 & operator=(const SA2& s2a)
    {
        if (this != &s2a)
        {
            Stop();
            SA2::Start(s2a.maxIdx1, s2a.maxIdx2);
            int i, j;
            for (i = 0; i < maxIdx1; i++)
            {
                for (j = 0; j < maxIdx2; j++)
                    Obj(i, j) = s2a.Obj(i, j);
            }
        }
        return *this;
    }

private:
    ELEM* ptr;

    void InitClassVariables(void)
    {
        ptr = NULL;
    }
};

//@} // end of  @defgroup DIM2

/// @defgroup DIM3 Kolmemõõtmeline staatiline massiiv
/// @ingroup TMPLARRAY
//@{


//-------------------------------------------------------
/// @brief
/// Klass kolmemõõtmelise massiivi indeksi teisendamiseks
/// ühemõõtmelise massiivi indeksiks.
//
/// Arvutab kolme indeksi järgi välja vastava ühemõõtmelise 
/// massiivi indeksi

class D3ARRAY : public D2ARRAY
{
public:
    int maxIdx3; ///< Kolmanda indeksi max suurus+1.

    /// Argumentideta konstrukor.
    //
    /// Argumentideta konstruktori korral tuleb järgmisena
    /// sellest klassist väljakutsuda D3ARRAY::Start() funktsioon.
    ///
    /// Argumentideta konstruktor õnnestub
    /// alati.

    D3ARRAY(void)
    {
        InitClassVariables();
        assert(EmptyClassInvariant());
    }

    /// Argumentidega konstruktor.
    //
    /// Argumentidedega konstruktor õnnestub
    /// alati.

    D3ARRAY(
            const int _maxIdx1_, ///< Esimese indeksi max suurus+1.
            const int _maxIdx2_, ///< Teise indeksi max suurus+1.
            const int _maxIdx3_ ///< Kolmanda indeksi max suurus+1.
            )
    {
        InitClassVariables();
        Start(_maxIdx1_, _maxIdx2_, _maxIdx3_);
        assert(ClassInvariant());
    }

    /// Initsialiseerimiseks peale argumentideta konstruktorit.
    //
    /// D3ARRAY::Start() funktsioon õnnestub
    /// alati.

    void Start(
               const int _maxIdx1_, ///< Esimese indeksi max suurus+1
               const int _maxIdx2_, ///< Teise indeksi max suurus+1.
               const int _maxIdx3_ ///< Kolmanda indeksi max suurus+1.
               )
    {
        D2ARRAY::Start(_maxIdx1_, _maxIdx2_);
        maxIdx3 = _maxIdx3_;
        assert(ClassInvariant());
    }

    /// @brief Arvuta kolmemõõtmelise massiivi
    /// indeksite järgi ühemõõtmelises massiivi indeksi.
    //
    /// @attention Ei kontrolli, kas indeksid jäävad lubatud piiridesse.
    /// Seda tuleks vajadusel eraldi kontrollida
    /// \a bool \a D3ARRAY::CheckIndexRange() funktsiooniga.
    /// @return Funktsiooni väärtuseks on vastav indeks ühemõõtmelises
    /// massiivis.

    int Index(
              const int idx1, ///< Esimene indeks (-1 < esimene indeks < D2ARRAY::maxIdx1)
              const int idx2, ///< Teine indeks   (-1 < teine indeks   < D2ARRAY::maxIdx2)
              const int idx3 ///< Kolmas indeks  (-1 < kolmas indeks  < D3ARRAY::maxIdx3)
              ) const
    {
        assert(ClassInvariant());
        assert(idx1 >= 0 && idx2 >= 0 && idx3 >= 0);

        return D2ARRAY::Index(idx1, idx2) * maxIdx3 + idx3;
    }

    bool EmptyClassInvariant(void) const
    {
        return D2ARRAY::EmptyClassInvariant() &&
                                maxIdx1 == 0 && maxIdx2 == 0 && maxIdx3 == 0;
    }

    /// Klassi invariant.
    //
    /// Klassi invariant võimaldab kontrollida,
    /// kas argumentidega konstruktor õnnestus või ei
    ///
    /// @return Funktsiooni väärtus:
    /// - \a ==true: klass on OK
    /// - \a ==false: klass on vigane

    bool ClassInvariant(void) const
    {
        return D2ARRAY::ClassInvariant() &&
                                    maxIdx1 > 0 && maxIdx2 > 0 && maxIdx3 > 0;
    }

    /// Kontrollib, kas indeksid jäävad lubatud piiridesse.

    bool CheckIndexRange(
                         const int idx1, ///< Esimene indeks (-1 < esimene indeks < D2ARRAY::maxIdx1)
                         const int idx2, ///< Teine indeks   (-1 < teine indeks   < D2ARRAY::maxIdx2)
                         const int idx3 ///< Kolmas indeks  (-1 < kolmas indeks  < D3ARRAY::maxIdx3)
                         ) const
    {
        return D2ARRAY::CheckIndexRange(idx1, idx2) &&
            (idx3 >= 0 && idx3 < maxIdx3);
    }
    
    void Stop(void)
    {
        D2ARRAY::Stop();
        InitClassVariables();
        assert(EmptyClassInvariant());
    }
    
private:

    void InitClassVariables(void)
    {
        maxIdx3 = 0;
    }
    // Need on illegaliseed-{{

    D3ARRAY(const D3ARRAY&)
    {
        assert(false);
    }

    D3ARRAY & operator=(const D3ARRAY&)
    {
        assert(false);
        return *this;
    }
    // }}-Need on illegaliseed
};

/// \brief 
/// Klass kolmemõõtmelise massiivi indeksite järgi ühemõõtmeliset
/// massiivist elemendi leidmiseks

template <class ELEM>
class SA3 : public D3ARRAY
{
public:
    /// Argumentideta konstrukor.
    //
    /// Argumentideta konstruktori korral tuleb järgmisena
    /// sellest klassist väljakutsuda SA3::Start() funktsioon.
    ///
    /// Argumentideta konstruktor õnnestub
    /// alati.

    SA3(void)
    {
        InitClassVariables();
        assert(EmptyClassInvariant());
    }

    /// Argumentidega konstruktor.
    //
    /// @attention Argumentidega konstruktori korral kontrolli
    /// \a bool \a SA3::ClassInvariant()
    /// funktsiooni abil, kas konstrueerimine õnnestus.

    SA3(
        const int _maxIdx1_, ///< Esimese indeksi max suurus+1.
        const int _maxIdx2_, ///< Teise indeksi max suurus+1.
        const int _maxIdx3_ ///< Kolmanda indeksi max suurus+1.
        )
    {
        try
        {
            InitClassVariables();
            Start(_maxIdx1_, _maxIdx2_, _maxIdx3_);
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /// Argumentidega konstruktor.
    //
    /// @attention Argumentidega konstruktori korral kontrolli
    /// \a bool \a SA3::ClassInvariant()
    /// funktsiooni abil, kas konstrueerimine õnnestus.

    SA3(
        const ELEM& initValue, ///< Esimese indeksi max suurus+1.
        const int _maxIdx1_, ///< Teise indeksi max suurus+1.
        const int _maxIdx2_, ///< Teise indeksi max suurus+1.
        const int _maxIdx3_ ///< Kolmanda indeksi max suurus+1.
        )
    {
        try
        {
            InitClassVariables();
            Start(initValue, _maxIdx1_, _maxIdx2_, _maxIdx3_);
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /// Initsialiseerib klassi peale argumentideta konstruktorit.

    void Start(
               const int _maxIdx1_, ///< Esimese indeksi max suurus+1.
               const int _maxIdx2_, ///< Teise indeksi max suurus+1.
               const int _maxIdx3_ ///< Kolmanda indeksi max suurus+1.
               )
    {
        D3ARRAY::Start(_maxIdx1_, _maxIdx2_, _maxIdx3_);
        ptr = new ELEM[Index(_maxIdx1_, _maxIdx2_, _maxIdx3_)];
        assert(ClassInvariant());
    }

    /// Initsialiseerib klassi peale argumentideta konstruktorit.

    void Start(
               const ELEM& initValue, ///< Algväärtus kõigile massiivi elementidele.
               const int _maxIdx1_, ///< Esimese indeksi max suurus+1.
               const int _maxIdx2_, ///< Teise indeksi max suurus+1.
               const int _maxIdx3_ ///< Kolmanda indeksi max suurus+1.
               )
    {
        Start(_maxIdx1_, _maxIdx2_, _maxIdx3_);
        int i, j, k;
        for (i = 0; i < maxIdx1; i++)
        {
            for (j = 0; j < maxIdx2; j++)
            {
                for (k = 0; k < maxIdx3; k++)
                    Obj(i, j, k) = initValue;
            }
        }
        assert(ClassInvariant());
    }

    void Stop(void)
    {
        if (ptr != NULL)
            delete [] ptr;
        D3ARRAY::Stop();
        InitClassVariables();
        assert(EmptyClassInvariant());
    }

    ~SA3(void)
    {
        Stop();
    }

    /// Kolmemõõtmelise massiivi indeksite järgi massiivist element.
    //
    /// @attention Ei kontrolli, kas indeksid jäävad lubatud piiridesse.
    /// Seda tuleks vajadusel eraldi kontrollida
    /// \a bool \a D3ARRAY:CheckIndexRange() funktsiooniga.
    /// @return Kolmemõõtmelise massiivi indeksite järgi massiivi element.

    ELEM& Obj(
              const int idx1,
              ///< Esimene indeks.
              ///< \a -1 < esimene indeks < \a D2ARRAY::maxIdx1
              const int idx2,
              ///< Teine indeks.
              ///< \a -1 < teine indeks < \a D2ARRAY::maxIdx2
              const int idx3
              ///< Kolmas indeks.
              ///< \a -1 < kolmas indeks < \a D3ARRAY::maxIdx3
              ) const
    {
        assert(ClassInvariant());
        assert(CheckIndexRange(idx1, idx2, idx3));
        return ptr[Index(idx1, idx2, idx3)];
    }

    /// Kolmemõõtmelise massiivi indeksite järgi massiivist elemendi viit.
    //
    /// @attention Ei kontrolli, kas indeksid jäävad lubatud piiridesse.
    /// Seda tuleks vajadusel eraldi kontrollida
    /// \a bool \a D3ARRAY:CheckIndexRange() funktsiooniga.
    /// @return Kolmemõõtmelise massiivi indeksite järgi massiivi elemendi viit.

    ELEM* Ptr(
              const int idx1,
              ///< Esimene indeks.
              ///< \a -1 < esimene indeks < \a maxIdx1
              const int idx2,
              ///< Teine indeks.
              ///< \a -1 < teine indeks < \a maxIdx2
              const int idx3
              ///< Kolmas indeks.
              ///< \a -1 < kolmas indeks < \a maxIdx3
              ) const
    {
        assert(ClassInvariant());
        assert(CheckIndexRange(idx1, idx2, idx3));
        return ptr + Index(idx1, idx2, idx3);
    }

    bool EmptyClassInvariant(void) const
    {
        return (D3ARRAY::EmptyClassInvariant() && ptr == NULL);
    }

    /// Klassi invariant.
    //
    /// Klassi invariant võimaldab kontrollida,
    /// kas argumentidega konstruktor õnnestus või ei.
    ///
    /// \return Funktsiooni väärtus:
    /// - \a ==true: klass on OK
    /// - \a ==false: klass on vigane

    bool ClassInvariant(void) const
    {
        return (D3ARRAY::ClassInvariant() && ptr != NULL);
    }
private:
    ELEM* ptr;

    void InitClassVariables(void)
    {
        ptr = NULL;
    }
    // Need on illegaliseed-{{

    SA3(const SA3&)
    {
        assert(false);
    }

    SA3 & operator=(const SA3&)
    {
        assert(false);
        return *this;
    }
    // }}-Need on illegaliseed
};

//@} // end of  @defgroup DIM3

//@} // end of @defgroup TMPLARRAY



#endif
