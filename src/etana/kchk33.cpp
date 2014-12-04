
/*
* kontrollib, kas S6na on pref+tyvi+suf+lp
* v�imal. prefiksid ja sufiksid peavad juba olema ahelas
*/

#include "mrf-mrf.h"

int MORF0::kchk33(
    VARIANTIDE_AHEL **variandid, 
    VARIANTIDE_AHEL **sobivad_variandid, 
    char *paha_koht,
    const int paha_koha_suurus)
    {
    int res;
    CVARIANTIDE_AHEL cvahe_variant;
    KOMPONENT *pref, *tyvi, *suff, *lopp, *essa;

    /* ts�kkel �le prefiksite, alates l�himast; 0-pref ja 0-suff pole lubat. */
    for (VARIANTIDE_AHEL *variant=*variandid; variant; variant=variant->jargmine_variant)
	    {
        essa = esimene_komp(variant);
        if (essa->k_tyyp != K_PREF) /* ei algagi prefiksiga */
            continue;
        pref = essa;
        tyvi = pref->komp_jargmine;
        suff = tyvi->komp_jargmine;
        if (suff->k_tyyp != K_SUFF)
            continue;
        lopp = suff->komp_jargmine;
        if (lopp->k_tyyp != K_LOPP)
            continue;
        res = ty_suf(suff, tyvi->nihe, tyvi->k_pikkus, &cvahe_variant.ptr, paha_koht, paha_koha_suurus);
	    if (res > ALL_RIGHT)
	        return res; /* viga! */
        if (!cvahe_variant.ptr)  
            continue;  /* tyve polnud */
        for (VARIANTIDE_AHEL *tmp=cvahe_variant.ptr; tmp; tmp=tmp->jargmine_variant) /* vt neid juhte, kus ty+suf juba sobivad */
            { /* kopeeri sobivate hulka koik tyved, mis selle pref-ga sobivad */
            if (sobib_p_t_s(pref, esimene_komp(tmp), suff))
                {
                kopeeri_komp(tyvi, esimene_komp(tmp));
                //VARIANTIDE_AHEL *sobiv_variant; //ok
                //sobiv_variant = lisa_ahel(sobivad_variandid, variant);
                //if (!sobiv_variant)
                if(lisa_ahel(sobivad_variandid, variant)==NULL)
                    return CRASH;
                if(mrfFlags.Chk(MF_SPELL))
                    {
                    ahelad_vabaks(&cvahe_variant.ptr);
			        return ALL_RIGHT; /* 1. sobiv variant k�lbab */
                    }
                }
            }
        ahelad_vabaks(&cvahe_variant.ptr);
	    }
    return ALL_RIGHT;
    }
