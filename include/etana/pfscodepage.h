
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

