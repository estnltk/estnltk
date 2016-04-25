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
#if !defined _FSUTIL_H_
#define _FSUTIL_H_

#if defined (WIN32)
#define FSUNUSED UNREFERENCED_PARAMETER
#else
int __FSUnused(...);
#define FSUNUSED(...) ((void)sizeof(__FSUnused(__VA_ARGS__)))
#endif

/**
* Template-based min-max functions, faster than standard min/max.
*/
template <class T1, class T2> T1 FSMIN(T1 a, T2 b) {
	return (a < b ? a : b);
}
template <class T1, class T2> T1 FSMAX(T1 a, T2 b) {
	return (a > b ? a : b);
}
template <class T1, class T2> T1 FSMINMAX(T1 a, T2 min, T2 max) {
	return FSMIN(FSMAX(a, min), max);
}

#define DECLARE_FSNOCOPY(Class) \
	Class(const Class &) { RT_ASSERT(false); } \
	Class &operator =(const Class &) { RT_ASSERT(false); return *this; }

/**
* Tries to assign one variable to another.
* @param[out] ItemDest Variable to be set.
* @param[in] ItemSource Source variable.
* @return true Assignment succeeded.
* @return false Assignment failed.
*/
template <class ITEMDEST, class ITEMSOURCE>
bool FSAssign(ITEMDEST &ItemDest, ITEMSOURCE ItemSource)
{
	ItemDest=(ITEMDEST)ItemSource;
	if (ItemSource!=(ITEMSOURCE)ItemDest) {
		return false;
	}
	return !((ItemSource>0)^(ItemDest>0));
}

/**
* Initializes memory for data with any block size.
* @param[in] pDest Memory block to be initialized.
* @param[in] Data Value that will be used on initialization.
* @param[in] iCount Count of blocks to be initialized (not bytes).
*/
template <class ITEM>
void FSMemSet(ITEM *pDest, ITEM Data, INTPTR iCount)
{
	for (; iCount>0; iCount--) {
		*pDest++=Data;
	}
}

#endif // _FSUTIL_H_
