
#include <string.h>
#include "cxxbs3.h"

// Muditud klassindust 2002.kevad
// KOtsi 
//  ==true:  v6ti   oli  kahendtabelis element nr  *idx
//  ==false: v6ti polnud kahendtabelis, lisada *idx-indaks
//
bool cTYVEDETABEL::KOtsi
	(
	const BTABLE  *kt,
	const FSxCHAR *v6ti,
	const int vPikkus,
	int   *idx) const
	{
    ASSERT( vPikkus >=0 && v6ti != NULL);

    int i;
	int v = 0,
	    p = kt->ktSuurus - 1,
	    k = (p - v) / 2,
		n=0;
    if(vPikkus<=0 || v6ti==NULL || *v6ti==FSxSTR("")[0])
        {
        *idx=0;
        return false;
        }
	// Otsime kahendtabelist
    //
	while(v <= p)
		{        
        const FSxCHAR *ptr = kt->v6tmed + kt->kTabel[k].s_nihe;
        int l1=vPikkus;
        int l2=kt->kTabel[k].len;
        int ll=l1 < l2 ? l1 : l2;    
        ASSERT( l1 > 0 && l2 >= 0 && ll >= 0);
        if(ll)
            {
            for(i=0; i < ll && (n=TaheHulgad::FSxCHCMP(v6ti[i], ptr[i]))==0; i++)
                ;
            if(n==0)
                n = l1 - l2;
            }
        else
            {
            n=1; // oli 2ndtabeli 1mene 0pikkusega element
            ASSERT( k==0 &&  kt->kTabel[k].len==0 );
            }
        if(n < 0)
			{
			p = k - 1;      // v6ti < kahendtabeli jooksvast v�tmest
			}
		else if(n > 0)
			{
			v = k + 1;      // v6ti > kahendtabeli jooksvast v�tmest
			}
		else                // n == 0 st oli kahendtabelis
			{
			*idx = k;       // v6ti == kahendtabeli jooksva v�tmega
			return true;    // Leidsin kahendtabelist!
			}
		k = v + (p - v) / 2;
		}
	*idx = v;               // Polnud kahendtabelis.
	return false;
	}

