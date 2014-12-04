/*
* arvan, et S6na on ...+tyvi2+lp
*/
#include "mrf-mrf.h"
#include "post-fsc.h"

int MORF0::arvans1(MRFTULEMUSED *tulemus, FSXSTRING *S6na, int S6naPikkus, VARIANTIDE_AHEL **variandid)
    {
    int res;
    int  cnt, ty2pik;
    CVARIANTIDE_AHEL ctyvi2_variant, cvahe_variant, csobivad_variandid;
    KOMPONENT komp, *k_tyvi, *tyvi1;
    FSXSTRING ema = FSxSTR("ema");
    FSXSTRING tyvi2;
    //int tugevus;
    int maxty2, minty;

    // et saaks ty2lp() kasutada 
    tyvi1 = &komp;
	res = cXXfirst(ema, 3, &cnt);
    if (res == POLE_SEDA || res == POLE_YLDSE)  // sellist tyve pole olemas 
        return CRASH;  // sellist asja ei saa olla 
    nulli_1komp(tyvi1);
    lisa_min_info(tyvi1, &ema, 0, 3);
    lisa_psl_info(tyvi1, K_TYVI, 0);
    // leiame tyvi1 liitumis-liigid 
    res = juht1(tyvi1, dptr, cnt, &cvahe_variant.ptr);
	if (res > ALL_RIGHT)
	    return res; 
    
    maxty2 = S6naPikkus > 20 ? 20 : S6naPikkus-3;
    if (TaheHulgad::OnSuur(S6na, 0)) // oletatavatele nimedele luban �sna pikki j�relkomponente
        minty = 5;
    else
        minty = 2;
    // vt ko'iki v�imalikke l�ppe 
    for (VARIANTIDE_AHEL *variant=*variandid; variant; variant=variant->jargmine_variant)
	    {
        k_tyvi = esimene_komp(variant);
        if (k_tyvi->komp_jargmine->k_tyyp != K_LOPP)
            continue;
        maxty2 = k_tyvi->k_pikkus > 20 ? 20 : k_tyvi->k_pikkus-3;
        for (ty2pik=maxty2; ty2pik >= minty; ty2pik--)
            {
            tyvi2 = k_tyvi->k_algus.Right(ty2pik);
            if (ty2pik < 4)
                {
                if (!oletajaDct.sobivad_tyved2.Get((const FSxCHAR *)tyvi2))
                    continue; // pole lyhike kuid sobiv
                }
            else
                {
                if (oletajaDct.pahad_tyved2.Get((const FSxCHAR *)tyvi2))
                    continue; // on paha
                }
            // leiame tyvi2 
            res = ty_lp(k_tyvi->komp_jargmine, k_tyvi->k_pikkus - ty2pik, ty2pik, &ctyvi2_variant.ptr, NULL, 0);

	        if (res > ALL_RIGHT)
	            return res; 
            for (VARIANTIDE_AHEL *tmp=ctyvi2_variant.ptr; tmp; tmp=tmp->jargmine_variant) // leia tyvi2 tyybid 
                {
                juht2(esimene_komp(tmp));
                }
            for (VARIANTIDE_AHEL *tmp=cvahe_variant.ptr; tmp; tmp=tmp->jargmine_variant) // tyvi1 tyvepikkus paika 
                {
                lisa_min_info(esimene_komp(tmp), S6na, 0, k_tyvi->k_pikkus - ty2pik); // tyvele uus pikkus 
                esimene_komp(tmp)->sonastikust = 0; // tyvi1 pole s�nastikust HJK 17.05.2004 
                }
            // int tugevus = 
            tyvi1tyvi2(&cvahe_variant.ptr, &ctyvi2_variant.ptr, &csobivad_variandid.ptr);
            // siin vo'iks kunagi veel kontrollida tugevus va'a'rtust, et mitte liiga kahtlasi lubada ...
            ahelad_vabaks(&ctyvi2_variant.ptr);
            if (csobivad_variandid.ptr) // mingi ty1-ga leidub sobiv kombinatsioon 
                {
                ahelad_vabaks(&cvahe_variant.ptr);
                ahelad_vabaks(&ctyvi2_variant.ptr);
                break;   // lyhemaid tyvesid selle lopu puhul ei vt 
                }
            }
	    }
    //ahelad_vabaks(&cvahe_variant.ptr);    //destruktoris
    //ahelad_vabaks(&ctyvi2_variant.ptr);   //destruktoris
    if (csobivad_variandid.ptr)
        {
        if (TaheHulgad::OnSuur(S6na, 0))
            {
            variandid_tulemuseks(tulemus, LIIK_YLDNIMI, &csobivad_variandid.ptr);
            if (tulemus->on_tulem())
                tulemus->TulemidNimeks(LIIK_KAANDSONA);
            }
        else
            variandid_tulemuseks(tulemus, KOIK_LIIGID, &csobivad_variandid.ptr);
        //ahelad_vabaks(&csobivad_variandid.ptr);   //destruktoris
        }
    return ALL_RIGHT;
    }
