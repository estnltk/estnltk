
#include "mrf-mrf.h"

// v�ljundiks on tulemuste struktuur, mitte string

// lyli=konveier->Lyli(0,A2_SUVALINE_LYLI,&idx);
// sisse <== lyli->ptr.pStr
// lyli->ptr.pMrfAnal <== tul
//

void MORF0::chkmin(
                   const FSXSTRING *sisse,
                   const FSXSTRING* sissePuhastatud,
                   MRFTULEMUSED *tul,
                   const int maxtasand)
{
    int n, res;

    //z FSXSTRING sona = *sisse;
    FSXSTRING sona = *sissePuhastatud;
    TaheHulgad::AsendaMitu(&sona, TaheHulgad::uni_kriipsud, TaheHulgad::amor_kriipsud);

    tul->tagasiTasand = 0;
    tul->mitmeS6naline = 1;
    tul->keeraYmber = false;
    tul->eKustTulemused = eMRF_AP; // anal��sid p�his�nastikust
    tul->DelAll();

    //printf("%s:%d  ", __FILE__,__LINE__);
    //wprintf(L"%s\n", (const FSWCHAR *)*sisse);
    if (sona.GetLength() >= STEMLEN)
    {
        tul->s6na = *sisse;
        if (mrfFlags.Chk(MF_SPELL) || mrfFlags.Chk(MF_PIKADVALED))
            return;
        else
        {
            tul->Add((const FSxCHAR *) (*sissePuhastatud), FSxSTR(""), FSxSTR(""), FSxSTR("Z"), FSxSTR("")); // parema puudusel
            return;
        }
    }
    if (mrfFlags.ChkB(MF_EITULETALIIT)) // tesaurusest k�simiseks eesk�tt
    {
        res = chkvaljend(tul, &sona); // kas on mitmesonaline v�ljend?
        if (res != ALL_RIGHT)
        {
            tul->s6na = FSxSTR("");
            tul->eKustTulemused = eMRF_XX;
            throw (VEAD(ERR_MG_MOOTOR, ERR_MINGIJAMA, __FILE__, __LINE__, "$Revision: 878 $")); //jama!
        }
        if (!tul->on_tulem()) // polnd v�ljend
        {
            res = chkgeon(tul, &sona, &(tul->mitmeS6naline)); // kas on mitmesonaline geonimi?
            if (res != ALL_RIGHT)
            {
                tul->s6na = FSxSTR("");
                tul->eKustTulemused = eMRF_XX;
                throw (VEAD(ERR_MG_MOOTOR, ERR_MINGIJAMA, __FILE__, __LINE__, "$Revision: 878 $")); //jama!
            }
        }
        if (tul->on_tulem()) // oli v�ljend v�i geonimi
        {
            tul->tagasiTasand = 1; // et oleks samasugune kui morf ja spell jms
        }
        else // kas on �ksiks�nana s�nastikus?
        {
            CVARIANTIDE_AHEL ctoo_variandid, csobivad_variandid;

            tul->mitmeS6naline = 1;
            TaheHulgad::Puhasta(&sona);
            if (sona.GetLength() >= STEMLEN)
            {
                tul->s6na = FSxSTR("");
                tul->eKustTulemused = eMRF_XX;
                throw (VEAD(ERR_MG_MOOTOR, ERR_MINGIJAMA, __FILE__, __LINE__, "$Revision: 878 $")); //jama!
            }
            sona.TrimRight(FSxSTR("."));
            res = kchk1(&ctoo_variandid.ptr, &sona, sona.GetLength(), &csobivad_variandid.ptr, NULL, 0);
            if (res > ALL_RIGHT)
            {
                tul->s6na = FSxSTR("");
                tul->eKustTulemused = eMRF_XX;
                throw (VEAD(ERR_MG_MOOTOR, ERR_MINGIJAMA, __FILE__, __LINE__, "$Revision: 878 $")); //jama!
            }
            if (csobivad_variandid.ptr)
            {
                variandid_tulemuseks(tul, KOIK_LIIGID, &csobivad_variandid.ptr);
            }
            if (TaheHulgad::SuurAlgustaht(&sona)
                || TaheHulgad::AintSuuredjaKriipsud(&sona))
            { // lunastaja ja Lunastaja
                sona.MakeLower();
                ahelad_vabaks(&ctoo_variandid.ptr);
                ahelad_vabaks(&csobivad_variandid.ptr);
                res = kchk1(&ctoo_variandid.ptr, &sona, sona.GetLength(), &csobivad_variandid.ptr, NULL, 0);
                if (res > ALL_RIGHT)
                {
                    tul->s6na = FSxSTR("");
                    tul->eKustTulemused = eMRF_XX;
                    throw (VEAD(ERR_MG_MOOTOR, ERR_MINGIJAMA, __FILE__, __LINE__, "$Revision: 878 $")); //jama!
                }
                if (csobivad_variandid.ptr)
                {
                    variandid_tulemuseks(tul, KOIK_LIIGID, &csobivad_variandid.ptr);
                }
            }
            ahelad_vabaks(&ctoo_variandid.ptr);
            ahelad_vabaks(&csobivad_variandid.ptr);
            if (!tul->on_tulem())
            {
                if (TaheHulgad::OnAlguses(&sona, FSxSTR("-"))) // -poolne
                {
                    sona.TrimLeft(FSxSTR("-"));
                    sona.MakeLower();
                    res = kchk1(&ctoo_variandid.ptr, &sona, sona.GetLength(), &csobivad_variandid.ptr, NULL, 0);
                    if (res > ALL_RIGHT)
                    {
                        tul->s6na = FSxSTR("");
                        tul->eKustTulemused = eMRF_XX;
                        throw (VEAD(ERR_MG_MOOTOR, ERR_MINGIJAMA, __FILE__, __LINE__, "$Revision: 878 $")); //jama!
                    }
                    if (csobivad_variandid.ptr)
                    {
                        variandid_tulemuseks(tul, MITTE_VERB, &csobivad_variandid.ptr);
                        if (tul->on_tulem())
                            tul->LisaTyvedeleEtte(FSxSTR("-"));
                    }
                    ahelad_vabaks(&ctoo_variandid.ptr);
                    ahelad_vabaks(&csobivad_variandid.ptr);
                }
            }
            if (!tul->on_tulem())
                res = chklyh2(tul, &sona); // abc wc puhuks
            if (res > ALL_RIGHT)
            {
                tul->s6na = FSxSTR("");
                tul->eKustTulemused = eMRF_XX;
                throw (VEAD(ERR_MG_MOOTOR, ERR_MINGIJAMA, __FILE__, __LINE__, "$Revision: 878 $")); //jama!
            }
            if (!tul->on_tulem() && sona.GetLength() > 3) // proovime kigi otsast maha v�tta
            {
                FSXSTRING S6na3, ki;
                FSxCHAR enne_ki;

                ki = (const FSxCHAR *) (sona.Right(2));
                enne_ki = sona[sona.GetLength() - 3];
                if ((// on nii, et...
                    (ki == FSxSTR("ki") && TaheHulgad::OnHelitu(enne_ki)) || // enne 'ki' helitu h��lik
                    (ki == FSxSTR("gi") && !TaheHulgad::OnHelitu(enne_ki)) || // enne 'gi' heliline h��lik
                    ((ki == FSxSTR("ki") || ki == FSxSTR("gi")) && (enne_ki == V_SH || enne_ki == V_ZH)) // s'ja z' puhul on lubatud nii gi kui ki
                    ))
                {
                    S6na3 = (const FSxCHAR *) (sona.Mid(0, sona.GetLength() - 2));
                    if ((dctLoend[0])[(FSxCHAR *) (const FSxCHAR *) S6na3] == -1)
                    { // sonale ikka tohib [gk]i otsa panna
                        res = kchk1(&ctoo_variandid.ptr, &S6na3, S6na3.GetLength(), &csobivad_variandid.ptr, NULL, 0); /* ty+lp */
                        if (res > ALL_RIGHT)
                        {
                            tul->s6na = FSxSTR("");
                            tul->eKustTulemused = eMRF_XX;
                            throw (VEAD(ERR_MG_MOOTOR, ERR_MINGIJAMA, __FILE__, __LINE__, "$Revision: 878 $")); //jama!
                        }
                        ahelad_vabaks(&ctoo_variandid.ptr);
                        if (csobivad_variandid.ptr)
                        {
                            variandid_tulemuseks(tul, KI_LIIGID, &csobivad_variandid.ptr);
                            if (tul->on_tulem())
                                tul->LisaLoppudeleTaha((const FSxCHAR *) ki);
                            ahelad_vabaks(&csobivad_variandid.ptr);
                        }
                    }
                }
            }
        }
    }
    else // morf ja spell jms
    {
        if (mrfFlags.Chk(MF_GENE))
        {
            res = chkvaljend(tul, &sona); // kas on mitmesonaline v�ljend?
            if (res != ALL_RIGHT)
            {
                tul->s6na = FSxSTR("");
                tul->eKustTulemused = eMRF_XX;
                throw (VEAD(ERR_MG_MOOTOR, ERR_MINGIJAMA, __FILE__, __LINE__, "$Revision: 878 $")); //jama!
            }
        }
        if (!tul->on_tulem()) // polnd v�ljend
        {
            res = chkgeon(tul, &sona, &(tul->mitmeS6naline)); // kas on mitmesonaline geonimi?
            if (res != ALL_RIGHT)
            {
                tul->s6na = FSxSTR("");
                tul->eKustTulemused = eMRF_XX;
                throw (VEAD(ERR_MG_MOOTOR, ERR_MINGIJAMA, __FILE__, __LINE__, "$Revision: 878 $")); //jama!
            }
        }
        if (tul->on_tulem()) // oli mitmesonaline geonimi
        {
            tul->tagasiTasand = 1;
        }
        else
        {
            // vt, kas *sisse on 1 taval eesti sona
            tul->mitmeS6naline = 1;
            int lyhrez = mrfFlags.Chk(MF_LYHREZH);
            if (mrfFlags.Chk(MF_OLETA))
                mrfFlags.Off(MF_LYHREZH); // oletaja korral ei hakka siin l�henditega taidlema
            //res = chkx( tul, &sona, sona.GetLength(), maxtasand, tagasitasand );
            // kontrollin, kas on nt tema(kese)le
            res = chksuluga(tul, &sona, maxtasand);
            if (res != ALL_RIGHT)
            {
                mrfFlags.OnOff(MF_LYHREZH, lyhrez); // taastame algse l�henirziimi
                tul->s6na = FSxSTR("");
                tul->eKustTulemused = eMRF_XX;
                throw (VEAD(ERR_MG_MOOTOR, ERR_MINGIJAMA, __FILE__, __LINE__, "$Revision: 878 $")); //jama!
            }
            if (!tul->on_tulem())
            {
                TaheHulgad::Puhasta(&sona);
                res = chkx(tul, &sona, sona.GetLength(), maxtasand, &(tul->tagasiTasand));
                if (res != ALL_RIGHT)
                {
                    mrfFlags.OnOff(MF_LYHREZH, lyhrez); // taastame algse l�henirziimi
                    tul->s6na = FSxSTR("");
                    tul->eKustTulemused = eMRF_XX;
                    throw (VEAD(ERR_MG_MOOTOR, ERR_MINGIJAMA, __FILE__, __LINE__, "$Revision: 878 $")); //jama!
                }
            }
            if (!tul->on_tulem())
            {
                if (sona.TrimLeft(TaheHulgad::amor_apostroof) || sona.TrimRight(TaheHulgad::amor_apostroof))
                    res = chkx(tul, &sona, sona.GetLength(), maxtasand, &(tul->tagasiTasand));
                if (res != ALL_RIGHT)
                {
                    mrfFlags.OnOff(MF_LYHREZH, lyhrez); // taastame algse l�henirziimi
                    tul->s6na = FSxSTR("");
                    tul->eKustTulemused = eMRF_XX;
                    throw (VEAD(ERR_MG_MOOTOR, ERR_MINGIJAMA, __FILE__, __LINE__, "$Revision: 878 $")); //jama!
                }
            }
            if (!tul->on_tulem())
            {
                // if (mrfFlags.Chk(MF_LUBAMITMIKUO)) vana versioon HJK 04.2015
                if (mrfFlags.Chk(MF_V0TAKOKKU)==false && // ei võta Sri Lankat kokku
                    mrfFlags.Chk(MF_DFLT_SUG)==false)    // ... ega ole soovitaja
                {           // ... siis Sri kõlbab lubatavaks sõnaks
                    if (((dctLoend[5])[(FSxCHAR *) (const FSxCHAR *) sona] != -1) ||
                        ((dctLoend[6])[(FSxCHAR *) (const FSxCHAR *) sona] != -1))
                        // voib olla mitmesonal. geogr. nime 1. voi 2. osa
                    {
                        tul->Add((const FSxCHAR *) sona, FSxSTR(""), FSxSTR(""), FSxSTR("H"), FSxSTR("?, ")); /* parema puudusel */
                        tul->tagasiTasand = 1;
                    }
                }
            }
            mrfFlags.OnOff(MF_LYHREZH, lyhrez); // taastame algse l�henirziimi
        }
    }
    tul->s6na = *sisse;

    // konveieri puhastamine juurdekirjutada
    // ka 'false' harudele
    for (n = tul->mitmeS6naline; n > 1; n--)
    {
        int idx;
        tul->s6na += FSxSTR(" ");
        tul->s6na += (const FSxCHAR *) (konveier->LyliInf0(1, PRMS_SONA, &idx));
        assert(idx >= 0);
        konveier->Del(idx);
    }
}

