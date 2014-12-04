
/*
* kontrollib, kas word on tyvi+lp;

	chk1  !=  ALL_RIGHT -- viga
	chk1  == ALL_RIGHT
		*sobivad_variandid != 0 -- on   s�nastikus/�ige
		*sobivad_variandid == 0 -- pole s�nastikus/�ige

* algoritm: eraldab s�na l�pust l�ppe (alates LYHIMAST v�imalikust) ja
*           kontrollib, kas m�ni v�ib olla eesti k s�na l�pp
*           kui v�ib, siis kontrollib, kas vastav t�vi on s�nastikus
*           kui on, siis kontrollib, kas eraldatud l�pp ja leitud t�vi sobivad kokku
*           kui sobivad, siis lisab variantide ahela
*/
#include "mrf-mrf.h"

int MORF0::kchk1(
    VARIANTIDE_AHEL **variandid, 
    FSXSTRING *word, 
    int S6naPikkus, 
    VARIANTIDE_AHEL **sobivad_variandid, 
    char *paha_koht,
    const int paha_koha_suurus)
    {
    register int i, tyvepik;
    int  res;
    int  algp;
    FSXSTRING sona, end;
    signed char lnr;
    VARIANTIDE_AHEL **mille_taha, *variant, *sobiv_variant, **sobiva_taha, *tmp; //ok
    CVARIANTIDE_AHEL cvahe_variant; 
    KOMPONENT *tyvi, *lopp;
    sona = *word;
    mille_taha = variandid;  /* kuhu uus komponentide ahel paigutada */
    sobiva_taha = sobivad_variandid;
    if ( S6naPikkus > ENDLEN )
	    algp = ENDLEN - 1;    /* v�imalik max pikkusega l�pp */
    else
	    {
        if (sona[0] == (FSxCHAR)'e' || sona[0] == V_O_UML)
	        algp = S6naPikkus - 1;    /* tyvi v�ib olla 1 t�heline */
	    else
	        algp = S6naPikkus - 2;    /* tyvi olgu v�hemalt 2 t�heline */
	    }
    for (i = 0; i <= algp; i++)
	    {
	    if (i)
	        {
	        tyvepik = S6naPikkus - i;
            end = (const FSxCHAR *)(sona.Mid(tyvepik));
            if(mrfFlags.Chk(MF_GENE)) /* vt ainult algv. loppe */
                {
                if (loend.head_gene_lopud.Get((FSxCHAR *)(const FSxCHAR *)end))
	                lnr = lpnr( (const FSxCHAR *)end );
                else
		            continue;     /* vt 1 t�he v�rra l�hemat l�ppu */
                }
            else        /* vt. koiki loppe */
                {
	            lnr = lpnr( (const FSxCHAR *)end );
	            if (lnr == -1)    /* sellist l�ppu pole olemas */
		            continue;     /* vt 1 t�he v�rra l�hemat l�ppu */
                }
	        }
	    else         /* null-l�pp */
	        {
	        tyvepik = S6naPikkus;
	        lnr = null_lopp;
	        }
        /* mingi lopp leitud */
        variant = lisa_1ahel(mille_taha);
        mille_taha = &variant;
        tyvi = lisa_esimene(variant);
        if (!tyvi)
            {
            return CRASH;
            }
        lisa_min_info(tyvi, word, 0, tyvepik);
        lopp = lisa_1komp(&tyvi);
        if (!lopp)
            {
            return CRASH; 
            }
        lisa_min_info(lopp, word, tyvepik, i);
        lisa_psl_info(lopp, K_LOPP, lnr);
        /* otsi ty ja kontrolli ta sobivust lopuga */
        res = ty_lp(lopp, 0, tyvepik, &cvahe_variant.ptr, paha_koht,paha_koha_suurus);
	    if (res > ALL_RIGHT)
            {
	        return res; /* viga! */
            }
        if (!cvahe_variant.ptr)  
            continue;  /* tyve polnud */
        for (tmp=cvahe_variant.ptr; tmp; tmp=tmp->jargmine_variant)
            { /* kopeeri sobivate hulka koik tyved, mis selle lopuga sobivad */
            sobiv_variant = lisa_ahel(sobiva_taha, tmp);
            if (!sobiv_variant)
                {
                return CRASH;
                }
            if(mrfFlags.Chk(MF_SPELL)) // aitab 1 tyvest kyll
                break;
            sobiva_taha = &sobiv_variant;
            }
        ahelad_vabaks(&cvahe_variant.ptr);
        if(mrfFlags.Chk(MF_SPELL))
            {
            return ALL_RIGHT; /* rohkem variante ei vt. */
            }
        }
    return ALL_RIGHT;
    }

