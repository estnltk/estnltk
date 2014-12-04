
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
