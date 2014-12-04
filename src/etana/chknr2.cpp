
/*
* kontrollib, kas S6na on mingi nr kombinatsioon;
* n�iteks:
* arv  j�rgarv  murdarv  ???  protsent  kraad vahemik  kellaaeg  kuup�ev  seis
*  1    1.      0,5 1/3  3x100   5%             2-3      5.00    9.05.95   1:0
*
* 5-aastane, 5aastane
* 5-ni, 5ni
* 30-ndad, 30ndad
*
* osa numbri ja l�pu kombinatsioone t��deldakse chklyh3 sees
*
*/
#include "mrf-mrf.h"
#include "mittesona.h"

int MORF0::chknr2(MRFTULEMUSED *tulemus, FSXSTRING *S6na)
    {
    int res;
    //int tulem = -1; //FS_Failure;
    int tagasi1;
    const FSxCHAR *vn;
    FSXSTRING s_algus, sona, s, ss;
    FSXSTRING kriips, lopp;
    FSXSTRING tmpsona, vorminimi, tmplopp;
    int tyyp=0, s_pik;
    #define PROTSENT 2
    #define KELL 3
    #define ARV 4
    #define NUMBER 5
    #define KRAAD 6
    #define KRAADC 7
    #define PARAGRAHV 8
    FSxCHAR vi=0;
    FSXSTRING kl;

    kl = FSxSTR("CFK");
    s_algus = (const FSxCHAR *)(S6na->Mid(0,1));
    if (s_algus == FSxSTR("+") || s_algus == FSxSTR("-"))
        sona = (const FSxCHAR *)(S6na->Mid(1));
    else
        {
        sona = *S6na;
        s_algus = FSxSTR("");
        }
    s = (const FSxCHAR *)(sona.SpanIncluding((const FSxCHAR *)(TaheHulgad::protsendinumber)));
    if (s.GetLength() != 0)
        if (TaheHulgad::OnLopus(&s, FSxSTR("%")) || TaheHulgad::OnLopus(&s, FSxSTR("%-")))
            tyyp = PROTSENT;
    if (!tyyp)
        {
//        vi = s[s.GetLength()-1];
        s = (const FSxCHAR *)(sona.SpanIncluding((const FSxCHAR *)(TaheHulgad::kraadinrtht)));
		if (s.GetLength() != 0)
			{
            if (TaheHulgad::OnLopus(&s, (const FSxCHAR *)(TaheHulgad::kraad)) 
                || TaheHulgad::OnLopus(&s, (const FSxCHAR *)(TaheHulgad::kraadjakriips)))
                tyyp = KRAAD;
            else 
                {
                if (s.GetLength() > 2)
                    {
                    vi = s[s.GetLength()-1];
                    if (s.Find((const FSxCHAR *)(TaheHulgad::kraad)) == s.GetLength()-2 && kl.Find(vi)!=-1)
                        tyyp = KRAADC;
                    }
                }
			}
        }
    if (!tyyp)
        {
        s = (const FSxCHAR *)(S6na->SpanIncluding((const FSxCHAR *)(TaheHulgad::paranumber)));
        if (s.GetLength() != 0)
            if (TaheHulgad::OnAlguses(&s, (const FSxCHAR *)(TaheHulgad::para)))
                tyyp = PARAGRAHV;
        }
    if (!tyyp)
        {
        if (sona.FindOneOf((const FSxCHAR *)(TaheHulgad::number)) == -1) // polegi numbrit kuskil...
	        return ALL_RIGHT;
        s = (const FSxCHAR *)(sona.SpanIncluding((const FSxCHAR *)(TaheHulgad::kellanumber)));
        ss = (const FSxCHAR *)(sona.SpanIncluding((const FSxCHAR *)(TaheHulgad::arv)));
        if (s_algus.GetLength() == 0) //  +- pole ees
            {
            if (s.GetLength() > ss.GetLength())
                tyyp = KELL;
            else if (ss.GetLength() != 0 && s.GetLength() <= ss.GetLength())
                {
                s = ss;
                tyyp = ARV;
                }
            }
        else // kellaajal ei tohi +- olla
            {
            if (ss.GetLength() !=0)
                {
                s = ss;
                tyyp = ARV;
                }
            }
        }
    if (!tyyp) // ei saa olla...
	    return ALL_RIGHT;
/////
    s_pik = s.GetLength();
    lopp = (const FSxCHAR *)(S6na->Mid(s_pik+s_algus.GetLength()));
    kriips = (const FSxCHAR *)(s.Mid(s_pik-1+s_algus.GetLength()));
    if (kriips != FSxSTR("-"))
        kriips = FSxSTR("");
    s.TrimRight(FSxSTR("-"));
    if (TaheHulgad::PoleMuudKui(&s, &(TaheHulgad::number)))
        tyyp = NUMBER;
    if (lopp.GetLength() == 0) // loppu pole
        {
        if (tyyp == NUMBER)
            tulemus->Add((const FSxCHAR *)(*S6na), FSxSTR("0"), FSxSTR(""), FSxSTR("N"), FSxSTR("?, "));
        else if (tyyp == ARV || tyyp == KELL)
            {
            if (TaheHulgad::OnLopus(&s, FSxSTR(".")) && kriips == FSxSTR(""))
                {
                FSXSTRING nn;
//                nn = s;
                nn = (const FSxCHAR *)(s.Mid(0, s.GetLength()-1));
                if (TaheHulgad::PoleMuudKui(&nn, &TaheHulgad::number)) // ainult nr.
                    tulemus->Add((const FSxCHAR *)(*S6na), FSxSTR("0"), FSxSTR(""), FSxSTR("O"), FSxSTR("?, "));
                else 
                    {
                    int kr, kr_pik;
                    kr_pik = 2;
                    kr = nn.Find(FSxSTR(".-"));
                    if (kr == -1)
                        kr = nn.Find(FSxSTR("./"));
                    if (kr == -1)
                        {
                        kr_pik = 1;
                        kr = nn.Find(FSxSTR("-"));
                        }
                    if (kr == -1)
                        kr = nn.Find(FSxSTR("/"));
                    if (kr == -1)
                        {
                        kr_pik = 3;
                        kr = nn.Find(FSxSTR("..."));
                        }
                    if (kr != -1)
                        { // 11.-12. v�i 11-12.
                        FSXSTRING nn1, nn2;
                        nn1 = (const FSxCHAR *)(nn.Left(kr));
                        nn2 = (const FSxCHAR *)(nn.Mid(kr+kr_pik));
                        if (TaheHulgad::PoleMuudKui(&nn1, &(TaheHulgad::number)) 
                            && TaheHulgad::PoleMuudKui(&nn2, &(TaheHulgad::number)))
                            tulemus->Add((const FSxCHAR *)(*S6na), FSxSTR("0"), FSxSTR(""), FSxSTR("O"), FSxSTR("?, "));
                        }
                    else
                        tulemus->Add((const FSxCHAR *)(*S6na), FSxSTR("0"), FSxSTR(""), FSxSTR("N"), FSxSTR("?, "));
                    }
                }
            else
                tulemus->Add((const FSxCHAR *)(*S6na), FSxSTR("0"), FSxSTR(""), FSxSTR("N"), FSxSTR("?, "));
            }
        else if (tyyp == KRAAD || tyyp == KRAADC)
            tulemus->Add((const FSxCHAR *)(*S6na), FSxSTR("0"), FSxSTR(""), FSxSTR("Y"), FSxSTR("?, "));
        else if (tyyp == PROTSENT || tyyp == PARAGRAHV)
            {
            if (s_pik == 1) // %, paragrahv on lyhend
                tulemus->Add((const FSxCHAR *)(*S6na), FSxSTR("0"), FSxSTR(""), FSxSTR("Y"), FSxSTR("?, "));
            else
                {
                if (tyyp==PARAGRAHV && s_pik==2 && s[0]==s[1]) // parapara
                    tulemus->Add((const FSxCHAR *)(*S6na), FSxSTR("0"), FSxSTR(""), FSxSTR("Y"), FSxSTR("?, "));
                else
                    {
                    if (s.FindOneOf((const FSxCHAR *)(TaheHulgad::number)) == -1) // polegi numbrit kuskil...
	                    return ALL_RIGHT;
                    tulemus->Add((const FSxCHAR *)(*S6na), FSxSTR("0"), FSxSTR(""), FSxSTR("N"), FSxSTR("?, "));
                    }
                }
            }
        return ALL_RIGHT;              
        }
    if (s.GetLength() > 0)
        {
        vi = s[s.GetLength()-1];
        if (!(TaheHulgad::number.Find(vi)!=-1 || vi==(FSxCHAR)'%' || 
            TaheHulgad::kraad.Find(vi)!=-1 || kl.Find(vi)!=-1 ||    // ei l�ppe numbri, % ega kraadiga
            (tyyp==PARAGRAHV && s.GetLength()==1) ))                // ega ole lihtsalt paragrahvim�rk
            return ALL_RIGHT;             // pole korrektne number 
        }
    if (TaheHulgad::AintSuured(&lopp))
        lopp.MakeLower();
    if (!TaheHulgad::PoleSuuri(&lopp))
		return ALL_RIGHT; // oli suured-va"iksed segamini 


    if (loend.nr_lyh.Get((FSxCHAR *)(const FSxCHAR *)lopp))
        {
        tulemus->Add((const FSxCHAR *)(*S6na), FSxSTR("0"), FSxSTR(""), FSxSTR("Y"), FSxSTR("?, "));
	    return ALL_RIGHT;
        }
    tmpsona = s_algus;
    tmpsona += s;
	if (s.GetLength()==1 && (tyyp==PARAGRAHV || tyyp == PROTSENT)) // %-des
		{
        vn = nLopud.otsi_nr_vorm((const FSxCHAR *)lopp);
        if (vn == NULL && TaheHulgad::OnAlguses(&lopp, FSxSTR("de")))
			vn = nLopud.otsi_lyh_vorm((const FSxCHAR *)lopp);
        if (vn != NULL)
			{
            vorminimi = vn;
            vorminimi += FSxSTR(", ");
            tulemus->Add((const FSxCHAR *)tmpsona, 
                              (const FSxCHAR *)lopp, FSxSTR(""), FSxSTR("Y"), (const FSxCHAR *)vorminimi);
			}
        return ALL_RIGHT;
		}
//    if (lplen < 4) /* lihtne lopp */
    if (lopp.GetLength() < 4)
        {
        vn = nLopud.otsi_nr_vorm((const FSxCHAR *)lopp);
        if (vn != NULL)
            {
            vorminimi = vn;
            vorminimi += FSxSTR(", ");
//	        if ( *(S6na+k-1) == '%' || !strncmp(S6na+k-2, "%-", 2) || !strncmp(S6na+k-2, "\260-", 2))
            if (tyyp == PROTSENT || tyyp == KRAAD || tyyp == KRAADC || 
                (tyyp==PARAGRAHV && (s.GetLength()==1 || s[0]==s[1])))
                tulemus->Add((const FSxCHAR *)tmpsona, 
                              (const FSxCHAR *)lopp, FSxSTR(""), FSxSTR("Y"), (const FSxCHAR *)vorminimi);
	        else
                tulemus->Add((const FSxCHAR *)tmpsona, 
                             (const FSxCHAR *)lopp, FSxSTR(""), FSxSTR("N"), (const FSxCHAR *)vorminimi);
			return ALL_RIGHT;
	        }
        }
//    if ( *(S6na+k-1) == '\260' && strncmp(sisesona, "si", 2) )  // kraadima'rk; iga lopp ei sobi kah...
    if (tyyp == KRAAD && !TaheHulgad::OnAlguses(&lopp, FSxSTR("si")))
        {
        vn = nLopud.otsi_ne_vorm((const FSxCHAR *)lopp);
//        j = otsi(sisesona, (char **)ne_lopud, ne_loppe);
//        if ( j != -1 ) 
        if (vn != NULL)
            {
            vorminimi = vn;
            vorminimi += FSxSTR(", ");
            if (mrfFlags.Chk(MF_ALGV)) // algvormiks on kraadine
                {
                tmpsona += FSxSTR("=ne");
                }
            else
                {
                tmpsona += FSxSTR("=");
                if (lopp==FSxSTR("ne") || lopp==FSxSTR("se"))
                    tmpsona += lopp;
                else if (lopp==FSxSTR("st"))
                    tmpsona += FSxSTR("s");
                else if (TaheHulgad::OnAlguses(&lopp, FSxSTR("se")))
                    tmpsona += FSxSTR("se");
                else if (TaheHulgad::OnAlguses(&lopp, FSxSTR("ste")))
                    tmpsona += FSxSTR("s");
                else    // ei saa olla
                    return ALL_RIGHT;
                }
            if (lopp==FSxSTR("ne") || lopp==FSxSTR("se"))
                tmplopp = FSxSTR("0");
            else if (lopp==FSxSTR("st"))
                tmplopp = FSxSTR("t");
            else if (TaheHulgad::OnAlguses(&lopp, FSxSTR("se")))
                tmplopp = (const FSxCHAR *)(lopp.Mid(2));
            else if (TaheHulgad::OnAlguses(&lopp, FSxSTR("ste")))
                tmplopp = (const FSxCHAR *)(lopp.Mid(1));
            else    // ei saa olla
                return ALL_RIGHT;
            tulemus->Add((const FSxCHAR *)tmpsona, 
                         (const FSxCHAR *)tmplopp, FSxSTR(""), FSxSTR("A"), (const FSxCHAR *)vorminimi);
            }
        }
    if (tulemus->on_tulem())
	    return ALL_RIGHT;
/*
    if ( !strcmp(sisesona, "ne"))
        if ( strchr(num, *(S6na+k-2)))  // vahemalt 2-kohaline nr 
*/
    if (lopp == FSxSTR("ne")) // 115-ne 20-ne 
        {
        if (s.GetLength()>1 && tyyp == NUMBER)
            {
            FSxCHAR elvi;
            elvi = s[s.GetLength()-2];
            if (vi==(FSxCHAR)'0' || elvi==(FSxCHAR)'1')
                {
                if ( !mrfFlags.Chk(MF_ALGV) ) // ei taheta algvormi  
                    {
/*
                if ( *(S6na+k) == '-' )
                    strcat( tmpsona, "-" );
                strcat( tmpsona, sisesona );
*/
                    tmpsona += kriips;
                    tmpsona += lopp;
                    }
                }
            tulemus->Add((const FSxCHAR *)tmpsona, FSxSTR("0"), FSxSTR(""), FSxSTR("N"), FSxSTR("sg g, ")); 
            }
	    return ALL_RIGHT;
        }

//    if (strchr("03456789", *(S6na+k-1)) && !strncmp(sisesona, "nda", 3)) // nda...
    if (TaheHulgad::OnAlguses(&lopp, FSxSTR("nda")) && tyyp == NUMBER && s.GetLength()>0)
        {
        int nda = 0;
        if (TaheHulgad::ndanumber.Find(vi)!=-1)
            nda =1;
        else
            {
            if (s.GetLength()>1)
                {
                FSxCHAR elvi;
                elvi = s[s.GetLength()-2];
                if (elvi==(FSxCHAR)'1')   // 11-nda
                    nda = 1;
                }
            }
        if (nda)
	        {
            vorminimi = FSxSTR("");
            if (lopp == FSxSTR("nda"))
                {
                vorminimi = FSxSTR("sg g");
                tmplopp = FSxSTR("0");
                }
            else
                {
                FSXSTRING lopp_3;
                lopp_3 = (const FSxCHAR *)lopp.Mid(3);
                vn = nLopud.otsi_nda_vorm((const FSxCHAR *)lopp_3);
                if (vn != NULL)   // on mingi lopp 
                    {
                    vorminimi = vn;
                    tmplopp = lopp_3;
                    }
                }
            }
        if ( vorminimi.GetLength() !=0 )     // mingi vorm sobiski 
            {
            if ( !mrfFlags.Chk(MF_ALGV) ) /* ei taheta algvormi */
                {
                tmpsona += kriips;
                tmpsona += FSxSTR("nda");
                }
            else
                tmpsona += FSxSTR("=s");
            vorminimi += FSxSTR(", ");
            tulemus->Add((const FSxCHAR *)tmpsona, 
                          (const FSxCHAR *)tmplopp, FSxSTR(""), FSxSTR("O"), (const FSxCHAR *)vorminimi);
	        return ALL_RIGHT;
            }
        }
    /* a"kki on hoopis nr-sona v�i 8aastane */
    if (kriips.GetLength() == 1 || (kriips.GetLength()==0 && (tyyp==ARV || tyyp==NUMBER))) //kuni 8. aprill 2005 oli tyyp==NUMBER HJK
        {
        if (!TaheHulgad::OnAlguses(&lopp, FSxSTR("lise")) && 
            !TaheHulgad::OnAlguses(&lopp, FSxSTR("lasi")) && lopp.GetLength() > 3)
            {
            res = chkwrd(tulemus, &lopp, lopp.GetLength(), 100, &tagasi1, LIIK_A);
            if (res > ALL_RIGHT)
	            return res; /* viga! */
	        }
        if (!tulemus->on_tulem())   /* analyys ebannestus */
	        if ( lopp == FSxSTR("kaupa") )
                tulemus->Add((const FSxCHAR *)lopp, FSxSTR("0"), FSxSTR(""), FSxSTR("D"), FSxSTR("")); /* HJK 07.06.01; pole endas eriti kindel */
        }
    if (tulemus->on_tulem())   /* analyys �nnestus */
	    {
        tmpsona += FSxSTR("_");
        tulemus->LisaTyvedeleEtte((const FSxCHAR *)tmpsona);
        return ALL_RIGHT;
	    }
    if (lopp.GetLength() == 1 && TaheHulgad::eestitht.Find(lopp[0])!=-1 )  /* 1 taht voib ikka lopus olla */
        {
        tulemus->Add((const FSxCHAR *)(*S6na), FSxSTR("0"), FSxSTR(""), FSxSTR("Y"), FSxSTR("?, ")); 
	    return ALL_RIGHT;
        }
    return ALL_RIGHT;
    }
