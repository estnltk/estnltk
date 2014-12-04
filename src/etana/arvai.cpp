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
