
/*
* kontrollib, kas S6na on tyvi+suf+lp;
* paneb seejuures v�imal. sufiksid lp[]-sse
*/
#include <string.h>

#include "mrf-mrf.h"

/*
	kchk2 !=  ALL_RIGHT -- viga
	kchk2 == ALL_RIGHT
		*sobivad_variandid != 0 -- on   s�nastikus/�ige
		*sobivad_variandid == 0 -- pole s�nastikus/�ige
 */

int MORF0::kchk2(
    VARIANTIDE_AHEL **variandid, 
    VARIANTIDE_AHEL **sobivad_variandid, 
    char *paha_koht,
    const int paha_koha_suurus)
    {
    int j;
    int res;
    int  ssu, sty1, k, i;
    FSXSTRING sf;
    int sfnr, sfkoht;
    VARIANTIDE_AHEL *variant, *suf_variant, *mille_taha, *vt_piir, *uus_variant; //ok
    CVARIANTIDE_AHEL cvahe_variant;
    KOMPONENT *tyvi, *lopp, *suf_tyvi, *suf_suf, *suf_lopp;
    char suf_lp_sobiv[SONAL_MAX_PIK];
    FSXSTRING S6na, vt_tyvi;
    int ssl;  /* sufiksi sonaliigi indeks */
    int sobiv_leitud;  /* naitab seda, kas on leitud sobiv ty+suf+lp */

    mille_taha = viimane_variant(*variandid);  /* kuhu uus komponentide ahel paigutada */
    vt_piir = mille_taha;     /* ... ja millest tagapool olevaid ahelaid ei selles programmis ei vt */
    /* tsykkel yle l�ppude (alates lyhimast) */
    for (variant=*variandid; variant; variant=variant->jargmine_variant)
	    {
        if (variant->eelmine_variant == vt_piir) /* jo'udsime selles programmis lisatud variandini */
            break;
        tyvi = esimene_komp(variant);
        if (tyvi->k_tyyp == K_LOPP) /* voib-olla polegi seda kontrolli vaja */
            continue;
        lopp = tyvi->komp_jargmine;
	    sty1 = tyvi->k_pikkus;  /* tyvepikkus */
        S6na = tyvi->k_algus;
        sobiv_leitud = 0;
	    /* tsykkel yle sufiksite (alates pikimast); 0-tyvi ega suf pole lubatud */
	    /* tyvi olgu v�hemalt 2 t�hte pikk */
	    for (ssu = (sty1 > SUFLEN ? SUFLEN-1 : sty1-2); ssu > 0; ssu--)
	        {
	        sfkoht = sty1-ssu;
            sf = (const FSxCHAR *)(S6na.Mid(sfkoht));
	        vt_tyvi = (const FSxCHAR *)(S6na.Left(sfkoht));
	        sfnr = suffnr( (const FSxCHAR *)sf );
	        if (sfnr == -1)    /* sellist sufiksit pole olemas */
		        continue;      /* vt 1 t�he v�rra l�hemat sufiksit */

	        if ( TaheHulgad::OnAlguses(&sf, FSxSTR("lik")) ) 
		        {
                if (TaheHulgad::OnLopus(&(vt_tyvi), FSxSTR("se"))) // ...se+lik on �ldiselt mittesobiv
                    {
                    if (! (TaheHulgad::OnLopus(&(vt_tyvi), FSxSTR("naise")) || TaheHulgad::OnLopus(&(vt_tyvi), FSxSTR("poisikese")) ||
                           TaheHulgad::OnLopus(&(vt_tyvi), FSxSTR("lapse")) || TaheHulgad::OnLopus(&(vt_tyvi), FSxSTR("tossikese"))) )
                           continue;
                    }
                if (TaheHulgad::OnLopus(&(vt_tyvi), FSxSTR("ne"))) // ...ne+lik on �ldiselt mittesobiv
                    {
                    if (! (TaheHulgad::OnLopus(&(vt_tyvi), FSxSTR("laine")) || TaheHulgad::OnLopus(&(vt_tyvi), FSxSTR("eine")) ||
                           TaheHulgad::OnLopus(&(vt_tyvi), FSxSTR("l\x00E4\x00E4ne")) || TaheHulgad::OnLopus(&(vt_tyvi), FSxSTR("\x00F5nne")) || 
                           vt_tyvi == FSxSTR("aine") ))
                           continue;
                    }
                }
            if (TaheHulgad::OnAlguses(&sf, FSxSTR("ikkus")) && !TaheHulgad::OnLopus(&(vt_tyvi), FSxSTR("l"))) // inetu parandus selle puhuks, et on likkus ja ikkus
               continue;
	        /* leidsin 1 sobiva sufiksi */
	        if ( !liide_ok( &vt_tyvi, sfkoht, &sf, taandliik[ sufix[sfnr].tsl ] ) )
		        continue;     /* tyvi+suf ei sobi ortogr. p�hjustel */
            ssl = (unsigned char)(sufix[sfnr].ssl);
            /* maha kirjutanud cyybs.cpp pealt HJK 14.01.2002*/
            for(i=0; i < sonaliik[ssl]->GetLength(); i++)
                {
                MKTc *rec;
                if((rec=tyveMuutused[sufix[sfnr].suftyinf[i].idx.tab_idx])==NULL)
                    {
                    ASSERT( false ); //TODO::throw
                    return CRASH;
                    }
                if(sufix[sfnr].suftyinf[i].idx.blk_idx >= rec->n) 
                    {
                    ASSERT( false ); //TODO::throw
                    return CRASH;       // vale l�pu # grupis 
                    }
                sufix[sfnr].suftyinf[i].lg_nr = (_int16)(rec->mkt1c[sufix[sfnr].suftyinf[i].idx.blk_idx].lgNr);
                }
            if( mrfFlags.Chk(MF_GENE) /* vt ainult algv. loppe */
                && lopp->k_pikkus==0)            /* katsume om, os va'lja soeluda */ 
                {
                k = ssobivus( sufix[sfnr].suftyinf, 
                    (const FSxCHAR *)(*sonaliik[ssl]), sonaliik[ssl]->GetLength(), 
                    lopp->jrk_nr, FSxSTR("ABCDGHIJKMNOPSUXYZ"), sg_n, 
                    suf_lp_sobiv, sizeof(suf_lp_sobiv) );
                if (!k) /* akki on muutumatu sona? */
                    {
                     if ( sf == FSxSTR("mata") || sf == FSxSTR("v\x00F5itu") ) 
                        k = ssobivus( sufix[sfnr].suftyinf, 
                        (const FSxCHAR *)(*sonaliik[ssl]), sonaliik[ssl]->GetLength(), 
                        lopp->jrk_nr, FSxSTR("AD"), SUVA_VRM, suf_lp_sobiv, sizeof(suf_lp_sobiv) );
                    else
                        k = ssobivus( sufix[sfnr].suftyinf, 
                        (const FSxCHAR *)(*sonaliik[ssl]), sonaliik[ssl]->GetLength(), 
                        lopp->jrk_nr, FSxSTR("DGIJKPXYZ"), 
                        SUVA_VRM, suf_lp_sobiv, sizeof(suf_lp_sobiv) );
                    }
                }
            else
                k = ssobivus( sufix[sfnr].suftyinf, 
                (const FSxCHAR *)(*sonaliik[ssl]), sonaliik[ssl]->GetLength(), 
                lopp->jrk_nr, SUVA_LIIK, SUVA_VRM, suf_lp_sobiv, sizeof(suf_lp_sobiv)  );
	        if ( !k )         /* suf+l�pp ei sobi */
    		    continue;

            /* leitud sobiv suf+lp */
            for (j=0; k && j < SONAL_MAX_PIK; j++) /* teen koigi sobivate variantide ahelad */
                {
                if (suf_lp_sobiv[j] == 0)
                    continue;
                /* lisa suf komponent */
                suf_variant = lisa_ahel(&mille_taha, variant);
                if (!suf_variant)
                    return CRASH;
                mille_taha = suf_variant;
                suf_tyvi = esimene_komp(suf_variant);
                suf_lopp = suf_tyvi->komp_jargmine;
                suf_suf = lisa_1komp(&suf_tyvi);
                if (!suf_suf)
                    return CRASH;
                lisa_min_info(suf_tyvi, &S6na, 0, sfkoht);
                lisa_min_info(suf_suf, &S6na, sfkoht, ssu);
                lisa_psl_info(suf_suf, K_SUFF, sfnr);
                lisa_suf_ja_lp_info(suf_suf, (TYVE_INF *)&(sufix[sfnr].suftyinf), ssl, j, suf_lopp->jrk_nr);
                if (TaheHulgad::OnAlguses(&sf, FSxSTR("ke")) && !TaheHulgad::OnAlguses(&sf, FSxSTR("kee")))
                    suf_suf->sl = FSxSTR("");
          
                res = ty_suf(suf_suf, 0, sfkoht, &cvahe_variant.ptr, paha_koht,paha_koha_suurus);
	            if (res > ALL_RIGHT)
	                return res; /* viga! */
                if (cvahe_variant.ptr)
                    {
                    if (on_liitsona(esimene_komp(cvahe_variant.ptr))) /* nt aja_loo */
                        if (TaheHulgad::OnAlguses(&sf, FSxSTR("las")))
                            continue;                       /* et ei tuleks aja_loo_laps */
                    uus_variant = lisa_ahel(sobivad_variandid, cvahe_variant.ptr);
                    if (!uus_variant)
                        return CRASH;
                    ahelad_vabaks(&cvahe_variant.ptr);
                    sobiv_leitud = 1;
		            }
                k--;
                }
		    if (sobiv_leitud)
			    break;    /* selle lopu suf-e enam ei vt */
	        }
	    }
    //ahelad_vabaks(&vahe_variant); //destruktoris
	return ALL_RIGHT;
    }

/*
* kontrollib, kas tyve+sufiksi liitekoht ei sisalda kaash��liku�hendit,
* milles m�ni kaash��lik on topelt (n�it. *'l�pp+lik', aga 'vasall+lik')
*/

int MORF0::liide_ok( FSXSTRING *ty, int typik, FSXSTRING *suf, const FSxCHAR *suf_sl)
    {

    FSXSTRING ssl;
    FSxCHAR vi, eelvi, esi, teine;
    ssl = suf_sl;
    vi = (*ty)[typik-1];
    eelvi = (*ty)[typik-2];
    esi = (*suf)[0];
    teine = (*suf)[1];
    if (ssl.Find((FSxCHAR)'F')==-1)
	    return(1);     /* suf on j�relkomp; v�ib esineda igasug. kaash.yh*/
    if ( vi == esi )
        if ( TaheHulgad::OnKaashaalik1(esi) )
	        if ( TaheHulgad::OnKaashaalik1(teine) )
		        return(0);       /* K+KL; ei juhtu vist kunagi HJK 19.09.94 */
    if ( vi == eelvi )
        {
	    if ( TaheHulgad::OnKaashaalik(esi) )
	        if ( TaheHulgad::OnKaashaalik(vi) )
		    {
		    if ( vi == esi )
		        return(1);       /* KK+K vasall+lik */
		    else
		        return(0);       /* KK+L l�pp+lik*/
		    }
        }
    return(1);
    }

