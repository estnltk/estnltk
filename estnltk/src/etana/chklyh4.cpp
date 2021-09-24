/*
Copyright 2015 Filosoft OÜ

This file is part of Estnltk. It is available under the license of GPLv2 found
in the top-level directory of this distribution and
at http://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html .
No part of this file, may be copied, modified, propagated, or distributed
except according to the terms contained in the license.

This software is distributed on an "AS IS" basis, without warranties or conditions
of any kind, either express or implied.
*/
/*
* kontrollib, kas S6na on suurt�hel. lyhend ilma k��ndel�puta;
* n�iteks:
*
* USA
*
*/

#include "mrf-mrf.h"
#include "silp.h"

int MORF0::chklyh4(MRFTULEMUSED *tulemus, FSXSTRING *S6na, int S6naPikkus)
    {
    int IsRoman(char *Rom);
    int i=-1;

    if ( TaheHulgad::AintSuuredjaNrjaKriipsud(S6na) )         /* ilmselt LYH */
	    {
        if(mrfFlags.Chk(MF_LYHREZH) == 1) /* range lyhendirezhiim */
            {
            i = (dctLoend[3])[(FSxCHAR *)(const FSxCHAR *)(*S6na)];
            if (i == -1)
                if (S6naPikkus == 1 && TaheHulgad::AintSuured(S6na))  /* (aga 1-sonaline sobib alati) */
                    i = 1;
            }
         else if (!TaheHulgad::MataSymbol(S6na)) // pole ainult numbrite jm matas�mbolite kombinatsioon
            {
            SILP s; // silpide arvu kontroll lisatud 19.05.2003 HJK

            s.silbita(S6na);
            if (s.silpe() < 2)          // pigem akron��m 
                i = 1;
            }
	    if (i != -1)      /* ongi lyhend */
            tulemus->Add((const FSxCHAR *)(*S6na), FSxSTR("0"), FSxSTR(""), FSxSTR("Y"), FSxSTR("?, ")); 
	    }
    else
        return ALL_RIGHT;
    if (!mrfFlags.Chk(MF_ARAROOMA)) // vaja ikka rooma nr kontrollida
        {
	    if (TaheHulgad::OnRoomaNr(S6na))
            {   /* korraldame va"ljatryki */
            tulemus->Add((const FSxCHAR *)(*S6na), FSxSTR("0"), FSxSTR(""), FSxSTR("O"), FSxSTR("?, ")); 
		    }
        }
    return ALL_RIGHT;
    }
