/*
Copyright 2015 Filosoft OÜ

This file is part of Estnltk. It is available under the license of GPLv2 found
in the top-level directory of this distribution and
at http://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html .
No part of this file, may be copied, modified, propagated, or distributed
except according to the terms contained in the license.

This software is distributed on an "AS IS" basis, without warranties or conditions
of any kind, either express or implied.
*/
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
