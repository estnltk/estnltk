
#include "mrf-mrf.h"

/*
* kas voiks olla tyvi + lp ?
* lp on juba varem leitud
*/
int MORF0::ty_lp(
    KOMPONENT *lopp, 
    int nihe, 
    int typikkus, 
    VARIANTIDE_AHEL **sobivad_variandid, 
    char *paha_koht,
    const int paha_koha_suurus
    )
    {
    int  res;
    int  j, k, k1;
    int  cnt;
    signed char lnr;
    VARIANTIDE_AHEL *sobiv_variant;
    KOMPONENT *tyvi, *s_lopp;
    char sobivad[SONAL_MAX_PIK];
    char sobivad1[SONAL_MAX_PIK];

	res = hjk_cXXfirst(&(lopp->algsona), nihe, typikkus, &cnt, paha_koht,paha_koha_suurus);
	if (res > ALL_RIGHT)
	    {
	    return res; /* viga! */
	    }
	if (res == POLE_YLDSE || res == POLE_SEDA)
	    {
	    return ALL_RIGHT;  /* polnud tyve */
	    }
    /* ty leitud */
    lnr = (char)(lopp->jrk_nr);
    if( mrfFlags.Chk(MF_GENE) /* vt ainult algv. loppe */
        && lnr == null_lopp) /* verbile see ei sobi */
        {
        FSXSTRING ty = lopp->algsona.Mid(nihe, typikkus);
        if (omastavanr(&ty) != -1) /* lubatud ainult sg g, pole ohtusid */
            k = ssobivus( dptr, (const FSxCHAR *)(*sonaliik[cnt]), sonaliik[cnt]->GetLength(), 
            lnr, TYLP_LIIK1, sg_g, sobivad, sizeof(sobivad) );
        else                        /* lubatud sg n */
            {
            // peab vaatama nii k��nd- kui muutumatu s�na versiooni, nt enne 
            k = ssobivus( dptr, (const FSxCHAR *)(*sonaliik[cnt]), sonaliik[cnt]->GetLength(),
                lnr, TYLP_LIIK1, sg_n, sobivad, sizeof(sobivad));
            k1 = ssobivus( dptr, (const FSxCHAR *)(*sonaliik[cnt]), sonaliik[cnt]->GetLength(),
                lnr, TYLP_LIIK2, SUVA_VRM, sobivad1, sizeof(sobivad1) ); 
			// kuulukse, tunnukse, n�ikse jaoks
			if (!k && !k1)
				{
				if (lopp->algsona == FSxSTR("kuulukse") || 
					lopp->algsona == FSxSTR("tunnukse") ||
					lopp->algsona == FSxSTR("n\x00E4ikse") )
					k1 = ssobivus( dptr, (const FSxCHAR *)(*sonaliik[cnt]), sonaliik[cnt]->GetLength(), 
                    lnr, LIIK_VERB, SUVA_VRM, sobivad1, sizeof(sobivad1) ); 
				}
			// �ra ei jaoks
			if (!k && k1)
				{
				if (lopp->algsona == FSxSTR("\x00E4ra") ||
					lopp->algsona == FSxSTR("ei") )
					k = ssobivus( dptr, (const FSxCHAR *)(*sonaliik[cnt]), sonaliik[cnt]->GetLength(), 
                    lnr, LIIK_VERB, SUVA_VRM, sobivad, sizeof(sobivad) ); 
				}
            for (j=0; k1 && j < SONAL_MAX_PIK; j++) // tulemused kokku panna
                {
                if (sobivad1[j] == 1 && sobivad[j] == 0)
                    {
                    sobivad[j] = 1;
                    k++;
                    k1--;
                    }
                }
            }
        }
    else
	    k = ssobivus( dptr, (const FSxCHAR *)(*sonaliik[cnt]), sonaliik[cnt]->GetLength(), 
        lnr, SUVA_LIIK, SUVA_VRM, sobivad, sizeof(sobivad) );
    for (j=0; k && j < SONAL_MAX_PIK; j++) /* teen koigi sobivate variantide ahelad */
        {
        if (sobivad[j] == 0)
            continue;
        /* kopeeri ahel */
        sobiv_variant = lisa_1ahel(sobivad_variandid);
        tyvi = lisa_esimene(sobiv_variant);
        if (!tyvi)
            return CRASH;
        lisa_min_info(tyvi, &(lopp->algsona), nihe, typikkus);
        lisa_psl_info(tyvi, K_TYVI, 0);
        s_lopp = lisa_1komp(&tyvi);
        if (!s_lopp)
            return CRASH;
        kopeeri_komp(s_lopp, lopp);
        /* pane ahelas inf korda */
        lisa_ty_ja_lp_info(sobiv_variant, dptr, cnt, j, lnr);
        k--;
        }
    return ALL_RIGHT;
    }

/*
* kas voiks olla tyvi + suf ?
* suf + lp on juba varem leitud
*/

int MORF0::ty_suf(
    KOMPONENT *suff, 
    int nihe, int typikkus, 
    VARIANTIDE_AHEL **sobivad_variandid, 
    char *paha_koht,
    const int paha_koha_suurus
    )
    {
    int  res;
    int  j, k;
    int  cnt;
    signed char klp;
    FSXSTRING s_n_sl;    /* sufiksi poolt n�utav s�naliik */
    VARIANTIDE_AHEL *sobiv_variant;
    KOMPONENT *tyvi, *suf, *lopp;
    char sobivad[SONAL_MAX_PIK];
    char sodi_sobiv[SONAL_MAX_PIK];
    FSXSTRING vt_tyvi;
    FSXSTRING ty = suff->algsona.Mid(nihe, typikkus);
    int  tylp;   
    int ty1_sl_ind;
    int  sfnr;
    int  ssu;
    FSXSTRING sf;
    TYVE_INF ty1_lgrd[SONAL_MAX_PIK+1];
    FSXSTRING mooda;

#if defined( FSCHAR_ASCII )
    mooda = FSxSTR("m��da");
#elif defined( FSCHAR_UNICODE )
    mooda = FSxSTR("m\x00F6\x00F6\x0064\x0061");
#else 
    #error Unicode Realiseerimata
#endif
	sfnr = suff->jrk_nr;
	tylp = sufix[sfnr].tylp;
    vt_tyvi = ty;
    vt_tyvi += tyvelp[tylp];
    sf = suff->k_algus;
    ssu = suff->k_pikkus;
    if (sf == FSxSTR("kus") && TaheHulgad::OnLopus(&vt_tyvi, FSxSTR("rikas")))
        return ALL_RIGHT; // vastik erijuht: rikas on ainus A, millest ei saa teha tyvi - kas + kus

	if (tyvelp[tylp])
        res = cXXfirst(&vt_tyvi, &cnt);
    else
        res = hjk_cXXfirst(&(suff->algsona), nihe, typikkus, &cnt, paha_koht,paha_koha_suurus);
	if (res > ALL_RIGHT)
	    {
	    return res; /* viga! */
	    }
	if (res == POLE_YLDSE || res == POLE_SEDA) /*sellise algusega tyve sonastikus pole*/
		{
        if (sf == FSxSTR("tus") || sf == FSxSTR("tuse") )
            {                         /* vaa+tus - vaa+ta+ma */
            vt_tyvi += FSxSTR("ta");
		    res = cXXfirst(&vt_tyvi, &cnt);
		    if (res > ALL_RIGHT)
			    return res; /* viga! */
		    if (res == ALL_RIGHT)
			    klp = lopp_ma;
		    }
		}
	if (res == POLE_YLDSE || res == POLE_SEDA) /*sellist tyve sonastikus pole*/
        {             /* ehk on nt kompromislik ? */
        if (TaheHulgad::OnAlguses(&sf, FSxSTR("lik")) && vt_tyvi.GetLength()/*styvi*/ > 1)
            {
            if ( vt_tyvi.GetLength() > 2 &&
                TaheHulgad::OnKaashaalik( (int)vt_tyvi[vt_tyvi.GetLength()-1] ) &&
                !TaheHulgad::OnKaashaalik( (int)vt_tyvi[vt_tyvi.GetLength()-2] ))
                {
                vt_tyvi += vt_tyvi.Right(1);
		        //res = cXXfirst(vt_tyvi, vt_tyvi.GetLength()/*styvi*/, &cnt);
		        res = cXXfirst(&vt_tyvi, &cnt);
		        if (res > ALL_RIGHT)
			        return res; /* viga! */
                }
            }
        }
	if (res == POLE_YLDSE || res == POLE_SEDA)
	    {
	    return ALL_RIGHT;  /* polnud tyve */
	    }
    /* ty leitud */
	s_n_sl = taandliik[ sufix[suff->jrk_nr].tsl ];
   	klp = sufix[suff->jrk_nr].taandlp;
    k = ssobivus(dptr, (const FSxCHAR *)(*sonaliik[cnt]), sonaliik[cnt]->GetLength(), 
        klp, (const FSxCHAR *)s_n_sl, SUVA_VRM, sobivad, sizeof(sobivad));
	if ( !k )  /* aga tyvi+suf ei sobi */
		{      /* vt, kas 'tu' puhul S+(d)+suf sobivad */
		if ( sf.Left(ssu) == FSxSTR("tu"))
			{
            //k = ssobivus( dptr, sonaliik[cnt].sliik, sonaliik[cnt].pikkus, lopp_d, FSxSTR("S"), SUVA_VRM, sobivad );
            k = ssobivus( dptr, (const FSxCHAR *)(*sonaliik[cnt]), sonaliik[cnt]->GetLength(), 
                lopp_d, FSxSTR("S"), SUVA_VRM, sobivad, sizeof(sobivad) );
			if (k)
                suff->sl = FSxSTR("A");
			}
		}
	if ( !k )  /* aga tyvi+suf ei sobi */
		{      /* vt, kas 'tus' puhul S+(d)+suf sobivad */
		if ( /* ssu > 2 && ! strncmp(sf, "tuse", ssu) */ 
            TaheHulgad::OnAlguses(&sf, FSxSTR("tus")) )
			{
            //k = ssobivus( dptr, sonaliik[cnt].sliik, sonaliik[cnt].pikkus, lopp_d, FSxSTR("S"), SUVA_VRM, sobivad );
            k = ssobivus( dptr, (const FSxCHAR *)(*sonaliik[cnt]), sonaliik[cnt]->GetLength(),
                lopp_d, FSxSTR("S"), SUVA_VRM, sobivad, sizeof(sobivad) );
			}
		}
	if ( !k )  /* ikka tyvi+suf ei sobi */
		{      /* �kki on 'G'+line ? */
		if (s_n_sl.Find((FSxCHAR) 'G')!=-1 && klp == lopp_d )
			{ /* (nipitamine; vt failis 'sufiks' LINE, LISEM,...*/
            //k = ssobivus( dptr, sonaliik[cnt].sliik, sonaliik[cnt].pikkus, null_lopp, FSxSTR("G"), SUVA_VRM, sobivad );
            k = ssobivus( dptr, (const FSxCHAR *)(*sonaliik[cnt]), sonaliik[cnt]->GetLength(),
                null_lopp, FSxSTR("G"), SUVA_VRM, sobivad, sizeof(sobivad) );
			}
		}
	if (k)
		{
        if (klp == null_lopp)
            {
		    if ( s_n_sl.Find((FSxCHAR) 'G') != -1 )
			    {		/* st. suf v�i j�r.k. n�uab sg_ng */
			    //k = ssobivus(dptr, sonaliik[cnt].sliik, sonaliik[cnt].pikkus, klp, FSxSTR("G"), SUVA_VRM, sobivad);
			    k = ssobivus(dptr, (const FSxCHAR *)(*sonaliik[cnt]), sonaliik[cnt]->GetLength(),
                    klp, FSxSTR("G"), SUVA_VRM, sobivad, sizeof(sobivad));
                if (!k)
			        k = ssobivus(dptr, (const FSxCHAR *)(*sonaliik[cnt]), sonaliik[cnt]->GetLength(), 
                    klp, (const FSxCHAR *)s_n_sl, sg_n, sobivad, sizeof(sobivad));
                if (!k)
                    k = ssobivus(dptr, (const FSxCHAR *)(*sonaliik[cnt]), sonaliik[cnt]->GetLength(), 
                    klp, (const FSxCHAR *)s_n_sl, sg_g, sobivad, sizeof(sobivad));
			    }
		    else if ( /*(!strcmp(sf, "pidi") || !strcmp(sf, "m��da")) */
                    sf == FSxSTR("pidi") || sf == mooda)
			    {		/* st. j�r.k. n�uab 'partit' */
			    k = ssobivus( dptr, (const FSxCHAR *)(*sonaliik[cnt]), sonaliik[cnt]->GetLength(), 
                    klp, (const FSxCHAR *)s_n_sl, sg_p, sobivad, sizeof(sobivad));
                if (!k)
			        k = ssobivus( dptr, (const FSxCHAR *)(*sonaliik[cnt]), sonaliik[cnt]->GetLength(), 
                    klp, (const FSxCHAR *)s_n_sl, pl_p, sobivad, sizeof(sobivad));
			    }
            else;
            }
		}
	if (k)     /* tyvi+suf+lp sobivad kokku */
		{
        if ( /* ! strncmp(sf, "tav", 3) && strncmp(sf, "tavasti", 7)*/ 
              TaheHulgad::OnAlguses(&sf, FSxSTR("tav")) && !TaheHulgad::OnAlguses(&sf, FSxSTR("tavasti")))
            {   /* on hoopis =v sufiks ? */
            if (/*strcmp(vt_tyvi, "kae") && strcmp(vt_tyvi, "soovi")*/
                  vt_tyvi != FSxSTR("kae") && vt_tyvi != FSxSTR("soovi"))
                {  /* kae=tava+id, soovi=tava+id ei muuda */
                vt_tyvi += FSxSTR("ta");
                ty1_sl_ind = cnt;
                LgCopy( ty1_lgrd, dptr, cnt );
			    res = cXXfirst(&vt_tyvi, &cnt);
			    if (res > ALL_RIGHT)
			        return res; // viga!
                if (res == ALL_RIGHT && // vt_tyvi+ta on OK...
                     (ssobivus(dptr, (const FSxCHAR *)(*sonaliik[cnt]), sonaliik[cnt]->GetLength(), 
                     klp, (const FSxCHAR *)s_n_sl, SUVA_VRM, sodi_sobiv, sizeof(sodi_sobiv)))!=0) //... ja sobib sufiksiga
                    {  /* siis =tav asemel sobiks =v */
                    cnt = ty1_sl_ind;
                    LgCopy( dptr, ty1_lgrd, cnt );
                    return ALL_RIGHT;  
                    }
                else
                    {
                    cnt = ty1_sl_ind;
                    LgCopy( dptr, ty1_lgrd, cnt );
                    }
                }
            }
        }
    if (k > 1 && klp == null_lopp) /* ja'relkomponentide jaoks */
        { /* valime ainsuse omastava tyve */
        FSXSTRING tsl = taandliik[ sufix[sfnr].tsl ];
        if (tsl.Find((FSxCHAR)'F')==-1) /* ja'relkomponent */
            k = ssobivus(dptr, (const FSxCHAR *)(*sonaliik[cnt]), sonaliik[cnt]->GetLength(), 
            klp, (const FSxCHAR *)s_n_sl, sg_g, sobivad, sizeof(sobivad));
        }

    for (j=0; k && j < SONAL_MAX_PIK; j++) /* teen koigi sobivate variantide ahelad */
        {
        if (sobivad[j] == 0)
            continue;
        /* kopeeri ahel */
        sobiv_variant = lisa_1ahel(sobivad_variandid);
        tyvi = lisa_esimene(sobiv_variant);
        if (!tyvi)
            return CRASH;
        lisa_min_info(tyvi, &(suff->algsona), nihe, typikkus);
        lisa_psl_info(tyvi, K_TYVI, 0);
        suf = lisa_1komp(&tyvi);
        if (!suf)
            return CRASH;
        lopp = lisa_1komp(&suf);
        if (!lopp)
            return CRASH;
        kopeeri_komp(suf, suff);
        kopeeri_komp(lopp, suff->komp_jargmine);
        /* pane ahelas inf korda */
        lisa_ty_info(tyvi, dptr, cnt, j);
        k--;
        }
    return ALL_RIGHT;
    }

/*
* leiab komponentide ahelast algusega 'tyvi', kas see v�iks olla tyvi+lp v�i tyvi+suf+lp
* seejuures m��ratleb ka tyvi tyybi liitsona viimase tyvena
*/
int MORF0::ty2jne(
    KOMPONENT *tyvi, 
    VARIANTIDE_AHEL **varasemad_variandid, 
    VARIANTIDE_AHEL **sobivad_variandid, 
    char *paha_koht,
    const int paha_koha_suurus)
    {
    int res = ALL_RIGHT;

    if (tyvi->komp_jargmine->k_tyyp == K_LOPP)
        res = ty_lp(tyvi->komp_jargmine, tyvi->nihe, tyvi->k_pikkus, sobivad_variandid, 
                                    paha_koht, paha_koha_suurus);
    else if (tyvi->komp_jargmine->k_tyyp == K_SUFF)
        {
        FSXSTRING tsl = taandliik[ sufix[tyvi->komp_jargmine->jrk_nr].tsl ];
        if (tsl.Find((FSxCHAR)'F')!=-1) /* t�eline sufiks */
            if (!on_tylopuga(*varasemad_variandid, NULL, tyvi->komp_jargmine->komp_jargmine)) /* selle lopuga varianti veel pole */
                res = ty_suf(tyvi->komp_jargmine, tyvi->nihe, tyvi->k_pikkus, sobivad_variandid, 
                                    paha_koht,paha_koha_suurus);
        }
    else 
        return CRASH;  /* voimatu olukord */
 
	if (res > ALL_RIGHT)
	    return res; /* viga! */
    for (VARIANTIDE_AHEL *tmp=*sobivad_variandid; tmp; tmp=tmp->jargmine_variant) /* leia tyvi2 tyybid */
        {
        juht2(esimene_komp(tmp));
        }

    return ALL_RIGHT;
    }





