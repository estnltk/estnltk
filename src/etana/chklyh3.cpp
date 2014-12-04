
/*
* kontrollib, kas S6na on suurt�hel. lyhend mingi l�puga;
* n�iteks:
*
* USA-ni, USAni, SS-lane, SSlane, IRA-meelne
*
*/
#include "mrf-mrf.h"
#include "mittesona.h"

int MORF0::chklyh3(MRFTULEMUSED *tulemus, FSXSTRING *S6na, int sygavus, int *tagasitasand)
    {
    int i;
    int res;
    FSXSTRING tmpsona, tmplopp, tmpliik, vorminimi;
    //int tulem = -1; //FS_Failure;
    const FSxCHAR *vn;
    FSXSTRING s;     // sona ise
    FSXSTRING kriips(FSxSTR(""));     // kriips (kui teda on)
    FSXSTRING lopp;     // l�pp ise
    FSXSTRING ne_lopp;     // line lane lopu jaoks
    FSXSTRING lali;     // line lane alguse jaoks
    FSXSTRING ss;     // 
    int s_pik;
    int tyyp=0;
    #define LYHEND 1
    #define PROTSENT 2
    #define KELL 3
    #define PARAGRAHV 4
    #define NUMBER 5
    #define KRAAD 6
    #define MATA 6

//    if ( !ChIsUpper(*S6na) && *S6na != '%' && *S6na != para) /* ei alga suure t�hega */
    // if (!TaheHulgad::OnSuur(S6na, 0) && (*S6na)[0] != (FSxCHAR)'%' && (*S6na)[0] != TaheHulgad::para[0] 
    if (TaheHulgad::AintSuuredjaNrjaKriipsud(S6na))      /* v�ib olla lihtsalt suuret�heline s�na */
	    return ALL_RIGHT;        /* ei suru v�gisi l�hendiks */

    s = (const FSxCHAR *)S6na->SpanIncluding((const FSxCHAR *)(TaheHulgad::protsendinumber));
    if (s.GetLength() != 0)
        if (TaheHulgad::OnLopus(&s, FSxSTR("%")) || TaheHulgad::OnLopus(&s, FSxSTR("%-")))
            tyyp = PROTSENT;
    if (!TaheHulgad::OnSuur(S6na, 0) && tyyp != PROTSENT && (*S6na)[0] != TaheHulgad::para[0] )
	    return ALL_RIGHT;

    if (!tyyp)
        {
        s = (const FSxCHAR *)(S6na->SpanIncluding((const FSxCHAR *)(TaheHulgad::kraadinumber)));
        if (s.GetLength() != 0)
            if (TaheHulgad::OnLopus(&s, (const FSxCHAR *)(TaheHulgad::kraad))
                || TaheHulgad::OnLopus(&s, (const FSxCHAR *)(TaheHulgad::kraadjakriips)) )
                tyyp = KRAAD;
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
        s = (const FSxCHAR *)(S6na->SpanIncluding((const FSxCHAR *)(TaheHulgad::matemaatika1)));
        if (s.GetLength() == 2 && TaheHulgad::OnLopus(&s, FSxSTR("-")))
            tyyp = MATA;
        }
    if (!tyyp)
        {
        s = (const FSxCHAR *)(S6na->SpanIncluding((const FSxCHAR *)(TaheHulgad::suurnrthtkriips)));
        ss = (const FSxCHAR *)(S6na->SpanIncluding((const FSxCHAR *)(TaheHulgad::kellanumber)));
        if (s.GetLength() > ss.GetLength())
            tyyp = LYHEND;
        else if (ss.GetLength() != 0 && s.GetLength() <= ss.GetLength())
            {
            s = ss;
            tyyp = KELL;
            }
        }
    if (!tyyp) // ei saa olla...
	    return ALL_RIGHT;

    s_pik = s.GetLength();
    lopp = (const FSxCHAR *)(S6na->Mid(s_pik));
    if (lopp.GetLength()==0) // pole siin midagi vaadata
        return ALL_RIGHT;
    kriips = (const FSxCHAR *)(s.Mid(s_pik-1));
    if (kriips != FSxSTR("-"))
        kriips = FSxSTR("");
    if (tyyp == LYHEND && kriips == FSxSTR("")) // ebakindel v�rk
        {
        if (s.GetLength()==1) // nt Arike 
            return ALL_RIGHT;
        i = s.ReverseFind(FSxSTR("-"));
        if (i == s.GetLength()-2)
            return ALL_RIGHT; // nt CD-Romile
        }
    s.TrimRight(FSxSTR("-"));
    if (s.GetLength()==0) // pole siin midagi vaadata
        return ALL_RIGHT;
    if (TaheHulgad::PoleMuudKui(&s, &TaheHulgad::number))
        tyyp = NUMBER;
    /* oletan, et on lyhend vm lubatud asi */
	i = 1;
    if (tyyp == LYHEND)
        {
        if(mrfFlags.Chk(MF_LYHREZH))
            {
            if (s.GetLength() == 1 || (!mrfFlags.Chk(MF_SPELL) && s.GetLength() < 7))
                i = 1;
            else
                i = (dctLoend[3])[(FSxCHAR *)(const FSxCHAR *)s];
            }
        }
    //    *(S6na+k) = taht;           /* taastan esialgse sona */
    if (i==-1)      /* pole lyhend */
	    return ALL_RIGHT;
    if ((s.GetLength() > 1 && tyyp == LYHEND && (TaheHulgad::OnAlguses(&lopp, FSxSTR("la")) || TaheHulgad::OnAlguses(&lopp, FSxSTR("li"))) ) 
        || ((tyyp == NUMBER || tyyp == PROTSENT || tyyp == KRAAD) && TaheHulgad::OnAlguses(&lopp, FSxSTR("li"))) )
        {
        ne_lopp = (const FSxCHAR *)(lopp.Mid(2));
        lali = (const FSxCHAR *)(lopp.Left(2));
        vn = nLopud.otsi_ne_vorm((const FSxCHAR *)ne_lopp);
        if (vn != NULL)   /* ongi line lise ... voi lane lase ... */
            {
            vorminimi = vn;
            vorminimi += FSxSTR(", ");
            tmpsona = s;
            if (kriips.GetLength() == 1 && !mrfFlags.Chk(MF_ALGV))
                tmpsona += kriips;
            else
                tmpsona += FSxSTR("=");
            tmpsona += lali;
            if (mrfFlags.Chk(MF_ALGV) || vorminimi == FSxSTR("sg n, "))
                tmpsona += FSxSTR("ne");
            else
                {
                if (TaheHulgad::OnAlguses(&vorminimi, FSxSTR("pl")) || TaheHulgad::OnAlguses(&vorminimi, FSxSTR("sg p")))
                    tmpsona += FSxSTR("s");
                else
                    tmpsona += FSxSTR("se");
                }
            if (ne_lopp == FSxSTR("ne") || ne_lopp == FSxSTR("se"))
                tmplopp = FSxSTR("0");
            else if (ne_lopp == FSxSTR("st"))
                tmplopp = FSxSTR("t");
            else if (TaheHulgad::OnAlguses(&vorminimi, FSxSTR("sg")))
                tmplopp = (const FSxCHAR *)(ne_lopp.Mid(2));
            else
                tmplopp = (const FSxCHAR *)(ne_lopp.Mid(1));
            if (lali == FSxSTR("la"))
                tmpliik = FSxSTR("S");
            else
                tmpliik = FSxSTR("A");
            tulemus->Add((const FSxCHAR *)tmpsona, (const FSxCHAR *)tmplopp, FSxSTR(""), 
                      (const FSxCHAR *)tmpliik, (FSxCHAR *)(const FSxCHAR *)vorminimi);

            *tagasitasand = 1;
	        return ALL_RIGHT;
            }
	    }
    vn = nLopud.otsi_lyh_vorm((const FSxCHAR *)lopp);
    if (vn == NULL)
        {
        if (tyyp == LYHEND && (kriips.GetLength() != 0 || mrfFlags.Chk(MF_OLETA)) &&      // LYH-sona
            !TaheHulgad::OnAlguses(&lopp, FSxSTR("lise")) && !TaheHulgad::OnAlguses(&lopp, FSxSTR("lasi")) )
            {
	        res = chkwrd(tulemus, &lopp, lopp.GetLength(), sygavus, tagasitasand, LIIK_SACU);
	        if (res > ALL_RIGHT)
	            return res; /* viga! */
	        if ( tulemus->on_tulem() )          /* analyys �nnestus */
		        {
                s += kriips;
                tulemus->LisaTyvedeleEtte((const FSxCHAR *)s);
		        }
	        }
		return ALL_RIGHT;
        }
    if (tyyp != LYHEND)
		return ALL_RIGHT;

    /* vist lihtne l�pp */
    *tagasitasand = 1;
    if (TaheHulgad::OnAlguses(&lopp, FSxSTR("te")) )// akronyymidele sellised lopud ei sobi 
	    return ALL_RIGHT;
    if (lopp == FSxSTR("i"))
        vorminimi = FSxSTR("adt, sg g, sg p, ");
    else if (lopp == FSxSTR("d"))
       vorminimi = FSxSTR("pl n, sg p, ");
    else
        {
        vorminimi = vn;
        vorminimi += FSxSTR(", ");
        }
    FSxCHAR vi;
    FSXSTRING fl;
    vi = s[s.GetLength()-1];
    fl = FSxSTR("FLMNRS");
    if (vi == (FSxCHAR)'J');   // jott voi dzhei; iga lopp sobib...
    else if (TaheHulgad::para.Find(vi) != -1 || vi == (FSxCHAR)'%')
        {
        if (lopp == FSxSTR("d"))
            vorminimi = FSxSTR("pl n, ");
        }
    else if (fl.Find(vi) != -1)
        {
        if (!mrfFlags.Chk(MF_OLETA))
            {
            if (!TaheHulgad::OnAlguses(&lopp, FSxSTR("i")) && !TaheHulgad::OnAlguses(&lopp, FSxSTR("e")))
	            return ALL_RIGHT;   // yldse ei sobinud 
            }
        else if (lopp == FSxSTR("d"))
           vorminimi = FSxSTR("pl n, ");
        }
    else
        {
        //vi = s.SuurPisiks(s.GetLength()-1); // tahan lihtsalt vi pisiks teha
        vi = TaheHulgad::SuurPisiks(&s, s.GetLength()-1); // tahan lihtsalt vi pisiks teha
        if (TaheHulgad::taish.Find(vi) != -1)  // lyh lopus vokaal
            {
            if (TaheHulgad::OnAlguses(&lopp, FSxSTR("i")) || TaheHulgad::OnAlguses(&lopp, FSxSTR("e")))
	            return ALL_RIGHT;   // yldse ei sobinud 
            }
        if (!mrfFlags.Chk(MF_OLETA))
            {
            if (s.GetLength() == 1)        
                {
                if (TaheHulgad::OnAlguses(&lopp, FSxSTR("i")) || TaheHulgad::OnAlguses(&lopp, FSxSTR("e")))
	                return ALL_RIGHT;   // yldse ei sobinud 
                }
            else
                {
                FSxCHAR eelvi;
                eelvi = TaheHulgad::SuurPisiks(&s, s.GetLength()-2);

                if (TaheHulgad::taish.Find(eelvi)==-1 && 
                    s != FSxSTR("GOST") && s != FSxSTR("GATT") && s != FSxSTR("SAPARD") && s != FSxSTR("SARS"))
                    if (TaheHulgad::OnAlguses(&lopp, FSxSTR("i")) || TaheHulgad::OnAlguses(&lopp, FSxSTR("e")))
	                    return ALL_RIGHT;   // yldse ei sobinud 
                }
            }
        }
    tulemus->Add((const FSxCHAR *)s, (const FSxCHAR *)lopp, FSxSTR(""), 
          FSxSTR("Y"), (const FSxCHAR *)vorminimi);
    return ALL_RIGHT;
    }
