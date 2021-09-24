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
// (C) 1996-97-2002

#if !defined(MKT2T_H)
#define MKT2T_H

#include "tyybid.h"

/** algvormi tüveindeks
 * selle abil saab ühe paradigma tüved omavahel siduda; vajalik sünteesi puhul
 */
typedef struct
{
    /** grupiNr -- tyvemuutuse grupi nr; sama paradigma tüvedel on see == */
    _int16 tab_idx;  
    /** mitmesGrupis -- mitmes antud grupi sees see tüvi on */
    _uint8 blk_idx; 
} AVTIDX;  

/**
 * info tüve kohta: 
 * millised hääldus- ja piirimärgid, millised võimalikud lõpud, millised tüved samas pardigmas
 */
typedef struct
{
    int piiriKr6nksud; // liitsõnades jm poolituskohad (nt foto_graaf)
    _int16 lg_nr;   // lõpugrupi nr -- millised lõpud sellele tüvele liituvad
    _int16 lisaKr6nksud; // hääldusmärgid
    AVTIDX idx;
} TYVE_INF;


/** kas kaks tüve on ühesugused
 * 
 * @param tyveInf1
 * @param tyveInf2
 * @return
 * <ul><li> @a true Võrdsed
 *     <li> @a false Erinevad
 * </ul> 
 */
bool SamadTYVE_INF(const TYVE_INF& tyveInf1, const TYVE_INF& tyveInf2);

#endif

