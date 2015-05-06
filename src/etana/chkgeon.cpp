
/*
* kontrollib, kas S6na on mitmes�naline geo nimi
*/
#include "mrflags.h"
#include "post-fsc.h"
#include "mrf-mrf.h"
//#include "valjatr.h"
#include "tloendid.h"

int MORF0::chkgeon(MRFTULEMUSED *tul, FSXSTRING *sona, int *mitu)
    {
    int res;
    FSXSTRING gsona;
    FSXSTRING gsona3;
    FSXSTRING lylist1Puhastatud, lylist2Puhastatud;
    CVARIANTIDE_AHEL ctoo_variandid, csobivad_variandid;
    gsona = *sona;
    TaheHulgad::Puhasta(&gsona);

    if (mrfFlags.ChkB(MF_V0TAKOKKU)==false) // ära võta sõnu üheks üksuseks kokku
         return ALL_RIGHT;   // ... siis siin pole midagi teha; 04.2015
        
 	if ( ( (dctLoend[5])[(FSxCHAR *)(const FSxCHAR *)gsona] ) == -1 )
         return ALL_RIGHT; // pole mitmesonal. geogr. nime 1. osa
    gsona += FSxSTR("=");
    
    //gsona += (FSxCHAR *)(konveier->LyliInf0(1));
    lylist1Puhastatud=konveier->LyliInf0(1);
    PuhastaXMList<FSXSTRING, FSWCHAR>(lylist1Puhastatud, mrfFlags.ChkB(MF_XML));
    gsona += lylist1Puhastatud;

    if (gsona.GetLength() >= STEMLEN)
        return ALL_RIGHT; // pole mitmesonal. geogr. nimi
    
    *mitu = 2;
    //if ( ( (dctLoend[6])[(FSxCHAR *)(konveier->LyliInf0(1))] ) != -1 )
    if ( ( (dctLoend[6])[(FSxCHAR *)(const FSxCHAR *)lylist1Puhastatud] ) != -1 )
        { 	    // voib olla mitmesonal. geogr. nime 2. osa
        gsona3 = gsona;
        gsona3 += FSxSTR("=");

        //gsona3 += (FSxCHAR *)(konveier->LyliInf0(2));
        lylist2Puhastatud=konveier->LyliInf0(2);
        PuhastaXMList<FSXSTRING, FSWCHAR>(lylist2Puhastatud, mrfFlags.ChkB(MF_XML));
        gsona3+=lylist2Puhastatud;

        if (gsona3.GetLength() < STEMLEN)
            {
            gsona = gsona3;
            *mitu = 3;
            }
        }
    TaheHulgad::Puhasta(&gsona);
    gsona.TrimRight(FSxSTR("."));
    // kontr, kas s�na on mitmeosaline geograafiline nimi + lp
    TaheHulgad::AsendaMitu(&gsona, TaheHulgad::uni_kriipsud, TaheHulgad::amor_kriipsud);
    res = kchk1(&ctoo_variandid.ptr, &gsona, gsona.GetLength(), &csobivad_variandid.ptr, NULL, 0);
    if (res > ALL_RIGHT)
        {
	    return res; // viga!
        }
    if (csobivad_variandid.ptr)
        {
        asenda_tyves(&csobivad_variandid.ptr, FSxSTR("="), FSxSTR(" "));
        variandid_tulemuseks(tul, LIIK_PARISNIMI, &csobivad_variandid.ptr);
        }
    //ahelad_vabaks(&ctoo_variandid.ptr);       //destruktoris
    //ahelad_vabaks(&csobivad_variandid.ptr);   //destruktoris
    return ALL_RIGHT;
    }


