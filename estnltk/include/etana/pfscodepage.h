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
#if !defined(PGSCODEPAGE_H)
#define PGSCODEPAGE_H

/** 
 * @file pfscodepage.h
 * Sisend/väljundfaili kooditabeli määramiseks vajalike konstantide loend.
 */

/** 
 * Loend sisend/väljundfaili kooditabeli määramiseks.
 * 
 * Selle loendi elemendid peavad olema kooskõlas failis
 * fsstring.h esitatud loendiga eFSCP
 */
enum PFSCODEPAGE
    {
    PFSCP_UC      = -5,             /**< ==   -5 2baidine UNICODE */
    PFSCP_UTF8    = FSCP_UTF8,      /**< ==   -3 UTF8 */
    PFSCP_HTMLEXT = -4,             /**< ==   -4 HTML-olemite loend failist */
    PFSCP_HTML    = FSCP_HTML,      /**< ==   -2 HTML-olemite loend Renee programmist */
    PFSCP_ACP     = FSCP_ACP,       /**< ==   -1 ASCII */
    PFSCP_SYSTEM  = FSCP_SYSTEM,    /**< ==    0  */
    PFSCP_WESTERN = FSCP_WESTERN,   /**< == 1252 WESTERN */
    PFSCP_BALTIC  = FSCP_BALTIC,    /**< == 1257 WinBaltic */
    };

#endif

