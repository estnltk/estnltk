
/*
* kontrollib, kas on pref + tyvi
*/

#include "mrf-mrf.h"

int MORF0::kchk30(
    VARIANTIDE_AHEL **variandid, 
    FSXSTRING *S6na, int S6naPikkus, 
    VARIANTIDE_AHEL **sobivad_variandid, 
    char *paha_koht,
    const int paha_koha_suurus)
    {
    register int i, max;
    VARIANTIDE_AHEL *sobiv_variant, *tmp, *variant, *pref_variant, *mille_taha, *vt_piir; //ok
    CVARIANTIDE_AHEL cvahe_variant;
    KOMPONENT *tt, *tyvi, *pref, *lopp, *essa;
    int prnr;
    int res;
    FSXSTRING prefiks;

    mille_taha = viimane_variant(*variandid);  /* kuhu uus komponentide ahel paigutada */
    vt_piir = mille_taha;     /* ... ja millest tagapool olevaid ahelaid ei selles programmis ei vt */
    max = S6naPikkus < PREFLEN ? S6naPikkus-2 : PREFLEN-1;
    /* teen kindlaks k�ik selle s�na v�imalikud prefiksid; alustan pikematest */
    for (i=max; i > 1; i--)
	    {
        prefiks = (const FSxCHAR *)(S6na->Left(i));
	    prnr = preffnr( (const FSxCHAR *) prefiks );
	    if (prnr == -1)    /* sellist prefiksit pole olemas */
	        continue;      /* vt 1 t�he v�rra pikemat prefiksit */
        /* lisan prefiksitega variandid ahelatesse */
        for (variant=*variandid; variant; variant=variant->jargmine_variant)
	        {
            if (variant->eelmine_variant == vt_piir) /* jo'udsime selles programmis lisatud variandini */
                break;
            tt = esimene_komp(variant); /* tt on ahela esimene komponent */
            if (tt->k_pikkus <= i) /* sellel tyvele pref ette ei mahu */
                continue;

            /* teen uue variandi ja lisan ta ahelate hulka */
            pref_variant = lisa_ahel(&mille_taha, variant);
            if (!pref_variant)
                return CRASH;
//            mille_taha = pref_variant;
            pref = esimene_komp(pref_variant);
            tyvi = lisa_1komp(&pref);
            if (!tyvi)
                return CRASH;
            nulli_1komp(pref);
            lisa_min_info(pref, S6na, 0, i);
            lisa_min_info(tyvi, S6na, i, tt->k_pikkus-i);
            lisa_psl_info(pref, K_PREF, prnr);
            /* kontr, kas uus variant on pref + ty + lp */
            lopp = tyvi->komp_jargmine;
            if (lopp->k_tyyp != K_LOPP)
                continue;
	        /* tyvi+lp */
            res = ty_lp(lopp, tyvi->nihe, tyvi->k_pikkus, &cvahe_variant.ptr, paha_koht,paha_koha_suurus);
	        if (res > ALL_RIGHT)
	            return res; /* viga! */
            if (!cvahe_variant.ptr)  
                continue;  /* tyve polnud */
            for (tmp=cvahe_variant.ptr; tmp; tmp=tmp->jargmine_variant) /* vt neid juhte, kus ty+lp juba sobivad */
                { /* kopeeri sobivate hulka koik tyved, mis selle lopuga sobivad */
                essa = esimene_komp(tmp);
                if (sobib_p_t(pref, essa))
                    {
                    kopeeri_komp(tyvi, essa);
                    kopeeri_komp(lopp, essa->komp_jargmine);
                    sobiv_variant = lisa_ahel(sobivad_variandid, pref_variant);
                    if (!sobiv_variant)
                        return CRASH;
                    if(mrfFlags.Chk(MF_SPELL))
                        {
                        //ahelad_vabaks(&vahe_variant); //destruktoris
			            return ALL_RIGHT; /* 1. sobiv variant k�lbab */
                        }
                    }
                }
            ahelad_vabaks(&cvahe_variant.ptr);
	        }
        if (*sobivad_variandid) /* rohkem prefe ei vt */
            return ALL_RIGHT;
        }
    return ALL_RIGHT;
    }
