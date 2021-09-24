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
#include "mrflags.h"
#include "post-fsc.h"


//find_fd == esimese erineva s�mboli index ChToLower()
//        == n, kui esimesed n-1 baiti v�rdsed


int find_fd(
	const FSxCHAR *s1,
	const FSxCHAR *s2,
	const int   n)
	{
	register int i;

	for(i = 0; (i < n) && (s1[i] == s2[i]); i++)
		;
	return i;
	}

int find_diff(
    const FSxCHAR *s1,  // 1mene string
    const int      l1,  // 1mese stringi pikkus
    const FSxCHAR *s2,  // 2ne string 
    const int      l2)  // 2se stringi pikkus
    {
    return find_fd(s1, s2, l1 < l2 ? l1 : l2);
    }
