

#if !defined( LOEFAILIST_H )
#define LOEFAILIST_H

#include "post-fsc.h"
#include "ahel2.h"

/** Kooditabeli teisendusega I/O klass */
class SISSEVALJA : public CPFSFile
{
public:

    SISSEVALJA(void)
    {
        InitEmptyClassVariables();
    }

    /** Sisend-väljundfaili avamine
     * 
     * 
     * @param[in] fileName -- Avatava faili nimi
     * @param[in] pmode -- Avamisviis, vt @a ::fopen() funktsiooni kirjeldust
     * @param[in] _codePage_ -- Avatava faili kooditabel
     * @param[in] path -- Kui @a path!=NULL, siis nendest kataloogidest otsime teisendustabelit
     * sisaldavat faili @a "sgml-uc-cnv.txt
     * @param[in] _ignoramp_ -- (vaikimisi @a false)
     * Kui @a _codePage_==PFSCP_HTMLEXT ja toimub failist lugemine
     * <ul>
     * <li> @a _ignoramp_==false -- Ampersand peab alustama lubatud hulka 
     *      kuuluvat SGML olemit. Kõik tekstis ampersandina mõeldud ampersandid
     *      peavad olema esitatud SGML olemina ("&amp;").
     * <li> @a _ignoramp_==true -- Ampersand väljaspool olemeid on lubatud
     * </ul>
     * @param[in] _autosgml_ -- (vaikimisi @a false)
     * Kui @a _codePage_==PFSCP_HTMLEXT ja toimub
     * <ul> 
     * <li> failist lugemine
     *   <ul> <li> @a _autosgml_==true -- lubatud SGML olemite hulga moodustavad
     *             failis @a sgml-uc-cnv.txt loetletud olemid ja olemid kujul &amp;kümnendkood;
     *        <li> @a _autosgml_==false -- lubatud SGML olemite hulga moodustavad ainult
     *             failis @a sgml-uc-cnv.txt loetletud olemid
     *   </ul>
     * </li>
     * <li> faili kirjatamine
     *   <ul> <li> @a _autosgml_==false -- ainult failis @a sgml-uc-cnv.txt loetletud
     *             UNICODEi sümbolid vastavateks SGML olemiteks, ülejäänud
     *             mitte-ASCII sümbolid annavad vea
     *        <li> @a _autosgml_==true -- failis @a sgml-uc-cnv.txt loetletud
     *             UNICODEi sümbolid teisendatakse vastavateks SGML olemiteks,
     *             ülejäänud mitte-ASCII sümbolid &amp;kümnendkood; kujul SGML olemiteks
     *   </ul> 
     * </li>
     * </ul>
     */
    SISSEVALJA(const CFSFileName& fileName, const FSTCHAR* pmode,
               const PFSCODEPAGE _codePage_, const FSTCHAR* path = NULL,
               const bool _ignoramp_ = false, const bool _autosgml_ = false)
    {
        try
        {
            InitEmptyClassVariables();
            Start(fileName, pmode, _codePage_, path, _ignoramp_, _autosgml_);
            // Jama korral Throw()
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** Sisend-väljundfaili avamine
     * 
     * @param[in] pfile -- Kasutame juba avatud faili
     * @param[in] pmode -- Avamisviis, vt @a ::fopen() funktsiooni kirjeldust
     * @param[in] _codePage_ -- Avatava faili kooditabel
     * @param[in] path -- Kui @a path!=NULL, siis nendest kataloogidest otsime teisendustabelit
     * sisaldavat faili @a "sgml-uc-cnv.txt
     * @param[in] _ignoramp_ -- (vaikimisi @a false)
     * Kui @a _codePage_==PFSCP_HTMLEXT ja toimub failist lugemine
     * <ul>
     * <li> @a _ignoramp_==false -- Ampersand peab alustama lubatud hulka 
     *      kuuluvat SGML olemit. Kõik tekstis ampersandina mõeldud ampersandid
     *      peavad olema esitatud SGML olemina ("&amp;").
     * <li> @a _ignoramp_==true -- Ampersand väljaspool olemeid on lubatud
     * </ul>
     * @param[in] _autosgml_ -- (vaikimisi @a false)
     * Kui @a _codePage_==PFSCP_HTMLEXT ja toimub
     * <ul> 
     * <li> failist lugemine
     *   <ul> <li> @a _autosgml_==true -- lubatud SGML olemite hulga moodustavad
     *             failis @a sgml-uc-cnv.txt loetletud olemid ja olemid kujul &amp;kümnendkood;
     *        <li> @a _autosgml_==false -- lubatud SGML olemite hulga moodustavad ainult
     *             failis @a sgml-uc-cnv.txt loetletud olemid
     *   </ul>
     * </li>
     * <li> faili kirjatamine
     *   <ul> <li> @a _autosgml_==false -- ainult failis @a sgml-uc-cnv.txt loetletud
     *             UNICODEi sümbolid vastavateks SGML olemiteks, ülejäänud
     *             mitte-ASCII sümbolid annavad vea
     *        <li> @a _autosgml_==true -- failis @a sgml-uc-cnv.txt loetletud
     *             UNICODEi sümbolid teisendatakse vastavateks SGML olemiteks,
     *             ülejäänud mitte-ASCII sümbolid &amp;kümnendkood; kujul SGML olemiteks
     *   </ul> 
     * </li>
     * </ul>
     */
    SISSEVALJA(FILE* pfile, const PFSCODEPAGE _codePage_,
               const FSTCHAR* path = NULL,
               const bool _ignoramp_ = false, const bool _autosgml_ = false)
    {
        try
        {
            InitEmptyClassVariables();
            Start(pfile, _codePage_, path, _ignoramp_, _autosgml_);
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** Sisend-väljundfaili avamine
     *
     * @param[in] fileName -- Avatava faili nimi
     * @param[in] pmode -- Avamisviis, vt @a ::fopen() funktsiooni kirjeldust
     * @param[in] _codePage_ -- Avatava faili kooditabel
     * @param[in] path -- Kui @a path!=NULL, siis nendest kataloogidest otsime teisendustabelit
     * sisaldavat faili @a "sgml-uc-cnv.txt
     * @param[in] _ignoramp_ -- (vaikimisi @a false)
     * Kui @a _codePage_==PFSCP_HTMLEXT ja toimub failist lugemine
     * <ul>
     * <li> @a _ignoramp_==false -- Ampersand peab alustama lubatud hulka
     *      kuuluvat SGML olemit. Kõik tekstis ampersandina mõeldud ampersandid
     *      peavad olema esitatud SGML olemina ("&amp;").
     * <li> @a _ignoramp_==true -- Ampersand väljaspool olemeid on lubatud
     * </ul>
     * @param[in] _autosgml_ -- (vaikimisi @a false)
     * Kui @a _codePage_==PFSCP_HTMLEXT ja toimub
     * <ul>
     * <li> failist lugemine
     *   <ul> <li> @a _autosgml_==true -- lubatud SGML olemite hulga moodustavad
     *             failis @a sgml-uc-cnv.txt loetletud olemid ja olemid kujul &amp;kümnendkood;
     *        <li> @a _autosgml_==false -- lubatud SGML olemite hulga moodustavad ainult
     *             failis @a sgml-uc-cnv.txt loetletud olemid
     *   </ul>
     * </li>
     * <li> faili kirjatamine
     *   <ul> <li> @a _autosgml_==false -- ainult failis @a sgml-uc-cnv.txt loetletud
     *             UNICODEi sümbolid vastavateks SGML olemiteks, ülejäänud
     *             mitte-ASCII sümbolid annavad vea
     *        <li> @a _autosgml_==true -- failis @a sgml-uc-cnv.txt loetletud
     *             UNICODEi sümbolid teisendatakse vastavateks SGML olemiteks,
     *             ülejäänud mitte-ASCII sümbolid &amp;kümnendkood; kujul SGML olemiteks
     *   </ul>
     * </li>
     * </ul>
     */
    void Start(const CFSFileName& fileName, const FSTCHAR* pmode,
               const PFSCODEPAGE _codePage_, const FSTCHAR* path = NULL,
               const bool _ignoramp_ = false, const bool _autosgml_ = false);

    /** Sisend-väljundfaili avamine
     * 
     * @param[in] pfile -- Kasutame juba avatud faili
     * @param[in] pmode -- Avamisviis, vt @a ::fopen() funktsiooni kirjeldust
     * @param[in] _codePage_ -- Avatava faili kooditabel
     * @param[in] path -- Kui @a path!=NULL, siis nendest kataloogidest otsime teisendustabelit
     * sisaldavat faili @a "sgml-uc-cnv.txt
     * @param[in] _ignoramp_ -- (vaikimisi @a false)
     * Kui @a _codePage_==PFSCP_HTMLEXT ja toimub failist lugemine
     * <ul>
     * <li> @a _ignoramp_==false -- Ampersand peab alustama lubatud hulka 
     *      kuuluvat SGML olemit. Kõik tekstis ampersandina mõeldud ampersandid
     *      peavad olema esitatud SGML olemina ("&amp;").
     * <li> @a _ignoramp_==true -- Ampersand väljaspool olemeid on lubatud
     * </ul>
     * @param[in] _autosgml_ -- (vaikimisi @a false)
     * Kui @a _codePage_==PFSCP_HTMLEXT ja toimub
     * <ul> 
     * <li> failist lugemine
     *   <ul> <li> @a _autosgml_==true -- lubatud SGML olemite hulga moodustavad
     *             failis @a sgml-uc-cnv.txt loetletud olemid ja olemid kujul &amp;kümnendkood;
     *        <li> @a _autosgml_==false -- lubatud SGML olemite hulga moodustavad ainult
     *             failis @a sgml-uc-cnv.txt loetletud olemid
     *   </ul>
     * </li>
     * <li> faili kirjatamine
     *   <ul> <li> @a _autosgml_==false -- ainult failis @a sgml-uc-cnv.txt loetletud
     *             UNICODEi sümbolid vastavateks SGML olemiteks, ülejäänud
     *             mitte-ASCII sümbolid annavad vea
     *        <li> @a _autosgml_==true -- failis @a sgml-uc-cnv.txt loetletud
     *             UNICODEi sümbolid teisendatakse vastavateks SGML olemiteks,
     *             ülejäänud mitte-ASCII sümbolid &amp;kümnendkood; kujul SGML olemiteks
     *   </ul> 
     * </li>
     * </ul>
     */
    void Start(FILE* pfile, const PFSCODEPAGE _codePage_,
               const FSTCHAR* path = NULL,
               const bool _ignoramp_ = false, const bool _autosgml_ = false);

    ~SISSEVALJA(void)
    {
        Stop();
    }

    bool EmptyClassInvariant(void)
    {
        return true;
    }

    bool ClassInvariant(void)
    {
        return true;
    }

    /** Sellest kooditabelise UNICODE'i või vastupidi */
    PFSCODEPAGE svKoodiTabel;

    /** Baidijärjemärk (BOM) kooditabeli IDks, vaikimisi Win Baltic */
    PFSCODEPAGE BomDetection(const CFSFileName& fileName)
    {
        PFSCODEPAGE codePage = PFSCP_BALTIC;
        sizeOfBOM = 0;
        char c1, c2, c3;
        if (CPFSFile::Open(fileName, FSTSTR("rb")) == true)
        {
            if (ReadChar(&c1) == true)
            {
                switch (c1)
                {
                case '\xFF':
                    if (ReadChar(&c2) == true && c2 == '\xFE')
                    {
                        codePage = PFSCP_UC;
                        sizeOfBOM = 2;
                    }
                    break;
                case '\xEF':
                    if (ReadChar(&c2) == true && ReadChar(&c3) == true &&
                        c2 == '\xBB' && c3 == '\xBF')
                    {
                        codePage = PFSCP_UTF8;
                        sizeOfBOM = 3;
                    }
                    break;
                }
            }
            CPFSFile::Close();
        }
        return codePage;
    }

    /** BOMi käsitlus sisendfailis
     *
     * Muutujus @a sizeOfBOM peetakse meeles BOMi
     * suurust (3-utf8, 2-unicode, 0-ülejäänud)
     *
     * @param[in] _bom_
     * <ul>
     * <li> @a ==false -- ei tegele BOMiga
     * <li> @a ==true
     *     <ul> <li> @a svKoodiTabel==PFSCP_UC peab fail algama xFF xFE-ga
     *          <li> @a svKoodiTabel==PFSCP_UTF8 peab fail algama  xEF xBB xBF-ga
     *     </ul>
     * </ul>
     */
    void BomIn(const bool _bom_)
    {
        if (_bom_ == false)
        {
            sizeOfBOM = 0;
            return;
        }
        switch (svKoodiTabel)
        {
        case PFSCP_UC:
            FSWCHAR bom;
            if (ReadChar(&bom) == false || bom != 0xFEFF) // pole ByteOrderMark
                throw VEAD(ERR_IO, ERR_NOMEM, __FILE__, __LINE__, "$Revision: 953 $",
                           "Faili alguses puudub UNICODE'i baidij2rjrmark");
            sizeOfBOM = 2;
            break;
        case PFSCP_UTF8:
            char c1, c2, c3;
            if (ReadChar(&c1) == false || ReadChar(&c2) == false || ReadChar(&c3) == false ||
                c1 != '\xEF' || c2 != '\xBB' || c3 != '\xBF')
                throw VEAD(ERR_IO, ERR_NOMEM, __FILE__, __LINE__, "$Revision: 953 $",
                           "Faili alguses puudub UTF8 baidij�rjrm�rk");
            sizeOfBOM = 3;
            break;
        default:
            break; // kisub jamaks
        }
        throw VEAD(ERR_IO, ERR_NOMEM, __FILE__, __LINE__, "$Revision: 953 $",
                   "Antud kooditabeliga sisendfailil ei saa olla baidij�rjrm�rki");
    }

    /** BOMi käsitlus väljundfailis
     *
     * Muutujus @a sizeOfBOM peetakse meeles BOMi
     * suurust (3-utf8, 2-unicode, 0-ülejäänud)
     *
     * @param[in] _bom_
     * <ul><li> @a ==false -- ei tegele BOMiga
     *     <li> @a ==true
     *     <ul><li> @a svKoodiTabel==PFSCP_UC kirjutab fail algusesse koodid xFF xFE
     *         <li> @a svKoodiTabel==PFSCP_UTF8 kirjutab faili algusesse koodid xEF xBB xBF
     *     </ul>
     * </ul>
     */
    void BomOut(const bool _bom_)
    {
        if (_bom_ == false)
        {
            sizeOfBOM = 0;
            return;
        }
        switch (svKoodiTabel)
        {
        case PFSCP_UC:
            WriteChar((FSWCHAR) 0xFEFF);
            sizeOfBOM = 2;
            break;
        case PFSCP_UTF8:
            WriteChar((char) '\xEF');
            WriteChar((char) '\xBB');
            WriteChar((char) '\xBF');
            sizeOfBOM = 3;
            break;
        default:
            break; // kisub jamaks
        }
        throw VEAD(ERR_IO, ERR_NOMEM, __FILE__, __LINE__, "$Revision: 953 $",
                   "Antud kooditabeliga v@ljundfailil ei saa olla baidij@rjrm@rki");
    }

protected:
    /** SGML-olemite teisendustabel (SGML-unicode) */
    CONV_HTML_UC2 cnv;

    /** BOMi suurus (3-utf8, 2-unicode, 0-ülejäänud) */
    int sizeOfBOM;

    /** Taastab argumentideta konstruktori järgse seisu */
    void Stop(void);

    // Need on illegalsed-{{

    /// Illegaalne

    SISSEVALJA(SISSEVALJA&)
    {
        assert(false);
    }

    /// Illegaalne

    SISSEVALJA & operator=(const SISSEVALJA&)
    {
        assert(false);
        return *this;
    }
    // }}-Need on illegalsed

    /// Klassi muutuajte esialgseks initsialiseerimsieks konstruktoris

    void InitEmptyClassVariables(void)
    {
        sizeOfBOM = 3;
    }
};

/** Loeb faili ja teisendab UNICODEi */
class VOTAFAILIST : public SISSEVALJA
{
public:

    VOTAFAILIST(void)
    {
        InitEmptyClassVariables();
    }

    /** Sisendfaili avamine
     *
     * @param[in] fileName -- Avatava faili nimi
     * @param[in] pmode -- Avamisviis, vt @a ::fopen() funktsiooni kirjeldust
     * <ul><li> @a FSTSTR("rb") -- lugemiseks binaarses režiimis
     * </ul>
     * @param[in] _codePage_ -- Avatava faili kooditabel
     * @param[in] path -- Kui @a path!=NULL, siis nendest kataloogidest otsime teisendustabelit
     * sisaldavat faili @a sgml-uc-cnv.txt
     * @param[in] _ignoramp_ -- (vaikimisi @a false) @n
     * Kui @a _codePage_==PFSCP_HTMLEXT
     * <ul>
     * <li> @a _ignoramp_==false -- Ampersand peab alustama lubatud hulka
     *      kuuluvat SGML olemit. Kõik tekstis ampersandina mõeldud ampersandid
     *      peavad olema esitatud SGML olemina ("&amp;").
     * <li> @a _ignoramp_==true -- Ampersand väljaspool olemeid on lubatud
     * </ul>
     * @param[in] _autosgml_ -- (vaikimisi @a false) @n
     * Kui @a _codePage_==PFSCP_HTMLEXT
     *   <ul> <li> @a _autosgml_==true -- lubatud SGML olemite hulga moodustavad
     *             failis @a sgml-uc-cnv.txt loetletud olemid ja olemid kujul &amp;kümnendkood;
     *        <li> @a _autosgml_==false -- lubatud SGML olemite hulga moodustavad ainult
     *             failis @a sgml-uc-cnv.txt loetletud olemid
     *   </ul>
     * @param[in] _bom_ -- (vaikimisi @a false)
     * <ul><li> @a ==false -- Ei tegele BOMi käsitlemisega
     *     <li> @a ==true -- Tegeleb BOMi käsitlemisega
     * </ul>
     */
    VOTAFAILIST(const CFSFileName& fileName, const FSTCHAR* pmode,
                const PFSCODEPAGE _codePage_, const FSTCHAR* path = NULL,
                const bool _ignoramp_ = false, const bool _autosgml_ = false, const bool _bom_ = false)
    {
        try
        {
            InitEmptyClassVariables();
            Start(fileName, pmode, _codePage_, path, _ignoramp_, _autosgml_, _bom_);
            // Jama korral Throw()
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** Loeb std-sisendit
     *
     * @param[in] _codePage_ -- Avatava faili kooditabel
     * @param[in] path -- Kui @a path!=NULL, siis nendest kataloogidest otsime teisendustabelit
     * sisaldavat faili @a sgml-uc-cnv.txt
     * @param[in] _ignoramp_ -- (vaikimisi @a false) @n
     * Kui @a _codePage_==PFSCP_HTMLEXT
     * <ul>
     * <li> @a _ignoramp_==false -- Ampersand peab alustama lubatud hulka
     *      kuuluvat SGML olemit. Kõik tekstis ampersandina mõeldud ampersandid
     *      peavad olema esitatud SGML olemina ("&amp;").
     * <li> @a _ignoramp_==true -- Ampersand väljaspool olemeid on lubatud
     * </ul>
     * @param[in] _autosgml_ -- (vaikimisi @a false) @n
     * Kui @a _codePage_==PFSCP_HTMLEXT
     *   <ul> <li> @a _autosgml_==true -- lubatud SGML olemite hulga moodustavad
     *             failis @a sgml-uc-cnv.txt loetletud olemid ja olemid kujul &amp;kümnendkood;
     *        <li> @a _autosgml_==false -- lubatud SGML olemite hulga moodustavad ainult
     *             failis @a sgml-uc-cnv.txt loetletud olemid
     *   </ul>
     * @param[in] _bom_ -- (vaikimisi @a false)
     * <ul><li> @a ==false -- Ei tegele BOMi käsitlemisega
     *     <li> @a ==true -- Tegeleb BOMi käsitlemisega
     * </ul>
     */
    VOTAFAILIST(const PFSCODEPAGE _codePage_, const FSTCHAR* path = NULL,
                const bool _ignoramp_ = false, const bool _autosgml_ = false,
                const bool _bom_ = false)
    {
        try
        {
            InitEmptyClassVariables();
            Start(_codePage_, path, _ignoramp_, _autosgml_, _bom_);
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /** Sisendfaili avamine
     *
     * @param[in] fileName -- Avatava faili nimi
     * @param[in] pmode -- Avamisviis, vt @a ::fopen() funktsiooni kirjeldust
     * <ul><li> @a FSTSTR("rb") -- lugemiseks binaarses režiimis
     * </ul>
     * @param[in] _codePage_ -- Avatava faili kooditabel
     * @param[in] path -- (vaikimisi @a NULL) Kui @a path!=NULL, siis nendest
     * kataloogidest otsime teisendustabelit
     * sisaldavat faili @a sgml-uc-cnv.txt
     * @param[in] _ignoramp_ -- (vaikimisi @a false) @n
     * Kui @a _codePage_==PFSCP_HTMLEXT
     * <ul><li> @a _ignoramp_==false -- Ampersand peab alustama lubatud hulka
     *          kuuluvat SGML olemit. Kõik tekstis ampersandina mõeldud
     *          ampersandidpeavad olema esitatud SGML olemina ("&amp;").
     *     <li> @a _ignoramp_==true -- Ampersand väljaspool olemeid on lubatud
     * </ul>
     * @param[in] _autosgml_ -- (vaikimisi @a false) @n
     * Kui @a _codePage_==PFSCP_HTMLEXT
     * <ul><li> @a _autosgml_==true -- lubatud SGML olemite hulga moodustavad
     *          failis @a sgml-uc-cnv.txt loetletud olemid ja olemid
     *          kujul &amp;kümnendkood;
     *     <li> @a _autosgml_==false -- lubatud SGML olemite hulga moodustavad
     *          ainult failis @a sgml-uc-cnv.txt loetletud olemid
     * </ul>
     * @param[in] _bom_ -- (vaikimisi @a false)
     * <ul><li> @a ==false -- Ei tegele BOMi käsitlemisega
     *     <li> @a ==true -- Tegeleb BOMi käsitlemisega
     * </ul>
     */
    void Start(const CFSFileName& fileName, const FSTCHAR* pmode,
               const PFSCODEPAGE _codePage_, const FSTCHAR* path = NULL,
               const bool _ignoramp_ = false, const bool _autosgml_ = false, const bool _bom_ = false);

    /** Sisendfaili avamine
     *
     * @param[in] _codePage_ -- Avatava faili kooditabel
     * @param[in] path -- (vaikimisi @a NULL) Kui @a path!=NULL, siis nendest
     * kataloogidest otsime teisendustabelit
     * sisaldavat faili @a sgml-uc-cnv.txt
     * @param[in] _ignoramp_ -- (vaikimisi @a false) @n
     * Kui @a _codePage_==PFSCP_HTMLEXT
     * <ul><li> @a _ignoramp_==false -- Ampersand peab alustama lubatud hulka
     *          kuuluvat SGML olemit. Kõik tekstis ampersandina mõeldud
     *          ampersandidpeavad olema esitatud SGML olemina ("&amp;").
     *     <li> @a _ignoramp_==true -- Ampersand väljaspool olemeid on lubatud
     * </ul>
     * @param[in] _autosgml_ -- (vaikimisi @a false) @n
     * Kui @a _codePage_==PFSCP_HTMLEXT
     * <ul><li> @a _autosgml_==true -- lubatud SGML olemite hulga moodustavad
     *          failis @a sgml-uc-cnv.txt loetletud olemid ja olemid
     *          kujul &amp;kümnendkood;
     *     <li> @a _autosgml_==false -- lubatud SGML olemite hulga moodustavad
     *          ainult failis @a sgml-uc-cnv.txt loetletud olemid
     * </ul>
     * @param[in] _bom_ -- (vaikimisi @a false)
     * <ul><li> @a ==false -- Ei tegele BOMi käsitlemisega
     *     <li> @a ==true -- Tegeleb BOMi käsitlemisega
     * </ul>
     */
    void Start(const PFSCODEPAGE _codePage_, const FSTCHAR* path = NULL,
               const bool _ignoramp_ = false, const bool _autosgml_ = false,
               const bool _bom_ = false);

    /** Sisendfaili avamine
     *
     * @param[in] fileName -- Avatava faili nimi
     * @param[in] pmode -- Avamisviis, vt @a ::fopen() funktsiooni kirjeldust
     * <ul><li> @a FSTSTR("rb") -- lugemiseks binaarses režiimis
     * </ul>
     */
    bool Start(const CFSFileName& fileName, const FSTCHAR* pmode);

    /** Loeb ettenatud kodeeringus failist rea ja teisendab UNICODEi.
     *
     * @param rida
     * @return
     * <ul><li> @a true -- rida loetud
     *     <li> @a false -- EOF
     */
    bool Rida(CFSWString& rida);

    /** Loeb ettenatud kodeeringus failist trimmitud rea ja teisendab UNICODEi.
     *
     * @param rida
     * @return
     * <ul><li> @a true -- rida loetud
     *     <li> @a false -- EOF
     */
    bool RidaTrimmitud(CFSWString& rida);

    /** Argumentideta startitud klassi invariant. */
    bool EmptyClassInvariant(void)
    {
        return true;
    }

    bool ClassInvariant(void)
    {
        return true;
    }

private:

    /** Ilegaalne */
    VOTAFAILIST(VOTAFAILIST&)
    {
        assert(false);
    }

    /** Ilegaalne */
    VOTAFAILIST & operator=(const VOTAFAILIST&)
    {
        assert(false);
        return *this;
    }

    void InitEmptyClassVariables(void)
    {
        SISSEVALJA::InitEmptyClassVariables();
    }
};

//--------------------------------------------------------

class VOTAANDMEFAILIST : public VOTAFAILIST
{
public:

    VOTAANDMEFAILIST(void)
    {
        InitEmptyClassVariables();
    }

    VOTAANDMEFAILIST(const CFSFileName& fileName)
    {
        try
        {
            InitEmptyClassVariables();
            Start(fileName);
            // Jama korral Throw()
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    void Start(const CFSFileName& fileName)
    {
        VOTAFAILIST::Start(fileName, FSTSTR("rb"), PFSCP_UC);
    }

    bool EmptyClassInvariant(void) const
    {
        return true;
    }

    bool ClassInvariant(void) const
    {
        return true;
    }

    /** Lugemisjärg faili võtmele taha
     *
     * @param[in] key
     * @return
     * <ul><li> @a true -- lugemisjärg failis vahetult võtmestringi taga
     *     <li> @a false -- ei leidnud failis 'white space'i vahelt antud stringi
     * </ul>
     */
    bool Seek2(const CFSWString &key);

    /** Loeb 'white space'i vahelt järjekordse sõne */
    bool Get(CFSWString &key);

private:

    void InitEmptyClassVariables(void)
    {
    }

    /** Illegaalne */
    VOTAANDMEFAILIST(const VOTAANDMEFAILIST&)
    {
        assert(false);
    }

    /** Illegaalne */
    VOTAANDMEFAILIST & operator=(const VOTAANDMEFAILIST&)
    {
        assert(false);
        return *this;
    }
};

/** Info kirjutamiseks faili.
 *
 * UNICODEis stringi või sisend-väljundahela lüli    faili kirjutamiseks.
 * Info teisendatakse enne kirjutamist konstruktoriga määratletud
 * kooditabelisse.
 */
class PANEFAILI : public SISSEVALJA
{
public:

    PANEFAILI(void)
    {
        InitEmptyClassVariables();
    }

    PANEFAILI(const CFSFileName& fileName, const FSTCHAR* pmode,
              const PFSCODEPAGE _codePage_, const FSTCHAR* path = NULL,
              const bool _ignoramp_ = false, const bool _autosgml_ = false,
              const bool _bom_ = false)
    {
        try
        {
            InitEmptyClassVariables();
            Start(fileName, pmode, _codePage_, path, _ignoramp_, _autosgml_, _bom_);
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    PANEFAILI(const PFSCODEPAGE _codePage_, const FSTCHAR* path = NULL,
              const bool _ignoramp_ = false, const bool _autosgml_ = false,
              const bool _bom_ = false)
    {
        try
        {
            InitEmptyClassVariables();
            Start(_codePage_, path, _ignoramp_, _autosgml_, _bom_);
            // Jama korral Throw()
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    void Start(const CFSFileName& fileName, const FSTCHAR* pmode,
               const PFSCODEPAGE _codePage_, const FSTCHAR* path = NULL,
               const bool _ignoramp_ = false, const bool _autosgml_ = false,
               const bool _bom_ = false);

    void Start(const PFSCODEPAGE _codePage_, const FSTCHAR* path = NULL,
               const bool _ignoramp_ = false, const bool _autosgml_ = false,
               const bool _bom_ = false);

    void Pane(const CFSWString &str);
    void Pane(const CFSAString &str);

    template <typename S_TYYP, typename C_TYYP>
    void PaneX(const LYLI_TMPL<S_TYYP, C_TYYP>& lyli, const MRF_FLAGS& mrfFlags);

    void Pane(const LYLI* plyli, const MRF_FLAGS& mrfFlags = MF_DFLT_OLETA | MF_YHELE_REALE);
    void Pane(const LYLI_UTF8* plyli, const MRF_FLAGS& mrfFlags = MF_DFLT_OLETA | MF_YHELE_REALE);

    bool EmptyClassInvariant(void)
    {
        return true;
    }

    bool ClassInvariant(void)
    {
        return true;
    }
private:

    void InitEmptyClassVariables(void)
    {
    }

    /** Illegaalne */
    PANEFAILI(PANEFAILI&)
    {
        assert(false);
    }

    /** Illegaalne */
    PANEFAILI & operator=(const PANEFAILI&)
    {
        assert(false);
        return *this;
    }
};

#endif

