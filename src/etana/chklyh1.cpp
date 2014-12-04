
/*
* kontrollib, kas S6na on muutumatu lyhend;
*
*/
#include "mrf-mrf.h"

int MORF0::chklyh1(MRFTULEMUSED *tulemus, FSXSTRING *S6na)
    {
    int k;
//    char S6na3[STEMLEN];
    FSXSTRING S6na3;

    k = ( (dctLoend[1])[(FSxCHAR *)(const FSxCHAR *)(*S6na)] );
    if ( k != -1 ) /* muutumatu lyhend */
	    {                          /* korraldame va"ljatryki */
        tulemus->Add((const FSxCHAR *)(*S6na), FSxSTR("0"), FSxSTR(""), FSxSTR("Y"), FSxSTR("?, ")); 
	    }
    else /* pole muutumatu lyhend */
	    {
        if ( TaheHulgad::AintSuured(S6na) /*koik_suured(S6na, S6naPikkus)*/ )  /* l�biva suurt�hega s�na */
	        {
            S6na3 = *S6na;
            S6na3.MakeLower();
	        k = ( (dctLoend[1])[(FSxCHAR *)(const FSxCHAR *)S6na3] );
            if ( k != -1 ) /* muutumatu lyhend */
	            {                          /* korraldame va"ljatryki */
                tulemus->Add((S6na3), FSxSTR("0"), FSxSTR(""), FSxSTR("Y"), FSxSTR("?, ")); 
	            }
	        }
	    }
    if(mrfFlags.Chk(MF_VEEBIAADRESS))
        {
        /* kontr, kas on www-aadress */
        if (sobiks_veebiaadressiks(S6na))
	        {                          /* korraldame va"ljatryki */
            tulemus->Add((const FSxCHAR *)(*S6na), FSxSTR("0"), FSxSTR(""), FSxSTR("Y"), FSxSTR("?, ")); 
	        }
        /* kontr, kas on e-maili aadress */
        if (sobiks_emailiks(S6na))
	        {                          /* korraldame va"ljatryki */
            tulemus->Add((const FSxCHAR *)(*S6na), FSxSTR("0"), FSxSTR(""), FSxSTR("Y"), FSxSTR("?, ")); 
	        }
        }
    return ALL_RIGHT;
    }

bool MORF0::sobiks_emailiks(FSXSTRING *S6na)
    {
    int k, l;

    k = S6na->Find(FSxSTR("@"));
    if (k > 1)
        {
        l = S6na->Find(FSxSTR("@"), k);
        if (l > k) // on mitu @
            return false;
        l = S6na->Find(FSxSTR("."), k);
        if (l > k+1 && l < S6na->GetLength()-2)
            {
	        return true;
            }
        }
    return false;
    }

bool MORF0::sobiks_veebiaadressiks(FSXSTRING *sisendS6na)
    {
    int k, l;
    FSXSTRING S6na;

    k = sisendS6na->Find(FSxSTR("@"));
    if (k > -1)
        return false;
    S6na = *sisendS6na;
    S6na.MakeLower();
    if (TaheHulgad::OnAlguses(&S6na, FSxSTR("http://")))
        return true;
    if (TaheHulgad::OnAlguses(&S6na, FSxSTR("https://")))
        return true;
    if (TaheHulgad::OnAlguses(&S6na, FSxSTR("ftp://")))
        return true;
    if (TaheHulgad::OnAlguses(&S6na, FSxSTR("telnet://")))
        return true;
    if (TaheHulgad::OnAlguses(&S6na, FSxSTR("gopher://")))
        return true;
    if (TaheHulgad::OnAlguses(&S6na, FSxSTR("ldap://")))
        return true;
    if (TaheHulgad::OnAlguses(&S6na, FSxSTR("www.")))
        return true;
    /* �kki on ikkagi www-aadress ? */
    k = S6na.Find(FSxSTR("."));
    if (k > 1)
        {
        l = S6na.Find(FSxSTR("."), k+1);
        if (l > k+2 && l < S6na.GetLength()-2) // oli 2 . ja nad olid piisaval kaugusel
            {
            FSXSTRING S6na1;
            S6na1 = S6na.Left(k);
            if ( TaheHulgad::PoleMuudKui(&S6na1, &(TaheHulgad::eestitht)) )     // aadressi alguses olgu ainult t�hed  
                {
                S6na1 = S6na.Mid(l+1);       // otsin aadressi l�ppu
                l = S6na1.Find(FSxSTR("/"));
                if (l != -1)                  // aadressi j�rel veel katalooge jms
                    S6na1 = S6na1.Left(l);
                l = S6na1.ReverseFind(FSxSTR("."));
                if (l != -1)
                    S6na1 = S6na1.Mid(l+1);   // S6na1 on aadressi viimane ots
                if ( TaheHulgad::PoleMuudKui(&S6na1, &(TaheHulgad::eestitht)) )       // aadressi l�pus on ainult t�hed
                    {
	                return true;
                    }
                }
            }
        }
    return false;
    }
