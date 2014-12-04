
// 2002.06.13
//
// TV000823 'cXXfirst()' annab 0pikkusega stringi peale 'POLE_YLDSE'
//
#include <string.h>

#include "cxxbs3.h"

int cTYVEINF::cXXfirst( //==0:leidis;==POLE_SEDA,POLE_YLDSE:polnud
    const FSXSTRING *stem,
    int *index)
    {
    return cXXfirst((const FSxCHAR *)(*stem), stem->GetLength(), index);
    }

int cTYVEINF::cXXfirst( //==0:leidis;==POLE_SEDA,POLE_YLDSE:polnud
	const FSxCHAR *stem,
	const int     slen,
	int          *index)
	{
	int tab_idx, ret=0, i;
    const UB1 *ptr;
    if(slen<=0)
        {
        return POLE_YLDSE;
        }
	if ( KOtsi(&ps, stem, slen, &tab_idx) == true )
		{
		// Oli kahendtabelis.
		FindBt(tab_idx, index);
        ret=0;
		} 
	else
		{
		// Polnud kahendtabelis.
		ret = FindBlk((tab_idx ? tab_idx - 1 : tab_idx), stem, slen, index);
		}
	if(ret == 0)
		{
        int nS6naLiiki=sonaliik[pre.v_tabidx()]->GetLength();
        //
        //selle koha peal anname tyveinfo tagasi, 
        //seda peab sutsu teisendama! 
        //
        ptr = (UB1 *)xptr;
        //
        //stem - otsitav t�vi
        //dptr viitab UUS_TYVE_INF struktuurile kettal
        //see tuleb teisendada vana TYVE_INF struktuuri elementideks
        //
        for(i=0; i < nS6naLiiki; i++)
            {
            int tmp;
			dptr[i].piiriKr6nksud = pre.v_piir(); // TV 990312            
            tmp = (((int)(ptr[0]))&0xFF) | ( (((int)(ptr[1]))&0xFF)<<8);
            dptr[i].idx.blk_idx = (_uint8)((tmp   )& 0x3F );
            dptr[i].idx.tab_idx = (_int16)((tmp>>6)& 0x3FF);
            switch(nKr6nksuBaiti)
                {
                case 1:
                    dptr[i].lisaKr6nksud=((_int16)(ptr[2]))&0xFF;
                    break;
                case 2:
                    dptr[i].lisaKr6nksud=(_int16)(((unsigned)(ptr[2])) | (((unsigned)(ptr[3])) << 8));
                    break;
                }
            ptr += sizeof(_uint8)+sizeof(_uint8)+nKr6nksuBaiti;
            MKT1c *rec;
            if((rec=tyveMuutused.Get(dptr[i].idx.tab_idx,dptr[i].idx.blk_idx))==NULL) 
                {
//printf("%s:%d -- SUUR JAMA\n", __FILE__,__LINE__);
                // vale l�pu # grupis 
                throw(VEAD(ERR_MG_MOOTOR,ERR_ROTTEN,__FILE__,__LINE__, "$Revision: 557 $"));
                }
            dptr[i].lg_nr = rec->lgNr; 
            }
        }
//printf("%s:%d -- %5d\n", __FILE__,__LINE__,ret);
	return ret;
	}

//protected
void cTYVEINF::NextPre(void)
	{
	//pptr += dSizeOfPrefiks+pre.v_erinevaid()*sizeof(FSxCHAR)+
	//    dSizeOfLg2(sonaliik[pre.v_tabidx()]->GetLength(),
    //    nKr6nksuBaiti); // selle arvut!!!! 
	pptr += dSizeOfPrefiks+pre.v_erinevaid()*dctsizeofFSxCHAR+
	    dSizeOfLg2(sonaliik[pre.v_tabidx()]->GetLength(),
        nKr6nksuBaiti); // selle arvut!!!! 
	pre.BytesToPrefiks(pptr);
	xptr = pptr + dSizeOfPrefiks; // viit jooksvale tyvejupile
	stem_no++;
	}

//private
void cTYVEINF::FindBt( // ==0:leidis; ==1:polnud; ==-1:jama
	const int tab_idx, // 2ndtabeli index = k@shi bloki nr 
	int *index)
	{
	register int res;

	if((res = CacheRead(&dctFile, tab_idx)) != 0)
		{
		throw(VEAD(ERR_MG_MOOTOR,ERR_RD,__FILE__,__LINE__, "$Revision: 557 $"));
		}
	pptr = xptr;
	pre.BytesToPrefiks(pptr);
	xptr += dSizeOfPrefiks;     // t�vejupp
	kcnt = pre.v_samasid();
	*index = pre.v_tabidx();    // s�naliikide tabeli indeks
	}

//  Otsime v6rdlemiseks sobiva tyve.
//sisse:
//  pre     - jooksev PREFIKS
//  kcnt    - nii-mitu peab kokkulangema
//  stem_no - jooksva tyve nr.
//  pptr    - char-viit jooksvale prefiksile pakitud puhvris
//v�lja:
//  next_w
//      == POLE_YLDSE
//      == POLE_SEDA
//      == V0RDLE
//extern:
//  pre     - jooksev PREFIKS
//  kcnt    - nii-mitu langeb kokku
//  stem_no - jooksva tyve nr.
//  pptr    - char-viit jooksvale prefiksile pakitud puhvris
//  xptr    - eelmisest erinev tyveosa
//
//private
int cTYVEINF::NextStem(void) // V�rdlemiseks sobiva tyve otsimine
	{
	while(pre.v_samasid() > (int)kcnt)
		{
		NextPre();
		}
    if(STRSOUP::Kahest(xptr) == EofB)
		{
		return POLE_SEDA; // bloki l6pp
		}
	if((int)kcnt == pre.v_samasid())
		{
		return V0RDLE;
		}
	// assert(pre.samasid < (int)kcnt);

	return POLE_YLDSE;
	}

//private
int cTYVEINF::FindDb( // {POLE_YLDSE, POLE_SEDA, s�naliikide-tabeli-idx}
	const FSxCHAR *stem,    // otsitav tyvi
	const int   slen)       // t�ve  pikkus
	{
	register int erinevaid,
			     res;

	while((res=NextStem())==V0RDLE)
		{
        erinevaid=pre.v_erinevaid();
		while((int)kcnt < slen && erinevaid > 0 && 
            STRSOUP::Kahest(xptr)==stem[kcnt])
			{
            xptr+=dctsizeofFSxCHAR;
			kcnt++;
			erinevaid--;
			}
		if((int)kcnt==slen)
			{
			if(erinevaid > 0)
				{
				return POLE_SEDA;
				}
			// erinevaid==0 -- leitud!
			return pre.v_tabidx(); // siin on mingi tyybiteisendus!
			}
		// kcnt < slen -- otsime yles j@rgmise
		//				  v6rdlemiseks sobiva tyve
        //if(erinevaid > 0 && *(FSxCHAR *)xptr > stem[kcnt])
        if(erinevaid > 0 && STRSOUP::Kahest(xptr) > stem[kcnt])
            {
            return POLE_YLDSE;
            }
		NextPre();
		}
	return res; // {POLE_YLDSE, POLE_SEDA}
	}

//private
int cTYVEINF::FindBlk(  // {POLE_YLDSE, POLE_SEDA, 0}: otsime blokist
	const int tab_idx,  // 2ndtabeli index == k�shi bloki nr
	const FSxCHAR *stem,
	const int slen,
	int *index)         // == s�naliikide tabeli idx v�lja
	{
    int find_diff(
        const FSxCHAR *s1, // 1mene string
        const int      l1, // 1mese stringi pikkus
        const FSxCHAR *s2, // 2ne string 
        const int      l2);// 2se stringi pikkus

    register int res;
    const FSxCHAR *kahendtabelist;
	if((res = CacheRead(&dctFile, tab_idx)) != 0) 
		{
		//return res; // viga -1 tegelikult
        throw(VEAD(ERR_MG_MOOTOR,ERR_ROTTEN,__FILE__,__LINE__, "$Revision: 557 $"));
		}
    kahendtabelist=ps.v6tmed + ps.kTabel[tab_idx].s_nihe;
//printf("%s:%d -- tab_idx %5d\n", __FILE__,__LINE__,tab_idx);
//printf("%s:%d -- ps.kTabel[tab_idx].s_nihe %5d\n", __FILE__,__LINE__,ps.kTabel[tab_idx].s_nihe);
    kcnt = find_diff(stem,slen,kahendtabelist,ps.kTabel[tab_idx].len);
	pptr = xptr;
	pre.BytesToPrefiks(pptr);
	NextPre(); // alustame 2st PREFIKSist
	if((*index = FindDb(stem, slen)) < 0)
		{
		return *index;  // {POLE_YLDSE, POLE_SEDA}
		}	
    return 0;           // *index == s6naliikide tabeli index
	}
//-------------*/

// }}-2002.05.30


