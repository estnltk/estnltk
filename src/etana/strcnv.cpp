#include "post-fsc.h"

//---------------------------------------------------------

void CONV_HTML_UC2::Start(
    const FSTCHAR* path,
    const bool _ignoramp_,
    const bool _autosgml_
    )
    {
    ignoramp=_ignoramp_;
    autosgml=_autosgml_;
    if(path!=NULL) // võtame loendi failist
        {
        CFSString tabeliFailiNimi(FSTSTR("sgml-uc-cnv.txt"));
        CFSString tabeliFailiPikkNimi;
        CFSString p(path);
        // Otsime üles, millises kataloogis teisendustabel
        if(Which(&tabeliFailiPikkNimi, &p, &tabeliFailiNimi)==false)
            throw VEAD(ERR_X_TYKK, ERR_OPN, __FILE__,__LINE__, "$Revision: 557 $",
                                    "Ei leia SGML olemite faili sgml-uc-cnv.txt");
        // Avame teisenustabelit sisaldaa faili
        CPFSFile tabeliFail;
        if(tabeliFail.Open(tabeliFailiPikkNimi, FSTSTR("rb"))==false)
                throw VEAD(ERR_X_TYKK, ERR_OPN, __FILE__,__LINE__, "$Revision: 557 $"
                             "Ei suuda avada SGML olemite faili"
#if !defined( _UNICODE )
                            ,(const char*)tabeliFailiPikkNimi
#endif
                             );
        // Loeme failist teisendustabeli mällu
        SGML_UC* rec;
        sgml2uc.Start(100,10);
        uc2sgml.Start(100,10);
        sgml_stringi_max_pikkus=0;
        int n;
        while((rec=sgml2uc.AddPlaceHolder())->Start(tabeliFail)==true)
            {
            uc2sgml.AddPtr(rec); // sellesse massiivi panema ainult viida 
            if((n=(int)strlen(rec->sgml))>sgml_stringi_max_pikkus)
                sgml_stringi_max_pikkus=n;
            }
        sgml2uc.Del(); // kustutame  viimase, sest sinna ei õnnestunud lugeda
        sgml2uc.Sort(SGML_UC::sortBySGMLStr);   // selle massiivi järjestame SGML olemite järgi
        uc2sgml.Sort(SGML_UC::sortByUCchar);    // selle massiivi järjestame UNICODEi sümbolite järgi
        }
    }

void CONV_HTML_UC2::ConvToUc(
    CFSWString& wStr,
    const CFSAString& aStr,
    const PFSCODEPAGE koodiTabel
    )
    {
    wStr.Empty();
    if(koodiTabel!=PFSCP_HTMLEXT) // Krutime Renee algoritmi järgi
        {
        wStr = FSStrAtoW(aStr, koodiTabel); // Kui teisendus käib Rene tabelite järgi, siis teeme ära ja valmis
        return;
        }
    assert(koodiTabel==PFSCP_HTMLEXT); // Kasutame teisendamiseks failist loetud tabelit
    if(sgml2uc.idxLast<=0)
            throw VEAD(ERR_X_TYKK, ERR_ARGVAL, __FILE__,__LINE__, "$Revision: 557 $",
                "SGML olemite tabel mällu lugemata, progeja peaks manuali lugema");
    int l, n=aStr.GetLength();
    for(l=0; l < n; l++)
        {
        if((aStr[l] & (~0x7F))!=0) // peab olema 7bitine ascii
            throw VEAD(ERR_X_TYKK, ERR_ARGVAL, __FILE__,__LINE__, "$Revision: 557 $",
                            "String peab koosnema ASCII (7bitistest) koodidest", (const char*)aStr+l);
        if(aStr[l]!='&') // ei alusta SGML olemit...
            {
tryki:      wStr += ((FSWCHAR)(aStr[l])) & 0x7F; // ...läheb niisama
            continue;
            }
        // Võib alustada mingit SGML olemit - &blah;
        int lSemiPos=(int)aStr.Find(";", l+1);
        if(lSemiPos<0) // see ampersand ilma lõpetava semita
            {
            if(ignoramp==true)
                goto tryki;
            throw VEAD(ERR_X_TYKK, ERR_ARGVAL, __FILE__,__LINE__, "$Revision: 557 $",
                                "Ampersandi tagant semi puudu", (const char*)aStr+l);
            }
        if(autosgml==true && aStr[l+1]=='#') // teisenda &#[{x|X}]12345; sümbolid
            {
            int tmp=0, j=l+2;
            if(aStr[j]=='x' || aStr[j]=='X')    // teisenda &#x12345; ja &#X12345; hexakoodid
                {
                j++;
                //if(sscanf(((const char*)aStr)+j, "%x", &tmp)!=1)
                //        throw VEAD(ERR_X_TYKK, ERR_ARGVAL, __FILE__,__LINE__, "$Revision: 557 $",
                //                    "Vigane SGML olem", (const char*)aStr+l);
                //for(; j<lSemiPos; j++)
                //    {
                //    if(strchr("0123456789aAbBcCdDeEfF", aStr[j])==NULL)
                //       throw VEAD(ERR_X_TYKK, ERR_ARGVAL, __FILE__,__LINE__, "$Revision: 557 $",
                //                    "Vigane SGML olem", (const char*)aStr+l);
                //    }
                j+=STRSOUP::UnsignedStr2Hex<int, char>(&tmp, ((const char*)aStr)+j);
                if(j<=0 || aStr[j]!=';')
                    throw VEAD(ERR_X_TYKK, ERR_ARGVAL, __FILE__,__LINE__, "$Revision: 557 $",
                                "Vigane SGML olem", (const char*)aStr+l);
                if(tmp>0xFFFF)
                    throw VEAD(ERR_X_TYKK, ERR_ARGVAL, __FILE__,__LINE__, "$Revision: 557 $",
                                "Vigane SGML olem (peab mahtuma 2 baidi peale)", (const char*)aStr+l);
                }
            else                                // teisenda &#12345; ja &#12345; kümnendkoodid
                {
                //for(; j<lSemiPos; j++)
                //    {
                //    if(aStr[j]<'0' || aStr[j]>'9')
                //        throw VEAD(ERR_X_TYKK, ERR_ARGVAL, __FILE__,__LINE__, "$Revision: 557 $",
                //                    "Vigane SGML olem (lubatud 0-9)", (const char*)aStr+l);
                //    if((tmp=10*tmp+aStr[j]-'0')>0xFFFF)
                //        throw VEAD(ERR_X_TYKK, ERR_ARGVAL, __FILE__,__LINE__, "$Revision: 557 $",
                //                    "Vigane SGML olem (peab mahtuma 2 baidi peale)", (const char*)aStr+l);
                //    }
                j+=STRSOUP::UnsignedStr2Num<int, char>(&tmp, ((const char*)aStr)+j);
                if(j<=0 || aStr[j]!=';')
                    throw VEAD(ERR_X_TYKK, ERR_ARGVAL, __FILE__,__LINE__, "$Revision: 557 $",
                                "Vigane SGML olem", (const char*)aStr+l);
                if(tmp>0xFFFF)
                    throw VEAD(ERR_X_TYKK, ERR_ARGVAL, __FILE__,__LINE__, "$Revision: 557 $",
                                "Vigane SGML olem (peab mahtuma 2 baidi peale)", (const char*)aStr+l);
                }
            wStr += (WCHAR)tmp;
            l=lSemiPos;
            continue;
            }
        if(lSemiPos-l+1 > sgml_stringi_max_pikkus) // nii pikk ei saa olla tabelis
            {
            if(ignoramp==true)
                goto tryki;
            throw VEAD(ERR_X_TYKK, ERR_ARGVAL, __FILE__,__LINE__, "$Revision: 557 $",
                                "Puudub SGML olemite tabelist", (const char*)aStr+l);
            }
		CFSAString szSymbol=aStr.Mid(l, lSemiPos-l+1); // lõikame &bla; sisendstringist välja
        SGML_UC* rec;
        if((rec=sgml2uc.Get(&szSymbol))==NULL) // ei leidnud kahendtabelist - jama lahti
            {
            if(ignoramp==true)
                goto tryki;
            throw VEAD(ERR_X_TYKK, ERR_ARGVAL, __FILE__,__LINE__, "$Revision: 557 $",
                        "Puudub SGML olemite tabelist", (const char*)szSymbol);
            }
		wStr += rec->uc;
        l=lSemiPos;
        }
    }

void CONV_HTML_UC2::ConvFromUc(
    CFSAString& aStr,
    const PFSCODEPAGE koodiTabel,
    const CFSWString& wStr
    )
    {
    aStr.Empty();
    if(koodiTabel!=PFSCP_HTMLEXT) // Krutime Renee algoritmi järgi
        {
        aStr = FSStrWtoA(wStr, koodiTabel); // Kui teisendus käib Rene tabelite järgi, siis teeme ära ja valmis
        return;
        }
    assert(koodiTabel==PFSCP_HTMLEXT); // Kasutame teisendamiseks failist loetud tabelit
    if(sgml2uc.idxLast<=0)
            throw VEAD(ERR_X_TYKK, ERR_ARGVAL, __FILE__,__LINE__, "$Revision: 557 $",
                "SGML olemite tabel mällu lugemata, progeja peaks manuali lugema");
    FSWCHAR wc;
    for(int i=0; (wc=wStr[i])!=0; i++)
        {
        if((wc & (~0x7F))==0) // Oli ASCII (7bitine) kood
            {
            if(ignoramp==false && wc==(FSWCHAR)'&') // Ampersand SGML olemiks
                aStr += "&amp;";
            else
                aStr += (char)(wc & 0x7F); // Muud ASCII koodid niisama üle
            continue;
            }
        // Polnud ASCII kood, peab olema  SGML olemite loendis
        SGML_UC* rec;
        if((rec=uc2sgml.Get((const FSWCHAR*)wStr+i))!=NULL) // leidsime loendist
            {
            aStr += rec->sgml;
            continue;
            }
        int olemiAlgusPos=aStr.GetLength();
        aStr+="&#";
        STRSOUP::UnsignedNum2Str<int, CFSAString, char, 10>((unsigned int)(wStr[i]), aStr);
        aStr+=';';
        if(autosgml==false)
            {
            throw VEAD(ERR_X_TYKK, ERR_ARGVAL, __FILE__,__LINE__, "$Revision: 557 $",
                        "UniCode'i kood programmi SGML olemite tabelist puudu, 10ndkood", 
                        (const char*)aStr+olemiAlgusPos);
            }
        /*
        if(autosgml==false)
            {
            char tmpBuf[128];
            sprintf(tmpBuf, "%d", (unsigned int)(wStr[i]));
            throw VEAD(ERR_X_TYKK, ERR_ARGVAL, __FILE__,__LINE__, "$Revision: 557 $",
                        "UniCode sümbol programmi SGML olemite tabelist puudu, kood", tmpBuf);
            }
        //autosgml==true;
        CFSAString revSgml;
        int j=-1;
        assert(wc > 0);
        do
            {
            revSgml[++j] = (unsigned)(wc%10)+(unsigned)'0';
            wc /= 10;
            } while(wc > 0);
        aStr += "&#";
        while(j>=0)
            aStr+=revSgml[j--];
        aStr += ';';
        */
        }
    }

void CONV_HTML_UC2::ConvFromTo(
    CFSAString& vStr,
    const PFSCODEPAGE vKoodiTabel,
    const CFSAString& sStr, 
    const PFSCODEPAGE sKoodiTabel
    )
    {
    if(sgml2uc.idxLast<=0 && (vKoodiTabel==PFSCP_HTMLEXT || sKoodiTabel==PFSCP_HTMLEXT))
        throw VEAD(ERR_X_TYKK, ERR_ARGVAL, __FILE__,__LINE__, "$Revision: 557 $",
                    "SGML olemite tabel mällu lugemata, progeja peaks manuali lugema");
    CFSWString wStr;
    ConvToUc(wStr,sStr, sKoodiTabel);
    ConvFromUc(vStr,vKoodiTabel,wStr);
    }

void CONV_HTML_UC2::Stop(void)
    {
    if(uc2sgml.idxLast>0)
        {
        if(uc2sgml.idxLast>0)
            {
            uc2sgml.DelAll(true);   // kustutame massiivist ainult viidad
            uc2sgml.Stop();
            }
        if(sgml2uc.idxLast>0)
            {
            sgml2uc.DelAll(false);  // siin kustutame kirjed ka
            sgml2uc.Stop();
            }
        }
    InitClassVariables();
    }

void ConvFile(
    CPFSFile &out,                  ///< Väljundfail
    const PFSCODEPAGE outKoodiTabel,///< Väljundfaili kooditabel
    CPFSFile &in,                   ///< Sisendfail
    const PFSCODEPAGE inKoodiTabel, ///< Sisendfaili kooditabel
    CONV_HTML_UC2 &cnv,             ///< Stringiteisendaja
    const bool feff,                ///< UNICODE'i korral määrab BOMi käsitlemise viidi
    PROGRESSIMOOTJA progr ///< Määrab edenemise kuvamise viisi
    )
    {
    CFSAString aStr;
    CFSWString wStr;
    PROGRESS p(progr, in);

    if(outKoodiTabel==inKoodiTabel)
        throw VEAD(ERR_X_TYKK, ERR_ARGVAL, __FILE__,__LINE__, "$Revision: 557 $",
                   "Sisendfaili kooditabel == Väljundfaili kooditabel -- Midagi targemat pole teha?");
    if(outKoodiTabel==PFSCP_UC) // mitteUNICODE --> UNICODE
        {
        if(feff)                            // BOM tuleb failipäisesse lisada
            out.WriteStringB(FSWSTR("\xFEFF")); 
        while(in.ReadLine(&aStr)==true)
            {
            cnv.ConvToUc(wStr, aStr, inKoodiTabel);
            out.WriteStringB(&wStr);
            p.Progress();
            }
        return;        
        }
   if(inKoodiTabel==PFSCP_UC)  // UNICODE --> mitteUNICODE
        {
        if(feff)                                // BOMi olemasolul kontrolli baidijärge
            {
            FSWCHAR wc;
            if(in.ReadChar(&wc)==true)
                {
                if(wc==0xFFFE)
                    throw VEAD(ERR_X_TYKK, ERR_ARGVAL, __FILE__,__LINE__, "$Revision: 557 $",
                                                        "Sisendfailis vale baidijärjega UNICODE");
                if(wc!=0xFEFF)
                    in.Seek(0L); // polnud BOM, kerime faili algusesse tagasi
                // ok, sobilik baidijärjekord
                }
            }
        while(in.ReadLine(&wStr)==true)
            {
            cnv.ConvFromUc(aStr, outKoodiTabel, wStr);
            out.WriteStringB(&aStr);
            p.Progress();
            }
        return;
        }
    
    CFSAString bStr;
    while(in.ReadLine(&aStr)==true) // mitteUNICODE --> mitteUNICODE
        {
        cnv.ConvFromTo(bStr,outKoodiTabel,aStr,inKoodiTabel);
        out.WriteStringB(&bStr);
        p.Progress();
        }
    }
