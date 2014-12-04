
/*
* proovib leida suf+lp kombinatsioone
* algoritm: eraldab s�na l�pust l�ppe ja
*           kontrollib, kas m�ni v�ib olla eesti k s�na l�pp
*           kui v�ib, siis otsib voimalikke sufikseid/ja'relkomponente
*           seejuures kasutab tavaliste s�nade anal��siks m�eldud programme kchk1 ja kchk2
*           otsib ka v�imalikke t�vesid, ehkki see on m�ttetu - nagunii neid pole
*/
#include "mrf-mrf.h"
#include "post-fsc.h"
#include "silp.h"

int MORF0::arvasuf1(VARIANTIDE_AHEL **too_variandid, FSXSTRING *S6na, int S6naPikkus, VARIANTIDE_AHEL **sobivad_variandid)
    {
    int res;
    KOMPONENT *tyvi, *suff, *lopp;
    FSXSTRING tsl, edu_lopp, edu_suff;
    bool edu = false;

    //TV char *paha_koht=NULL;
    //paha_koht = init_hjk_cxx(S6naPikkus, paha_koht);
    //if (!paha_koht)
    //    return CRASH;
    char paha_koht[(STEMLEN+1)*(STEMLEN+1)];
    init_hjk_cxx(S6naPikkus, paha_koht, sizeof(paha_koht));

    res = kchk1(too_variandid, S6na, S6naPikkus, sobivad_variandid, paha_koht, sizeof(paha_koht));    // otsi l�ppe 
    if (res > ALL_RIGHT)
	    return res; 
    if (!(*too_variandid))  // ei saa kuidagi olla eesti k sona 
        {
        //TV close_hjk_cxx(paha_koht);
	    return ALL_RIGHT;
        }
    if (!*sobivad_variandid)
        {
        res = kchk2(too_variandid, sobivad_variandid, paha_koht, sizeof(paha_koht)); // otsi suf
        if (res > ALL_RIGHT)
    	    return res; /* viga! */
        }
    //TV close_hjk_cxx(paha_koht);
    if (*sobivad_variandid)  // seda ei saa olla, aga ikkagi ...
	    return ALL_RIGHT;
    // viskame m�ned ebasobivad too_variandid minema
    for (VARIANTIDE_AHEL *variant=*too_variandid; variant; variant=variant->jargmine_variant)
	    {
        tyvi = esimene_komp(variant);
        suff = tyvi->komp_jargmine;
        if (suff->k_tyyp != K_SUFF)
            continue;
        lopp = suff->komp_jargmine;
        if (lopp->k_tyyp != K_LOPP)
            continue;
        // ongi tyvi+suf+l�pp
        if (tyvi->k_pikkus < 3) 
            continue;         // liiga lyhike tyvi on vale
        // j�tame sobimatud sufiksid v�lja
        tsl = taandliik[ sufix[suff->jrk_nr].tsl ];
        if (tsl.Find((FSxCHAR)'F')==-1) // on j�relkomponent
            {
            if (suff->k_pikkus < 5) 
                continue;         // liiga lyhike suf on vale
            }
        else
            {
            if (edu && lopp->k_algus == edu_lopp   // sellise l�puga versioon on juba edukalt leitud
					&& suff->k_algus != edu_suff)  // ja pole tegu v�ltevaheldusega (nt 'isti isti)
                continue;
            }
        if (oletajaDct.pahad_sufid.Get((FSxCHAR *)(const FSxCHAR *)suff->k_algus))
            {
//            eemalda_1ahel(&variant);
//            variant = variant->eelmine_variant; // sufiksiga variant ei ole kunagi ahelas 1.
            continue;
            }
        if (lopp->k_pikkus == 0)
            {
            if (suff->k_algus == FSxSTR("m") || suff->k_algus == FSxSTR("ma"))
                continue;
            }
        if (suff->k_algus == FSxSTR("ja") && TaheHulgad::OnLopus(&(tyvi->k_algus), FSxSTR("ma"))) // maja
            continue;
        if (lopp->k_pikkus < 2)
            {
            if (suff->k_algus == FSxSTR("va"))
                continue;  // vat, vad la'heks valesti =v+t =v+d ; gla=va
            if (suff->k_algus == FSxSTR("v"))
                if (TaheHulgad::OnTaishaalik(tyvi->k_algus[tyvi->k_pikkus-1]) &&
                    TaheHulgad::OnTaishaalik(tyvi->k_algus[tyvi->k_pikkus-2]))
                    continue; // laivi, laiv, subjektiiv, 
            }
        if (suff->k_algus == FSxSTR("lis") && lopp->k_algus == FSxSTR("t"))
            continue;         // lis+t la'heb sageli valesti line+t
        if (suff->k_algus == FSxSTR("mis") && TaheHulgad::OnLopus(&(tyvi->k_algus), FSxSTR("is")))
            continue;         // puritanismist -> puritanis=mine
        if (TaheHulgad::SuurAlgustaht(&(tyvi->k_algus)))  // vist pa'risnimi
            {
            if (tsl.Find((FSxCHAR)'F')==-1) // on j�relkomponent
                {
                if (tyvi->k_pikkus < 4 && 
                    !TaheHulgad::OnTaishaalik(tyvi->k_algus[tyvi->k_pikkus-1]))
                     continue;        // ebasobiv 1. ots
                }
            else 
                {
                if (!TaheHulgad::OnAlguses(&(suff->k_algus), FSxSTR("mine")) &&
                    !TaheHulgad::OnAlguses(&(suff->k_algus), FSxSTR("mise")))
                    continue;       // muid sufikseid p�risnimele ei luba
                }
            }
        else
            {
            if (tsl.Find((FSxCHAR)'F')!=-1) // pole j�relkomponent
                {
                if (TaheHulgad::OnAlguses(&(suff->k_algus), FSxSTR("mi")) || // mine, mise, mini jms
                    TaheHulgad::OnAlguses(&(suff->k_algus), FSxSTR("ke")) || // ke, kene
                    TaheHulgad::OnAlguses(&(suff->k_algus), FSxSTR("tu")))
                    {
                    SILP s;

                    s.silbita(&(tyvi->k_algus));
                    if (s.silpe() < 2)   // enne sufi 1 silp... 
                        continue; 
                    }
                if (TaheHulgad::OnAlguses(&(suff->k_algus), FSxSTR("mine")) || 
                    TaheHulgad::OnAlguses(&(suff->k_algus), FSxSTR("mise")) || 
                    TaheHulgad::OnAlguses(&(suff->k_algus), FSxSTR("sus")) || 
                    TaheHulgad::OnAlguses(&(suff->k_algus), FSxSTR("lik")) || 
                    TaheHulgad::OnAlguses(&(suff->k_algus), FSxSTR("ist")))
                    {} // enne sufi v�ib olla mistahes t�ht
                else
                    {
                    if (TaheHulgad::OnAlguses(&(suff->k_algus), FSxSTR("lus")) || // HJK 18.05.2004 enne oli suff->k_algus == "lu"
                        TaheHulgad::OnAlguses(&(suff->k_algus), FSxSTR("las")) ||
                        TaheHulgad::OnAlguses(&(suff->k_algus), FSxSTR("dus")) ||  // HJK 07.06.2003
                        TaheHulgad::OnTaishaalik(suff->k_algus[0]))
                        {   // enne sufi olgu kaash��lik
                        if (!TaheHulgad::OnKaashaalik(tyvi->k_algus[tyvi->k_pikkus-1]))
                             continue; // tyvi+suf ei sobi ortogr. p�hjustel
                        }
                    else if (TaheHulgad::OnAlguses(&(suff->k_algus), FSxSTR("da")) || 
                        TaheHulgad::OnAlguses(&(suff->k_algus), FSxSTR("du")))
                        { // enne sufi olgu 'l'
                        if (tyvi->k_algus[tyvi->k_pikkus-1] != (FSxCHAR)'l')
                            continue; // tyvi+suf ei sobi ortogr. p�hjustel
                        }
                    else if (TaheHulgad::OnAlguses(&(suff->k_algus), FSxSTR("nu")))
                        {   // enne sufi olgu aeiul
                        if (!TaheHulgad::OnAeiu(tyvi->k_algus[tyvi->k_pikkus-1]) &&
                            tyvi->k_algus[tyvi->k_pikkus-1] != (FSxCHAR)'l')
                             continue; // tyvi+suf ei sobi ortogr. p�hjustel
                        }
                    else    // sufi algul kaash��lik; enne sufi olgu aeiu                     
                        if (!TaheHulgad::OnAeiu(tyvi->k_algus[tyvi->k_pikkus-1]))
                            continue; // tyvi+suf ei sobi ortogr. p�hjustel
                    }
                }
            }
        // kopeeri too_variant -> sobivad_variandid
        if (suff->sl.GetLength() > 0)
            tyvi->sl = suff->sl;
        else
            tyvi->sl = LIIK_YLDNIMI;
		tyvi->sonastikust = 0;
        //VARIANTIDE_AHEL *sobiv_variant;
        //sobiv_variant = lisa_ahel(sobivad_variandid, variant);
        //if (!sobiv_variant)
        //    return CRASH;
        if(lisa_ahel(sobivad_variandid, variant)==NULL)
            return CRASH;
        edu_lopp = lopp->k_algus;
		edu_suff = suff->k_algus;
        edu = true;
        }
    return ALL_RIGHT;
    }

