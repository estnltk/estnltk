
// igasugu sonaloendid, mida kasutatakse mitmel pool

#include "mrf-mrf.h"
#include "sloendid.h"
#if defined( FSCHAR_UNICODE )   // kasutame UNICODE kooditabelit

// oletajas algvormide leidmiseks
static  FSxOTAB _oletaja_tabel_[] =
{
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ich"), FSxSTR(""), 2, 9, FSxSTR("Kranich"),  FSxSTR("H")}, // VVS 2 parisnimi
{0, FSxSTR("i"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("ich"), FSxSTR(""), 2, 9, FSxSTR("Kranich"),  FSxSTR("H")}, // VVS 2 parisnimi
{0, FSxSTR("i"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("ich"), FSxSTR(""), 2, 9, FSxSTR("Kranich"),  FSxSTR("H")}, // VVS 2 parisnimi
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("ich"), FSxSTR(""), 2, 9, FSxSTR("Kranich"),  FSxSTR("H")}, // VVS 2 parisnimi

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("x"), FSxSTR(""), 1, 1, FSxSTR("multiplex"),  FSxSTR("S")}, // VVS tyyp 22 
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("x"), FSxSTR(""), 1, 1, FSxSTR("multiplex"),  FSxSTR("S")}, // VVS tyyp 22 
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("x"), FSxSTR(""), 1, 1, FSxSTR("multiplex"),  FSxSTR("S")}, // VVS tyyp 22 
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("x"), FSxSTR(""), 1, 1, FSxSTR("multiplex"),  FSxSTR("S")}, // VVS tyyp 22 
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("x"), FSxSTR(""), 1, 1, FSxSTR("multiplex"),  FSxSTR("S")}, // VVS tyyp 22 
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("x"), FSxSTR(""), 1, 1, FSxSTR("multiplex"),  FSxSTR("S")}, // VVS tyyp 22 

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("x"), FSxSTR(""), 3, 9, FSxSTR("multiplex"),  FSxSTR("S")}, // VVS tyyp 22 
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("x"), FSxSTR(""), 3, 9, FSxSTR("multiplex"),  FSxSTR("S")}, // VVS tyyp 22 
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("x"), FSxSTR(""), 3, 9, FSxSTR("multiplex"),  FSxSTR("S")}, // VVS tyyp 22 
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("x"), FSxSTR(""), 3, 9, FSxSTR("multiplex"),  FSxSTR("S")}, // VVS tyyp 22 
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("x"), FSxSTR(""), 3, 9, FSxSTR("multiplex"),  FSxSTR("S")}, // VVS tyyp 22 
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("x"), FSxSTR(""), 3, 9, FSxSTR("multiplex"),  FSxSTR("S")}, // VVS tyyp 22 

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("x"), FSxSTR(""), 2, 2, FSxSTR("spandex"),  FSxSTR("S")}, // VVS tyyp 2 
{0, FSxSTR("i"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("x"), FSxSTR(""), 2, 2, FSxSTR("spandex"),  FSxSTR("S")}, // VVS tyyp 2 
{0, FSxSTR("i"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("x"), FSxSTR(""), 2, 2, FSxSTR("spandex"),  FSxSTR("S")}, // VVS tyyp 2 
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("x"), FSxSTR(""), 2, 2, FSxSTR("spandex"),  FSxSTR("S")}, // VVS tyyp 2 

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("x"), FSxSTR(""), 1, 1, FSxSTR("Max"),  FSxSTR("H")}, // VVS tyyp 22 parisnimi
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("x"), FSxSTR(""), 1, 1, FSxSTR("Max"),  FSxSTR("H")}, // VVS tyyp 22 parisnimi
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("x"), FSxSTR(""), 1, 1, FSxSTR("Max"),  FSxSTR("H")}, // VVS tyyp 22 parisnimi
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("x"), FSxSTR(""), 1, 1, FSxSTR("Max"),  FSxSTR("H")}, // VVS tyyp 22 parisnimi
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("x"), FSxSTR(""), 1, 1, FSxSTR("Max"),  FSxSTR("H")}, // VVS tyyp 22 parisnimi
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("x"), FSxSTR(""), 1, 1, FSxSTR("Max"),  FSxSTR("H")}, // VVS tyyp 22 parisnimi

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("x"), FSxSTR(""), 3, 9, FSxSTR("Interfax"),  FSxSTR("H")}, // VVS tyyp 22 parisnimi
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("x"), FSxSTR(""), 3, 9, FSxSTR("Interfax"),  FSxSTR("H")}, // VVS tyyp 22 parisnimi
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("x"), FSxSTR(""), 3, 9, FSxSTR("Interfax"),  FSxSTR("H")}, // VVS tyyp 22 parisnimi
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("x"), FSxSTR(""), 3, 9, FSxSTR("Interfax"),  FSxSTR("H")}, // VVS tyyp 22 parisnimi
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("x"), FSxSTR(""), 3, 9, FSxSTR("Interfax"),  FSxSTR("H")}, // VVS tyyp 22 parisnimi
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("x"), FSxSTR(""), 3, 9, FSxSTR("Interfax"),  FSxSTR("H")}, // VVS tyyp 22 parisnimi

{1, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("kk"), FSxSTR("CV"), 1, 1, FSxSTR("jakk"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("kk"), FSxSTR("CV"), 1, 1, FSxSTR("jakk"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("kk"), FSxSTR("CV"), 1, 1, FSxSTR("jakk"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("kk"), FSxSTR("CV"), 1, 1, FSxSTR("jakk"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("kk"), FSxSTR("CV"), 1, 1, FSxSTR("jakk"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("kk"), FSxSTR("CV"), 1, 1, FSxSTR("jakk"),  FSxSTR("S")}, // VVS tyyp 22

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ll"), FSxSTR("V"), 1, 1, FSxSTR("ball"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("ll"), FSxSTR("V"), 1, 1, FSxSTR("ball"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("ll"), FSxSTR("V"), 1, 1, FSxSTR("ball"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("ll"), FSxSTR("V"), 1, 1, FSxSTR("ball"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("ll"), FSxSTR("V"), 1, 1, FSxSTR("ball"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("ll"), FSxSTR("V"), 1, 1, FSxSTR("ball"),  FSxSTR("S")}, // VVS tyyp 22

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("mm"), FSxSTR("V"), 1, 1, FSxSTR("plomm"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("mm"), FSxSTR("V"), 1, 1, FSxSTR("plomm"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("mm"), FSxSTR("V"), 1, 1, FSxSTR("plomm"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("mm"), FSxSTR("V"), 1, 1, FSxSTR("plomm"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("mm"), FSxSTR("V"), 1, 1, FSxSTR("plomm"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("mm"), FSxSTR("V"), 1, 1, FSxSTR("plomm"),  FSxSTR("S")}, // VVS tyyp 22

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("nn"), FSxSTR("V"), 1, 1, FSxSTR("tonn"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("nn"), FSxSTR("V"), 1, 1, FSxSTR("tonn"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("nn"), FSxSTR("V"), 1, 1, FSxSTR("tonn"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("nn"), FSxSTR("V"), 1, 1, FSxSTR("tonn"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("nn"), FSxSTR("V"), 1, 1, FSxSTR("tonn"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("nn"), FSxSTR("V"), 1, 1, FSxSTR("tonn"),  FSxSTR("S")}, // VVS tyyp 22

{1, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("pp"), FSxSTR("CV"), 1, 1, FSxSTR("klipp"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("pp"), FSxSTR("CV"), 1, 1, FSxSTR("klipp"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("pp"), FSxSTR("CV"), 1, 1, FSxSTR("klipp"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("pp"), FSxSTR("CV"), 1, 1, FSxSTR("klipp"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("pp"), FSxSTR("CV"), 1, 1, FSxSTR("klipp"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("pp"), FSxSTR("CV"), 1, 1, FSxSTR("klipp"),  FSxSTR("S")}, // VVS tyyp 22

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("rr"), FSxSTR("V"), 1, 1, FSxSTR("varr"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("rr"), FSxSTR("V"), 1, 1, FSxSTR("varr"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("rr"), FSxSTR("V"), 1, 1, FSxSTR("varr"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("rr"), FSxSTR("V"), 1, 1, FSxSTR("varr"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("rr"), FSxSTR("V"), 1, 1, FSxSTR("varr"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("rr"), FSxSTR("V"), 1, 1, FSxSTR("varr"),  FSxSTR("S")}, // VVS tyyp 22

{1, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("\x0161\x0161"), FSxSTR("V"), 1, 1, FSxSTR("tu\x0161\x0161"),  FSxSTR("S")}, // VVS tyyp 22 tushsh
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("\x0161\x0161"), FSxSTR("V"), 1, 1, FSxSTR("tu\x0161\x0161"),  FSxSTR("S")}, // VVS tyyp 22 tushsh
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("\x0161\x0161"), FSxSTR("V"), 1, 1, FSxSTR("tu\x0161\x0161"),  FSxSTR("S")}, // VVS tyyp 22 tushsh
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("\x0161\x0161"), FSxSTR("V"), 1, 1, FSxSTR("tu\x0161\x0161"),  FSxSTR("S")}, // VVS tyyp 22 tushsh
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("\x0161\x0161"), FSxSTR("V"), 1, 1, FSxSTR("tu\x0161\x0161"),  FSxSTR("S")}, // VVS tyyp 22 tushsh
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("\x0161\x0161"), FSxSTR("V"), 1, 1, FSxSTR("tu\x0161\x0161"),  FSxSTR("S")}, // VVS tyyp 22 tushsh

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("t\x0161"), FSxSTR("V"), 1, 1, FSxSTR("kit\x0161"),  FSxSTR("S")}, // VVS tyyp 22 kitsh
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("t\x0161"), FSxSTR("V"), 1, 1, FSxSTR("kit\x0161"),  FSxSTR("S")}, // VVS tyyp 22 kitsh
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("t\x0161"), FSxSTR("V"), 1, 1, FSxSTR("kit\x0161"),  FSxSTR("S")}, // VVS tyyp 22 kitsh
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("t\x0161"), FSxSTR("V"), 1, 1, FSxSTR("kit\x0161"),  FSxSTR("S")}, // VVS tyyp 22 kitsh
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("t\x0161"), FSxSTR("V"), 1, 1, FSxSTR("kit\x0161"),  FSxSTR("S")}, // VVS tyyp 22 kitsh
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("t\x0161"), FSxSTR("V"), 1, 1, FSxSTR("kit\x0161"),  FSxSTR("S")}, // VVS tyyp 22 kitsh

{1, FSxSTR("gi"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("k"), FSxSTR("L"), 1, 1, FSxSTR("punk"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("k"), FSxSTR("L"), 1, 1, FSxSTR("punk"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("k"), FSxSTR("L"), 1, 1, FSxSTR("punk"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("k"), FSxSTR("L"), 1, 1, FSxSTR("punk"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("k"), FSxSTR("L"), 1, 1, FSxSTR("punk"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("k"), FSxSTR("L"), 1, 1, FSxSTR("punk"),  FSxSTR("S")}, // VVS tyyp 22

{1, FSxSTR("gi"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("k"), FSxSTR("VV"), 1, 1, FSxSTR("punk"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("k"), FSxSTR("VV"), 1, 1, FSxSTR("punk"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("k"), FSxSTR("VV"), 1, 1, FSxSTR("punk"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("k"), FSxSTR("VV"), 1, 1, FSxSTR("punk"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("k"), FSxSTR("VV"), 1, 1, FSxSTR("punk"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("k"), FSxSTR("VV"), 1, 1, FSxSTR("punk"),  FSxSTR("S")}, // VVS tyyp 22

{1, FSxSTR("gi"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("k"), FSxSTR("VV"), 2, 9, FSxSTR("asteek"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("k"), FSxSTR("VV"), 2, 9, FSxSTR("asteek"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("k"), FSxSTR("VV"), 2, 9, FSxSTR("asteek"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("k"), FSxSTR("VV"), 2, 9, FSxSTR("asteek"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("k"), FSxSTR("VV"), 2, 9, FSxSTR("asteek"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("k"), FSxSTR("VV"), 2, 9, FSxSTR("asteek"),  FSxSTR("S")}, // VVS tyyp 22

{1, FSxSTR("gi"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("k"), FSxSTR("VL"), 3, 9, FSxSTR("katafalk"),  FSxSTR("S")}, // VVS tyyp 22 mk tegelt ei esine
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("k"), FSxSTR("VL"), 3, 9, FSxSTR("katafalk"),  FSxSTR("S")}, // VVS tyyp 22 mk tegelt ei esine
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("k"), FSxSTR("VL"), 3, 9, FSxSTR("katafalk"),  FSxSTR("S")}, // VVS tyyp 22 mk tegelt ei esine
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("k"), FSxSTR("VL"), 3, 9, FSxSTR("katafalk"),  FSxSTR("S")}, // VVS tyyp 22 mk tegelt ei esine
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("k"), FSxSTR("VL"), 3, 9, FSxSTR("katafalk"),  FSxSTR("S")}, // VVS tyyp 22 mk tegelt ei esine
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("k"), FSxSTR("VL"), 3, 9, FSxSTR("katafalk"),  FSxSTR("S")}, // VVS tyyp 22 mk tegelt ei esine

{0, FSxSTR("u"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ak"), FSxSTR(""), 2, 2, FSxSTR("tuustak"),  FSxSTR("S")}, // VVS tyyp 2 
{0, FSxSTR("u"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("ak"), FSxSTR(""), 2, 2, FSxSTR("tuustak"),  FSxSTR("S")}, // VVS tyyp 2 
{0, FSxSTR("u"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("ak"), FSxSTR(""), 2, 2, FSxSTR("tuustak"),  FSxSTR("S")}, // VVS tyyp 2 
{0, FSxSTR("u"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("ak"), FSxSTR(""), 2, 2, FSxSTR("tuustak"),  FSxSTR("S")}, // VVS tyyp 2 

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("sk"), FSxSTR(""), 2, 2, FSxSTR("menisk"),  FSxSTR("S")}, // VVS tyyp 2 
{0, FSxSTR("i"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("sk"), FSxSTR(""), 2, 2, FSxSTR("menisk"),  FSxSTR("S")}, // VVS tyyp 2 
{0, FSxSTR("i"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("sk"), FSxSTR(""), 2, 2, FSxSTR("menisk"),  FSxSTR("S")}, // VVS tyyp 2 
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("sk"), FSxSTR(""), 2, 2, FSxSTR("menisk"),  FSxSTR("S")}, // VVS tyyp 2 

{1, FSxSTR("gi"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("iik"), FSxSTR(""), 1, 9, FSxSTR("antiik"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("iik"), FSxSTR(""), 1, 9, FSxSTR("antiik"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("iik"), FSxSTR(""), 1, 9, FSxSTR("antiik"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("iik"), FSxSTR(""), 1, 9, FSxSTR("antiik"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("iik"), FSxSTR(""), 1, 9, FSxSTR("antiik"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("iik"), FSxSTR(""), 1, 9, FSxSTR("antiik"),  FSxSTR("S")}, // VVS tyyp 22

{0, FSxSTR("u"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ik"), FSxSTR("CVCC"), 2, 2, FSxSTR("rullik"),  FSxSTR("S")}, // VVS tyyp 2 
{0, FSxSTR("u"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("ik"), FSxSTR("CVCC"), 2, 2, FSxSTR("rullik"),  FSxSTR("S")}, // VVS tyyp 2 
{0, FSxSTR("u"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("ik"), FSxSTR("CVCC"), 2, 2, FSxSTR("rullik"),  FSxSTR("S")}, // VVS tyyp 2 
{0, FSxSTR("u"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("ik"), FSxSTR("CVCC"), 2, 2, FSxSTR("rullik"),  FSxSTR("S")}, // VVS tyyp 2 

{0, FSxSTR("u"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ik"), FSxSTR("CCC"), 2, 9, FSxSTR("ristmik"),  FSxSTR("S")}, // VVS tyyp _S_ 25 aga tentsik? tyyp 2
{0, FSxSTR("ku"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("ik"), FSxSTR("CCC"), 2, 9, FSxSTR("ristmik"),  FSxSTR("S")}, // VVS tyyp _S_ 25 aga tentsik? tyyp 2
{0, FSxSTR("ku"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("ik"), FSxSTR("CCC"), 2, 9, FSxSTR("ristmik"),  FSxSTR("S")}, // VVS tyyp _S_ 25 aga tentsik? tyyp 2
{0, FSxSTR("e"), FSxSTR(""), FSxSTR("pl g, "), FSxSTR("ik"), FSxSTR("CCC"), 2, 9, FSxSTR("ristmik"),  FSxSTR("S")}, // VVS tyyp _S_ 25 aga tentsik? tyyp 2
{0, FSxSTR("ku"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("ik"), FSxSTR("CCC"), 2, 9, FSxSTR("ristmik"),  FSxSTR("S")}, // VVS tyyp _S_ 25 aga tentsik? tyyp 2
{0, FSxSTR("k"), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("ik"), FSxSTR("CCC"), 2, 9, FSxSTR("ristmik"),  FSxSTR("S")}, // VVS tyyp _S_ 25 aga tentsik? tyyp 2
{0, FSxSTR("ku"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("ik"), FSxSTR("CCC"), 2, 9, FSxSTR("ristmik"),  FSxSTR("S")}, // VVS tyyp _S_ 25 aga tentsik? tyyp 2

{0, FSxSTR("u"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ik"), FSxSTR("VVCC"), 2, 9, FSxSTR("toestik"),  FSxSTR("S")}, // VVS tyyp 25 _S_ aga lootsik? tyyp 2
{0, FSxSTR("ku"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("ik"), FSxSTR("VVCC"), 2, 9, FSxSTR("toestik"),  FSxSTR("S")}, // VVS tyyp 25 _S_ aga lootsik? tyyp 2
{0, FSxSTR("ku"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("ik"), FSxSTR("VVCC"), 2, 9, FSxSTR("toestik"),  FSxSTR("S")}, // VVS tyyp 25 _S_ aga lootsik? tyyp 2
{0, FSxSTR("e"), FSxSTR(""), FSxSTR("pl g, "), FSxSTR("ik"), FSxSTR("VVCC"), 2, 9, FSxSTR("toestik"),  FSxSTR("S")}, // VVS tyyp 25 _S_ aga lootsik? tyyp 2
{0, FSxSTR("ku"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("ik"), FSxSTR("VVCC"), 2, 9, FSxSTR("toestik"),  FSxSTR("S")}, // VVS tyyp 25 _S_ aga lootsik? tyyp 2
{0, FSxSTR("k"), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("ik"), FSxSTR("VVCC"), 2, 9, FSxSTR("toestik"),  FSxSTR("S")}, // VVS tyyp 25 _S_ aga lootsik? tyyp 2
{0, FSxSTR("ku"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("ik"), FSxSTR("VVCC"), 2, 9, FSxSTR("toestik"),  FSxSTR("S")}, // VVS tyyp 25 _S_ aga lootsik? tyyp 2

{0, FSxSTR("u"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ik"), FSxSTR("CVVC"), 2, 9, FSxSTR("debiilik"),  FSxSTR("S")}, // VVS tyyp 2 
{0, FSxSTR("u"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("ik"), FSxSTR("CVVC"), 2, 9, FSxSTR("debiilik"),  FSxSTR("S")}, // VVS tyyp 2 
{0, FSxSTR("u"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("ik"), FSxSTR("CVVC"), 2, 9, FSxSTR("debiilik"),  FSxSTR("S")}, // VVS tyyp 2 
{0, FSxSTR("u"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("ik"), FSxSTR("CVVC"), 2, 9, FSxSTR("debiilik"),  FSxSTR("S")}, // VVS tyyp 2 

{0, FSxSTR("u"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ik"), FSxSTR("CVC"), 3, 9, FSxSTR("asemik"),  FSxSTR("S")}, // VVS tyyp 25 _S_
{0, FSxSTR("ku"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("ik"), FSxSTR("CVC"), 3, 9, FSxSTR("asemik"),  FSxSTR("S")}, // VVS tyyp 25 _S_
{0, FSxSTR("ku"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("ik"), FSxSTR("CVC"), 3, 9, FSxSTR("asemik"),  FSxSTR("S")}, // VVS tyyp 25 _S_
{0, FSxSTR("e"), FSxSTR(""), FSxSTR("pl g, "), FSxSTR("ik"), FSxSTR("CVC"), 3, 9, FSxSTR("asemik"),  FSxSTR("S")}, // VVS tyyp 25 _S_
{0, FSxSTR("ku"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("ik"), FSxSTR("CVC"), 3, 9, FSxSTR("asemik"),  FSxSTR("S")}, // VVS tyyp 25 _S_
{0, FSxSTR("k"), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("ik"), FSxSTR("CVC"), 3, 9, FSxSTR("asemik"),  FSxSTR("S")}, // VVS tyyp 25 _S_
{0, FSxSTR("ku"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("ik"), FSxSTR("CVC"), 3, 9, FSxSTR("asemik"),  FSxSTR("S")}, // VVS tyyp 25 _S_

{0, FSxSTR("u"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ik"), FSxSTR(""), 1, 1, FSxSTR("asemik"),  FSxSTR("S")}, // VVS tyyp 25 _S_
{0, FSxSTR("ku"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("ik"), FSxSTR(""), 1, 1, FSxSTR("asemik"),  FSxSTR("S")}, // VVS tyyp 25 _S_
{0, FSxSTR("ku"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("ik"), FSxSTR(""), 1, 1, FSxSTR("asemik"),  FSxSTR("S")}, // VVS tyyp 25 _S_
{0, FSxSTR("e"), FSxSTR(""), FSxSTR("pl g, "), FSxSTR("ik"), FSxSTR(""), 1, 1, FSxSTR("asemik"),  FSxSTR("S")}, // VVS tyyp 25 _S_
{0, FSxSTR("ku"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("ik"), FSxSTR(""), 1, 1, FSxSTR("asemik"),  FSxSTR("S")}, // VVS tyyp 25 _S_
{0, FSxSTR("k"), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("ik"), FSxSTR(""), 1, 1, FSxSTR("asemik"),  FSxSTR("S")}, // VVS tyyp 25 _S_
{0, FSxSTR("ku"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("ik"), FSxSTR(""), 1, 1, FSxSTR("asemik"),  FSxSTR("S")}, // VVS tyyp 25 _S_

{0, FSxSTR("u"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ik"), FSxSTR("VC"), 2, 2, FSxSTR("pihik"),  FSxSTR("S")}, // VVS tyyp 2 
{0, FSxSTR("u"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("ik"), FSxSTR("VC"), 2, 2, FSxSTR("pihik"),  FSxSTR("S")}, // VVS tyyp 2 
{0, FSxSTR("u"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("ik"), FSxSTR("VC"), 2, 2, FSxSTR("pihik"),  FSxSTR("S")}, // VVS tyyp 2 
{0, FSxSTR("u"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("ik"), FSxSTR("VC"), 2, 2, FSxSTR("pihik"),  FSxSTR("S")}, // VVS tyyp 2 

{0, FSxSTR("u"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ik"), FSxSTR("CC"), 3, 9, FSxSTR("loomastik"),  FSxSTR("S")}, // VVS tyyp 25 _S_
{0, FSxSTR("ku"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("ik"), FSxSTR("CC"), 3, 9, FSxSTR("loomastik"),  FSxSTR("S")}, // VVS tyyp 25 _S_
{0, FSxSTR("ku"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("ik"), FSxSTR("CC"), 3, 9, FSxSTR("loomastik"),  FSxSTR("S")}, // VVS tyyp 25 _S_
{0, FSxSTR("e"), FSxSTR(""), FSxSTR("pl g, "), FSxSTR("ik"), FSxSTR("CC"), 3, 9, FSxSTR("loomastik"),  FSxSTR("S")}, // VVS tyyp 25 _S_
{0, FSxSTR("ku"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("ik"), FSxSTR("CC"), 3, 9, FSxSTR("loomastik"),  FSxSTR("S")}, // VVS tyyp 25 _S_
{0, FSxSTR("k"), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("ik"), FSxSTR("CC"), 3, 9, FSxSTR("loomastik"),  FSxSTR("S")}, // VVS tyyp 25 _S_
{0, FSxSTR("ku"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("ik"), FSxSTR("CC"), 3, 9, FSxSTR("loomastik"),  FSxSTR("S")}, // VVS tyyp 25 _S_

{0, FSxSTR("u"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("lik"), FSxSTR("CC"), 2, 9, FSxSTR("arglik"),  FSxSTR("A")}, // VVS tyyp 25 _A_ 
{0, FSxSTR("ku"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("lik"), FSxSTR("CC"), 2, 9, FSxSTR("arglik"),  FSxSTR("A")}, // VVS tyyp 25 _A_ 
{0, FSxSTR("ku"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("lik"), FSxSTR("CC"), 2, 9, FSxSTR("arglik"),  FSxSTR("A")}, // VVS tyyp 25 _A_ 
{0, FSxSTR("e"), FSxSTR(""), FSxSTR("pl g, "), FSxSTR("lik"), FSxSTR("CC"), 2, 9, FSxSTR("arglik"),  FSxSTR("A")}, // VVS tyyp 25 _A_ 
{0, FSxSTR("ku"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("lik"), FSxSTR("CC"), 2, 9, FSxSTR("arglik"),  FSxSTR("A")}, // VVS tyyp 25 _A_ 
{0, FSxSTR("k"), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("lik"), FSxSTR("CC"), 2, 9, FSxSTR("arglik"),  FSxSTR("A")}, // VVS tyyp 25 _A_ 
{0, FSxSTR("ku"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("lik"), FSxSTR("CC"), 2, 9, FSxSTR("arglik"),  FSxSTR("A")}, // VVS tyyp 25 _A_ 

{0, FSxSTR("u"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("lik"), FSxSTR("C"), 3, 9, FSxSTR("tehislik"),  FSxSTR("A")}, // VVS tyyp 25 _A_ 
{0, FSxSTR("ku"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("lik"), FSxSTR("C"), 3, 9, FSxSTR("tehislik"),  FSxSTR("A")}, // VVS tyyp 25 _A_ 
{0, FSxSTR("ku"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("lik"), FSxSTR("C"), 3, 9, FSxSTR("tehislik"),  FSxSTR("A")}, // VVS tyyp 25 _A_ 
{0, FSxSTR("e"), FSxSTR(""), FSxSTR("pl g, "), FSxSTR("lik"), FSxSTR("C"), 3, 9, FSxSTR("tehislik"),  FSxSTR("A")}, // VVS tyyp 25 _A_ 
{0, FSxSTR("ku"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("lik"), FSxSTR("C"), 3, 9, FSxSTR("tehislik"),  FSxSTR("A")}, // VVS tyyp 25 _A_ 
{0, FSxSTR("k"), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("lik"), FSxSTR("C"), 3, 9, FSxSTR("tehislik"),  FSxSTR("A")}, // VVS tyyp 25 _A_ 
{0, FSxSTR("ku"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("lik"), FSxSTR("C"), 3, 9, FSxSTR("tehislik"),  FSxSTR("A")}, // VVS tyyp 25 _A_ 

{0, FSxSTR("u"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("lik"), FSxSTR("CV"), 3, 9, FSxSTR("puudulik"),  FSxSTR("A")}, // VVS tyyp 25 _A_
{0, FSxSTR("ku"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("lik"), FSxSTR("CV"), 3, 9, FSxSTR("puudulik"),  FSxSTR("A")}, // VVS tyyp 25 _A_
{0, FSxSTR("ku"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("lik"), FSxSTR("CV"), 3, 9, FSxSTR("puudulik"),  FSxSTR("A")}, // VVS tyyp 25 _A_
{0, FSxSTR("e"), FSxSTR(""), FSxSTR("pl g, "), FSxSTR("lik"), FSxSTR("CV"), 3, 9, FSxSTR("puudulik"),  FSxSTR("A")}, // VVS tyyp 25 _A_
{0, FSxSTR("ku"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("lik"), FSxSTR("CV"), 3, 9, FSxSTR("puudulik"),  FSxSTR("A")}, // VVS tyyp 25 _A_
{0, FSxSTR("k"), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("lik"), FSxSTR("CV"), 3, 9, FSxSTR("puudulik"),  FSxSTR("A")}, // VVS tyyp 25 _A_
{0, FSxSTR("ku"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("lik"), FSxSTR("CV"), 3, 9, FSxSTR("puudulik"),  FSxSTR("A")}, // VVS tyyp 25 _A_

{0, FSxSTR("u"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("lik"), FSxSTR("VVC"), 2, 9, FSxSTR("reetlik"),  FSxSTR("A")}, // VVS tyyp 25 _A_ 
{0, FSxSTR("ku"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("lik"), FSxSTR("VVC"), 2, 9, FSxSTR("reetlik"),  FSxSTR("A")}, // VVS tyyp 25 _A_ 
{0, FSxSTR("ku"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("lik"), FSxSTR("VVC"), 2, 9, FSxSTR("reetlik"),  FSxSTR("A")}, // VVS tyyp 25 _A_ 
{0, FSxSTR("e"), FSxSTR(""), FSxSTR("pl g, "), FSxSTR("lik"), FSxSTR("VVC"), 2, 9, FSxSTR("reetlik"),  FSxSTR("A")}, // VVS tyyp 25 _A_ 
{0, FSxSTR("ku"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("lik"), FSxSTR("VVC"), 2, 9, FSxSTR("reetlik"),  FSxSTR("A")}, // VVS tyyp 25 _A_ 
{0, FSxSTR("k"), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("lik"), FSxSTR("VVC"), 2, 9, FSxSTR("reetlik"),  FSxSTR("A")}, // VVS tyyp 25 _A_ 
{0, FSxSTR("ku"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("lik"), FSxSTR("VVC"), 2, 9, FSxSTR("reetlik"),  FSxSTR("A")}, // VVS tyyp 25 _A_ 

{1, FSxSTR("gi"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("uuk"), FSxSTR(""), 1, 9, FSxSTR("luuk"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("uuk"), FSxSTR(""), 1, 9, FSxSTR("luuk"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("uuk"), FSxSTR(""), 1, 9, FSxSTR("luuk"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("uuk"), FSxSTR(""), 1, 9, FSxSTR("luuk"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("uuk"), FSxSTR(""), 1, 9, FSxSTR("luuk"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("uuk"), FSxSTR(""), 1, 9, FSxSTR("luuk"),  FSxSTR("S")}, // VVS tyyp 22

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("uk"), FSxSTR(""), 2, 2, FSxSTR("ujuk"),  FSxSTR("S")}, // VVS tyyp 2 
{0, FSxSTR("i"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("uk"), FSxSTR(""), 2, 2, FSxSTR("ujuk"),  FSxSTR("S")}, // VVS tyyp 2 
{0, FSxSTR("i"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("uk"), FSxSTR(""), 2, 2, FSxSTR("ujuk"),  FSxSTR("S")}, // VVS tyyp 2 
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("uk"), FSxSTR(""), 2, 2, FSxSTR("ujuk"),  FSxSTR("S")}, // VVS tyyp 2 

{1, FSxSTR("bi"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("p"), FSxSTR("L"), 1, 1, FSxSTR("karp"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("p"), FSxSTR("L"), 1, 1, FSxSTR("karp"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("p"), FSxSTR("L"), 1, 1, FSxSTR("karp"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("p"), FSxSTR("L"), 1, 1, FSxSTR("karp"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("p"), FSxSTR("L"), 1, 1, FSxSTR("karp"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("p"), FSxSTR("L"), 1, 1, FSxSTR("karp"),  FSxSTR("S")}, // VVS tyyp 22

{1, FSxSTR("bi"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("p"), FSxSTR("VV"), 1, 9, FSxSTR("satraap"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("p"), FSxSTR("VV"), 1, 9, FSxSTR("satraap"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("p"), FSxSTR("VV"), 1, 9, FSxSTR("satraap"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("p"), FSxSTR("VV"), 1, 9, FSxSTR("satraap"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("p"), FSxSTR("VV"), 1, 9, FSxSTR("satraap"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("p"), FSxSTR("VV"), 1, 9, FSxSTR("satraap"),  FSxSTR("S")}, // VVS tyyp 22

{1, FSxSTR("bi"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("p"), FSxSTR("VL"), 1, 9, FSxSTR("estamp"),  FSxSTR("S")}, // VVS tyyp 22 aga selliseid tegelt ei leidu?
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("p"), FSxSTR("VL"), 1, 9, FSxSTR("estamp"),  FSxSTR("S")}, // VVS tyyp 22 aga selliseid tegelt ei leidu?
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("p"), FSxSTR("VL"), 1, 9, FSxSTR("estamp"),  FSxSTR("S")}, // VVS tyyp 22 aga selliseid tegelt ei leidu?
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("p"), FSxSTR("VL"), 1, 9, FSxSTR("estamp"),  FSxSTR("S")}, // VVS tyyp 22 aga selliseid tegelt ei leidu?
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("p"), FSxSTR("VL"), 1, 9, FSxSTR("estamp"),  FSxSTR("S")}, // VVS tyyp 22 aga selliseid tegelt ei leidu?
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("p"), FSxSTR("VL"), 1, 9, FSxSTR("estamp"),  FSxSTR("S")}, // VVS tyyp 22 aga selliseid tegelt ei leidu?

{1, FSxSTR("di"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("t"), FSxSTR("L"), 1, 1, FSxSTR("fort"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("t"), FSxSTR("L"), 1, 1, FSxSTR("fort"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("t"), FSxSTR("L"), 1, 1, FSxSTR("fort"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("t"), FSxSTR("L"), 1, 1, FSxSTR("fort"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("t"), FSxSTR("L"), 1, 1, FSxSTR("fort"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("t"), FSxSTR("L"), 1, 1, FSxSTR("fort"),  FSxSTR("S")}, // VVS tyyp 22

{1, FSxSTR("di"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("t"), FSxSTR("VV"), 1, 9, FSxSTR("magnetiit"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("t"), FSxSTR("VV"), 1, 9, FSxSTR("magnetiit"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("t"), FSxSTR("VV"), 1, 9, FSxSTR("magnetiit"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("t"), FSxSTR("VV"), 1, 9, FSxSTR("magnetiit"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("t"), FSxSTR("VV"), 1, 9, FSxSTR("magnetiit"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("t"), FSxSTR("VV"), 1, 9, FSxSTR("magnetiit"),  FSxSTR("S")}, // VVS tyyp 22

{1, FSxSTR("di"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("t"), FSxSTR("VL"), 1, 9, FSxSTR("komitent"),  FSxSTR("S")}, // VVS tyyp 22 mt tegelt ei esine
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("t"), FSxSTR("VL"), 1, 9, FSxSTR("komitent"),  FSxSTR("S")}, // VVS tyyp 22 mt tegelt ei esine
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("t"), FSxSTR("VL"), 1, 9, FSxSTR("komitent"),  FSxSTR("S")}, // VVS tyyp 22 mt tegelt ei esine
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("t"), FSxSTR("VL"), 1, 9, FSxSTR("komitent"),  FSxSTR("S")}, // VVS tyyp 22 mt tegelt ei esine
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("t"), FSxSTR("VL"), 1, 9, FSxSTR("komitent"),  FSxSTR("S")}, // VVS tyyp 22 mt tegelt ei esine
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("t"), FSxSTR("VL"), 1, 9, FSxSTR("komitent"),  FSxSTR("S")}, // VVS tyyp 22 mt tegelt ei esine

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("kt"), FSxSTR("V"), 1, 9, FSxSTR("viadukt"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("kt"), FSxSTR("V"), 1, 9, FSxSTR("viadukt"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("kt"), FSxSTR("V"), 1, 9, FSxSTR("viadukt"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("kt"), FSxSTR("V"), 1, 9, FSxSTR("viadukt"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("kt"), FSxSTR("V"), 1, 9, FSxSTR("viadukt"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("kt"), FSxSTR("V"), 1, 9, FSxSTR("viadukt"),  FSxSTR("S")}, // VVS tyyp 22

{1, FSxSTR("di"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("nt"), FSxSTR("V"), 1, 9, FSxSTR("preprint"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("nt"), FSxSTR("V"), 1, 9, FSxSTR("preprint"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("nt"), FSxSTR("V"), 1, 9, FSxSTR("preprint"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("nt"), FSxSTR("V"), 1, 9, FSxSTR("preprint"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("nt"), FSxSTR("V"), 1, 9, FSxSTR("preprint"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("nt"), FSxSTR("V"), 1, 9, FSxSTR("preprint"),  FSxSTR("S")}, // VVS tyyp 22

{1, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("tt"), FSxSTR("CV"), 1, 1, FSxSTR("hitt"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("tt"), FSxSTR("CV"), 1, 1, FSxSTR("hitt"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("tt"), FSxSTR("CV"), 1, 1, FSxSTR("hitt"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("tt"), FSxSTR("CV"), 1, 1, FSxSTR("hitt"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("tt"), FSxSTR("CV"), 1, 1, FSxSTR("hitt"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("tt"), FSxSTR("CV"), 1, 1, FSxSTR("hitt"),  FSxSTR("S")}, // VVS tyyp 22

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("st"), FSxSTR("V"), 1, 9, FSxSTR("galerist"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("st"), FSxSTR("V"), 1, 9, FSxSTR("galerist"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("st"), FSxSTR("V"), 1, 9, FSxSTR("galerist"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("st"), FSxSTR("V"), 1, 9, FSxSTR("galerist"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("st"), FSxSTR("V"), 1, 9, FSxSTR("galerist"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("st"), FSxSTR("V"), 1, 9, FSxSTR("galerist"),  FSxSTR("S")}, // VVS tyyp 22

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("net"), FSxSTR(""), 1, 9, FSxSTR("kabinet"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("ti"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("net"), FSxSTR(""), 1, 9, FSxSTR("kabinet"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("ti"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("net"), FSxSTR(""), 1, 9, FSxSTR("kabinet"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("ti"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("net"), FSxSTR(""), 1, 9, FSxSTR("kabinet"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("t"), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("net"), FSxSTR(""), 1, 9, FSxSTR("kabinet"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("ti"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("net"), FSxSTR(""), 1, 9, FSxSTR("kabinet"),  FSxSTR("S")}, // VVS tyyp 22

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("lot"), FSxSTR(""), 1, 9, FSxSTR("kabinet"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("ti"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("lot"), FSxSTR(""), 1, 9, FSxSTR("kabinet"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("ti"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("lot"), FSxSTR(""), 1, 9, FSxSTR("kabinet"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("ti"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("lot"), FSxSTR(""), 1, 9, FSxSTR("kabinet"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("t"), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("lot"), FSxSTR(""), 1, 9, FSxSTR("kabinet"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("ti"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("lot"), FSxSTR(""), 1, 9, FSxSTR("kabinet"),  FSxSTR("S")}, // VVS tyyp 22

{1, FSxSTR("na"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("kond"), FSxSTR("C"), 1, 9, FSxSTR("praostkond"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("a"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("kond"), FSxSTR("C"), 1, 9, FSxSTR("praostkond"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("a"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("kond"), FSxSTR("C"), 1, 9, FSxSTR("praostkond"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("a"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("kond"), FSxSTR("C"), 1, 9, FSxSTR("praostkond"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("a"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("kond"), FSxSTR("C"), 1, 9, FSxSTR("praostkond"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("i"), FSxSTR("pl p, "), FSxSTR("kond"), FSxSTR("C"), 1, 9, FSxSTR("praostkond"),  FSxSTR("S")}, // VVS tyyp 22

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("hl"), FSxSTR("V"), 1, 1, FSxSTR("ball"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("hl"), FSxSTR("V"), 1, 1, FSxSTR("ball"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("hl"), FSxSTR("V"), 1, 1, FSxSTR("ball"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("hl"), FSxSTR("V"), 1, 1, FSxSTR("ball"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("hl"), FSxSTR("V"), 1, 1, FSxSTR("ball"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("hl"), FSxSTR("V"), 1, 1, FSxSTR("ball"),  FSxSTR("S")}, // VVS tyyp 22

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("l"), FSxSTR("VV"), 1, 9, FSxSTR("biennaal"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("l"), FSxSTR("VV"), 1, 9, FSxSTR("biennaal"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("l"), FSxSTR("VV"), 1, 9, FSxSTR("biennaal"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("l"), FSxSTR("VV"), 1, 9, FSxSTR("biennaal"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("l"), FSxSTR("VV"), 1, 9, FSxSTR("biennaal"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("l"), FSxSTR("VV"), 1, 9, FSxSTR("biennaal"),  FSxSTR("S")}, // VVS tyyp 22

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("l"), FSxSTR("CV"), 2, 2, FSxSTR("pobul"),  FSxSTR("S")}, // VVS tyyp 2
{0, FSxSTR("i"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("l"), FSxSTR("CV"), 2, 2, FSxSTR("pobul"),  FSxSTR("S")}, // VVS tyyp 2
{0, FSxSTR("i"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("l"), FSxSTR("CV"), 2, 2, FSxSTR("pobul"),  FSxSTR("S")}, // VVS tyyp 2
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("l"), FSxSTR("CV"), 2, 2, FSxSTR("pobul"),  FSxSTR("S")}, // VVS tyyp 2

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("l"), FSxSTR("CV"), 3, 9, FSxSTR("molekul"),  FSxSTR("S")}, // VVS tyyp 19
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("l"), FSxSTR("CV"), 3, 9, FSxSTR("molekul"),  FSxSTR("S")}, // VVS tyyp 19
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("l"), FSxSTR("CV"), 3, 9, FSxSTR("molekul"),  FSxSTR("S")}, // VVS tyyp 19
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("l"), FSxSTR("CV"), 3, 9, FSxSTR("molekul"),  FSxSTR("S")}, // VVS tyyp 19
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("l"), FSxSTR("CV"), 3, 9, FSxSTR("molekul"),  FSxSTR("S")}, // VVS tyyp 19
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("l"), FSxSTR("CV"), 3, 9, FSxSTR("molekul"),  FSxSTR("S")}, // VVS tyyp 19

{2, FSxSTR("li"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("el"), FSxSTR("VVC"), 2, 2, FSxSTR("oraakel"),  FSxSTR("S")}, // VVS tyyp 2 ?? kui kindel see on?
{2, FSxSTR("li"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("el"), FSxSTR("VVC"), 2, 2, FSxSTR("oraakel"),  FSxSTR("S")}, // VVS tyyp 2 ?? kui kindel see on?
{2, FSxSTR("li"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("el"), FSxSTR("VVC"), 2, 2, FSxSTR("oraakel"),  FSxSTR("S")}, // VVS tyyp 2 ?? kui kindel see on?
{2, FSxSTR("le"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("el"), FSxSTR("VVC"), 2, 2, FSxSTR("oraakel"),  FSxSTR("S")}, // VVS tyyp 2 ?? kui kindel see on?

{2, FSxSTR("li"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("el"), FSxSTR("VLP"), 2, 2, FSxSTR("mantel"),  FSxSTR("S")}, // VVS tyyp 2 ?? kui kindel see on?
{2, FSxSTR("li"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("el"), FSxSTR("VLP"), 2, 2, FSxSTR("mantel"),  FSxSTR("S")}, // VVS tyyp 2 ?? kui kindel see on?
{2, FSxSTR("li"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("el"), FSxSTR("VLP"), 2, 2, FSxSTR("mantel"),  FSxSTR("S")}, // VVS tyyp 2 ?? kui kindel see on?
{2, FSxSTR("le"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("el"), FSxSTR("VLP"), 2, 2, FSxSTR("mantel"),  FSxSTR("S")}, // VVS tyyp 2 ?? kui kindel see on?

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("eel"), FSxSTR("C"), 1, 9, FSxSTR("juveel"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("eel"), FSxSTR("C"), 1, 9, FSxSTR("juveel"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("eel"), FSxSTR("C"), 1, 9, FSxSTR("juveel"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("eel"), FSxSTR("C"), 1, 9, FSxSTR("juveel"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("eel"), FSxSTR("C"), 1, 9, FSxSTR("juveel"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("eel"), FSxSTR("C"), 1, 9, FSxSTR("juveel"),  FSxSTR("S")}, // VVS tyyp 22

{2, FSxSTR("li"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("aabel"), FSxSTR("C"), 2, 9, FSxSTR("saabel"),  FSxSTR("S")}, // VVS tyyp 2
{2, FSxSTR("li"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("aabel"), FSxSTR("C"), 2, 9, FSxSTR("saabel"),  FSxSTR("S")}, // VVS tyyp 2
{2, FSxSTR("li"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("aabel"), FSxSTR("C"), 2, 9, FSxSTR("saabel"),  FSxSTR("S")}, // VVS tyyp 2
{2, FSxSTR("le"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("aabel"), FSxSTR("C"), 2, 9, FSxSTR("saabel"),  FSxSTR("S")}, // VVS tyyp 2

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("m"), FSxSTR("VV"), 1, 9, FSxSTR("binoom"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("m"), FSxSTR("VV"), 1, 9, FSxSTR("binoom"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("m"), FSxSTR("VV"), 1, 9, FSxSTR("binoom"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("m"), FSxSTR("VV"), 1, 9, FSxSTR("binoom"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("m"), FSxSTR("VV"), 1, 9, FSxSTR("binoom"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("m"), FSxSTR("VV"), 1, 9, FSxSTR("binoom"),  FSxSTR("S")}, // VVS tyyp 22

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("m"), FSxSTR("CV"), 2, 2, FSxSTR("jalam"),  FSxSTR("S")}, // VVS tyyp 2
{0, FSxSTR("i"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("m"), FSxSTR("CV"), 2, 2, FSxSTR("jalam"),  FSxSTR("S")}, // VVS tyyp 2
{0, FSxSTR("i"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("m"), FSxSTR("CV"), 2, 2, FSxSTR("jalam"),  FSxSTR("S")}, // VVS tyyp 2
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("m"), FSxSTR("CV"), 2, 2, FSxSTR("jalam"),  FSxSTR("S")}, // VVS tyyp 2

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("um"), FSxSTR("C"), 3, 9, FSxSTR("kliinikum"),  FSxSTR("S")}, // VVS tyyp 19
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("um"), FSxSTR("C"), 3, 9, FSxSTR("kliinikum"),  FSxSTR("S")}, // VVS tyyp 19
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("um"), FSxSTR("C"), 3, 9, FSxSTR("kliinikum"),  FSxSTR("S")}, // VVS tyyp 19
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("um"), FSxSTR("C"), 3, 9, FSxSTR("kliinikum"),  FSxSTR("S")}, // VVS tyyp 19
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("um"), FSxSTR("C"), 3, 9, FSxSTR("kliinikum"),  FSxSTR("S")}, // VVS tyyp 19
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("um"), FSxSTR("C"), 3, 9, FSxSTR("kliinikum"),  FSxSTR("S")}, // VVS tyyp 19

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ism"), FSxSTR(""), 1, 9, FSxSTR("babtism"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("ism"), FSxSTR(""), 1, 9, FSxSTR("babtism"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("ism"), FSxSTR(""), 1, 9, FSxSTR("babtism"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("ism"), FSxSTR(""), 1, 9, FSxSTR("babtism"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("ism"), FSxSTR(""), 1, 9, FSxSTR("babtism"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("ism"), FSxSTR(""), 1, 9, FSxSTR("babtism"),  FSxSTR("S")}, // VVS tyyp 22

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ium"), FSxSTR(""), 2, 9, FSxSTR("sootsium"),  FSxSTR("S")}, // VVS tyyp 2 ja 19; veidi erineb VVB 22-st
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("ium"), FSxSTR(""), 2, 9, FSxSTR("sootsium"),  FSxSTR("S")}, // VVS tyyp 2 ja 19; veidi erineb VVB 22-st
{0, FSxSTR("i"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("ium"), FSxSTR(""), 2, 9, FSxSTR("sootsium"),  FSxSTR("S")}, // VVS tyyp 2 ja 19; veidi erineb VVB 22-st
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("ium"), FSxSTR(""), 2, 9, FSxSTR("sootsium"),  FSxSTR("S")}, // VVS tyyp 2 ja 19; veidi erineb VVB 22-st
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("ium"), FSxSTR(""), 2, 9, FSxSTR("sootsium"),  FSxSTR("S")}, // VVS tyyp 2 ja 19; veidi erineb VVB 22-st
{0, FSxSTR("i"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("ium"), FSxSTR(""), 2, 9, FSxSTR("sootsium"),  FSxSTR("S")}, // VVS tyyp 2 ja 19; veidi erineb VVB 22-st
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("ium"), FSxSTR(""), 2, 9, FSxSTR("sootsium"),  FSxSTR("S")}, // VVS tyyp 2 ja 19; veidi erineb VVB 22-st
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("ium"), FSxSTR(""), 2, 9, FSxSTR("sootsium"),  FSxSTR("S")}, // VVS tyyp 2 ja 19; veidi erineb VVB 22-st

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("eum"), FSxSTR(""), 2, 9, FSxSTR("muuseum"),  FSxSTR("S")}, // VVS tyyp 2 ja 19; veidi erineb VVB 22-st; aga karboliineum on 22 (sest ro'hk on teises kohas )
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("eum"), FSxSTR(""), 2, 9, FSxSTR("muuseum"),  FSxSTR("S")}, // VVS tyyp 2 ja 19; veidi erineb VVB 22-st; aga karboliineum on 22 (sest ro'hk on teises kohas )
{0, FSxSTR("i"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("eum"), FSxSTR(""), 2, 9, FSxSTR("muuseum"),  FSxSTR("S")}, // VVS tyyp 2 ja 19; veidi erineb VVB 22-st; aga karboliineum on 22 (sest ro'hk on teises kohas )
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("eum"), FSxSTR(""), 2, 9, FSxSTR("muuseum"),  FSxSTR("S")}, // VVS tyyp 2 ja 19; veidi erineb VVB 22-st; aga karboliineum on 22 (sest ro'hk on teises kohas )
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("eum"), FSxSTR(""), 2, 9, FSxSTR("muuseum"),  FSxSTR("S")}, // VVS tyyp 2 ja 19; veidi erineb VVB 22-st; aga karboliineum on 22 (sest ro'hk on teises kohas )
{0, FSxSTR("i"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("eum"), FSxSTR(""), 2, 9, FSxSTR("muuseum"),  FSxSTR("S")}, // VVS tyyp 2 ja 19; veidi erineb VVB 22-st; aga karboliineum on 22 (sest ro'hk on teises kohas )
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("eum"), FSxSTR(""), 2, 9, FSxSTR("muuseum"),  FSxSTR("S")}, // VVS tyyp 2 ja 19; veidi erineb VVB 22-st; aga karboliineum on 22 (sest ro'hk on teises kohas )
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("eum"), FSxSTR(""), 2, 9, FSxSTR("muuseum"),  FSxSTR("S")}, // VVS tyyp 2 ja 19; veidi erineb VVB 22-st; aga karboliineum on 22 (sest ro'hk on teises kohas )

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("n"), FSxSTR("VV"), 1, 9, FSxSTR("laguun"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("n"), FSxSTR("VV"), 1, 9, FSxSTR("laguun"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("n"), FSxSTR("VV"), 1, 9, FSxSTR("laguun"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("n"), FSxSTR("VV"), 1, 9, FSxSTR("laguun"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("n"), FSxSTR("VV"), 1, 9, FSxSTR("laguun"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("n"), FSxSTR("VV"), 1, 9, FSxSTR("laguun"),  FSxSTR("S")}, // VVS tyyp 22

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("n"), FSxSTR("CV"), 2, 2, FSxSTR("tohman"),  FSxSTR("S")}, // VVS tyyp 2
{0, FSxSTR("i"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("n"), FSxSTR("CV"), 2, 2, FSxSTR("tohman"),  FSxSTR("S")}, // VVS tyyp 2
{0, FSxSTR("i"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("n"), FSxSTR("CV"), 2, 2, FSxSTR("tohman"),  FSxSTR("S")}, // VVS tyyp 2
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("n"), FSxSTR("CV"), 2, 2, FSxSTR("tohman"),  FSxSTR("S")}, // VVS tyyp 2

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("n"), FSxSTR("CV"), 3, 9, FSxSTR("partisan"),  FSxSTR("S")}, // VVS tyyp 19
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("n"), FSxSTR("CV"), 3, 9, FSxSTR("partisan"),  FSxSTR("S")}, // VVS tyyp 19
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("n"), FSxSTR("CV"), 3, 9, FSxSTR("partisan"),  FSxSTR("S")}, // VVS tyyp 19
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("n"), FSxSTR("CV"), 3, 9, FSxSTR("partisan"),  FSxSTR("S")}, // VVS tyyp 19
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("n"), FSxSTR("CV"), 3, 9, FSxSTR("partisan"),  FSxSTR("S")}, // VVS tyyp 19
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("n"), FSxSTR("CV"), 3, 9, FSxSTR("partisan"),  FSxSTR("S")}, // VVS tyyp 19

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("iin"), FSxSTR(""), 1, 9, FSxSTR("bensiin"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("iin"), FSxSTR(""), 1, 9, FSxSTR("bensiin"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("iin"), FSxSTR(""), 1, 9, FSxSTR("bensiin"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("iin"), FSxSTR(""), 1, 9, FSxSTR("bensiin"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("iin"), FSxSTR(""), 1, 9, FSxSTR("bensiin"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("iin"), FSxSTR(""), 1, 9, FSxSTR("bensiin"),  FSxSTR("S")}, // VVS tyyp 22

{0, FSxSTR("a"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("in"), FSxSTR("C"), 2, 2, FSxSTR("ragin"),  FSxSTR("S")}, // VVS tyyp 2
{0, FSxSTR("a"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("in"), FSxSTR("C"), 2, 2, FSxSTR("ragin"),  FSxSTR("S")}, // VVS tyyp 2
{0, FSxSTR("a"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("in"), FSxSTR("C"), 2, 2, FSxSTR("ragin"),  FSxSTR("S")}, // VVS tyyp 2
{0, FSxSTR("a"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("in"), FSxSTR("C"), 2, 2, FSxSTR("ragin"),  FSxSTR("S")}, // VVS tyyp 2

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ion"), FSxSTR(""), 2, 9, FSxSTR("pension"),  FSxSTR("S")}, // VVS tyyp 2 ja 19; veidi erineb VVB 22-st
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("ion"), FSxSTR(""), 2, 9, FSxSTR("pension"),  FSxSTR("S")}, // VVS tyyp 2 ja 19; veidi erineb VVB 22-st
{0, FSxSTR("i"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("ion"), FSxSTR(""), 2, 9, FSxSTR("pension"),  FSxSTR("S")}, // VVS tyyp 2 ja 19; veidi erineb VVB 22-st
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("ion"), FSxSTR(""), 2, 9, FSxSTR("pension"),  FSxSTR("S")}, // VVS tyyp 2 ja 19; veidi erineb VVB 22-st
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("ion"), FSxSTR(""), 2, 9, FSxSTR("pension"),  FSxSTR("S")}, // VVS tyyp 2 ja 19; veidi erineb VVB 22-st
{0, FSxSTR("i"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("ion"), FSxSTR(""), 2, 9, FSxSTR("pension"),  FSxSTR("S")}, // VVS tyyp 2 ja 19; veidi erineb VVB 22-st
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("ion"), FSxSTR(""), 2, 9, FSxSTR("pension"),  FSxSTR("S")}, // VVS tyyp 2 ja 19; veidi erineb VVB 22-st
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("ion"), FSxSTR(""), 2, 9, FSxSTR("pension"),  FSxSTR("S")}, // VVS tyyp 2 ja 19; veidi erineb VVB 22-st

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("r"), FSxSTR("VV"), 1, 9, FSxSTR("basaar"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("r"), FSxSTR("VV"), 1, 9, FSxSTR("basaar"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("r"), FSxSTR("VV"), 1, 9, FSxSTR("basaar"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("r"), FSxSTR("VV"), 1, 9, FSxSTR("basaar"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("r"), FSxSTR("VV"), 1, 9, FSxSTR("basaar"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("r"), FSxSTR("VV"), 1, 9, FSxSTR("basaar"),  FSxSTR("S")}, // VVS tyyp 22

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("hver"), FSxSTR(""), 2, 2, FSxSTR("ohver"),  FSxSTR("S")}, // VVS tyyp 2 
{0, FSxSTR("i"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("hver"), FSxSTR(""), 2, 2, FSxSTR("ohver"),  FSxSTR("S")}, // VVS tyyp 2 
{0, FSxSTR("i"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("hver"), FSxSTR(""), 2, 2, FSxSTR("ohver"),  FSxSTR("S")}, // VVS tyyp 2
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("hver"), FSxSTR(""), 2, 2, FSxSTR("ohver"),  FSxSTR("S")}, // VVS tyyp 2 

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("aider"), FSxSTR(""), 2, 2, FSxSTR("autsaider"),  FSxSTR("S")}, // VVS tyyp 2 
{0, FSxSTR("i"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("aider"), FSxSTR(""), 2, 2, FSxSTR("autsaider"),  FSxSTR("S")}, // VVS tyyp 2 
{0, FSxSTR("i"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("aider"), FSxSTR(""), 2, 2, FSxSTR("autsaider"),  FSxSTR("S")}, // VVS tyyp 2
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("aider"), FSxSTR(""), 2, 2, FSxSTR("autsaider"),  FSxSTR("S")}, // VVS tyyp 2 

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("der"), FSxSTR("VV"), 2, 2, FSxSTR("liider"),  FSxSTR("S")}, // VVS tyyp 2 
{0, FSxSTR("i"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("der"), FSxSTR("VV"), 2, 2, FSxSTR("liider"),  FSxSTR("S")}, // VVS tyyp 2 
{0, FSxSTR("i"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("der"), FSxSTR("VV"), 2, 2, FSxSTR("liider"),  FSxSTR("S")}, // VVS tyyp 2
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("der"), FSxSTR("VV"), 2, 2, FSxSTR("liider"),  FSxSTR("S")}, // VVS tyyp 2 

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("r"), FSxSTR("CV"), 2, 2, FSxSTR("pitser"),  FSxSTR("S")}, // VVS tyyp 2 siider valesti!
{0, FSxSTR("i"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("r"), FSxSTR("CV"), 2, 2, FSxSTR("pitser"),  FSxSTR("S")}, // VVS tyyp 2 siider valesti!
{0, FSxSTR("i"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("r"), FSxSTR("CV"), 2, 2, FSxSTR("pitser"),  FSxSTR("S")}, // VVS tyyp 2 siider valesti!
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("r"), FSxSTR("CV"), 2, 2, FSxSTR("pitser"),  FSxSTR("S")}, // VVS tyyp 2 siider valesti!

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("r"), FSxSTR("CV"), 3, 9, FSxSTR("korgitser"),  FSxSTR("S")}, // VVS tyyp 19
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("r"), FSxSTR("CV"), 3, 9, FSxSTR("korgitser"),  FSxSTR("S")}, // VVS tyyp 19
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("r"), FSxSTR("CV"), 3, 9, FSxSTR("korgitser"),  FSxSTR("S")}, // VVS tyyp 19
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("r"), FSxSTR("CV"), 3, 9, FSxSTR("korgitser"),  FSxSTR("S")}, // VVS tyyp 19
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("r"), FSxSTR("CV"), 3, 9, FSxSTR("korgitser"),  FSxSTR("S")}, // VVS tyyp 19
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("r"), FSxSTR("CV"), 3, 9, FSxSTR("korgitser"),  FSxSTR("S")}, // VVS tyyp 19

{2, FSxSTR("ri"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("eeder"), FSxSTR(""), 2, 9, FSxSTR("leeder"),  FSxSTR("S")}, // VVS tyyp 2
{2, FSxSTR("ri"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("eeder"), FSxSTR(""), 2, 9, FSxSTR("leeder"),  FSxSTR("S")}, // VVS tyyp 2
{2, FSxSTR("ri"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("eeder"), FSxSTR(""), 2, 9, FSxSTR("leeder"),  FSxSTR("S")}, // VVS tyyp 2
{2, FSxSTR("re"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("eeder"), FSxSTR(""), 2, 9, FSxSTR("leeder"),  FSxSTR("S")}, // VVS tyyp 2

{2, FSxSTR("ri"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("der"), FSxSTR("VL"), 2, 9, FSxSTR("kalender"),  FSxSTR("S")}, // VVS tyyp 2
{2, FSxSTR("ri"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("der"), FSxSTR("VL"), 2, 9, FSxSTR("kalender"),  FSxSTR("S")}, // VVS tyyp 2
{2, FSxSTR("ri"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("der"), FSxSTR("VL"), 2, 9, FSxSTR("kalender"),  FSxSTR("S")}, // VVS tyyp 2
{2, FSxSTR("re"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("der"), FSxSTR("VL"), 2, 9, FSxSTR("kalender"),  FSxSTR("S")}, // VVS tyyp 2

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ior"), FSxSTR(""), 2, 9, FSxSTR("seenior"),  FSxSTR("S")}, // VVS tyyp 2 ja 19; veidi erineb VVB 22-st
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("ior"), FSxSTR(""), 2, 9, FSxSTR("seenior"),  FSxSTR("S")}, // VVS tyyp 2 ja 19; veidi erineb VVB 22-st
{0, FSxSTR("i"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("ior"), FSxSTR(""), 2, 9, FSxSTR("seenior"),  FSxSTR("S")}, // VVS tyyp 2 ja 19; veidi erineb VVB 22-st
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("ior"), FSxSTR(""), 2, 9, FSxSTR("seenior"),  FSxSTR("S")}, // VVS tyyp 2 ja 19; veidi erineb VVB 22-st
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("ior"), FSxSTR(""), 2, 9, FSxSTR("seenior"),  FSxSTR("S")}, // VVS tyyp 2 ja 19; veidi erineb VVB 22-st
{0, FSxSTR("i"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("ior"), FSxSTR(""), 2, 9, FSxSTR("seenior"),  FSxSTR("S")}, // VVS tyyp 2 ja 19; veidi erineb VVB 22-st
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("ior"), FSxSTR(""), 2, 9, FSxSTR("seenior"),  FSxSTR("S")}, // VVS tyyp 2 ja 19; veidi erineb VVB 22-st
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("ior"), FSxSTR(""), 2, 9, FSxSTR("seenior"),  FSxSTR("S")}, // VVS tyyp 2 ja 19; veidi erineb VVB 22-st

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("oor"), FSxSTR(""), 1, 9, FSxSTR("furoor"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("oor"), FSxSTR(""), 1, 9, FSxSTR("furoor"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("oor"), FSxSTR(""), 1, 9, FSxSTR("furoor"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("oor"), FSxSTR(""), 1, 9, FSxSTR("furoor"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("oor"), FSxSTR(""), 1, 9, FSxSTR("furoor"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("oor"), FSxSTR(""), 1, 9, FSxSTR("furoor"),  FSxSTR("S")}, // VVS tyyp 22

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("or"), FSxSTR("C"), 2, 9, FSxSTR("diskor"),  FSxSTR("S")}, // VVS tyyp 2
{0, FSxSTR("i"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("or"), FSxSTR("C"), 2, 9, FSxSTR("diskor"),  FSxSTR("S")}, // VVS tyyp 2
{0, FSxSTR("i"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("or"), FSxSTR("C"), 2, 9, FSxSTR("diskor"),  FSxSTR("S")}, // VVS tyyp 2
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("or"), FSxSTR("C"), 2, 9, FSxSTR("diskor"),  FSxSTR("S")}, // VVS tyyp 2

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ier"), FSxSTR(""), 2, 9, FSxSTR("pleier"),  FSxSTR("S")}, // VVS tyyp 2; veidi erineb VVB 22-st
{0, FSxSTR("i"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("ier"), FSxSTR(""), 2, 9, FSxSTR("pleier"),  FSxSTR("S")}, // VVS tyyp 2; veidi erineb VVB 22-st
{0, FSxSTR("i"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("ier"), FSxSTR(""), 2, 9, FSxSTR("pleier"),  FSxSTR("S")}, // VVS tyyp 2; veidi erineb VVB 22-st
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("ier"), FSxSTR(""), 2, 9, FSxSTR("pleier"),  FSxSTR("S")}, // VVS tyyp 2; veidi erineb VVB 22-st

{0, FSxSTR("u"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ing"), FSxSTR(""), 2, 9, FSxSTR("holding"),  FSxSTR("S")}, // VVS tyyp 2; veidi erineb VCC 22-st
{0, FSxSTR("u"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("ing"), FSxSTR(""), 2, 9, FSxSTR("holding"),  FSxSTR("S")}, // VVS tyyp 2; veidi erineb VCC 22-st
{0, FSxSTR("u"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("ing"), FSxSTR(""), 2, 9, FSxSTR("holding"),  FSxSTR("S")}, // VVS tyyp 2; veidi erineb VCC 22-st
{0, FSxSTR("u"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("ing"), FSxSTR(""), 2, 9, FSxSTR("holding"),  FSxSTR("S")}, // VVS tyyp 2; veidi erineb VCC 22-st

{0, FSxSTR("u"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ang"), FSxSTR(""), 2, 2, FSxSTR("valang"),  FSxSTR("S")}, // VVS tyyp 2; veidi erineb VCC 22-st
{0, FSxSTR("u"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("ang"), FSxSTR(""), 2, 2, FSxSTR("valang"),  FSxSTR("S")}, // VVS tyyp 2; veidi erineb VCC 22-st
{0, FSxSTR("u"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("ang"), FSxSTR(""), 2, 2, FSxSTR("valang"),  FSxSTR("S")}, // VVS tyyp 2; veidi erineb VCC 22-st
{0, FSxSTR("u"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("ang"), FSxSTR(""), 2, 2, FSxSTR("valang"),  FSxSTR("S")}, // VVS tyyp 2; veidi erineb VCC 22-st

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ung"), FSxSTR(""), 2, 2, FSxSTR("loosung"),  FSxSTR("S")}, // VVS tyyp 2; veidi erineb VCC 22-st
{0, FSxSTR("i"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("ung"), FSxSTR(""), 2, 2, FSxSTR("loosung"),  FSxSTR("S")}, // VVS tyyp 2; veidi erineb VCC 22-st
{0, FSxSTR("i"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("ung"), FSxSTR(""), 2, 2, FSxSTR("loosung"),  FSxSTR("S")}, // VVS tyyp 2; veidi erineb VCC 22-st
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("ung"), FSxSTR(""), 2, 2, FSxSTR("loosung"),  FSxSTR("S")}, // VVS tyyp 2; veidi erineb VCC 22-st

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("nd"), FSxSTR("V"), 2, 2, FSxSTR("juugend"),  FSxSTR("S")}, // VVS tyyp 2
{0, FSxSTR("i"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("nd"), FSxSTR("V"), 2, 2, FSxSTR("juugend"),  FSxSTR("S")}, // VVS tyyp 2
{0, FSxSTR("i"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("nd"), FSxSTR("V"), 2, 2, FSxSTR("juugend"),  FSxSTR("S")}, // VVS tyyp 2
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("nd"), FSxSTR("V"), 2, 2, FSxSTR("juugend"),  FSxSTR("S")}, // VVS tyyp 2

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("rd"), FSxSTR("V"), 2, 2, FSxSTR("rekord"),  FSxSTR("S")}, // VVS tyyp 2
{0, FSxSTR("i"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("rd"), FSxSTR("V"), 2, 2, FSxSTR("rekord"),  FSxSTR("S")}, // VVS tyyp 2
{0, FSxSTR("i"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("rd"), FSxSTR("V"), 2, 2, FSxSTR("rekord"),  FSxSTR("S")}, // VVS tyyp 2
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("rd"), FSxSTR("V"), 2, 2, FSxSTR("rekord"),  FSxSTR("S")}, // VVS tyyp 2

{2, FSxSTR("se"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ne"), FSxSTR("C"), 2, 9, FSxSTR("paukne"),  FSxSTR("A")}, // VVS tyyp 2
{2, FSxSTR("se"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("ne"), FSxSTR("C"), 2, 9, FSxSTR("paukne"),  FSxSTR("A")}, // VVS tyyp 2
{2, FSxSTR("se"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("ne"), FSxSTR("C"), 2, 9, FSxSTR("paukne"),  FSxSTR("A")}, // VVS tyyp 2
{2, FSxSTR("se"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("ne"), FSxSTR("C"), 2, 9, FSxSTR("paukne"),  FSxSTR("A")}, // VVS tyyp 2

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("s"), FSxSTR(""), 2, 9, FSxSTR("James"),  FSxSTR("H")}, // VVS tyyp 22 ainult nimede jaoks
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("s"), FSxSTR(""), 2, 9, FSxSTR("James"),  FSxSTR("H")}, // VVS tyyp 22 ainult nimede jaoks
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("s"), FSxSTR(""), 2, 9, FSxSTR("James"),  FSxSTR("H")}, // VVS tyyp 22 ainult nimede jaoks
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("s"), FSxSTR(""), 2, 9, FSxSTR("James"),  FSxSTR("H")}, // VVS tyyp 22 ainult nimede jaoks
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("s"), FSxSTR(""), 2, 9, FSxSTR("James"),  FSxSTR("H")}, // VVS tyyp 22 ainult nimede jaoks
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("s"), FSxSTR(""), 2, 9, FSxSTR("James"),  FSxSTR("H")}, // VVS tyyp 22 ainult nimede jaoks

{0, FSxSTR("e"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("s"), FSxSTR("CV"), 2, 2, FSxSTR("Jaanus"),  FSxSTR("H")}, // VVS tyyp 9 nimede jaoks
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("s"), FSxSTR("CV"), 2, 2, FSxSTR("Jaanus"),  FSxSTR("H")}, // VVS tyyp 9 nimede jaoks
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("s"), FSxSTR("CV"), 2, 2, FSxSTR("Jaanus"),  FSxSTR("H")}, // VVS tyyp 9 nimede jaoks
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("s"), FSxSTR("CV"), 2, 2, FSxSTR("Jaanus"),  FSxSTR("H")}, // VVS tyyp 9 nimede jaoks

{0, FSxSTR("e"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ias"), FSxSTR(""), 2, 9, FSxSTR("Jaanus"),  FSxSTR("H")}, // VVS tyyp 9 nimede jaoks
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("ias"), FSxSTR(""), 2, 9, FSxSTR("Jaanus"),  FSxSTR("H")}, // VVS tyyp 9 nimede jaoks
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("ias"), FSxSTR(""), 2, 9, FSxSTR("Jaanus"),  FSxSTR("H")}, // VVS tyyp 9 nimede jaoks
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("ias"), FSxSTR(""), 2, 9, FSxSTR("Jaanus"),  FSxSTR("H")}, // VVS tyyp 9 nimede jaoks

{0, FSxSTR("e"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ies"), FSxSTR(""), 2, 9, FSxSTR("Jaanus"),  FSxSTR("H")}, // VVS tyyp 9 nimede jaoks
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("ies"), FSxSTR(""), 2, 9, FSxSTR("Jaanus"),  FSxSTR("H")}, // VVS tyyp 9 nimede jaoks
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("ies"), FSxSTR(""), 2, 9, FSxSTR("Jaanus"),  FSxSTR("H")}, // VVS tyyp 9 nimede jaoks
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("ies"), FSxSTR(""), 2, 9, FSxSTR("Jaanus"),  FSxSTR("H")}, // VVS tyyp 9 nimede jaoks

{0, FSxSTR("e"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ius"), FSxSTR(""), 2, 9, FSxSTR("Antonius"),  FSxSTR("H")}, // VVS tyyp 9, 11 nimede jaoks
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("ius"), FSxSTR(""), 2, 9, FSxSTR("Antonius"),  FSxSTR("H")}, // VVS tyyp 9, 11 nimede jaoks
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("ius"), FSxSTR(""), 2, 9, FSxSTR("Antonius"),  FSxSTR("H")}, // VVS tyyp 9, 11 nimede jaoks
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("ius"), FSxSTR(""), 2, 9, FSxSTR("Antonius"),  FSxSTR("H")}, // VVS tyyp 9, 11 nimede jaoks

{0, FSxSTR("e"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ios"), FSxSTR(""), 2, 9, FSxSTR("Jaanus"),  FSxSTR("H")}, // VVS tyyp 9 nimede jaoks
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("ios"), FSxSTR(""), 2, 9, FSxSTR("Jaanus"),  FSxSTR("H")}, // VVS tyyp 9 nimede jaoks
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("ios"), FSxSTR(""), 2, 9, FSxSTR("Jaanus"),  FSxSTR("H")}, // VVS tyyp 9 nimede jaoks
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("ios"), FSxSTR(""), 2, 9, FSxSTR("Jaanus"),  FSxSTR("H")}, // VVS tyyp 9 nimede jaoks

{0, FSxSTR("e"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("s"), FSxSTR("CV"), 3, 9, FSxSTR("Homeros"),  FSxSTR("H")}, // VVS tyyp 11 nimede jaoks
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("s"), FSxSTR("CV"), 3, 9, FSxSTR("Homeros"),  FSxSTR("H")}, // VVS tyyp 11 nimede jaoks
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("s"), FSxSTR("CV"), 3, 9, FSxSTR("Homeros"),  FSxSTR("H")}, // VVS tyyp 11 nimede jaoks
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("s"), FSxSTR("CV"), 3, 9, FSxSTR("Homeros"),  FSxSTR("H")}, // VVS tyyp 11 nimede jaoks

{0, FSxSTR("e"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("s"), FSxSTR("CVCV"), 2, 2, FSxSTR("rakis"),  FSxSTR("S")}, // VVS tyyp 9
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("s"), FSxSTR("CVCV"), 2, 2, FSxSTR("rakis"),  FSxSTR("S")}, // VVS tyyp 9
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("s"), FSxSTR("CVCV"), 2, 2, FSxSTR("rakis"),  FSxSTR("S")}, // VVS tyyp 9
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("s"), FSxSTR("CVCV"), 2, 2, FSxSTR("rakis"),  FSxSTR("S")}, // VVS tyyp 9

{0, FSxSTR("e"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("s"), FSxSTR("CCV"), 2, 2, FSxSTR("sundus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11; valesti kui on 2 va'lde
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("s"), FSxSTR("CCV"), 2, 2, FSxSTR("sundus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11; valesti kui on 2 va'lde
{0, FSxSTR(""), FSxSTR("se"), FSxSTR("adt, "), FSxSTR("s"), FSxSTR("CCV"), 2, 2, FSxSTR("sundus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11; valesti kui on 2 va'lde
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("s"), FSxSTR("CCV"), 2, 2, FSxSTR("sundus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11; valesti kui on 2 va'lde
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("s"), FSxSTR("CCV"), 2, 2, FSxSTR("sundus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11; valesti kui on 2 va'lde
{0, FSxSTR(""), FSxSTR("i"), FSxSTR("pl p, "), FSxSTR("s"), FSxSTR("CCV"), 2, 2, FSxSTR("sundus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11; valesti kui on 2 va'lde

{0, FSxSTR("e"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("s"), FSxSTR("CCV"), 4, 9, FSxSTR("ekstravagantsus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11; valesti kui on 2 va'lde
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("s"), FSxSTR("CCV"), 4, 9, FSxSTR("ekstravagantsus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11; valesti kui on 2 va'lde
{0, FSxSTR(""), FSxSTR("se"), FSxSTR("adt, "), FSxSTR("s"), FSxSTR("CCV"), 4, 9, FSxSTR("ekstravagantsus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11; valesti kui on 2 va'lde
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("s"), FSxSTR("CCV"), 4, 9, FSxSTR("ekstravagantsus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11; valesti kui on 2 va'lde
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("s"), FSxSTR("CCV"), 4, 9, FSxSTR("ekstravagantsus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11; valesti kui on 2 va'lde
{0, FSxSTR(""), FSxSTR("i"), FSxSTR("pl p, "), FSxSTR("s"), FSxSTR("CCV"), 4, 9, FSxSTR("ekstravagantsus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11; valesti kui on 2 va'lde

{0, FSxSTR("e"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("s"), FSxSTR("VVCV"), 2, 2, FSxSTR("kuumus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11; valesti kui on 2 va'lde 
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("s"), FSxSTR("VVCV"), 2, 2, FSxSTR("kuumus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11; valesti kui on 2 va'lde 
{0, FSxSTR(""), FSxSTR("se"), FSxSTR("adt, "), FSxSTR("s"), FSxSTR("VVCV"), 2, 2, FSxSTR("kuumus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11; valesti kui on 2 va'lde 
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("s"), FSxSTR("VVCV"), 2, 2, FSxSTR("kuumus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11; valesti kui on 2 va'lde 
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("s"), FSxSTR("VVCV"), 2, 2, FSxSTR("kuumus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11; valesti kui on 2 va'lde 
{0, FSxSTR(""), FSxSTR("i"), FSxSTR("pl p, "), FSxSTR("s"), FSxSTR("VVCV"), 2, 2, FSxSTR("kuumus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11; valesti kui on 2 va'lde 

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("s"), FSxSTR("VV"), 1, 9, FSxSTR("askees"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("s"), FSxSTR("VV"), 1, 9, FSxSTR("askees"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("s"), FSxSTR("VV"), 1, 9, FSxSTR("askees"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("s"), FSxSTR("VV"), 1, 9, FSxSTR("askees"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("s"), FSxSTR("VV"), 1, 9, FSxSTR("askees"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("s"), FSxSTR("VV"), 1, 9, FSxSTR("askees"),  FSxSTR("S")}, // VVS tyyp 22

{0, FSxSTR("e"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("s"), FSxSTR("V"), 2, 9, FSxSTR("kuumus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11; lihtsalt et s-lopulised ikka alati synditaks valesti kui on 2 va'lde 
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("s"), FSxSTR("V"), 2, 9, FSxSTR("kuumus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11; lihtsalt et s-lopulised ikka alati synditaks valesti kui on 2 va'lde 
{0, FSxSTR(""), FSxSTR("se"), FSxSTR("adt, "), FSxSTR("s"), FSxSTR("V"), 2, 9, FSxSTR("kuumus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11; lihtsalt et s-lopulised ikka alati synditaks valesti kui on 2 va'lde 
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("s"), FSxSTR("V"), 2, 9, FSxSTR("kuumus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11; lihtsalt et s-lopulised ikka alati synditaks valesti kui on 2 va'lde 
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("s"), FSxSTR("V"), 2, 9, FSxSTR("kuumus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11; lihtsalt et s-lopulised ikka alati synditaks valesti kui on 2 va'lde 
{0, FSxSTR(""), FSxSTR("i"), FSxSTR("pl p, "), FSxSTR("s"), FSxSTR("V"), 2, 9, FSxSTR("kuumus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11; lihtsalt et s-lopulised ikka alati synditaks valesti kui on 2 va'lde 

{0, FSxSTR("e"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("is"), FSxSTR("VVC"), 2, 2, FSxSTR("suunis"),  FSxSTR("S")}, // VVS tyyp 9 
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("is"), FSxSTR("VVC"), 2, 2, FSxSTR("suunis"),  FSxSTR("S")}, // VVS tyyp 9 
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("is"), FSxSTR("VVC"), 2, 2, FSxSTR("suunis"),  FSxSTR("S")}, // VVS tyyp 9 
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("is"), FSxSTR("VVC"), 2, 2, FSxSTR("suunis"),  FSxSTR("S")}, // VVS tyyp 9 

{0, FSxSTR("e"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("is"), FSxSTR("C"), 3, 3, FSxSTR("laterdis"),  FSxSTR("S")}, // VVS tyyp 11
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("is"), FSxSTR("C"), 3, 3, FSxSTR("laterdis"),  FSxSTR("S")}, // VVS tyyp 11
{0, FSxSTR(""), FSxSTR("se"), FSxSTR("adt, "), FSxSTR("is"), FSxSTR("C"), 3, 3, FSxSTR("laterdis"),  FSxSTR("S")}, // VVS tyyp 11
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("is"), FSxSTR("C"), 3, 3, FSxSTR("laterdis"),  FSxSTR("S")}, // VVS tyyp 11
{0, FSxSTR(""), FSxSTR("i"), FSxSTR("pl p, "), FSxSTR("is"), FSxSTR("C"), 3, 3, FSxSTR("laterdis"),  FSxSTR("S")}, // VVS tyyp 11

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("iis"), FSxSTR(""), 2, 9, FSxSTR("aniis"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("iis"), FSxSTR(""), 2, 9, FSxSTR("aniis"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("iis"), FSxSTR(""), 2, 9, FSxSTR("aniis"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("iis"), FSxSTR(""), 2, 9, FSxSTR("aniis"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("iis"), FSxSTR(""), 2, 9, FSxSTR("aniis"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("iis"), FSxSTR(""), 2, 9, FSxSTR("aniis"),  FSxSTR("S")}, // VVS tyyp 22

{0, FSxSTR("e"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("us"), FSxSTR("CVC"), 3, 3, FSxSTR("plahvatus"),  FSxSTR("S")}, // VVS tyyp 11
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("us"), FSxSTR("CVC"), 3, 3, FSxSTR("plahvatus"),  FSxSTR("S")}, // VVS tyyp 11
{0, FSxSTR(""), FSxSTR("se"), FSxSTR("adt, "), FSxSTR("us"), FSxSTR("CVC"), 3, 3, FSxSTR("plahvatus"),  FSxSTR("S")}, // VVS tyyp 11
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("us"), FSxSTR("CVC"), 3, 3, FSxSTR("plahvatus"),  FSxSTR("S")}, // VVS tyyp 11
{0, FSxSTR(""), FSxSTR("i"), FSxSTR("pl p, "), FSxSTR("us"), FSxSTR("CVC"), 3, 3, FSxSTR("plahvatus"),  FSxSTR("S")}, // VVS tyyp 11

{0, FSxSTR("e"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("us"), FSxSTR("CVC"), 4, 9, FSxSTR("erutatus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("us"), FSxSTR("CVC"), 4, 9, FSxSTR("erutatus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11
{0, FSxSTR(""), FSxSTR("se"), FSxSTR("adt, "), FSxSTR("us"), FSxSTR("CVC"), 4, 9, FSxSTR("erutatus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("us"), FSxSTR("CVC"), 4, 9, FSxSTR("erutatus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("us"), FSxSTR("CVC"), 4, 9, FSxSTR("erutatus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11
{0, FSxSTR(""), FSxSTR("i"), FSxSTR("pl p, "), FSxSTR("us"), FSxSTR("CVC"), 4, 9, FSxSTR("erutatus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("uus"), FSxSTR(""), 1, 9, FSxSTR("arbuus"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("uus"), FSxSTR(""), 1, 9, FSxSTR("arbuus"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("uus"), FSxSTR(""), 1, 9, FSxSTR("arbuus"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("uus"), FSxSTR(""), 1, 9, FSxSTR("arbuus"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("uus"), FSxSTR(""), 1, 9, FSxSTR("arbuus"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("uus"), FSxSTR(""), 1, 9, FSxSTR("arbuus"),  FSxSTR("S")}, // VVS tyyp 22

{0, FSxSTR("e"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("dus"), FSxSTR("C"), 3, 9, FSxSTR("harvendus"),  FSxSTR("S")}, // VVS tyyp 11
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("dus"), FSxSTR("C"), 3, 9, FSxSTR("harvendus"),  FSxSTR("S")}, // VVS tyyp 11
{0, FSxSTR(""), FSxSTR("se"), FSxSTR("adt, "), FSxSTR("dus"), FSxSTR("C"), 3, 9, FSxSTR("harvendus"),  FSxSTR("S")}, // VVS tyyp 11
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("dus"), FSxSTR("C"), 3, 9, FSxSTR("harvendus"),  FSxSTR("S")}, // VVS tyyp 11
{0, FSxSTR(""), FSxSTR("i"), FSxSTR("pl p, "), FSxSTR("dus"), FSxSTR("C"), 3, 9, FSxSTR("harvendus"),  FSxSTR("S")}, // VVS tyyp 11

{0, FSxSTR("e"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("lus"), FSxSTR("VVC"), 2, 9, FSxSTR("katoliiklus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("lus"), FSxSTR("VVC"), 2, 9, FSxSTR("katoliiklus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11
{0, FSxSTR(""), FSxSTR("se"), FSxSTR("adt, "), FSxSTR("lus"), FSxSTR("VVC"), 2, 9, FSxSTR("katoliiklus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("lus"), FSxSTR("VVC"), 2, 9, FSxSTR("katoliiklus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("lus"), FSxSTR("VVC"), 2, 9, FSxSTR("katoliiklus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11
{0, FSxSTR(""), FSxSTR("i"), FSxSTR("pl p, "), FSxSTR("lus"), FSxSTR("VVC"), 2, 9, FSxSTR("katoliiklus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11

{0, FSxSTR("e"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("sklus"), FSxSTR(""), 3, 9, FSxSTR("tantsisklus"),  FSxSTR("S")}, // VVS tyyp 11
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("sklus"), FSxSTR(""), 3, 9, FSxSTR("tantsisklus"),  FSxSTR("S")}, // VVS tyyp 11
{0, FSxSTR(""), FSxSTR("se"), FSxSTR("adt, "), FSxSTR("sklus"), FSxSTR(""), 3, 9, FSxSTR("tantsisklus"),  FSxSTR("S")}, // VVS tyyp 11
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("sklus"), FSxSTR(""), 3, 9, FSxSTR("tantsisklus"),  FSxSTR("S")}, // VVS tyyp 11
{0, FSxSTR(""), FSxSTR("i"), FSxSTR("pl p, "), FSxSTR("sklus"), FSxSTR(""), 3, 9, FSxSTR("tantsisklus"),  FSxSTR("S")}, // VVS tyyp 11

{0, FSxSTR("e"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("sus"), FSxSTR("VVC"), 2, 9, FSxSTR("modaalsus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("sus"), FSxSTR("VVC"), 2, 9, FSxSTR("modaalsus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11
{0, FSxSTR(""), FSxSTR("se"), FSxSTR("adt, "), FSxSTR("sus"), FSxSTR("VVC"), 2, 9, FSxSTR("modaalsus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("sus"), FSxSTR("VVC"), 2, 9, FSxSTR("modaalsus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("sus"), FSxSTR("VVC"), 2, 9, FSxSTR("modaalsus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11
{0, FSxSTR(""), FSxSTR("i"), FSxSTR("pl p, "), FSxSTR("sus"), FSxSTR("VVC"), 2, 9, FSxSTR("modaalsus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11

{0, FSxSTR("e"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("tsus"), FSxSTR("C"), 2, 9, FSxSTR("autentsus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("tsus"), FSxSTR("C"), 2, 9, FSxSTR("autentsus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11
{0, FSxSTR(""), FSxSTR("se"), FSxSTR("adt, "), FSxSTR("tsus"), FSxSTR("C"), 2, 9, FSxSTR("autentsus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("tsus"), FSxSTR("C"), 2, 9, FSxSTR("autentsus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("tsus"), FSxSTR("C"), 2, 9, FSxSTR("autentsus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11
{0, FSxSTR(""), FSxSTR("i"), FSxSTR("pl p, "), FSxSTR("tsus"), FSxSTR("C"), 2, 9, FSxSTR("autentsus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11

{0, FSxSTR("e"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ntlus"), FSxSTR(""), 2, 9, FSxSTR("sektantlus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("ntlus"), FSxSTR(""), 2, 9, FSxSTR("sektantlus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11
{0, FSxSTR(""), FSxSTR("se"), FSxSTR("adt, "), FSxSTR("ntlus"), FSxSTR(""), 2, 9, FSxSTR("sektantlus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("ntlus"), FSxSTR(""), 2, 9, FSxSTR("sektantlus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("ntlus"), FSxSTR(""), 2, 9, FSxSTR("sektantlus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11
{0, FSxSTR(""), FSxSTR("i"), FSxSTR("pl p, "), FSxSTR("ntlus"), FSxSTR(""), 2, 9, FSxSTR("sektantlus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11

{0, FSxSTR("e"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("arius"), FSxSTR(""), 3, 9, FSxSTR("ordinaarius"),  FSxSTR("S")}, // VVS tyyp 11
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("arius"), FSxSTR(""), 3, 9, FSxSTR("ordinaarius"),  FSxSTR("S")}, // VVS tyyp 11
{0, FSxSTR(""), FSxSTR("se"), FSxSTR("adt, "), FSxSTR("arius"), FSxSTR(""), 3, 9, FSxSTR("ordinaarius"),  FSxSTR("S")}, // VVS tyyp 11
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("arius"), FSxSTR(""), 3, 9, FSxSTR("ordinaarius"),  FSxSTR("S")}, // VVS tyyp 11
{0, FSxSTR(""), FSxSTR("i"), FSxSTR("pl p, "), FSxSTR("arius"), FSxSTR(""), 3, 9, FSxSTR("ordinaarius"),  FSxSTR("S")}, // VVS tyyp 11

{0, FSxSTR("e"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ikkus"), FSxSTR("C"), 2, 9, FSxSTR("muutlikkus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("ikkus"), FSxSTR("C"), 2, 9, FSxSTR("muutlikkus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11
{0, FSxSTR(""), FSxSTR("se"), FSxSTR("adt, "), FSxSTR("ikkus"), FSxSTR("C"), 2, 9, FSxSTR("muutlikkus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("ikkus"), FSxSTR("C"), 2, 9, FSxSTR("muutlikkus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("ikkus"), FSxSTR("C"), 2, 9, FSxSTR("muutlikkus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11
{0, FSxSTR(""), FSxSTR("i"), FSxSTR("pl p, "), FSxSTR("ikkus"), FSxSTR("C"), 2, 9, FSxSTR("muutlikkus"),  FSxSTR("S")}, // VVS tyyp 9 ja 11

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ss"), FSxSTR("V"), 1, 1, FSxSTR("fess"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("ss"), FSxSTR("V"), 1, 1, FSxSTR("fess"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("ss"), FSxSTR("V"), 1, 1, FSxSTR("fess"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("ss"), FSxSTR("V"), 1, 1, FSxSTR("fess"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("ss"), FSxSTR("V"), 1, 1, FSxSTR("fess"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("ss"), FSxSTR("V"), 1, 1, FSxSTR("fess"),  FSxSTR("S")}, // VVS tyyp 22

{1, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ss"), FSxSTR("L"), 1, 1, FSxSTR("kurss"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("ss"), FSxSTR("L"), 1, 1, FSxSTR("kurss"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("ss"), FSxSTR("L"), 1, 1, FSxSTR("kurss"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("ss"), FSxSTR("L"), 1, 1, FSxSTR("kurss"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("ss"), FSxSTR("L"), 1, 1, FSxSTR("kurss"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("ss"), FSxSTR("L"), 1, 1, FSxSTR("kurss"),  FSxSTR("S")}, // VVS tyyp 22

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ks"), FSxSTR(""), 2, 2, FSxSTR("apeks"),  FSxSTR("S")}, // VVS tyyp 2 
{0, FSxSTR("i"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("ks"), FSxSTR(""), 2, 2, FSxSTR("apeks"),  FSxSTR("S")}, // VVS tyyp 2 
{0, FSxSTR("i"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("ks"), FSxSTR(""), 2, 2, FSxSTR("apeks"),  FSxSTR("S")}, // VVS tyyp 2 
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("ks"), FSxSTR(""), 2, 2, FSxSTR("apeks"),  FSxSTR("S")}, // VVS tyyp 2 

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("x"), FSxSTR(""), 2, 2, FSxSTR("Unix"),  FSxSTR("H")}, // VVS tyyp 2 parisnimi
{0, FSxSTR("i"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("x"), FSxSTR(""), 2, 2, FSxSTR("Unix"),  FSxSTR("H")}, // VVS tyyp 2 parisnimi
{0, FSxSTR("i"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("x"), FSxSTR(""), 2, 2, FSxSTR("Unix"),  FSxSTR("H")}, // VVS tyyp 2 parisnimi
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("x"), FSxSTR(""), 2, 2, FSxSTR("Unix"),  FSxSTR("H")}, // VVS tyyp 2 parisnimi

{1, FSxSTR(""), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("gas"), FSxSTR(""), 3, 9, FSxSTR("heeringas"),  FSxSTR("S")}, // VVS tyyp 2 
{1, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("gas"), FSxSTR(""), 3, 9, FSxSTR("heeringas"),  FSxSTR("S")}, // VVS tyyp 2 
{1, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("gas"), FSxSTR(""), 3, 9, FSxSTR("heeringas"),  FSxSTR("S")}, // VVS tyyp 2 
{1, FSxSTR(""), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("gas"), FSxSTR(""), 3, 9, FSxSTR("heeringas"),  FSxSTR("S")}, // VVS tyyp 2 

{1, FSxSTR(""), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("jas"), FSxSTR(""), 2, 9, FSxSTR("kreemjas"),  FSxSTR("A")}, // VVS tyyp 2 
{1, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("jas"), FSxSTR(""), 2, 9, FSxSTR("kreemjas"),  FSxSTR("A")}, // VVS tyyp 2 
{1, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("jas"), FSxSTR(""), 2, 9, FSxSTR("kreemjas"),  FSxSTR("A")}, // VVS tyyp 2 
{1, FSxSTR(""), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("jas"), FSxSTR(""), 2, 9, FSxSTR("kreemjas"),  FSxSTR("A")}, // VVS tyyp 2 

{1, FSxSTR(""), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("kas"), FSxSTR(""), 3, 9, FSxSTR("jumakas"),  FSxSTR("S")}, // VVS tyyp 2 
{1, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("kas"), FSxSTR(""), 3, 9, FSxSTR("jumakas"),  FSxSTR("S")}, // VVS tyyp 2 
{1, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("kas"), FSxSTR(""), 3, 9, FSxSTR("jumakas"),  FSxSTR("S")}, // VVS tyyp 2 
{1, FSxSTR(""), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("kas"), FSxSTR(""), 3, 9, FSxSTR("jumakas"),  FSxSTR("S")}, // VVS tyyp 2 

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("iits"), FSxSTR(""), 1, 9, FSxSTR("noviits"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("iits"), FSxSTR(""), 1, 9, FSxSTR("noviits"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("iits"), FSxSTR(""), 1, 9, FSxSTR("noviits"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("iits"), FSxSTR(""), 1, 9, FSxSTR("noviits"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("iits"), FSxSTR(""), 1, 9, FSxSTR("noviits"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("iits"), FSxSTR(""), 1, 9, FSxSTR("noviits"),  FSxSTR("S")}, // VVS tyyp 22

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("nts"), FSxSTR(""), 1, 9, FSxSTR("distants"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("nts"), FSxSTR(""), 1, 9, FSxSTR("distants"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("nts"), FSxSTR(""), 1, 9, FSxSTR("distants"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("nts"), FSxSTR(""), 1, 9, FSxSTR("distants"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("nts"), FSxSTR(""), 1, 9, FSxSTR("distants"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("nts"), FSxSTR(""), 1, 9, FSxSTR("distants"),  FSxSTR("S")}, // VVS tyyp 22

{1, FSxSTR(""), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("nud"), FSxSTR(""), 2, 9, FSxSTR("kogenud"),  FSxSTR("A")}, // VVS tyyp 2 
{1, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("nud"), FSxSTR(""), 2, 9, FSxSTR("kogenud"),  FSxSTR("A")}, // VVS tyyp 2 
{1, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("nud"), FSxSTR(""), 2, 9, FSxSTR("kogenud"),  FSxSTR("A")}, // VVS tyyp 2 
{1, FSxSTR(""), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("nud"), FSxSTR(""), 2, 9, FSxSTR("kogenud"),  FSxSTR("A")}, // VVS tyyp 2 

{1, FSxSTR(""), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("tud"), FSxSTR(""), 2, 9, FSxSTR("armastatud"),  FSxSTR("A")}, // VVS tyyp 2 
{1, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("tud"), FSxSTR(""), 2, 9, FSxSTR("armastatud"),  FSxSTR("A")}, // VVS tyyp 2 
{1, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("tud"), FSxSTR(""), 2, 9, FSxSTR("armastatud"),  FSxSTR("A")}, // VVS tyyp 2 
{1, FSxSTR(""), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("tud"), FSxSTR(""), 2, 9, FSxSTR("armastatud"),  FSxSTR("A")}, // VVS tyyp 2 

{1, FSxSTR(""), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("dud"), FSxSTR(""), 2, 9, FSxSTR("toodud"),  FSxSTR("A")}, // VVS tyyp 2 
{1, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("dud"), FSxSTR(""), 2, 9, FSxSTR("toodud"),  FSxSTR("A")}, // VVS tyyp 2 
{1, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("dud"), FSxSTR(""), 2, 9, FSxSTR("toodud"),  FSxSTR("A")}, // VVS tyyp 2 
{1, FSxSTR(""), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("dud"), FSxSTR(""), 2, 9, FSxSTR("toodud"),  FSxSTR("A")}, // VVS tyyp 2 

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ats"), FSxSTR(""), 2, 2, FSxSTR("nokats"),  FSxSTR("S")}, // VVS tyyp 2
{0, FSxSTR("i"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("ats"), FSxSTR(""), 2, 2, FSxSTR("nokats"),  FSxSTR("S")}, // VVS tyyp 2
{0, FSxSTR("i"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("ats"), FSxSTR(""), 2, 2, FSxSTR("nokats"),  FSxSTR("S")}, // VVS tyyp 2
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("ats"), FSxSTR(""), 2, 2, FSxSTR("nokats"),  FSxSTR("S")}, // VVS tyyp 2

{0, FSxSTR("a"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("its"), FSxSTR(""), 2, 2, FSxSTR("uulits"),  FSxSTR("S")}, // VVS tyyp 2
{0, FSxSTR("a"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("its"), FSxSTR(""), 2, 2, FSxSTR("uulits"),  FSxSTR("S")}, // VVS tyyp 2
{0, FSxSTR("a"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("its"), FSxSTR(""), 2, 2, FSxSTR("uulits"),  FSxSTR("S")}, // VVS tyyp 2
{0, FSxSTR("a"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("its"), FSxSTR(""), 2, 2, FSxSTR("uulits"),  FSxSTR("S")}, // VVS tyyp 2

{0, FSxSTR(""), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("vere"), FSxSTR(""), 3, 9, FSxSTR("Adavere"),  FSxSTR("H")}, // VVS tyyp 16
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("vere"), FSxSTR(""), 3, 9, FSxSTR("Adavere"),  FSxSTR("H")}, // VVS tyyp 16
{1, FSxSTR("re"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("vere"), FSxSTR(""), 3, 9, FSxSTR("Adavere"),  FSxSTR("H")}, // VVS tyyp 16
{0, FSxSTR(""), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("vere"), FSxSTR(""), 3, 9, FSxSTR("Adavere"),  FSxSTR("H")}, // VVS tyyp 16
{0, FSxSTR(""), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("vere"), FSxSTR(""), 3, 9, FSxSTR("Adavere"),  FSxSTR("H")}, // VVS tyyp 16

{0, FSxSTR(""), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("e"), FSxSTR("C"), 2, 9, FSxSTR("kunde"),  FSxSTR("S")}, // VVS tyyp 16
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("e"), FSxSTR("C"), 2, 9, FSxSTR("kunde"),  FSxSTR("S")}, // VVS tyyp 16
{0, FSxSTR(""), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("e"), FSxSTR("C"), 2, 9, FSxSTR("kunde"),  FSxSTR("S")}, // VVS tyyp 16
{0, FSxSTR(""), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("e"), FSxSTR("C"), 2, 9, FSxSTR("kunde"),  FSxSTR("S")}, // VVS tyyp 16

{2, FSxSTR("se"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("kene"), FSxSTR("V"), 3, 9, FSxSTR("mehikene"),  FSxSTR("S")}, // VVS tyyp 12 omadussõnu moodust. sellega tegelt üliharva 
{2, FSxSTR("s"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("kene"), FSxSTR("V"), 3, 9, FSxSTR("mehikene"),  FSxSTR("S")}, // VVS tyyp 12
{2, FSxSTR("s"), FSxSTR("se"), FSxSTR("adt, "), FSxSTR("kene"), FSxSTR("V"), 3, 9, FSxSTR("mehikene"),  FSxSTR("S")}, // VVS tyyp 12
{2, FSxSTR("s"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("kene"), FSxSTR("V"), 3, 9, FSxSTR("mehikene"),  FSxSTR("S")}, // VVS tyyp 12
{2, FSxSTR("s"), FSxSTR("i"), FSxSTR("pl p, "), FSxSTR("kene"), FSxSTR("V"), 3, 9, FSxSTR("mehikene"),  FSxSTR("S")}, // VVS tyyp 12

{0, FSxSTR("se"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ke"), FSxSTR("V"), 3, 9, FSxSTR("tossike"),  FSxSTR("S")}, // VVS tyyp 12 omadussõnu moodust. sellega tegelt üliharva 
{0, FSxSTR("s"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("ke"), FSxSTR("V"), 3, 9, FSxSTR("tossike"),  FSxSTR("S")}, // VVS tyyp 12
{0, FSxSTR("s"), FSxSTR("se"), FSxSTR("adt, "), FSxSTR("ke"), FSxSTR("V"), 3, 9, FSxSTR("tossike"),  FSxSTR("S")}, // VVS tyyp 12
{0, FSxSTR("s"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("ke"), FSxSTR("V"), 3, 9, FSxSTR("tossike"),  FSxSTR("S")}, // VVS tyyp 12
{0, FSxSTR("s"), FSxSTR("i"), FSxSTR("pl p, "), FSxSTR("ke"), FSxSTR("V"), 3, 9, FSxSTR("tossike"),  FSxSTR("S")}, // VVS tyyp 12

{2, FSxSTR("se"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ne"), FSxSTR("V"), 3, 3, FSxSTR("prahine"),  FSxSTR("A")}, // VVS tyyp 10
{2, FSxSTR("s"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("ne"), FSxSTR("V"), 3, 3, FSxSTR("prahine"),  FSxSTR("A")}, // VVS tyyp 10
{2, FSxSTR("s"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("ne"), FSxSTR("V"), 3, 3, FSxSTR("prahine"),  FSxSTR("A")}, // VVS tyyp 10
{2, FSxSTR("se"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("ne"), FSxSTR("V"), 3, 3, FSxSTR("prahine"),  FSxSTR("A")}, // VVS tyyp 10

{2, FSxSTR("se"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ne"), FSxSTR("VV"), 2, 2, FSxSTR("praene"),  FSxSTR("A")}, // VVS tyyp 10
{2, FSxSTR("s"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("ne"), FSxSTR("VV"), 2, 2, FSxSTR("praene"),  FSxSTR("A")}, // VVS tyyp 10
{2, FSxSTR("s"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("ne"), FSxSTR("VV"), 2, 2, FSxSTR("praene"),  FSxSTR("A")}, // VVS tyyp 10
{2, FSxSTR("se"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("ne"), FSxSTR("VV"), 2, 2, FSxSTR("praene"),  FSxSTR("A")}, // VVS tyyp 10

{2, FSxSTR("se"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ne"), FSxSTR("V"), 4, 9, FSxSTR("vanaldane"),  FSxSTR("A")}, // VVS tyyp 12
{2, FSxSTR("s"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("ne"), FSxSTR("V"), 4, 9, FSxSTR("vanaldane"),  FSxSTR("A")}, // VVS tyyp 12
{2, FSxSTR("s"), FSxSTR("se"), FSxSTR("adt, "), FSxSTR("ne"), FSxSTR("V"), 4, 9, FSxSTR("vanaldane"),  FSxSTR("A")}, // VVS tyyp 12
{2, FSxSTR("s"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("ne"), FSxSTR("V"), 4, 9, FSxSTR("vanaldane"),  FSxSTR("A")}, // VVS tyyp 12
{2, FSxSTR("s"), FSxSTR("i"), FSxSTR("pl p, "), FSxSTR("ne"), FSxSTR("V"), 4, 9, FSxSTR("vanaldane"),  FSxSTR("A")}, // VVS tyyp 12

{2, FSxSTR("se"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ine"), FSxSTR("VVCC"), 3, 3, FSxSTR("juurmine"),  FSxSTR("A")}, // VVS tyyp 10 ja 12; =mine?
{2, FSxSTR("s"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("ine"), FSxSTR("VVCC"), 3, 3, FSxSTR("juurmine"),  FSxSTR("A")}, // VVS tyyp 10 ja 12; =mine?
{2, FSxSTR("s"), FSxSTR("se"), FSxSTR("adt, "), FSxSTR("ine"), FSxSTR("VVCC"), 3, 3, FSxSTR("juurmine"),  FSxSTR("A")}, // VVS tyyp 10 ja 12; =mine?
{2, FSxSTR("s"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("ine"), FSxSTR("VVCC"), 3, 3, FSxSTR("juurmine"),  FSxSTR("A")}, // VVS tyyp 10 ja 12; =mine?
{2, FSxSTR("se"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("ine"), FSxSTR("VVCC"), 3, 3, FSxSTR("juurmine"),  FSxSTR("A")}, // VVS tyyp 10 ja 12; =mine?
{2, FSxSTR("s"), FSxSTR("i"), FSxSTR("pl p, "), FSxSTR("ine"), FSxSTR("VVCC"), 3, 3, FSxSTR("juurmine"),  FSxSTR("A")}, // VVS tyyp 10 ja 12; =mine?

{2, FSxSTR("se"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ine"), FSxSTR("VCCC"), 3, 3, FSxSTR("servmine"),  FSxSTR("A")}, // VVS tyyp 10 ja 12; =mine?
{2, FSxSTR("s"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("ine"), FSxSTR("VCCC"), 3, 3, FSxSTR("servmine"),  FSxSTR("A")}, // VVS tyyp 10 ja 12; =mine?
{2, FSxSTR("s"), FSxSTR("se"), FSxSTR("adt, "), FSxSTR("ine"), FSxSTR("VCCC"), 3, 3, FSxSTR("servmine"),  FSxSTR("A")}, // VVS tyyp 10 ja 12; =mine?
{2, FSxSTR("s"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("ine"), FSxSTR("VCCC"), 3, 3, FSxSTR("servmine"),  FSxSTR("A")}, // VVS tyyp 10 ja 12; =mine?
{2, FSxSTR("se"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("ine"), FSxSTR("VCCC"), 3, 3, FSxSTR("servmine"),  FSxSTR("A")}, // VVS tyyp 10 ja 12; =mine?
{2, FSxSTR("s"), FSxSTR("i"), FSxSTR("pl p, "), FSxSTR("ine"), FSxSTR("VCCC"), 3, 3, FSxSTR("servmine"),  FSxSTR("A")}, // VVS tyyp 10 ja 12; =mine?

{2, FSxSTR("se"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("lane"), FSxSTR("CC"), 3, 9, FSxSTR("karsklane"),  FSxSTR("S")}, // VVS tyyp 10 ja 12
{2, FSxSTR("s"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("lane"), FSxSTR("CC"), 3, 9, FSxSTR("karsklane"),  FSxSTR("S")}, // VVS tyyp 10 ja 12
{2, FSxSTR("s"), FSxSTR("se"), FSxSTR("adt, "), FSxSTR("lane"), FSxSTR("CC"), 3, 9, FSxSTR("karsklane"),  FSxSTR("S")}, // VVS tyyp 10 ja 12
{2, FSxSTR("s"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("lane"), FSxSTR("CC"), 3, 9, FSxSTR("karsklane"),  FSxSTR("S")}, // VVS tyyp 10 ja 12
{2, FSxSTR("se"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("lane"), FSxSTR("CC"), 3, 9, FSxSTR("karsklane"),  FSxSTR("S")}, // VVS tyyp 10 ja 12
{2, FSxSTR("s"), FSxSTR("i"), FSxSTR("pl p, "), FSxSTR("lane"), FSxSTR("CC"), 3, 9, FSxSTR("karsklane"),  FSxSTR("S")}, // VVS tyyp 10 ja 12

{2, FSxSTR("se"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("lane"), FSxSTR("VVC"), 3, 9, FSxSTR("itaallane"),  FSxSTR("S")}, // VVS tyyp 10 ja 12
{2, FSxSTR("s"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("lane"), FSxSTR("VVC"), 3, 9, FSxSTR("itaallane"),  FSxSTR("S")}, // VVS tyyp 10 ja 12
{2, FSxSTR("s"), FSxSTR("se"), FSxSTR("adt, "), FSxSTR("lane"), FSxSTR("VVC"), 3, 9, FSxSTR("itaallane"),  FSxSTR("S")}, // VVS tyyp 10 ja 12
{2, FSxSTR("s"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("lane"), FSxSTR("VVC"), 3, 9, FSxSTR("itaallane"),  FSxSTR("S")}, // VVS tyyp 10 ja 12
{2, FSxSTR("se"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("lane"), FSxSTR("VVC"), 3, 9, FSxSTR("itaallane"),  FSxSTR("S")}, // VVS tyyp 10 ja 12
{2, FSxSTR("s"), FSxSTR("i"), FSxSTR("pl p, "), FSxSTR("lane"), FSxSTR("VVC"), 3, 9, FSxSTR("itaallane"),  FSxSTR("S")}, // VVS tyyp 10 ja 12

{2, FSxSTR("se"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("lane"), FSxSTR("P"), 3, 3, FSxSTR("britlane"),  FSxSTR("S")}, // VVS tyyp 10 ja 12
{2, FSxSTR("s"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("lane"), FSxSTR("P"), 3, 3, FSxSTR("britlane"),  FSxSTR("S")}, // VVS tyyp 10 ja 12
{2, FSxSTR("s"), FSxSTR("se"), FSxSTR("adt, "), FSxSTR("lane"), FSxSTR("P"), 3, 3, FSxSTR("britlane"),  FSxSTR("S")}, // VVS tyyp 10 ja 12
{2, FSxSTR("s"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("lane"), FSxSTR("P"), 3, 3, FSxSTR("britlane"),  FSxSTR("S")}, // VVS tyyp 10 ja 12
{2, FSxSTR("se"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("lane"), FSxSTR("P"), 3, 3, FSxSTR("britlane"),  FSxSTR("S")}, // VVS tyyp 10 ja 12
{2, FSxSTR("s"), FSxSTR("i"), FSxSTR("pl p, "), FSxSTR("lane"), FSxSTR("P"), 3, 3, FSxSTR("britlane"),  FSxSTR("S")}, // VVS tyyp 10 ja 12

{2, FSxSTR("se"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("lane"), FSxSTR("P"), 4, 9, FSxSTR("korsiklane"),  FSxSTR("S")}, // VVS tyyp 12
{2, FSxSTR("s"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("lane"), FSxSTR("P"), 4, 9, FSxSTR("korsiklane"),  FSxSTR("S")}, // VVS tyyp 12
{2, FSxSTR("s"), FSxSTR("se"), FSxSTR("adt, "), FSxSTR("lane"), FSxSTR("P"), 4, 9, FSxSTR("korsiklane"),  FSxSTR("S")}, // VVS tyyp 12
{2, FSxSTR("s"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("lane"), FSxSTR("P"), 4, 9, FSxSTR("korsiklane"),  FSxSTR("S")}, // VVS tyyp 12
{2, FSxSTR("s"), FSxSTR("i"), FSxSTR("pl p, "), FSxSTR("lane"), FSxSTR("P"), 4, 9, FSxSTR("korsiklane"),  FSxSTR("S")}, // VVS tyyp 12

{2, FSxSTR("se"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("lane"), FSxSTR(""), 4, 4, FSxSTR("enamlane"),  FSxSTR("S")}, // VVS tyyp 12
{2, FSxSTR("s"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("lane"), FSxSTR(""), 4, 4, FSxSTR("enamlane"),  FSxSTR("S")}, // VVS tyyp 12
{2, FSxSTR("s"), FSxSTR("se"), FSxSTR("adt, "), FSxSTR("lane"), FSxSTR(""), 4, 4, FSxSTR("enamlane"),  FSxSTR("S")}, // VVS tyyp 12
{2, FSxSTR("s"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("lane"), FSxSTR(""), 4, 4, FSxSTR("enamlane"),  FSxSTR("S")}, // VVS tyyp 12
{2, FSxSTR("s"), FSxSTR("i"), FSxSTR("pl p, "), FSxSTR("lane"), FSxSTR(""), 4, 4, FSxSTR("enamlane"),  FSxSTR("S")}, // VVS tyyp 12

{2, FSxSTR("se"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("line"), FSxSTR("VV"), 3, 9, FSxSTR("kiuline"),  FSxSTR("A")}, // VVS tyyp 10 ja 12
{2, FSxSTR("s"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("line"), FSxSTR("VV"), 3, 9, FSxSTR("kiuline"),  FSxSTR("A")}, // VVS tyyp 10 ja 12
{2, FSxSTR("s"), FSxSTR("se"), FSxSTR("adt, "), FSxSTR("line"), FSxSTR("VV"), 3, 9, FSxSTR("kiuline"),  FSxSTR("A")}, // VVS tyyp 10 ja 12
{2, FSxSTR("s"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("line"), FSxSTR("VV"), 3, 9, FSxSTR("kiuline"),  FSxSTR("A")}, // VVS tyyp 10 ja 12
{2, FSxSTR("se"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("line"), FSxSTR("VV"), 3, 9, FSxSTR("kiuline"),  FSxSTR("A")}, // VVS tyyp 10 ja 12
{2, FSxSTR("s"), FSxSTR("i"), FSxSTR("pl p, "), FSxSTR("line"), FSxSTR("VV"), 3, 9, FSxSTR("kiuline"),  FSxSTR("A")}, // VVS tyyp 10 ja 12

{2, FSxSTR("se"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("stikune"), FSxSTR(""), 5, 9, FSxSTR("ligistikune"),  FSxSTR("A")}, // VVS tyyp 10 ja 12
{2, FSxSTR("s"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("stikune"), FSxSTR(""), 5, 9, FSxSTR("ligistikune"),  FSxSTR("A")}, // VVS tyyp 10 ja 12
{2, FSxSTR("s"), FSxSTR("se"), FSxSTR("adt, "), FSxSTR("stikune"), FSxSTR(""), 5, 9, FSxSTR("ligistikune"),  FSxSTR("A")}, // VVS tyyp 10 ja 12
{2, FSxSTR("s"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("stikune"), FSxSTR(""), 5, 9, FSxSTR("ligistikune"),  FSxSTR("A")}, // VVS tyyp 10 ja 12
{2, FSxSTR("se"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("stikune"), FSxSTR(""), 5, 9, FSxSTR("ligistikune"),  FSxSTR("A")}, // VVS tyyp 10 ja 12
{2, FSxSTR("s"), FSxSTR("i"), FSxSTR("pl p, "), FSxSTR("stikune"), FSxSTR(""), 5, 9, FSxSTR("ligistikune"),  FSxSTR("A")}, // VVS tyyp 10 ja 12

{0, FSxSTR(""), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("a"), FSxSTR("C"), 2, 9, FSxSTR("sopka"),  FSxSTR("S")}, // VVS tyyp 16
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("a"), FSxSTR("C"), 2, 9, FSxSTR("sopka"),  FSxSTR("S")}, // VVS tyyp 16
{0, FSxSTR(""), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("a"), FSxSTR("C"), 2, 9, FSxSTR("sopka"),  FSxSTR("S")}, // VVS tyyp 16
{0, FSxSTR(""), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("a"), FSxSTR("C"), 2, 9, FSxSTR("sopka"),  FSxSTR("S")}, // VVS tyyp 16

{0, FSxSTR(""), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ia"), FSxSTR(""), 2, 9, FSxSTR("meedia"),  FSxSTR("S")}, // VVS tyyp 1
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("ia"), FSxSTR(""), 2, 9, FSxSTR("meedia"),  FSxSTR("S")}, // VVS tyyp 1
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("ia"), FSxSTR(""), 2, 9, FSxSTR("meedia"),  FSxSTR("S")}, // VVS tyyp 1
{0, FSxSTR(""), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("ia"), FSxSTR(""), 2, 9, FSxSTR("meedia"),  FSxSTR("S")}, // VVS tyyp 1

{0, FSxSTR(""), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ja"), FSxSTR(""), 2, 9, FSxSTR("tegija"),  FSxSTR("S")}, // VVS tyyp 1
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("ja"), FSxSTR(""), 2, 9, FSxSTR("tegija"),  FSxSTR("S")}, // VVS tyyp 1
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("ja"), FSxSTR(""), 2, 9, FSxSTR("tegija"),  FSxSTR("S")}, // VVS tyyp 1
{0, FSxSTR(""), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("ja"), FSxSTR(""), 2, 9, FSxSTR("tegija"),  FSxSTR("S")}, // VVS tyyp 1

{0, FSxSTR(""), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ika"), FSxSTR("C"), 3, 9, FSxSTR("paprika"),  FSxSTR("S")}, // VVS tyyp 1
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("ika"), FSxSTR("C"), 3, 9, FSxSTR("paprika"),  FSxSTR("S")}, // VVS tyyp 1
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("ika"), FSxSTR("C"), 3, 9, FSxSTR("paprika"),  FSxSTR("S")}, // VVS tyyp 1
{0, FSxSTR(""), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("ika"), FSxSTR("C"), 3, 9, FSxSTR("paprika"),  FSxSTR("S")}, // VVS tyyp 1

{0, FSxSTR(""), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("la"), FSxSTR(""), 3, 9, FSxSTR("lesila"),  FSxSTR("S")}, // VVS tyyp 1
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("la"), FSxSTR(""), 3, 9, FSxSTR("lesila"),  FSxSTR("S")}, // VVS tyyp 1
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("la"), FSxSTR(""), 3, 9, FSxSTR("lesila"),  FSxSTR("S")}, // VVS tyyp 1
{0, FSxSTR(""), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("la"), FSxSTR(""), 3, 9, FSxSTR("lesila"),  FSxSTR("S")}, // VVS tyyp 1

{0, FSxSTR(""), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("tu"), FSxSTR(""), 2, 9, FSxSTR("ajastu"),  FSxSTR("S")}, // VVS tyyp 1
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("tu"), FSxSTR(""), 2, 9, FSxSTR("ajastu"),  FSxSTR("S")}, // VVS tyyp 1
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("tu"), FSxSTR(""), 2, 9, FSxSTR("ajastu"),  FSxSTR("S")}, // VVS tyyp 1
{0, FSxSTR(""), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("tu"), FSxSTR(""), 2, 9, FSxSTR("ajastu"),  FSxSTR("S")}, // VVS tyyp 1

{0, FSxSTR(""), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("i"), FSxSTR("C"), 2, 9, FSxSTR("marli"),  FSxSTR("S")}, // VVS tyyp 16
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("i"), FSxSTR("C"), 2, 9, FSxSTR("marli"),  FSxSTR("S")}, // VVS tyyp 16
{0, FSxSTR(""), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("i"), FSxSTR("C"), 2, 9, FSxSTR("marli"),  FSxSTR("S")}, // VVS tyyp 16
{0, FSxSTR(""), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("i"), FSxSTR("C"), 2, 9, FSxSTR("marli"),  FSxSTR("S")}, // VVS tyyp 16

{0, FSxSTR(""), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ti"), FSxSTR(""), 3, 3, FSxSTR("valgusti"),  FSxSTR("S")}, // VVS tyyp 1
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("ti"), FSxSTR(""), 3, 3, FSxSTR("valgusti"),  FSxSTR("S")}, // VVS tyyp 1
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("ti"), FSxSTR(""), 3, 3, FSxSTR("valgusti"),  FSxSTR("S")}, // VVS tyyp 1
{1, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("ti"), FSxSTR(""), 3, 3, FSxSTR("valgusti"),  FSxSTR("S")}, // VVS tyyp 1

{0, FSxSTR(""), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("di"), FSxSTR("L"), 3, 3, FSxSTR("kiirendi"),  FSxSTR("S")}, // VVS tyyp 1
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("di"), FSxSTR("L"), 3, 3, FSxSTR("kiirendi"),  FSxSTR("S")}, // VVS tyyp 1
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("di"), FSxSTR("L"), 3, 3, FSxSTR("kiirendi"),  FSxSTR("S")}, // VVS tyyp 1
{1, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("di"), FSxSTR("L"), 3, 3, FSxSTR("kiirendi"),  FSxSTR("S")}, // VVS tyyp 1

{0, FSxSTR(""), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("o"), FSxSTR("C"), 3, 3, FSxSTR("riisiko"),  FSxSTR("S")}, // VVS tyyp 1
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("o"), FSxSTR("C"), 3, 3, FSxSTR("riisiko"),  FSxSTR("S")}, // VVS tyyp 1
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("o"), FSxSTR("C"), 3, 3, FSxSTR("riisiko"),  FSxSTR("S")}, // VVS tyyp 1
{0, FSxSTR(""), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("o"), FSxSTR("C"), 3, 3, FSxSTR("riisiko"),  FSxSTR("S")}, // VVS tyyp 1

{0, FSxSTR(""), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("o"), FSxSTR("C"), 2, 2, FSxSTR("soolo"),  FSxSTR("S")}, // VVS tyyp 16
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("o"), FSxSTR("C"), 2, 2, FSxSTR("soolo"),  FSxSTR("S")}, // VVS tyyp 16
{0, FSxSTR(""), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("o"), FSxSTR("C"), 2, 2, FSxSTR("soolo"),  FSxSTR("S")}, // VVS tyyp 16
{0, FSxSTR(""), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("o"), FSxSTR("C"), 2, 2, FSxSTR("soolo"),  FSxSTR("S")}, // VVS tyyp 16

{0, FSxSTR(""), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("io"), FSxSTR(""), 2, 9, FSxSTR("raadio"),  FSxSTR("S")}, // VVS tyyp 1
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("io"), FSxSTR(""), 2, 9, FSxSTR("raadio"),  FSxSTR("S")}, // VVS tyyp 1
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("io"), FSxSTR(""), 2, 9, FSxSTR("raadio"),  FSxSTR("S")}, // VVS tyyp 1
{0, FSxSTR(""), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("io"), FSxSTR(""), 2, 9, FSxSTR("raadio"),  FSxSTR("S")}, // VVS tyyp 1

{0, FSxSTR(""), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("elu"), FSxSTR("C"), 4, 9, FSxSTR("arutelu"),  FSxSTR("S")}, // VVS tyyp 17
{0, FSxSTR(""), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("elu"), FSxSTR("C"), 4, 9, FSxSTR("arutelu"),  FSxSTR("S")}, // VVS tyyp 17
{1, FSxSTR("lu"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("elu"), FSxSTR("C"), 4, 9, FSxSTR("arutelu"),  FSxSTR("S")}, // VVS tyyp 17
{0, FSxSTR(""), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("elu"), FSxSTR("C"), 4, 9, FSxSTR("arutelu"),  FSxSTR("S")}, // VVS tyyp 17
{0, FSxSTR(""), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("elu"), FSxSTR("C"), 4, 9, FSxSTR("arutelu"),  FSxSTR("S")}, // VVS tyyp 17

{0, FSxSTR(""), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("aa"), FSxSTR(""), 2, 9, FSxSTR("maa"),  FSxSTR("S")}, // VVS tyyp 26
{0, FSxSTR(""), FSxSTR("d"), FSxSTR("sg p, "), FSxSTR("aa"), FSxSTR(""), 2, 9, FSxSTR("maa"),  FSxSTR("S")}, // VVS tyyp 26
{0, FSxSTR(""), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("aa"), FSxSTR(""), 2, 9, FSxSTR("maa"),  FSxSTR("S")}, // VVS tyyp 26
{0, FSxSTR(""), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("aa"), FSxSTR(""), 2, 9, FSxSTR("maa"),  FSxSTR("S")}, // VVS tyyp 26
{1, FSxSTR(""), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("aa"), FSxSTR(""), 2, 9, FSxSTR("maa"),  FSxSTR("S")}, // VVS tyyp 26

{0, FSxSTR(""), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ee"), FSxSTR(""), 2, 9, FSxSTR("armee"),  FSxSTR("S")}, // VVS tyyp 26
{0, FSxSTR(""), FSxSTR("d"), FSxSTR("sg p, "), FSxSTR("ee"), FSxSTR(""), 2, 9, FSxSTR("armee"),  FSxSTR("S")}, // VVS tyyp 26
{0, FSxSTR(""), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("ee"), FSxSTR(""), 2, 9, FSxSTR("armee"),  FSxSTR("S")}, // VVS tyyp 26
{0, FSxSTR(""), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("ee"), FSxSTR(""), 2, 9, FSxSTR("armee"),  FSxSTR("S")}, // VVS tyyp 26
{1, FSxSTR(""), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("ee"), FSxSTR(""), 2, 9, FSxSTR("armee"),  FSxSTR("S")}, // VVS tyyp 26

{0, FSxSTR(""), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("uu"), FSxSTR(""), 2, 9, FSxSTR("puu"),  FSxSTR("S")}, // VVS tyyp 26
{0, FSxSTR(""), FSxSTR("d"), FSxSTR("sg p, "), FSxSTR("uu"), FSxSTR(""), 2, 9, FSxSTR("puu"),  FSxSTR("S")}, // VVS tyyp 26
{0, FSxSTR(""), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("uu"), FSxSTR(""), 2, 9, FSxSTR("puu"),  FSxSTR("S")}, // VVS tyyp 26
{1, FSxSTR(""), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("uu"), FSxSTR(""), 2, 9, FSxSTR("puu"),  FSxSTR("S")}, // VVS tyyp 26
{0, FSxSTR(""), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("uu"), FSxSTR(""), 2, 9, FSxSTR("puu"),  FSxSTR("S")}, // VVS tyyp 26

{0, FSxSTR(""), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("\366\366"), FSxSTR("C"), 2, 9, FSxSTR("t\366\366"),  FSxSTR("S")}, // VVS tyyp 26 to'o'
{0, FSxSTR(""), FSxSTR("d"), FSxSTR("sg p, "), FSxSTR("\366\366"), FSxSTR("C"), 2, 9, FSxSTR("t\366\366"),  FSxSTR("S")}, // VVS tyyp 26 to'o'
{0, FSxSTR(""), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("\366\366"), FSxSTR("C"), 2, 9, FSxSTR("t\366\366"),  FSxSTR("S")}, // VVS tyyp 26 to'o'
{1, FSxSTR(""), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("\366\366"), FSxSTR("C"), 2, 9, FSxSTR("t\366\366"),  FSxSTR("S")}, // VVS tyyp 26 to'o'
{0, FSxSTR(""), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("\366\366"), FSxSTR("C"), 2, 9, FSxSTR("t\366\366"),  FSxSTR("S")}, // VVS tyyp 26 to'o'

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("v"), FSxSTR("VV"), 1, 9, FSxSTR("alkoov"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("v"), FSxSTR("VV"), 1, 9, FSxSTR("alkoov"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("v"), FSxSTR("VV"), 1, 9, FSxSTR("alkoov"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("v"), FSxSTR("VV"), 1, 9, FSxSTR("alkoov"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("v"), FSxSTR("VV"), 1, 9, FSxSTR("alkoov"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("v"), FSxSTR("VV"), 1, 9, FSxSTR("alkoov"),  FSxSTR("S")}, // VVS tyyp 22

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ov"), FSxSTR(""), 2, 9, FSxSTR("b\366fstrooganov"),  FSxSTR("S")}, // VVS tyyp 19
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR("ov"), FSxSTR(""), 2, 9, FSxSTR("b\366fstrooganov"),  FSxSTR("S")}, // VVS tyyp 19
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR("ov"), FSxSTR(""), 2, 9, FSxSTR("b\366fstrooganov"),  FSxSTR("S")}, // VVS tyyp 19
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("ov"), FSxSTR(""), 2, 9, FSxSTR("b\366fstrooganov"),  FSxSTR("S")}, // VVS tyyp 19
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR("ov"), FSxSTR(""), 2, 9, FSxSTR("b\366fstrooganov"),  FSxSTR("S")}, // VVS tyyp 19
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("ov"), FSxSTR(""), 2, 9, FSxSTR("b\366fstrooganov"),  FSxSTR("S")}, // VVS tyyp 19

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("ov"), FSxSTR(""), 2, 9, FSxSTR("Kirov"),  FSxSTR("H")}, // VVS tyyp 2
{0, FSxSTR("i"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("ov"), FSxSTR(""), 2, 9, FSxSTR("Kirov"),  FSxSTR("H")}, // VVS tyyp 2
{0, FSxSTR("i"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("ov"), FSxSTR(""), 2, 9, FSxSTR("Kirov"),  FSxSTR("H")}, // VVS tyyp 2
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR("ov"), FSxSTR(""), 2, 9, FSxSTR("Kirov"),  FSxSTR("H")}, // VVS tyyp 2

{0, FSxSTR(""), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("y"), FSxSTR(""), 2, 2, FSxSTR("lobby"),  FSxSTR("S")}, // VVS tyyp 16
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("y"), FSxSTR(""), 2, 2, FSxSTR("lobby"),  FSxSTR("S")}, // VVS tyyp 16
{0, FSxSTR(""), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("y"), FSxSTR(""), 2, 2, FSxSTR("lobby"),  FSxSTR("S")}, // VVS tyyp 16
{0, FSxSTR(""), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("y"), FSxSTR(""), 2, 2, FSxSTR("lobby"),  FSxSTR("S")}, // VVS tyyp 16

{0, FSxSTR(""), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("y"), FSxSTR("C"), 3, 3, FSxSTR("Kennedy"),  FSxSTR("H")}, // VVS tyyp 1
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("y"), FSxSTR("C"), 3, 3, FSxSTR("Kennedy"),  FSxSTR("H")}, // VVS tyyp 1
{0, FSxSTR(""), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR("y"), FSxSTR("C"), 3, 3, FSxSTR("Kennedy"),  FSxSTR("H")}, // VVS tyyp 1
{0, FSxSTR(""), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("y"), FSxSTR("C"), 3, 3, FSxSTR("Kennedy"),  FSxSTR("H")}, // VVS tyyp 1

{0, FSxSTR(""), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("y"), FSxSTR(""), 2, 9, FSxSTR("Henry"),  FSxSTR("H")}, // VVS tyyp 16
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR("y"), FSxSTR(""), 2, 9, FSxSTR("Henry"),  FSxSTR("H")}, // VVS tyyp 16
{0, FSxSTR(""), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("y"), FSxSTR(""), 2, 9, FSxSTR("Henry"),  FSxSTR("H")}, // VVS tyyp 16
{0, FSxSTR(""), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("y"), FSxSTR(""), 2, 9, FSxSTR("Henry"),  FSxSTR("H")}, // VVS tyyp 16

{0, FSxSTR(""), FSxSTR(""), FSxSTR("sg g, "), FSxSTR("y"), FSxSTR(""), 1, 1, FSxSTR("Roy"),  FSxSTR("H")}, // VVS tyyp 26 
{0, FSxSTR(""), FSxSTR("d"), FSxSTR("sg p, "), FSxSTR("y"), FSxSTR(""), 1, 1, FSxSTR("Roy"),  FSxSTR("H")}, // VVS tyyp 26 
{0, FSxSTR(""), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR("y"), FSxSTR(""), 1, 1, FSxSTR("Roy"),  FSxSTR("H")}, // VVS tyyp 26 
{0, FSxSTR(""), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR("y"), FSxSTR(""), 1, 1, FSxSTR("Roy"),  FSxSTR("H")}, // VVS tyyp 26 

{0, FSxSTR(""), FSxSTR(""), FSxSTR("sg g, "), FSxSTR(""), FSxSTR("V"), 1, 1, FSxSTR("koi"),  FSxSTR("S")}, // VVS tyyp 26 
{0, FSxSTR(""), FSxSTR("d"), FSxSTR("sg p, "), FSxSTR(""), FSxSTR("V"), 1, 1, FSxSTR("koi"),  FSxSTR("S")}, // VVS tyyp 26 
{0, FSxSTR(""), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR(""), FSxSTR("V"), 1, 1, FSxSTR("koi"),  FSxSTR("S")}, // VVS tyyp 26 
{0, FSxSTR(""), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR(""), FSxSTR("V"), 1, 1, FSxSTR("koi"),  FSxSTR("S")}, // VVS tyyp 26 

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR(""), FSxSTR("C"), 1, 1, FSxSTR("faks"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR(""), FSxSTR("C"), 1, 1, FSxSTR("faks"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR(""), FSxSTR("C"), 1, 1, FSxSTR("faks"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR(""), FSxSTR("C"), 1, 1, FSxSTR("faks"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR(""), FSxSTR("C"), 1, 1, FSxSTR("faks"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR(""), FSxSTR("C"), 1, 1, FSxSTR("faks"),  FSxSTR("S")}, // VVS tyyp 22

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR(""), FSxSTR("VVB"), 1, 9, FSxSTR("satiin"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR(""), FSxSTR("VVB"), 1, 9, FSxSTR("satiin"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR(""), FSxSTR("VVB"), 1, 9, FSxSTR("satiin"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR(""), FSxSTR("VVB"), 1, 9, FSxSTR("satiin"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR(""), FSxSTR("VVB"), 1, 9, FSxSTR("satiin"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR(""), FSxSTR("VVB"), 1, 9, FSxSTR("satiin"),  FSxSTR("S")}, // VVS tyyp 22

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR(""), FSxSTR("VCB"), 1, 9, FSxSTR("marketing"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR(""), FSxSTR("VCB"), 1, 9, FSxSTR("marketing"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR(""), FSxSTR("VCB"), 1, 9, FSxSTR("marketing"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR(""), FSxSTR("VCB"), 1, 9, FSxSTR("marketing"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR(""), FSxSTR("VCB"), 1, 9, FSxSTR("marketing"),  FSxSTR("S")}, // VVS tyyp 22
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR(""), FSxSTR("VCB"), 1, 9, FSxSTR("marketing"),  FSxSTR("S")}, // VVS tyyp 22

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR(""), FSxSTR("D"), 2, 9, FSxSTR("pilet"),  FSxSTR("S")}, // VVS tyyp 2 parisnimi
{0, FSxSTR("i"), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR(""), FSxSTR("D"), 2, 9, FSxSTR("pilet"),  FSxSTR("S")}, // VVS tyyp 2 parisnimi
{0, FSxSTR("i"), FSxSTR("te"), FSxSTR("pl g, "), FSxSTR(""), FSxSTR("D"), 2, 9, FSxSTR("pilet"),  FSxSTR("S")}, // VVS tyyp 2 parisnimi
{0, FSxSTR("e"), FSxSTR("id"), FSxSTR("pl p, "), FSxSTR(""), FSxSTR("D"), 2, 9, FSxSTR("pilet"),  FSxSTR("S")}, // VVS tyyp 2 parisnimi

{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg g, "), FSxSTR(""), FSxSTR("L"), 3, 9, FSxSTR("talisman"),  FSxSTR("S")}, // VVS tyyp 19
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("sg p, "), FSxSTR(""), FSxSTR("L"), 3, 9, FSxSTR("talisman"),  FSxSTR("S")}, // VVS tyyp 19
{0, FSxSTR("i"), FSxSTR(""), FSxSTR("adt, "), FSxSTR(""), FSxSTR("L"), 3, 9, FSxSTR("talisman"),  FSxSTR("S")}, // VVS tyyp 19
{0, FSxSTR("i"), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR(""), FSxSTR("L"), 3, 9, FSxSTR("talisman"),  FSxSTR("S")}, // VVS tyyp 19
{0, FSxSTR(""), FSxSTR("e"), FSxSTR("pl p, "), FSxSTR(""), FSxSTR("L"), 3, 9, FSxSTR("talisman"),  FSxSTR("S")}, // VVS tyyp 19
{0, FSxSTR("i"), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR(""), FSxSTR("L"), 3, 9, FSxSTR("talisman"),  FSxSTR("S")}, // VVS tyyp 19

{0, FSxSTR(""), FSxSTR(""), FSxSTR("sg g, "), FSxSTR(""), FSxSTR("CV"), 2, 9, FSxSTR("veto"),  FSxSTR("S")}, // VVS tyyp 16
{0, FSxSTR(""), FSxSTR("t"), FSxSTR("sg p, "), FSxSTR(""), FSxSTR("CV"), 2, 9, FSxSTR("veto"),  FSxSTR("S")}, // VVS tyyp 16
{0, FSxSTR(""), FSxSTR("de"), FSxSTR("pl g, "), FSxSTR(""), FSxSTR("CV"), 2, 9, FSxSTR("veto"),  FSxSTR("S")}, // VVS tyyp 16
{0, FSxSTR(""), FSxSTR("sid"), FSxSTR("pl p, "), FSxSTR(""), FSxSTR("CV"), 2, 9, FSxSTR("veto"),  FSxSTR("S")}, // VVS tyyp 16

// **********************************************************
// verbid
// **********************************************************
{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("eeri"), FSxSTR(""), 3, 9, FSxSTR("seeri"), FSxSTR("V")}, // VVS tyyp 28
{0, FSxSTR(""), FSxSTR("da"), FSxSTR("da, "), FSxSTR("eeri"), FSxSTR(""), 3, 9, FSxSTR("seeri"), FSxSTR("V")}, // VVS tyyp 28
{0, FSxSTR(""), FSxSTR("b"), FSxSTR("b, "), FSxSTR("eeri"), FSxSTR(""), 3, 9, FSxSTR("seeri"), FSxSTR("V")}, // VVS tyyp 28
{0, FSxSTR(""), FSxSTR("tud"), FSxSTR("tud, "), FSxSTR("eeri"), FSxSTR(""), 3, 9, FSxSTR("seeri"), FSxSTR("V")}, // VVS tyyp 28

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("eeru"), FSxSTR(""), 3, 9, FSxSTR("muteeru"), FSxSTR("V")}, // VVS tyyp 27
{0, FSxSTR(""), FSxSTR("da"), FSxSTR("da, "), FSxSTR("eeru"), FSxSTR(""), 3, 9, FSxSTR("muteeru"), FSxSTR("V")}, // VVS tyyp 27
{0, FSxSTR(""), FSxSTR("b"), FSxSTR("b, "), FSxSTR("eeru"), FSxSTR(""), 3, 9, FSxSTR("muteeru"), FSxSTR("V")}, // VVS tyyp 27
{0, FSxSTR(""), FSxSTR("tud"), FSxSTR("tud, "), FSxSTR("eeru"), FSxSTR(""), 3, 9, FSxSTR("muteeru"), FSxSTR("V")}, // VVS tyyp 27

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("skle"), FSxSTR(""), 2, 2, FSxSTR("viskle"), FSxSTR("V")}, // VVS tyyp 30
{3, FSxSTR("el"), FSxSTR("da"), FSxSTR("da, "), FSxSTR("skle"), FSxSTR(""), 2, 2, FSxSTR("viskle"), FSxSTR("V")}, // VVS tyyp 30
{0, FSxSTR(""), FSxSTR("b"), FSxSTR("b, "), FSxSTR("skle"), FSxSTR(""), 2, 2, FSxSTR("viskle"), FSxSTR("V")}, // VVS tyyp 30
{3, FSxSTR("el"), FSxSTR("dud"), FSxSTR("tud, "), FSxSTR("skle"), FSxSTR(""), 2, 2, FSxSTR("viskle"), FSxSTR("V")}, // VVS tyyp 30

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("kle"), FSxSTR("L"), 2, 2, FSxSTR("vonkle"), FSxSTR("V")}, // VVS tyyp 30
{3, FSxSTR("gel"), FSxSTR("da"), FSxSTR("da, "), FSxSTR("kle"), FSxSTR("L"), 2, 2, FSxSTR("vonkle"), FSxSTR("V")}, // VVS tyyp 30
{0, FSxSTR(""), FSxSTR("b"), FSxSTR("b, "), FSxSTR("kle"), FSxSTR("L"), 2, 2, FSxSTR("vonkle"), FSxSTR("V")}, // VVS tyyp 30
{3, FSxSTR("gel"), FSxSTR("dud"), FSxSTR("tud, "), FSxSTR("kle"), FSxSTR("L"), 2, 2, FSxSTR("vonkle"), FSxSTR("V")}, // VVS tyyp 30

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("kle"), FSxSTR("VV"), 2, 2, FSxSTR("lookle"), FSxSTR("V")}, // VVS tyyp 30
{3, FSxSTR("gel"), FSxSTR("da"), FSxSTR("da, "), FSxSTR("kle"), FSxSTR("VV"), 2, 2, FSxSTR("lookle"), FSxSTR("V")}, // VVS tyyp 30
{0, FSxSTR(""), FSxSTR("b"), FSxSTR("b, "), FSxSTR("kle"), FSxSTR("VV"), 2, 2, FSxSTR("lookle"), FSxSTR("V")}, // VVS tyyp 30
{3, FSxSTR("gel"), FSxSTR("dud"), FSxSTR("tud, "), FSxSTR("kle"), FSxSTR("VV"), 2, 2, FSxSTR("lookle"), FSxSTR("V")}, // VVS tyyp 30

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("hkle"), FSxSTR("V"), 2, 2, FSxSTR("vehkle"), FSxSTR("V")}, // VVS tyyp 30
{3, FSxSTR("el"), FSxSTR("da"), FSxSTR("da, "), FSxSTR("hkle"), FSxSTR("V"), 2, 2, FSxSTR("vehkle"), FSxSTR("V")}, // VVS tyyp 30
{0, FSxSTR(""), FSxSTR("b"), FSxSTR("b, "), FSxSTR("hkle"), FSxSTR("V"), 2, 2, FSxSTR("vehkle"), FSxSTR("V")}, // VVS tyyp 30
{3, FSxSTR("el"), FSxSTR("dud"), FSxSTR("tud, "), FSxSTR("hkle"), FSxSTR("V"), 2, 2, FSxSTR("vehkle"), FSxSTR("V")}, // VVS tyyp 30

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("ple"), FSxSTR("L"), 2, 2, FSxSTR("krample"), FSxSTR("V")}, // VVS tyyp 30
{3, FSxSTR("bel"), FSxSTR("da"), FSxSTR("da, "), FSxSTR("ple"), FSxSTR("L"), 2, 2, FSxSTR("krample"), FSxSTR("V")}, // VVS tyyp 30
{0, FSxSTR(""), FSxSTR("b"), FSxSTR("b, "), FSxSTR("ple"), FSxSTR("L"), 2, 2, FSxSTR("krample"), FSxSTR("V")}, // VVS tyyp 30
{3, FSxSTR("bel"), FSxSTR("dud"), FSxSTR("tud, "), FSxSTR("ple"), FSxSTR("L"), 2, 2, FSxSTR("krample"), FSxSTR("V")}, // VVS tyyp 30

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("ple"), FSxSTR("VV"), 2, 2, FSxSTR("kauple"), FSxSTR("V")}, // VVS tyyp 30
{3, FSxSTR("bel"), FSxSTR("da"), FSxSTR("da, "), FSxSTR("ple"), FSxSTR("VV"), 2, 2, FSxSTR("kauple"), FSxSTR("V")}, // VVS tyyp 30
{0, FSxSTR(""), FSxSTR("b"), FSxSTR("b, "), FSxSTR("ple"), FSxSTR("VV"), 2, 2, FSxSTR("kauple"), FSxSTR("V")}, // VVS tyyp 30
{3, FSxSTR("bel"), FSxSTR("dud"), FSxSTR("tud, "), FSxSTR("ple"), FSxSTR("VV"), 2, 2, FSxSTR("kauple"), FSxSTR("V")}, // VVS tyyp 30

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("stle"), FSxSTR(""), 2, 2, FSxSTR("vestle"), FSxSTR("V")}, // VVS tyyp 30
{2, FSxSTR("el"), FSxSTR("da"), FSxSTR("da, "), FSxSTR("stle"), FSxSTR(""), 2, 2, FSxSTR("vestle"), FSxSTR("V")}, // VVS tyyp 30
{0, FSxSTR(""), FSxSTR("b"), FSxSTR("b, "), FSxSTR("stle"), FSxSTR(""), 2, 2, FSxSTR("vestle"), FSxSTR("V")}, // VVS tyyp 30
{2, FSxSTR("el"), FSxSTR("dud"), FSxSTR("tud, "), FSxSTR("stle"), FSxSTR(""), 2, 2, FSxSTR("vestle"), FSxSTR("V")}, // VVS tyyp 30

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("tle"), FSxSTR("VV"), 2, 2, FSxSTR("heitle"), FSxSTR("V")}, // VVS tyyp 30
{3, FSxSTR("del"), FSxSTR("da"), FSxSTR("da, "), FSxSTR("tle"), FSxSTR("VV"), 2, 2, FSxSTR("heitle"), FSxSTR("V")}, // VVS tyyp 30
{0, FSxSTR(""), FSxSTR("b"), FSxSTR("b, "), FSxSTR("tle"), FSxSTR("VV"), 2, 2, FSxSTR("heitle"), FSxSTR("V")}, // VVS tyyp 30
{3, FSxSTR("del"), FSxSTR("dud"), FSxSTR("tud, "), FSxSTR("tle"), FSxSTR("VV"), 2, 2, FSxSTR("heitle"), FSxSTR("V")}, // VVS tyyp 30

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("htle"), FSxSTR("V"), 2, 2, FSxSTR("kahtle"), FSxSTR("V")}, // VVS tyyp 30
{3, FSxSTR("el"), FSxSTR("da"), FSxSTR("da, "), FSxSTR("htle"), FSxSTR("V"), 2, 2, FSxSTR("kahtle"), FSxSTR("V")}, // VVS tyyp 30
{0, FSxSTR(""), FSxSTR("b"), FSxSTR("b, "), FSxSTR("htle"), FSxSTR("V"), 2, 2, FSxSTR("kahtle"), FSxSTR("V")}, // VVS tyyp 30
{3, FSxSTR("el"), FSxSTR("dud"), FSxSTR("tud, "), FSxSTR("htle"), FSxSTR("V"), 2, 2, FSxSTR("kahtle"), FSxSTR("V")}, // VVS tyyp 30

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("le"), FSxSTR("C"), 2, 2, FSxSTR("aimle"), FSxSTR("V")}, // VVS tyyp 30
{2, FSxSTR("el"), FSxSTR("da"), FSxSTR("da, "), FSxSTR("le"), FSxSTR("C"), 2, 2, FSxSTR("aimle"), FSxSTR("V")}, // VVS tyyp 30
{0, FSxSTR(""), FSxSTR("b"), FSxSTR("b, "), FSxSTR("le"), FSxSTR("C"), 2, 2, FSxSTR("aimle"), FSxSTR("V")}, // VVS tyyp 30
{2, FSxSTR("el"), FSxSTR("dud"), FSxSTR("tud, "), FSxSTR("le"), FSxSTR("C"), 2, 2, FSxSTR("aimle"), FSxSTR("V")}, // VVS tyyp 30

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("ksu"), FSxSTR(""), 2, 2, FSxSTR("raksu"), FSxSTR("V")}, // VVS tyyp 28
{0, FSxSTR(""), FSxSTR("da"), FSxSTR("da, "), FSxSTR("ksu"), FSxSTR(""), 2, 2, FSxSTR("raksu"), FSxSTR("V")}, // VVS tyyp 28
{0, FSxSTR(""), FSxSTR("b"), FSxSTR("b, "), FSxSTR("ksu"), FSxSTR(""), 2, 2, FSxSTR("raksu"), FSxSTR("V")}, // VVS tyyp 28
{0, FSxSTR(""), FSxSTR("tud"), FSxSTR("tud, "), FSxSTR("ksu"), FSxSTR(""), 2, 2, FSxSTR("raksu"), FSxSTR("V")}, // VVS tyyp 28

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("psu"), FSxSTR(""), 2, 2, FSxSTR("popsu"), FSxSTR("V")}, // VVS tyyp 28
{0, FSxSTR(""), FSxSTR("da"), FSxSTR("da, "), FSxSTR("psu"), FSxSTR(""), 2, 2, FSxSTR("popsu"), FSxSTR("V")}, // VVS tyyp 28
{0, FSxSTR(""), FSxSTR("b"), FSxSTR("b, "), FSxSTR("psu"), FSxSTR(""), 2, 2, FSxSTR("popsu"), FSxSTR("V")}, // VVS tyyp 28
{0, FSxSTR(""), FSxSTR("tud"), FSxSTR("tud, "), FSxSTR("psu"), FSxSTR(""), 2, 2, FSxSTR("popsu"), FSxSTR("V")}, // VVS tyyp 28

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("tsu"), FSxSTR(""), 2, 2, FSxSTR("patsu"), FSxSTR("V")}, // VVS tyyp 28
{0, FSxSTR(""), FSxSTR("da"), FSxSTR("da, "), FSxSTR("tsu"), FSxSTR(""), 2, 2, FSxSTR("patsu"), FSxSTR("V")}, // VVS tyyp 28
{0, FSxSTR(""), FSxSTR("b"), FSxSTR("b, "), FSxSTR("tsu"), FSxSTR(""), 2, 2, FSxSTR("patsu"), FSxSTR("V")}, // VVS tyyp 28
{0, FSxSTR(""), FSxSTR("tud"), FSxSTR("tud, "), FSxSTR("tsu"), FSxSTR(""), 2, 2, FSxSTR("patsu"), FSxSTR("V")}, // VVS tyyp 28

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("ki"), FSxSTR("VV"), 2, 9, FSxSTR("rooki"), FSxSTR("V")}, // VVS tyyp 28
{0, FSxSTR(""), FSxSTR("da"), FSxSTR("da, "), FSxSTR("ki"), FSxSTR("VV"), 2, 9, FSxSTR("rooki"), FSxSTR("V")}, // VVS tyyp 28
{2, FSxSTR("gi"), FSxSTR("b"), FSxSTR("b, "), FSxSTR("ki"), FSxSTR("VV"), 2, 9, FSxSTR("rooki"), FSxSTR("V")}, // VVS tyyp 28
{2, FSxSTR("gi"), FSxSTR("tud"), FSxSTR("tud, "), FSxSTR("ki"), FSxSTR("VV"), 2, 9, FSxSTR("rooki"), FSxSTR("V")}, // VVS tyyp 28

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("pi"), FSxSTR("VV"), 2, 9, FSxSTR("kleepi"), FSxSTR("V")}, // VVS tyyp 28
{0, FSxSTR(""), FSxSTR("da"), FSxSTR("da, "), FSxSTR("pi"), FSxSTR("VV"), 2, 9, FSxSTR("kleepi"), FSxSTR("V")}, // VVS tyyp 28
{2, FSxSTR("bi"), FSxSTR("b"), FSxSTR("b, "), FSxSTR("pi"), FSxSTR("VV"), 2, 9, FSxSTR("kleepi"), FSxSTR("V")}, // VVS tyyp 28
{2, FSxSTR("bi"), FSxSTR("tud"), FSxSTR("tud, "), FSxSTR("pi"), FSxSTR("VV"), 2, 9, FSxSTR("kleepi"), FSxSTR("V")}, // VVS tyyp 28

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("ti"), FSxSTR("VV"), 2, 9, FSxSTR("nuuti"), FSxSTR("V")}, // VVS tyyp 28
{0, FSxSTR(""), FSxSTR("da"), FSxSTR("da, "), FSxSTR("ti"), FSxSTR("VV"), 2, 9, FSxSTR("nuuti"), FSxSTR("V")}, // VVS tyyp 28
{2, FSxSTR("di"), FSxSTR("b"), FSxSTR("b, "), FSxSTR("ti"), FSxSTR("VV"), 2, 9, FSxSTR("nuuti"), FSxSTR("V")}, // VVS tyyp 28
{2, FSxSTR("di"), FSxSTR("tud"), FSxSTR("tud, "), FSxSTR("ti"), FSxSTR("VV"), 2, 9, FSxSTR("nuuti"), FSxSTR("V")}, // VVS tyyp 28

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("ki"), FSxSTR("L"), 2, 2, FSxSTR("torki"), FSxSTR("V")}, // VVS tyyp 28
{0, FSxSTR(""), FSxSTR("da"), FSxSTR("da, "), FSxSTR("ki"), FSxSTR("L"), 2, 2, FSxSTR("torki"), FSxSTR("V")}, // VVS tyyp 28
{2, FSxSTR("gi"), FSxSTR("b"), FSxSTR("b, "), FSxSTR("ki"), FSxSTR("L"), 2, 2, FSxSTR("torki"), FSxSTR("V")}, // VVS tyyp 28
{2, FSxSTR("gi"), FSxSTR("tud"), FSxSTR("tud, "), FSxSTR("ki"), FSxSTR("L"), 2, 2, FSxSTR("torki"), FSxSTR("V")}, // VVS tyyp 28

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("pi"), FSxSTR("L"), 2, 2, FSxSTR("kompi"), FSxSTR("V")}, // VVS tyyp 28
{0, FSxSTR(""), FSxSTR("da"), FSxSTR("da, "), FSxSTR("pi"), FSxSTR("L"), 2, 2, FSxSTR("kompi"), FSxSTR("V")}, // VVS tyyp 28
{2, FSxSTR("bi"), FSxSTR("b"), FSxSTR("b, "), FSxSTR("pi"), FSxSTR("L"), 2, 2, FSxSTR("kompi"), FSxSTR("V")}, // VVS tyyp 28
{2, FSxSTR("bi"), FSxSTR("tud"), FSxSTR("tud, "), FSxSTR("pi"), FSxSTR("L"), 2, 2, FSxSTR("kompi"), FSxSTR("V")}, // VVS tyyp 28

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("ti"), FSxSTR("L"), 2, 2, FSxSTR("sporti"), FSxSTR("V")}, // VVS tyyp 28
{0, FSxSTR(""), FSxSTR("da"), FSxSTR("da, "), FSxSTR("ti"), FSxSTR("L"), 2, 2, FSxSTR("sporti"), FSxSTR("V")}, // VVS tyyp 28
{2, FSxSTR("di"), FSxSTR("b"), FSxSTR("b, "), FSxSTR("ti"), FSxSTR("L"), 2, 2, FSxSTR("sporti"), FSxSTR("V")}, // VVS tyyp 28
{2, FSxSTR("di"), FSxSTR("tud"), FSxSTR("tud, "), FSxSTR("ti"), FSxSTR("L"), 2, 2, FSxSTR("sporti"), FSxSTR("V")}, // VVS tyyp 28

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("ssi"), FSxSTR("L"), 2, 2, FSxSTR("purssi"), FSxSTR("V")}, // VVS tyyp 28
{0, FSxSTR(""), FSxSTR("da"), FSxSTR("da, "), FSxSTR("ssi"), FSxSTR("L"), 2, 2, FSxSTR("purssi"), FSxSTR("V")}, // VVS tyyp 28
{2, FSxSTR("i"), FSxSTR("b"), FSxSTR("b, "), FSxSTR("ssi"), FSxSTR("L"), 2, 2, FSxSTR("purssi"), FSxSTR("V")}, // VVS tyyp 28
{2, FSxSTR("i"), FSxSTR("tud"), FSxSTR("tud, "), FSxSTR("ssi"), FSxSTR("L"), 2, 2, FSxSTR("purssi"), FSxSTR("V")}, // VVS tyyp 28

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("hki"), FSxSTR("V"), 2, 2, FSxSTR("puhki"), FSxSTR("V")}, // VVS tyyp 28
{0, FSxSTR(""), FSxSTR("da"), FSxSTR("da, "), FSxSTR("hki"), FSxSTR("V"), 2, 2, FSxSTR("puhki"), FSxSTR("V")}, // VVS tyyp 28
{2, FSxSTR("i"), FSxSTR("b"), FSxSTR("b, "), FSxSTR("hki"), FSxSTR("V"), 2, 2, FSxSTR("puhki"), FSxSTR("V")}, // VVS tyyp 28
{2, FSxSTR("i"), FSxSTR("tud"), FSxSTR("tud, "), FSxSTR("hki"), FSxSTR("V"), 2, 2, FSxSTR("puhki"), FSxSTR("V")}, // VVS tyyp 28

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("hti"), FSxSTR("V"), 2, 2, FSxSTR("tohti"), FSxSTR("V")}, // VVS tyyp 28
{0, FSxSTR(""), FSxSTR("da"), FSxSTR("da, "), FSxSTR("hti"), FSxSTR("V"), 2, 2, FSxSTR("tohti"), FSxSTR("V")}, // VVS tyyp 28
{2, FSxSTR("i"), FSxSTR("b"), FSxSTR("b, "), FSxSTR("hti"), FSxSTR("V"), 2, 2, FSxSTR("tohti"), FSxSTR("V")}, // VVS tyyp 28
{2, FSxSTR("i"), FSxSTR("tud"), FSxSTR("tud, "), FSxSTR("hti"), FSxSTR("V"), 2, 2, FSxSTR("tohti"), FSxSTR("V")}, // VVS tyyp 28

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("kki"), FSxSTR("V"), 2, 2, FSxSTR("nokki"), FSxSTR("V")}, // VVS tyyp 28
{0, FSxSTR(""), FSxSTR("da"), FSxSTR("da, "), FSxSTR("kki"), FSxSTR("V"), 2, 2, FSxSTR("nokki"), FSxSTR("V")}, // VVS tyyp 28
{2, FSxSTR("i"), FSxSTR("b"), FSxSTR("b, "), FSxSTR("kki"), FSxSTR("V"), 2, 2, FSxSTR("nokki"), FSxSTR("V")}, // VVS tyyp 28
{2, FSxSTR("i"), FSxSTR("tud"), FSxSTR("tud, "), FSxSTR("kki"), FSxSTR("V"), 2, 2, FSxSTR("nokki"), FSxSTR("V")}, // VVS tyyp 28

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("ppi"), FSxSTR("V"), 2, 2, FSxSTR("noppi"), FSxSTR("V")}, // VVS tyyp 28
{0, FSxSTR(""), FSxSTR("da"), FSxSTR("da, "), FSxSTR("ppi"), FSxSTR("V"), 2, 2, FSxSTR("noppi"), FSxSTR("V")}, // VVS tyyp 28
{2, FSxSTR("i"), FSxSTR("b"), FSxSTR("b, "), FSxSTR("ppi"), FSxSTR("V"), 2, 2, FSxSTR("noppi"), FSxSTR("V")}, // VVS tyyp 28
{2, FSxSTR("i"), FSxSTR("tud"), FSxSTR("tud, "), FSxSTR("ppi"), FSxSTR("V"), 2, 2, FSxSTR("noppi"), FSxSTR("V")}, // VVS tyyp 28

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("tti"), FSxSTR("V"), 2, 2, FSxSTR("kratti"), FSxSTR("V")}, // VVS tyyp 28
{0, FSxSTR(""), FSxSTR("da"), FSxSTR("da, "), FSxSTR("tti"), FSxSTR("V"), 2, 2, FSxSTR("kratti"), FSxSTR("V")}, // VVS tyyp 28
{2, FSxSTR("i"), FSxSTR("b"), FSxSTR("b, "), FSxSTR("tti"), FSxSTR("V"), 2, 2, FSxSTR("kratti"), FSxSTR("V")}, // VVS tyyp 28
{2, FSxSTR("i"), FSxSTR("tud"), FSxSTR("tud, "), FSxSTR("tti"), FSxSTR("V"), 2, 2, FSxSTR("kratti"), FSxSTR("V")}, // VVS tyyp 28

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("kka"), FSxSTR("V"), 2, 9, FSxSTR("hakka"), FSxSTR("V")}, // VVS tyyp 29
{2, FSxSTR("a"), FSxSTR("ta"), FSxSTR("da, "), FSxSTR("kka"), FSxSTR("V"), 2, 9, FSxSTR("hakka"), FSxSTR("V")}, // VVS tyyp 29
{0, FSxSTR(""), FSxSTR("b"), FSxSTR("b, "), FSxSTR("kka"), FSxSTR("V"), 2, 9, FSxSTR("hakka"), FSxSTR("V")}, // VVS tyyp 29
{2, FSxSTR("a"), FSxSTR("tud"), FSxSTR("tud, "), FSxSTR("kka"), FSxSTR("V"), 2, 9, FSxSTR("hakka"), FSxSTR("V")}, // VVS tyyp 29

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("ppa"), FSxSTR("V"), 2, 9, FSxSTR("toppa"), FSxSTR("V")}, // VVS tyyp 29
{2, FSxSTR("a"), FSxSTR("ta"), FSxSTR("da, "), FSxSTR("ppa"), FSxSTR("V"), 2, 9, FSxSTR("toppa"), FSxSTR("V")}, // VVS tyyp 29
{0, FSxSTR(""), FSxSTR("b"), FSxSTR("b, "), FSxSTR("ppa"), FSxSTR("V"), 2, 9, FSxSTR("toppa"), FSxSTR("V")}, // VVS tyyp 29
{2, FSxSTR("a"), FSxSTR("tud"), FSxSTR("tud, "), FSxSTR("ppa"), FSxSTR("V"), 2, 9, FSxSTR("toppa"), FSxSTR("V")}, // VVS tyyp 29

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("tta"), FSxSTR("V"), 2, 9, FSxSTR("rutta"), FSxSTR("V")}, // VVS tyyp 29
{2, FSxSTR("a"), FSxSTR("ta"), FSxSTR("da, "), FSxSTR("tta"), FSxSTR("V"), 2, 9, FSxSTR("rutta"), FSxSTR("V")}, // VVS tyyp 29
{0, FSxSTR(""), FSxSTR("b"), FSxSTR("b, "), FSxSTR("tta"), FSxSTR("V"), 2, 9, FSxSTR("rutta"), FSxSTR("V")}, // VVS tyyp 29
{2, FSxSTR("a"), FSxSTR("tud"), FSxSTR("tud, "), FSxSTR("tta"), FSxSTR("V"), 2, 9, FSxSTR("rutta"), FSxSTR("V")}, // VVS tyyp 29

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("da"), FSxSTR("L"), 3, 9, FSxSTR("sahmerda"), FSxSTR("V")}, // VVS tyyp 27 
{0, FSxSTR(""), FSxSTR("da"), FSxSTR("da, "), FSxSTR("da"), FSxSTR("L"), 3, 9, FSxSTR("sahmerda"), FSxSTR("V")}, // VVS tyyp 27 
{0, FSxSTR(""), FSxSTR("b"), FSxSTR("b, "), FSxSTR("da"), FSxSTR("L"), 3, 9, FSxSTR("sahmerda"), FSxSTR("V")}, // VVS tyyp 27 
{0, FSxSTR(""), FSxSTR("tud"), FSxSTR("tud, "), FSxSTR("da"), FSxSTR("L"), 3, 9, FSxSTR("sahmerda"), FSxSTR("V")}, // VVS tyyp 27 

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("ma"), FSxSTR("V"), 2, 2, FSxSTR("h\x00E4ma"), FSxSTR("V")}, // VVS tyyp 27 h�ma
{0, FSxSTR(""), FSxSTR("da"), FSxSTR("da, "), FSxSTR("ma"), FSxSTR("V"), 2, 2, FSxSTR("h\x00E4ma"), FSxSTR("V")}, // VVS tyyp 27 h�ma
{0, FSxSTR(""), FSxSTR("b"), FSxSTR("b, "), FSxSTR("ma"), FSxSTR("V"), 2, 2, FSxSTR("h\x00E4ma"), FSxSTR("V")}, // VVS tyyp 27 h�ma
{0, FSxSTR(""), FSxSTR("tud"), FSxSTR("tud, "), FSxSTR("ma"), FSxSTR("V"), 2, 2, FSxSTR("h\x00E4ma"), FSxSTR("V")}, // VVS tyyp 27 h�ma

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("ta"), FSxSTR("V"), 3, 9, FSxSTR("vajuta"), FSxSTR("V")}, // VVS tyyp 27
{0, FSxSTR(""), FSxSTR("da"), FSxSTR("da, "), FSxSTR("ta"), FSxSTR("V"), 3, 9, FSxSTR("vajuta"), FSxSTR("V")}, // VVS tyyp 27
{0, FSxSTR(""), FSxSTR("b"), FSxSTR("b, "), FSxSTR("ta"), FSxSTR("V"), 3, 9, FSxSTR("vajuta"), FSxSTR("V")}, // VVS tyyp 27
{0, FSxSTR(""), FSxSTR("tud"), FSxSTR("tud, "), FSxSTR("ta"), FSxSTR("V"), 3, 9, FSxSTR("vajuta"), FSxSTR("V")}, // VVS tyyp 27

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("hta"), FSxSTR("V"), 3, 9, FSxSTR("suigahta"), FSxSTR("V")}, // VVS tyyp 27
{0, FSxSTR(""), FSxSTR("da"), FSxSTR("da, "), FSxSTR("hta"), FSxSTR("V"), 3, 9, FSxSTR("suigahta"), FSxSTR("V")}, // VVS tyyp 27
{0, FSxSTR(""), FSxSTR("b"), FSxSTR("b, "), FSxSTR("hta"), FSxSTR("V"), 3, 9, FSxSTR("suigahta"), FSxSTR("V")}, // VVS tyyp 27
{0, FSxSTR(""), FSxSTR("tud"), FSxSTR("tud, "), FSxSTR("hta"), FSxSTR("V"), 3, 9, FSxSTR("suigahta"), FSxSTR("V")}, // VVS tyyp 27

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("sta"), FSxSTR(""), 3, 9, FSxSTR("lipsusta"), FSxSTR("V")}, // VVS tyyp 27
{0, FSxSTR(""), FSxSTR("da"), FSxSTR("da, "), FSxSTR("sta"), FSxSTR(""), 3, 9, FSxSTR("lipsusta"), FSxSTR("V")}, // VVS tyyp 27
{0, FSxSTR(""), FSxSTR("b"), FSxSTR("b, "), FSxSTR("sta"), FSxSTR(""), 3, 9, FSxSTR("lipsusta"), FSxSTR("V")}, // VVS tyyp 27
{0, FSxSTR(""), FSxSTR("tud"), FSxSTR("tud, "), FSxSTR("sta"), FSxSTR(""), 3, 9, FSxSTR("lipsusta"), FSxSTR("V")}, // VVS tyyp 27

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("ne"), FSxSTR(""), 2, 3, FSxSTR("leevene"), FSxSTR("V")}, // VVS tyyp 27
{0, FSxSTR(""), FSxSTR("da"), FSxSTR("da, "), FSxSTR("ne"), FSxSTR(""), 2, 3, FSxSTR("leevene"), FSxSTR("V")}, // VVS tyyp 27
{0, FSxSTR(""), FSxSTR("b"), FSxSTR("b, "), FSxSTR("ne"), FSxSTR(""), 2, 3, FSxSTR("leevene"), FSxSTR("V")}, // VVS tyyp 27
{0, FSxSTR(""), FSxSTR("tud"), FSxSTR("tud, "), FSxSTR("ne"), FSxSTR(""), 2, 3, FSxSTR("leevene"), FSxSTR("V")}, // VVS tyyp 27

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("tse"), FSxSTR("CV"), 2, 9, FSxSTR("vandaalitse"), FSxSTR("V")}, // VVS tyyp 27
{0, FSxSTR(""), FSxSTR("da"), FSxSTR("da, "), FSxSTR("tse"), FSxSTR("CV"), 2, 9, FSxSTR("vandaalitse"), FSxSTR("V")}, // VVS tyyp 27
{0, FSxSTR(""), FSxSTR("b"), FSxSTR("b, "), FSxSTR("tse"), FSxSTR("CV"), 2, 9, FSxSTR("vandaalitse"), FSxSTR("V")}, // VVS tyyp 27
{0, FSxSTR(""), FSxSTR("tud"), FSxSTR("tud, "), FSxSTR("tse"), FSxSTR("CV"), 2, 9, FSxSTR("vandaalitse"), FSxSTR("V")}, // VVS tyyp 27

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("tu"), FSxSTR("V"), 3, 9, FSxSTR("kopitu"), FSxSTR("V")}, // VVS tyyp 27
{0, FSxSTR(""), FSxSTR("da"), FSxSTR("da, "), FSxSTR("tu"), FSxSTR("V"), 3, 9, FSxSTR("kopitu"), FSxSTR("V")}, // VVS tyyp 27
{0, FSxSTR(""), FSxSTR("b"), FSxSTR("b, "), FSxSTR("tu"), FSxSTR("V"), 3, 9, FSxSTR("kopitu"), FSxSTR("V")}, // VVS tyyp 27
{0, FSxSTR(""), FSxSTR("tud"), FSxSTR("tud, "), FSxSTR("tu"), FSxSTR("V"), 3, 9, FSxSTR("kopitu"), FSxSTR("V")}, // VVS tyyp 27

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("stu"), FSxSTR("V"), 2, 9, FSxSTR("libastu"), FSxSTR("V")}, // VVS tyyp 27
{0, FSxSTR(""), FSxSTR("da"), FSxSTR("da, "), FSxSTR("stu"), FSxSTR("V"), 2, 9, FSxSTR("libastu"), FSxSTR("V")}, // VVS tyyp 27
{0, FSxSTR(""), FSxSTR("b"), FSxSTR("b, "), FSxSTR("stu"), FSxSTR("V"), 2, 9, FSxSTR("libastu"), FSxSTR("V")}, // VVS tyyp 27
{0, FSxSTR(""), FSxSTR("tud"), FSxSTR("tud, "), FSxSTR("stu"), FSxSTR("V"), 2, 9, FSxSTR("libastu"), FSxSTR("V")}, // VVS tyyp 27

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("i"), FSxSTR("C"), 2, 2, FSxSTR("logi"), FSxSTR("V")}, // VVS tyyp 27 
{0, FSxSTR(""), FSxSTR("da"), FSxSTR("da, "), FSxSTR("i"), FSxSTR("C"), 2, 2, FSxSTR("logi"), FSxSTR("V")}, // VVS tyyp 27 
{0, FSxSTR(""), FSxSTR("b"), FSxSTR("b, "), FSxSTR("i"), FSxSTR("C"), 2, 2, FSxSTR("logi"), FSxSTR("V")}, // VVS tyyp 27 
{0, FSxSTR(""), FSxSTR("tud"), FSxSTR("tud, "), FSxSTR("i"), FSxSTR("C"), 2, 2, FSxSTR("logi"), FSxSTR("V")}, // VVS tyyp 27 

{0, FSxSTR(""), FSxSTR("ma"), FSxSTR("ma, "), FSxSTR("u"), FSxSTR("C"), 2, 2, FSxSTR("jahu"), FSxSTR("V")}, // VVS tyyp 27 
{0, FSxSTR(""), FSxSTR("da"), FSxSTR("da, "), FSxSTR("u"), FSxSTR("C"), 2, 2, FSxSTR("jahu"), FSxSTR("V")}, // VVS tyyp 27 
{0, FSxSTR(""), FSxSTR("b"), FSxSTR("b, "), FSxSTR("u"), FSxSTR("C"), 2, 2, FSxSTR("jahu"), FSxSTR("V")}, // VVS tyyp 27 
{0, FSxSTR(""), FSxSTR("tud"), FSxSTR("tud, "), FSxSTR("u"), FSxSTR("C"), 2, 2, FSxSTR("jahu"), FSxSTR("V")}, // VVS tyyp 27 
};

static  FSxC5I1 _pn_lopud_jm_[] =
    {
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed1, FSxSTR(""),      FSxSTR("adt, "),    FSxSTR(""),   FSxSTR("adt, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed1, FSxSTR(""),      FSxSTR("sg g, "),   FSxSTR(""),   FSxSTR("sg g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed1, FSxSTR(""),      FSxSTR("sg p, "),   FSxSTR(""),   FSxSTR("sg p, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed1, FSxSTR("d"),     FSxSTR("sg p, "),   FSxSTR("d"),  FSxSTR("sg p, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed1, FSxSTR("d"),     FSxSTR("pl n, "),   FSxSTR(""),   FSxSTR("sg g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed1, FSxSTR("de"),    FSxSTR("pl g, "),   FSxSTR("de"), FSxSTR("pl g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed1, FSxSTR("dega"),  FSxSTR("pl kom, "), FSxSTR("de"), FSxSTR("pl g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed1, FSxSTR("deks"),  FSxSTR("pl tr, "),  FSxSTR("de"), FSxSTR("pl g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed1, FSxSTR("del"),   FSxSTR("pl ad, "),  FSxSTR("de"), FSxSTR("pl g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed1, FSxSTR("dele"),  FSxSTR("pl all, "), FSxSTR("de"), FSxSTR("pl g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed1, FSxSTR("delt"),  FSxSTR("pl abl, "), FSxSTR("de"), FSxSTR("pl g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed1, FSxSTR("dena"),  FSxSTR("pl es, "),  FSxSTR("de"), FSxSTR("pl g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed1, FSxSTR("deni"),  FSxSTR("pl ter, "), FSxSTR("de"), FSxSTR("pl g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed1, FSxSTR("des"),   FSxSTR("pl in, "),  FSxSTR("de"), FSxSTR("pl g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed1, FSxSTR("desse"), FSxSTR("pl ill, "), FSxSTR("de"), FSxSTR("pl g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed1, FSxSTR("dest"),  FSxSTR("pl el, "),  FSxSTR("de"), FSxSTR("pl g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed1, FSxSTR("deta"),  FSxSTR("pl ab, "),  FSxSTR("de"), FSxSTR("pl g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed5, FSxSTR("e"),     FSxSTR("pl p, "),   FSxSTR("e"),  FSxSTR("pl p, "), 0}, //
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed1, FSxSTR("ga"),    FSxSTR("sg kom, "), FSxSTR(""),   FSxSTR("sg g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed6, FSxSTR("i"),     FSxSTR("pl p, "),   FSxSTR("i"),  FSxSTR("pl p, "), 0}, //
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed3, FSxSTR("id"),    FSxSTR("pl p, "),   FSxSTR("id"), FSxSTR("pl p, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed3, FSxSTR("iks"),   FSxSTR("pl tr, "),  FSxSTR("id"), FSxSTR("pl p, "), 0}, //
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed3, FSxSTR("il"),    FSxSTR("pl ad, "),  FSxSTR("id"), FSxSTR("pl p, "), 0}, //
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed3, FSxSTR("ile"),   FSxSTR("pl all, "), FSxSTR("id"), FSxSTR("pl p, "), 0}, //
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed3, FSxSTR("ilt"),   FSxSTR("pl abl, "), FSxSTR("id"), FSxSTR("pl p, "), 0}, //
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed3, FSxSTR("ina"),   FSxSTR("pl es, "),  FSxSTR("id"), FSxSTR("pl p, "), 0}, //
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed3, FSxSTR("ini"),   FSxSTR("pl ter, "), FSxSTR("id"), FSxSTR("pl p, "), 0}, //
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed3, FSxSTR("is"),    FSxSTR("pl in, "),  FSxSTR("id"), FSxSTR("pl p, "), 0}, //
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed3, FSxSTR("isse"),  FSxSTR("pl ill, "), FSxSTR("id"), FSxSTR("pl p, "), 0}, //
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed3, FSxSTR("ist"),   FSxSTR("pl el, "),  FSxSTR("id"), FSxSTR("pl p, "), 0}, //
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed1, FSxSTR("ks"),    FSxSTR("sg tr, "),  FSxSTR(""),   FSxSTR("sg g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed1, FSxSTR("l"),     FSxSTR("sg ad, "),  FSxSTR(""),   FSxSTR("sg g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed1, FSxSTR("le"),    FSxSTR("sg all, "), FSxSTR(""),   FSxSTR("sg g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed1, FSxSTR("lt"),    FSxSTR("sg abl, "), FSxSTR(""),   FSxSTR("sg g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed1, FSxSTR("na"),    FSxSTR("sg es, "),  FSxSTR(""),   FSxSTR("sg g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed1, FSxSTR("ni"),    FSxSTR("sg ter, "), FSxSTR(""),   FSxSTR("sg g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed1, FSxSTR("s"),     FSxSTR("sg in, "),  FSxSTR(""),   FSxSTR("sg g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed1, FSxSTR("sid"),   FSxSTR("pl p, "),   FSxSTR(""),   FSxSTR("sg g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed6, FSxSTR("se"),    FSxSTR("adt, "),    FSxSTR("se"), FSxSTR("adt, "), 0},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed1, FSxSTR("sse"),   FSxSTR("sg ill, "), FSxSTR(""),   FSxSTR("sg g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed1, FSxSTR("st"),    FSxSTR("sg el, "),  FSxSTR(""),   FSxSTR("sg g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed2, FSxSTR("t"),     FSxSTR("sg p, "),   FSxSTR("t"),  FSxSTR("sg p, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed1, FSxSTR("ta"),    FSxSTR("sg ab, "),  FSxSTR(""),   FSxSTR("sg g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed2, FSxSTR("te"),    FSxSTR("pl g, "),   FSxSTR("te"), FSxSTR("pl g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed2, FSxSTR("tega"),  FSxSTR("pl kom, "), FSxSTR("te"), FSxSTR("pl g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed2, FSxSTR("teks"),  FSxSTR("pl tr, "),  FSxSTR("te"), FSxSTR("pl g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed2, FSxSTR("tel"),   FSxSTR("pl ad, "),  FSxSTR("te"), FSxSTR("pl g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed2, FSxSTR("tele"),  FSxSTR("pl all, "), FSxSTR("te"), FSxSTR("pl g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed2, FSxSTR("telt"),  FSxSTR("pl abl, "), FSxSTR("te"), FSxSTR("pl g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed2, FSxSTR("tena"),  FSxSTR("pl es, "),  FSxSTR("te"), FSxSTR("pl g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed2, FSxSTR("teni"),  FSxSTR("pl ter, "), FSxSTR("te"), FSxSTR("pl g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed2, FSxSTR("tes"),   FSxSTR("pl in, "),  FSxSTR("te"), FSxSTR("pl g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed2, FSxSTR("tesse"), FSxSTR("pl ill, "), FSxSTR("te"), FSxSTR("pl g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed2, FSxSTR("test"),  FSxSTR("pl el, "),  FSxSTR("te"), FSxSTR("pl g, "), 1},
    {(FSXSTRING *)&TaheHulgad::pn_eeltahed2, FSxSTR("teta"),  FSxSTR("pl ab, "),  FSxSTR("te"), FSxSTR("pl g, "), 1},
    // verbil�pud
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR(""),  FSxSTR("o, "), FSxSTR("b"), FSxSTR("b, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("b"),  FSxSTR("b, "), FSxSTR("b"), FSxSTR("b, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("d"),  FSxSTR("d, "), FSxSTR("b"), FSxSTR("b, "), 3}, 
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("da"),  FSxSTR("da, "), FSxSTR("da"), FSxSTR("da, "), 3}, // elada
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("da"),  FSxSTR("ta, "), FSxSTR("dud"), FSxSTR("tud, "), 3}, // ei riielda
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("dagu"),  FSxSTR("tagu, "), FSxSTR("dud"), FSxSTR("tud, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("daks"),  FSxSTR("taks, "), FSxSTR("dud"), FSxSTR("tud, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("dakse"),  FSxSTR("takse, "), FSxSTR("dud"), FSxSTR("tud, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("dama"),  FSxSTR("tama, "), FSxSTR("dud"), FSxSTR("tud, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("dav"),  FSxSTR("tav, "), FSxSTR("dud"), FSxSTR("tud, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("davat"),  FSxSTR("tavat, "), FSxSTR("dud"), FSxSTR("tud, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("des"),  FSxSTR("des, "), FSxSTR("da"), FSxSTR("da, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("di"),  FSxSTR("ti, "), FSxSTR("dud"), FSxSTR("tud, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("dud"),  FSxSTR("tud, "), FSxSTR("dud"), FSxSTR("tud, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("duks"),  FSxSTR("tuks, "), FSxSTR("dud"), FSxSTR("tud, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("duvat"),  FSxSTR("tuvat, "), FSxSTR("dud"), FSxSTR("tud, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("ge"),  FSxSTR("ge, "), FSxSTR("da"), FSxSTR("da, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("gem"),  FSxSTR("gem, "), FSxSTR("da"), FSxSTR("da, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("gu"),  FSxSTR("gu, "), FSxSTR("da"), FSxSTR("da, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("ke"),  FSxSTR("ge, "), FSxSTR("ta"), FSxSTR("da, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("kem"),  FSxSTR("gem, "), FSxSTR("ta"), FSxSTR("da, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("ks"),  FSxSTR("ks, "), FSxSTR("b"), FSxSTR("b, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("ksid"),  FSxSTR("ksid, "), FSxSTR("b"), FSxSTR("b, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("ksime"),  FSxSTR("ksime, "), FSxSTR("b"), FSxSTR("b, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("ksin"),  FSxSTR("ksin, "), FSxSTR("b"), FSxSTR("b, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("ksite"),  FSxSTR("ksite, "), FSxSTR("b"), FSxSTR("b, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("ku"),  FSxSTR("gu, "), FSxSTR("ta"), FSxSTR("da, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("ma"),  FSxSTR("ma, "), FSxSTR("ma"),  FSxSTR("ma, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("maks"),  FSxSTR("maks, "), FSxSTR("ma"),  FSxSTR("ma, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("mas"),  FSxSTR("mas, "), FSxSTR("ma"),  FSxSTR("ma, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("mast"),  FSxSTR("mast, "), FSxSTR("ma"),  FSxSTR("ma, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("mata"),  FSxSTR("mata, "), FSxSTR("ma"),  FSxSTR("ma, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("me"),  FSxSTR("me, "), FSxSTR("b"), FSxSTR("b, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("n"),  FSxSTR("n, "), FSxSTR("b"), FSxSTR("b, "), 3},
    // elanud, leppinud, riielnud
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("nud"),  FSxSTR("nud, "), FSxSTR("da"),  FSxSTR("da, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("nuks"),  FSxSTR("nuks, "), FSxSTR("da"),  FSxSTR("da, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("nuksid"),  FSxSTR("nuksid, "), FSxSTR("da"),  FSxSTR("da, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("nuksime"),  FSxSTR("nuksime, "), FSxSTR("da"),  FSxSTR("da, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("nuksin"),  FSxSTR("nuksin, "), FSxSTR("da"),  FSxSTR("da, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("nuksite"),  FSxSTR("nuksite, "), FSxSTR("da"),  FSxSTR("da, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("nuvat"),  FSxSTR("nuvat, "), FSxSTR("da"),  FSxSTR("da, "), 3},
    // h�panud
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("nud"),  FSxSTR("nud, "), FSxSTR("ta"),  FSxSTR("da, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("nuks"),  FSxSTR("nuks, "), FSxSTR("ta"),  FSxSTR("da, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("nuksid"),  FSxSTR("nuksid, "), FSxSTR("ta"),  FSxSTR("da, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("nuksime"),  FSxSTR("nuksime, "), FSxSTR("ta"),  FSxSTR("da, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("nuksin"),  FSxSTR("nuksin, "), FSxSTR("ta"),  FSxSTR("da, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("nuksite"),  FSxSTR("nuksite, "), FSxSTR("ta"),  FSxSTR("da, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("nuvat"),  FSxSTR("nuvat, "), FSxSTR("ta"),  FSxSTR("da, "), 3},

    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("s"),  FSxSTR("s, "), FSxSTR("ma"),  FSxSTR("ma, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("sid"),  FSxSTR("sid, "), FSxSTR("ma"),  FSxSTR("ma, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("sime"),  FSxSTR("sime, "), FSxSTR("ma"),  FSxSTR("ma, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("sin"),  FSxSTR("sin, "), FSxSTR("ma"),  FSxSTR("ma, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("site"),  FSxSTR("site, "), FSxSTR("ma"),  FSxSTR("ma, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("ta"),  FSxSTR("da, "), FSxSTR("ta"),  FSxSTR("da, "), 3}, // h�pata
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("ta"),  FSxSTR("ta, "), FSxSTR("tud"),  FSxSTR("tud, "), 3}, // ei elata
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("tagu"),  FSxSTR("tagu, "), FSxSTR("tud"), FSxSTR("tud, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("taks"),  FSxSTR("taks, "), FSxSTR("tud"), FSxSTR("tud, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("takse"),  FSxSTR("takse, "), FSxSTR("tud"), FSxSTR("tud, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("tama"),  FSxSTR("tama, "), FSxSTR("tud"), FSxSTR("tud, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("tav"),  FSxSTR("tav, "), FSxSTR("tud"), FSxSTR("tud, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("tavat"),  FSxSTR("tavat, "), FSxSTR("tud"), FSxSTR("tud, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("te"),  FSxSTR("te, "), FSxSTR("b"), FSxSTR("b, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("tes"),  FSxSTR("des, "), FSxSTR("ta"), FSxSTR("da, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("ti"),  FSxSTR("ti, "), FSxSTR("tud"), FSxSTR("tud, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("tud"),  FSxSTR("tud, "), FSxSTR("tud"), FSxSTR("tud, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("tuks"),  FSxSTR("tuks, "), FSxSTR("tud"), FSxSTR("tud, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("tuvat"),  FSxSTR("tuvat, "), FSxSTR("tud"), FSxSTR("tud, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("v"),  FSxSTR("v, "), FSxSTR("ma"), FSxSTR("ma, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("vad"),  FSxSTR("vad, "), FSxSTR("b"), FSxSTR("b, "), 3},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("vat"),  FSxSTR("vat, "), FSxSTR("ma"),  FSxSTR("ma, "), 3},
    };

static  FSxOC5 _verbi_lopud_jm_[] = // verbil�pud vana versioon
    {
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR(""),  FSxSTR("o, "), FSxSTR("b"), FSxSTR("b, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("b"),  FSxSTR("b, "), FSxSTR("b"), FSxSTR("b, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("d"),  FSxSTR("d, "), FSxSTR("b"), FSxSTR("b, ")}, 
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("da"),  FSxSTR("da, "), FSxSTR("da"), FSxSTR("da, ")}, // elada
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("da"),  FSxSTR("ta, "), FSxSTR("dud"), FSxSTR("tud, ")}, // ei riielda
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("dagu"),  FSxSTR("tagu, "), FSxSTR("dud"), FSxSTR("tud, ")},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("daks"),  FSxSTR("taks, "), FSxSTR("dud"), FSxSTR("tud, ")},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("dakse"),  FSxSTR("takse, "), FSxSTR("dud"), FSxSTR("tud, ")},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("dama"),  FSxSTR("tama, "), FSxSTR("dud"), FSxSTR("tud, ")},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("dav"),  FSxSTR("tav, "), FSxSTR("dud"), FSxSTR("tud, ")},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("davat"),  FSxSTR("tavat, "), FSxSTR("dud"), FSxSTR("tud, ")},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("des"),  FSxSTR("des, "), FSxSTR("da"), FSxSTR("da, ")},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("di"),  FSxSTR("ti, "), FSxSTR("dud"), FSxSTR("tud, ")},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("dud"),  FSxSTR("tud, "), FSxSTR("dud"), FSxSTR("tud, ")},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("duks"),  FSxSTR("tuks, "), FSxSTR("dud"), FSxSTR("tud, ")},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("duvat"),  FSxSTR("tuvat, "), FSxSTR("dud"), FSxSTR("tud, ")},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("ge"),  FSxSTR("ge, "), FSxSTR("da"), FSxSTR("da, ")},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("gem"),  FSxSTR("gem, "), FSxSTR("da"), FSxSTR("da, ")},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("gu"),  FSxSTR("gu, "), FSxSTR("da"), FSxSTR("da, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("ke"),  FSxSTR("ge, "), FSxSTR("ta"), FSxSTR("da, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("kem"),  FSxSTR("gem, "), FSxSTR("ta"), FSxSTR("da, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("ks"),  FSxSTR("ks, "), FSxSTR("b"), FSxSTR("b, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("ksid"),  FSxSTR("ksid, "), FSxSTR("b"), FSxSTR("b, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("ksime"),  FSxSTR("ksime, "), FSxSTR("b"), FSxSTR("b, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("ksin"),  FSxSTR("ksin, "), FSxSTR("b"), FSxSTR("b, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("ksite"),  FSxSTR("ksite, "), FSxSTR("b"), FSxSTR("b, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("ku"),  FSxSTR("gu, "), FSxSTR("ta"), FSxSTR("da, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("ma"),  FSxSTR("ma, "), FSxSTR("ma"),  FSxSTR("ma, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("maks"),  FSxSTR("maks, "), FSxSTR("ma"),  FSxSTR("ma, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("mas"),  FSxSTR("mas, "), FSxSTR("ma"),  FSxSTR("ma, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("mast"),  FSxSTR("mast, "), FSxSTR("ma"),  FSxSTR("ma, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("mata"),  FSxSTR("mata, "), FSxSTR("ma"),  FSxSTR("ma, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("me"),  FSxSTR("me, "), FSxSTR("b"), FSxSTR("b, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("n"),  FSxSTR("n, "), FSxSTR("b"), FSxSTR("b, ")},
    // elanud, leppinud, riielnud
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("nud"),  FSxSTR("nud, "), FSxSTR("da"),  FSxSTR("da, ")},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("nuks"),  FSxSTR("nuks, "), FSxSTR("da"),  FSxSTR("da, ")},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("nuksid"),  FSxSTR("nuksid, "), FSxSTR("da"),  FSxSTR("da, ")},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("nuksime"),  FSxSTR("nuksime, "), FSxSTR("da"),  FSxSTR("da, ")},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("nuksin"),  FSxSTR("nuksin, "), FSxSTR("da"),  FSxSTR("da, ")},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("nuksite"),  FSxSTR("nuksite, "), FSxSTR("da"),  FSxSTR("da, ")},
    {(FSXSTRING *)&TaheHulgad::aeiul, FSxSTR("nuvat"),  FSxSTR("nuvat, "), FSxSTR("da"),  FSxSTR("da, ")},
    // h�panud
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("nud"),  FSxSTR("nud, "), FSxSTR("ta"),  FSxSTR("da, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("nuks"),  FSxSTR("nuks, "), FSxSTR("ta"),  FSxSTR("da, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("nuksid"),  FSxSTR("nuksid, "), FSxSTR("ta"),  FSxSTR("da, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("nuksime"),  FSxSTR("nuksime, "), FSxSTR("ta"),  FSxSTR("da, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("nuksin"),  FSxSTR("nuksin, "), FSxSTR("ta"),  FSxSTR("da, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("nuksite"),  FSxSTR("nuksite, "), FSxSTR("ta"),  FSxSTR("da, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("nuvat"),  FSxSTR("nuvat, "), FSxSTR("ta"),  FSxSTR("da, ")},

    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("s"),  FSxSTR("s, "), FSxSTR("ma"),  FSxSTR("ma, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("sid"),  FSxSTR("sid, "), FSxSTR("ma"),  FSxSTR("ma, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("sime"),  FSxSTR("sime, "), FSxSTR("ma"),  FSxSTR("ma, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("sin"),  FSxSTR("sin, "), FSxSTR("ma"),  FSxSTR("ma, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("site"),  FSxSTR("site, "), FSxSTR("ma"),  FSxSTR("ma, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("ta"),  FSxSTR("da, "), FSxSTR("ta"),  FSxSTR("da, ")}, // h�pata
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("ta"),  FSxSTR("ta, "), FSxSTR("tud"),  FSxSTR("tud, ")}, // ei elata
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("tagu"),  FSxSTR("tagu, "), FSxSTR("tud"), FSxSTR("tud, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("taks"),  FSxSTR("taks, "), FSxSTR("tud"), FSxSTR("tud, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("takse"),  FSxSTR("takse, "), FSxSTR("tud"), FSxSTR("tud, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("tama"),  FSxSTR("tama, "), FSxSTR("tud"), FSxSTR("tud, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("tav"),  FSxSTR("tav, "), FSxSTR("tud"), FSxSTR("tud, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("tavat"),  FSxSTR("tavat, "), FSxSTR("tud"), FSxSTR("tud, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("te"),  FSxSTR("te, "), FSxSTR("b"), FSxSTR("b, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("tes"),  FSxSTR("des, "), FSxSTR("ta"), FSxSTR("da, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("ti"),  FSxSTR("ti, "), FSxSTR("tud"), FSxSTR("tud, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("tud"),  FSxSTR("tud, "), FSxSTR("tud"), FSxSTR("tud, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("tuks"),  FSxSTR("tuks, "), FSxSTR("tud"), FSxSTR("tud, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("tuvat"),  FSxSTR("tuvat, "), FSxSTR("tud"), FSxSTR("tud, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("v"),  FSxSTR("v, "), FSxSTR("ma"), FSxSTR("ma, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("vad"),  FSxSTR("vad, "), FSxSTR("b"), FSxSTR("b, ")},
    {(FSXSTRING *)&TaheHulgad::aeiu, FSxSTR("vat"),  FSxSTR("vat, "), FSxSTR("ma"),  FSxSTR("ma, ")},
    };
// ----
static  FSxC5 ad_hoc_sonad[] =
    {
    {FSxSTR("S\x00FCnd"), FSxSTR("s\x00FCnd"),  FSxSTR("0"), FSxSTR("Y"),  FSxSTR("?, ") },
    {FSxSTR("VII"),  FSxSTR("VII"),   FSxSTR("0"), FSxSTR("O"),  FSxSTR("?, ") },
    {FSxSTR("eks"),  FSxSTR("eks"),   FSxSTR("0"), FSxSTR("Y"),  FSxSTR("?, ") },
    {FSxSTR("end"),  FSxSTR("end"),   FSxSTR("0"), FSxSTR("Y"),  FSxSTR("?, ") },
    {FSxSTR("jaan"), FSxSTR("jaan"),  FSxSTR("0"), FSxSTR("Y"),  FSxSTR("?, ") },
    {FSxSTR("komm"), FSxSTR("komm"),  FSxSTR("0"), FSxSTR("Y"),  FSxSTR("?, ") },
    {FSxSTR("sel"),  FSxSTR("sel"),   FSxSTR("0"), FSxSTR("Y"),  FSxSTR("?, ") },
    {FSxSTR("s\x00FCnd"), FSxSTR("s\x00FCnd"),  FSxSTR("0"), FSxSTR("Y"),  FSxSTR("?, ") },
    {FSxSTR("va"),   FSxSTR("va"),    FSxSTR("0"), FSxSTR("Y"),  FSxSTR("?, ") },
    {FSxSTR("vii"),  FSxSTR("vii"),   FSxSTR("0"), FSxSTR("O"),  FSxSTR("?, ") },
    };
static  FSxI2C5I1C4 ad_hoc_vormid[]= 
    {
    // V+mata = A=mata+0 
    {1, 1, FSxSTR(""),  FSxSTR("mata"),  FSxSTR("V"),   FSxSTR("mata, "),  FSxSTR("mata"),  0,  FSxSTR("=mata"), FSxSTR("0"),    FSxSTR("A"),     FSxSTR("")       },
    // V+nud = A=nud+0, A=nu(d)+d, S=nu+d 
    {1, 1, FSxSTR(""),  FSxSTR("nud"),   FSxSTR("V"),   FSxSTR("nud, "),   FSxSTR("nud"),   0,  FSxSTR("=nud"),  FSxSTR("0"),    FSxSTR("A"),     FSxSTR("")       },
    {1, 1, FSxSTR(""),  FSxSTR("nud"),   FSxSTR("V"),   FSxSTR("nud, "),   FSxSTR("nud"),   0,  FSxSTR("=nud"),  FSxSTR("0"),    FSxSTR("A"),     FSxSTR("sg n, ") },
    {1, 0, FSxSTR(""),  FSxSTR("nud"),   FSxSTR("V"),   FSxSTR("nud, "),   FSxSTR("nud"),   0,  FSxSTR("=nud"),  FSxSTR("d"),    FSxSTR("A"),     FSxSTR("pl n, ") },
    {0, 1, FSxSTR(""),  FSxSTR("nud"),   FSxSTR("V"),   FSxSTR("nud, "),   FSxSTR("nu"),    0,  FSxSTR("=nu"),   FSxSTR("d"),    FSxSTR("A"),     FSxSTR("pl n, ") },
    {1, 1, FSxSTR(""),  FSxSTR("nud"),   FSxSTR("V"),   FSxSTR("nud, "),   FSxSTR("nu"),    0,  FSxSTR("=nu"),   FSxSTR("d"),    FSxSTR("S"),     FSxSTR("pl n, ") },
    // V+nuks = A=nu(d)+ks, S=nu+ks 
    {1, 0, FSxSTR(""),  FSxSTR("nuks"),  FSxSTR("V"),   FSxSTR("nuks, "),  FSxSTR("nud"),   0,  FSxSTR("=nud"),  FSxSTR("ks"),    FSxSTR("A"),    FSxSTR("sg tr, ") },
    {0, 1, FSxSTR(""),  FSxSTR("nuks"),  FSxSTR("V"),   FSxSTR("nuks, "),  FSxSTR("nu"),    0,  FSxSTR("=nu"),   FSxSTR("ks"),    FSxSTR("A"),    FSxSTR("sg tr, ") },
    {1, 1, FSxSTR(""),  FSxSTR("nuks"),  FSxSTR("V"),   FSxSTR("nuks, "),  FSxSTR("nu"),    0,  FSxSTR("=nu"),   FSxSTR("ks"),    FSxSTR("S"),    FSxSTR("sg tr, ") },
    // S=[ntd]ud+d = A=[ntd]ud+0, A=[ntd]u(d)+d 
    {1, 1, FSxSTR("=nu"), FSxSTR("d"),   FSxSTR("S"),   FSxSTR("pl n, "),  FSxSTR("nud"),   0,  FSxSTR("d"),  FSxSTR("0"),     FSxSTR("A"),     FSxSTR("")       },  
    {1, 1, FSxSTR("=nu"), FSxSTR("d"),   FSxSTR("S"),   FSxSTR("pl n, "),  FSxSTR("nud"),   0,  FSxSTR("d"),  FSxSTR("0"),     FSxSTR("A"),     FSxSTR("sg n, ") }, 
    {1, 0, FSxSTR("=nu"), FSxSTR("d"),   FSxSTR("S"),   FSxSTR("pl n, "),  FSxSTR("nud"),   0,  FSxSTR("d"),  FSxSTR("d"),     FSxSTR("A"),     FSxSTR("pl n, ") }, 
    {0, 1, FSxSTR("=nu"), FSxSTR("d"),   FSxSTR("S"),   FSxSTR("pl n, "),  FSxSTR("nu"),    0,  FSxSTR(""),   FSxSTR("d"),     FSxSTR("A"),     FSxSTR("pl n, ") },  
    {1, 1, FSxSTR("=du"), FSxSTR("d"),   FSxSTR("S"),   FSxSTR("pl n, "),  FSxSTR("dud"),   0,  FSxSTR("d"),  FSxSTR("0"),     FSxSTR("A"),     FSxSTR("")       },  
    {1, 1, FSxSTR("=du"), FSxSTR("d"),   FSxSTR("S"),   FSxSTR("pl n, "),  FSxSTR("dud"),   0,  FSxSTR("d"),  FSxSTR("0"),     FSxSTR("A"),     FSxSTR("sg n, ") }, 
    {1, 0, FSxSTR("=du"), FSxSTR("d"),   FSxSTR("S"),   FSxSTR("pl n, "),  FSxSTR("dud"),   0,  FSxSTR("d"),  FSxSTR("d"),     FSxSTR("A"),     FSxSTR("pl n, ") }, 
    {0, 1, FSxSTR("=du"), FSxSTR("d"),   FSxSTR("S"),   FSxSTR("pl n, "),  FSxSTR("du"),    0,  FSxSTR(""),   FSxSTR("d"),     FSxSTR("A"),     FSxSTR("pl n, ") },  
    {1, 1, FSxSTR("=tu"), FSxSTR("d"),   FSxSTR("S"),   FSxSTR("pl n, "),  FSxSTR("tud"),   0,  FSxSTR("d"),  FSxSTR("0"),     FSxSTR("A"),     FSxSTR("")       },  
    {1, 1, FSxSTR("=tu"), FSxSTR("d"),   FSxSTR("S"),   FSxSTR("pl n, "),  FSxSTR("tud"),   0,  FSxSTR("d"),  FSxSTR("0"),     FSxSTR("A"),     FSxSTR("sg n, ") }, 
    {1, 0, FSxSTR("=tu"), FSxSTR("d"),   FSxSTR("S"),   FSxSTR("pl n, "),  FSxSTR("tud"),   0,  FSxSTR("d"),  FSxSTR("d"),     FSxSTR("A"),     FSxSTR("pl n, ") }, 
    {0, 1, FSxSTR("=tu"), FSxSTR("d"),   FSxSTR("S"),   FSxSTR("pl n, "),  FSxSTR("tu"),    0,  FSxSTR(""),   FSxSTR("d"),     FSxSTR("A"),     FSxSTR("pl n, ") },  
    // A+lt = D=lt 
    {1, 1, FSxSTR(""),   FSxSTR("lt"),   FSxSTR("A"),   FSxSTR("sg abl, "), FSxSTR("lt"),   1,  FSxSTR("=lt"),   FSxSTR("0"),      FSxSTR("D"),     FSxSTR("")    },
    // C+lt = Dmalt 
    {1, 1, FSxSTR("ma"), FSxSTR("lt"),   FSxSTR("C"),   FSxSTR("sg abl, "), FSxSTR("lt"),   0,  FSxSTR("lt"),   FSxSTR("0"),      FSxSTR("D"),     FSxSTR("")     },
    {1, 1, FSxSTR("m"),  FSxSTR("lt"),   FSxSTR("C"),   FSxSTR("sg abl, "), FSxSTR("lt"),   0,  FSxSTR("alt"),  FSxSTR("0"),      FSxSTR("D"),     FSxSTR("")     },
    // S=[ndt]u+0 = A=nu(d)+0 
    {1, 0, FSxSTR("=nu"), FSxSTR("0"),   FSxSTR("S"),   FSxSTR("sg g, "),  FSxSTR("nud"),   0,  FSxSTR("d"),  FSxSTR("0"),     FSxSTR("A"),     FSxSTR("sg g, ") }, 
    {0, 1, FSxSTR("=nu"), FSxSTR("0"),   FSxSTR("S"),   FSxSTR("sg g, "),  FSxSTR("nu"),    0,  FSxSTR(""),   FSxSTR("0"),     FSxSTR("A"),     FSxSTR("sg g, ") }, 
    {1, 0, FSxSTR("=du"), FSxSTR("0"),   FSxSTR("S"),   FSxSTR("sg g, "),  FSxSTR("dud"),   0,  FSxSTR("d"),  FSxSTR("0"),     FSxSTR("A"),     FSxSTR("sg g, ") }, 
    {0, 1, FSxSTR("=du"), FSxSTR("0"),   FSxSTR("S"),   FSxSTR("sg g, "),  FSxSTR("du"),    0,  FSxSTR(""),   FSxSTR("0"),     FSxSTR("A"),     FSxSTR("sg g, ") }, 
    {1, 0, FSxSTR("=tu"), FSxSTR("0"),   FSxSTR("S"),   FSxSTR("sg g, "),  FSxSTR("tud"),   0,  FSxSTR("d"),  FSxSTR("0"),     FSxSTR("A"),     FSxSTR("sg g, ") }, 
    {0, 1, FSxSTR("=tu"), FSxSTR("0"),   FSxSTR("S"),   FSxSTR("sg g, "),  FSxSTR("tu"),    0,  FSxSTR(""),   FSxSTR("0"),     FSxSTR("A"),     FSxSTR("sg g, ") }, 
    // A[ntd]ud+0 = A=[ntd]ud+0 muutumatu 
    {1, 1, FSxSTR("nud"), FSxSTR("0"),   FSxSTR("A"),   FSxSTR("sg n, "),  FSxSTR("nud"),   0,  FSxSTR(""),      FSxSTR("0"),     FSxSTR("A"),     FSxSTR("")       }, 
    {1, 1, FSxSTR("dud"), FSxSTR("0"),   FSxSTR("A"),   FSxSTR("sg n, "),  FSxSTR("dud"),   0,  FSxSTR(""),      FSxSTR("0"),     FSxSTR("A"),     FSxSTR("")       }, 
    {1, 1, FSxSTR("tud"), FSxSTR("0"),   FSxSTR("A"),   FSxSTR("sg n, "),  FSxSTR("tud"),   0,  FSxSTR(""),      FSxSTR("0"),     FSxSTR("A"),     FSxSTR("")       }, 
    // V+[dt]av = A=[dt]av+0 
    {1, 1, FSxSTR(""),  FSxSTR("dav"),   FSxSTR("V"),   FSxSTR("tav, "),   FSxSTR("dav"),   0,  FSxSTR("=dav"),  FSxSTR("0"),     FSxSTR("A"),     FSxSTR("sg n, ") },
    {1, 1, FSxSTR(""),  FSxSTR("tav"),   FSxSTR("V"),   FSxSTR("tav, "),   FSxSTR("tav"),   0,  FSxSTR("=tav"),  FSxSTR("0"),     FSxSTR("A"),     FSxSTR("sg n, ") },
    // V+[dt]avat = A=[dt]av(a)+t 
    {1, 0, FSxSTR(""),  FSxSTR("davat"), FSxSTR("V"),   FSxSTR("tavat, "), FSxSTR("dav"),   0,  FSxSTR("=dav"),  FSxSTR("t"),     FSxSTR("A"),     FSxSTR("sg p, ") },
    {0, 1, FSxSTR(""),  FSxSTR("davat"), FSxSTR("V"),   FSxSTR("tavat, "), FSxSTR("dava"),  0,  FSxSTR("=dava"), FSxSTR("t"),     FSxSTR("A"),     FSxSTR("sg p, ") },
    {1, 0, FSxSTR(""),  FSxSTR("tavat"), FSxSTR("V"),   FSxSTR("tavat, "), FSxSTR("tav"),   0,  FSxSTR("=tav"),  FSxSTR("t"),     FSxSTR("A"),     FSxSTR("sg p, ") },
    {0, 1, FSxSTR(""),  FSxSTR("tavat"), FSxSTR("V"),   FSxSTR("tavat, "), FSxSTR("tava"),  0,  FSxSTR("=tava"), FSxSTR("t"),     FSxSTR("A"),     FSxSTR("sg p, ") },
    // V+[dt]ud = A=[dt]ud+0, A=[dt]u(d)+d, S=[dt]u+d 
    {1, 1, FSxSTR(""),  FSxSTR("dud"),   FSxSTR("V"),   FSxSTR("tud, "),   FSxSTR("dud"),   0,  FSxSTR("=dud"),  FSxSTR("0"),     FSxSTR("A"),     FSxSTR("")       },
    {1, 1, FSxSTR(""),  FSxSTR("dud"),   FSxSTR("V"),   FSxSTR("tud, "),   FSxSTR("dud"),   0,  FSxSTR("=dud"),  FSxSTR("0"),     FSxSTR("A"),     FSxSTR("sg n, ") },
    {1, 0, FSxSTR(""),  FSxSTR("dud"),   FSxSTR("V"),   FSxSTR("tud, "),   FSxSTR("dud"),   0,  FSxSTR("=dud"),  FSxSTR("d"),     FSxSTR("A"),     FSxSTR("pl n, ") },
    {0, 1, FSxSTR(""),  FSxSTR("dud"),   FSxSTR("V"),   FSxSTR("tud, "),   FSxSTR("du"),    0,  FSxSTR("=du"),   FSxSTR("d"),     FSxSTR("A"),     FSxSTR("pl n, ") },
    {1, 1, FSxSTR(""),  FSxSTR("dud"),   FSxSTR("V"),   FSxSTR("tud, "),   FSxSTR("du"),    0,  FSxSTR("=du"),   FSxSTR("d"),     FSxSTR("S"),     FSxSTR("pl n, ") },
    {1, 1, FSxSTR(""),  FSxSTR("tud"),   FSxSTR("V"),   FSxSTR("tud, "),   FSxSTR("tud"),   0,  FSxSTR("=tud"),  FSxSTR("0"),     FSxSTR("A"),     FSxSTR("")       },
    {1, 1, FSxSTR(""),  FSxSTR("tud"),   FSxSTR("V"),   FSxSTR("tud, "),   FSxSTR("tud"),   0,  FSxSTR("=tud"),  FSxSTR("0"),     FSxSTR("A"),     FSxSTR("sg n, ") },
    {1, 0, FSxSTR(""),  FSxSTR("tud"),   FSxSTR("V"),   FSxSTR("tud, "),   FSxSTR("tud"),   0,  FSxSTR("=tud"),  FSxSTR("d"),     FSxSTR("A"),     FSxSTR("pl n, ") },
    {0, 1, FSxSTR(""),  FSxSTR("tud"),   FSxSTR("V"),   FSxSTR("tud, "),   FSxSTR("tu"),    0,  FSxSTR("=tu"),   FSxSTR("d"),     FSxSTR("A"),     FSxSTR("pl n, ") },
    {1, 1, FSxSTR(""),  FSxSTR("tud"),   FSxSTR("V"),   FSxSTR("tud, "),   FSxSTR("tu"),    0,  FSxSTR("=tu"),   FSxSTR("d"),     FSxSTR("S"),     FSxSTR("pl n, ") },
    // V+[dt]uks = A=[dt]u(d)+ks 
    {1, 0, FSxSTR(""),  FSxSTR("duks"),  FSxSTR("V"),   FSxSTR("tuks, "),  FSxSTR("dud"),   0,  FSxSTR("=dud"),  FSxSTR("ks"),    FSxSTR("A"),    FSxSTR("sg tr, ") },
    {0, 1, FSxSTR(""),  FSxSTR("duks"),  FSxSTR("V"),   FSxSTR("tuks, "),  FSxSTR("du"),    0,  FSxSTR("=du"),   FSxSTR("ks"),    FSxSTR("A"),    FSxSTR("sg tr, ") },
    {1, 1, FSxSTR(""),  FSxSTR("duks"),  FSxSTR("V"),   FSxSTR("tuks, "),  FSxSTR("du"),    0,  FSxSTR("=du"),   FSxSTR("ks"),    FSxSTR("S"),    FSxSTR("sg tr, ") },
    {1, 0, FSxSTR(""),  FSxSTR("tuks"),  FSxSTR("V"),   FSxSTR("tuks, "),  FSxSTR("tud"),   0,  FSxSTR("=tud"),  FSxSTR("ks"),    FSxSTR("A"),    FSxSTR("sg tr, ") },
    {0, 1, FSxSTR(""),  FSxSTR("tuks"),  FSxSTR("V"),   FSxSTR("tuks, "),  FSxSTR("tu"),    0,  FSxSTR("=tu"),   FSxSTR("ks"),    FSxSTR("A"),    FSxSTR("sg tr, ") },
    {1, 1, FSxSTR(""),  FSxSTR("tuks"),  FSxSTR("V"),   FSxSTR("tuks, "),  FSxSTR("tu"),    0,  FSxSTR("=tu"),   FSxSTR("ks"),    FSxSTR("S"),    FSxSTR("sg tr, ") },
    // V+v = A=v+0 
    {1, 1, FSxSTR(""),  FSxSTR("v"),     FSxSTR("V"),   FSxSTR("v, "),     FSxSTR("v"),     0,  FSxSTR("=v"),     FSxSTR("0"),    FSxSTR("A"),    FSxSTR("sg n, ")  },
    // V+vad = A=v(a)+d 
    {1, 0, FSxSTR(""),  FSxSTR("vad"),   FSxSTR("V"),   FSxSTR("vad, "),   FSxSTR("v"),     3,  FSxSTR("=v"),     FSxSTR("d"),    FSxSTR("A"),    FSxSTR("pl n, ")  },
    {0, 1, FSxSTR(""),  FSxSTR("vad"),   FSxSTR("V"),   FSxSTR("vad, "),   FSxSTR("va"),    3,  FSxSTR("=va"),    FSxSTR("d"),    FSxSTR("A"),    FSxSTR("pl n, ")  },
    // V+vat = A=v(a)+t 
    {1, 0, FSxSTR(""),  FSxSTR("vat"),   FSxSTR("V"),   FSxSTR("vat, "),   FSxSTR("v"),     2,  FSxSTR("=v"),     FSxSTR("t"),    FSxSTR("A"),    FSxSTR("sg p, ") },
    {0, 1, FSxSTR(""),  FSxSTR("vat"),   FSxSTR("V"),   FSxSTR("vat, "),   FSxSTR("va"),    2,  FSxSTR("=va"),    FSxSTR("t"),    FSxSTR("A"),    FSxSTR("sg p, ") },
    };
static  FSxC1 ad_hoc_verbilopud[] =    //m�ned adhoc verbilopud
    {
        {FSxSTR("v")},      {FSxSTR("dav")},    {FSxSTR("tav")},    {FSxSTR("davat")}, 
        {FSxSTR("tavat")},  {FSxSTR("vad")},    {FSxSTR("vat")}, 
    };
static  FSxC1 _nr_lyh_[] =    //numbrile k�lge sobivad l�hendid
    {
        {FSxSTR("a")},   {FSxSTR("b")},  {FSxSTR("c")},  {FSxSTR("cm")},  {FSxSTR("d")}, 
        {FSxSTR("e")},   {FSxSTR("g")},  {FSxSTR("ha")}, {FSxSTR("hh")},  {FSxSTR("kg")},
        {FSxSTR("kgf")}, {FSxSTR("kl")}, {FSxSTR("km")}, {FSxSTR("m")},   {FSxSTR("mm")},
    };
static  FSxC1 _omastavad_[] =    //omastav ongi algvorm
    {
        {FSxSTR("iseenese")},    {FSxSTR("ise_enese")},   {FSxSTR("ligida")},        {FSxSTR("l\x00FChida")}, 
        {FSxSTR("l\x00E4heda")}, {FSxSTR("m\x00F5lema")}, {FSxSTR("omaenese")},      {FSxSTR("oma_enese")},
        {FSxSTR("teineteise")},  {FSxSTR("teine_teise")}, {FSxSTR("\x00FCksteise")}, {FSxSTR("\x00FCks_teise")}
    };
static  FSxC1 _pahad_hyyd_[] =  // ei sobi liits�nadesse
    {
        {FSxSTR("ena")},    {FSxSTR("pele")}, {FSxSTR("raip")}, {FSxSTR("vaat")}, {FSxSTR("paganamas")},
        {FSxSTR("servus")}, {FSxSTR("kurat")},     
    };
static  FSxC1 _head_om_[] =  // sobivad liits�nade 2. komponendiks 
    {
        {FSxSTR("k\x00F5lblik")}, {FSxSTR("k\x00F5lbulik")}, {FSxSTR("ohtlik")}, {FSxSTR("tundlik")}, {FSxSTR("suutlik")},
        {FSxSTR("k\x00F5lbmatu")},{FSxSTR("suutmatu")},      {FSxSTR("andeka")}, {FSxSTR("n\x00F5udlik")},
        {FSxSTR("v\x00F5imeka")}, {FSxSTR("osav")},          {FSxSTR("tihe")},
        {FSxSTR("kindel")},       {FSxSTR("kindla")}, 
        // muutumatud om_sonad
        {FSxSTR("karva")}, {FSxSTR("kasvu")}, {FSxSTR("moodi")}, {FSxSTR("v\x00E4rvi")}, 
        {FSxSTR("v\x00E4\x00E4rt")}, {FSxSTR("korras")},
    };
static  FSxC1 _head_gene_lopud_[] =  // sobivad gene algvormi l�puks 
    {
        {FSxSTR("ma")},  {FSxSTR("d")},   {FSxSTR("lt")}, {FSxSTR("nud")},  {FSxSTR("tud")}, {FSxSTR("dud")},
        {FSxSTR("tav")}, {FSxSTR("dav")}, {FSxSTR("v")},  {FSxSTR("mata")},
    };
static  FSxC1 _harvad_lopud_1_[] =  // ei sobi oletamisel sageli p�risnime l�puks 
    {
        {FSxSTR("na")}, {FSxSTR("ni")}, {FSxSTR("t")}, {FSxSTR("ta")}, {FSxSTR("te")}, 
    };
static  FSxC1 _sage_lopud_1_[] =  // sobivad oletamisel h�sti p�risnime l�puks 
    {
        {FSxSTR("de")}, {FSxSTR("ga")}, {FSxSTR("le")}, {FSxSTR("lt")}, {FSxSTR("sse")}, 
    };
static  FSxC1 _pahad_sufid_[] =  // ei sobi oletamisel sufiksiks 
    {
        {FSxSTR("ist")}, {FSxSTR("lu")}, {FSxSTR("du")}, {FSxSTR("kus")}, {FSxSTR("mini")}, {FSxSTR("iti")}, 
    };
static  FSxC1 _pahad_tyved2_[] =  // ei sobi oletamisel nimis�na viimaseks komponendiks 
    {
        {FSxSTR("induse")}, {FSxSTR("ustava")},{FSxSTR("sahvti")},
        {FSxSTR("aade")},   {FSxSTR("aare")},  {FSxSTR("aari")},  {FSxSTR("aaria")}, {FSxSTR("aate")}, 
        {FSxSTR("akti")},   {FSxSTR("aktiivne")}, {FSxSTR("aktiivse")},
        {FSxSTR("alane")},  {FSxSTR("alas")},  {FSxSTR("alase")}, {FSxSTR("alasi")}, {FSxSTR("andi")}, 
        {FSxSTR("anna")},   {FSxSTR("anni")},  {FSxSTR("asse")},  {FSxSTR("assi")},  {FSxSTR("aste")}, 
        {FSxSTR("astel")},  {FSxSTR("augu")},  {FSxSTR("aval")},  {FSxSTR("bell")},  {FSxSTR("biidi")},
        {FSxSTR("biit")},   {FSxSTR("biiti")}, {FSxSTR("bool")}, 
        {FSxSTR("booli")},  {FSxSTR("boor")},  {FSxSTR("boori")}, {FSxSTR("emis")},  {FSxSTR("emise")}, 
        {FSxSTR("ende")},   {FSxSTR("enne")},  {FSxSTR("foor")},  {FSxSTR("foori")},
        {FSxSTR("hein")},   {FSxSTR("iidi")},  {FSxSTR("iili")},  {FSxSTR("iive")},  {FSxSTR("ikoon")}, {FSxSTR("ikooni")},
        {FSxSTR("ilane")},  {FSxSTR("ilas")}, 
        {FSxSTR("ilase")},  {FSxSTR("imik")},  {FSxSTR("imiku")},
        {FSxSTR("ingel")},  {FSxSTR("ingli")}, {FSxSTR("ioon")},  {FSxSTR("iooni")}, {FSxSTR("iste")},
        {FSxSTR("kaan")},   {FSxSTR("kaani")}, {FSxSTR("kaar")},  {FSxSTR("kaare")},
        {FSxSTR("kade")},   {FSxSTR("kali")},  {FSxSTR("kann")},  
        {FSxSTR("kanni")},  {FSxSTR("kate")},  {FSxSTR("keti")},  {FSxSTR("kiin")},  {FSxSTR("kiini")},
        {FSxSTR("kilt")},   {FSxSTR("kilda")}, {FSxSTR("kildi")}, {FSxSTR("kilti")},
        {FSxSTR("kiti")},   {FSxSTR("konn")},  {FSxSTR("konna")}, {FSxSTR("kult")},  {FSxSTR("laad")}, 
        {FSxSTR("laadi")},  {FSxSTR("laane")}, {FSxSTR("laas")},  {FSxSTR("laada")}, {FSxSTR("laat")}, {FSxSTR("laata")},
        {FSxSTR("lage")},   {FSxSTR("lagi")},  {FSxSTR("landi")}, {FSxSTR("lant")},  
        {FSxSTR("lanti")},  {FSxSTR("lase")},  {FSxSTR("lasi")},  {FSxSTR("lass")},  {FSxSTR("last")}, 
        {FSxSTR("lasti")},  {FSxSTR("leen")},  {FSxSTR("leeni")}, {FSxSTR("leer")},  {FSxSTR("leeri")}, 
        {FSxSTR("liit")},   {FSxSTR("liidu")}, {FSxSTR("liitu")}, {FSxSTR("lina")},  {FSxSTR("ling")},
        {FSxSTR("link")},   {FSxSTR("linki")}, {FSxSTR("lits")},  {FSxSTR("litsi")}, {FSxSTR("lj\x00F6\x00F6")}, //lj��
        {FSxSTR("loid")}, 
        {FSxSTR("loiu")},   {FSxSTR("loti")},  {FSxSTR("lott")},  {FSxSTR("lotti")}, {FSxSTR("male")},  
        {FSxSTR("mann")},   {FSxSTR("manni")}, {FSxSTR("mant")},  {FSxSTR("mandi")}, {FSxSTR("manti")}, 
        {FSxSTR("mari")},   {FSxSTR("mast")},  {FSxSTR("mate")}, 
        {FSxSTR("mest")},   {FSxSTR("miin")},  {FSxSTR("miini")}, {FSxSTR("mink")},  {FSxSTR("minki")},
        {FSxSTR("mingi")},  {FSxSTR("naadi")}, {FSxSTR("naat")}, 
        {FSxSTR("naati")},  {FSxSTR("nati")},  {FSxSTR("natsioon")},{FSxSTR("natsiooni")},
        {FSxSTR("neer")},   {FSxSTR("neeru")}, {FSxSTR("neid")},  {FSxSTR("nina")}, 
        {FSxSTR("niidi")},  {FSxSTR("niini")}, {FSxSTR("niine")}, {FSxSTR("niit")}, 
        {FSxSTR("niiti")},  {FSxSTR("noova")},
        {FSxSTR("n\x00E4\x00E4r")}, {FSxSTR("n\x00E4\x00E4ri")},
        {FSxSTR("okas")},   {FSxSTR("okse")},  
        {FSxSTR("oomi")},
        {FSxSTR("ossa")},   {FSxSTR("paal")},  {FSxSTR("paali")}, {FSxSTR("ping")},  {FSxSTR("pingi")},  
        {FSxSTR("pood")},   {FSxSTR("poodi")}, {FSxSTR("poe")},
        {FSxSTR("poni")},   {FSxSTR("pordi")}, {FSxSTR("port")},  {FSxSTR("porti")}, {FSxSTR("raad")},  
        {FSxSTR("raadi")},  {FSxSTR("raal")},  {FSxSTR("raali")}, {FSxSTR("raats")}, 
        {FSxSTR("randi")},  {FSxSTR("rant")},  {FSxSTR("ranti")}, {FSxSTR("ratsioon")}, {FSxSTR("ratsiooni")},
        {FSxSTR("reid")}, 
        {FSxSTR("rida")},   {FSxSTR("riid")},  {FSxSTR("riigi")}, {FSxSTR("riit")}, 
        {FSxSTR("riiu")},   {FSxSTR("ring")}, 
        {FSxSTR("ringi")},  {FSxSTR("rist")},  {FSxSTR("risti")}, {FSxSTR("roid")},  {FSxSTR("rool")}, {FSxSTR("rooli")},
        {FSxSTR("saad")},
        {FSxSTR("saan")},   {FSxSTR("saani")},
        {FSxSTR("sahvt")}, 
        {FSxSTR("saki")},   {FSxSTR("sakk")},  {FSxSTR("sakki")}, {FSxSTR("sandi")},
        {FSxSTR("sant")}, 
        {FSxSTR("sante")},  {FSxSTR("santi")}, {FSxSTR("sasi")},  {FSxSTR("seen")},  {FSxSTR("seene")},
        {FSxSTR("seim")},   {FSxSTR("sendi")}, 
        {FSxSTR("sent")},   {FSxSTR("senti")}, {FSxSTR("sess")},  {FSxSTR("sesse")}, {FSxSTR("side")}, 
        {FSxSTR("sile")},   {FSxSTR("siid")},  {FSxSTR("siidi")},
        {FSxSTR("siin")},   {FSxSTR("siini")}, {FSxSTR("sina")},  {FSxSTR("sine")}, 
        {FSxSTR("sionism")},{FSxSTR("sionismi")},{FSxSTR("soon")},{FSxSTR("soone")},
        {FSxSTR("sule")}, 
        {FSxSTR("taks")},   {FSxSTR("taksi")}, {FSxSTR("takse")}, {FSxSTR("tall")},  {FSxSTR("talli")},
        {FSxSTR("tali")},   {FSxSTR("taline")},{FSxSTR("tati")},  {FSxSTR("tava")}, 
        {FSxSTR("teegi")},  {FSxSTR("teek")},  {FSxSTR("teeki")}, {FSxSTR("tele")},  
        {FSxSTR("tera")},   {FSxSTR("test")},  {FSxSTR("tikk")}, 
        {FSxSTR("tiku")}, 
        {FSxSTR("ting")},   {FSxSTR("tingi")}, {FSxSTR("tingu")}, {FSxSTR("tite")},  {FSxSTR("toor")}, 
        {FSxSTR("toori")},  {FSxSTR("tori")},  {FSxSTR("torin")}, {FSxSTR("torina")}, 
        {FSxSTR("tuur")},   {FSxSTR("tuuri")}, {FSxSTR("tust")},  {FSxSTR("tusti")}, 
        {FSxSTR("tuste")},  {FSxSTR("unna")},  {FSxSTR("ukse")}, 
        {FSxSTR("ustav")},  
        {FSxSTR("uure")},   {FSxSTR("uuri")},  {FSxSTR("vada")},  {FSxSTR("vaka")},  {FSxSTR("vakk")}, {FSxSTR("vakka")},
        {FSxSTR("vere")},   {FSxSTR("verre")}, {FSxSTR("vest")},  {FSxSTR("vesti")},
        {FSxSTR("vaks")},   {FSxSTR("viit")},  {FSxSTR("vile")},  {FSxSTR("vool")},  {FSxSTR("\x00E4ngi")},
    };
static  FSxC1 _ns_tylopud_[] =  // sg n mittesobivad t�vel�pud; oletamiseks 
    {
        {FSxSTR("aadi")}, {FSxSTR("andi")}, {FSxSTR("audi")}, {FSxSTR("eedi")}, {FSxSTR("eegi")},
        {FSxSTR("endi")}, {FSxSTR("erdi")}, {FSxSTR("iidi")}, {FSxSTR("indi")}, {FSxSTR("ondi")},
        {FSxSTR("oobi")}, {FSxSTR("oodi")}, {FSxSTR("ordi")}, {FSxSTR("uudi")}, {FSxSTR("\374\374di")}, // yydi 
        {FSxSTR("ismi")}, {FSxSTR("ikud")},
    };
static  FSxC1 _sobivad_tyved2_[] =  // l�hikesed, aga ikkagi sobiksid oletamisel nimis�na viimaseks komponendiks 
    {
        {FSxSTR("aeg")}, {FSxSTR("elu")}, {FSxSTR("ma")}, {FSxSTR("maa")},
        {FSxSTR("t\x00F6\x00F6")}, //* to'o'
        {FSxSTR("\365de")},    // o~de
        {FSxSTR("\365e")},     // o~e 
    };
static  FSxOPAHALP _pahad_sg_n_lopud_[] =  // ei sobi oletamisel sg n s�na l�puks 
    {
    {FSxSTR("sed"),  3},
	{FSxSTR("de"),   4},
	{FSxSTR("sel"),  3},
	{FSxSTR("ses"),  3},
	{FSxSTR("jat"),  2},
	{FSxSTR("sest"), 2},
	{FSxSTR("id"),   2}, // viimases silbis enne voib olla suval tahti 
	{FSxSTR("lt"),   2},
	{FSxSTR("ast"),  1},
	{FSxSTR("ist"),  2},
	{FSxSTR("ust"),  2},
	{FSxSTR("ost"),  2},
	{FSxSTR("ut"),   2},
    {FSxSTR("ga"),   2}, //2},  enne 3 silpi ja need koik on lyhikesed, nt. Watanaga, siis sg_n
//    {FSxSTR("le"),   2}, //3},  enne 2 silpi ja 1. lyhike, siis sg_n 
    {FSxSTR("se"),   2}, //4},  eelviimase silbi lopus on t voi hou voi sonas tapitaht, siis sg_n  
    {FSxSTR("te"),   2}, //5},  olgu VVK-se-te voi 5+ silpe 
    {FSxSTR("is"),   3}, //6},  viimases silbis enne voib olla konsonant 
    {FSxSTR("it"),   2}, //6},
    {FSxSTR("ks"),   3}, //7},  viimases silbis enne mistahes taht, vokaal 
    {FSxSTR("il"),   2}, //8},  nagu juhtum 6; + mobil 
    };

extern "C" // m�ned v�rdlusfunktsioonid
    {
    int FSxC1Srt(const void *ee1, const void *ee2 )// vajalik sortimiseks
        {
        int v;
        FSxC1 *e1=*(FSxC1 **)ee1, *e2=*(FSxC1 **)ee2;
        v = FSStrCmpW0( e1->string, e2->string);
        assert(v != 0);
        return v;
        }

    // ==0: kui v�ti == kirje v�ti
    //
    int FSxC1Bs(const void *ee1, const void *ee2 )// vajalik 2ndotsimiseks
        {
        //const FSxCHAR *e1=(const FSxCHAR *)ee1; 
        const FSxCHAR *e1=(const FSxCHAR *)ee1;
        const FSxC1   *e2=*(const FSxC1 **)ee2;
        return FSxSTRCMP( e1, e2->string);
        }
    
    // ==0: Kui v�tme algus == kirje v�ti
    //
    int FSxC1BsSamaAlgusega(const void *ee1, const void *ee2 )// vajalik 2ndotsimiseks
        {
        const FSxCHAR *e1=(const FSxCHAR *)ee1; // v�ti
        const FSxC1   *e2=*(const FSxC1 **)ee2; // kirje
        int i;
        for(i=0; e2->string[i] != 0 && TaheHulgad::FSxCHCMP(e1[i], e2->string[i])==0; i++)
            ;
        if(e2->string[i] == 0)
            return 0;

        return TaheHulgad::FSxCHCMP(e1[i], e2->string[i]);
        }
    int FSxC5I1Srt(const void *ee1, const void *ee2 )// vajalik sortimiseks
        {
        int v;
        const FSxC5I1 *e1=*(const FSxC5I1 **)ee1, *e2=*(const FSxC5I1 **)ee2;
        v = FSxSTRCMP( e1->lopp, e2->lopp);
        if (v==0)
            v = FSxSTRCMP( e1->vorm, e2->vorm);
        if (v==0)
            v = FSxSTRCMP( (const FSxCHAR *)*(e1->eeltahed), (const FSxCHAR *)*(e2->eeltahed));
        if (v==0)
            v = FSxSTRCMP( e1->tabeli_lopp, e2->tabeli_lopp);
        if (v==0)
            v = FSxSTRCMP( e1->tabeli_vorm, e2->tabeli_vorm);
        assert(v != 0);
        return v;
        }
    int FSxC5I1Bs(const void *ee1, const void *ee2 )// vajalik 2ndotsimiseks
        {
        const FSxCHAR *e1=(const FSxCHAR *)ee1; // v�ti
        const FSxC5I1 *e2=*(const FSxC5I1 **)ee2; // kirje
        return FSxSTRCMP( e1, e2->lopp);
        }
    int FSxC5Srt(const void *ee1, const void *ee2 )// vajalik sortimiseks
        {
        int v;
        const FSxC5 *e1=*(const FSxC5 **)ee1, *e2=*(const FSxC5 **)ee2;
        v = FSxSTRCMP( e1->sona, e2->sona);
        assert(v != 0);
        return v;
        }
    int FSxC5Bs(const void *ee1, const void *ee2 )// vajalik 2ndotsimiseks
        {
        const FSxCHAR *e1=(const FSxCHAR *)ee1; 
        const FSxC5   *e2=*(const FSxC5 **)ee2;
        return FSxSTRCMP( e1, e2->sona);
        }
    int FSxOC5Srt(const void *ee1, const void *ee2 )// vajalik sortimiseks
        {
        int v;
        const FSxOC5 *e1=*(const FSxOC5 **)ee1, *e2=*(const FSxOC5 **)ee2;
        v = FSxSTRCMP( e1->lopp, e2->lopp);
        if (v==0)
            v = FSxSTRCMP( (const FSxCHAR *)*(e1->eeltahed), (const FSxCHAR *)*(e2->eeltahed));
        if (v==0)
            v = FSxSTRCMP( e1->vorm, e2->vorm);
        if (v==0)
            v = FSxSTRCMP( e1->tabeli_lopp, e2->tabeli_lopp);
        if (v==0)
            v = FSxSTRCMP( e1->tabeli_vorm, e2->tabeli_vorm);
        assert(v != 0);
        return v;
        }
    int FSxOC5Bs(const void *ee1, const void *ee2 )// vajalik 2ndotsimiseks
        {
        const FSxCHAR *e1=(const FSxCHAR *)ee1; 
        const FSxOC5  *e2=*(const FSxOC5  **)ee2;
        return FSxSTRCMP( e1, e2->lopp);
        }
    int FSxI2C5I1C4Srt(const void *ee1, const void *ee2 )// vajalik sortimiseks
        {
        int v;
        const FSxI2C5I1C4 *e1=*(const FSxI2C5I1C4 **)ee1, *e2=*(const FSxI2C5I1C4 **)ee2;
        v = FSxSTRCMP( e1->on_vorm, e2->on_vorm);
        if (v==0)
            v = FSxSTRCMP( e1->on_sl, e2->on_sl);
        if (v==0)
            v = FSxSTRCMP( e1->on_lopp, e2->on_lopp);
        if (v==0)
            v = FSxSTRCMP( e1->kohustuslik_tyvelp, e2->kohustuslik_tyvelp);
        if (v==0)
            v = FSxSTRCMP( e1->eelmistel_keelatud_tyvelp, e2->eelmistel_keelatud_tyvelp);
        if (v==0)
            v = FSxSTRCMP( e1->uuele_tyvele_otsa, e2->uuele_tyvele_otsa);
        if (v==0)
            v = FSxSTRCMP( e1->uus_lp, e2->uus_lp);
        if (v==0)
            v = FSxSTRCMP( e1->uus_sl, e2->uus_sl);
        if (v==0)
            v = FSxSTRCMP( e1->uus_vorm, e2->uus_vorm);
        assert(v != 0);
        return v;
        }
    int FSxI2C5I1C4Bs(const void *ee1, const void *ee2 )// vajalik 2ndotsimiseks
        {
        const FSxCHAR *e1=(const FSxCHAR *)ee1; 
        const FSxI2C5I1C4 *e2=*(const FSxI2C5I1C4 **)ee2;
        return FSxSTRCMP( e1, e2->on_vorm);
        }
    int FSxOTABSrt(const void *ee1, const void *ee2 )// vajalik sortimiseks
        {
        int v;
        
        const FSxOTAB *e1=*(const FSxOTAB **)ee1, *e2=*(const FSxOTAB **)ee2;
        v = FSxSTRCMP( e1->lp, e2->lp);
        if (v==0)
            v = FSxSTRCMP( e1->vorm, e2->vorm);
        if (v==0)
            v = FSxSTRLEN(e2->u_tylp) - FSxSTRLEN(e1->u_tylp); // pikem u_tylp on eespool
        if (v==0)
            v = FSxSTRCMP( e1->u_tylp, e2->u_tylp);
        if (v==0)
            v = FSxSTRLEN(e2->a_tylp) - FSxSTRLEN(e1->a_tylp); // pikem a_tylp on eespool
        if (v==0)
            v = FSxSTRCMP( e1->a_tylp, e2->a_tylp);
        if (v==0)
            v = FSxSTRLEN(e2->meta) - FSxSTRLEN(e1->meta); // pikem meta on eespool
        if (v==0)
            v = FSxSTRCMP( e1->meta, e2->meta);
        if (v==0)
            {  // muutumatu silpide arvuga mallid ettepoole
            if (e1->min_silpe == e1->max_silpe)
                {
                if (e2->min_silpe == e2->max_silpe)
                    v = e1->min_silpe - e2->min_silpe; // kahest muutumatust v�iksem ettepoole
                else
                    v = -1;  // e1 ettepoole
                }
            else if (e2->min_silpe == e2->max_silpe)
                v = 1;
            else
                v = e1->min_silpe - e2->min_silpe;
            }
        if (v==0)
            v = e1->max_silpe - e2->max_silpe;
        if (v==0)
            v = FSxSTRCMP( e1->tyypsona, e2->tyypsona);
        assert(v != 0);
        return v;
        }
    int FSxOTABBs(const void *ee1, const void *ee2 )// vajalik 2ndotsimiseks
        {
        const FSxCHAR *e1=(const FSxCHAR *)ee1; 
        const FSxOTAB *e2=*(const FSxOTAB **)ee2;
        return FSxSTRCMP( e1, e2->lp);
        }
    int FSxOPAHALPSrt(const void *ee1, const void *ee2 )// vajalik sortimiseks
        {
        int v;
        FSxOPAHALP *e1=*(FSxOPAHALP **)ee1, *e2=*(FSxOPAHALP **)ee2;
        v = FSxSTRCMP( e1->tyvelp, e2->tyvelp);
        assert(v != 0);
        return v;
        }
    int FSxOPAHALP_Ls(const void *ee1, const void *ee2 )// vajalik lin otsimiseks
        {
        const FSXSTRING   e1 = (const FSxCHAR *)ee1; 
        const FSxOPAHALP *e2 = *(const FSxOPAHALP **)ee2;
        if (TaheHulgad::OnLopus(&e1, e2->tyvelp))
            return 0;
        else
            return -1;
        }
   }

AD_HOC::AD_HOC(void) // vt adhoc.h
    {
    vormid.Start(ad_hoc_vormid, sizeof(ad_hoc_vormid)/sizeof(FSxI2C5I1C4), FSxI2C5I1C4Srt,FSxI2C5I1C4Bs);
    sonad.Start(ad_hoc_sonad, sizeof(ad_hoc_sonad)/sizeof(FSxC5), FSxC5Srt,FSxC5Bs);
    verbilopud.Start(ad_hoc_verbilopud, sizeof(ad_hoc_verbilopud)/sizeof(FSxC1), FSxC1Srt,FSxC1Bs);
    }
 
MUUD_LOENDID::MUUD_LOENDID(void)
    {
    nr_lyh.Start(_nr_lyh_, sizeof(_nr_lyh_)/sizeof(FSxC1),FSxC1Srt, FSxC1Bs);
    omastavad.Start(_omastavad_, sizeof(_omastavad_)/sizeof(FSxC1),FSxC1Srt, FSxC1Bs);
    pahad_hyyd.Start(_pahad_hyyd_, sizeof(_pahad_hyyd_)/sizeof(FSxC1),FSxC1Srt, FSxC1Bs);
    head_om.Start(_head_om_, sizeof(_head_om_)/sizeof(FSxC1),FSxC1Srt, FSxC1BsSamaAlgusega);
    head_gene_lopud.Start(_head_gene_lopud_, sizeof(_head_gene_lopud_)/sizeof(FSxC1),FSxC1Srt, FSxC1Bs);
    }

OLETAJA_DCT::OLETAJA_DCT(void)
    {
    a_tyvi = FSxSTR("");

    harvad_lopud_1.Start(_harvad_lopud_1_, sizeof(_harvad_lopud_1_)/sizeof(FSxC1),FSxC1Srt, FSxC1Bs);
 
    sage_lopud_1.Start(_sage_lopud_1_, sizeof(_sage_lopud_1_)/sizeof(FSxC1),FSxC1Srt, FSxC1Bs);
    pahad_sufid.Start(_pahad_sufid_, sizeof(_pahad_sufid_)/sizeof(FSxC1),FSxC1Srt, FSxC1Bs);

    pahad_tyved2.Start(_pahad_tyved2_, sizeof(_pahad_tyved2_)/sizeof(FSxC1),FSxC1Srt, FSxC1Bs);
                                  ///< ei sobi oletamisel nimis�na viimaseks komponendiks 

    ns_tylopud.Start(_ns_tylopud_, sizeof(_ns_tylopud_)/sizeof(FSxC1),FSxC1Srt, FSxC1Bs);
                             ///< sg n mittesobivad t�vel�pud; oletamiseks 

    sobivad_tyved2.Start(_sobivad_tyved2_, sizeof(_sobivad_tyved2_)/sizeof(FSxC1),FSxC1Srt, FSxC1Bs);
            //l�hikesed, aga ikkagi sobiksid oletamisel nimis�na viimaseks komponendiks
 
    pn_lopud_jm.Start(_pn_lopud_jm_, sizeof(_pn_lopud_jm_)/sizeof(FSxC5I1),FSxC5I1Srt, FSxC5I1Bs);

    verbi_lopud_jm.Start(_verbi_lopud_jm_, sizeof(_verbi_lopud_jm_)/sizeof(FSxOC5),FSxOC5Srt, FSxOC5Bs);

    pahad_sg_n_lopud.Start(_pahad_sg_n_lopud_, sizeof(_pahad_sg_n_lopud_)/sizeof(FSxOPAHALP),FSxOPAHALPSrt, FSxOPAHALP_Ls);
    
    oletaja_tabel.Start(_oletaja_tabel_, sizeof(_oletaja_tabel_)/sizeof(FSxOTAB), FSxOTABSrt,FSxOTABBs);
    

    gene_oletaja_tabel.Start(_oletaja_tabel_, 
        sizeof(_oletaja_tabel_)/sizeof(FSxOTAB)); // jama korral throw(VEAD(...));
    //gene_oletaja_tabel.Start(oletaja_tabel);
    //gene_oletaja_tabel.SortUniq();

    assert(ClassInvariant());
    }

#else
    #error Defineeri FSCHAR_UNICODE
#endif
