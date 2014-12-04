
#if !defined(TULEM_H)
#define TULEM_H

// 17.05.2002

#include <stdlib.h>
//=========================================================
#include "mrflags.h"
#include "post-fsc.h"
#include "tloendid.h"
#include "cxxbs3.h"
#include "puhasta.h"

#define ENDLEN      10   //* s�na l�pu max pikkus                    *
#define STEMLEN     40  //* peab olema == tmk2tx.h/TYVE_MAX_PIKKUS  *
#define VORMIDLEN   40  //* tulemuse vorminimede stringi max pikkus *

typedef struct S_TUL
    {
	struct S_TUL *tul_jargmine;
	struct S_TUL *tul_eelmine;
    char tyvi[3*STEMLEN];   // 3-osaliste geonimede & palakr�nksude mahutamiseks
    char lopp[ENDLEN];    
    char sl[2];             // s�naliigistring (st alati sl[1]=='\0')
    char vormid[VORMIDLEN]; // suvaline pikkus valitud 
    } TUL;  // nov. 2000 HJK: sona analyysi tulemus, 
            // millest saab lihtsalt va'ljundstringi teha 

// need k�sitlevad morf anal��si tulemuste struktuuri 
// kommentaarid puudu :-(((


class TULEM : public PUHASTA
    {
    public:
//        TULEM(void) {};
        TULEM(void)
            { 
            t = NULL;
            tul = &t;
            };
        TUL *t;
        TUL **tul;

                                        
/*
        void Finish(TUL **tul) // m�lu vabaks ja  pood kinni
            {
            tul_vabaks(tul);
            };
*/

        ~TULEM(void) {tul_vabaks();};

        int on_juba(
//            TUL **tul, 
            char *tyvelp, 
            char *lopp, 
            char *sl, 
            char *vormid);

        int lopu_taha( 
//            TUL **tul, 
            char *ki );

        void lisa_1tulem(
//            TUL **tul, 
            char *tyvi, 
            char *lopp, 
            char *sl, 
            char *vormid);

        void kopeeri_tul(
//            TUL **kuhu_tul, 
            TUL **kust_tul);

        void tul_vabaks();
//            TUL **tul);

        void tulem_struktuuri(
//            TUL **tul, 
            char *sl, 
            char *S6na );

        int  tyve_ette( 
//            TUL **tul, 
            char *ette );

        void lisa_tulemid(
//            TUL **tul, 
            int tyvesid, 
            char *lp, 
            char *sl, 
            char *vormid);

        int  on_tulemis_sl(
//            TUL **tulemus, 
            char *sl);

        int  on_tulemis_vorm(
//            TUL **tulemus, 
            char *vorm);

        int  on_tulemis_lopp(
//            TUL **tulemus, 
            char *lopp);

        int  tulemist_tyvi_jm(
            char *tyvi, 
            char *lopp, 
            char *sl, 
            char *vorm, 
//            TUL **tulemus, 
            int nr);

        void sh_korda(void);

        void valjatr( 
//            TUL **tul, 
            char *str );

        void tulemid_nimeks( 
//            TUL **tul,
            char *alg_sl_hulk);

//        void tyvi_nimeks(char *tyvi);
        int on_tulem(void);

        void pane_tulemus(
            TUL *tul, 
            char *tyvi, 
            char *lopp, 
            char *sl, 
            char *vormid);

    
};



#endif  
