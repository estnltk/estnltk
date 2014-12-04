
/*
* otsib tyve, kusjuures arvestab juba leitud juppidega
*/
#include <string.h>

#include "mrf-mrf.h"

int MORF0::hjk_cXXfirst(
    FSXSTRING *S6na_algus, 
    int nihe, 
    int JupiPikkus, 
    int *cnt, 
    char *paha_koht,            //massiivi 'paha_koht' pikkus muutujas 'paha_koha_suurus'
    const int paha_koha_suurus  //throw, kui �ritab kirjutada �le massiivi 'paha_koht' otsa
    )
    {
    int res;
    assert(nihe>=0 && JupiPikkus>=0 && paha_koha_suurus>=0);
    
    if (!paha_koht) /* pahade kohtade tabelit pole olemaski */
        return(cXXfirst(S6na_algus->Mid(nihe)/*S6na_algus+nihe*/, JupiPikkus, cnt));
    if (!(*(paha_koht + nihe*(STEMLEN+1) + JupiPikkus))) /* selle jupi k�lbmatus pole teada */
	{
	res = cXXfirst(S6na_algus->Mid(nihe)/*S6na_algus+nihe*/, JupiPikkus, cnt);
        if (res == POLE_SEDA)         /* m�rgin k�lbmatu(d) koha(d) �ra */
            {
            int pos=nihe*(STEMLEN+1)+JupiPikkus;
            if(pos >= paha_koha_suurus)
                throw VEAD(ERR_MORFI_MOOTOR, ERR_MINGIJAMA, __FILE__, __LINE__,"$Revision: 596 $");
            paha_koht[pos]=1;
            }
        else if (res == POLE_YLDSE)
            {
            int algus=nihe*(STEMLEN+1) + JupiPikkus;
            int pikkus=STEMLEN-JupiPikkus+1;
            if(algus<0 || pikkus<0 || algus+pikkus>paha_koha_suurus)
                throw VEAD(ERR_MORFI_MOOTOR, ERR_MINGIJAMA, __FILE__, __LINE__,"$Revision: 596 $");
            memset(paha_koht+algus, 1, pikkus);
            }
        return res;
	}
    else 
        return POLE_SEDA;
    }

void MORF0::init_hjk_cxx(
    int S6naPikkus, 
    char *paha_koht, 
    const int paha_koha_pikkus
    )
    {
    int i;
    
    if (!paha_koht)
        throw VEAD(ERR_MORFI_MOOTOR, ERR_MINGIJAMA, __FILE__, __LINE__,"$Revision: 596 $");
    for (i=0; i <= S6naPikkus; i++)
        {
        if(i*(STEMLEN+1)+S6naPikkus+1>paha_koha_pikkus)
            throw VEAD(ERR_MORFI_MOOTOR, ERR_MINGIJAMA, __FILE__, __LINE__,"$Revision: 596 $");
        memset(paha_koht + i*(STEMLEN+1), 0, S6naPikkus+1);
        }
    }

/*
* kui alayysitav sona on eelmise sona mingi osa, 
* siis tuleb tema vana paha_koht v_paha teisendada uueks massiiviks u_paha 
* kõlbab ka selleks puhuks, kui u_paha on suurem kui v_paha
*/
//TV080723 char *MORF0::uus_paha( 
void MORF0::uus_paha(
    int v_pikkus, 
    const char *v_paha, 
    int u_pikkus, 
    char *u_paha,           // massiivi 'u_paha' pikkus muutujas 'u_paha_pikkus'
    const int u_paha_pikkus // throw, kui massiivi 'u_paha' kirjutamine l�heb �le otsa
    )
    {
    int i, j, vahe, u_koht, v_koht;

    if (!v_paha || !u_paha)
        throw VEAD(ERR_MORFI_MOOTOR, ERR_MINGIJAMA, __FILE__, __LINE__,"$Revision: 596 $");
    vahe = v_pikkus - u_pikkus;
    for (i=0; i <= u_pikkus; i++)
        {
        for (j=0; j <= u_pikkus-i+1; j++)
            {
            if (i+vahe >=0 && j+vahe >= 0) /* sest vahe v�ib olla negatiivne */
                {
                v_koht = (i+vahe)*(STEMLEN+1) + j;
                u_koht = i*(STEMLEN+1) + j;
                if(u_koht>=u_paha_pikkus) // kontrollime, et ei kirjutaks �le otsa
                    throw VEAD(ERR_MORFI_MOOTOR, ERR_MINGIJAMA, __FILE__, __LINE__,"$Revision: 596 $");
                u_paha[u_koht]=v_paha[v_koht];
                }
            }
        }
    }
