/*
* proovib arvata pa'risnime
*/
#include "mrf-mrf.h"
#include "post-fsc.h"
// return true, kui v�iks olla eesti ne -> s-l�puline nimi
bool MORF0::eesti_pn_s( FSXSTRING *tyvi, int tyvepikkus)
    {
    FSXSTRING sona;
    SILP s;

    sona = *tyvi;
    sona += FSxSTR("e");
    s.silbita(&sona);
    return(eesti_pn_se(&sona, tyvepikkus+1, &s));
    }

// return true, kui v�iks olla eesti ne -> se-l�puline nimi
bool MORF0::eesti_pn_se( FSXSTRING *tyvi, int tyvepikkus, SILP *s )
    {
    int i;

    if (tyvepikkus < 5)
        return false;
    if (s->silpe() < 3)
        return false;
    if (!TaheHulgad::PoleMuudKui(tyvi, &(TaheHulgad::eesti_taht)))
        return false;
    if (s->silbid[s->silpe()-2]->silp == FSxSTR("u")) // eus, ius
        return false;
    if (TaheHulgad::OnLopus(tyvi, FSxSTR("aise")) && s->silpe() > 2)
        return true;
    if (TaheHulgad::OnTaishaalik((*tyvi)[tyvepikkus-2]))
        {
        i = tyvi->FindOneOf(TaheHulgad::taish);
        ASSERT(i > -1 && i < tyvepikkus-1);
        if (TaheHulgad::OnTaishaalik((*tyvi)[i+1]))
            return true;
        }
    return false;
    }
// return true, kui v�iks olla soome nen -> s-l�puline nimi
bool MORF0::soome_pn_s( FSXSTRING *tyvi, int tyvepikkus)
    {
    FSXSTRING sona;
    SILP s;

    sona = *tyvi;
    sona += FSxSTR("e");
    s.silbita(&sona);
    return(soome_pn_se(&sona, tyvepikkus+1, &s));
    }

// return true, kui v�iks olla soome nen -> se-l�puline nimi
bool MORF0::soome_pn_se( FSXSTRING *tyvi, int tyvepikkus, SILP *s )
    {
    int i;

    if (tyvepikkus < 5)
        return false;
    if (s->silpe() < 3)
        return false;
    if (!TaheHulgad::PoleMuudKui(tyvi, &(TaheHulgad::soome_taht)))
        return false;
    if (s->silbid[s->silpe()-2]->silp == FSxSTR("u")) // eus, ius
        return false;
    if (TaheHulgad::OnLopus(tyvi, FSxSTR("aise")) && s->silpe() > 2)
        return true;
    if (TaheHulgad::OnTaishaalik((*tyvi)[tyvepikkus-3]))
        {
        if (tyvi->Find(FSxSTR("kk")) != -1 ||
            tyvi->Find(FSxSTR("pp")) != -1 ||
            tyvi->Find(FSxSTR("tt")) != -1)
            return true;
        i = tyvi->FindOneOf(TaheHulgad::taish);
        ASSERT(i > -1 && i < tyvepikkus-2);
        if (TaheHulgad::OnTaishaalik((*tyvi)[i+1]))
            return true;
        }
    return false;
    }
// kas s�na sobiks �ldse sg n vormi?
bool MORF0::sobiks_sg_n( FSXSTRING *sona, int sonapikkus, SILP *s)
    {
    FSXSTRING tmp;
    SILP ss;
    const FSxOPAHALP *paha_lp;
    int i;

    ASSERT(s->silpe() > 0);
	s->silbivalted();
    if (TaheHulgad::OnLopus(sona, FSxSTR("neni")))
        {
        tmp = sona->Left(sonapikkus-4);
        tmp += FSxSTR("se");
        ss.silbita(&tmp);
        if (soome_pn_se(&tmp, sonapikkus-2, &ss)) // soome nimi -neni
            return false;
        }
    if (s->silpe() == 1) /* 1-silbiline voib alati sg n olla */
        return true;
    if (s->silpe() > 2)
        if ( TaheHulgad::OnLopus(sona, FSxSTR("ovi")) || TaheHulgad::OnLopus(sona, FSxSTR("evi")))
            return false; // Ivanovi jms ei saa olla algvormiks 
    tmp = s->silbid[s->silpe()-1]->silp;
    paha_lp = oletajaDct.pahad_sg_n_lopud.LGetRec((const FSxCHAR *)tmp);
    if (paha_lp)
        {
        if (s->silpe() - 1 < paha_lp->enne_silpe ) // piisavalt v�he silpe 
            return true;
        if (FSxSTRCMP(paha_lp->tyvelp, FSxSTR("ga"))==0)
            {
            if (TaheHulgad::pn_eeltahed4.Find((*sona)[sonapikkus-3]) == -1)
                return true;
            if (s->silpe() > 2 && FSxSTRCMP(s->silbid[s->silpe()-2]->silp, FSxSTR("ta"))==0)
                return true; // V�ljataga
            if (s->silpe() == 4) // enne 3 silpi ja need koik on lyhikesed, nt. Watanaga, siis sg_n
                { // Wa-ta-na-ga
                for (i=0; i < 3; i++)
					{
                    if (s->silbid[i]->valde > 1)
                        return false;
					}
                return true;
                }
            return false;
            }
        else if (FSxSTRCMP(paha_lp->tyvelp, FSxSTR("le"))==0)
            { 
            if (TaheHulgad::pn_eeltahed4.Find((*sona)[sonapikkus-3]) == -1)
                return true;
            if (s->silpe() == 3) // enne 2 silpi ja 1. on lyhike, siis sg_n
                {
                if (s->silbid[0]->valde != 1)
                    return false;
                else
                    return true;
                }
            return false;
            }
        else if (FSxSTRCMP(paha_lp->tyvelp, FSxSTR("se"))==0)
            {
            if (!TaheHulgad::OnAeiu((*sona)[sonapikkus-3]) &&
                (*sona)[sonapikkus-3] != (FSxCHAR)'s')
                return true; 
            if (sona->FindOneOf(TaheHulgad::tapilised) != -1)
                return true; // sonas tapiline taht 
            if (TaheHulgad::OnLopus(sona, FSxSTR("tse")) || TaheHulgad::OnLopus(sona, FSxSTR("house")))
                return true; // sona l�pus tse v�i house
            return false;
            }
        else if (FSxSTRCMP(paha_lp->tyvelp, FSxSTR("te"))==0) // olgu VVK-se-te voi 5+ silpe
            {
            if (s->silpe() > 5)
                return false; // miks false? ebak�la kommentaariga !
            if (TaheHulgad::OnLopus(sona, FSxSTR("sete")))
                {
                FSXSTRING tmp1;
                tmp1 = sona->Left(sonapikkus-4);
                if (ent_tyvi(&tmp1, sonapikkus-4, s->silpe() - 2))
                    return false; // VVK-sete
                }
            return true;
            }
        else if (FSxSTRCMP(paha_lp->tyvelp, FSxSTR("is"))==0 || 
            FSxSTRCMP(paha_lp->tyvelp, FSxSTR("it"))==0 || 
            FSxSTRCMP(paha_lp->tyvelp, FSxSTR("il"))==0)
            { 
            if (TaheHulgad::OnLopus(sona, FSxSTR("mobil")))
                return true;
            // kui enne on konsonant, siis see pole sg n
            if (TaheHulgad::OnKaashaalik((*sona)[sonapikkus-3]))
                return false;
            else
                return true;
            }
        else if (FSxSTRCMP(paha_lp->tyvelp, FSxSTR("ks"))==0)
            { // kui enne on vokaal, siis see pole sg n
            if (TaheHulgad::OnTaishaalik((*sona)[sonapikkus-3]))
                return false;
            else
                return true;
            }
        else
            return false;
        }
    return true;
    }
// return true, kui t�ve l�pus on ent, aak, ood vms �lipikk silp 
bool MORF0::ent_tyvi(FSXSTRING *tyvi, int tyvepik, int silpe)
    {
    if (silpe < 2 || tyvepik < 5)
        return false;
    if (TaheHulgad::OnKaashaalik((*tyvi)[tyvepik-1]) &&
        TaheHulgad::OnTaishaalik((*tyvi)[tyvepik-2]) &&
        TaheHulgad::OnTaishaalik((*tyvi)[tyvepik-3]))
        return true; // aak
    if (TaheHulgad::OnKaashaalik((*tyvi)[tyvepik-1]) &&
        TaheHulgad::OnKaashaalik((*tyvi)[tyvepik-2]) &&
        TaheHulgad::OnTaishaalik((*tyvi)[tyvepik-3]) &&
        (*tyvi)[tyvepik-1] != (*tyvi)[tyvepik-2])
        return true;  // ent
    return false;
    }
