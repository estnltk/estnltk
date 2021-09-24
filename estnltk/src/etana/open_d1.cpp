/*
Copyright 2015 Filosoft OÜ

This file is part of Estnltk. It is available under the license of GPLv2 found
in the top-level directory of this distribution and
at http://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html .
No part of this file, may be copied, modified, propagated, or distributed
except according to the terms contained in the license.

This software is distributed on an "AS IS" basis, without warranties or conditions
of any kind, either express or implied.
*/// (C) AS Filosoft 1994-1996
// 2002.03.19 klass �mberv��natud

#include "cxxbs3.h" 
#include "viga.h"


void DCTRD::open_d1( //==0:ok; ==-1:jama,vtErrNo()
    const CFSFileName *dct_file)
	{
    // avab s�nastikufaili ja 
    // loeb sisse s6nastiku-infobloki
    ReadFileInfo(dct_file);
    //TODO::kunagi tee �mber
    // nii inetu, et ei k�lba karup...e ka
    // aga niimodi saab kudagi tehtud
    if(tyveMuutused.Start(file_info.tyveL6ppudeAlgus,&dctFile)==false)
        {
        throw(VEAD(ERR_MORFI_PS6N, ERR_MINGIJAMA, __FILE__, __LINE__, "$Revision: 521 $"));
        }
    if(LISAKR6NKSUD1::Start(this)==false) // pol�morfism: this --> (cFILEINFO *)
        {
        throw(VEAD(ERR_MORFI_PS6N, ERR_MINGIJAMA, __FILE__, __LINE__, "$Revision: 521 $"));
        }
	}
