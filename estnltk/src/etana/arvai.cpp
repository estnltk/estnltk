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
// HJK000822  kahtlaste kohtade parandus
/*
* kontrollib, kas S6na on ha'a'litsus;
* n�iteks:
*
* ��hh 
*
*/
#include "mrf-mrf.h"

int MORF0::arvai(MRFTULEMUSED *tulemus, FSXSTRING *S6na, int S6naPikkus)
    {
    FSXSTRING sona;

    if (S6naPikkus < 3)
	    return ALL_RIGHT;
    sona = *S6na;
    sona.MakeLower();
    if (TaheHulgad::OnLopus(&(sona), FSxSTR("hh")) && !TaheHulgad::OnLopus(&(sona), FSxSTR("ehh"))) // pole nt tshehh
		{		  // korraldame va"ljatryki 
        tulemus->Add((const FSxCHAR *)(sona), FSxSTR("0"), FSxSTR(""), FSxSTR("I"), FSxSTR("")); 
	    return ALL_RIGHT;
	    }
    if (TaheHulgad::PoleMuudKui(&sona, &(TaheHulgad::haalitsus1)) ||
        TaheHulgad::PoleMuudKui(&sona, &(TaheHulgad::haalitsus2)))
		{		  // korraldame va"ljatryki 
        tulemus->Add((const FSxCHAR *)(sona), FSxSTR("0"), FSxSTR(""), FSxSTR("I"), FSxSTR("")); 
	    return ALL_RIGHT;
	    }

    return ALL_RIGHT;
    }
