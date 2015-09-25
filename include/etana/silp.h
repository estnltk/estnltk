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
#if !defined( SILP_H )
    #define SILP_H

    #include "fsxstring.h"
    #include "tloendid.h"
    #include "tmplptrsrtfnd.h"

    class SILBISTR
        {
        public:
            FSXSTRING silp;
            int valde;
            int rohk;

            SILBISTR(void) {};
            void Start(const SILBISTR& silbiStr)
                {
                silp=silbiStr.silp;
                valde=silbiStr.valde;
                rohk=silbiStr.rohk;
                }
        };

    class SILP
        {
        public:
            SILP(void)
                {
                InitEmptyClassVariables();
                }
            ~SILP()
                {
                }
            TMPLPTRARRAY<SILBISTR> silbid;
            inline int silpe(void) const // silpide arv
                {
                return silbid.idxLast;
                }
            //int silbita(FSXSTRING *S6na, SILBISTR *silbid);
            int silbita(const FSXSTRING *S6na);
            void silbivalted(void);
            int silbis_vv(const FSXSTRING *silp);
            int viimane_rohuline_silp(void);


            bool EmptyClassInvariant(void) const
                {
                return silpe()==0;
                }
            bool ClassInvariant(void) const
                {
                return silpe()>=0;
                }

        private:    
            SILP(const SILP&) { assert( false ); }
            SILP& operator=(const SILP&) { assert(false);  return *this; }

            int on_voorvokjada(const FSXSTRING *S6na);
            int on_dift_vahe(const FSXSTRING *S6na);
            bool InitEmptyClassVariables(void)
                {
                silbid.Start(5,5);
                assert(EmptyClassInvariant());
                return true;
                }
        };
#endif
