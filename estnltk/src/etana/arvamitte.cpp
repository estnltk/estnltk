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
* oletab et S6na on 'mittes�na' nt . " *
  eri t��pi kriipsudega ei tegele;
  sellega tegelevad nii chkmin kui arvamin
*/
#include "mrf-mrf.h"

int MORF0::arvamitte(MRFTULEMUSED *tulemus, FSXSTRING *S6na)
    {
    if ( TaheHulgad::PoleMuudKui(S6na, &(TaheHulgad::s_punktuatsioon)))         /* ilmselt _Z_ */
	    {			  /* korraldame va"ljatryki */
        tulemus->Add((const FSxCHAR *)(*S6na), FSxSTR(""), FSxSTR(""), FSxSTR("Z"), FSxSTR("")); 
	    }
	return ALL_RIGHT;
	}
