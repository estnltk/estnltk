#if !defined(ADHOC_H)
#define ADHOC_H

// 17.05.2002

//=========================================================
#include "mrflags.h"
#include "post-fsc.h"
#include "sloendid.h"

/// AD HOC loendid
class AD_HOC
    {
    public:
        AD_HOC(void);

        CLOEND<FSxC5,  FSxCHAR> sonad; //TMPLPTRARRAYBIN<CFSxC5,  FSxCHAR> sonad; //LOEND<FSxC5,  FSxCHAR *> sonad;
        //LOEND<FSxC1,  FSxCHAR *> verbilopud;
        //KLOEND<FSxI2C5I1C4,  FSxCHAR *> vormid;

        CLOEND<FSxC1, FSxCHAR> verbilopud; ///< m�ned adhoc verbilopud
        CKLOEND<FSxI2C5I1C4,  FSxCHAR> vormid;
    };

#endif
