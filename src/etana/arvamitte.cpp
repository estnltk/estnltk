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
