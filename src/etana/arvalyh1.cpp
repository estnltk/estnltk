/*
* kontrollib, kas S6na on v�iket�hel. lyhend ilma k��ndel�puta;
	arvalyh1  !=  ALL_RIGHT -- viga
	arvalyh1  == ALL_RIGHT
		*tulem == Success -- on  nr
		*tulem == Failure -- pole nr

* n�iteks:
*
* c 
*
*/
#include "mrf-mrf.h"

int MORF0::arvalyh1(MRFTULEMUSED *tulemus, FSXSTRING *S6na)
    {
	if (sobiks_lyhendiks(S6na))
        tulemus->Add((const FSxCHAR *)(*S6na), FSxSTR("0"), FSxSTR(""), FSxSTR("Y"), FSxSTR("?, ")); 
    return ALL_RIGHT;
    }
// return true, kui v�iks olla l�hend
bool MORF0::sobiks_lyhendiks(FSXSTRING *S6na)
    {
    //bool i=false;
    int k, l, S6naPikkus;
 
    S6naPikkus = S6na->GetLength();
    if (S6naPikkus == 1)
        return true;
    if (S6naPikkus == 2)
        {
        k = (MORF0::dctLoend[6])[(FSxCHAR *)(const FSxCHAR *)(*S6na)];
        if (k == -1)
            return true;
        }
    if ( TaheHulgad::PoleMuudKui(S6na, &(TaheHulgad::lyh_kaash)) &&
            !TaheHulgad::PoleMuudKui(S6na, &(TaheHulgad::haalitsus2)))       // v�ib olla LYHEND
        return true;
    // �kki on m.o.t.t v�i K.K (l�pupunkt v�ib olla juba �ra v�etud)
    k = S6na->Find(FSxSTR("."));
    if (k != 1)
        return false;
    for (l=0; l < S6naPikkus; l=l+2)
        {
        k = l+1;
        if (!TaheHulgad::eestitht.Find((*S6na)[l]))
            return false; // pole �ige t�ht
        if (k == S6naPikkus) // l�pus pole punkti, aga muidu korras
            return true;
        if ((*S6na)[k] != '.')
            return false; 
        if (k == S6naPikkus-1) // l�pus punkt
            return true;
        }
    return false;
    }

