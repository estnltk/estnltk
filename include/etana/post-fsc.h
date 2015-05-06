#if !defined( POST_FSC_H )
#define POST_FSC_H

#include <assert.h>
#if defined( WIN32 ) || defined( WIN64 )
#include <fcntl.h>
#include <io.h>
#endif
#include <time.h>

#include "fsc.h"

#include "tmplptrsrtfnd.h"
#include "suurused.h"
#include "viga.h"
#include "pfscodepage.h"
#include "fsxstring.h"

/// Lisavad natuke täiendavat funktsionaalsust
/// FSC-klassidele.

template<class CHARTYPE>
inline void PTFSStrCpy(CHARTYPE* dest, const int destSize,
                       const CHARTYPE * const src)
{
    if (dest == NULL || src == NULL || FSStrLen(src) >= destSize)
        throw VEAD(ERR_X_TYKK, ERR_ARGVAL, __FILE__, __LINE__);
    FSStrCpy(dest, destSize, src);
}

inline void PFSStrCpy(char* dest, const int destSize, const char* src)
{
    PTFSStrCpy<char>(dest, destSize, src);
}

inline void PFSStrCpy(FSWCHAR* dest, const int destSize, const FSWCHAR* src)
{
    PTFSStrCpy<FSWCHAR > (dest, destSize, src);
}

class CPFSFile;

#define EritiSobiViit(C_TYYP, str) SobiViit<C_TYYP>(str, FSWSTR(str))

template<class C_TYYP>
inline const C_TYYP* SobiViit(const char* ascii, const FSWCHAR* unicode)
{
    assert(sizeof (C_TYYP) == sizeof (char) || sizeof (C_TYYP) == sizeof (FSWCHAR));

    if (sizeof (C_TYYP) == sizeof (char))
        return (const C_TYYP*) ascii;
    return (const C_TYYP*) unicode;
}

inline int KaksYheks(const char c1, const char c2)
{
    const int i1 = ((int) ((const unsigned char) c1))& 0xFF;
    const int i2 = ((int) ((const unsigned char) c2))& 0xFF;
    return (i1 << 8) | i2;
}

//----------------------------------------------------------------------------

/** Template klass, mis lisab baastüübile @a BASIC_TYPE võrdlusfunktsiooni
 *
 * Baastüübil @a BASIC_TYPE peavad olema defineeritud
 * omistamisoperaator ja võrdlusoperaatorid.
 */
template <class BASIC_TYPE>
class BASIC_TYPE_WITH_CMP
{
public:
    /** Peab olema sellist tüüpi, et tal oleks defineeritud
     * omistamisoperaator ja võrdlusoperaatorid.
     */
    BASIC_TYPE obj;

    /** Konstruktor */
    BASIC_TYPE_WITH_CMP(void)
    {
    }

    /** Copy-konstruktor */
    BASIC_TYPE_WITH_CMP(BASIC_TYPE_WITH_CMP& rec)
    {
        *this = operator=(rec);
    }

    /** Konstruktor */
    BASIC_TYPE_WITH_CMP(BASIC_TYPE& o)
    {
        obj = o;
    }

    /** BASIC_TYPE_WITH_CMP tüüpi kirjete võrdlemiseks */
    int Compare(const BASIC_TYPE_WITH_CMP *rec, const int sortOrder = 0) const
    {
        return Compare(&(rec->obj));
    }

    /** BASIC_TYPE tüüpi kirjete võrdlemiseks */
    int Compare(const BASIC_TYPE *key, const int sortOrder = 0) const
    {
        if (obj > *key)
            return 1;
        if (obj < *key)
            return -1;
        return 0;
    }

    /* void Start(const BASIC_TYPE *rec) {obj = rec->obj; } */

    /** Argumentideta konstrultori järgne invariant */
    bool EmptyClassInvariant(void) const
    {
        return true;
    }

    /** Initsialiseeritud klassi invariant */
    bool ClassInvariant(void) const
    {
        return true;
    }

    /** Omistamisoperaator */
    BASIC_TYPE_WITH_CMP & operator=(BASIC_TYPE_WITH_CMP& rec)
    {
        if (this != &rec)
            obj = rec->obj;
        return *this;
    }

    /** Omistamisoperaator */
    BASIC_TYPE_WITH_CMP & operator=(BASIC_TYPE& o)
    {
        obj = o;
        return *this;
    }

};

typedef BASIC_TYPE_WITH_CMP<int> INTCMP;
typedef TMPLPTRARRAYBIN<INTCMP, int> TMPLPTRARRAYSRTINT;

//----------------------------------------------------------------------------

/** Lisavidinatega @a CFSAString */
class PCFSAString : public CFSAString
{
public:

    /** String koosneb sellise baidisuuresega märkidest */
    enum
    {
        charSize = sizeof (char)
    };

    /** Argumentideta konstruktor */
    PCFSAString(void)
    {
    }

    /** Konstrueerib @a CFSAString tüüpi stringist */
    PCFSAString(const CFSAString& str) : CFSAString(str)
    {
    }

    /** Konstrueerib UTF8 vormingus stringi @a CFSWString tüüpi stringist */
    PCFSAString(const CFSWString& str)
    {
        Start(str);
    }

    /** Konstrueerib @a char tüüpi 0-lõpulisest viidast */
    PCFSAString(const char* pStr) : CFSAString(pStr)
    {
    }

    /** Konstrueerib @a FSWCHAR tüüpi 0-lõpulisest viidast */
    PCFSAString(const FSWCHAR* pStr)
    {
        Start(pStr);
    }

    /** Konstrueerib @a char tüüpi viida @a lLength esiemsest tähest */
    PCFSAString(const char* pStr, INTPTR lLength) : CFSAString(pStr, lLength)
    {
    }

    /** Konstrueerib @a CFSAString tüüpi stringist */
    void Start(const CFSAString& str)
    {
        *this = CFSAString::operator=(str);
    }

    /** Konstrueerib UTF8 vormingus stringi @a CFSWString tüüpi stringist */
    void Start(const CFSWString& str)
    {
        *this = FSStrWtoA(str, FSCP_UTF8);
    }

    void Start(const FSWCHAR* pStr)
    {
        CFSWString str(pStr);
        Start(str);
    }

    /** Võrdlemine, argumendiks stringiklassiviit
     *
     * @param[in] s -- võrreldava stringi viit
     * @param[in] sortOrder -- pole kasutusel
     * @return
     * <ul><li> @a &lt;0 Kui *this &lt; *s
     *     <li>  ==0 Kui *this == *s
     *     <li> @a &gt;0 Kui *this &gt; *s
     * </ul>
     */
    int Compare(const CFSAString* key, const int sortOrder = 0) const
    {
        FSUNUSED(sortOrder);
        assert(key != NULL);
        return CFSAString::Compare(*key); // polümorfism
    }

    /** Võrdlemine, argumendiks stringiklass
     *
     * @param[in] s -- võrreldav string
     * @param[in] sortOrder -- pole kasutusel
     * @return
     * <ul><li> @a &lt;0 Kui *this &lt; *s
     *     <li>  ==0 Kui *this == *s
     *     <li> @a &gt;0 Kui *this &gt; *s
     * </ul>
     */
    int Compare(const PCFSAString rec, const int sortOrder = 0) const
    {
        FSUNUSED(sortOrder);
        assert(rec != NULL);
        return CFSAString::Compare(rec); // polümorfism
    }
};

/** Leiab keskonnamuutaja @a PATH väärtuse */
class PATHSTR
{
public:

    PATHSTR(void)
    {
        InitClassVariables();
#if defined( WINRT )
		throw VEAD(ERR_X_TYKK, ERR_ARGVAL, __FILE__, __LINE__, "$Revision: 1236 $");
#elif defined( WIN32 )
        errno_t err;
        size_t len;
#if defined(UNICODE)
        err = _wdupenv_s(&buffer, &len, FSWSTR("Path"));
#else
        err = _dupenv_s(&buffer, &len, "Path");
#endif
        sizeOfBuffer = (int) len;
        if (err)
            throw VEAD(ERR_X_TYKK, ERR_ARGVAL, __FILE__, __LINE__, "$Revision: 1236 $");
#else
        //UNIXid/LINUXid
        if (getenv("PATH") == NULL || (buffer = strdup(getenv("PATH"))) == NULL)
            throw VEAD(ERR_X_TYKK, ERR_ARGVAL, __FILE__, __LINE__, "$Revision: 1236 $");
        sizeOfBuffer = strlen(buffer);
#endif
    }

    operator const FSTCHAR* (void) const
    {
        return buffer;
    }

    ~PATHSTR(void)
    {
        if (buffer != NULL)
            free(buffer);
    }
private:
    FSTCHAR* buffer;
    int sizeOfBuffer;

    void InitClassVariables(void)
    {
        sizeOfBuffer = 0;
        buffer = NULL;
    }

    PATHSTR(const PATHSTR&)
    {
        assert(false);
    }

    PATHSTR & operator=(const PATHSTR&)
    {
        assert(false);
        return *this;
    }
};

/** Leiab faili @a pathname'i
 * 
 * @param[out] dctPathStr Leitud @a pathname
 * @param[in] path Sellest proovime katalooge. 
 *            Windowsis kataloogid eraldatud semikooloniga, Unixis kooloniga.
 * @param[in] file Vaatame kas sellise nimega fail asub mõnes 
 *            ülaloetletud kataloogis.
 * @return 
 * <ul><li> @a true Leidus, muutujas @a dctPathStr vastav pathname
 */
bool Which(CFSString* dctPathStr, const CFSString* path, const CFSString* file);

/** Unicode'i või ASCII string stringide massiiviks
 *
 * Tükeldab stringi etteantud eraldajate kohalt massiviks.
 * Näiteks:
 * <ul><li> 
 * Tükeldame Unicode'is stringi white space'ide kohalt järjestatud massiviks:
 * @code
 * typedef TMPLPTRARRAYBIN&lt;PCFSWString,CFSWString&gt; TMPLPTRARRAYBIN_CFSWS;
 * TYKELDATUDPCFSSTRING&lt;PCFSWString, CFSWString, TMPLPTRARRAYBIN_CFSWS&gt; blaba;
 * blaba.Start(FSWSTR("Tere Talv"), FSWSTR(" \\t\\r\\n"), 3, 3); 
 * blaba.Sort();
 * @endcode
 * <li>
 * Tükeldame ASCII stringi white space'ide kohalt (mittejärjestatud) massiviks:
 * @code
 * typedef TMPLPTRARRAY&lt;PCFSAString&gt; TMPLPTRARRAY_CFSAS;
 * TYKELDATUDPCFSSTRING&lt;PCFSAString, CFSAString, TMPLPTRARRAY_CFSAS&gt; bla;
 * bla.Start("Tere Talv", " \\t\\r\\n", 3, 3); 
 * @endcode
 * </ul>
 */
template <class RECSTR, class KEYSTR, class ARRAY>
class TYKELDATUDPCFSSTRING : public ARRAY
{
public:

    TYKELDATUDPCFSSTRING(void)
    {
        InitClassVariables();
    }

    /**
     * 
     * @param[in] buf Tükeldatav string.
     * @param[in] eraldajad Eraldajad. Nende kohtade pealt tükeldame.
     * @param[in] algsuurus Tükikesi sisaldava (järjestava) massiivi algsuurus.
     * @param[in] samm Vajadusel suurendame massiivi sellise sammuga.
     * @param[in] yhekohalineEraldaja Väljade eraldaja ühe tähemärgi laiune
     */
    TYKELDATUDPCFSSTRING(const KEYSTR& buf, const KEYSTR& eraldajad,
                         const int algsuurus = 10, const int samm = 10,
                         const bool yhekohalineEraldaja = false)
    {
        InitClassVariables();
        Start(buf, eraldajad, algsuurus, samm, yhekohalineEraldaja);
    }

    /// Initsialiseerib klassi.
    //
    /// Initsialiseerib klassi peale argumentideta konstruktorit.
    /// @return Funktsiooni väärtus:
    /// - \a ==true õnnestus
    /// - \a ==false ebaõnnstus

    /**
     * 
     * @param[in] buf Tükeldatav string.
     * @param[in] eraldajad Eraldajad. Nende kohtade pealt tükeldame.
     * @param[in] algsuurus Tükikesi sisaldava (järjestava) massiivi algsuurus.
     * @param[in] samm Vajadusel suurendame massiivi sellise sammuga.
     * @param[in] yhekohalineEraldaja Väljade eraldaja ühe tähemärgi laiune
     */
    void Start(const KEYSTR& buf, const KEYSTR& eraldajad,
               const int algsuurus = 10, const int samm = 10,
               const bool yhekohalineEraldaja = false)
    {
        if (ARRAY::EmptyClassInvariant() == false)
            ARRAY::Stop();
        ARRAY::Start(algsuurus, samm);
        RECSTR wstr;
        int algus, lopp;
        for (algus = lopp = 0; buf[lopp]; algus = lopp)
        {
            //üle alustavate eraldajate
            if (buf[algus] && eraldajad.Find(buf[algus]) >= 0)
            {
                algus++;
                while (yhekohalineEraldaja == false && buf[algus] && eraldajad.Find(buf[algus]) >= 0)
                    algus++;
            }
            lopp = algus;
            while (buf[lopp] && eraldajad.Find(buf[lopp]) < 0)
                lopp++;
            if (yhekohalineEraldaja == true || algus < lopp)
            {
                wstr = buf.Mid(algus, lopp - algus);
                ARRAY::AddClone(wstr);
            }
        }
    }

    bool ClassInvariant(void) const
    {
        return ARRAY::ClassInvariant();
    }
private:

    void InitClassVariables(void)
    {
    }

    TYKELDATUDPCFSSTRING(TYKELDATUDPCFSSTRING&)
    {
        assert(false);
    }

    TYKELDATUDPCFSSTRING & operator=(TYKELDATUDPCFSSTRING&)
    {
        assert(false);
        return *this;
    }
};

namespace STRSOUP
{

/** Kontrollib, kas @a char* string koosneb ainult 7bitistest
 * 
 * @param[in] str Selle stringi koostist kontrollime.
 * @return 
 * <ul><li> @a true Koosneb ainult 7bitistest või oli NULL-viit
 *     <li> @a false Sisaldab mingit 8bitist koodi
 */
inline bool Ainult7Bitised(const signed char* str)
{
    //return Ainult7Bitised((unsigned char*)str);
    if (str == NULL)
        return true;
    for (int i = 0; str[i] != '\0'; i++)
    {
        if ((str[i]&'\x80') != '\0')
            return false;
    }
    return true;
}

/** Kontrollib, kas @a unsigned @a char* string koosneb ainult 7bitistest
 * 
 * @param[in] str Selle stringi koostist kontrollime.
 * @return 
 * <ul><li> @a true Koosneb ainult 7bitistest või oli NULL-viit
 *     <li> @a false Sisaldab mingit 8bitist koodi
 */
inline bool Ainult7Bitised(const unsigned char* str)
{
    if (str == NULL)
        return true;
    for (int i = 0; str[i] != '\0'; i++)
    {
        if ((str[i]&'\x80') != '\0')
            return false;
    }
    return true;
}

/** Kaks 8bitist üheks FSWCHARiks (16 või 32 bitiseks).
 * 
 * @param[in] ptr Sellelt aadressilt keerame kahe esimese baidi 
 * järjekorra 'õigeks'.
 * @return Õigeks keeratud baidijärjega @a FSWCHAR. @n
 * @a (FSWCHAR)((ptr[0]|(ptr[1]<<8))&0xFFFF)
 */
inline FSWCHAR Kahest(const unsigned char* ptr)
{
    assert(ptr != NULL);
    return (FSWCHAR) ((ptr[0] | (ptr[1] << 8))&0xFFFF);
}

/** 16bitise 0-lõpulise stringi baidijärg õigeks, tulemus 0-lõpulisse stringi
 * 
 * @param[out] pWstr Siia paneme 'õigekskeeratud' baidijärjega stringi.
 * @attention Peab olema tagatud, 
 * et @a wcslen(pStr) @a >= @a wcstrlen((wchar_t*)pStr)
 * @param[in] pStr Esialgse baidijärjega string.
 * @return Funktsiooni väärtuseks on 'õigeks'
 * keeratud baidipaaride arv. Stringilõputunnus 
 * läheb ka arvesse. Kasutab funktsiooni Kahest().
 * @attention Peab olema tagatud, 
 * et @a wcslen(pStr) @a >= @a wcstrlen((wchar_t*)pStr)
 *
 *  Oli süsteemi mõttes, reaalselt ei kasuta
 * 
inline int FixStrByteOrder(FSWCHAR* pWstr, const unsigned char* pStr)
{
    assert(pWstr != NULL && pStr != NULL);
    if (pWstr == NULL || pStr == NULL)
    {
        return 0;
    }
    int i = 0;
    for (int pos = 0; (pWstr[i] = Kahest(pStr + pos)) != 0; pos += 2)
    {
        i++;
    }
    return i + 1;
}
*/

/** 16bitise 0-lõpulise stringi baidijärg õigeks, tulemus stringiklassi
 * 
 * @param[out] pcWstr Siia paneme 'õigekskeeratud' baidijärjega stringi.
 * Sobib ka @a FSXSTRING \a *pcWstr.
 * @param[in] pStr Esialgse baidijärjega string.
 * @return Niimitu FSWCHARi keeras ümber, EOS läheb arvesse.
 */
/*inline int FixStrByteOrder(CFSWString* cWstr, const unsigned char* pStr)
{
    assert(cWstr != NULL);
    assert(pStr != NULL);
    if (pStr == NULL)
        return 0;
    cWstr->Empty();
    FSWCHAR wChar;
    int i = 0;
    for (int pos = 0; (wChar = Kahest(pStr + pos)) != 0; pos += 2)
    {
        *cWstr += wChar;
        i++;
    }
    return i + 1;
}*/

inline int FixStrByteOrder(CFSWString& cWstr, const unsigned char* pStr)
{
    assert(pStr != NULL);
    if (pStr == NULL)
        return 0;
    cWstr.Empty();
    FSWCHAR wChar;
    int i = 0;
    for (int pos = 0; (wChar = Kahest(pStr + pos)) != 0; pos += 2)
    {
        cWstr += wChar;
        i++;
    }
    return i + 1;
}

/** Positiivne number stringi(klassile) sappa
 * 
 * Numbri kirjutame olemaolevale stringile sappa lisaks! 
 * 
 * Malliparameetrid:
 * <ul><li> NUMTYPE = {int, long, ...}
 *    <li> STRCTYPE = { CFSAString, CFSWString, ...}
 *    <li> CHRTYPE  = { char, wchar_t, ...}
 *    <li> int base = {8, 10, 16}
 * </ul>
 * @param[in] num Seda numbrit teisendame stringiks.
 * @param[out] fsStr Numbri kirjutame sellele stringile sappa.
 */
template <class NUMTYPE, class STRCTYPE, class CHRTYPE, int base>
inline void UnsignedNum2Str(NUMTYPE num, STRCTYPE& fsStr)
{
    if (num < 0)
        throw VEAD(ERR_X_TYKK, ERR_ARGVAL, __FILE__, __LINE__, "$Revision: 1236 $");
    if (base != 8 && base != 10 && base != 16)
        throw VEAD(ERR_X_TYKK, ERR_ARGVAL, __FILE__, __LINE__, "$Revision: 1236 $");
    int numbriAlgus = fsStr.GetLength(); // stringi lõpp, siia hakkame numbreid juurde kirjutama
    do
    {
        NUMTYPE tmp = num % ((NUMTYPE) base);
        if (tmp > 9)
        {
            assert(base == 16);
            fsStr += (CHRTYPE) (tmp - 10)+(CHRTYPE) 'a';
        }
        else
            fsStr += (CHRTYPE) tmp + (CHRTYPE) '0';
        num /= base;
    }
    while (num > 0);
    //keerame tagurpidi numbri õigetpidiseks
    for (int n = (fsStr.GetLength() - numbriAlgus) / 2 - 1; n >= 0; n--)
    {
        CHRTYPE tmp = fsStr[numbriAlgus + n];
        fsStr[numbriAlgus + n] = fsStr[fsStr.GetLength() - n - 1];
        fsStr[fsStr.GetLength() - n - 1] = tmp;
    }
}

/** String (märgita) 10nd-numbriks
 * 
 * Malliparameetrid:
 * <ul><li> NUMTYPE = {int, long, ...}
 *     <li> STRTYPE = {char, FSWCHAR, FSTCHAR, ...}
 * </ul>
 * @param[out] pNum Stringist kokkuarvutatud (märgita) number.
 * @param[in] pStr Sellest stringist õngitseme (märgita) numbri.
 * Kui string ei alanud numbriga \a (0-9),
 * tagastatakse @a 0. Märk @a (+-) ei sobi numbrit alustama.
 * @return Funktsiooni väärtuseks on arvuks teisendatud 
 * numbrite hulk. Kui string ei alanud numbriga @a (0-9),
 * tagastatakse @a 0. 
 * Märk @a (+-) ei sobi numbrit alustama.
 */
template <class NUMTYPE, class STRTYPE>
inline int UnsignedStr2Num(NUMTYPE* pNum, const STRTYPE* pStr)
{
    assert(pNum != NULL && pStr != NULL);
    int i;
    *pNum = 0;
    for (i = 0; pStr[i] && pStr[i] >= (STRTYPE) '0' && pStr[i] <= (STRTYPE) '9'; i++)
        *pNum = 10 * (*pNum) + ((NUMTYPE) (pStr[i]) - (NUMTYPE) '0');
    return i;
}

/** String (märgita) 8nd-numbriks
 * 
 * Malliparameetrid:
 * <ul><li> NUMTYPE = {int, long, ...}
 *     <li> STRTYPE = {char, FSWCHAR, FSTCHAR, ...}
 * </ul>
 * @param[out] pNum Stringist kokkuarvutatud (märgita) number.
 * @param[in] pStr Sellest stringist õngitseme (märgita) numbri.
 * Kui string ei alanud numbriga \a (0-9),
 * tagastatakse @a 0. Märk @a (+-) ei sobi numbrit alustama.
 * @return Funktsiooni väärtuseks on arvuks teisendatud 
 * numbrite hulk. Kui string ei alanud numbriga @a (0-7),
 * tagastatakse @a 0. 
 * Märk @a (+-) ei sobi numbrit alustama.
 */
template <class NUMTYPE, class STRTYPE>
inline int UnsignedStr2Oct(NUMTYPE* pNum, const STRTYPE* pStr)
{
    assert(pNum != NULL && pStr != NULL);
    int i;
    *pNum = 0;
    for (i = 0; pStr[i] != (STRTYPE) 0; i++)
    {
        if (pStr[i] >= (STRTYPE) '0' && pStr[i] <= (STRTYPE) '7')
            *pNum = 8 * (*pNum) + ((NUMTYPE) (pStr[i]) - (NUMTYPE) '0');
        else
            break;
    }
    return i;
}

/** String (märgita) 16nd-numbriks
 * 
 * Malliparameetrid:
 * <ul><li> NUMTYPE = {int, long, ...}
 *     <li> STRTYPE = {char, FSWCHAR, FSTCHAR, ...}
 * </ul>
 * @param[out] pNum Stringist kokkuarvutatud (märgita) number.
 * @param[in] pStr Sellest stringist õngitseme (märgita) numbri.
 * Kui string ei alanud numbriga \a (0-9),
 * tagastatakse @a 0. Märk @a (+-) ei sobi numbrit alustama.
 * @return Funktsiooni väärtuseks on arvuks teisendatud 
 * numbrite hulk. Kui string ei alanud numbriga @a (0-9a-fA-F),
 * tagastatakse @a 0. 
 * Märk @a (+-) ei sobi numbrit alustama.
 */
template <class NUMTYPE, class STRTYPE>
inline int UnsignedStr2Hex(NUMTYPE* pNum, const STRTYPE* pStr)
{
    assert(pNum != NULL && pStr != NULL);
    int i;
    *pNum = 0;

    for (i = 0; pStr[i] != (STRTYPE) 0; i++)
    {
        NUMTYPE num;
        if (pStr[i] >= (STRTYPE) '0' && pStr[i] <= (STRTYPE) '9')
            num = (NUMTYPE) (pStr[i]) - (NUMTYPE) '0';
        else if (pStr[i] >= (STRTYPE) 'a' && pStr[i] <= (STRTYPE) 'f')
            num = (NUMTYPE) (pStr[i]) - (NUMTYPE) 'a' + (NUMTYPE) 10;
        else if (pStr[i] >= (STRTYPE) 'A' && pStr[i] <= (STRTYPE) 'F')
            num = (NUMTYPE) (pStr[i]) - (NUMTYPE) 'A' + (NUMTYPE) 10;
        else
            break;
        *pNum = 16 * (*pNum) + num;
    }
    return i;
}

/// String (märgiga) numbriks.
//
/// NUMTYPE = {int, long, ...}
/// STRTYPE = {char, FSWCHAR, FSTCHAR, ...}
/// @return Funktsiooni väärtuseks on arvuks teisendatud 
/// numbrite hulk. Kui string ei alanud numbriga \a (0-9)
/// väi märgiga \a (+-), tagastatakse \a 0.

template <class NUMTYPE, class STRTYPE>
inline int SignedStr2Num(//==numbri pikkus stringis
                         NUMTYPE* pNum,
                         ///< Stringist kokkuarvutatud
                         ///<  (märgiga) number.
                         const STRTYPE* pStr
                         ///< Sellest stringist õngitseme (märgiga) numbri.
                         ///< Kui string ei alanud numbriga \a (0-9),
                         ///< või märgiga \a (+-), tagastatakse \a 0.
                         )
{
    assert(pNum != NULL && pStr != NULL);
    bool miinus = false;
    int offset = 0, ret;
    if (pStr[0] == (STRTYPE) '-')
    {
        miinus = true;
        offset = 1;
    }
    else if (pStr[0] == (STRTYPE) '+')
    {
        offset = 1;
    }
    if ((ret = UnsignedStr2Num<NUMTYPE, STRTYPE > (pNum, pStr + offset)) > 0)
    {
        if (miinus)
        {
            *pNum = -(*pNum);
        }
    }
    return ret;
}

/// Loeb stringist märgita/märgiga arvu 1/2/4 baidisena.
//
// TYPE2READ={UB1, UB2, UB4} 
// TYPE4ARG={(un)signed char, (un)signed short, (un)signed int, (un)signed long, enum} jne

template <class TYPE2READ, class TYPE4ARG>
inline void ReadUnsignedFromString(
                                   const unsigned char* pStr,
                                   ///< Sisendstring.
                                   ///< Sisendstringist loetakse TYPE4ARG tüüpi arv baithaaval.
                                   ///< { (*pNum)>>(i*8)==pStr[i] | i=0, 1, ..., sizeof(TYPE2READ) },
                                   ///< kus TYPE2READ={UB1, UB2, UB4}
                                   TYPE4ARG* pNum,
                                   ///< Siia loeme sisendist õiges
                                   ///< järjekorras õige arvu baite.
                                   const TYPE2READ readArg = 0
                                   ///< Seda ei kasutata kunagi.
                                   ///< TYPE2READ={UB1, UB2, UB4}
                                   )
{
    FSUNUSED(readArg);
    assert(pStr != NULL && pNum != NULL);
    assert(sizeof (TYPE2READ) == 1 || sizeof (TYPE2READ) == 2 || sizeof (TYPE2READ) == 4);
    assert(sizeof (TYPE2READ) <= sizeof (TYPE4ARG));
    *pNum = 0;
    for (unsigned int i = 0; i < sizeof (TYPE2READ); i++)
    {
        //unsigned char tmp_c=pStr[i];
        //TYPE4ARG tmp_arg1=(TYPE4ARG)tmp_c;
        //TYPE4ARG tmp_arg2=tmp_arg1&0xFF;
        //TYPE4ARG tmp_arg3=tmp_arg2<<(i*8);
        // *pNum += tmp_arg3;

        *pNum += (((TYPE4ARG) (pStr[i]))&0xFF) << (i * 8);
    }
}

/// Kirjutab baidimassiivi baithaaaval märgita/märgiga arvu 1/2/4 baidisena.

template <class TYPE2WRITE, class TYPE4ARG>
inline void WriteUnsignedToString(
                                  unsigned char* pStr,
                                  ///< Väljundstringi kirjutatakse TYPE2WRITE tüüpi arv baithaaval.
                                  ///< { num>>(i*8)==pStr[i] | i=0, 1, ..., sizeof(TYPE2WRITE) },
                                  ///< kus TYPE2WRITE={UB1, UB2, UB4}
                                  ///< @attention @a pStr peab viitama puhvrile,
                                  ///< mille suurus on vähemalt @a sizeof(TYPE2WRITE).
                                  const TYPE4ARG num,
                                  ///< Sellest numbrist kirjutame õiges
                                  ///< järjekorras õige arvu baite väljundisse.
                                  /// TYPE4ARG={(un)signed char, (un)signed short, (un)signed int, (un)signed long}
                                  const TYPE2WRITE writeArg = 0
                                  ///< Selle parameetri väärtust ei kasutata kunagi.
                                  ///< Määrab väljundstringi kirjutatava arvu tüübi.
                                  ///< TYPE2WRITE={UB1, UB2, UB4}
                                  )
{
    FSUNUSED(writeArg);
    assert(pStr != NULL);
    assert(sizeof (TYPE2WRITE) == 1u || sizeof (TYPE2WRITE) == 2u || sizeof (TYPE2WRITE) == 4u);
    assert(sizeof (TYPE4ARG) == 1u || sizeof (TYPE4ARG) == 2u || sizeof (TYPE4ARG) == 4u);
    assert(sizeof (TYPE2WRITE) <= sizeof (TYPE4ARG));
    // kontrollime, kas number on piisavalt väike, et kõik bitid ära mahuksid
    assert((sizeof (TYPE2WRITE) == sizeof (TYPE4ARG)) ||
           ((sizeof (TYPE2WRITE) == 1u) && ((num & 0x000000ff) == num)) ||
           ((sizeof (TYPE2WRITE) == 2u) && ((num & 0x0000ffff) == num)));
    for (unsigned int i = 0; i < sizeof (TYPE2WRITE); i++)
    {
        pStr[i] = (unsigned char) ((num >> (i * 8u))&0xFF);
    }
}
};

/// Standardsisendi ja -väljundi käsitlusega FSC-failiklass.

class CPFSFile
{
public:

    /// Argumentideta konstruktor.

    CPFSFile(void) : dontClose(true)
    {
    };
    
    /** Avab faili
     * 
     * @param fileName -- faili nimi
     * @param lpszMode -- sama mis @a ::fopen() funktsioonil
     * @return 
     * <ul><li> @a bool -- õnnestus
     *      <li> @a false -- äpardus
     * </ul>
     */
    bool Open(const CFSFileName& fileName, const FSTCHAR* lpszMode)
    {
        assert(lpszMode != NULL);
        dontClose = false;
        try
        {
            file.Open(fileName, lpszMode);
        }
        catch (...)
        {
            return false;
        }
        return true;
    }

    operator FILE* (void)
    {
        return (FILE *) file;
    }


    /// Avab faili.
    //
    /// @return
    /// - \a ==true Ok
    /// - \a !=false Viga

    bool Open(
              FILE* pFile ///< Käideldav fail (reeglina @a stdin, @a stdout või @a stderr)
              )
    {
        assert(pFile != NULL);
        Close();
#if defined( WIN32 ) || defined( WIN64 )
        if (file == stdin || file == stdout || file == stderr)
        {
            if (_setmode(_fileno(pFile), _O_BINARY) == -1)
            {
                return false;
            }
        }
#endif
        dontClose = true;
        file.Attach(pFile);
        return true;
    }

    /// Loeb failist märgita/märgiga arvu 1/2/4 baidisena.
    //
    /// Peab kehtima assert( sizeof(TYPE2READ) <= sizeof(TYPE4ARG) ).
    ///
    /// @return
    /// - \a ==true õnnestus
    /// - \a ==false Ebaõnnestus
    /// TYPE2READ={UB1, UB2, UB4}

    template <class TYPE2READ, class TYPE4ARG>
    bool ReadUnsigned(
                      TYPE4ARG* pNum,
                      ///< Siia loeme failist õiges järjekorras
                      ///< @a sizeof(TYPE2READ) baiti.
                      ///< TYPE4ARG={(un)signed char, (un)signed short, (un)signed int, (un)signed long, enum, ...}
                      const TYPE2READ readArg = 0
                      ///< Selle parameetri väärtust ei kasutata kunagi.
                      ///< Sisendfailist loetakse @a sizeof(TYPE2READ) baiti.
                      ///< Baidjärg keeratakse "õigeks" @a STRSOUP::ReadUnsignedFromString() funktsiooniga.
                      )
    {
        FSUNUSED(readArg);
        assert(pNum != NULL);
        assert(sizeof (TYPE2READ) == 1 || sizeof (TYPE2READ) == 2 || sizeof (TYPE2READ) == 4);
        assert(sizeof (TYPE2READ) <= sizeof (TYPE4ARG));
        unsigned char tmp[sizeof (TYPE2READ)];
        try
        {
            file.ReadBuf(tmp, sizeof (TYPE2READ)); // õige arv baite failist puhvrisse
        }
        catch (...)
        {
            return false;
        }
        STRSOUP::ReadUnsignedFromString<TYPE2READ, TYPE4ARG > (tmp, pNum); //  baidijärg õigeks ja muutujasse
        return true;
    };

    /// Kirjutab faili märgita/märgiga arvu 1/2/4 baidisena.
    //
    /// Peab kehtima assert( sizeof(TYPE2WRITE) <= sizeof(TYPE4ARG) ).
    /// TYPE4ARG tüüpi numbrist kirjutame faili sizeof(TYPE2WRITE) baiti.
    /// @return
    /// - \a ==true õnnestus
    /// - \a ==false Ebaõnnestus

    template <class TYPE2WRITE, class TYPE4ARG>
    bool WriteUnsigned(
                       const TYPE4ARG num,
                       ///< Sellest numbrist kirjutame faili õiges järjekorras
                       ///<@a sizeof(TYPE2WRITE) baiti.
                       /// TYPE4ARG={(un)signed char, (un)signed short, (un)signed int, (un)signed long, ...}
                       const TYPE2WRITE writeArg = 0
                       ///< Selle parameetri väärtust ei kasutata kunagi.
                       ///< Väljundfaili kirjutatakse sizeof(TYPE2WRITE) baiti.
                       ///< Baidijärg keeratakse "õigeks" @a STRSOUP::WriteUnsignedToString() funktsiooniga.
                       )
    {
        FSUNUSED(writeArg);
        assert(sizeof (TYPE2WRITE) == 1 || sizeof (TYPE2WRITE) == 2 || sizeof (TYPE2WRITE) == 4);
        assert(sizeof (TYPE2WRITE) <= sizeof (TYPE4ARG));
        //assert( ((sizeof(TYPE2WRITE)==1) && ((num&0x000000ff)==num)) ||
        //        ((sizeof(TYPE2WRITE)==2) && ((num&0x0000ffff)==num)) );
        unsigned char tmp[sizeof (TYPE2WRITE)];
        STRSOUP::WriteUnsignedToString<TYPE2WRITE, TYPE4ARG > (tmp, num); // puhvris baidijärg õigeks
        try
        {
            file.WriteBuf(tmp, sizeof (TYPE2WRITE)); // õige baidijärjega puhver faili
        }
        catch (...)
        {
            return false;
        }
        return true;
    }

    /// Loeb failist 1baidise sümboli.
    //
    /// @return
    /// - @a ==true Sümbol loetud.
    /// - @a ==false EOF või viga.

    bool ReadChar(
                  char* c ///< Siia loeme
                  )
    {
        assert(c != NULL);
        try
        {
            file.ReadChar(c);
        }
        catch (...)
        {
            return false;
        }
        return true;
    }

    /// Kirjutab faili 1baidise sümboli.
    //
    /// @return
    /// - @a ==true Sümbol kirjutatud.
    /// - @a ==false Viga.

    bool WriteChar(
                   char c ///< Selle kirjutame
                   )
    {
        try
        {
            file.WriteChar((char) c);
        }
        catch (...)
        {
            return false;
        }
        return true;
    }

    /// Loeb failist UC2 sümboli.
    //
    /// UC2 peab failis olema Litttle Endian baidijärjega.
    /// @return
    /// - @a ==true Sümbol loetud.
    /// - @a ==false EOF või viga.

    bool ReadChar(
                  FSWCHAR* wChar ///< Siia loeme
                  )
    {
        assert(wChar != NULL);
        return ReadUnsigned<UB2, FSWCHAR > (wChar);
    }

    /// Kirjutab faili UC2 sümboli.
    //
    /// UC2 kirjutatakse faili Litttle Endian baidijärjega.
    /// @return
    /// - @a ==true Sümbol kirjutatud.
    /// - @a ==false EOF või viga.

    bool WriteChar(
                   FSWCHAR wChar ///< Selle kirjutame
                   )
    {
        return WriteUnsigned<UB2, FSWCHAR > (wChar);
    }

    /// Loeb failist etteantud arvu baite.
    //
    /// @return
    /// - @a ==true Puhver loetud.
    /// - @a ==false EOF või viga.

    bool ReadBuffer(
                    void* pBuf, ///< Siia loeme baidid.
                    const int lBytes ///< Niimitu baiti loeme.
                    )
    {
        assert(pBuf != NULL);
        try
        {
            file.ReadBuf(pBuf, lBytes);
        }
        catch (...)
        {
            return false;
        }
        return true;
    }

    /// Loeb failist baite stringipuhvrisse
    //
    /// @return 
    /// - @a ==true Luges vähemalt ühe baidi
    /// - @a ==false Ei lugenud ühtegi baiti (eof)

    /*
    bool AppendToStringBuf(CFSAString& str, const int nBytes)
    {
        char buf [nBytes + 1];
        int n;
        if ((n = (int) CFSFile::ReadBuf(buf, nBytes)) > 0)
        {
            buf[n] = '\0';
            str += buf;
            return true;
        }
        return false;
    }
     */
    int LoeBaite(void* pBuf, const int lBytes)
    {
        return file.ReadBuf(pBuf, lBytes, false); // niimitu baiti luges
    }

    /** Loeb failist 1baidistest sümbolitest (näit UTF8) koosneva rea
     *
     * @param pString Sellesse stringi loeme failist rea
     * @return Kui fail otsas @a false, muidu @a true
     */
    bool ReadLine(CFSAString* pString)
    {
        assert(pString != NULL);
        return ReadString(pString, '\n', true);
    }

    /** Loeb failist 1baidistest sümbolitest (näit UTF8) koosneva @a Trimmed() rea
     *
     * @param[out] pString - Sellesse stringi loeme failist @a Trimmed() rea
     * @return Kui fail otsas @a false, muidu @a true
     */
    bool ReadTrimmedLine(CFSAString* pString)
    {
        assert(pString != NULL);
        return ReadString(pString, '\n', false, true);
    }

    /** Loeb failist UC2 sümbolitest koosneva rea.
     *
     * @param[out] pString - Sellesse stringi loeme failist rea
     * @return Kui fail otsas @a false, muidu @a true
     */
    bool ReadLine(CFSWString* pString)
    {
        assert(pString != NULL);
        return ReadString(pString, (FSWCHAR) '\n', true);
    }

    /** Loeb failist UC2 sümbolitest koosneva @a Trimmed() rea.
     *
     * @param[out] pString - Sellesse stringi loeme failist @a Trimmed() rea
     * @return Kui fail otsas @a false, muidu @a true
     */
    bool ReadTrimmedLine(CFSWString* pString)
    {
        assert(pString != NULL);
        return ReadString(pString, (FSWCHAR) '\n', false, true);
    }

    /** Loeb failist 1baidiseid sümboleid etteantud sümbolini.
     *
     * @param[out] pString - Siia loeme sisendist
     * @param[in] eos - Loeme selle sümbolini (või faililõpuni).
     * Vaikimisi 0.
     * @param[in] inclEos - @a false, kui @a EOS jäetakse stringist
     * välja. @a true, kui @a EOS jäetakse stringi sisse.
     * Vaikimisi @a false
     * @attention String ei lõppe @a EOSiga, kui @a EOF tuli enne @a EOSi
     * @param[in] trim - Kui @a true, siis teeme @a Trim(pString), muidu mitte.
     * Vaikimisi @a false
     * @return Kui EOF siis @a false, muidu @a true
     */
    bool ReadString(CFSAString* pString, const char eos = '\0',
                    const bool inclEos = false, const bool trim = false)
    {
        assert(pString != NULL);
        pString->Empty();
        char c;
        bool failPoleOtsas = true;
        while (failPoleOtsas == true)
        {
            while ((failPoleOtsas = ReadChar(&c)) == true && c != eos) // pole faili/stringi lõpp
                (*pString) += c; // kirjutame sappa juurde
            assert(failPoleOtsas == false || (failPoleOtsas == true && c == eos));
            if (failPoleOtsas == true && inclEos == true)
                (*pString) += c; // lisame lõputunnuse
            if (trim == true)
            {
                pString->Trim();
                if (pString->GetLength() <= 0)
                    continue; // Ingnoreerime ridasid mille pikkus peale trimmimist on null.
            }
            if (failPoleOtsas == true || pString->GetLength() > 0)
                return true;
        }
        return false; // fail otsas
    }

    /** Loeb failist UC2 Little Endian baidijärjega sümboleid etteantud sümbolini.
     *
     * @param[out] pString - Siia loeme sisendist
     * @param[in] eos - Loeme selle sümbolini (või faililõpuni).
     * @param[in] inclEos - @a false, kui @a EOS jäetakse stringist
     * välja. @a true, kui @a EOS jäetakse stringi sisse
     * @attention String ei lõppe @a EOSiga, kui @a EOF tuli enne @a EOSi
     * @param[in] trim - Kui @a true, siis teeme @a Trim(pString), muidu mitte.
     * @return Kui EOF siis @a false, muidu @a true
     */
    bool ReadString(CFSWString* pString, const FSWCHAR eos = (FSWCHAR) '\0',
                    const bool inclEos = false, const bool trim = false)
    {
        assert(pString != NULL);
        pString->Empty();
        FSWCHAR c;
        bool failPoleOtsas = true;
        while (failPoleOtsas == true)
        {
            while ((failPoleOtsas = ReadChar(&c)) == true && c != eos) // pole faili/stringi lõpp
                (*pString) += c; // kirjutame sappa juurde
            assert(failPoleOtsas == false || (failPoleOtsas == true && c == eos));
            if (failPoleOtsas == true && inclEos == true)
                (*pString) += c; // lisame lõputunnuse
            if (trim == true)
            {
                pString->Trim();
                if (pString->GetLength() <= 0)
                    continue; // Ingnoreerime ridsid mille pikkus peale trimmimist on null.
            }
            if (failPoleOtsas == true || pString->GetLength() > 0)
                return true;
        }
        return false; // fail otsas
    }

    void WriteStr(const CFSAString aStr)
    {
        file.WriteBuf(aStr, aStr.GetLength());
    }

    void WriteStr(const CFSWString wStr)
    {
        file.WriteBuf(wStr, wStr.GetLength());
    }

    /// Kirjutab faili 1baidiste sümbolitega stringi.
    //
    /// Vaikimisi kirjtame ilma stringilõputunnuseta.
    /// @return
    /// - \a == true OK
    /// - \a == false Mistahes jama (sh throw)

    bool WriteStringB(
                      const CFSAString* aStr, ///< Selle kirjutame faili.
                      const bool inclNULL = false
                      ///< Kui @a inclNULL:
                      ///< - @a ==true Stringlilõpu 0 kirjutatakse ka faili.
                      ///< - @a ==false Stringilõpu 0 ei kirjutata faili.
                      )
    {
        assert(aStr != NULL);
        try
        {
            if (inclNULL == true)
                file.WriteBuf(*aStr, aStr->GetLength() + 1);
            else
                file.WriteBuf(*aStr, aStr->GetLength());
        }
        catch (...)
        {
            return false;
        }
        return true;
    }

    /// Kirjutab faili ettenatud pikkusega 1baidiste sümbolitega stringi.
    //
    /// @return
    /// - \a == true OK
    /// - \a == false Mistahes jama (sh throw)

    bool WriteString(
                     const char* aStr, ///< Selle kirjutame faili.
                     const int len ///< Niimitu sümbolit kirjutame faili.
                     )
    {
        assert(aStr != NULL && len >= 0);
        return WriteBuffer(aStr, len);
    }

    /// Kirjutab faili ettenatud pikkusega puhvri
    //
    /// @return
    /// - \a == true OK
    /// - \a == false Mistahes jama (sh throw)

    bool WriteBuffer(
                     const void* buf, ///< Selle kirjutame faili.
                     const int len ///< Niimitu sümbolit kirjutame faili.
                     )
    {
        assert(buf != NULL && len >= 0);
        try
        {
            file.WriteBuf(buf, len);
        }
        catch (...)
        {
            return false;
        }
        return true;
    }

    /// Kirjutab faili UC2 sümbolitest koosneva stringi.
    //
    /// Vaikimisi kirjtame ilma stringilõputunnuseta.
    /// UC2 kirjutatakse faili Litttle Endian baidijärjega.
    /// Stringilõputunnust ei kirjuta.
    /// @return
    /// - \a == true OK
    /// - \a == false Mingi jama.

    bool WriteStringB(
                      const CFSWString* wStr, ///< Selle kirjutame faili.
                      const bool inclNULL = false
                      ///< Kui @a inclNULL:
                      ///< - @a ==true Stringlilõpu 0 kirjutatakse ka faili.
                      ///< - @a ==false Stringilõpu 0 ei kirjutata faili.
                      )
    {
        assert(wStr != NULL);
        return WriteStringB((const FSWCHAR*) (*wStr), inclNULL);
    }

    /// Kirjutab faili UC2 sümbolitest koosneva stringi
    //
    /// Vaikimisi kirjtame ilma stringilõputunnuseta.
    /// UC2 kirjutatakse faili Litttle Endian baidijärjega.
    /// Stringilõputunnust ei kirjuta.
    /// @return
    /// - \a == true Ok
    /// - \a == false Mingi jama.

    bool WriteStringB(
                      const FSWCHAR* wStr, ///< Selle kirjutame faili.
                      const bool inclNULL = false
                      ///< Kui @a inclNULL:
                      ///< - @a ==true Stringlilõpu 0 kirjutatakse ka faili.
                      ///< - @a ==false Stringilõpu 0 ei kirjutata faili.

                      )
    {
        assert(wStr != NULL);
        FSWCHAR wChar;
        for (int i = 0; (wChar = wStr[i]) != (FSWCHAR) '\0'; i++)
        {
            if (WriteChar(wChar) == false)
                return false;
        }
        if (inclNULL == true)
        {
            if (WriteChar(wChar) == false)
                return false;
        }
        return true;
    }

    /// Kirjutab faili etteantud pikkusega UC2 sümbolitest koosneva stringi
    //
    /// UC2 kirjutatakse faili Litttle Endian baidijärjega.
    /// @return
    /// - \a == true OK
    /// - \a == false Mingi jama.

    bool WriteString(
                     const FSWCHAR* wStr, ///< Selle kirjutame faili.
                     const int len ///< Niimitu sümbolit kirjutame faili.
                     )
    {
        assert(wStr != NULL && len >= 0);
        for (int i = 0; i < len; i++)
        {
            if (WriteChar(wStr[i]) == false)
                return false;
        }
        return true;
    }

    /** Lugemise/kirjutamise järg failis ettentud kohale
     *
     * @param pos Mihe parameetriga @a mode määratud positsiooni suhtes
     * @param mode Selle suhtes nihutame @a pos võrra.
     * Võimalikud väärtused:
     * \a SEEK_SET faili algusest (vaikeväärtus),
     * \a SEEK_CUR jooksvast positsioonist,
     * \a SEEK_END faili lõpust.
     * @return Misiganes jama korral @a false, muidu @a true
     */
    bool Seek(const long pos, const int mode = SEEK_SET)
    {
        try
        {
            file.Seek(pos, mode);
        }
        catch (...)
        {
            return false;
        }
        return true;
    }

    /// Jooksev positsioon failist lugemiseks/kirjutamiseks.
    //
    /// Klassikalise tell() funktsiooni analoog.
    /// @return
    /// - \a >=0L Jooksev positsioon.
    /// - \a ==-1L Viga

    long Tell(void)
    {
        return (long) file.Tell();
    }

    /// Sulgeb faili.
    //
    /// Kui eelnevalt kasutati Open(FILE *) funktsiooni 
    /// (argumendiks reeglina @a stdin, @a stdout või @a stderr),
    /// siis faili ei suleta.
    /// @return
    /// - \a ==true: OK
    /// - \a ==false: Viga

    bool Close(void)
    {
        if (dontClose == false) // polnud std-sisend/väljund
        {
            try
            {
                file.Close();
            }
            catch (...)
            {
                return false;
            }
        }
        file.Detach();
        return true;
    }

    ~CPFSFile(void)
    {
        Close();
    }
    bool dontClose;

protected:

    class CFriendFile : public CFSFile
    {
    public:

        void Attach(FILE *pFile)
        {
            m_pFile = pFile;
        }

        void Detach()
        {
            m_pFile = 0;
        }
    } file;
};

typedef long long PROGRESSIMOOTJA;

const static PROGRESSIMOOTJA progressEiMidagi = 0x0LL; ///< Ei kuva midagi.
const static PROGRESSIMOOTJA progressKriips = 0x0000000002000000LL;
///< Kriips   (::MF_KUVAPROGR_KR).
///< Peab sobima mrflagsh.h/MF_KUVAPROGR_* bittidega.
const static PROGRESSIMOOTJA progressProtsent = 0x0000002000000000LL;
///< Protsent (::MF_KUVAPROGR_PR).
///< Peab sobima mrflagsh.h/MF_KUVAPROGR_* bittidega.
const static PROGRESSIMOOTJA progressNumber = 0x0000000004000000LL;
///< Number   (::MF_KUVAPROGR_NR).
///< Peab sobima mrflagsh.h/MF_KUVAPROGR_* bittidega.
const static PROGRESSIMOOTJA progressAeg = 0x0000004000000000LL;
///< Number   (::MF_KUVAPROGR_TM).
///< Peab sobima mrflagsh.h/MF_KUVAPROGR_* bittidega.


/// Klass progressinäidiku kuvamiseks.

class PROGRESS
{
public:
    /*
    typedef long long PROGRESSIMOOTJA;

    const static PROGRESSIMOOTJA eiMidagi = 0x0LL; ///< Ei kuva midagi.
    const static PROGRESSIMOOTJA kriips   = 0x0000000002000000LL;
                    ///< Kriips   (::MF_KUVAPROGR_KR).
                    ///< Peab sobima mrflagsh.h/MF_KUVAPROGR_* bittidega.
    const static PROGRESSIMOOTJA protsent = 0x0000002000000000LL;
                    ///< Protsent (::MF_KUVAPROGR_PR).
                    ///< Peab sobima mrflagsh.h/MF_KUVAPROGR_* bittidega.
    const static PROGRESSIMOOTJA number   = 0x0000000004000000LL;
                    ///< Number   (::MF_KUVAPROGR_NR).
                    ///< Peab sobima mrflagsh.h/MF_KUVAPROGR_* bittidega.
    const static PROGRESSIMOOTJA aeg   = 0x0000004000000000LL;
                    ///< Number   (::MF_KUVAPROGR_TM).
                    ///< Peab sobima mrflagsh.h/MF_KUVAPROGR_* bittidega.
     */

    PROGRESSIMOOTJA tyyp;
    unsigned long counter;
    CPFSFile* in; ///< sisse: Mõõdetav fail.
    double failiSuurus; ///< sisse: Mõõdetava faili suurus.
    time_t algusAeg;

    /// 2in1 - Argumentidega ja argumentideta konstruktor.

    PROGRESS(
             PROGRESSIMOOTJA misLiiki, ///< sisse: Kastutava progressimõõdiku tüüp.
             CPFSFile& _in_ ///< sisse: Mõõdetav fail.
             ) : kriipsud("|/-\\")
    {
        InitClassVariables();
        Start(misLiiki, &_in_);
    }

    /// 2in1 - Argumentidega ja argumentideta konstruktor.

    PROGRESS(
             PROGRESSIMOOTJA misLiiki = progressEiMidagi, ///< sisse: Kastutava progressimõõdiku tüüp.
             CPFSFile* _in_ = NULL ///< sisse: Mõõdetav fail.
             ) : kriipsud("|/-\\")
    {
        InitClassVariables();
        Start(misLiiki, _in_);
    }

    /// Argumentidega konstruktor.

    PROGRESS(
             CPFSFile* _in_ ///< sisse: Mõõdetav fail.
             ) : kriipsud("|/-\\")
    {
        InitClassVariables();
        Start(_in_);
    }

    /// Initsialiseerimiseks.
    //
    /// Initsialiseerib argumentideta konstrukori
    /// abil loodud klassi.
    /// @return
    /// - \a ==true Ok
    /// - \a ==false Jama

    bool Start(
               PROGRESSIMOOTJA misLiiki = progressEiMidagi, ///< sisse: Kastutava progressimõõdiku tüüp.
               CPFSFile* _in_ = NULL ///< sisse: Mõõdetav fail.
               )
    {
        InitClassVariables();
        if ((in = _in_) == NULL || (FILE*) * in == stdin || in->dontClose)
        {
            tyyp = progressEiMidagi;
            return ClassInvariant();
        }
        tyyp = misLiiki;

        if ((tyyp & progressAeg) == progressAeg)
            time(&algusAeg);

        if ((tyyp & progressProtsent) != progressProtsent)
            return true;
        //in->Seek(0L,SEEK_END);
        failiSuurus = (double) in->Tell();
        //in->Seek(0L);
        fprintf(stderr, "  0%% [");
        for (int i = 0; i < kokkuKriipse; i++)
            fprintf(stderr, " ");
        fprintf(stderr, "]\r");
        return ClassInvariant();
    }

    /// Initsialiseerimiseks.
    //
    /// Initsialiseerib argumentideta konstrukori
    /// abil loodud klassi.
    /// @return
    /// - \a ==true Ok
    /// - \a ==false Jama

    bool Start(
               CPFSFile* _in_ ///< sisse: Mõõdetav fail.
               )
    {
        assert(_in_ != NULL);
        return Start(progressProtsent, _in_);
    }

    /// Initsialiseerimiseks.
    //
    /// Initsialiseerib argumentideta konstrukori
    /// abil loodud klassi.
    /// @return
    /// - \a ==true Ok
    /// - \a ==false Jama

    bool Start(
               CPFSFile* _in_, ///< sisse: Mõõdetav fail.
               PROGRESSIMOOTJA misLiiki ///< sisse: Kastutava progressimõõdiku tüüp.
               )
    {
        return misLiiki == progressProtsent ? Start(_in_) : Start(misLiiki);
    }

    /// Kuvab mõõdiku uue seisu.

    void Progress(void)
    {
        counter++;
        if ((tyyp & progressKriips) == progressKriips)
            fprintf(stderr, "%c\r", kriipsud[counter % 4]);
        else if ((tyyp & progressNumber) == progressNumber)
            fprintf(stderr, "%8ld\r", counter);
        else if ((tyyp & progressProtsent) == progressProtsent)
        {
            double pos = (double) (in->Tell());
            double prots = pos * 100.0 / failiSuurus;
            if (prots > eelmineProts)
            {
                fprintf(stderr, "%3.0f%%", prots);
                eelmineProts = prots;
                int nKriipsu = ((int) prots) / yksKriips;
                if (nKriipsu > eelmineNkriipsu)
                {
                    int i;
                    fprintf(stderr, " [");
                    for (i = 0; i < nKriipsu; i++)
                        fprintf(stderr, "=");
                    if (i < kokkuKriipse)
                        fprintf(stderr, ">");
                    eelmineNkriipsu = nKriipsu;
                }
                fprintf(stderr, "\r");
            }
        }
        else if (tyyp == progressAeg) // kui li ainult aeg, siis kuvame kulunud aega
        {
            time_t jooksevAeg;
            time(&jooksevAeg);
            fprintf(stderr, "%10ld sekundit\r", (long) (jooksevAeg - algusAeg));
        }
        assert(ClassInvariant());
    }

    void Stop(void)
    {
        if (tyyp != progressEiMidagi) // kustuta ära
        {
            for (int i = 0; i < kokkuKriipse + 7; i++)
                fprintf(stderr, " ");
            fprintf(stderr, "\r");
        }
        if ((tyyp & progressAeg) == progressAeg)
        {
            time_t jooksevAeg;
            time(&jooksevAeg);
            fprintf(stderr, "%10ld sekundit\n", (long) (jooksevAeg - algusAeg));
        }
    }

    /// Destrukor.

    ~PROGRESS(void)
    {
        Stop();
    }

    /// Klassi invariant.
    //
    /// Klassi invariant võimaldab kontrollida,
    /// kas argumentidega konstruktor õnnestus või ei.
    /// @return
    /// - \a ==true klass on OK
    /// - \a ==false klass on vigane

    bool ClassInvariant(void)
    {
        if ((tyyp & progressProtsent) == progressProtsent)
        {
            return in != NULL && failiSuurus >= 0L && counter >= 0L;
        }
        return failiSuurus == 0L && counter >= 0L;
    }
private:

    void InitClassVariables(void)
    {
        kokkuKriipse = 50;
        yksKriips = 100 / kokkuKriipse;
        //kriipsud = "|/-\\";
        eelmineProts = -1L;
        eelmineNkriipsu = -1L;

        counter = 0;
        in = NULL;
        failiSuurus = 0L;
        tyyp = progressEiMidagi;
    }
    long kokkuKriipse;
    long yksKriips;

    const char *kriipsud;
    //long eelmineProts;
    double eelmineProts;
    long eelmineNkriipsu;
};

/// Loeb failist ridade massiivi ja kirjutab faili(le sappa) massiivist ridasid

template <class REC, class KEY>
class TXSTRARR :
public TMPLPTRARRAYBIN<REC, KEY>,
public CPFSFile
{
public:
    /// Argumentideta konstruktor
    //
    /// @throw
    /// VEAD, ....

    TXSTRARR(void) : TMPLPTRARRAYBIN<REC, KEY>(50, 50)
    {
    };

    /// Lisab etteantud nimega failist loetud read massiivi.
    //
    /// @return
    /// - @a ==true Kõik läks kenasti
    /// - @a ==false Faili avamine äpardus
    /// @throw VEAD, ...

    bool ReadLines(const FSTCHAR *fail)
    {
        REC xstr;

        if (CPFSFile::Open(fail, FSTSTR("rb")) == false)
        {
            return false;
        }
        while (ReadLine(&xstr) == true)
        {
            xstr.TrimRight();
            TMPLPTRARRAYBIN<REC, KEY>::AddClone(xstr); // jama korral siit throw
        }
        Close();
        return true;
    }

    /// Loob ette etteantud nimega faili ja kirjutab sinna massiivist read
    //
    /// Igale reale kirjutatakse
    /// reavahetus (012) sappa.
    /// @return
    /// - @a ==true Kõik läks kenasti
    /// - @a ==false Faili avamine äpardus
    /// @throw
    /// VEAD, ...

    bool KirjutaReadFaili(
                          const FSTCHAR *fail) // sellesse faili kirjutame stringid
    {
        if (CPFSFile::Open(fail, FSTSTR("wb+")) == false) // avame tekstifaili
            return false;
        for (int i = 0; i < TMPLPTRARRAYBIN<REC, KEY>::idxLast; i++) // uhame stringid välja
        {
            if (CPFSFile::WriteStringB(TMPLPTRARRAYBIN<REC, KEY>::rec[i]) == false)
                throw VEAD(ERR_X_TYKK, ERR_WRITE, __FILE__, __LINE__, "$Revision: 1236 $");
            // reavahetus sappa
            if ((TMPLPTRARRAYBIN<REC, KEY>::operator[](i)->charSize == sizeof (char)
                ? CPFSFile::WriteString("\n", 1)
                : CPFSFile::WriteString(FSWSTR("\n"), 1)) == false)
                throw VEAD(ERR_X_TYKK, ERR_WRITE, __FILE__, __LINE__, "$Revision: 1236 $");
        }
        CPFSFile::Close(); // fail kinni
        return true; // happy end
    }

    /// Lisab etteantud nimega faili sappa massiivist read
    //
    /// @return
    /// - @a ==true Kõik läks kenasti
    /// - @a ==false Midagi läks nässu (IO-viga, mälu otsas vms).
    /// @throw
    /// VEAD, ...

    bool KirjutaStringidFailileSappa(
                                     const FSTCHAR* fail, // selle faili sappa kirjutame stringid
                                     long* algusNihe, // sellest positsioonist algavad
                                     int* pikkus) // niimitu baiti kirjutasin
    {
        if (CPFSFile::Open(fail, FSTSTR("rb+")) == false) // avame sõnastikufaili
        {
            return false;
        }
        CPFSFile::Seek(0L, SEEK_END); // hüppame lõppu
        *algusNihe = CPFSFile::Tell(); // küsime alguspostsiooni

        bool ret = true;
        for (int i = 0; ret == true && i < TMPLPTRARRAYBIN<REC, KEY>::idxLast; i++) // uhame stringid välja
        {
            ret = WriteStringB(TMPLPTRARRAYBIN<REC, KEY>::rec[i], true);
        }
        *pikkus = (int) (CPFSFile::Tell() - *algusNihe); // arvutame pikkuse
        CPFSFile::Close(); // fail kinni

        return ret;
    }
};

//--------------------------------------------

/// UNICODEi ja SGML olemite vahelise teisendustabeli element

class SGML_UC
{
public:

    enum
    {
        sortBySGMLStr, ///< Funktsioon Compare() järjestab SGML olemite järgi
        sortByUCchar ///< Funktsioon Compare() järjestab UNICODEi sümbolite järgi
    };

    CFSAString sgml; ///< UNICODi sümbolile vastavat SGML olemit esitav string
    WCHAR uc; ///< SGML olemit esitavale stringile vastav UNICODEi sümbol

    /// Argumentideta konstruktor

    SGML_UC(void)
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

    /// Argumentidega konstruktor

    SGML_UC(
            const char* _sgml_, ///< SGML olemit esitav string
            const WCHAR _uc_ ///< Vastav UNICODE'i sümbol
            )
    {
        try
        {
            InitClassVariables();
            Start(_sgml_, _uc_);
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /// Copy-konstruktor

    SGML_UC(
            const SGML_UC& rec ///< Kloonitav kirje
            )
    {
        try
        {
            InitClassVariables();
            Start(rec);
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    /// Initsialiseerimiseks

    void Start(
               const SGML_UC& rec ///< Kloonitav kirje
               )
    {
        //Stop(); -- pole tarvidust
        Start(rec.sgml, rec.uc);
    }

    /// Initsialiseerimiseks

    void Start(
               const char* _sgml_, ///< SGML olemit esitav string
               const WCHAR _uc_ ///< Vastav UNICODEi sümbol
               )
    {
        //Stop(); -- pole tarvidust
        sgml = _sgml_;
        uc = _uc_;
    }

    /// Loeb failist ühe kirje
    //
    /// Trelliga algavaid ridu ignoreeritakse (kommnetaar).
    /// Loeb failist järjekordse rea, mis peab olema kujul:@n
    /// @a sgml-olem @a white-space @a heksakood
    /// @return
    /// - @a ==true Kirje sisseloetud
    /// - @a ==false Fail otsas

    bool Start(
               CPFSFile& file ///< Sisendfail (standardsisend lubatud)
               )
    {
        //Stop(); -- pole tarvidust
        CFSAString rida;
        for (;;)
        {
            if (file.ReadLine(&rida) == false)
                return false; // eof
            rida.TrimLeft();
            if (rida.GetLength() > 0 && rida[0] != '#') // pole kommentaar
            {
                int pos = (int) rida.Find(';');
                if (pos <= 2)
                    throw VEAD(ERR_X_TYKK, ERR_ARGVAL, __FILE__, __LINE__, "$Revision: 1236 $");
                sgml = rida.Left(pos + 1);
                //TODO: Mul peaks olema mingi stringist arvu lugemise funktsioon
                for (pos += 2; rida[pos] == ' ' || rida[pos] == '\t'; pos++)
                    ;
                int n;
                for (uc = 0;; pos++)
                {
                    if (rida[pos] >= '0' && rida[pos] <= '9')
                        n = rida[pos] - '0';
                    else if (rida[pos] >= 'A' && rida[pos] <= 'F')
                        n = rida[pos] - 'A' + 10;
                    else if (rida[pos] >= 'a' && rida[pos] <= 'f')
                        n = rida[pos] - 'a' + 10;
                    else
                        return true;
                    uc = uc * 16 + n;
                }
            }
        }
    }

    /// Taastab argumentideta konstruktori järgse seisu

    void Stop(void)
    {
        InitClassVariables();
    }

    /// Kirjete võrdlemiseks

    int Compare(
                const SGML_UC* rec, ///< Viit kirjele, millega võrdleme
                const int sortOrder ///< Määrab, mis on kirjes võtmeks
                )
    {
        if (rec == NULL)
            throw VEAD(ERR_X_TYKK, ERR_ARGVAL, __FILE__, __LINE__, "$Revision: 1236 $");
        int ret;
        switch (sortOrder)
        {
        case sortBySGMLStr:
            if ((ret = sgml.Compare(rec->sgml)) == 0)
                ret = (int) uc - (int) (rec->uc);
            return ret;
        case sortByUCchar:
            if ((ret = (int) uc - (int) (rec->uc)) == 0)
                ret = strcmp(sgml, rec->sgml);
            return ret;
        }
        throw VEAD(ERR_X_TYKK, ERR_ARGVAL, __FILE__, __LINE__, "$Revision: 1236 $");
    }

    /// Võrdleb kirje võtit etteantud võtmega

    int Compare(
                const WCHAR* key, ///< Võtmeks on viit UNICODE'i sümbolile
                const int sortOrder = sortByUCchar
                )
    {
        assert(key != NULL);
        if (key == NULL)
            throw VEAD(ERR_X_TYKK, ERR_ARGVAL, __FILE__, __LINE__);
        
        //assert(sortOrder == sortByUCchar);
        //if (sortOrder != sortByUCchar)
        //    throw VEAD(ERR_X_TYKK, ERR_ARGVAL, __FILE__, __LINE__);
        
        return (int) uc - (int) * key;
    }

    /// Võrdleb kirje võtit etteantud võtmega

    int Compare(
                const CFSAString* key, ///< Võtmeks on SGML olem
                const int sortOrder = sortBySGMLStr
                )
    {
        if (key == NULL || sortOrder != sortBySGMLStr)
            throw VEAD(ERR_X_TYKK, ERR_ARGVAL, __FILE__, __LINE__, "$Revision: 1236 $");
        return sgml.Compare(*key);
    }

    /// Initsaliseeritud klassi invariant

    bool ClassInvariant(void)
    {
        return sgml != NULL && uc != (WCHAR) 0;
    }

    /// Argmentideta konstruktori järgne klassi invariant

    bool EmptyClassInvariant(void)
    {
        return sgml == NULL && uc == (WCHAR) 0;
    }

private:

    /// initsialiseerib klassi andmed konstruktoris

    void InitClassVariables(void)
    {
        sgml.Empty();
        uc = (WCHAR) 0;
    }
};

/// Klass stringi teisendamiseks UNICODEi või UNICODEist

class CONV_HTML_UC2
{
public:
    /// Argumentideta konstruktor

    CONV_HTML_UC2(void)
    {
        InitClassVariables();
    }

    /// Argumentidega konstruktor
    //
    /// Kui @a koodiTabel==PFSCP_HTMLEXT ja toimub teisendamine @a UNICODEi:
    /// - @a _autosgml_==true Lubatud SGML olemite hulga moodustavad failis "sgml-uc-cnv.txt" loetletud olemid
    /// ja kõik olemid kujul &kümnendkood;
    /// - @a _autosgml_==false Lubatud SGML olemite hulga moodustavad ainult failis "sgml-uc-cnv.txt"
    /// loetletud olemid
    /// - @a _ignoramp_==false Ampersand peab alustama lubatud hulka kuuluvat SGML olemit.
    /// Kõik tekstis ampersandina mõeldud ampersandid peavad olema esitatud SGNL olemina ("&amp;").
    ///
    /// Kui @a koodiTabel==PFSCP_HTMLEXT ja toimub teisendamine @a UNICODEist:
    /// - @ _autosgml_==false Ainult failis "sgml-uc-cnv.txt" loetletud UNICODEi sümbolid
    /// vastavateks SGML olemiteks, ülejäänud mitte-ASCII sümbolid annavad vea
    /// - @ _autosgml_==true Failis "sgml-uc-cnv.txt" loetletud UNICODEi sümbolid vastavateks SGML olemiteks,
    /// ülejäänud mitte-ASCII sümbolid &kümnendkood; kujul SGML olemiteks

    CONV_HTML_UC2(
                  const FSTCHAR* path, ///< Kui @a path!=NULL,
                  ///< siis nendest kataloogidest otsime teisendustabelit
                  ///< sisaldavat faili @a "sgml-uc-cnv.txt"
                  const bool _ignoramp_ = false,
                  const bool _autosgml_ = false
                  )
    {
        try
        {
            InitClassVariables();
            Start(path, _ignoramp_, _autosgml_);
        }
        catch (...)
        {
            Stop();
            throw;
        }
    }

    ///  Klassi (argumentideta konstruktori järgseks) initsialiseerimiseks
    void Start(
               const FSTCHAR* path = NULL, ///< Kui @a path!=NULL,
               ///< siis nendest kataloogidest otsime teisendustabelit
               ///< sisaldavat faili @a "sgml-uc-cnv.txt"
               const bool _ignoramp_ = false,
               const bool _autosgml_ = false
               );

    /// Teisendame sisendstringi UNICODEi
    //
    /// Kasutab konstruktori või Start() funktsiooni poolt määratud
    /// ignoramp ja autosgml parameetrite väärtusi.
    void ConvToUc(
                  CFSWString& wStr, ///< Väljundstring
                  const CFSAString& aStr, ///< Sisendstring
                  const PFSCODEPAGE koodiTabel ///< Sisendstringi kooditabel
                  );

    /// Teisendame sisendstringi UNICODEist
    //
    /// Kasutab konstrultori või Start() funktsiooni poolt määratud
    /// ignoramp ja autosgml parameetrite väärtusi.
    void ConvFromUc(
                    CFSAString& aStr, ///< Väljundstring
                    const PFSCODEPAGE koodiTabel, ///< Väljundstringi kooditabel
                    const CFSWString& wStr ///< Sisendstring
                    );


    /// Teisendame sisendstringi väljundstringiks
    //
    /// PFSCP_HTMLEXT kooditabeli kasutamiseks peab see olema
    /// konstruktoris või Start() funktsiooniga määratud.
    void ConvFromTo(
                    CFSAString& vStr, ///< Väljunstring
                    const PFSCODEPAGE vKoodiTabel, ///< Väljundstringi kooditabel
                    const CFSAString& sStr, ///< Sisendstring
                    const PFSCODEPAGE sKoodiTabel ///< Sisendstringi kooditabel
                    );

    /// Taastab argumentideta konstruktori järgse seisu
    void Stop(void);

    /// Destruktor

    ~CONV_HTML_UC2(void)
    {
        Stop();
    }

private:
    /// Muutujate esialgseks initsialiseerimiseks kontruktorites

    void InitClassVariables(void)
    {
        sgml_stringi_max_pikkus = -1;
        ignoramp = false;
        autosgml = false;
    }

    bool ignoramp;
    bool autosgml;
    int sgml_stringi_max_pikkus; ///< Kõige pikem SGML olemi tabelis
    TMPLPTRARRAYLIN<SGML_UC, CFSAString> sgml2uc; ///< Tabel SGML olemite tõlkimiseks UNICODEi
    TMPLPTRARRAYLIN<SGML_UC, WCHAR> uc2sgml; ///< Tabel UNICODEist SGML olemite tegemiseks

};

/// Teisendab UC2 faili mingi 8bitise kooditabeliga failiks või vastupidi
//
/// UC2 failis kasutatakse
/// Litle Endian baidijärge.
/// @n @a BOM (byte order mark) on:
/// - @a FFFE failis (FEFF unicode-i sümbolis) little endian baidijärje korral (x86 arhitektuur)
/// - @a FEFF failis (FFEF unicode-i sümbolis) big endaian baidijärje korral (SUN)
void ConvFile(
              CPFSFile &out, ///< Väljundfail
              const PFSCODEPAGE outKoodiTabel, ///< Väljundfaili kooditabel
              CPFSFile &in, ///< Sisendfail
              const PFSCODEPAGE inKoodiTabel, ///< Sisendfaili kooditabel
              CONV_HTML_UC2 &cnv, ///< Stringiteisendaja
              const bool feff, ///< UNICODE'i korral määrab BOMi käsitlemise viidi
              PROGRESSIMOOTJA progr ///< Määrab edenemise kuvamise viisi
              );

#endif
