
#include "mittesona.h"
#include "mrf-mrf.h"


static  FSxC6 lopp_ja_vormid[] =    //eri liiki mittes�nade l�ppude t�lgendamiseks
              
//1. veerg noomenite tavalised lopud 
//2. veerg chknr2.cpp   nda_vormid 
//3. veerg chklyh3.cpp  lyh_vormid 
//4. veerg arvans.cpp   ns_vormid
//5. veerg arvapn.cpp   pn_vormid
//5. veerg chknr2.cpp   numbritele sobivad vormid
    {
    {FSxSTR("d"),     FSxSTR("pl n"),  FSxSTR("pl n"),                  0,                0,                0},
    {FSxSTR("de"),                 0,  FSxSTR("pl g"),     FSxSTR("pl g"),   FSxSTR("pl g"),                0},
    {FSxSTR("dega"),               0,  FSxSTR("pl kom"), FSxSTR("pl kom"), FSxSTR("pl kom"),                0},
    {FSxSTR("deks"),               0,  FSxSTR("pl tr"),   FSxSTR("pl tr"),  FSxSTR("pl tr"),                0},
    {FSxSTR("del"),                0,  FSxSTR("pl ad"),   FSxSTR("pl ad"),  FSxSTR("pl ad"),                0},
    {FSxSTR("dele"),               0,  FSxSTR("pl all"), FSxSTR("pl all"), FSxSTR("pl all"),                0},
    {FSxSTR("delt"),               0,  FSxSTR("pl abl"), FSxSTR("pl abl"), FSxSTR("pl abl"),                0},
    {FSxSTR("dena"),               0,  FSxSTR("pl es"),   FSxSTR("pl es"),  FSxSTR("pl es"),                0},
    {FSxSTR("deni"),               0,  FSxSTR("pl ter"), FSxSTR("pl ter"), FSxSTR("pl ter"),                0},
    {FSxSTR("des"),                0,  FSxSTR("pl in"),   FSxSTR("pl in"),  FSxSTR("pl in"),                0},
    {FSxSTR("desse"),              0,  FSxSTR("pl ill"), FSxSTR("pl ill"), FSxSTR("pl ill"),                0},
    {FSxSTR("dest"),               0,  FSxSTR("pl el"),   FSxSTR("pl el"),  FSxSTR("pl el"),                0},
    {FSxSTR("deta"),               0,  FSxSTR("pl ab"),   FSxSTR("pl ab"),  FSxSTR("pl ab"),                0},
    {FSxSTR("e"),                  0,  FSxSTR("pl p"),     FSxSTR("pl p"),                0,                0},
    {FSxSTR("ga"),  FSxSTR("sg kom"),  FSxSTR("sg kom"), FSxSTR("sg kom"), FSxSTR("sg kom"), FSxSTR("sg kom")},
    {FSxSTR("i"),                  0,  FSxSTR("sg g, sg p"),FSxSTR("pl p"),               0,                0},
    {FSxSTR("id"),    FSxSTR("pl p"),  FSxSTR("pl n"),     FSxSTR("pl p"),   FSxSTR("pl p"),                0},
    {FSxSTR("ide"),                0,  FSxSTR("pl g"),                  0,                0,                0},
    {FSxSTR("idega"),              0,  FSxSTR("pl kom"),                0,                0,                0},
    {FSxSTR("ideks"),              0,  FSxSTR("pl tr"),                 0,                0,                0},
    {FSxSTR("idel"),               0,  FSxSTR("pl ad"),                 0,                0,                0},
    {FSxSTR("idele"),              0,  FSxSTR("pl all"),                0,                0,                0},
    {FSxSTR("idelt"),              0,  FSxSTR("pl abl"),                0,                0,                0},
    {FSxSTR("idena"),              0,  FSxSTR("pl es"),                 0,                0,                0},
    {FSxSTR("ideni"),              0,  FSxSTR("pl ter"),                0,                0,                0},
    {FSxSTR("ides"),               0,  FSxSTR("pl in"),                 0,                0,                0},
    {FSxSTR("idesse"),             0,  FSxSTR("pl ill"),                0,                0,                0},
    {FSxSTR("idest"),              0,  FSxSTR("pl el"),                 0,                0,                0},
    {FSxSTR("ideta"),              0,  FSxSTR("pl ab"),                 0,                0,                0},
    {FSxSTR("iga"),                0,  FSxSTR("sg kom"),                0,                0,                0},
    {FSxSTR("iks"),  FSxSTR("pl tr"),  FSxSTR("sg tr"),   FSxSTR("pl tr"),                0,                0},
    {FSxSTR("il"),   FSxSTR("pl ad"),  FSxSTR("sg ad"),   FSxSTR("pl ad"),                0,                0},
    {FSxSTR("ile"), FSxSTR("pl all"),  FSxSTR("sg all"), FSxSTR("pl all"),                0,                0},
    {FSxSTR("ilt"), FSxSTR("pl abl"),  FSxSTR("sg abl"), FSxSTR("pl abl"),                0,                0},
    {FSxSTR("ina"),  FSxSTR("pl es"),  FSxSTR("sg es"),   FSxSTR("pl es"),                0,                0},
    {FSxSTR("ini"), FSxSTR("pl ter"),  FSxSTR("sg ter"), FSxSTR("pl ter"),                0,                0},
    {FSxSTR("is"),   FSxSTR("pl in"),  FSxSTR("sg in"),   FSxSTR("pl in"),                0,                0},
    {FSxSTR("isse"),FSxSTR("pl ill"),  FSxSTR("sg ill"), FSxSTR("pl ill"),                0,                0},
    {FSxSTR("ist"),  FSxSTR("pl el"),  FSxSTR("sg el"),   FSxSTR("pl el"),                0,                0},
    {FSxSTR("ita"),                0,  FSxSTR("sg ab"),                 0,                0,                0},
    {FSxSTR("ks"),   FSxSTR("sg tr"),  FSxSTR("sg tr"),   FSxSTR("sg tr"),  FSxSTR("sg tr"),  FSxSTR("sg tr")},
    {FSxSTR("l"),    FSxSTR("sg ad"),  FSxSTR("sg ad"),   FSxSTR("sg ad"),  FSxSTR("sg ad"),  FSxSTR("sg ad")},
    {FSxSTR("le"),  FSxSTR("sg all"),  FSxSTR("sg all"), FSxSTR("sg all"), FSxSTR("sg all"), FSxSTR("sg all")},
    {FSxSTR("lt"),  FSxSTR("sg abl"),  FSxSTR("sg abl"), FSxSTR("sg abl"), FSxSTR("sg abl"), FSxSTR("sg abl")},
    {FSxSTR("na"),   FSxSTR("sg es"),  FSxSTR("sg es"),   FSxSTR("sg es"),  FSxSTR("sg es"),  FSxSTR("sg es")},
    {FSxSTR("ni"),  FSxSTR("sg ter"),  FSxSTR("sg ter"), FSxSTR("sg ter"), FSxSTR("sg ter"), FSxSTR("sg ter")},
    {FSxSTR("s"),    FSxSTR("sg in"),  FSxSTR("sg in"),   FSxSTR("sg in"),  FSxSTR("sg in"),  FSxSTR("sg in")},
    {FSxSTR("sid"),                0,  FSxSTR("pl p"),     FSxSTR("pl p"),   FSxSTR("pl p"),                0},
    {FSxSTR("sse"), FSxSTR("sg ill"),  FSxSTR("sg ill"), FSxSTR("sg ill"), FSxSTR("sg ill"), FSxSTR("sg ill")}, 
    {FSxSTR("st"),   FSxSTR("sg el"),  FSxSTR("sg el"),   FSxSTR("sg el"),  FSxSTR("sg el"),  FSxSTR("sg el")},
    {FSxSTR("t"),     FSxSTR("sg p"),  FSxSTR("sg p"),     FSxSTR("sg p"),   FSxSTR("sg p"),                0},
    {FSxSTR("ta"),   FSxSTR("sg ab"),  FSxSTR("sg ab"),   FSxSTR("sg ab"),  FSxSTR("sg ab"),  FSxSTR("sg ab")},
    {FSxSTR("te"),    FSxSTR("pl g"),  FSxSTR("pl g"),     FSxSTR("pl g"),   FSxSTR("pl g"),                0},
    {FSxSTR("tega"),FSxSTR("pl kom"),  FSxSTR("pl kom"), FSxSTR("pl kom"), FSxSTR("pl kom"),                0},
    {FSxSTR("teks"), FSxSTR("pl tr"),  FSxSTR("pl tr"),   FSxSTR("pl tr"),  FSxSTR("pl tr"),                0},
    {FSxSTR("tel"),  FSxSTR("pl ad"),  FSxSTR("pl ad"),   FSxSTR("pl ad"),  FSxSTR("pl ad"),                0},
    {FSxSTR("tele"),FSxSTR("pl all"),  FSxSTR("pl all"), FSxSTR("pl all"), FSxSTR("pl all"),                0},
    {FSxSTR("telt"),FSxSTR("pl abl"),  FSxSTR("pl abl"), FSxSTR("pl abl"), FSxSTR("pl abl"),                0},
    {FSxSTR("tena"), FSxSTR("pl es"),  FSxSTR("pl es"),   FSxSTR("pl es"),  FSxSTR("pl es"),                0},
    {FSxSTR("teni"),FSxSTR("pl ter"),  FSxSTR("pl ter"), FSxSTR("pl ter"), FSxSTR("pl ter"),                0},
    {FSxSTR("tes"),  FSxSTR("pl in"),  FSxSTR("pl in"),   FSxSTR("pl in"),  FSxSTR("pl in"),                0},
    {FSxSTR("tesse"),FSxSTR("pl ill"), FSxSTR("pl ill"), FSxSTR("pl ill"), FSxSTR("pl ill"),                0},
    {FSxSTR("test"), FSxSTR("pl el"),  FSxSTR("pl el"),   FSxSTR("pl el"),  FSxSTR("pl el"),                0},
    {FSxSTR("teta"), FSxSTR("pl ab"),  FSxSTR("pl ab"),   FSxSTR("pl ab"),  FSxSTR("pl ab"),                0},
    };

static  FSxC2 ne_lopp_ja_vorm[] =    //line, lane jms
{
    {FSxSTR("ne"),    FSxSTR("sg n")},
    {FSxSTR("se"),    FSxSTR("sg g")},
    {FSxSTR("sed"),   FSxSTR("pl n")},
    {FSxSTR("sega"),  FSxSTR("sg kom")},
    {FSxSTR("seid"),  FSxSTR("pl p")},
    {FSxSTR("seks"),  FSxSTR("sg tr")},
    {FSxSTR("sel"),   FSxSTR("sg ad")},
    {FSxSTR("sele"),  FSxSTR("sg all")},
    {FSxSTR("selt"),  FSxSTR("sg abl")},
    {FSxSTR("sena"),  FSxSTR("sg es")},
    {FSxSTR("seni"),  FSxSTR("sg ter")},
    {FSxSTR("ses"),   FSxSTR("sg in")},
    {FSxSTR("sesse"), FSxSTR("sg ill")},
    {FSxSTR("sest"),  FSxSTR("sg el")},
    {FSxSTR("seta"),  FSxSTR("sg ab")},
    {FSxSTR("si"),    FSxSTR("pl p")},
    {FSxSTR("siks"),  FSxSTR("pl tr")},
    {FSxSTR("sil"),   FSxSTR("pl ad")},
    {FSxSTR("sile"),  FSxSTR("pl all")},
    {FSxSTR("silt"),  FSxSTR("pl abl")},
    {FSxSTR("sis"),   FSxSTR("pl in")},
    {FSxSTR("sisse"), FSxSTR("pl ill")},
    {FSxSTR("sist"),  FSxSTR("pl el")},
    {FSxSTR("st"),    FSxSTR("sg p")},
    {FSxSTR("ste"),   FSxSTR("pl g")},
    {FSxSTR("stega"), FSxSTR("pl kom")},
    {FSxSTR("steks"), FSxSTR("pl tr")},
    {FSxSTR("stel"),  FSxSTR("pl ad")},
    {FSxSTR("stele"), FSxSTR("pl all")},
    {FSxSTR("stelt"), FSxSTR("pl abl")},
    {FSxSTR("stena"), FSxSTR("pl es")},
    {FSxSTR("steni"), FSxSTR("pl ter")},
    {FSxSTR("stes"),  FSxSTR("pl in")},
    {FSxSTR("stesse"),FSxSTR("pl ill")},
    {FSxSTR("stest"), FSxSTR("pl el")},
    {FSxSTR("steta"), FSxSTR("pl ab")},
};

extern "C" // m�ned v�rdlusfunktsioonid
    {
    int FSxC2Srt(const void *ee1, const void *ee2 )// vajalik sortimiseks
        {
        //const FSxC2 *e1=(const FSxC2 *)ee1, *e2=(const FSxC2 *)ee2;
        const FSxC2 *e1=*(const FSxC2 **)ee1, *e2=*(const FSxC2 **)ee2;
        return FSStrCmpW0( e1->lopp, e2->lopp);
        }
    int FSxC2Bs(const void *ee1, const void *ee2 )// vajalik 2ndotsimiseks
        {
        //const FSxC2   *e2=(const FSxC2   *)ee2;
        const FSxC2   *e2=*(const FSxC2 **)ee2;
        const FSxCHAR *e1=(const FSxCHAR *)ee1; 
        return FSxSTRCMP( e1, e2->lopp);
        }
    int FSxC6Srt(const void *ee1, const void *ee2 )// vajalik sortimiseks
        {
        //const FSxC6 *e1=(const FSxC6 *)ee1, *e2=(const FSxC6 *)ee2;
        const FSxC6 *e1=*(const FSxC6 **)ee1, *e2=*(const FSxC6 **)ee2;
        return FSxSTRCMP( e1->lopp, e2->lopp);
        }
    int FSxC6Bs(const void *ee1, const void *ee2 )// vajalik 2ndotsimiseks
        {
        //const FSxC6   *e2=(const FSxC6   *)ee2;
        const FSxC6   *e2=*(const FSxC6   **)ee2;
        const FSxCHAR *e1=(const FSxCHAR *)ee1; 
        return FSxSTRCMP( e1, e2->lopp);
        }
    }

NLOPUD::NLOPUD(void)
    {
    lnd1.Start(lopp_ja_vormid, sizeof(lopp_ja_vormid)/sizeof(FSxC6), FSxC6Srt,FSxC6Bs);
    lnd2.Start(ne_lopp_ja_vorm, sizeof(ne_lopp_ja_vorm)/sizeof(FSxC2), FSxC2Srt,FSxC2Bs);
    }

/*  pole tegelt vaja HJK 24.09.2004
static  FSxC01 mark_ja_liik[] =    //kui on yksik m�rk ja tahaks liigitada...
{
    { (FSxCHAR)'-', FSxSTR("Z")},
    { (FSxCHAR)'&', FSxSTR("J")},
};
extern "C" // m�ned v�rdlusfunktsioonid
    {
    int FSxC01Srt(const void *ee1, const void *ee2 )// vajalik sortimiseks
        {
        FSxC01 *e1=(FSxC01 *)ee1, *e2=(FSxC01 *)ee2;
        return TaheHulgad::FSxCHCMP(e1->mark,e2->mark);
        }

    int FSxC01Bs(const void *ee1, const void *ee2 )// vajalik 2ndotsimiseks
        {
        FSxCHAR  *e1=(FSxCHAR *)ee1; 
        FSxC01   *e2=(FSxC01   *)ee2;
        return TaheHulgad::FSxCHCMP( *e1, e2->mark);
        }

    }
*/
/*  pole tegelt vaja HJK 24.09.2004
MARK::MARK(void)
    {
    lnd.Start(mark_ja_liik, sizeof(mark_ja_liik)/sizeof(FSxC01), FSxC01Srt,FSxC01Bs);
    }
*/


