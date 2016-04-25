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
* kontrollib, kas S6na on 1-t�hel. lyhend;
*/
#include "mrf-mrf.h"
#include "rooma.h"

int MORF0::chklyh0(MRFTULEMUSED *tulemus, FSXSTRING *S6na, int S6naPikkus)
    {
//    int IsRoman(char *Rom);

    if ( S6naPikkus == 1 && TaheHulgad::eestitht.Find(S6na[0])!=-1 )
        {
        if (TaheHulgad::OnSuur(S6na, 0)) // A X
	        {                          /* korraldame va"ljatryki */
            tulemus->Add((const FSxCHAR *)(*S6na), FSxSTR("0"), FSxSTR(""), FSxSTR("Y"), FSxSTR("?, "));
            // if (IsRoman(S6na))
	        //if (IsRoman((const FSxCHAR *)S6na))
            if (!mrfFlags.Chk(MF_ARAROOMA)) // vaja ikka rooma nr kontrollida
                {
                if (TaheHulgad::OnRoomaNr(S6na))
                    {   /* korraldame va"ljatryki */
                    tulemus->Add((const FSxCHAR *)(*S6na), FSxSTR("0"), FSxSTR(""), FSxSTR("O"), FSxSTR("?, ")); 
		            }
                }
	        }
        if (!TaheHulgad::OnSuur(S6na, 0) ||     /*  a */
            TaheHulgad::OnMatemaatika1((*S6na)[0]) /*strchr( "%=+-/", *S6na )*/ || (*S6na)[0] == TaheHulgad::para[0])
	        {                          /* korraldame va"ljatryki */
            tulemus->Add((const FSxCHAR *)(*S6na), FSxSTR("0"), FSxSTR(""), FSxSTR("Y"), FSxSTR("?, ")); 
	        }
        }
    if ( TaheHulgad::OnSuur(S6na, 0) ) /* algab suure t�hega */
        if ( ( S6naPikkus == 2 && (*S6na)[1] == (FSxCHAR)'.' ) ||            /* A. */
	     ( S6naPikkus == 5 && (*S6na)[1] == (FSxCHAR)'.' && (*S6na)[2] == (FSxCHAR)'-' &&
	       TaheHulgad::OnSuur(S6na, 3) && (*S6na)[4] == (FSxCHAR)'.') ) /* A.-E. */
	        {                          /* korraldame va"ljatryki */
            tulemus->Add((const FSxCHAR *)(*S6na), FSxSTR("0"), FSxSTR(""), FSxSTR("Y"), FSxSTR("?, ")); 
	        }
    return ALL_RIGHT;
    }
