
#if !defined( FSXSTRING_H )
#define FSXSTRING_H

#include <assert.h>
#include "post-fsc.h"

/** Lisavidinatega @a CFSWString */
class FSXSTRING : public CFSWString
{
public:
    /** String koosneb sellise baidisuuresega märkidest */
    enum { charSize = sizeof (WCHAR) };

    /** Argumentideta konstruktor */
    FSXSTRING()
    {
    }

    /** Initsialiseerib @a CFSWString tüüpi stringist */
    FSXSTRING(const CFSWString& str) : CFSWString(str)
    {
    }

    /** Initsialiseerib @a CFSAString tüüpi UTF8 kodeeringus stringist */
    FSXSTRING(const CFSAString& str)
    {
        Start(str);
    }

    /** Initsialiseerib @a FSWCHAR tüüpi 0-lõpulisest viidast */
    FSXSTRING(const FSWCHAR* pStr) : CFSWString(pStr)
    {
    }

    /** Initsialiseerib @a char tüüpi utf8 kodeeringis 0-lõpulisest viidast */
    FSXSTRING(const char* pStr)
    {
        Start(pStr);
    }

    /** Initsialiseerib @a FSWCHAR tüüpi viida @a lLength esiemsest tähest */
    FSXSTRING(const FSWCHAR* pStr, INTPTR lLength) : CFSWString(pStr, lLength)
    {
    }

    FSXSTRING(FSWCHAR wChar, INTPTR lRepeat = 1) : CFSWString(wChar, lRepeat)
    {
    }

    /** Initsialiseerib @a CFSWString tüüpi stringist */
    void Start(const CFSWString& str)
    {
        *this = CFSWString::operator=(str);
    }

    /** Initsialiseerib @a CFSAString tüüpi UTF8 kodeeringus stringist */
    void Start(const CFSAString& str)
    {
        *this = FSStrAtoW(str, FSCP_UTF8);
    }

    /** Initsialiseerib @a char tüüpi utf8 kodeeringis 0-lõpulisest viidast */
    void Start(const char* pStr)
    {
        CFSAString str(pStr);
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
    int Compare(const CFSWString *s, const int sortOrder = 0) const
    {
        FSUNUSED(sortOrder);
        assert(s != NULL);
        assert(GetLength() >= 0);
        assert(s->GetLength() >= 0);

        if (GetLength() == 0)
        {
            if (s->GetLength() == 0)
                return 0;
            return -1;
        }
        if (s->GetLength() == 0)
             return 1;
        return CFSWString::Compare(*s);
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
    int Compare(const CFSWString &s, const int sortOrder = 0) const
    {
        FSUNUSED(sortOrder);
        assert(s != NULL);
        assert(GetLength() >= 0);
        assert(s.GetLength() >= 0);

        if (GetLength() == 0)
        {
            if (s.GetLength() == 0)
                return 0;
            return -1;
        }
        if (s.GetLength() == 0)
             return 1;
        return CFSWString::Compare(s);
    }
};

#endif



