
#ifndef CxxCASH_H
    #define CxxCASH_H
    #define CASH0

    #include "post-fsc.h"
    #include "tyybid.h"

    #define MIN_CASH_SIZE 23    // h�sh-tabeli min pikkus
    #define MIN_BUFFERS   17
    #define VABA          -1    // puhver on tyhi

    #if defined( CASH0 )    //===========================================

        /// Cache'i poolt k�ideladav puhver
	    typedef struct STRUCT_CASH
		    {
		    int   index;	        ///< Puhvri indeks
		    unsigned char *buffer;  ///< Puhver
		    } CASH;

        /// Cache Cooperdatud s�nastikublokkide lugemiseks
        class cCACHE
            {
            public:
                cCACHE(void);
                ~cCACHE(void);

                /// Initsialiseerib cache'i
                //
                /// @return
                /// - @a ==0 OK
                /// - @a ==1 Jama
                int CacheOpen(
                    const int DBSIZE,   ///< Bloki suurus tuleb FILE_INFO struktuurist
	                const int nBlokki   ///< See cache'i versioon ei kasuta seda muutujat
                    );

                /// Loeb cache'ist
                //
                /// @return
                /// - @a ==0 OK
                /// - @a ==-1 Jama
                int CacheRead(
                    CPFSFile *pDctFile, ///< S�nastikufail
                    const int idx       ///< Loetava bloki indeks
                    );
                
                void CacheClose(void);
            
                unsigned char* xptr;     ///< Jooksva bloki algus

            private:
                CASH *dbuf;             ///< Jooksev blokk
                int DBSIZE;             ///< Bloki suurus
                int ClassInvariant(void);
            };

    #elif defined( CASH1 )  //===========================================
        // CASH_SIZE == H�sh-tabeli pikkus.
        // Soovitus: H�sh-tabeli pikkus olgu algarv.
        
        typedef struct STRUCT_CACHE
	        {
	        int   index;	// puhvri indeks
	        char *buffer;	// puhver
	        } S_CACHE;
    
        class C_CACHE
            {
            public:
                C_CACHE(void);
                ~C_CACHE(void);
                int CacheOpen(
                    const int DBSIZE,     // bloki suurus tuleb FILE_INFOst
	                const int nBlokki);

                int CacheRead(
                    const int dfd, 
                    int blockNo);

                int CacheClose(void);

            protected:

            private:
                RESULT CacheSize(int cacheSize);

                int CACHE_SIZE;      // h�sh tabeli pikkus, soovit. algarv
                char *cBuf;
                S_CACHE *cache;
            };

    #elif defined( CASH2 )  //===========================================

        typedef struct STRUCT_CASH
            {
            struct STRUCT_CASH
		            *chn_next, // puhvrite 
		            *chn_prev, //         aheldamiseks
		            *hsh_next, // h�sh-tabelis
		            *hsh_prev; //	p�rgete lahendamiseks
            int   index;	   // puhvris asuva bloki nr
            char *buffer;	   // puhver
            } S_CASH;

        class C_CACHE
            {
            public:
                C_CACHE(void);
                ~C_CACHE(void);
                RESULT CacheOpen(int cacheSize);
                RESULT CacheRead(int blockNo);
                void   CacheClose(void);

            protected:

            private:
                RESULT CacheSize(int cacheSize);

                void ChnInsert(	    // lisame ahelasse c2-e c1-e j�rele
	                S_CASH *c1,	    // selle j�rele tuleb lisada
	                S_CASH *c2);    // uus ahela l�li
            
                void ChnDelete(
                    S_CASH *c);

                int CACHE_SIZE;      // h�sh tabeli pikkus, soovit. algarv
                int N_BUFFERS;      // puhvrite arv, soovit. 75% h�sh tabeli pikkusest
                char *cBuf;
                S_CASH *sBuf;
                S_CASH **cash;
                S_CASH *chnLst;

                int KordArv(int arv);
            };
    #else
        #error CASH0, CASH1 or CASH2 must be defined.
    #endif
#endif



