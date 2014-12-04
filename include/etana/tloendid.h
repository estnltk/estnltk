#if !defined( TLOENDID_H )
#define TLOENDID_H

// 2002.04.04

#include <assert.h>
#include <stdlib.h>
//=========================================================
#include "mrflags.h"
#include "post-fsc.h"
#include "fsxstring.h"
#include "rooma.h"
#include "tmplptrarrayblabla.h"

#define FSCHAR_UNICODE

#if defined( FSCHAR_UNICODE )   // kasutame UNICODE kooditabelit

#define APOSTROOF (FSWCHAR)0x2019 // ülaindeks 9  

#define S_O_TILDE (FSWCHAR)0x00D5 
#define V_O_TILDE (FSWCHAR)0x00F5 
#define V_O_UML   (FSWCHAR)0x00F6    

#define V_SH      (FSWCHAR)0x0161 
/* 1/4 */
#define S_SH      (FSWCHAR)0x0160 
#define V_ZH      (FSWCHAR)0x017E 
/* 1/2 */
#define S_ZH      (FSWCHAR)0x017D 

#else
#error Defineeri FSCHAR_UNICODE
#endif

int FSStrCmpW0(const FSWCHAR *s1, const FSWCHAR *s2);

/** Lõikab sisendstringist XML-märgendid välja ja teeb olemid vastavateks 
    * märkideks
    *
    * @param[in,out] CFSWString& @wStr
    * sisendstring string
    * @param[in] bool @vajaPuhastada
    * Vaikimisi vajaPuhastada==true. Kui vajaPuhastada==true kustutame olemid 
    * ja märgendid, muidu jääb muutmata.
    */
template <class S_TYYP, class C_TYYP>
void PuhastaXMList(S_TYYP& xStr, bool vajaPuhastada=true)
{
    //assert(wStr.GetLength() > 0);
    if(vajaPuhastada==false || xStr.GetLength()==0)
        return;
    int j;
    for (int i = 0; i < xStr.GetLength(); )
    {
        switch (xStr[i])
        {
        case (C_TYYP) '<': // Märgendi algus
            j=xStr.Find((C_TYYP)'>', i+1); // otsime üles märgendi lõpu
            if(j<=i) // märgendit lõpetav märk '>' puudu
                throw(VEAD(ERR_X_TYKK, ERR_MINGIJAMA, __FILE__,__LINE__, "Vigane XML margend"));
            xStr.Delete(i, j-i+1); // viskame märgendi vahelt välja
            break;
        // tegeleme olemitega
        case (C_TYYP) '&':
            if(xStr.ContainsAt(i, EritiSobiViit(C_TYYP, "&gt;"))==true)
            {
                xStr[i++]=(C_TYYP)'>';
                xStr.Delete(i,3);
            }
            else if(xStr.ContainsAt(i, EritiSobiViit(C_TYYP, "&lt;"))==true)
            {
                xStr[i++]=(C_TYYP)'<';
                xStr.Delete(i,3);
            }
            else if(xStr.ContainsAt(i, EritiSobiViit(C_TYYP, "&amp;"))==true)
            {
                xStr[i++]=(C_TYYP)'&';
                xStr.Delete(i,4);
            }
            else if(xStr.ContainsAt(i, EritiSobiViit(C_TYYP, "&apos;"))==true)
            {
                xStr[i++]=(C_TYYP)'\'';
                xStr.Delete(i,5);
            }
            else if(xStr.ContainsAt(i, EritiSobiViit(C_TYYP, "&quot;"))==true)
            {
                xStr[i++]=(C_TYYP)'"';
                xStr.Delete(i,5);
            }
            else if(xStr.ContainsAt(i, EritiSobiViit(C_TYYP,"&#"))==true)
            {
                int j=xStr.Find((C_TYYP)';', i+1); // otsime üles olemi lõpu
                if(j<=i) // märgendit lõpetav märk ';' puudu
                    throw(VEAD(ERR_X_TYKK, ERR_MINGIJAMA, __FILE__,__LINE__, 
                            NULL, "Vigane &#kood; olem", (const C_TYYP*)xStr));
                unsigned int kood=0;
                for(int k=i+2; k<j; k++)
                    kood = 10*kood + (unsigned int)(xStr[k]) - 
                                                (unsigned int)(C_TYYP)'0';
                xStr[i++]=(C_TYYP)kood;
                xStr.Delete(i, j-i+1); // olem koodiga asendatud
                break;
            }
            else
                // lubatud ainult 5 XMLis eeldefineeritud olemit
                // ja olemeid kujul &#kood;
                throw(VEAD(ERR_X_TYKK, ERR_MINGIJAMA, __FILE__,__LINE__, 
                            NULL, "Vigane olem", (const C_TYYP*)xStr));
            break;
        default:
            i++;
            break;
        }
    }
}

/** Erinevate tähehulkadega opereerimiseks */
class TaheHulgad
{
public:

    inline static int FSxCHCMP(const FSxCHAR* c1ptr, const FSxCHAR* c2ptr)
    {
        assert(c1ptr != NULL && c2ptr != NULL);
        return FSxCHCMP(*c1ptr, *c2ptr);
    }

    inline static int FSxCHCMP(const FSxCHAR c1, const FSxCHAR c2)
    {
        if (c1 < c2)
            return -1;
        else if (c1 > c2)
            return 1;
        return 0;
    }

    /** Kas on täishäälik */
    inline static bool OnTaishaalik(const FSxCHAR c)
    {
        return taish.Find(c) == -1 ? false : true;
    }

    /** Kas on kaashäälik (hulk @a kaash) */
    inline static bool OnKaashaalik(const FSxCHAR c)
    {
        return kaash.Find(c) == -1 ? false : true;
    }

    /** Kas on kaashäälik (hulk @a kaash1) */
    inline static bool OnKaashaalik1(const FSxCHAR c)
    {
        return kaash1.Find(c) == -1 ? false : true;
    }

    inline static bool OnAeiu(const FSxCHAR c)
    {
        return aeiu.Find(c) == -1 ? false : true;
    }

    inline static bool OnKpt(const FSxCHAR c)
    {
        return kpt.Find(c) == -1 ? false : true;
    }

    inline static bool OnLmnr(const FSxCHAR c)
    {
        return lmnr.Find(c) == -1 ? false : true;
    }

    inline static bool OnUs_ees(const FSxCHAR c)
    {
        return us_ees.Find(c) == -1 ? false : true;
    }

    inline static bool OnMatemaatika1(const FSxCHAR c)
    {
        return matemaatika1.Find(c) == -1 ? false : true;
    }

    inline static bool OnHelitu(const FSxCHAR c)
    {
        return helitu.Find(c) == -1 ? false : true;
    }

    inline static bool OnWhiteSpace(const FSWCHAR c)
    {
        return wWhiteSpace.Find(c) == -1 ? false : true;
    }

    inline static bool OnLisaKr6nks(const FSxCHAR c)
    {
        return lisaKr6nksudeStr.Find(c) == -1 ? false : true;
    }

    /** Kas on liitsõnapiir */
    inline static bool OnLiitsonaPiir(const FSxCHAR c)
    {
        return c == liitSonaPiir[0];
    }

    /** Indeksile vastav märk väiketäheks */
    inline static FSWCHAR SuurPisiks(const CFSWString* wStr,const int idx)
    {
        assert(idx >= 0 && idx < wStr->GetLength());
        return FSToLower((*wStr)[idx]);
    }

    /** Indeksile vastav märk suurtäheks */
    inline static FSWCHAR PisiSuureks(const CFSWString* wStr, const int idx)
    {
        assert(idx >= 0 && idx < wStr->GetLength());
        return FSToUpper((*wStr)[idx]);
    }

    /** Kas indeksiga antud positsioonis on suurtäht */
    inline static bool OnSuur(const CFSWString* wStr, const int idx)
    {
        assert(idx >= 0 && idx < wStr->GetLength());
        return TaheHulgad::OnTaht(wStr, idx) && 
                                ((*wStr)[idx] == FSToUpper((*wStr)[idx]));
    }

    /** Kas indeksiga antud positsioonis on väiketäht */
    inline static bool OnPisi(const CFSWString* wStr, const int idx)
    {
        assert(idx >= 0 && idx < wStr->GetLength());
        return TaheHulgad::OnTaht(wStr, idx) && 
                                    ((*wStr)[idx] == FSToLower((*wStr)[idx]));
    }

    /** Kas indeksiga antud positsioonis on täht */
    inline static bool OnTaht(const CFSWString* wStr, const int idx)
    {
        assert(idx >= 0 && idx < wStr->GetLength());
        if (wStr->GetLength() < 1)
            return false;
        FSWCHAR c = (*wStr)[idx];
        return (FSToLower(c) == FSToUpper(c) ? false : true);
    }

    /** Kas kõik sümbol stringis kuuluvad etteantud loendisse */
    inline static bool PoleMuudKui(const CFSWString* wStr, 
                                                    const CFSWString* loend)
    {
        for (int i = (int) wStr->GetLength() - 1; i >= 0; i--)
        {
            if (loend->Find((*wStr)[i]) == -1)
                return false;
        }
        return true;
    }

    /** Kas ükski sümbol stringis ei kuulu etteantud loendisse */
    inline static bool PoleYhtegi(const CFSWString* wStr, const FSWCHAR* loend)
    {
        return wStr->FindOneOf(loend) == -1 ? true : false;
    }

    /** Kopeerib osa from-ist to-sse, jättes need kopeerimata, mis not-is */
    inline static void StrNCpy(CFSWString* pTo, const CFSWString* pFrom,
                                                        const FSWCHAR* pNot)
    {
        *pTo = *pFrom;
        if (pTo->GetLength() > 0)
        {
            for (int i = 0; pNot[i]; i++)
            {
                pTo->Remove(pNot[i]);
            }
        }
    }

    /** Kas sisendstring võiks olla rooma nr */
    inline static bool OnRoomaNr(const CFSWString* wStr)
    {
        CRomanNr RomanNr;
        return RomanNr.IsRomanNr((const FSWCHAR *) (*wStr));
    }

    /// Esimene lisakr�nksudej�rgne t�ht sisendstringis suureks.

    inline static void AlgusSuureks(
                                    CFSWString* wStr ///< sisendstring
                                    )
    {
        int l = (int) wStr->GetLength(), pik;
        for (pik = 0; pik < l && lisaKr6nksudeStr.Find((*wStr)[pik]) != -1; pik++)
            ;
        if (pik < l)
        {
            //wStr->SetAt(pik, TaheHulgad::PisiSuureks(wStr, pik));
            wStr->SetAt(pik, FSToUpper((*wStr)[pik]));
        }
    }

    /// Kontrollib, kas sisendstring l�ppeb etteantud stringiga.

    inline static bool OnLopus(
                               const CFSWString* wStr, ///< Sisendstring.
                               const FSWCHAR* s ///< Kontrollime, kas see on l�pus.
                               )
    {
        assert(wStr != NULL || s != NULL);

        int pik;
        for (pik = 0; s[pik]; pik++) // leian s pikkuse
            ;
        if (pik == 0)
            return true;
        int len = (int) wStr->GetLength();
        if (len < pik)
            return false;
        return wStr->Find(s, len - pik) == -1 ? false : true;
    }

    /// Kontrollib, kas sisendstring algab etteantud stringiga.

    inline static bool OnAlguses(
                                 const CFSWString* wStr, ///< Sisendstring.
                                 const FSWCHAR* s ///< Kontrollime, kas see on alguses.
                                 )
    {
        assert(s != NULL);

        if (wStr->GetLength() == 0)
            return false;
        for (int pik = 0; s[pik]; pik++)
        {
            if (!(*wStr)[pik])
                return false;
            if ((*wStr)[pik] != s[pik])
                return false;
        }
        return true;
    }

    /// L�ikab sisendstringil "ees-" ja "tagasodi" maha.

    inline static void Puhasta(
                               CFSWString* wStr ///< Sisendstring.
                               )
    {
        assert(wStr->GetLength() > 0);

        wStr->TrimLeft(eessodi);

        CFSWString uus = *wStr;
        uus.TrimRight(FSxSTR("."));
        if (uus.TrimRight(tagasodi)) // tagasodi alati l�pust maha
            *wStr = uus; // . l�pust maha, kui ta on tagasodi j�rel
        else if (uus.GetLength() > 0 && wStr->GetLength() == (uus.GetLength() + 3)) // ... alati l�pust maha
            *wStr = uus;
    }

    /** 
     * 
     * @param[out] c 
     * <ul><li> Kui @a wStr[pos] alustab olemit, siis olemile vastav UNICODE'i 
     * sümbol. 
     *     <li> Kui wStr[pos] alustab märgendit siis 0. 
     *     <li> Kui polnud olem ega märgend, siis wStr[pos] muutmatul kujul.
     * </ul>
     * @param[out] pikkus 
     * <ul><li> Kui @a wStr[pos] alustab olemit, siis vastava olemi pikkus.
     *     <li> Kui @a wStr[pos] alustab märgendit, siis vastava märgendi pikkus.
     *     <li> Kui polnud olem ega märgend siis 1.
     * </ul>
     * @param[in] wStr Sisendstring
     * @param[in] pos Positsioon sisendstringis
     * @param[in] vajaPuhastada On @a true, kui on vaja teisendada olemeid ja leida märgendeid. Muidu @a false.
     * @return On @a false kui @a wStr[pos]==EndOfString, Muidu @a true,
     */
    inline static bool Xml2wchar(FSWCHAR& c, int& pikkus, CFSWString& wStr, 
                                        int pos, bool vajaPuhastada = true)
    {
        if (pos >= wStr.GetLength())
            return false;
        if(vajaPuhastada == false)
        {
            pikkus = 1;
            c = wStr[pos];
            return true;
        }
        int j;
        switch (wStr[pos])
        {
        case (FSWCHAR) '<': // Märgendi algus
            j = wStr.Find((FSWCHAR) '>', pos + 1); // otsime üles märgendi lõpu
            if (j <= pos) // märgendit lõpetav märk '>' puudu
                throw (VEAD(ERR_X_TYKK, ERR_MINGIJAMA, __FILE__, __LINE__, "Vigane XML margend"));
            pikkus = j - pos + 1;
            c = (FSWCHAR) '\0';
            break;
        case (FSWCHAR) '&': // tegeleme olemitega
            if (wStr.ContainsAt(pos, FSWSTR("&gt;")) == true)
            {
                pikkus = 4;
                c = (FSWCHAR) '>';
            }
            else if (wStr.ContainsAt(pos, FSWSTR("&lt;")) == true)
            {
                pikkus = 4;
                c = (FSWCHAR) '<';
            }
            else if (wStr.ContainsAt(pos, FSWSTR("&amp;")) == true)
            {
                pikkus = 5;
                c = (FSWCHAR) '&';
            }
            else if (wStr.ContainsAt(pos, FSWSTR("&apos;")) == true)
            {
                pikkus = 6;
                c = (FSWCHAR) '\'';
            }
            else if (wStr.ContainsAt(pos, FSWSTR("&quot;")) == true)
            {
                pikkus = 6;
                c = (FSWCHAR) '"';
            }
            else if (wStr.ContainsAt(pos, FSWSTR("&#")) == true)
            {
                int j = wStr.Find((FSWCHAR) ';', pos + 1); // otsime üles olemi lõpu
                if (j <= pos) // märgendit lõpetav märk ';' puudu
                    throw (VEAD(ERR_X_TYKK, ERR_MINGIJAMA, __FILE__, __LINE__, 
                                "Vigane &#kood; olem"));
                unsigned int kood = 0;
                for (int k = pos + 2; k < j; k++)
                    kood = 10 * kood + (unsigned int) (wStr[k]) - (unsigned int) '0';
                pikkus = j - pos + 1;
                c = (FSWCHAR) kood;
            }
            else
                // lubatud ainult 5 XMLis eeldefineeritud olemit
                // ja olemeid kujul &#kood;
                throw (VEAD(ERR_X_TYKK, ERR_MINGIJAMA, __FILE__, __LINE__, "Vigane olem"));
            break;
        default:
            pikkus = 1;
            c = wStr[pos];
            break;
        }
        return true;
    }

    /// Asendab Unicode'i kujul olevad susisevad sh ja zh vastu
    //
    /// Vajalik arvamisel-oletamisel anal��si
    /// teisendamiseks originaalkujule.

    inline static void Susisev2ShZh(
                                    CFSWString* wStr ///< Sisendstring.
                                    )
    {
        wStr->Replace(FSxSTR("\x0160"), FSxSTR("Sh"), 1);
        wStr->Replace(FSxSTR("\x017D"), FSxSTR("Zh"), 1);
        wStr->Replace(FSxSTR("\x0161"), FSxSTR("sh"), 1);
        wStr->Replace(FSxSTR("\x017E"), FSxSTR("zh"), 1);
    }

    /// Asendab sh ja zh kujul olevad susinad Unicode'i susisevatega.

    inline static void ShZh2Susisev(
                                    CFSWString* wStr ///< Sisendstring.
                                    )
    {
        wStr->Replace(FSxSTR("Sh"), FSxSTR("\x0160"), 1);
        wStr->Replace(FSxSTR("Zh"), FSxSTR("\x017D"), 1);
        wStr->Replace(FSxSTR("SH"), FSxSTR("\x0160"), 1);
        wStr->Replace(FSxSTR("ZH"), FSxSTR("\x017D"), 1);
        wStr->Replace(FSxSTR("sh"), FSxSTR("\x0161"), 1);
        wStr->Replace(FSxSTR("zh"), FSxSTR("\x017E"), 1);
    }

    /// Asendab sisendstringis �hed t�hed teistega.
    //
    /// @return Asendatud
    /// t�hem�rkide arv.

    inline static long AsendaMitu(
                                  CFSWString* wStr, ///< Sisendstring.
                                  const FSWCHAR* mis, ///< Sisendstringis mis[i] asemele millega[i]
                                  const FSWCHAR* millega ///< Sisendstringis mis[i] asemele millega[i]
                                  )
    {
        long mitu = 0L;
        CFSWString a = mis;
        CFSWString b = millega;
        for (int i = 0; mis[i]; i++)
        {
            if (!millega[i])
                return mitu;
            mitu = mitu + (int) wStr->Replace(a.Mid(i, 1), b.Mid(i, 1), 1);
        }
        return mitu;
    }

    /// Kontrollib, kas sona on suure algust�hega (aga muud on v�ikesed t�hed, - / nr jms)
    //
    /// @return
    /// - \a ==true Esimene suurt�ht ja �lej��nud ei ole suurt�hed.
    /// - \a ==false Midagi muud.

    inline bool static SuurAlgustaht(
                                     const FSXSTRING* s ///< Viit kontrollitavale stringi(klassi)le.
                                     )
    {
        if (!TaheHulgad::OnSuur(s, 0))
            return false;
        FSXSTRING s1;
        s1 = (const FSxCHAR *) s->Mid(1);
        return PoleSuuri(&s1);
    }

    /// Kontrollib, et s�na ei sisaldaks suurt�hti.
    //
    /// @return
    /// - \a ==true Ei sisalda �htegi suurt�hte.
    /// - \a ==false Sisaldab v�hemalt �hte suurt�hte.

    inline bool static PoleSuuri(
                                 const FSXSTRING* s ///< Viit kontrollitavale stringi(klassi)le.
                                 )
    {
        return (s->FindOneOf(suurtht) == -1 ? true : false);
    }

    /// Kontrollib, kas s�nas koosneks ainult suurt�htedest.
    //
    /// @return
    /// - \@a ==true Koosneb.
    /// - \@a ==false Sisaldab ka midagi muud.

    inline bool static AintSuured(
                                  const FSXSTRING *s ///< Viit kontrollitavale stringi(klassi)le.
                                  )
    {
        return PoleMuudKui(s, &suurtht);
    }

    /// Kontrollib, kas s�nas koosneb ainult suurt�htedest ja kriipsudest.
    //
    /// @return
    /// - \@a ==true Koosneb.
    /// - \@a ==false Sisaldab ka midagi muud.

    inline bool static AintSuuredjaKriipsud(
                                            const FSXSTRING* s ///< Viit kontrollitavale stringi(klassi)le.
                                            )
    {
        return PoleMuudKui(s, &suurthtkriips);
    }

    /// Kontrollib, kas s�nas koosneb ainult suurt�htedest ja numbritest.
    //
    /// @return
    /// - \@a ==true Koosneb.
    /// - \@a ==false Sisaldab ka midagi muud.

    inline bool static AintSuuredjaNr(
                                      const FSXSTRING* s ///< Viit kontrollitavale stringi(klassi)le.
                                      )
    {
        return PoleMuudKui(s, &suurnrtht);
    }

    /// Kontrollib, kas s�nas koosneb ainult suurt�htedest, numbritest ja kriipsudest.
    //
    /// @return
    /// - \@a ==true Koosneb.
    /// - \@a ==false Sisaldab ka midagi muud.

    inline bool static AintSuuredjaNrjaKriipsud(
                                                const FSXSTRING* s ///< Viit kontrollitavale stringi(klassi)le.
                                                )
    {
        return PoleMuudKui(s, &suurnrthtkriips);
    }

    /// Kontrollib, kas s�nas on ainult matemaatilised s�mbolid.
    //
    /// @return
    /// - \@a ==true Koosneb.
    /// - \@a ==false Sisaldab ka midagi muud.

    inline bool static MataSymbol(
                                  const FSXSTRING* s ///< Viit kontrollitavale stringi(klassi)le.
                                  )
    {
        return PoleMuudKui(s, &matemaatika);
    }

    /// Kontrollib, kas s�nas koosneb ainult numbritest.
    //
    /// @return
    /// - \@a ==true Koosneb.
    /// - \@a ==false Sisaldab ka midagi muud.

    inline bool static OnNumber(
                                const FSXSTRING* s ///< Viit kontrollitavale stringi(klassi)le.
                                )
    {
        return PoleMuudKui(s, &number);
    }

    /// Kontrollib, kas s�nas koosneb ainult kellaja numbritest.
    //
    /// @return
    /// - \@a ==true Koosneb.
    /// - \@a ==false Sisaldab ka midagi muud.

    inline bool static OnKellanumber(
                                     const FSXSTRING* s ///< Viit kontrollitavale stringi(klassi)le.
                                     )
    {
        return PoleMuudKui(s, &kellanumber);
    }

    /// Kontrollib, kas s�nas koosneb ainult protsendinumbritest.
    //
    /// @return
    /// - \@a ==true Koosneb.
    /// - \@a ==false Sisaldab ka midagi muud.

    inline bool static OnProtsendinumber(
                                         const FSXSTRING* s ///< Viit kontrollitavale stringi(klassi)le.
                                         )
    {
        return PoleMuudKui(s, &protsendinumber);
    }

    /// Kontrollib, kas s�nas koosneb ainult paragrahvinumbritest.
    //
    /// @return
    /// - \@a ==true Koosneb.
    /// - \@a ==false Sisaldab ka midagi muud.

    inline bool static OnParagrahvinumber(
                                          const FSXSTRING* s ///< Viit kontrollitavale stringi(klassi)le.
                                          )
    {
        return PoleMuudKui(s, &paranumber);
    }


    // NB! nende stringide doc failis tloendid.cpp
    const static FSXSTRING
    lisaKr6nksudeStr,
    liitSonaPiir,
    wWhiteSpace;

    // �hesugused fskooditabelis ja unicode-is
    // NB! nende stringide doc failis tloendid.cpp
    const static FSXSTRING kpt, gbd, helitu, hs, lmnr, aeiu, aeiul, kaash1,
    us_ees, matemaatika, matemaatika1, suludmatemaatika, arv,
    number, ndanumber, kellanumber, protsendinumber,
    lyh_kaash;

    // erinevad fskooditabelis ja unicode-is
    // NB! nende stringide doc failis tloendid.cpp
    const static FSXSTRING
    para,
    kraad,
    kraadjakriips,
    paranumber,
    kraadinumber,
    kraadinrtht,
    taish,
    kaash,
    vaiketht,
    amortht,
    eestitht,
    uni_kriipsud,
    amor_kriipsud,
    amor_apostroof,
    tapilised,
    heliline,
    suurtht,
    suurthtkriips,
    suurnrtht,
    suurnrthtkriips,
    suurnrtht1,
    eessodi,
    tagasodi,
    s_tagasodi,
    kaldjakriips,
    punktuatsioon,
    s_punktuatsioon,
    haalitsus1,
    haalitsus2,
    pn_eeltahed1,
    pn_eeltahed2,
    pn_eeltahed3,
    pn_eeltahed4,
    pn_eeltahed5,
    pn_eeltahed6,
    soome_taht,
    eesti_taht;


};

// Mingis .CPP failis initsialiseerid t�heloendid:
//  const CFSxSTRING TaheHulgad::konsonant(FSxSTR("kptgbdKPTGBD"));
//  const CFSxSTRING TaheHulgad::eessodi  (FSxSTR("([<{\""      ));
//  const CFSxSTRING TaheHulgad::tagasodi (FSxSTR(")]>}\"?!:;," ));
// Kasutamine .CPP failides:
//      n = TaheHulgad::KustutaSodi(s3);
//  if(TaheHulgad::OnKonsonant(c)==true){konsonant} else {mittekonsonant}


//=========================================================

/// Klass massiivist sorditud koopia tegemiseks ja sellest 2ndotsimiseks

template <class REC, class KEY> // <kirje-t��p, v�tme-t��p *>
class LOEND
{
public:
    /// Argumentideta konstruktor
    //
    /// Argumentideta konstruktor
    /// �nnestub alati.

    LOEND(void) throw ()
    {
        InitClassVariables();
    }; // alati: ClassInvariant()==false

    /// Argumentidega konstruktor
    //
    /// @throw VEAD,
    /// CFSFileException, CFSMemoryException, CFSRuntimeException

    /*LOEND(
          REC* _ptr_, ///< massiivi viit
          const int _len_, ///< massiivi pikkus
          const CMPFUNSRT _cmpsrt_, ///< v�rdleb(kirje, kirje)
          const CMPFUNBS _cmpbs_, ///< v�rdleb(v�ti,  kirje)
          const bool _makeCopy_ = true
          ///< @a ==true Reseveerib m�lu, teeb massiivist koopia
          ///< ja sordib seda. Vabastab reserveeritud m�lu.
          ///< M�lu, millele viitab _ptr_ ei vabastata. @n
          ///< @a ==false Sordib argumentmassiivi ennast.
          ///< @attention Vabastab m�lu, millele viitab _ptr_.
          )
    {
        assert(_makeCopy_ == false);
        InitClassVariables();
        Start(_ptr_, _len_, _cmpsrt_, _cmpbs_, _makeCopy_);

        assert(ClassInvariant());
    }; // ok, kui: ClassInvariant()==true*/

    /// Klassi initsailiseerimiseks peale argumentideta konstruktorit
    //
    /// @throw VEAD,
    /// CFSFileException, CFSMemoryException, CFSRuntimeException

    void Start(
               REC* _ptr_, ///< massiivi viit
               const int _len_, ///< massiivi pikkus
               const CMPFUNSRT _cmpsrt_, ///< v�rdleb(kirje, kirje)
               const CMPFUNBS _cmpbs_, ///< v�rdleb(v�ti,  kirje)
               const bool _makeCopy_ = true
               ///< @a ==true Sordib massiivi koopiat
               ///< @a ==false Sordib argumentmassiivi ennast
               )
    {
        Stop();
        if (_makeCopy_)
        {
            if ((ptr = (REC*) malloc(_len_ * sizeof (REC))) == NULL) // see malloc() on OK
            {
                throw (VEAD(ERR_X_TYKK, ERR_NOMEM, __FILE__, __LINE__));
            }
            memmove(ptr, _ptr_, _len_ * sizeof (REC));
        }
        else
        {
            ptr = _ptr_;
        }
        len = (_len_);
        cmpsrt = (_cmpsrt_);
        cmpbs = (_cmpbs_);
        if (_cmpsrt_ != NULL)
            sort();
        assert(ClassInvariant());
    }; // ok, kui: ClassInvariant()==true

    /// M�lu vabaks ja  pood kinni

    void Stop(void) throw ()
    {
        if (ptr)
        {
            free(ptr);
        }
        InitClassVariables();
    }; // alati: ClassInvariant()==false

    ~LOEND(void)
    {
        Stop();
    };

    //ClassInvariant()==false>>Start()>>ClassInvariant()==true>>Finish()>>ClassInvariant()==false

    /// Kahendotsimine: leiab kirje viida ettentud pikkusega v�tme j�rgi
    //
    /// @return
    /// - @a !=NULL Leidis
    /// - @a ==NULL Ei leidnud

    REC* Get(
             const FSxCHAR* key, ///< V�tme viit
             const int keyLen ///< V�tme pikkus
             )
    {
        assert(keyLen >= 0);
        assert(ClassInvariant());

        if (key == NULL || keyLen == 0)
            return NULL;
        tmpString = key;
        tmpString[keyLen] = 0;
        return Get((FSxCHAR *) ((const FSxCHAR *) tmpString));
    };

    /// Kahendotsimine: leiab kirje viida v�tme j�rgi
    //
    /// @return
    /// - @a !=NULL Leidis
    /// - @a ==NULL Ei leidnud

    REC* Get(
             const KEY key ///< V�tme viit (KEY peab olema viitmuutuja t��p)
             ) const
    {
        assert(ClassInvariant());

        if (key == NULL)
            return NULL;
        return (REC*) bsearch(key, ptr, len, sizeof (REC), cmpbs);
    };

    /// Lineaarne otsimine: Kirje viit ja indeks v�tme j�rgi
    //
    /// @return
    /// - @a !=NULL Leidis
    /// - @a ==NULL Ei leidnud

    REC* LGetRec(
                 const KEY key, ///< V�tme viit
                 int* idx = NULL ///< Kirje indeks, kui leidis
                 )
    {
        assert(ClassInvariant());

        if (key == NULL)
            return NULL;
        int i;
        for (i = 0; i < len; i++)
        {
            if (cmpbs(key, ptr + i) == 0)
            {
                if (idx)
                    *idx = i;
                return ptr + i;
            }
        }
        if (idx)
            *idx = -1;
        return NULL; // ei leidnud
    };

    /// Lineaarne otsimine: Kirje viit ja indeks v�tme j�rgi
    //
    /// @return
    /// - @a >= Kirje indeks
    /// - @a ==-1 Polnud

    int LGetIdx(
                const KEY key, ///< v�tme viit
                REC** rec = NULL
                ///< @a ==NULL Polnud
                ///< @a !=NULL v�tmele vastava kirje viit
                )
    {
        assert(rec != NULL);
        assert(ClassInvariant());

        if (key == NULL)
            return NULL;
        int i;
        for (i = 0; i < len; i++)
        {
            if (cmpbs(key, ptr + i) == 0)
            {
                if (rec)
                    *rec = ptr + i;
                return i;
            }
        }
        if (rec)
            *rec = NULL;
        return -1; // ei leidnud
    };

    /// Indeks kirje viidaks
    //
    /// @attention Ei kontrolli, et indeks
    /// j��b lubatud piiridesse.

    REC operator[] (
        const int idx ///< indeks
        ) const
    {
        assert(ClassInvariant());

        return ptr[idx];
    };

    /// Kahendotsimine: Kirje indeks v�tme j�rgi
    //
    /// @return
    /// - @a >= 0 Kirje indeks
    /// - @a ==-1 Polnud

    int operator[] (
        const KEY key ///< V�tme viit
        ) const
    {
        return Find(key);
    };

    int len; ///< massiivi pikkus

    /// Kahendotsimine: v�ti indeksiks
    //
    /// @return
    /// - @a >=0 Leitud indeks
    /// - @a ==-1 Polnud

    int Find(const KEY key) const
    {
        assert(key != NULL);
        assert(ClassInvariant());

        REC* t = (REC*) bsearch(key, ptr, len, sizeof (REC), cmpbs);
        return (t == NULL) ? -1 : (int) (t - ptr);
    };

    bool EmptyClassInvariant(void) const throw ()
    {
        return len == 0 && cmpsrt == NULL && cmpbs == NULL && ptr == NULL;
    };

    bool ClassInvariant(void) const throw ()
    {
        return len > 0 && cmpbs != NULL && ptr != NULL;
    };


    //protected:

    CMPFUNSRT cmpsrt; ///< Viit funktsioonile (v�rdleb kirjeid)
    CMPFUNBS cmpbs; ///< Viit funktsioonile (v�rdleb v�tit kirje v�tmega)
    REC *ptr; ///< Viit massiivile
    FSXSTRING tmpString; ///< Abistring

    //private:

    /// Funktsioon kirjete j�rjestamiseks

    inline
    void sort(void)
    {
        assert(ClassInvariant());

        qsort(ptr, len, sizeof (REC), cmpsrt);
    };

    /// Argumentideta konstruktoris klassi muutujate esialgseks initsaliseerimiseks

    void InitClassVariables(void)
    {
        len = 0;
        cmpsrt = NULL;
        cmpbs = NULL;
        ptr = NULL;
    };
};

typedef TXSTRARR<FSXSTRING, FSXSTRING> XSTRARR;

#endif


