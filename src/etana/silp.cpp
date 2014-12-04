
/*
* leiab etteantud stringi silbistruktuuri;
* eeldab, et sona on teisendatud vaiketaheliseks (v.a 1. taht)
*/

#include "silp.h"

//int SILP::silbita(FSXSTRING *S6na, SILBISTR *silbid)
int SILP::silbita(const FSXSTRING *S6na/*, TMPLPTRARRAY<SILBISTR> *silbid*/)
    {
    int sona_algus = 1;
    int i, i1, i2, oli_silp;
    FSXSTRING tmpstr;
    FSXSTRING S6nna = *S6na;
    SILBISTR *yksilp;
    
    i1 = S6nna.ReverseFind(FSxSTR("-"));     // kriipsu eelne jupp ei loe
    i2 = S6nna.ReverseFind(FSxSTR("/"));
    i = i1 > i2 ? i1 : i2;
    if (i != -1)
        S6nna = S6nna.Mid(i+1);

    if (TaheHulgad::OnAlguses(S6na, FSxSTR("Mc")))
        {
        //silbid[silbinr].silp = FSxSTR("Mc");
        //silbinr++;
        if((yksilp=silbid.AddPlaceHolder())==NULL)
            return 0; // liiga palju, ei mahu m�llu
        yksilp->silp=FSxSTR("Mc");
        S6nna = S6nna.Mid(2);
        }
    S6nna.MakeLower();
    while (S6nna.GetLength() > 0)
        {
        sona_algus = 1;
        oli_silp = 0;
        for (i=0 ;; i++) // kuni s�na kestab otsi silbipiiri
            {
            if (TaheHulgad::OnTaishaalik(S6nna[i]) || S6nna[i] == (FSxCHAR)'y')
                {
                if (i > 0) // m�nikord on silbipiir t�ish vahel
                    {
                    if (TaheHulgad::OnTaishaalik(S6nna[i-1]))
                        {
                        if (silbid.idxLast > 0 ) 
                            {     
                            if (S6nna[i-1] == (FSxCHAR)'i' && S6nna[i] == (FSxCHAR)'a') // ia -> i_a
                                {
                                if((yksilp=silbid.AddPlaceHolder())==NULL)
                                    return 0; // liiga palju, ei mahu m�llu
                                yksilp->silp=S6nna.Left(i);
                                S6nna = S6nna.Mid(i);           // tee s�na algusest silbi v�rra l�hemaks
                                break;
                                }
                            if (i < S6nna.GetLength()-1)
                                {     
                                tmpstr = S6nna.Left(i+2);
                                if (on_dift_vahe(&tmpstr))    // eus -> e_us
                                    {   // silbipiir diftongi vahel
                                    if((yksilp=silbid.AddPlaceHolder())==NULL)
                                        return 0; // liiga palju, ei mahu m�llu
                                    yksilp->silp=S6nna.Left(i); // t�sta silp k�rvale                            
                                    S6nna = S6nna.Mid(i);           // tee s�na algusest silbi v�rra l�hemaks
                                    break;
                                    }
                                }
                            if (i < S6nna.GetLength()-2 && S6nna[i-1] != (FSxCHAR)'i')
                                {     // ego_ist
                                tmpstr = S6nna.Mid(i, 3);
                                if (tmpstr == FSxSTR("ist") || tmpstr == FSxSTR("ism"))
                                    {   // silbipiir diftongi vahel
                                    if((yksilp=silbid.AddPlaceHolder())==NULL)
                                        return 0; // liiga palju, ei mahu m�llu
                                    yksilp->silp=S6nna.Left(i); // t�sta silp k�rvale                            
                                    S6nna = S6nna.Mid(i);           // tee s�na algusest silbi v�rra l�hemaks
                                    break;
                                    }
                                }
                            }
                        if (i < S6nna.GetLength()-1 && TaheHulgad::OnTaishaalik(S6nna[i+1]))
                            {
                            if (S6nna[i-1] != S6nna[i] && // spi-oon...
                                S6nna[i+1] == S6nna[i]) 
                                {
                                if((yksilp=silbid.AddPlaceHolder())==NULL)
                                    return 0; // liiga palju, ei mahu m�llu
                                yksilp->silp=S6nna.Left(i);
                                S6nna = S6nna.Mid(i);           // tee s�na algusest silbi v�rra l�hemaks
                                break;
                                }
                            tmpstr = S6nna.Mid(i-1, 3);
                            if (S6nna[i+1] != S6nna[i] && // Vii-o...
                                !on_voorvokjada(&tmpstr)) // Pau-a
                                {
                                if((yksilp=silbid.AddPlaceHolder())==NULL)
                                    return 0; // liiga palju, ei mahu m�llu
                                yksilp->silp=S6nna.Left(i+1);
                                S6nna = S6nna.Mid(i+1);           // tee s�na algusest silbi v�rra l�hemaks
                                break;
                                }
                            }
                        if (silbid.idxLast > 0 ) // mitte eriti kindel reegel
                            {     
                            if (S6nna[i-1] == (FSxCHAR)'e' && S6nna[i] == (FSxCHAR)'o') // eo -> e_o
                                {
                                if((yksilp=silbid.AddPlaceHolder())==NULL)
                                    return 0; // liiga palju, ei mahu m�llu
                                yksilp->silp=S6nna.Left(i);
                                S6nna = S6nna.Mid(i);           // tee s�na algusest silbi v�rra l�hemaks
                                break;
                                }
                            }
                        // tegemata erandid: israeliit, danaoslane, avaus, karaul
                        // toreadoor hevea okean... ideali...
                        }
                    }
                if (oli_silp) // kirjuta vana silp �ra
                    {
                    if((yksilp=silbid.AddPlaceHolder())==NULL)
                        return 0; // liiga palju, ei mahu m�llu
                    yksilp->silp=S6nna.Left(i-1); // t�sta silp k�rvale                            
                    S6nna = S6nna.Mid(i-1);           // tee s�na algusest silbi v�rra l�hemaks
                    break;
                   }
                else
                    {
                    sona_algus = 0;
                    }
                }
            else
                {
                if (!sona_algus)
                    oli_silp = 1;
                }
            if (i == S6nna.GetLength()-1) // see on viimane silp
                {
                if((yksilp=silbid.AddPlaceHolder())==NULL)
                    return 0; // liiga palju, ei mahu m�llu
                yksilp->silp=S6nna; // t�sta silp k�rvale                            
                S6nna = FSxSTR("");           // tee s�na algusest silbi v�rra l�hemaks
                break;
                }
            }
        }
    //i = silbivalted(silbid.idxLast, silbid);
    return(silpe());
    }


int SILP::on_voorvokjada(const FSXSTRING *S6na)
    {
    if (*S6na==FSxSTR("ieu") ||
        *S6na==FSxSTR("iou") ||
        *S6na==FSxSTR("eau") ||
        *S6na==FSxSTR("oui") ||
        *S6na==FSxSTR("oua"))
        return(1);
    return(0);
    }

int SILP::on_dift_vahe(const FSXSTRING *S6na)
    {
    if (TaheHulgad::OnLopus(S6na, FSxSTR("eum")) ||
        TaheHulgad::OnLopus(S6na, FSxSTR("eus")) ||
        TaheHulgad::OnLopus(S6na, FSxSTR("ius")) ||
        TaheHulgad::OnLopus(S6na, FSxSTR("ium")) ||
        (TaheHulgad::OnLopus(S6na, FSxSTR("iel")) && !TaheHulgad::OnLopus(S6na, FSxSTR("fiel"))))
        return(1);
    return(0);
    }

/*
* paneb massiivi silbid silpe iseloomustavad andmed:
* va'lte ja ro'hu
* 1. ja 3. v�lde, kui nad m�rgitakse, siis on nad ka �iged
* 2. v�lde v�ib olla vale, s.t. tegelt peaks tema asemel olema vahel 3. v�lde
*/

void SILP::silbivalted(void)
    {
    int vt_silp = 0;
    int i, sl;

    if (silbid.idxLast == 1) // 1-silbiline on alati 3. v�ltes
        {
        silbid[0]->valde = 3;
        silbid[0]->rohk = 1;
        return;
        }
    if (silbid[0]->silp == FSxSTR("Mc"))
        {
        silbid[0]->valde = 1;
        silbid[0]->rohk = 0;
        vt_silp++;
        }
    for (i=vt_silp; i < silbid.idxLast; i++)
        {
        sl = silbid[i]->silp.GetLength();
        silbid[i]->valde = 2; // vaikimisi va'a'rtus 
        silbid[i]->rohk = 0;  // vaikimisi va'a'rtus 
        if (sl == 1) // ongi ainult 1 ta'ht 
            {
            if (i < silbid.idxLast-1)                     // pole viimane silp ja
                {
                if (!TaheHulgad::OnKpt(silbid[i+1]->silp[0])) // j�rgmise alguses pole kpt
                    silbid[i]->valde = 1;             // l�hike silp; 1. valde
                }
            else
                silbid[i]->valde = 1;             // l�hike silp; 1. valde
            continue;
            }
        if (TaheHulgad::OnTaishaalik( silbid[i]->silp[sl-1])) // silbi l�pus vokaal
            {
            if (TaheHulgad::OnKaashaalik( silbid[i]->silp[sl-2])) // enne seda konsonant
                {
                if (i < silbid.idxLast-1)                      // pole viimane silp ja
                    {
                    if (!TaheHulgad::OnKpt(silbid[i+1]->silp[0])) // j�rgmise alguses pole kpt
                        silbid[i]->valde = 1;         // l�hike silp => 1. v�lde
                    }
                else
                    silbid[i]->valde = 1;         // l�hike silp => 1. v�lde
                continue;
                }
            else            // silbi l�pus 2 vokaali;  pikk silp => 2. v 3. v�lde
                {
                if (TaheHulgad::OnLopus(&(silbid[i]->silp), FSxSTR("io")) || 
                            TaheHulgad::OnLopus(&(silbid[i]->silp), FSxSTR("iu"))) 
                    continue; // erandlik olukord; pole r�huline
                silbid[i]->rohk = 1;
                if (silbid[i]->silp[sl-1] == (FSxCHAR)'a')
                    {
                    if (silbid[i]->silp[sl-2] != (FSxCHAR)'a' &&
                        silbid[i]->silp[sl-2] != (FSxCHAR)'e' )
                        {  // Hint: Va on alati 3. v�ltes, v.a. aa ja ea
                        silbid[i]->valde = 3;
                        continue;
                        }
                    }
                if (i == silbid.idxLast-1) // on viimane silp 
                    { 
                    silbid[i]->valde = 3;    // 3. v�lde
                    continue;
                    }
                else // pole viimane silp
                    {
                    if (TaheHulgad::OnKpt(silbid[i+1]->silp[0])) // j�rgmise silbi alguses kpt
                        { // au_to Ai_ta v�listan sellega, et pole 1. silp
                        if (i > vt_silp) // 2 jne silp; seega 
                            { // valesti l�heks Spo_saa_to, bi_oota
                            silbid[i]->valde = 3;   // 3. v�lde
                            continue;
                            }
                        }
                    if (i < silbid.idxLast-2 )  // silbi taga veel v�hemalt 2 silpi
                        { // kas nende vahel on i_V ?
                        if (TaheHulgad::OnTaishaalik(silbid[i+2]->silp[0]) &&
                            silbid[i+1]->silp[silbid[i+1]->silp.GetLength()-1] == (FSxCHAR)'i')
                            { // naa_li_um
                            silbid[i]->valde = 3;   // 3. v�lde
                            continue;
                            }
                        }
                    }
                }
            }
        else // silbi l�pus konsonant;  pikk silp => 2. v 3. v�lde
            {
            if (i == silbid.idxLast-1) // on viimane silp
                {
                if (TaheHulgad::OnLopus(&(silbid[i]->silp), FSxSTR("ich")))  // Lurich, Kranich
                    {
                    continue; // ei saaks �elda et on 3. v�lde ja r�huline
                    }
                if (silbis_vv(&silbid[i]->silp) != -1)
                    { // _loog
                    silbid[i]->rohk = 1;
                    silbid[i]->valde = 3;  // 3. v�lde
                    continue;
                    }
                if (silbid[i-1]->valde == 1)  // eelneb l�hike silp
                    { // et v�listada kot_let, Tar_mak; aga v�listab ka ab_tiss, so_lip_sist
                    if (TaheHulgad::OnKpt(silbid[i]->silp[sl-1]) && // see on kpt 
                        silbid[i]->silp != FSxSTR("bot"))          // ja pole nt. ro_bot
                        { // _ent _ist
                        silbid[i]->rohk = 1;
                        silbid[i]->valde = 3;  // 3. v�lde
                        continue;
                        }
                    if (TaheHulgad::OnKaashaalik(silbid[i]->silp[sl-2])) // l�pus mitu konsonanti
                        {
                        silbid[i]->rohk = 1;
                        silbid[i]->valde = 3;  // 3. v�lde
                        continue;
                        }
                    }
                }
            else // pole viimane silp
                {
                if (TaheHulgad::OnKpt(silbid[i+1]->silp[0]))  // j�rgmise silbi alguses kpt
                    {
                    if (silbid[i+1]->silp[0] == silbid[i]->silp[sl-1]) // mis == selle silbi viimasega
                        { // nak_ki
                        silbid[i]->rohk = 1;
                        silbid[i]->valde = 3;  // 3. v�lde
                        continue;
                        }
                    }
                if (TaheHulgad::OnLmnr(silbid[i]->silp[sl-1])) // silbi l�pus on lmnr
                    {
                    if (TaheHulgad::gbd.Find(silbid[i+1]->silp[0]))  // j�rgmise silbi alguses gbd
                        {
                        if (silbis_vv(&silbid[i]->silp) != -1)
                            { // loor_du
                            silbid[i]->rohk = 1;
                            silbid[i]->valde = 3;  // 3. v�lde
                            continue;
                            }
                        }
                    }
                if (i < silbid.idxLast-2 )  // silbi taga veel v�hemalt 2 silpi
                    { // kas nende vahel on i_V ?
                    if (TaheHulgad::OnTaishaalik(silbid[i+2]->silp[0]) &&
                        silbid[i+1]->silp[silbid[i+1]->silp.GetLength()-1] == (FSxCHAR)'i')
                        { // nab_ri_um
                        if (silbis_vv(&silbid[i]->silp) != -1)
                            { // naab_ri_um
                            silbid[i]->rohk = 1;
                            silbid[i]->valde = 3;  // 3. v�lde
                            continue;
                            }
                        }
                    }
                }
            }
        }
    // paneme r�hu paika
    // 3-v�ltelised silpidele pandi alati ka r�hk juurde
    for (i=vt_silp; i < silbid.idxLast; i++)
        {
        if (silbid[i]->rohk != 0)  // kuskil juba r�hk olemas
            return;
        }
//  kahtlane reegel...
/*    for (i=vt_silp; i < silbid.idxLast; i++)
        {
        if (silbid[i]->valde == 2)  // pikale silbile
            {
            silbid[i]->rohk = 1;    // r�hk
            return;
            }
        }
*/
    silbid[vt_silp]->rohk = 1;       // esimesele silbile r�hk
    }

// return see koht, kui silbis on kaks k�rvuti vokaali
int SILP::silbis_vv(const FSXSTRING *silp)
    {
    int k;

    k = silp->FindOneOf(TaheHulgad::taish);
    if (k == -1)
        return k;
    if (TaheHulgad::OnTaishaalik((*silp)[k+1])) 
        return (k);
    return -1;
    }
int SILP::viimane_rohuline_silp(void)
    {
    int k;

    for (k=silpe()-1; k >= 0; k--)
        {
        if (silbid[k]->rohk)
            return k;
        }
    assert(k >= 0);
    return -1;
    }

