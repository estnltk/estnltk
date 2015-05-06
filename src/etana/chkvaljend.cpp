
/*
* kontrollib, kas S6na on mitmesõnaline väljend (nt. ette tulema)
*/
#include "mrflags.h"
#include "post-fsc.h"
#include "mrf-mrf.h"
//#include "valjatr.h"
#include "tloendid.h"

int MORF0::chkvaljend(MRFTULEMUSED *tul, FSXSTRING *sona)
    {
    int res;
    FSXSTRING valjend;
    FSXSTRING jupp1, jupp2;
    CVARIANTIDE_AHEL ctoo_variandid, csobivad_variandid;
    FSXSTRING ki;
    FSXSTRING S6na3;
    FSxCHAR enne_ki;

    if (mrfFlags.ChkB(MF_V0TAKOKKU)==false) // ära võta sõnu üheks üksuseks kokku
         return ALL_RIGHT;   // ... siis siin pole midagi teha; 04.2015
    jupp2 = (FSxCHAR *)(konveier->LyliInf0(1));
    if (jupp2.GetLength() == 0) // v�ljendit polegi
        return ALL_RIGHT;
    jupp1 = *sona;
    valjend = jupp1;
    valjend += FSxSTR("=");
    valjend += jupp2;
    TaheHulgad::Puhasta(&valjend);
    if (valjend.GetLength() >= STEMLEN)
        return ALL_RIGHT; /* pole mitmesonal. geogr. nimi */
    valjend.TrimRight(FSxSTR("."));
    if ( TaheHulgad::SuurAlgustaht(&jupp1)
        || TaheHulgad::AintSuuredjaKriipsud(&jupp1) 
        || TaheHulgad::SuurAlgustaht(&jupp2)
        || TaheHulgad::AintSuuredjaKriipsud(&jupp2) )
        valjend.MakeLower();
    /* kontr, kas see on s�nastikus olev v�ljend */
    res = kchk1(&ctoo_variandid.ptr, &valjend, valjend.GetLength(), &csobivad_variandid.ptr, NULL,0);
    if (res > ALL_RIGHT)
	    return res; /* viga! */
    ki = FSxSTR("");
    if (!csobivad_variandid.ptr) // v�tan l�pust ki/gi maha
        {
        ahelad_vabaks(&ctoo_variandid.ptr);
        ki = (const FSxCHAR *)(valjend.Right(2));
        enne_ki = valjend[valjend.GetLength()-3];
        if ( (     // on nii, et...
            (ki == FSxSTR("ki") && TaheHulgad::OnHelitu(enne_ki))  ||    // enne 'ki' helitu h��lik
            (ki == FSxSTR("gi") && !TaheHulgad::OnHelitu(enne_ki)) ||    // enne 'gi' heliline h��lik
            ((ki == FSxSTR("ki") || ki == FSxSTR("gi")) && (enne_ki == V_SH || enne_ki == V_ZH)) // s'ja z' puhul on lubatud nii gi kui ki
            ) )
            {
            S6na3 = (const FSxCHAR *)(valjend.Mid(0, valjend.GetLength()-2));
	        if ( (dctLoend[0])[(FSxCHAR *)(const FSxCHAR *)S6na3] == -1 )
                { // sonale ikka tohib [gk]i otsa panna
                res = kchk1(&ctoo_variandid.ptr, &S6na3, S6na3.GetLength(), &csobivad_variandid.ptr, NULL,0); /* ty+lp */
		        if (res > ALL_RIGHT)
		            return false; /* viga! */
                }
            }
        }
    if (csobivad_variandid.ptr)
        {
        asenda_tyves(&csobivad_variandid.ptr, FSxSTR("="), FSxSTR(" "));
        variandid_tulemuseks(tul, KOIK_LIIGID, &csobivad_variandid.ptr);
        tul->keeraYmber = false;
        tul->mitmeS6naline = 2;
        tul->LisaLoppudeleTaha((const FSxCHAR *)ki);
        }
    if (!tul->on_tulem())
        {  // kontrolli, kas juppide �ravahetamisel saame v�ljendi (verbi)
        valjend = jupp2;
        valjend += FSxSTR("=");
        valjend += jupp1;
        if ( TaheHulgad::SuurAlgustaht(&jupp1)
            || TaheHulgad::AintSuuredjaKriipsud(&jupp1) 
            || TaheHulgad::SuurAlgustaht(&jupp2)
            || TaheHulgad::AintSuuredjaKriipsud(&jupp2) )
            valjend.MakeLower();
        /* kontr, kas see on s�nastikus olev v�ljend */
        res = kchk1(&ctoo_variandid.ptr, &valjend, valjend.GetLength(), &csobivad_variandid.ptr, NULL,0);
        if (res > ALL_RIGHT)
	        return res; /* viga! */
        ki = FSxSTR("");
        if (!csobivad_variandid.ptr) // v�tan l�pust ki/gi maha
            {
            ahelad_vabaks(&ctoo_variandid.ptr);
            ki = (const FSxCHAR *)(valjend.Right(2));
            enne_ki = valjend[valjend.GetLength()-3];
            if ( (     // on nii, et...
                (ki == FSxSTR("ki") && TaheHulgad::OnHelitu(enne_ki))  ||    // enne 'ki' helitu h��lik
                (ki == FSxSTR("gi") && !TaheHulgad::OnHelitu(enne_ki)) ||    // enne 'gi' heliline h��lik
                ((ki == FSxSTR("ki") || ki == FSxSTR("gi")) && (enne_ki == V_SH || enne_ki == V_ZH)) // s'ja z' puhul on lubatud nii gi kui ki
                ) )
                {
                S6na3 = (const FSxCHAR *)(valjend.Mid(0, valjend.GetLength()-2));
	            if ( (dctLoend[0])[(FSxCHAR *)(const FSxCHAR *)S6na3] == -1 )
                    { // sonale ikka tohib [gk]i otsa panna
                    res = kchk1(&ctoo_variandid.ptr, &S6na3, S6na3.GetLength(), &csobivad_variandid.ptr, NULL,0); /* ty+lp */
		            if (res > ALL_RIGHT)
		                return false; /* viga! */
                    }
                }
            }
        if (csobivad_variandid.ptr)
            {
            asenda_tyves(&csobivad_variandid.ptr, FSxSTR("="), FSxSTR(" "));
            variandid_tulemuseks(tul, LIIK_VERB, &csobivad_variandid.ptr);
            if (tul->on_tulem())
                {
                tul->keeraYmber = true;
                tul->mitmeS6naline = 2;
                tul->LisaLoppudeleTaha((const FSxCHAR *)ki);
               }
            }
        }
    //ahelad_vabaks(&too_variandid);        //destruktoris
    //ahelad_vabaks(&sobivad_variandid);    //destruktoris
    return ALL_RIGHT;
    }


