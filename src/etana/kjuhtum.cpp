
// teeb kindlaks, millise tyybiga on liitsõnas tyvi1 puhul tegu
//

#include <string.h>

#include "mrf-mrf.h"
#include "cxxbs3.h"
#include "mittesona.h"

void MORF0::BStart(AHEL2 *a2)
    {
    konveier=a2;  

    ty1_tyyp.Start(48, 5); // Algselt ruum 48 kirjele. Kui puudu tuleb, lisab 5 kaupa
    /*01*/ ty1_tyyp.AddPtr(new TY1TYYP('A', &lopp_0,  &suva_vrm, FSxSTR(""),        7, 22));// 0 A lyhenenud tyvi (ilma -ne loputa)
    /*02*/ ty1_tyyp.AddPtr(new TY1TYYP('A', &lopp_0,  &suva_vrm, FSxSTR(""),       11, 10));// 1 ka'a'ndumatu A ?
    /*03*/ ty1_tyyp.AddPtr(new TY1TYYP('A', &lopp_0,  &sg_n,     FSxSTR(""),        2, 11));// 2 lik-lopuline A
    /*04*/ ty1_tyyp.AddPtr(new TY1TYYP('A', &lopp_0,  &sg_n,     FSxSTR(""),        3, 12));// 3 ne, ke -lopuline A
    /*05*/ ty1_tyyp.AddPtr(new TY1TYYP('A', &lopp_0,  &sg_n,     FSxSTR(""),        4, 13));// 4 pole lopus ei lik, ne ega ke ega atav
    /*06*/ ty1_tyyp.AddPtr(new TY1TYYP('A', &lopp_0,  &sg_g,     FSxSTR(""),        5, 14));// 5 se, iku -lopuline A
    /*07*/ ty1_tyyp.AddPtr(new TY1TYYP('A', &lopp_0,  &sg_g,     FSxSTR(""),        6, 15));// 6 pole lopus ei se ega iku ega atava
    /*08*/ ty1_tyyp.AddPtr(new TY1TYYP('B', &lopp_0,  &sg_n,     FSxSTR(""),        0, 16));// 7
    /*09*/ ty1_tyyp.AddPtr(new TY1TYYP('B', &lopp_0,  &sg_g,     FSxSTR(""),        0, 17));// 8
    /*10*/ ty1_tyyp.AddPtr(new TY1TYYP('C', &lopp_0,  &sg_n,     FSxSTR(""),        0, 18));// 9
    /*11*/ ty1_tyyp.AddPtr(new TY1TYYP('C', &lopp_0,  &sg_g,     FSxSTR(""),        0, 19));// 10
    /*12*/ ty1_tyyp.AddPtr(new TY1TYYP('D', &lopp_0,  &suva_vrm, FSxSTR("ammu"),    0, 29));//11 ammu
    /*13*/ ty1_tyyp.AddPtr(new TY1TYYP('D', &lopp_0,  &suva_vrm, FSxSTR("\x00E4sja"),   0, 29));//12 a'sja
    /*14*/ ty1_tyyp.AddPtr(new TY1TYYP('D', &lopp_0,  &suva_vrm, FSxSTR("v\x00F5istu"), 0, 25));//13 vo~istu
    /*15*/ ty1_tyyp.AddPtr(new TY1TYYP('D', &lopp_0,  &suva_vrm, FSxSTR(""),        1, 25));//14 ajuti; v�gisi ...
    /*16*/ ty1_tyyp.AddPtr(new TY1TYYP('G', &suva_lp, &suva_vrm, FSxSTR(""),       15, 28));//15 vahe_mere jms 
    /*17*/ ty1_tyyp.AddPtr(new TY1TYYP('G', &suva_lp, &suva_vrm, FSxSTR(""),        0, 27));//16 ladina
    /*18*/ ty1_tyyp.AddPtr(new TY1TYYP('I', &suva_lp, &suva_vrm, FSxSTR(""),       10, 25));//17 ladina
    /*19*/ ty1_tyyp.AddPtr(new TY1TYYP('N', &lopp_0,  &sg_n,     FSxSTR(""),        0, 23));//18
    /*20*/ ty1_tyyp.AddPtr(new TY1TYYP('N', &lopp_0,  &sg_g,     FSxSTR(""),        0, 24));//19
    /*21*/ ty1_tyyp.AddPtr(new TY1TYYP('O', &lopp_0,  &sg_g,     FSxSTR(""),        0, 24));//20
    /*22*/ ty1_tyyp.AddPtr(new TY1TYYP('P', &lopp_0,  &sg_g,     FSxSTR(""),        8, 24));//21 enese enda kelle mille tolle minu sinu tema endi
    /*23*/ ty1_tyyp.AddPtr(new TY1TYYP('P', &lopp_0,  &pl_g,     FSxSTR(""),        8, 24));//22 meie teie
    /*24*/ ty1_tyyp.AddPtr(new TY1TYYP('P', &suva_lp, &suva_vrm, FSxSTR(""),        0, L_TYVE_TYYP));//23 nen+de puhuks; vajalik ty1+lp+ty2 jaoks
    /*25*/ ty1_tyyp.AddPtr(new TY1TYYP('S', &lopp_0,  &sg_n,     FSxSTR("likkus"),  0,  1));//24 ohtlikkus
    /*26*/ ty1_tyyp.AddPtr(new TY1TYYP('S', &lopp_0,  &sg_n,     FSxSTR("sus"),    13,  2));//25 elastsus
    /*27*/ ty1_tyyp.AddPtr(new TY1TYYP('S', &lopp_0,  &sg_n,     FSxSTR("us"),     16, 30));//26 S [rtpsdgjklvbnm]us teavitus
    /*28*/ ty1_tyyp.AddPtr(new TY1TYYP('S', &lopp_0,  &sg_n,     FSxSTR("ja"),     12,  3));//27 l�psja
    /*28*/ ty1_tyyp.AddPtr(new TY1TYYP('S', &lopp_0,  &sg_n,     FSxSTR(""),       17,  4));//28 ma'gi
    /*30*/ ty1_tyyp.AddPtr(new TY1TYYP('S', &lopp_0,  &sg_g,     FSxSTR("likkuse"), 0,  5));//29 ohtlikkuse
    /*31*/ ty1_tyyp.AddPtr(new TY1TYYP('S', &lopp_0,  &sg_g,     FSxSTR("suse"),   13,  6));//30 elastsuse
    /*32*/ ty1_tyyp.AddPtr(new TY1TYYP('S', &lopp_0,  &sg_g,     FSxSTR("use"),    16, 31));//31 S [rtpsdgjklvbnm]use teavituse
    /*33*/ ty1_tyyp.AddPtr(new TY1TYYP('S', &lopp_0,  &sg_g,     FSxSTR(""),       18,  7));//32 ma'e
    /*34*/ ty1_tyyp.AddPtr(new TY1TYYP('S', &lopp_0,  &sg_p,     FSxSTR(""),        0,  8));//33 ma'ge
    /*35*/ ty1_tyyp.AddPtr(new TY1TYYP('S', &lopp_0,  &adt,      FSxSTR(""),        0,  9));//34 ma'kke
    /*36*/ ty1_tyyp.AddPtr(new TY1TYYP('S', &lopp_0,  &pl_g,     FSxSTR(""),        0,  7));//35 jalge rinde silme
    /*37*/ ty1_tyyp.AddPtr(new TY1TYYP('S', &lopp_d,  &pl_n,     FSxSTR(""),       14,  7));//36 jo~ulu + d
    /*38*/ ty1_tyyp.AddPtr(new TY1TYYP('S', &lopp_t,  &sg_p,     FSxSTR("mis"),     0, 26));//37 lyhenenud tyvi; tyve lopus s ?? 
    /*39*/ ty1_tyyp.AddPtr(new TY1TYYP('S', &lopp_t,  &sg_p,     FSxSTR("lis"),     0, 26));//38 lyhenenud tyvi; tyve lopus s ??
    /*40*/ ty1_tyyp.AddPtr(new TY1TYYP('S', &lopp_t,  &sg_p,     FSxSTR("las"),     0,  2));//39 lyhenenud tyvi; tyve lopus s ??
    /*41*/ ty1_tyyp.AddPtr(new TY1TYYP('S', &suva_lp, &suva_vrm, FSxSTR(""),        0, L_TYVE_TYYP));//40 S + mistahes; vajalik ty1+lp+ty2 jaoks
    /*42*/ ty1_tyyp.AddPtr(new TY1TYYP('U', &lopp_0,  &sg_n,     FSxSTR(""),        0, 20));//41
    /*43*/ ty1_tyyp.AddPtr(new TY1TYYP('U', &lopp_0,  &sg_g,     FSxSTR(""),        0, 21));//42
    /*44*/ ty1_tyyp.AddPtr(new TY1TYYP('V', &lopp_ma, &ma,       FSxSTR(""),        0, L_TYVE_TYYP+1));//43 V + ma
    /*45*/ ty1_tyyp.AddPtr(new TY1TYYP('V', &lopp_da, &da,       FSxSTR(""),        0, L_TYVE_TYYP+2));//44 V + da
    /*46*/ ty1_tyyp.AddPtr(new TY1TYYP('V', &lopp_ta, &da,       FSxSTR(""),        0, L_TYVE_TYYP+2));//45 V + da
    /*47*/ ty1_tyyp.AddPtr(new TY1TYYP('V', &lopp_a,  &da,       FSxSTR(""),        0, L_TYVE_TYYP+2));//46 V + da
    /*48*/ ty1_tyyp.AddPtr(new TY1TYYP('X', &suva_lp, &suva_vrm, FSxSTR(""),        0, 25));//47 plehku
    ty1_tyyp.Sort();
    }

/*
* sobivale sonaliigile+lopule voib vastata mitu tyypi
* nt raha+0 (raha - raha) S sg_n = 20; S sg_g = 21; (rahk - raha) S sg_g = 21
*/
int MORF0::juht1(KOMPONENT *tyvi, TYVE_INF *lgrd, int sl_ind, VARIANTIDE_AHEL **sobivad_variandid)
    {
    register int i;
    int k, lll, llnr, ffnr, tingimus;
    char sobiv[SONAL_MAX_PIK];
    FSxCHAR sl[2] = {0, 0};
    KOMPONENT *tyyp, *komp;
    VARIANTIDE_AHEL *sobiv_variant; //ok
    FSXSTRING ty;
    int pik;
    TYVE_INF yksgrupp;
    int cnt, res;
    FSXSTRING vt_tyvi;
    TY1TYYP *t;
    FSXSTRING slsonalk;

    ty = tyvi->k_algus;
    pik = tyvi->k_pikkus;
    if (!pik) // igaks juhuks kontrollin 30.05.2002 HJK
        return ALL_RIGHT;
    slsonalk = (FSxCHAR *)(const FSxCHAR *)*(sonaliik[sl_ind]);
    if (slsonalk.Find(MITTELIITUV_SL)!=-1) // 26.05.2006 HJK et igasugu liitsõnad ei saaks osaleda
        return ALL_RIGHT;
    if (mrfFlags.Chk(MF_EILUBATABU)) // nt soovitaja puhul
        {
        if (slsonalk.Find(TABU_SL)!=-1)
            return ALL_RIGHT;
        }
   for (i=0; i < sonaliik[sl_ind]->GetLength(); i++) /* vt tyve koiki voimalikke sonaliike */
        {
        sl[0] = (*sonaliik[sl_ind])[i];
		// sl stringi ei tohi ts�kli sees muuta.
		// Kui seda teha, on jama k�es.
        for (t=ty1_tyyp.Get(sl); t; t=ty1_tyyp.GetNext(sl))
            {
            yksgrupp = lgrd[i];
            k = ssobivus(&yksgrupp, sl, 1,  
                         *(t->sobiks_lp), sl, *(t->vorm), sobiv, sizeof(sobiv));
            if (!k)
                continue;
            if (*(t->tyvelp))
                {
                if (!TaheHulgad::OnLopus(&(ty), t->tyvelp))
                    continue; // polnud sobiv tyvelp 
                }
            tingimus = 0;
            switch (t->lisakontroll)
                {
                case 0:
                    tingimus = 1;
                    break;
                case 1:
	                if (!lgrd[i].piiriKr6nksud)  /* pole liitsõna */
                        {
                        if (TaheHulgad::OnLopus(&(ty), FSxSTR("i")) && !TaheHulgad::OnAlguses(&ty, FSxSTR("ei")))
                            tingimus = 1;                          // D + (0)
                        }
                    else
                        { /* ??? need on ju ja'relkomponendid, miks siin on ? hjk 10.2001 */
                        if (TaheHulgad::OnLopus(&(ty), FSxSTR("pidi")) || TaheHulgad::OnLopus(&ty, FSxSTR("poole")))
                            tingimus = 1;                          /* D + (0) */
                        }
                    break;
                case 2: /* tyve lopus -lik */
                    if (TaheHulgad::OnLopus(&(ty), FSxSTR("lik")))
                        tingimus = 1;
                    break;
                case 3: /* tyve lopus -ne voi -ke */
                    if (TaheHulgad::OnLopus(&(ty), FSxSTR("ne")) || TaheHulgad::OnLopus(&ty, FSxSTR("ke")))
                        tingimus = 1;
                    break;
                case 4: /* tyve lopus pole -atav -lik -ne -ke */
                    if (TaheHulgad::OnLopus(&(ty), FSxSTR("atav")) || 
                        TaheHulgad::OnLopus(&(ty), FSxSTR("lik")) ||
                        TaheHulgad::OnLopus(&(ty), FSxSTR("ne")) ||
                        TaheHulgad::OnLopus(&(ty), FSxSTR("ke")) )
                            break;
                    tingimus = 1;
                    break;
                case 5: /* tyve lopus -se voi -iku */
                    if (TaheHulgad::OnLopus(&ty, FSxSTR("se")) || 
                        TaheHulgad::OnLopus(&ty, FSxSTR("iku")) )
                        tingimus = 1;
                    break;
                case 6: /* tyve lopus pole -atava -iku -se */
                    if (TaheHulgad::OnLopus(&ty, FSxSTR("atava")) || 
                        TaheHulgad::OnLopus(&ty, FSxSTR("iku")) || 
                        TaheHulgad::OnLopus(&ty, FSxSTR("se")) )
                            break; 
                    tingimus = 1;
                    break;
                case 7: /* tyvel voiks olla ne-lopp, aga pole */
	            if (sobiks_ne(&ty, pik))
                        tingimus = 1;
                    break;
                case 8: /* tyve pikkus 4 v�i 5 */
                    if (pik == 4 || pik == 5)
                        tingimus = 1;
                    break;
                case 10: /* I jaoks */
                    if (!loend.pahad_hyyd.Get((FSxCHAR *)(const FSxCHAR *)ty, pik))
                        tingimus = 1;
                    break;
                case 11: /* ka'a'ndumatu A */
                    for (lll=0; lll < sonaliik[sl_ind]->GetLength(); lll++)
	                {
	                if (sobiv[lll] /*&& sonaliik[sl_ind].sliik[lll] == 'A'*/)
		            {
		            llnr = (groups[GetLgNr(lgrd, lll)].gr_algus << 8) |
				              groups[GetLgNr(lgrd, lll)].gr_lopp;
		            ffnr = fgr[ homo_form * llnr ];
		            if (ffnr)                /* 0-lõpp ja vorm */
		                sobiv[lll] = 0;        /* pole mittekäänduv 'A' */
                            else
                                tingimus = 1;
		            }
	                }
                      /* chk4 kontrollis seda tingimust...*/
                    if (TaheHulgad::OnLopus(&ty, FSxSTR("ma")) ||
                        TaheHulgad::OnLopus(&ty, FSxSTR("ta")) ||
                        TaheHulgad::OnLopus(&ty, FSxSTR("va")) )
                        tingimus = 0;
                    break;
                case 12:  /* kontr, kas on verbist tuletatud ja-lopuline sona */
	            res = cXXfirst((const FSxCHAR *)ty, ty.GetLength()-2/*pik-pik1*/, &cnt);
	            if (res > ALL_RIGHT)
	                return res; /* viga! */
	            if (res == POLE_YLDSE || res == POLE_SEDA)
                        ; /* ei tee midagi */
                    else
                        {
                        //if (ssobivus(dptr, sonaliik[cnt].sliik, sonaliik[cnt]->GetLength(), lopp_ma, FSxSTR("V"), ma, sobiv))
                        if (ssobivus(dptr, (const FSxCHAR *)(*sonaliik[cnt]), sonaliik[cnt]->GetLength(),
                            lopp_ma, FSxSTR("V"), ma, sobiv, sizeof(sobiv)))
                            tingimus = 1;
                        }
                    break;
                case 13:  /* kontr, kas on omaduss�nast tuletatud sus-lopuline sona */
                    vt_tyvi = ty;
                    vt_tyvi.Delete(vt_tyvi.GetLength()-3);
                    vt_tyvi += FSxSTR("ne");
                    res = cXXfirst(&vt_tyvi, &cnt);
	            if (res > ALL_RIGHT)
	                return res; /* viga! */
	            if (res == POLE_YLDSE || res == POLE_SEDA)
                        ; /* ei tee midagi */
                    else
                        {
                        if (ssobivus(dptr, (const FSxCHAR *)(*(sonaliik[cnt])), sonaliik[cnt]->GetLength(),
                            lopp_0, FSxSTR("A"), sg_n, sobiv, sizeof(sobiv)))
                            tingimus = 1;
                        }
                    break;
                case 14:  /* et v�ltida topelt liitumistyybi m��ramist sg g ja pl n korral*/
                    if (TaheHulgad::OnLopus(&ty, FSxSTR("use")) )/* et v�ltida use-lo'pulisi so'nu (need kuuluvad muudesse tu'u'pidesse)*/
                        {
                        tingimus = 0;
                        break;
                        }
                    tingimus = 1;
                    if (*sobivad_variandid)  /* juba mingi liitumistyyp leitud */
                        {
                        for (sobiv_variant=*sobivad_variandid; sobiv_variant; sobiv_variant=sobiv_variant->jargmine_variant)
                            {
                            komp=esimene_komp(sobiv_variant);
                            if (komp->liitumistyyp == 5 ||
                                komp->liitumistyyp == 6 ||
                                komp->liitumistyyp == 7 )
                                tingimus = 0;  /* on homon. sg g tyvega; seega pole teda vaja */
                            }
                        }
                    break;
                case 15: /* vahe_mere jts liitsonades vabamalt esinevad G */
                    if (on_liitsona(tyvi))
                        tingimus = 1;
                    break;
                case 16:
                    if (ty.GetLength() > 4)
                        {
                        if (TaheHulgad::OnLopus(&ty, FSxSTR("use")))
                            {
                            if (TaheHulgad::OnUs_ees(ty[ty.GetLength()-4]))
                                tingimus = 1;
                            }
                        else if (TaheHulgad::OnLopus(&ty, FSxSTR("us")))
                            {
                            if (TaheHulgad::OnUs_ees(ty[ty.GetLength()-3]))
                                tingimus = 1;
                            }
                        }
                    break;
                case 17: /* et va'ltida us-lopulisi sonu (need kuuluvad muudesse tu'u'pidesse) */
                    tingimus = 1;
                    if (ty.GetLength() > 4)
                        if (TaheHulgad::OnLopus(&ty, FSxSTR("us")))
                            if (TaheHulgad::OnUs_ees(ty[ty.GetLength()-3]))
                                tingimus = 0;
                    break;
                case 18: /* et va'ltida use-lopulisi sonu (need kuuluvad muudesse tu'u'pidesse) */
                    tingimus = 1;
                    if (ty.GetLength() > 4)
                        if (TaheHulgad::OnLopus(&ty, FSxSTR("use")))
                            if (TaheHulgad::OnUs_ees(ty[ty.GetLength()-4]))
                                tingimus = 0;
                    break;

                }
            if (!tingimus)
                continue;
            /* leidsin tyybi */
            /* kopeeri ahel */
            sobiv_variant = lisa_1ahel(sobivad_variandid);
            tyyp = lisa_esimene(sobiv_variant);
            if (!tyyp)
                return CRASH;
            kopeeri_komp(tyyp, tyvi);
            tyyp->liitumistyyp = t->tyyp;
            lisa_ty_info(tyyp, lgrd, sl_ind, i);
            }
        }
    return ALL_RIGHT;
	}

/*
* tyvi2 liitumistyybi ma'a'ramine
* NB! tabelite kirjete jrk on oluline !
*/

/*static  TY2TYYP ty2_tyyp [] =
    {
    {'A', FSxSTR(""), 11, 4},      // ka'a'ndumatu A 
    {'A', FSxSTR("ne"), 0, 5},     // ne lo'puline A 
    {'A', FSxSTR("se"), 0, 5},     // ne lo'puline A 
    {'A', FSxSTR("s"), 12, 5},      // ne lo'puline A 
    {'A', FSxSTR("rohke"), 1, 5},  // "rohke" 
    {'A', FSxSTR("vaba"), 1, 5},   // "vaba" 
    {'A', FSxSTR("rikas"), 1, 5},   // "rikas" 
    {'A', FSxSTR("rikka"), 1, 5},   // "rikas" 
    {'A', FSxSTR(""), 10, 10},      // m�ned vabamalt liituvad A 
    {'A', FSxSTR("ev"), 0, 6},     // v lo'puline A 
    {'A', FSxSTR("va"), 12, 6},     // v lo'puline A 
    {'A', FSxSTR(""), 12, 11},      // tavaline A 
    {'B', FSxSTR(""), 0, 7},
    {'C', FSxSTR(""), 0, 8},
#if defined ( FSCHAR_ASCII )     // kasutame 8bitist (filosofti)kooditabelit
    {'D', FSxSTR("m��da"), 1, 6},   // "mo'o'da" 
#elif defined( FSCHAR_UNICODE )   // kasutame UNICODE kooditabelit
    {'D', FSxSTR("m\x00F6\x00F6\x0064\x0061"), 1, 6},   // "mo'o'da" 
#else
    #error Defineeri  FSCHAR_ASCII v�i FSCHAR_UNICODE
#endif
    {'D', FSxSTR("vargil"), 1, 5},   // "vargil" 
    {'D', FSxSTR("vargile"), 1, 5},   // "vargile" 
    {'G', FSxSTR(""), 0, 2},
    {'K', FSxSTR("pidi"), 1, 6},   // "pidi" 
    {'S', FSxSTR("mine"), 0, 18},   // vrd ka ty2suf_tyyp 
    {'S', FSxSTR("mise"), 0, 18},
    {'S', FSxSTR("mis"), 0, 18},
    {'S', FSxSTR(""), 2, 3},      // SW 
    {'S', FSxSTR(""), 0, 1},
    {'U', FSxSTR(""), 0, 9},
//    {'W', FSxSTR(""), 2, 202},
//    {' ', FSxSTR(""), 0, 0}         // lo'putingimus
    };*/
/*static  TY2SUFTYYP ty2suf_tyyp [] =
    {
    {'A', FSxSTR("rikka"), SUVA_SL, FSxSTR(""), 5},     // rikka=m jms oletaja_tabel.AddPtr(new CFSxOTAB(
    {'A', FSxSTR("vaese"), SUVA_SL, FSxSTR(""), 5},     // vaese=m jms oletaja_tabel.AddPtr(new CFSxOTAB(
    {'A', FSxSTR("rohke"), SUVA_SL, FSxSTR(""), 5},     // rohke=m jms oletaja_tabel.AddPtr(new CFSxOTAB(
    {'A', FSxSTR("vaba"), SUVA_SL, FSxSTR(""), 5},     // vaba=m jms oletaja_tabel.AddPtr(new CFSxOTAB(
    {'A', FSxSTR("va"), SUVA_SL, FSxSTR(""), 19},     // A ty lopus va oletaja_tabel.AddPtr(new CFSxOTAB(
    {'A', FSxSTR("se"), SUVA_SL, FSxSTR(""), 14},     // A ty lopus se oletaja_tabel.AddPtr(new CFSxOTAB(
    {'A', FSxSTR(""), SUVA_SL, FSxSTR(""), 13},     // A ty lopus pole va, se oletaja_tabel.AddPtr(new CFSxOTAB(
    {'B', FSxSTR(""), 'A', FSxSTR(""), 13},
    {'B', FSxSTR(""), 'S', FSxSTR(""), 13},
    {'B', FSxSTR(""), SUVA_SL, FSxSTR(""), 15},
    {'C', FSxSTR(""), 'A', FSxSTR(""), 13},
    {'C', FSxSTR(""), 'S', FSxSTR(""), 13},
    {'C', FSxSTR(""), SUVA_SL, FSxSTR(""), 15},
    {'G', FSxSTR(""), SUVA_SL, FSxSTR(""), 13},
    {'N', FSxSTR(""), 'A', FSxSTR(""), 13},
    {'N', FSxSTR(""), 'S', FSxSTR(""), 13},
    {'N', FSxSTR(""), 'C', FSxSTR(""), 17},
    {'N', FSxSTR(""), 'U', FSxSTR(""), 17},
    {'S', FSxSTR(""), SUVA_SL, FSxSTR(""), 13},
    {'U', FSxSTR(""), SUVA_SL, FSxSTR(""), 15},
    {'U', FSxSTR(""), 'A', FSxSTR(""), 13},
    {'U', FSxSTR(""), 'S', FSxSTR(""), 13},
    {'V', FSxSTR(""), SUVA_SL, FSxSTR("v"), 19},    // v(a) vus(e) jne oletaja_tabel.AddPtr(new CFSxOTAB(
    {'V', FSxSTR(""), SUVA_SL, FSxSTR("tav"), 19},  // tav(a) oletaja_tabel.AddPtr(new CFSxOTAB(
    {'V', FSxSTR(""), SUVA_SL, FSxSTR("dav"), 19},  // dav(a) oletaja_tabel.AddPtr(new CFSxOTAB(
    {'V', FSxSTR(""), SUVA_SL, FSxSTR("mat"), 19},  // mata matu oletaja_tabel.AddPtr(new CFSxOTAB(
    {'V', FSxSTR(""), SUVA_SL, FSxSTR("nu"), 19},   // nu(d) oletaja_tabel.AddPtr(new CFSxOTAB(
    {'V', FSxSTR(""), SUVA_SL, FSxSTR("du"), 20},   // du(d) oletaja_tabel.AddPtr(new CFSxOTAB(
    {'V', FSxSTR(""), SUVA_SL, FSxSTR("tu"), 20},   // tu(d) oletaja_tabel.AddPtr(new CFSxOTAB(
    {'V', FSxSTR(""), SUVA_SL, FSxSTR("mine"), 18},    // ette sobib A(ne), SA SUVA_VRM, V+da oletaja_tabel.AddPtr(new CFSxOTAB(
    {'V', FSxSTR(""), SUVA_SL, FSxSTR("mise"), 18},    // ette sobib A(ne), SA SUVA_VRM, V+da oletaja_tabel.AddPtr(new CFSxOTAB(
    {'V', FSxSTR(""), SUVA_SL, FSxSTR("mis"), 18},    // ette sobib A(ne), SA SUVA_VRM, V+da oletaja_tabel.AddPtr(new CFSxOTAB(
    {'V', FSxSTR(""), SUVA_SL, FSxSTR("ja"), 18},    // ette sobib A(ne), SA SUVA_VRM, V+daoletaja_tabel.AddPtr(new CFSxOTAB(
    {'V', FSxSTR(""), SUVA_SL, FSxSTR("tamatu"), 16},    // ette sobib A(ne), SA SUVA_VRM oletaja_tabel.AddPtr(new CFSxOTAB(
    {'V', FSxSTR(""), SUVA_SL, FSxSTR("us"), 16},    // ette sobib A(ne), SA SUVA_VRM oletaja_tabel.AddPtr(new CFSxOTAB(
    {'V', FSxSTR(""), SUVA_SL, FSxSTR(""), 12},     // V + mitte v tav dav mat nu du tu mine mise mis ja tamatu us; lubab enda ette SA SUVA_VRM oletaja_tabel.AddPtr(new CFSxOTAB(         
//    {' ', FSxSTR(""), SUVA_SL, FSxSTR(""), 0}         // lo'putingimus
    };
// 12 V + mitte v tav dav mat nu du tu mine mise mis ja tamatu us; ette sobib SA SUVA_VRM, ei sobi A(ne) oletaja_tabel.AddPtr(new CFSxOTAB(
// 13 A ty lopus pole va; S; B + AS; C + AS; U + AS; G; N + AS; ette sobib S sg n, sg g, pl n (0-lopuline); A sg n sg g oletaja_tabel.AddPtr(new CFSxOTAB(
// 14 A ty lopus on se; ette sobib S sg n, sg g, pl n (0-lopuline); A sg n sg g; A ka'a'ndumatuoletaja_tabel.AddPtr(new CFSxOTAB(
// 15 BCU+; ette sobib A lik  A sg n oletaja_tabel.AddPtr(new CFSxOTAB(
// 16 V + tamatu, us; ette sobib A(ne), SA SUVA_VRM oletaja_tabel.AddPtr(new CFSxOTAB(
// 17 N + CU; ette sobib lyhenenud tyvi nt kiirus/piirang; ty1ty2s_6 alusel oletaja_tabel.AddPtr(new CFSxOTAB(
// 18 V + mine, ja; ette sobib A(ne), SA SUVA_VRM, V+da oletaja_tabel.AddPtr(new CFSxOTAB(
// 19 A + va; V + v(a) vus(e) tav(a) mata matu nu(d) tu(d) jne; ette sobib SA sg p, adt, V da oletaja_tabel.AddPtr(new CFSxOTAB(
*/
/*extern "C" // m�ned v�rdlusfunktsioonid
    {
    int FSxTY2Bs(const void *ee1, const void *ee2 )// vajalik 2ndotsimiseks
        {
        const FSxCHAR  *e1=(const FSxCHAR *)ee1; 
        const TY2TYYP  *e2=(const TY2TYYP   *)ee2;
        return TaheHulgad::FSxCHCMP( *e1, e2->sl);
        }

    int FSxTY2SUFBs(const void *ee1, const void *ee2 )// vajalik 2ndotsimiseks
        {
        const FSxCHAR  *e1=(const FSxCHAR *)ee1; 
        const TY2SUFTYYP  *e2=(const TY2SUFTYYP   *)ee2;
        return TaheHulgad::FSxCHCMP( *e1, e2->sl);
        }
    }*/

TY2::TY2(void)
    {
    //tyyp.Start(ty2_tyyp, sizeof(ty2_tyyp)/sizeof(TY2TYYP), 0, FSxTY2Bs);    
    tyyp.Start(26,0); // NB! seda ei sordi-peab olema kirjutatud �ige j�rjestusega; kui lisad ridu, siis suurenda ka numbrit 26 !!
    tyyp.AddPtr(new CTY2TYYP('A', FSxSTR(""), 11, 4));      // ka'a'ndumatu A 
    tyyp.AddPtr(new CTY2TYYP('A', FSxSTR("ne"), 0, 5));     // ne lo'puline A 
    tyyp.AddPtr(new CTY2TYYP('A', FSxSTR("se"), 0, 5));     // ne lo'puline A 
    tyyp.AddPtr(new CTY2TYYP('A', FSxSTR("s"), 12, 5));      // ne lo'puline A 
    tyyp.AddPtr(new CTY2TYYP('A', FSxSTR("rohke"), 1, 5));  // "rohke" 
    tyyp.AddPtr(new CTY2TYYP('A', FSxSTR("vaba"), 1, 5));   // "vaba" 
    tyyp.AddPtr(new CTY2TYYP('A', FSxSTR("rikas"), 1, 5));   // "rikas" 
    tyyp.AddPtr(new CTY2TYYP('A', FSxSTR("rikka"), 1, 5));   // "rikas" 
    tyyp.AddPtr(new CTY2TYYP('A', FSxSTR(""), 10, 10));      // m�ned vabamalt liituvad A 
    tyyp.AddPtr(new CTY2TYYP('A', FSxSTR("ev"), 0, 6));     // v lo'puline A 
    tyyp.AddPtr(new CTY2TYYP('A', FSxSTR("va"), 12, 6));     // v lo'puline A 
    tyyp.AddPtr(new CTY2TYYP('A', FSxSTR(""), 12, 11));      // tavaline A 
    tyyp.AddPtr(new CTY2TYYP('B', FSxSTR(""), 0, 7));
    tyyp.AddPtr(new CTY2TYYP('C', FSxSTR(""), 0, 8));
    tyyp.AddPtr(new CTY2TYYP('D', FSxSTR("m\x00F6\x00F6\x0064\x0061"), 1, 6));   // "mo'o'da" 
    tyyp.AddPtr(new CTY2TYYP('D', FSxSTR("vargil"), 1, 5));   // "vargil" 
    tyyp.AddPtr(new CTY2TYYP('D', FSxSTR("vargile"), 1, 5));   // "vargile" 
    tyyp.AddPtr(new CTY2TYYP('G', FSxSTR(""), 0, 2));
    tyyp.AddPtr(new CTY2TYYP('K', FSxSTR("pidi"), 1, 6));   // "pidi" 
    tyyp.AddPtr(new CTY2TYYP('S', FSxSTR("mine"), 0, 18));   // vrd ka ty2suf_tyyp 
    tyyp.AddPtr(new CTY2TYYP('S', FSxSTR("mise"), 0, 18));
    tyyp.AddPtr(new CTY2TYYP('S', FSxSTR("mis"), 0, 18));
    tyyp.AddPtr(new CTY2TYYP('S', FSxSTR(""), 2, 3));      // SW 
    tyyp.AddPtr(new CTY2TYYP('S', FSxSTR(""), 3, 4));      // m�ned S ei liitu sg n-le, nt. "und"
    tyyp.AddPtr(new CTY2TYYP('S', FSxSTR(""), 0, 1));
    tyyp.AddPtr(new CTY2TYYP('U', FSxSTR(""), 0, 9));
//    {'W', FSxSTR(""), 2, 202));
//    {' ', FSxSTR(""), 0, 0}         // lo'putingimus

    //suftyyp.Start(ty2suf_tyyp, sizeof(ty2suf_tyyp)/sizeof(TY2SUFTYYP), 0, FSxTY2SUFBs);  
    suftyyp.Start(36,0); // NB! seda ei sordi-peab olema kirjutatud �uge j�rjestusega
    suftyyp.AddPtr(new CTY2SUFTYYP('A', FSxSTR("rikka"), SUVA_SL, FSxSTR(""), 5));     // rikka=m jms oletaja_tabel.AddPtr(new CFSxOTAB(
    suftyyp.AddPtr(new CTY2SUFTYYP('A', FSxSTR("vaese"), SUVA_SL, FSxSTR(""), 5));     // vaese=m jms oletaja_tabel.AddPtr(new CFSxOTAB(
    suftyyp.AddPtr(new CTY2SUFTYYP('A', FSxSTR("rohke"), SUVA_SL, FSxSTR(""), 5));     // rohke=m jms oletaja_tabel.AddPtr(new CFSxOTAB(
    suftyyp.AddPtr(new CTY2SUFTYYP('A', FSxSTR("vaba"), SUVA_SL, FSxSTR(""), 5));     // vaba=m jms oletaja_tabel.AddPtr(new CFSxOTAB(
    suftyyp.AddPtr(new CTY2SUFTYYP('A', FSxSTR("va"), SUVA_SL, FSxSTR(""), 19));     // A ty lopus va oletaja_tabel.AddPtr(new CFSxOTAB(
    suftyyp.AddPtr(new CTY2SUFTYYP('A', FSxSTR("se"), SUVA_SL, FSxSTR(""), 14));     // A ty lopus se oletaja_tabel.AddPtr(new CFSxOTAB(
    suftyyp.AddPtr(new CTY2SUFTYYP('A', FSxSTR(""), SUVA_SL, FSxSTR(""), 13));     // A ty lopus pole va, se oletaja_tabel.AddPtr(new CFSxOTAB(
    suftyyp.AddPtr(new CTY2SUFTYYP('B', FSxSTR(""), 'A', FSxSTR(""), 13));
    suftyyp.AddPtr(new CTY2SUFTYYP('B', FSxSTR(""), 'S', FSxSTR(""), 13));
    suftyyp.AddPtr(new CTY2SUFTYYP('B', FSxSTR(""), SUVA_SL, FSxSTR(""), 15));
    suftyyp.AddPtr(new CTY2SUFTYYP('C', FSxSTR(""), 'A', FSxSTR(""), 13));
    suftyyp.AddPtr(new CTY2SUFTYYP('C', FSxSTR(""), 'S', FSxSTR(""), 13));
    suftyyp.AddPtr(new CTY2SUFTYYP('C', FSxSTR(""), SUVA_SL, FSxSTR(""), 15));
    suftyyp.AddPtr(new CTY2SUFTYYP('G', FSxSTR(""), SUVA_SL, FSxSTR(""), 13));
    suftyyp.AddPtr(new CTY2SUFTYYP('N', FSxSTR(""), 'A', FSxSTR(""), 13));
    suftyyp.AddPtr(new CTY2SUFTYYP('N', FSxSTR(""), 'S', FSxSTR(""), 13));
    suftyyp.AddPtr(new CTY2SUFTYYP('N', FSxSTR(""), 'C', FSxSTR(""), 17));
    suftyyp.AddPtr(new CTY2SUFTYYP('N', FSxSTR(""), 'U', FSxSTR(""), 17));
    suftyyp.AddPtr(new CTY2SUFTYYP('S', FSxSTR(""), SUVA_SL, FSxSTR(""), 13));
    suftyyp.AddPtr(new CTY2SUFTYYP('U', FSxSTR(""), SUVA_SL, FSxSTR(""), 15));
    suftyyp.AddPtr(new CTY2SUFTYYP('U', FSxSTR(""), 'A', FSxSTR(""), 13));
    suftyyp.AddPtr(new CTY2SUFTYYP('U', FSxSTR(""), 'S', FSxSTR(""), 13));
    suftyyp.AddPtr(new CTY2SUFTYYP('V', FSxSTR(""), SUVA_SL, FSxSTR("v"), 19));    // v(a) vus(e) jne oletaja_tabel.AddPtr(new CFSxOTAB(
    suftyyp.AddPtr(new CTY2SUFTYYP('V', FSxSTR(""), SUVA_SL, FSxSTR("tav"), 19));  // tav(a) oletaja_tabel.AddPtr(new CFSxOTAB(
    suftyyp.AddPtr(new CTY2SUFTYYP('V', FSxSTR(""), SUVA_SL, FSxSTR("dav"), 19));  // dav(a) oletaja_tabel.AddPtr(new CFSxOTAB(
    suftyyp.AddPtr(new CTY2SUFTYYP('V', FSxSTR(""), SUVA_SL, FSxSTR("mat"), 19));  // mata matu oletaja_tabel.AddPtr(new CFSxOTAB(
    suftyyp.AddPtr(new CTY2SUFTYYP('V', FSxSTR(""), SUVA_SL, FSxSTR("nu"), 19));   // nu(d) oletaja_tabel.AddPtr(new CFSxOTAB(
    suftyyp.AddPtr(new CTY2SUFTYYP('V', FSxSTR(""), SUVA_SL, FSxSTR("du"), 20));   // du(d) oletaja_tabel.AddPtr(new CFSxOTAB(
    suftyyp.AddPtr(new CTY2SUFTYYP('V', FSxSTR(""), SUVA_SL, FSxSTR("tu"), 20));   // tu(d) oletaja_tabel.AddPtr(new CFSxOTAB(
    suftyyp.AddPtr(new CTY2SUFTYYP('V', FSxSTR(""), SUVA_SL, FSxSTR("mine"), 18));    // ette sobib A(ne), SA SUVA_VRM, V+da oletaja_tabel.AddPtr(new CFSxOTAB(
    suftyyp.AddPtr(new CTY2SUFTYYP('V', FSxSTR(""), SUVA_SL, FSxSTR("mise"), 18));    // ette sobib A(ne), SA SUVA_VRM, V+da oletaja_tabel.AddPtr(new CFSxOTAB(
    suftyyp.AddPtr(new CTY2SUFTYYP('V', FSxSTR(""), SUVA_SL, FSxSTR("mis"), 18));    // ette sobib A(ne), SA SUVA_VRM, V+da oletaja_tabel.AddPtr(new CFSxOTAB(
    suftyyp.AddPtr(new CTY2SUFTYYP('V', FSxSTR(""), SUVA_SL, FSxSTR("ja"), 18));    // ette sobib A(ne), SA SUVA_VRM, V+daoletaja_tabel.AddPtr(new CFSxOTAB(
    suftyyp.AddPtr(new CTY2SUFTYYP('V', FSxSTR(""), SUVA_SL, FSxSTR("tamatu"), 16));    // ette sobib A(ne), SA SUVA_VRM oletaja_tabel.AddPtr(new CFSxOTAB(
    suftyyp.AddPtr(new CTY2SUFTYYP('V', FSxSTR(""), SUVA_SL, FSxSTR("us"), 16));    // ette sobib A(ne), SA SUVA_VRM oletaja_tabel.AddPtr(new CFSxOTAB(
    suftyyp.AddPtr(new CTY2SUFTYYP('V', FSxSTR(""), SUVA_SL, FSxSTR(""), 12));     // V + mitte v tav dav mat nu du tu mine mise mis ja tamatu us; lubab enda ette SA SUVA_VRM oletaja_tabel.AddPtr(new CFSxOTAB(         
//  {' ', FSxSTR(""), SUVA_SL, FSxSTR(""), 0}         // lo'putingimus
// 12 V + mitte v tav dav mat nu du tu mine mise mis ja tamatu us; ette sobib SA SUVA_VRM, ei sobi A(ne) oletaja_tabel.AddPtr(new CFSxOTAB(
// 13 A ty lopus pole va; S; B + AS; C + AS; U + AS; G; N + AS; ette sobib S sg n, sg g, pl n (0-lopuline); A sg n sg g oletaja_tabel.AddPtr(new CFSxOTAB(
// 14 A ty lopus on se; ette sobib S sg n, sg g, pl n (0-lopuline); A sg n sg g; A ka'a'ndumatuoletaja_tabel.AddPtr(new CFSxOTAB(
// 15 BCU+; ette sobib A lik  A sg n oletaja_tabel.AddPtr(new CFSxOTAB(
// 16 V + tamatu, us; ette sobib A(ne), SA SUVA_VRM oletaja_tabel.AddPtr(new CFSxOTAB(
// 17 N + CU; ette sobib lyhenenud tyvi nt kiirus/piirang; ty1ty2s_6 alusel oletaja_tabel.AddPtr(new CFSxOTAB(
// 18 V + mine, ja; ette sobib A(ne), SA SUVA_VRM, V+da oletaja_tabel.AddPtr(new CFSxOTAB(
// 19 A + va; V + v(a) vus(e) tav(a) mata matu nu(d) tu(d) jne; ette sobib SA sg p, adt, V da oletaja_tabel.AddPtr(new CFSxOTAB(
    //suftyyp.Sort(); // NB! seda ei sordi-peab olema kirjutatud �uge j�rjestusega
    }


int MORF0::juht2(KOMPONENT *tyvi)
    {
//    int j;
    int tingimus;
    KOMPONENT *lopp;
    CTY2TYYP *t;
    CTY2SUFTYYP *st;

    tyvi->liitumistyyp = 0;  /* igaks juhuks */
    lopp = tyvi->komp_jargmine;
    if (!lopp)
        return 0; /* vo'imatu olukord */
    if ((tyvi->liitumisinfo).Find(MITTELIITUV_SL) != -1) // HJK 26.05.2006 et igasugu liits�nad ei saaks osaleda
        return 0;
    if ((tyvi->liitumisinfo).Find(L_MITTELIITUV_SL) != -1) // HJK 6.06.2006 et igasugu l�his�nad ei saaks osaleda
        return 0;
    if (lopp->k_tyyp == K_LOPP) /* ty + lp */
        {
        for (t=ty2.tyyp.Get((FSxCHAR *)(const FSxCHAR *)(tyvi->sl)); t; t=ty2.tyyp.GetNext())
            {
            if (!TaheHulgad::OnLopus(&(tyvi->k_algus), t->tyvelp))
                continue;  /* tyvelp ei sobinud */
            tingimus = 0;
            switch (t->lisakontroll)
                {
                case 0:
                    tingimus = 1;
                    break;
                case 1:
                    if (tyvi->k_algus == t->tyvelp)
                        tingimus = 1;
                    break;
                case 2: // SW, aga mitte "olev"   
                    if ((tyvi->liitumisinfo).Find(W_SL) != -1 && (tyvi->algvorm != FSxSTR("olev")))
                        tingimus = 1;
                    break;
                case 3: // juuni 2006 HJK 
                    if (tyvi->algvorm == FSxSTR("uni") || //"uni, und" ei saa liituda S sg n-ga, vaid v�hematega (on selle poolest nagu k��ndumatu A)   
                        tyvi->k_algus == FSxSTR("iste"))  // et vältida Palm_iste jms
                        tingimus = 1;
                    break;
                case 10: /* m�ned lik ja matu-lopulised sonad */
                    if (loend.head_om.Get((FSxCHAR *)(const FSxCHAR *)(tyvi->k_algus)))
/*
                    if (!strncmp(tyvi->k_algus, "k�lblik", 7) ||
                        !strncmp(tyvi->k_algus, "ohtlik", 6) ||
                        !strncmp(tyvi->k_algus, "tundlik", 7) ||
                        !strncmp(tyvi->k_algus, "suutlik", 7) ||
                        !strncmp(tyvi->k_algus, "k�lbmatu", 8) ||
                        !strncmp(tyvi->k_algus, "suutmatu", 8) ||
                        !strncmp(tyvi->k_algus, "andeka", 6) ||
                        !strncmp(tyvi->k_algus, "n�udlik", 7) ||
                        !strncmp(tyvi->k_algus, "v�imeka", 7) ||
                        !strncmp(tyvi->k_algus, "osav", 4) ||
                        !strncmp(tyvi->k_algus, "tihe", 4) )
*/
                        tingimus = 1;
                    break;
                case 11: /* ka'a'ndumatu A */
                    if (on_muutumatu(tyvi))
                        {
                    if (loend.head_om.Get((FSxCHAR *)(const FSxCHAR *)(tyvi->k_algus)))
/*
                        if (tyvi->k_pikkus == 5)
                            {
                            if (!strcmp(tyvi->k_algus, "karva") || 
                                !strcmp(tyvi->k_algus, "kasvu") ||
                                !strcmp(tyvi->k_algus, "moodi") ||
                                !strcmp(tyvi->k_algus, "v�rvi") ||
                                !strcmp(tyvi->k_algus, "v��rt") )
                                tingimus = 1;
                            }
                        else if (tyvi->k_pikkus == 6 && !strcmp(tyvi->k_algus, "korras") )
*/
                            tingimus = 1;
                        }
                    break;
                case 12: /* ka'a'nduv A */
                    if (!on_muutumatu(tyvi))
                        tingimus = 1;
                    break;
                }
            if (!tingimus)
                continue;
            /* leidsin tyybi */
            tyvi->liitumistyyp = t->tyyp;
            return tyvi->liitumistyyp;
            }
        }
    if (lopp->k_tyyp == K_SUFF) /* ty + suf */
        {
        for (st=ty2.suftyyp.Get((FSxCHAR *)(const FSxCHAR *)(tyvi->sl)); st; st=ty2.suftyyp.GetNext())
            {
            if (!TaheHulgad::OnLopus(&(tyvi->k_algus), st->tyvelp))
                continue;  /* tyvelp ei sobinud */
            if (st->sufsl != SUVA_SL)
                if (st->sufsl != lopp->sl[0])
                    continue;  /* sufiksi sonaliik ei sobinud */
            if (!TaheHulgad::OnAlguses(&(lopp->k_algus), st->suf))
                continue;  /* sufiksi algus ei sobinud */
            /* leidsin tyybi */
            tyvi->liitumistyyp = st->tyyp;
            return tyvi->liitumistyyp;
            }
        }
    return 0;
    }
/*
* ty1 + ty2 lubavate kombinatsioonide tabel
*/
#define TY1_TYYPE 43
#define TY2_TYYPE 20

static  char ty1ty2s[TY1_TYYPE + 1][TY2_TYYPE + 1] =
    /* 0     1     2     3     4     5     6     7     8     9    10    11    12    13    14    15    16    17    18    19      20*/
    {/*0     S     G    SW     A    Ane   Av     B     C     U     A     A    V+  AS;+AS Ase+  BCU+   V+  N+CU V+mine  A+va; V+ V+[dt]u */
    {  0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0},
    /* 1     S+likkus */
    {  0,    0,    0,   80,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0},
    /* 2     S+sus */
    {  0,   90,    0,   90,   80,   80,    0,    0,    0,    0,   80,   80,    0,    0,    0,    0,   80,    0,   80,    0,    0},
    /* 3     S+ja */
    {  0,   80,    0,   80,   80,   80,    0,    0,    0,    0,    0,   80,    0,    0,    0,    0,   80,    0,   80,    0,    0},
    /* 4     S nom   ma'gi */
    {  0,   80,    0,   80,    0,   70,    0,   80,    0,    0,    0,   80,   80,   80,   80,   80,   80,    0,   80,    0,    0},
    /* 5     S + likkuse */
    {  0,   90,   90,   90,   90,   90,    0,   90,    0,    0,    0,   90,   90,   90,   90,   90,   90,    0,   90,    0,    0},
    /* 6     S + suse */
    {  0,   90,   90,   90,   90,   90,    0,   90,    0,    0,    0,   90,   90,   90,   90,   90,   90,    0,   90,    0,    0},
    /* 7     S gen   ma'e jalge rinde silme jo~ulu + d*/
    {  0,   90,   90,   90,   90,   90,    0,   90,    0,    0,   90,   90,   90,   90,   90,   90,   90,    0,   90,    0,    0},
    /* 8     S part  ma'ge */
    {  0,    0,    0,    0,    0,    0,   90,    0,    0,    0,    0,   0,   90,    0,    0,    0,    0,    0,    0,   90,   90},
    /* 9     S adt   ma'kke */
    {  0,    0,    0,   90,    0,    0,   90,    0,    0,    0,    0,   0,   90,    0,    0,    0,   90,    0,   90,   90,   90},
    /* 10     ka'a'ndumatu A ?*/
    {  0,    0,    0,   60,    0,   60,    0,    0,    0,    0,    0,   0,    0,   60,   60,    0,    0,    0,    0,    0,    0},
    /* 11     lik-lopuline A */
    {  0,    0,    0,    0,    0,   90,    0,    0,    0,    0,    0,   0,    0,    0,   90,    0,    0,    0,    0,    0,    0},
    /* 12     ne, ke -lopuline A ??? ei liitugi ??? */
    {  0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,   0,    0,    0,    0,    0,    0,    0,    0,    0,    0},
    /* 13     A pole lopus lik, ne, ke, atav*/
    {  0,   80,    0,   80,    0,   90,    0,    0,    0,    0,    0,  90,   80,   90,   60,    0,   80,    0,   80,    0,    0},
    /* 14     se, iku -lopuline A */
    {  0,    0,    0,    0,    0,   90,    0,    0,    0,    0,    0,   0,    0,   90,   90,    0,    0,    0,    0,    0,    0},
    /* 15     A pole lopus se, iku, atava*/
    {  0,   90,    0,   90,    0,   90,    0,    0,    0,    0,    0,   0,   90,   90,   90,    0,   90,    0,   90,    0,    0},
    /* 16     B sg n */
    {  0,   80,    0,   80,    0,   80,    0,    0,    0,    0,    0,  90,    0,   80,   80,    0,    0,    0,   90,    0,    0},
    /* 17     B sg g */
    {  0,   90,    0,   90,    0,   90,    0,    0,    0,    0,    0,   0,    0,   90,   90,    0,    0,    0,    0,    0,    0},
    /* 18     C sg n */
    {  0,   60,    0,    0,    0,   60,    0,    0,    0,    0,   60,   0,    0,   60,   60,    0,    0,    0,    0,    0,    0},
    /* 19     C sg g */
    {  0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,   0,    0,   60,    0,    0,    0,    0,    0,    0,    0},
    /* 20     U sg n */
    {  0,   60,    0,    0,    0,   60,    0,    0,    0,    0,    0,   0,    0,   60,   60,    0,    0,    0,    0,    0,    0},
    /* 21     U sg g */
    {  0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,   0,    0,    0,   00,    0,    0,    0,    0,    0,    0},
    /* 22     A lyhenenud tyvi (ilma -ne loputa)*/
    {  0,   90,   90,   90,   90,   90,    0,    0,    0,    0,    0,   0,    0,   90,   90,    0,    0,    0,   90,   90,   90},
    /* 23     N sg n */
    {  0,   90,    0,   90,    0,    0,    0,    0,    0,    0,    0,   0,    0,   90,   90,    0,    0,    0,   90,    0,    0},
    /* 24     P sg g, pl g enese enda kelle mille tolle minu sinu tema endi meie teie; ON sg g */
    {  0,   90,    0,   90,    0,   90,    0,    0,    0,    0,    0,   0,   90,   90,   90,    0,   90,    0,   90,    0,    0},
    /* 25     D ajuti; v�gisi ... X plehku I */
    {  0,    0,    0,   90,    0,    0,   90,    0,    0,    0,    0,   0,   90,    0,    0,    0,   90,    0,   90,   90,   90},
    /* 26     lyhenenud tyvi; tyve lopus s ?? */
    {  0,   90,   90,   90,   90,   90,    0,    0,    0,    0,   90,   0,    0,   90,   90,    0,    0,    0,   90,   90,   90},
    /* 27     G ladina */
    {  0,    0,    0,   90,    0,   90,    0,    0,    0,    0,    0,   0,   90,   90,   90,    0,   90,    0,   90,    0,    0},
    /* 28     G vahe_mere jms */
    {  0,   90,    0,   90,    0,   90,    0,    0,    0,    0,    0,   0,   90,   90,   90,    0,   90,    0,   90,    0,    0},
    /* 29     D ammu */
    {  0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,   0,    0,    0,    0,    0,    0,    0,    0,   90,   90},
    /* 30     S [tdvls]us */
    {  0,   90,    0,   90,    0,   90,    0,    0,    0,    0,   80,  80,   80,   80,   80,   80,   80,    0,   80,    0,    0},
    /* 31     S [tdvls]use */
    {  0,   80,    0,   80,   60,   80,    0,    0,    0,    0,    0,  80,   80,   80,   80,   80,   80,    0,   80,    0,    0},
    {  0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,   0,    0,    0,    0,    0,    0,    0,    0,    0,    0},
    {  0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,   0,    0,    0,    0,    0,    0,    0,    0,    0,    0},
    {  0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,   0,    0,    0,    0,    0,    0,    0,    0,    0,    0},
    {  0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,   0,    0,    0,    0,    0,    0,    0,    0,    0,    0},
    {  0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,   0,    0,    0,    0,    0,    0,    0,    0,    0,    0},
    {  0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,   0,    0,    0,    0,    0,    0,    0,    0,    0,    0},
    {  0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,   0,    0,    0,    0,    0,    0,    0,    0,    0,    0},
    {  0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,   0,    0,    0,    0,    0,    0,    0,    0,    0,    0},
    /* 40     S, P suvaline tyvi */
    {  0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,   0,    0,    0,    0,    0,    0,    0,    0,    0,    0},
    /* 41     V ma */
    {  0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,   0,    0,    0,    0,    0,    0,    0,    0,    0,    0},
    /* 42     V da */
    {  0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,   0,    0,    0,    0,    0,    0,    0,    0,    0,    0}
    };

int MORF0::ty1ty2(int ty1tyyp, int ty2tyyp)
    {
    return (ty1ty2s[ty1tyyp][ty2tyyp]);
    }

/*
* (ty1 + lp) + ty2 lubavate kombinatsioonide tabel
*/
#define TY1_L_TYYPE 9

static  char ty1_l_ty2s[TY1_L_TYYPE+1][TY2_TYYPE+1] =
    /* 0     1     2     3     4     5     6     7     8     9     10   11    12    13    14    15    16    17    18    19     20 */
    {/*0     S     G    SW     A    Ane   Av     B     C     U     A      A    V+  AS;+AS Ase+  BCU+   V+  N+CU V+mine A+va;V+ V+[dt]u */
    {  0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0},
    /* 41     V ma */
    {  0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0},
    /* 42     V da */
    {  0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0},
    /* 43     S pl g ; nen+de */
    {  0,   80,    0,   90,   80,   90,    0,    0,    0,    0,    0,    0,    0,   80,    0,    0,    0,    0,   90,    0,    0},
    /* 44     S part */
    {  0,    0,    0,    0,    0,    0,   90,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,   90,   90},
    /* 45     S adt */
    {  0,    0,    0,   90,    0,    0,   90,    0,    0,    0,    0,    0,    0,    0,    0,    0,   90,    0,   90,   90,   90},
    /* 46     S obliikva */
    {  0,    0,    0,   90,    0,    0,   90,    0,    0,    0,    0,    0,    0,    0,    0,    0,   90,    0,   90,   90,   90},
    /* 47     V ma, mata */
    {  0,    0,    0,   90,    0,    0,   90,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,   90,   90,   90},
    /* 48     V da */
    {  0,    0,    0,    0,    0,    0,   90,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,   90,   90,   90},
    /* 49      */
    {  0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0}
    };

int MORF0::ty1_l_ty2(int ty1tyyp, int ty2tyyp)
    {
    return (ty1_l_ty2s[ty1tyyp-L_TYVE_TYYP][ty2tyyp]);
    }

int MORF0::tyvi1tyvi2(VARIANTIDE_AHEL **ty1_variandid, VARIANTIDE_AHEL **ty2_variandid, VARIANTIDE_AHEL **sobivad_variandid)
    {
    VARIANTIDE_AHEL *tmp1, *tmp2, *tmp2_jargmine, *sobiv_variant, *vahe_variant=0;
    CVARIANTIDE_AHEL cvahe_variandid;
    KOMPONENT *tyvi1, *tyvi2;
    int  l, l1, maxl=0;
    FSXSTRING vt_tyvi;

    for (tmp2=*ty2_variandid; tmp2; ) /* vt tyvi2 tyype */
        {
        tmp2_jargmine = tmp2->jargmine_variant;
        tyvi2 = esimene_komp(tmp2);
        l = 0;
        for (tmp1=*ty1_variandid; tmp1; tmp1=tmp1->jargmine_variant) /* vt ty1 tyype */
            {
            for (tyvi1 = esimene_komp(tmp1); tyvi1->komp_jargmine; tyvi1=tyvi1->komp_jargmine); /* loeb viimase komponendi tyyp*/
            vt_tyvi = tyvi1->k_algus;
            vt_tyvi += tyvi2->k_algus;
            if (viletsls(&vt_tyvi)) /* lubamatu liits�na, nt kapi_laar */
                continue;
            if (tyvi1->liitumistyyp < L_TYVE_TYYP)     /* ty1+ty2 */
                l1 = ty1ty2(tyvi1->liitumistyyp, tyvi2->liitumistyyp);
            else 
                {/* ty1+lp+ty2 */
                l1 = ty1_l_ty2(tyvi1->liitumistyyp, tyvi2->liitumistyyp);
                /* V+da puhul tohib ty2 olla ainult saa */
                if (tyvi1->liitumistyyp == L_TYVE_TYYP+8)  /* V+da*/
                    if (tyvi2->liitumistyyp == 17 || tyvi2->liitumistyyp == 18)  /* V+mine, A+v */
                        if (!TaheHulgad::OnLopus(&(tyvi2->k_algus), FSxSTR("saa")))
                            l1 = 0;
                }
            if (l1 <= l)  /* see ty1 variant ei sobi ty2-ga kokku paremini kui mo'ni eelmine */
                continue;
            if (l1 < maxl)  /* see ty1 variant sobib selle ty2-ga halvemini kui mo'ni eelmine ty1 mo'ne eelmise ty2-ga*/
                continue;
            /* viletsamad eemaldada; parim ahelasse */
            l = l1;
            ahelad_vabaks(&cvahe_variandid.ptr);
            vahe_variant = lisa_ahel(&cvahe_variandid.ptr, tmp1);
            if (!vahe_variant)
                return CRASH;
            if (tyvi2->sl[0] == (FSxCHAR)'K' && tyvi2->k_tyyp == K_TYVI)  /* pidi juhuks */
                if (tyvi2->k_algus == FSxSTR("pidi"))
                    tyvi2->sl[0] = (FSxCHAR)'D';
            kopeeri_ahel(vahe_variant, tmp2);
            }
        if (l)  /* midagi sobis */
            {
            sobiv_variant = lisa_ahel(sobivad_variandid, vahe_variant);
            if (!sobiv_variant)
                return CRASH;
            ahelad_vabaks(&cvahe_variandid.ptr);
            if (l > maxl)
                maxl = l;
            }
        tmp2 = tmp2_jargmine;
        }
    return(maxl);
    }

int MORF0::liitsona(
    VARIANTIDE_AHEL **ty1_ahelad, 
    KOMPONENT *ty2, 
    FSXSTRING *S6na, 
    int eel_pik, 
    VARIANTIDE_AHEL **sobivad_variandid, 
    char *paha_koht,
    const int paha_koha_suurus)
    {
    CVARIANTIDE_AHEL ctyvi2_variant;
    KOMPONENT *viimane, *eelviimane;
    int res;

    lisa_min_info(ty2, S6na, ty2->nihe+eel_pik, ty2->k_pikkus-eel_pik); /* tyvele uus pikkus (*) */
    res = ty2jne(ty2, sobivad_variandid, &ctyvi2_variant.ptr, paha_koht,paha_koha_suurus);
	if (res > ALL_RIGHT)
        {
	    return res; /* viga! */
        }
    /* v�ldime tegelikult juba leitud variantide uuesti leidmist */
    for (VARIANTIDE_AHEL *tmp=ctyvi2_variant.ptr; tmp; tmp=tmp->jargmine_variant) 
        {
        for (viimane=esimene_komp(tmp); viimane->komp_jargmine; viimane=viimane->komp_jargmine)
            ;
        eelviimane = viimane->komp_eelmine;
        if (on_tylopuga(*sobivad_variandid, eelviimane, viimane)) /* selle ty/suf+lopuga variant juba olemas */
            {
            ahelad_vabaks(&ctyvi2_variant.ptr);
            lisa_min_info(ty2, S6na, ty2->nihe-eel_pik, ty2->k_pikkus+eel_pik); /* tyvele endine pikkus tagasi; vt (*) */
            return ALL_RIGHT;
            }
        }

    // int tugevus = 
    tyvi1tyvi2(ty1_ahelad, &ctyvi2_variant.ptr, sobivad_variandid);
    /* siin vo'iks kunagi veel kontrollida tugevus va'a'rtust, et mitte liiga kahtlasi lubada ...*/
    ahelad_vabaks(&ctyvi2_variant.ptr);
    lisa_min_info(ty2, S6na, ty2->nihe-eel_pik, ty2->k_pikkus+eel_pik); /* tyvele endine pikkus tagasi; vt (*) */
    return ALL_RIGHT;
    }

/* ty1+ty2+t3 puhuks ty1 ja ty2 sobivuse kirjeldamiseks */
/* teisendustabel ty1 tyybi teisendamiseks ty1+ty2 juhult ty1+ty2+t3 tarvis */ 
static  int ty1_to_ty11[TY1_TYYPE] =
    { 0,  0,  1,  2,  3,  0, 16,  4,  0,  0,
      0,  0,  0,  5,  0,  6,  7,  8,  0,  0,
      0,  0,  9,  0, 10,  0, 11,  0,  0,  0,
      3,  4,  0,  0,  0,  0,  0,  0,  0,  0,
     15, 14,  0 };

int MORF0::ty11tyyp(int ty1tyyp)
    {
    //assert(ty1_to_ty11[ty1tyyp] >= 0);
    return (ty1_to_ty11[ty1tyyp]);
    }

#define TY11_TYYPE 17
static  char ty11_ty11[TY11_TYYPE][TY11_TYYPE] =
    {/*   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16 */
    { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
    /*1      2 S sg n sus-l�puline */
    { 0, 60, 60, 80, 90,  0,  0,  0,  0,  0,  0, 80,  0,  0,  0, 80,  0 },
    /*2      3 S sg n/sg g ja-l�puline */
    { 0, 80, 60, 80, 90,  0,  0,  0,  0,  0,  0, 80,  0,  0,  0, 80,  0 },
    /*3      4 S sg n muu */
    { 0, 80, 60, 80, 90, 80, 90, 80, 90, 70,  0, 80,  0,  0,  0, 80,  0 },
    /*4      7 S omastava-tyvi */
    { 0, 90, 90, 90, 90, 90, 90, 90, 90, 90,  0, 90,  0,  0, 80, 80, 80 },
    /*5      13 A sg n; pole lopus ei lik, ne ega ke ega atav */
    { 0, 80, 60, 80, 90, 80,  0,  0, 90, 70,  0, 80,  0,  0,  0, 80,  0 },
    /*6      15 A sg g; pole lopus ei se ega iku ega atava */
    { 0,  0, 60, 80, 80,  0,  0,  0,  0, 60,  0, 60,  0,  0,  0, 70,  0 },
    /*7      16 B sg n */
    { 0, 80, 60, 80, 90, 80,  0,  0, 90, 70,  0, 80,  0,  0,  0, 80,  0 },
    /*8      17 B sg g */
    { 0,  0, 60, 80, 80,  0,  0,  0,  0, 60,  0, 60,  0,  0,  0, 70,  0 },
    /*9      22 A, mis kaotanud (ne) */
    { 0, 80, 80, 90, 90,  0,  0,  0,  0, 60,  0, 80,  0,  0,  0, 80,  0 },
    /*10     24 */ /* N O P enese endi jms */
    { 0, 80, 80,  0, 80,  0,  0,  0,  0,  0,  0, 80,  0,  0, 80, 70,  0 },
    /*11     26 S mis/lis/las-l�puline */
    { 0, 80, 80, 80, 90, 60, 60, 60,  0, 60,  0, 60,  0,  0,  0, 80,  0 },
    /*12     prefiks sobiks S-ga*/
    { 0,  0, 70, 70, 80,  0,  0,  0,  0, 60,  0, 90,  0,  0, 80, 70,  0 },
    /*13     prefiks sobiks V-st tehtud sonadega*/
    { 0, 80, 80,  0,  0,  0,  0,  0,  0,  0,  0, 90,  0,  0, 80,  0,  0 },
    /*14     V-st tehtud sona; temaga sobivad m�ned ty1 */
    { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
    /*15     S mistahes; talle+lp sobivad m�ned ty1 ??? */
    { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
    /*16     S suse-l�puline;  */
    { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 }
    };

int MORF0::ty11ty11(int ty1tyyp, int ty2tyyp)
    {
    return (ty11_ty11[ty1tyyp][ty2tyyp]);
    }

