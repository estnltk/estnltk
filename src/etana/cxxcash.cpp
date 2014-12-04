
#include "cxxcash.h"

#ifdef CASH0 //==see on praegu kasutusel=======================================


    cCACHE::cCACHE(void)
        {
        xptr=NULL;
        dbuf=NULL;
        DBSIZE=0;
        }

    int cCACHE::CacheOpen( 
        const int _DBSIZE_,
	    const int nBlokki // see CACHEi versioon ei kasua seda muutuja, selleks et oleks teistega kompatiibel
        )
	    {
		FSUNUSED(nBlokki);
        assert( (_DBSIZE_ % 256)==0 ); // peab olema n*256

        xptr=NULL;
        dbuf=NULL;
        DBSIZE=_DBSIZE_;
        dbuf = (struct STRUCT_CASH *)(malloc(sizeof(CASH) + DBSIZE)); // see malloc on OK
	    if(dbuf==NULL)
		    {
            assert( ClassInvariant() );
		    return 1;
		    }
	    dbuf->index = VABA;
	    dbuf->buffer = (unsigned char *)(dbuf+1);   // MIS KURAT SEE VEEL ON?
                                                    // ahaa, vt �lal m�lureserveerimist
        assert( ClassInvariant() );
	    return 0;
	    }
                            
    int cCACHE::CacheRead(
        CPFSFile *pDctFile,
        const int idx) 
	    {
        assert( pDctFile != NULL );

	    if(dbuf->index != idx)
		    {
		    //polnud m@lus - loeme kettalt dbuf'i
            if(pDctFile->Seek((long)idx * (long)DBSIZE)==false)
			    {
                assert( ClassInvariant() );
	            return -1;
			    }
		    if(pDctFile->ReadBuffer(dbuf->buffer, DBSIZE)==false)
			    {
			    dbuf->index = VABA;	// puhver tyhi...
                xptr=NULL;

                assert( ClassInvariant() );
			    return -1;    // ... lugemine eba6nnestus
			    }
		    dbuf->index = idx;
		    }
	    xptr = dbuf->buffer;
    #ifdef STEM_NO
		    stem_no = 1;
    #endif
        assert( ClassInvariant() );
	    return 0;
	    }

    void cCACHE::CacheClose(
	    void)
	    {
        if(dbuf)
            {
            free(dbuf); 
            dbuf=NULL;
            }
        xptr=NULL;
	    }

    cCACHE::~cCACHE(void)
        {
        CacheClose();
        }

    int cCACHE::ClassInvariant(void)
        {
        return
            (dbuf==NULL && xptr==NULL) ||
            (dbuf!=NULL && xptr==NULL && dbuf->index==VABA) ||
            (dbuf!=NULL && xptr!=NULL && dbuf->index>=0);
        }

// }}=cxxcash-0

#elif defined( CASH1 ) //================================================

    C_CACHE *morfCache=NULL;

    RESULT cXXcash_open(int prots)
        {
        morfCache=new C_CACHE;
        return morfCache->CacheOpen(prots);
        }

    RESULT cXXcash(const int index)
        {
        return morfCache->CacheRead(index);
        }

    void cXXcash_close(void)
        {
        if(morfCache)
            {
            morfCache->CacheClose();
            delete morfCache;
            morfCache=NULL;
            }
        }

    // public:
    C_CACHE::C_CACHE(void)
        {
        CACHE_SIZE = 1;
        cBuf=NULL;
        cache=NULL;
        }

    // public:
    C_CACHE::~C_CACHE(void)
        {
        CacheClose();    
        }

    // public:
    RESULT C_CACHE::CacheOpen(int cacheSize) /* reserveerib m�lu */
	    {
	    int n=0;
	    char *ptr;
        RESULT res;

        if((res=CacheSize(cacheSize))!= ALL_RIGHT)
            {
            return res;
            }
        cBuf = new char[CACHE_SIZE*DBSIZE];
        ptr = cBuf;          // viit puhvrile
	    for(n = 0; n < CACHE_SIZE; n++)
		    {
            cache[n].index    = VABA; // puhver t�hi
            cache[n].buffer   = ptr;  // viit puhvrile
	        ptr += DBSIZE;
		    }
        return ALL_RIGHT;
	    }

    // public:
    RESULT C_CACHE::CacheRead(
	    int blkNo)
	    {
	    register int h = blkNo % CACHE_SIZE;
        S_CACHE *dbuf;
	    // Otsime vastavast h�sh-tabeli ahelast.

        dbuf=cache+h;
	    if(dbuf->index==blkNo)
            {
		    xptr = dbuf->buffer;
		    return ALL_RIGHT;
		    }
	    // Polnud h�sh-tabeli  vastavas  ahelas,
	    // liigume failis otsitava bloki kohale.

	    if(lseek(dfd, blkNo * DBSIZE, SEEK_SET) == -1L)
		    {
		    // Polnud blokki nr. idx - viga!

		    return ILL_SEEK;
		    }

	    // Loeme kettalt bloki puhvrisse ja ...

	    if(read(dfd, dbuf->buffer, DBSIZE) == -1)
		    {
		    // lugemine eba�nnestus, puhver j��b ...

		    dbuf->index = VABA;		// ... vabaks	
		    return ILL_READ;
		    }
	    // ... blokk �nnelikult m�llu loetud ... 

	    xptr = dbuf->buffer;
	    dbuf->index = blkNo;	// Uus bloki nr.

	    // ... ja lisame h�sh-tabelisse vastava ahela algusesse

	    return ALL_RIGHT;
	    }

    // public:
    void C_CACHE::CacheClose(void) // vabastab m�lu ja sulgeb faili
	    {
	    if(cache != NULL)
            delete [] cache;
        if(cBuf != NULL)
            delete [] cBuf;
	    }

    // private:
    RESULT C_CACHE::CacheSize(
        int cacheSizeProts) 
	    {
        int sadaProtsBuffe = ps.ktSuurus;

        if(cacheSizeProts <= 0)
            {
            return ALL_RIGHT;
            }
	    CACHE_SIZE = sadaProtsBuffe * cacheSizeProts / 100;
	    return ALL_RIGHT ;
	    }


#elif defined( CASH2 ) //================================================
// cxxcash2-{{

#include <f-info.h>

    C_CACHE *morfCache=NULL;
    
    RESULT cXXcash_open(int prots)
        {
        morfCache=new C_CACHE;
        return morfCache->CacheOpen(prots);
        }

    RESULT cXXcash(const int index)
        {
        return morfCache->CacheRead(index);
        }

    void cXXcash_close(void)
        {
        if(morfCache)
            {
            morfCache->CacheClose();
            delete morfCache;
            morfCache=NULL;
            }
        }

    // public:
    C_CACHE::C_CACHE(void)
        {
        N_BUFFERS = MIN_BUFFERS;
        CACHE_SIZE = MIN_CASH_SIZE;
        sBuf=NULL;
        cBuf=NULL;
        cash=NULL;
        chnLst=NULL;
        }

    // public:
    C_CACHE::~C_CACHE(void)
        {
        CacheClose();    
        }

    // private:
    int C_CACHE::KordArv(
	    int arv)
        {
	    int x;

	    for(x = arv - 1; x > 1; x--)
		    {
		    if(arv % x == 0)
			    {
			    return x; // Arv jagub x-ga.
			    }
		    }

	    return 0; // Arv jagub ainult 1-he ja iseendaga.
	    }

    /** cXXcash_size ****************************************************
    */

    // private:
    RESULT C_CACHE::CacheSize(
        int cacheSizeProts) 
	    {
        int sadaProtsBuffe = ps.ktSuurus;

        if(cacheSizeProts <= 0)
            {
            return ALL_RIGHT;
            }
	    if((N_BUFFERS = sadaProtsBuffe * cacheSizeProts / 100) < MIN_BUFFERS)
            {
            N_BUFFERS = MIN_BUFFERS;
            }
        CACHE_SIZE = 100 * N_BUFFERS / 75;
	    if(CACHE_SIZE < MIN_CASH_SIZE)
		    {
		    CACHE_SIZE = MIN_CASH_SIZE;
		    }
        // tv-270496-{{

	    //while(CACHE_SIZE > MIN_CASH_SIZE && KordArv(CACHE_SIZE))
		//    {
		//    CACHE_SIZE--;
		//    }
	    while(KordArv(CACHE_SIZE))
		    {
		    CACHE_SIZE++;
		    }
        // }}-tv-270496

	    return ALL_RIGHT ;
	    }

    /** cXXcash_open ****************************************************

    Antud:
    ******	DFNAME    == viit faili nimele
	    DBSIZE    == puhvri suurus
	    cash      == h�sh-tabel
	    CASH_SIZE == h�sh-tabeli pikkus
	    N_BUFFERS == puhvrite arv ahelas

    Tulem:
    ******	kui   cXXcash == ALL_RIGHT
		    cash    == puhvritega seotud info h�sh tabel
		    chn_lst == viit viimati kasutatud puhvriga seotud infole
	    muidu cXXcash == vastava veakoodiga
    */

    // public:
    RESULT C_CACHE::CacheOpen(int cacheSize) /* reserveerib m�lu */
	    {
	    int n=0;
	    char *ptr;
        RESULT res;

        if((res=CacheSize(cacheSize))!= ALL_RIGHT)
            {
            return res;
            }
        cBuf = new char[N_BUFFERS*DBSIZE];

	    for(n = 0; n < CACHE_SIZE; n++)
		    {
		    cash[n] = NULL;     // H�sh-tabelis pole �htegi puhvrit.
		    }
	    
        sBuf[0].chn_prev = sBuf+N_BUFFERS-1;    // esimesele eelneb viimane
        sBuf[0].index    = VABA;	            // puhver t�hi
	    sBuf[0].hsh_next = sBuf[0].hsh_prev = NULL;
        sBuf[0].buffer   = ptr = cBuf;          // viit puhvrile
	    ptr += DBSIZE;

	    for(n = 1; n < N_BUFFERS; n++)
		    {
            sBuf[n-1].chn_next = sBuf+n;
            sBuf[n].chn_prev = sBuf+n-1;
            sBuf[n].index    = VABA;	// puhver t�hi
	        sBuf[n].hsh_next = sBuf[n].hsh_prev = NULL;
            sBuf[n].buffer   = ptr;  // viit puhvrile
	        ptr += DBSIZE;
		    }
        sBuf[N_BUFFERS-1].chn_next = sBuf; // viimasele j�rgneb esimene
        chnLst=sBuf;

        return ALL_RIGHT;
	    }

    /** r�ngasahelast l�li eemaldamine **********************************/

    // private:
    void C_CACHE::ChnDelete(
        S_CASH *c)
        {
        c->chn_prev->chn_next = c->chn_next;
        c->chn_next->chn_prev = c->chn_prev;
        }

    /** r�ngas-ahelasse l�li lisamine ***********************************/

    // private:
    void C_CACHE::ChnInsert(	// lisame ahelasse c2-e c1-e j�rele
	    S_CASH *c1,	            // selle j�rele tuleb lisada
	    S_CASH *c2) 	        // uus ahela l�li
	    {
	    S_CASH *c3 = c1->chn_next;

	    c1->chn_next = c2;
	    c2->chn_prev = c1;
	    c2->chn_next = c3;
	    c3->chn_prev = c2;
	    }


    /** cXXcash *********************************************************

    Antud:
    ******  idx       == otsitava bloki nr
	    cash      == h�sh-tabel
	    CASH_SIZE == h�sh-tabeli pikkus
	    chn_lst   == viit infole, mis on seotud viimati kasutatud puhvriga
	    DBSIZE    == puhvri suurus
	    dfd       == sisendfailideskriptor

    Tulem:
    ******	kui   cXXcash == ALL_RIGHT
		    dbuf == viit blokki nr idx sisaldavle k�shi elemendile
		    xptr == viit blokki nr idx sisaldavale puhvrile
	    muidu cXXcash == vastava veakoodiga
    */

    // public:
    RESULT C_CACHE::CacheRead(
	    int blkNo)
	    {
	    register int h = blkNo % CACHE_SIZE;
        S_CASH *dbuf;
	    // Otsime vastavast h�sh-tabeli ahelast.

	    for(dbuf = cash[h]; dbuf != NULL; dbuf = dbuf->hsh_next)
		    {
		    if(dbuf->index == blkNo)
			    {
			    // Otsitav blokk h�shtabeli vastavas ahelas olemas,
                // t�stame  ta  r�ngasahela  l�ppu.

			    ChnDelete(dbuf);	        // eemaldame
			    ChnInsert(chnLst, dbuf);    // lisame ... 
			    chnLst = dbuf;              //   ... l�ppu 

			    xptr = dbuf->buffer;
			    return ALL_RIGHT;
			    }
		    }
	    // Polnud h�sh-tabeli  vastavas  ahelas,
	    // liigume failis otsitava bloki kohale.

	    if(lseek(dfd, blkNo * DBSIZE, SEEK_SET) == -1L)
		    {
		    // Polnud blokki nr. idx - viga!

		    return ILL_SEEK;
		    }

	    // V�tame sellise blokiga puhvri,
        // mida k�ige kauem pole kasutatud...

	    chnLst = chnLst->chn_next;

	    // ... ja kui ta on h�sh-tabelis, 
        // siis eemaldame ta sealt.

	    if(chnLst->index != VABA)
		    {
		    // chnLst oli chnLst->index-i j�rgi h�sh-tabelis,eemaldame.

		    if(chnLst->hsh_prev)
			    {
			    // eelmine l�li oli olemas, v�tame vahelt v�lja.

			    if((chnLst->hsh_prev->hsh_next =
						    chnLst->hsh_next) != NULL)
				    {
				    // pole viimane

				    chnLst->hsh_next->hsh_prev =
							    chnLst->hsh_prev;
				    }
			    }
		    else
			    {
			    // eelmist polnud, j�rgmine saab esimesks

			    if((cash[chnLst->index % CACHE_SIZE] =
						    chnLst->hsh_next) != NULL)
				    {
				    // pole viimane

				    chnLst->hsh_next->hsh_prev = NULL;
				    }
			    }
		    }
	    // ... ja loeme kettalt bloki puhvrisse ja ...

	    if(read(dfd, chnLst->buffer, DBSIZE) == -1)
		    {
		    // lugemine eba�nnestus, puhver j��b ...

		    chnLst->index = VABA;		// ... vabana ...	
		    chnLst = chnLst->chn_prev;	// ... ahela algusesse	

		    return ILL_READ;
		    }
	    // ... blokk �nnelikult m�llu loetud ... 

	    xptr = chnLst->buffer;
	    dbuf = chnLst;
	    chnLst->index = blkNo;	/* Uus bloki nr. */

	    // ... ja lisame h�sh-tabelisse vastava ahela algusesse

	    chnLst->hsh_prev = NULL;
	    if((chnLst->hsh_next = cash[h]) != NULL)
		    {
		    chnLst->hsh_next->hsh_prev = chnLst;
		    }
	    cash[h] = chnLst;

	    return ALL_RIGHT;
	    }

    /** cXXcash_close ***************************************************

    Antud:
    ******	cash == Viit h�sh-tabelile.

    Tulem:
    ******  Vabastab cash-i ja puhvrite poolt h�ivatud m�lu.
    */

    // public:
    void C_CACHE::CacheClose(void) // vabastab m�lu ja sulgeb faili
	    {
	    if(cash != NULL)
            delete [] cash;
        if(cBuf != NULL)
            delete [] cBuf;
        if(sBuf != NULL)
            delete [] sBuf;
	    }


// }}-cxxcash2

#else
    #error CASH0, CASH1 or CASH2 must be defined.
#endif


