// kontrollib, kas s�na on suurt�heline l�hend
#include "mrf-mrf.h"

int MORF0::arvalyh2(MRFTULEMUSED *tulemus, FSXSTRING *S6na)
    {
    if (sobiks_akronyymiks(S6na))
        tulemus->Add((const FSxCHAR *)(*S6na), FSxSTR("0"), FSxSTR(""), FSxSTR("Y"), FSxSTR("?, ")); 
    return ALL_RIGHT;
    }

// return true, kui v�iks olla akron��m
bool MORF0::sobiks_akronyymiks(FSXSTRING *S6na)
    {
    SILP s;
    int S6naPikkus;

    S6naPikkus = S6na->GetLength();
    if (S6naPikkus < 3)
        return true;
    if (!TaheHulgad::PoleMuudKui(S6na, &(TaheHulgad::suurnrthtkriips)))
        return false;
    if (S6naPikkus < 5)
        return true;
    s.silbita(S6na);
    if (s.silpe() < 2)          // pigem akron��m
        return true;
    return false;
    }
