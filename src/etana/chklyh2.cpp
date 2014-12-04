
// HJK000823 boundcheckerige leitud vigade parandus
/*
* kontrollib, kas S6na on lyhend voi lyhend-lp;
*
*/
#include "mrf-mrf.h"
#include "mittesona.h"

int MORF0::chklyh2(MRFTULEMUSED *tulemus, FSXSTRING *S6na)
    {
    int  k, k1;
    const FSxCHAR *vn;
    FSXSTRING S6na3;
    FSXSTRING lyhend;
    FSXSTRING lopp;
    FSXSTRING vorminimi;

    k = (dctLoend[2])[(FSxCHAR *)(const FSxCHAR *)(*S6na)];   // seekord muutuv lyhend ilma loputa
    if ( k != -1 ) /* muutuv lyhend */
	    {                          /* korraldame va"ljatryki */
        tulemus->Add((const FSxCHAR *)(*S6na), FSxSTR("0"), FSxSTR(""), FSxSTR("Y"), FSxSTR("?, ")); 
	    return ALL_RIGHT;
	    }
    else /* pole muutumatu lyhend */
	    {
	    if ( TaheHulgad::AintSuured(S6na) )  /* l�biva suurt�hega s�na */
	        {
            S6na3 = *S6na;
            S6na3.MakeLower();
            k = (dctLoend[2])[(FSxCHAR *)(const FSxCHAR *)S6na3];   
            if ( k != -1 ) /* muutuv lyhend */
	            {                          /* korraldame va"ljatryki */
                tulemus->Add((const FSxCHAR *)(S6na3), FSxSTR("0"), FSxSTR(""), FSxSTR("Y"), FSxSTR("?, ")); 
	            return ALL_RIGHT;
	            }
	        }
	    }
    k1 = S6na->Find((FSxCHAR)'-');
    if ( k1 == -1 )                    /* ei saa olla k��ndel�puga l�hend */
    	return ALL_RIGHT;
    lyhend = (const FSxCHAR *)(S6na->Left(k1));
    if ( (dctLoend[2])[(FSxCHAR *)(const FSxCHAR *)lyhend] == -1 ) /* pole lyhend */
	    {
        if (k1 == 1 && TaheHulgad::eestitht.Find(S6na[0])!=-1); /* 1-ta'heline lyhend on ok */
        else
            {
	        return ALL_RIGHT;
            }
	    }
    lopp = (const FSxCHAR *)(S6na->Mid(k1+1));
    vn = nLopud.otsi_lyh_vorm((const FSxCHAR *)lopp);    
    if ( vn == NULL ) /* pole mingi lopp */
	    {
	    return ALL_RIGHT;
        }
    vorminimi = vn;
    vorminimi += FSxSTR(", ");
    if (lopp == FSxSTR("d") && k1 == 1)
        vorminimi += FSxSTR("sg p, ");
    tulemus->Add((const FSxCHAR *)lyhend, 
              (const FSxCHAR *)lopp, FSxSTR(""), FSxSTR("Y"), (const FSxCHAR *)vorminimi); 
    return ALL_RIGHT;
    }
