
#if !defined(MITTESONA_H)
#define MITTESONA_H

// 13.05.2002

#include <stdlib.h>
//=========================================================
#include "mrflags.h"
#include "post-fsc.h"
#include "tloendid.h"


typedef struct // teeme n��d selliste struktuuride massiivi
    {
    const FSxCHAR* lopp;
    const FSxCHAR* nda_vorm;
    const FSxCHAR* lyh_vorm;
    const FSxCHAR* ns_vorm;
    const FSxCHAR* pn_vorm;
    const FSxCHAR* nr_vorm;
    } FSxC6;

typedef struct // kui on aint lopp ja vorm
    {
    const FSxCHAR* lopp;
    const FSxCHAR* vorm;
    } FSxC2;

class NLOPUD
    {
    public:
        NLOPUD(void);

        //LOEND<FSxC6,  FSxCHAR *> lnd1;
        //LOEND<FSxC2,  FSxCHAR *> lnd2;
        CLOEND<FSxC6,  FSxCHAR> lnd1;
        CLOEND<FSxC2,  FSxCHAR> lnd2;

        const FSxCHAR *otsi_lyh_vorm(const FSxCHAR *lvorm) const
            {
            const FSxC6 *rec=lnd1.Get(lvorm); //(FSxCHAR *)(const FSxCHAR *lvorm)

            return rec ? rec->lyh_vorm : NULL;
            }
        const FSxCHAR *otsi_nda_vorm(const FSxCHAR *lvorm) const
            {
            const FSxC6 *rec=lnd1.Get(lvorm); //(FSxCHAR *)(const FSxCHAR *lvorm)

            return rec ? rec->nda_vorm : NULL;
            }
        const FSxCHAR *otsi_ns_vorm(const FSxCHAR *lvorm) const
            {
            const FSxC6 *rec=lnd1.Get(lvorm); //(FSxCHAR *)(const FSxCHAR *lvorm)

            return rec ? rec->ns_vorm : NULL;
            }
        const FSxCHAR *otsi_pn_vorm(const FSxCHAR *lvorm) const
            {
            const FSxC6 *rec=lnd1.Get(lvorm); //(FSxCHAR *)(const FSxCHAR *lvorm)

            return rec ? rec->pn_vorm : NULL;
            }
        const FSxCHAR *otsi_nr_vorm(const FSxCHAR *lvorm) const
            {
            const FSxC6 *rec=lnd1.Get(lvorm); //(FSxCHAR *)(const FSxCHAR *lvorm)

            return rec ? rec->nr_vorm : NULL;
            }
        const FSxCHAR *otsi_ne_vorm(const FSxCHAR *lvorm) const
            {
            const FSxC2 *rec=lnd2.Get(lvorm); //(FSxCHAR *)(const FSxCHAR *lvorm)

            return rec ? rec->vorm : NULL;
            }
    };

typedef struct // kui on mingi imem�rk ja s�naliik
    {
    FSxCHAR  mark;
    FSxCHAR* sonaliik;
    } FSxC01;

/*  pole tegelt vaja HJK 24.09.2004
class MARK
    {
    public:
        MARK(void);

        LOEND<FSxC01, FSxCHAR *> lnd;
        
        inline FSxCHAR *otsi_sonaliik(const FSxCHAR *mark) const
            {
            FSxC01 *rec=lnd.Get((FSxCHAR *)mark); //(FSxCHAR *)(const FSxCHAR *lvorm)

            return rec ? rec->sonaliik : NULL;
            };

    };

*/
#endif



