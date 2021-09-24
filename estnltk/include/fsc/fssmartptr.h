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
#if !defined _FSSMARTPTR_H_
#define _FSSMARTPTR_H_

/**
* Class provides reference counting with autorelease for any memory block allocated with "new".
*/
template <class ITEM>
class CFSSmartPtr{
public:
	CFSSmartPtr() {
		Init();
	}
	CFSSmartPtr(ITEM *pItem) {
		Init();
		operator =(pItem);
	}
	CFSSmartPtr(const CFSSmartPtr &Ptr) {
		Init();
		operator =(Ptr);
	}
	virtual ~CFSSmartPtr() {
		Release();
	}

	CFSSmartPtr &operator =(ITEM *pItem) {
		Release();
		m_pItem=pItem;
		AddRef();
		return *this;
	}
	CFSSmartPtr &operator =(const CFSSmartPtr &Ptr) {
		Release();
		m_pItem=Ptr.m_pItem;
		m_pRefCount=Ptr.m_pRefCount;
		AddRef();
		return *this;
	}

	operator ITEM* () const {
		return m_pItem;
	}
	ITEM* operator ->() const {
		return m_pItem;
	}

protected:
	void Init() {
		m_pItem=0;
		m_pRefCount=0;
	}
	void AddRef(){
		if (!m_pItem) {
			return;
		}
		if (!m_pRefCount) {
			m_pRefCount=new INTATOMIC;
			(*m_pRefCount)=1;
		}
		else {
			FSAtomicInc(m_pRefCount);
		}
	}
	void Release(){
		if (!m_pRefCount) {
			return;
		}
		if (FSAtomicDec(m_pRefCount)<=0) {
			delete m_pRefCount;
			delete m_pItem;
		}
		m_pRefCount=0;
		m_pItem=0;
	}

	ITEM *m_pItem;
	INTATOMIC *m_pRefCount;
};

#endif // _FSSMARTPTR_H_
