#include <stdlib.h>

#include "loefailist.h"
#include "ctulem.h"
#include "ahel2.h"
#include "tloendid.h"

void SISSEVALJA::Start(const CFSFileName& fileName, const FSTCHAR* pmode,
                       const PFSCODEPAGE _codePage_, const FSTCHAR* path,
                       const bool _ignoramp_, const bool _autosgml_)
{
    assert(EmptyClassInvariant());
    if (Open(fileName, pmode) == false)
        throw VEAD(ERR_IO, ERR_OPN, __FILE__, __LINE__, NULL,
                   "Ei suuda avada faili:", (const FSTCHAR*) fileName);
    svKoodiTabel = _codePage_;
    if (svKoodiTabel == PFSCP_HTMLEXT)
        cnv.Start(path, _ignoramp_, _autosgml_);
    assert(ClassInvariant());
}

void SISSEVALJA::Start(FILE* pfile, const PFSCODEPAGE _codePage_,
           const FSTCHAR* path, const bool _ignoramp_, const bool _autosgml_)
{
    assert(EmptyClassInvariant());
    assert(pfile == stdin || pfile == stdout || pfile == stderr);
#if defined(WIN32) || defined(WIN64)
    if (_setmode(_fileno(pfile), _O_BINARY) == -1)
        throw (VEAD(ERR_IO,
                    ERR_OPN,
                    __FILE__, __LINE__, "$Revision: 1097 $"));
#endif
    if (Open(pfile) == false)
        throw (VEAD(ERR_IO,
                    ERR_OPN,
                    __FILE__, __LINE__, "$Revision: 1097 $"));
    svKoodiTabel = _codePage_;
    if (svKoodiTabel == PFSCP_HTMLEXT)
        cnv.Start(path, _ignoramp_, _autosgml_);
    assert(ClassInvariant());
}

void SISSEVALJA::Stop(void)
{
    cnv.Stop();
    Close();
    InitEmptyClassVariables();
}

//---------------------------------------------------------

void VOTAFAILIST::Start(const CFSFileName& fileName, const FSTCHAR* pmode,
                        const PFSCODEPAGE _codePage_, const FSTCHAR* path,
                        const bool _ignoramp_, const bool _autosgml_, const bool _bom_)
{
    assert(EmptyClassInvariant());
    SISSEVALJA::Start(fileName, pmode, _codePage_, path, _ignoramp_, _autosgml_);
    BomIn(_bom_);
    assert(ClassInvariant());
}

void VOTAFAILIST::Start(const PFSCODEPAGE _codePage_, const FSTCHAR* path,
                        const bool _ignoramp_, const bool _autosgml_, const bool _bom_)
{
    assert(EmptyClassInvariant());
    SISSEVALJA::Start(stdin, _codePage_, path, _ignoramp_, _autosgml_);
    BomIn(_bom_);
    assert(ClassInvariant());
}

// Kui faili alustab "\xFF\xFE", siis PFSCP_UC
// Kui faili alustab "\xEF\xBB\xBF" siis PFSCP_UTF8
// Muidu PFSCP_BALTIC
//

bool VOTAFAILIST::Start(const CFSFileName& fileName, const FSTCHAR* pmode)
{
    SISSEVALJA::Start(fileName, pmode, BomDetection(fileName));
    return true;
}

bool VOTAFAILIST::Rida(CFSWString& rida)
{
    assert(ClassInvariant());
    if (svKoodiTabel == PFSCP_UC) // loeme sisse UNICODE'i
    {
        if (ReadLine(&rida) == false)
        {
            assert(ClassInvariant());
            return false; // viga v�i EOF
        }
    }
    else
    {
        CFSAString astr;
        if (ReadLine(&astr) == false)
        {
            assert(ClassInvariant());
            return false; // viga või EOF
        }
        cnv.ConvToUc(rida, astr, svKoodiTabel);
    }
    assert(ClassInvariant());
    return true;
}

bool VOTAFAILIST::RidaTrimmitud(CFSWString& rida)
{
    while (Rida(rida) == true)
    {
        rida.Trim();
        if (rida.GetLength() > 0)
            return true;
    }
    return false;
}

//---------------------------------------------------------

void PANEFAILI::Start(const CFSFileName& fileName, const FSTCHAR* pmode,
                      const PFSCODEPAGE _codePage_, const FSTCHAR* path,
                      const bool _ignoramp_, const bool _autosgml_, const bool _bom_)
{
    assert(EmptyClassInvariant());
    SISSEVALJA::Start(fileName, pmode, _codePage_, path, _ignoramp_, _autosgml_);
    BomOut(_bom_);
    assert(ClassInvariant());
}

void PANEFAILI::Start(
                      const PFSCODEPAGE _codePage_,
                      const FSTCHAR* path,
                      const bool _ignoramp_,
                      const bool _autosgml_,
                      const bool _bom_
                      )
{
    assert(EmptyClassInvariant());
    SISSEVALJA::Start(stdout, _codePage_, path, _ignoramp_, _autosgml_);
    BomOut(_bom_);
    assert(ClassInvariant());
}

void PANEFAILI::Pane(const CFSWString &wStr)
{
    assert(ClassInvariant());
    if (svKoodiTabel == PFSCP_UC) // kirjutame UNICODE'i
        WriteStringB(&wStr);
    else
    {
        CFSAString astr;
        cnv.ConvFromUc(astr, svKoodiTabel, wStr);
        WriteStringB(&astr);
    }
    assert(ClassInvariant());
}

void PANEFAILI::Pane(const CFSAString &aStr)
{
    assert(ClassInvariant());
    if (svKoodiTabel == PFSCP_UC) // kirjutame UNICODE'i
    {
        CFSWString wStr=FSStrAtoW(aStr, FSCP_UTF8);
        WriteStringB(&wStr);
    }
    else
         WriteStringB(&aStr);
}

template <typename S_TYYP, typename C_TYYP>
void PANEFAILI::PaneX(const LYLI_TMPL<S_TYYP, C_TYYP>& lyli,
                                                    const MRF_FLAGS& mrfFlags)
{
    S_TYYP str;
    if((lyli.lipp & PRMS_SARV) == PRMS_SARV)
        str.Format(EritiSobiViit(C_TYYP, "<%d/>\n"), lyli.ptr.arv);
    else if ((lyli.lipp & PRMS_STRKLASS) == PRMS_STRKLASS)
        str = *lyli.ptr.pStr + EritiSobiViit(C_TYYP, "\n");
    else if ((lyli.lipp & PRMS_STRID) == PRMS_STRID)
        //str.Format(EritiSobiViit(C_TYYP, "%s <%d/>\n"),
        //           (const C_TYYP *)lyli.ptr.strid->str, lyli.ptr.strid->id);
        str.Format(EritiSobiViit(C_TYYP, "%s\n"),
                                    (const C_TYYP *)lyli.ptr.strid->str);
    else if ((lyli.lipp & PRMS_MRF) == PRMS_MRF)
        lyli.ptr.pMrfAnal->Strct2Strng(&str, &mrfFlags);
    else
        throw VEAD(ERR_X_TYKK, ERR_MINGIJAMA, __FILE__, __LINE__,
                            "Ei oska sellist LYLI tekstina faili kirjutada");
    Pane(str);
}

/** Lüli väljundfaili
 * 
 * @param plyli
 * @param mrfFlags
 */
void PANEFAILI::Pane(const LYLI* plyli, const MRF_FLAGS& mrfFlags)
{
    PaneX<FSXSTRING, FSWCHAR>(*plyli, mrfFlags);
}

void PANEFAILI::Pane(const LYLI_UTF8* plyli, const MRF_FLAGS& mrfFlags)
{
    LYLI_UTF8 tmpLyli(*plyli);
    PaneX<FSXSTRING, FSWCHAR>(tmpLyli, mrfFlags);
    
}
//---------------------------------------------------------

// key peab olema white space'iga ümbritsetud (reaalgus/reavahetus sobib ka)
// kommentaari alustab rea-algus/tühik/tabulatsioon# ja lõpetab reavahe
// kommentaari ignoreeritakse

bool VOTAANDMEFAILIST::Seek2(const CFSWString &key)
{
    Seek((long) sizeOfBOM); //kerime faili algusesse BOMi taha
    CFSWString wstr;
    while (Get(wstr) == true) //loeme white space'i vahelt sõna...
    {
        if (wstr == key) //...ja vaatame kas võrdub võtmega
            return true; //jess
    }
    return false; //ei leidnud
}

bool VOTAANDMEFAILIST::Get(CFSWString &value)
{
    FSWCHAR wchar;
    bool ret = ReadChar(&wchar);

    while (ret == true)
    {
        //vaatame, kas on white space
        if (TaheHulgad::OnWhiteSpace(wchar) == true)
        {
            do
            { //h�ppame �le white space'i
                ret = ReadChar(&wchar);
            }
            while (ret == true && TaheHulgad().OnWhiteSpace(wchar) == true);
            continue;
        }
        //vaatame kas on kommentaar
        if (wchar == (FSWCHAR) '#')
        {
            do
            { //h�ppame �le kommentaari
                ret = ReadChar(&wchar);
            }
            while (ret == true && wchar != (FSWCHAR) '\n');
            continue;
        }
        //korjame stringi kuni white space'ni üles
        value = FSWSTR(""); //nullime väljundstringi
        do
        {
            value += wchar;
            ret = ReadChar(&wchar);
        }
        while (ret == true && TaheHulgad().OnWhiteSpace(wchar) == false);
        return true; //tükike käes
    }
    return false; //fail otsas, ei saanud miskit
}

