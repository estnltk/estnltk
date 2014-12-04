#if !defined _FSLIST_H_
#define _FSLIST_H_

#include "fsexception.h"
#include "fsblockalloc.h"
#include "fsstream.h"

template <class KEY, class VALUE>
struct CFSKeyValuePair
{
	KEY Key;
	VALUE Value;
};

template <class SEARCHITEM, class KEY, class VALUE>
bool operator ==(const SEARCHITEM &SearchItem, const CFSKeyValuePair<KEY, VALUE> &Pair)
{
	return SearchItem==Pair.Key;
}

template <class SEARCHITEM, class KEY, class VALUE>
bool operator <(const SEARCHITEM &SearchItem, const CFSKeyValuePair<KEY, VALUE> &Pair)
{
	return SearchItem<Pair.Key;
}

/*
* Can be used to search from static arrays or key-value pairs
*/

template <class ITEM, class SEARCHITEM>
INTPTR FSArrayFind(const ITEM *pItems, INTPTR ipSize, const SEARCHITEM &SearchItem) {
	for (INTPTR ip=0; ip<ipSize; ip++) {
		if (SearchItem==pItems[ip]) return ip;
	}
	return -1;
}

template <size_t SIZE, class ITEM, class SEARCHITEM>
INTPTR FSArrayFind(const ITEM (&Items)[SIZE], const SEARCHITEM &SearchItem)
{
	return FSArrayFind(Items, SIZE, SearchItem);
}


template <class ITEM, class SEARCHITEM>
INTPTR FSArrayFind2(const ITEM *pItems, INTPTR ipSize, const SEARCHITEM &SearchItem) {
	INTPTR ipStart=0;
	INTPTR ipEnd=ipSize;
	for (;;) {
		if (ipStart>=ipEnd-1) {
			if (ipStart==ipEnd-1 && SearchItem==pItems[ipStart]) {
				return ipStart;
			} else {
				return -1;
			}
		}

		INTPTR ipMiddle=(ipStart+ipEnd)/2;
		if (SearchItem<pItems[ipMiddle]) {
			ipEnd=ipMiddle;
		} else {
			ipStart=ipMiddle;
		}
	}
}

template <size_t SIZE, class ITEM, class SEARCHITEM>
INTPTR FSArrayFind2(const ITEM (&Items)[SIZE], const SEARCHITEM &SearchItem)
{
	return FSArrayFind2(Items, SIZE, SearchItem);
}

/**
* Template class for simple type arrays (==vectors) (char, int, float, void *, small structures, classes etc).
* Do not use if element copying is expensive.\n
* Element access: Direct\n
* Begin-Add: Elements are copied\n
* Mid-Add: Elements are copied\n
* End-Add: Elements are sometimes copied\n
* Begin-Remove: Elements are copied\n
* Mid-Remove: Elements are copied\n
* End-Remove: Nothing\n
* Memory overhead:\n
* Growing: up to (element count * 1.25 + 8) * sizeof element\n
* Maximum: unlimited\n
* Compacted: None
* @sa CFSObjArray, CFSClassArray
*/
template <class ITEM>
class CFSArray{
public:
/**
* Constructs object with initial size.
* @param[in] ipSize Preallocate space for ipSize elements.
*/
	CFSArray(INTPTR ipSize=0)
	{
		if (ipSize<0) {
			ipSize=0;
		}
		m_ipItemCount=0;
		m_ipBufferSize=ipSize;
		m_pItems=(m_ipBufferSize ? CFSBlockAlloc<ITEM>::Alloc(m_ipBufferSize) : 0);
	}
	CFSArray(const CFSArray &Array)
	{
		m_ipItemCount=0;
		m_ipBufferSize=0;
		m_pItems=0;
		operator =(Array);
	}
#if defined (__FSCXX0X)
	CFSArray(CFSArray &&Array)
	{
		m_ipItemCount=Array.m_ipItemCount;
		Array.m_ipItemCount=0;
		m_ipBufferSize=Array.m_ipBufferSize;
		Array.m_ipBufferSize=0;
		m_pItems=Array.m_pItems;
		Array.m_pItems=0;
	}
#endif
	virtual ~CFSArray()
	{
		Cleanup();
	}

/**
* Removes all elements and reinitializes the class.
*/
	void Cleanup()
	{
		if (m_pItems){
			for (INTPTR ip=0; ip<m_ipItemCount; ip++) {
				OnItemDestroy(ip);
			}
			CFSBlockAlloc<ITEM>::Free(m_pItems, 0, m_ipItemCount);
			m_ipItemCount=0;
			m_ipBufferSize=0;
			m_pItems=0;
		}
	}

/**
* Compacts array and releases all unused resources.
*/
	void FreeExtra()
	{
		if (m_ipItemCount==0) {
			Cleanup();
		}
		else if (m_ipItemCount<m_ipBufferSize) {
			ITEM *pItems=CFSBlockAlloc<ITEM>::Alloc(m_ipItemCount);
			CFSBlockAlloc<ITEM>::AssignMove(pItems, m_pItems, m_ipItemCount);
			CFSBlockAlloc<ITEM>::Free(m_pItems, 0, m_ipItemCount);
			m_pItems=pItems;
			m_ipBufferSize=m_ipItemCount;
		}
	}

/**
* Returns size of the array.
* @return Number of elements in array.
*/
	INTPTR GetSize() const
	{
		return m_ipItemCount;
	}

/**
* Reserves buffer for array. Only expands bufffer, never shrinks.
* @param[in] ipSize New size of reserverd buffer.
*/
	void Reserve(INTPTR ipSize)
	{
		if (ipSize>m_ipBufferSize) {
			ITEM *pItems=CFSBlockAlloc<ITEM>::Alloc(ipSize);
			CFSBlockAlloc<ITEM>::AssignMove(pItems, m_pItems, m_ipItemCount);
			CFSBlockAlloc<ITEM>::Free(m_pItems, 0, m_ipItemCount);
			m_pItems=pItems;
			m_ipBufferSize=ipSize;
		}
	}

/**
* Sets array size.
* @param[in] ipSize New size for the array.
*/
	void SetSize(INTPTR ipSize, bool bReserveMore=true)
	{
		if (ipSize<=0){
			Cleanup();
		}
		if (ipSize<m_ipItemCount) {
			for (INTPTR ip=ipSize; ip<m_ipItemCount; ip++) {
				OnItemDestroy(ip);
				m_pItems[ip].~ITEM();
			}
			m_ipItemCount=ipSize;
		}
		else if (ipSize>m_ipItemCount) {
			if (ipSize>m_ipBufferSize) {
				Reserve(bReserveMore ? GetNewSize(ipSize) : ipSize);
			}
			CFSBlockAlloc<ITEM>::Init(m_pItems+m_ipItemCount, ipSize-m_ipItemCount);
			m_ipItemCount=ipSize;
		}
	}

/**
* Returns element of array.
* @param[in] ipIndex Index of element to receive.
* @return Element at requested index.
*/
	const ITEM &GetItem(INTPTR ipIndex) const
	{
		return operator[](ipIndex);
	}

/**
* Appends new element into array.
* @param[in] Item Element to add.
* @sa InsertItem
*/
	void AddItem(const ITEM &Item)
	{
		if (m_ipItemCount+1>m_ipBufferSize){
			Reserve(GetNewSize(m_ipItemCount+1));
		}
		CFSBlockAlloc<ITEM>::AssignCopy(m_pItems+m_ipItemCount, &Item, 1);
		m_ipItemCount++;
	}

/**
* Inserts new element into array.
* @param[in] ipIndex Index to add element to. ipIndex must be >=0 and <=GetSize().
* @param[in] Item Element to add.
* @sa AddItem
*/
	void InsertItem(INTPTR ipIndex, const ITEM &Item)
	{
		RT_ASSERT(ipIndex>=0 && ipIndex<=m_ipItemCount);
		if (ipIndex>=m_ipItemCount) {
			AddItem(Item);
			return;
		}
		if (m_ipItemCount<m_ipBufferSize){
			CFSBlockAlloc<ITEM>::AssignMove(m_pItems+m_ipItemCount, m_pItems+m_ipItemCount-1, 1);
			CFSBlockAlloc<ITEM>::Move(m_pItems+ipIndex+1, m_pItems+ipIndex, m_ipItemCount-ipIndex-1);
			m_pItems[ipIndex]=Item;
		}
		else{
			INTPTR ipNewSize=GetNewSize(m_ipItemCount+1);
			ITEM *pItems=CFSBlockAlloc<ITEM>::Alloc(ipNewSize);
			CFSBlockAlloc<ITEM>::AssignMove(pItems, m_pItems, ipIndex);
			CFSBlockAlloc<ITEM>::AssignCopy(pItems+ipIndex, &Item, 1);
			CFSBlockAlloc<ITEM>::AssignMove(pItems+ipIndex+1, m_pItems+ipIndex, m_ipItemCount-ipIndex);
			CFSBlockAlloc<ITEM>::Free(m_pItems, 0, m_ipItemCount);
			m_pItems=pItems;
			m_ipBufferSize=ipNewSize;
		}
		m_ipItemCount++;
	}

/**
* Removes element from array.
* @param[in] ipIndex Index of first element to remove.
* @param[in] ipCount Count of items to remove.
*/
	void RemoveItem(INTPTR ipIndex, INTPTR ipCount=1)
	{
		if (ipIndex>=m_ipItemCount) {
			return;
		}
		if (ipIndex<0) {
			ipCount+=ipIndex;
			ipIndex=0;
		}
		ipCount=FSMIN(ipCount, m_ipItemCount-ipIndex);
		if (ipCount<=0) {
			return;
		}

		for (INTPTR ip=0; ip<ipCount; ip++) {
			OnItemDestroy(ipIndex+ip);
		}
		CFSBlockAlloc<ITEM>::Move(m_pItems+ipIndex, m_pItems+ipIndex+ipCount, m_ipItemCount-ipIndex-ipCount);
		CFSBlockAlloc<ITEM>::Terminate(m_pItems+m_ipItemCount-ipCount, ipCount);
		m_ipItemCount-=ipCount;
	}

/**
* Returns element of array.
* @param[in] ipIndex Index of element to receive.
* @return Element at requested index.
*/
	const ITEM &operator[](INTPTR ipIndex) const
	{
		RT_ASSERT(ipIndex>=0 && ipIndex<m_ipItemCount); 
		return m_pItems[ipIndex];
	}

/**
* Returns reference of array element.
* @param[in] ipIndex Index of element to receive.
* @return Reference of element at requested index.
*/
	ITEM &operator[](INTPTR ipIndex)
	{
		RT_ASSERT(ipIndex>=0 && ipIndex<m_ipItemCount);
		return m_pItems[ipIndex];
	}

/*
* Copies one array to another.
* @param[in] Array Array to clone.
* @return Result of copy.
*/
	CFSArray &operator =(const CFSArray &Array)
	{
		if (&Array!=this) {
			Cleanup();
			m_ipItemCount=m_ipBufferSize=Array.m_ipItemCount;
			m_pItems=CFSBlockAlloc<ITEM>::Alloc(m_ipBufferSize);
			CFSBlockAlloc<ITEM>::AssignCopy(m_pItems, Array.m_pItems, m_ipItemCount);
			for (INTPTR ip=0; ip<m_ipItemCount; ip++) {
				OnItemCopy(ip);
			}
		}
		return *this;
	}
#if defined (__FSCXX0X)
	CFSArray &operator =(CFSArray &&Array)
	{
		if (&Array!=this) {
			Cleanup();
			m_ipItemCount=Array.m_ipItemCount;
			Array.m_ipItemCount=0;
			m_ipBufferSize=Array.m_ipBufferSize;
			Array.m_ipBufferSize=0;
			m_pItems=Array.m_pItems;
			Array.m_pItems=0;
		}
		return *this;
	}
#endif

	CFSArray operator +(const CFSArray &Array) const
	{
		CFSArray Result;
		Result.Reserve(GetSize()+Array.GetSize());
		Result+=*this;
		Result+=Array;
		return Result;
	}

/**
* Appends one array to another.
* @param[in] Array Array to append.
* @return Result of append (this).
* @sa Add
*/
	CFSArray &operator +=(const CFSArray &Array)
	{
		Add(Array);
		return *this;
	}

/**
* Appends one array to another.
* @param[in] Array Array to append.
* @sa operator +=
*/
	void Add(const CFSArray &Array)
	{
		if (m_ipItemCount+Array.m_ipItemCount>m_ipBufferSize){
			Reserve(GetNewSize(m_ipItemCount+Array.m_ipItemCount));
		}
		CFSBlockAlloc<ITEM>::AssignCopy(m_pItems+m_ipItemCount, Array.m_pItems, Array.m_ipItemCount);
		for (INTPTR ip=0; ip<Array.m_ipItemCount; ip++) {
			OnItemCopy(m_ipItemCount+ip);
		}
		m_ipItemCount+=Array.m_ipItemCount;
	}

/**
* Inserts one array into another.
* @param[in] ipIndex Index to insert array to. ipIndex must be >=0 and <=GetSize().
* @param[in] Array Array to insert.
* @sa operator +=
*/
	void Insert(INTPTR ipIndex, const CFSArray &Array)
	{
		RT_ASSERT(ipIndex>=0 && ipIndex<=m_ipItemCount);
		if (Array.m_ipItemCount<=0) {
			return;
		}
		if (ipIndex>=m_ipItemCount) {
			Add(Array);
			return;
		}
		if (m_ipItemCount+Array.m_ipItemCount>m_ipBufferSize || this==&Array){
			INTPTR ipNewSize=GetNewSize(m_ipItemCount+Array.m_ipItemCount);
			ITEM *pItems=CFSBlockAlloc<ITEM>::Alloc(ipNewSize);
			CFSBlockAlloc<ITEM>::AssignMove(pItems, m_pItems, ipIndex);
			CFSBlockAlloc<ITEM>::AssignCopy(pItems+ipIndex, Array.m_pItems, Array.m_ipItemCount);
			CFSBlockAlloc<ITEM>::AssignMove(pItems+ipIndex+Array.m_ipItemCount, m_pItems+ipIndex, m_ipItemCount-ipIndex);
			CFSBlockAlloc<ITEM>::Free(m_pItems, 0, m_ipItemCount);
			m_pItems=pItems;
			m_ipBufferSize=ipNewSize;
		}
		else{
			INTPTR ipAssign=FSMIN(m_ipItemCount-ipIndex, Array.m_ipItemCount);
			INTPTR ipCopy=m_ipItemCount-ipIndex-ipAssign;
			CFSBlockAlloc<ITEM>::AssignMove(m_pItems+ipIndex+Array.m_ipItemCount+ipCopy, m_pItems+ipIndex+ipCopy, ipAssign);
			CFSBlockAlloc<ITEM>::Move(m_pItems+ipIndex+Array.m_ipItemCount, m_pItems+ipIndex, ipCopy);
			ipCopy=ipAssign;
			ipAssign=Array.m_ipItemCount-ipCopy;
			CFSBlockAlloc<ITEM>::Copy(m_pItems+ipIndex, Array.m_pItems, ipCopy);
			CFSBlockAlloc<ITEM>::AssignCopy(m_pItems+ipIndex+ipCopy, Array.m_pItems+ipCopy, ipAssign);
		}
		for (INTPTR ip=0; ip<Array.m_ipItemCount; ip++) {
			OnItemCopy(ipIndex+ip);
		}
		m_ipItemCount+=Array.m_ipItemCount;
	}

/**
* Finds element in array.
* @param[in] Item Find element, that matches Item.
* @param[in] ipIndex Index of element to start search from.
* @return Index of first element, that matches Item.
* @retval -1 Not found.
*/
	INTPTR Find(const ITEM &Item, INTPTR ipIndex=0) const
	{
		if (ipIndex<0) {
			ipIndex=0;
		}
		for (INTPTR ip=ipIndex; ip<GetSize(); ip++){
			if (m_pItems[ip]==Item) {
				return ip;
			}
		}
		return -1;
	}

/**
* Swaps two elements.
* @param[in] ipIndex1 Index of first element to swap.
* @param[in] ipIndex2 Index of second element to swap.
*/
	void Swap(INTPTR ipIndex1, INTPTR ipIndex2)
	{
		RT_ASSERT(ipIndex1>=0 && ipIndex1<m_ipItemCount);
		RT_ASSERT(ipIndex2>=0 && ipIndex2<m_ipItemCount);
		if (ipIndex1!=ipIndex2) {
			ITEM Item(FSMove(m_pItems[ipIndex1]));
			m_pItems[ipIndex1]=FSMove(m_pItems[ipIndex2]);
			m_pItems[ipIndex2]=FSMove(Item);
		}
	}

	friend CFSStream &operator<<(CFSStream &Stream, const CFSArray &Array)
	{
		Stream << (UINTPTR)Array.GetSize();
		for (INTPTR ip=0; ip<Array.GetSize(); ip++) {
			Stream << Array.m_pItems[ip];
		}
		return Stream;
	}

	friend CFSStream &operator>>(CFSStream &Stream, CFSArray &Array)
	{
		INTPTR ipSize;
		Stream >> (UINTPTR &)ipSize;
		if (ipSize<0) {
			throw CFSFileException(CFSFileException::INVALIDDATA);
		}
		Array.SetSize(ipSize, false);
		for (INTPTR ip=0; ip<ipSize; ip++) {
			Stream >> Array.m_pItems[ip];
		}
		return Stream;
	}

protected:
/**
* Function is called if element is internally duplicated.
* @param[in] ipIndex Index of copied element.
*/
	virtual void OnItemCopy(INTPTR ipIndex) { FSUNUSED(ipIndex); }
/**
* Function is called if element is removed from array.
* @param[in] ipIndex Index of element that is removed.
*/
	virtual void OnItemDestroy(INTPTR ipIndex) { FSUNUSED(ipIndex); }

/**
* Heuristically estimates how big buffer to allocate.
* @param[in] ipMinSize Minimus size of buffer required.
* @return Size of the buffer to allocate.
*/
	virtual INTPTR GetNewSize(INTPTR ipMinSize) const
	{
		INTPTR ipSize=m_ipBufferSize*5/4+8;
		if (ipSize<ipMinSize) {
			ipSize=ipMinSize;
		}
		return ipSize;
	}

	ITEM *m_pItems;
	INTPTR m_ipItemCount;
	INTPTR m_ipBufferSize;
};

/**
* Array to store large objects/classes or bigger data blocks.
* If element is removed from array, it is automatically deleted.
* Class usage is very similar to CFSArray, except elements are pointers to memory blocks allocated with new.\n
* Typical usage: ObjArray.AddItem(new CFSString("tere"));\n
* Element access: Direct\n
* Begin-Add: Element references are copied\n
* Mid-Add: Element references are copied\n
* End-Add: Element references are sometimes copied\n
* Begin-Remove: Element references are copied\n
* Mid-Remove: Element references are copied\n
* End-Remove: Nothing\n
* Memory overhead:\n
* Growing: up to (element count * 1.25 + 8) * sizeof(void *) + element count * malloc overhead\n
* Maximum: unlimited\n
* Compacted: element count * (sizeof(void *) + malloc overhead)
*/
template <class ITEM> class CFSObjArray
: public CFSArray<ITEM *>
{
public:
	CFSObjArray() : CFSArray<ITEM *>() { }
	CFSObjArray(const CFSObjArray &Array)
	{
		operator =(Array);
	}
#if defined (__FSCXX0X)
	CFSObjArray(CFSObjArray &&Array)
	{
		operator =(FSMove(Array));
	}
#endif
	virtual ~CFSObjArray()
	{
		this->Cleanup();
	}

	CFSObjArray &operator =(const CFSObjArray &Array)
	{
		CFSArray<ITEM *>::operator =(Array);
		return *this;
	}
#if defined (__FSCXX0X)
	CFSObjArray &operator =(CFSObjArray &&Array)
	{
		CFSArray<ITEM *>::operator =(FSMove(Array));
		return *this;
	}
#endif

	CFSObjArray operator +(const CFSObjArray &Array) const
	{
		CFSObjArray Result;
		Result.Reserve(this->GetSize()+Array.GetSize());
		Result+=*this;
		Result+=Array;
		return Result;
	}

	CFSObjArray &operator +=(const CFSObjArray &Array)
	{
		CFSArray<ITEM *>::operator +=(Array);
		return *this;
	}

	friend CFSStream &operator<<(CFSStream &Stream, const CFSObjArray &Array)
	{
		Stream << (UINTPTR)Array.GetSize();
		for (INTPTR ip=0; ip<Array.GetSize(); ip++) {
			Stream << *Array.m_pItems[ip];
		}
		return Stream;
	}

	friend CFSStream &operator>>(CFSStream &Stream, CFSObjArray &Array)
	{
		Array.Cleanup();
		INTPTR ipSize;
		Stream >> (UINTPTR &)ipSize;
		if (ipSize<0) {
			throw CFSFileException(CFSFileException::INVALIDDATA);
		}
		Array.SetSize(ipSize, false);
		for (INTPTR ip=0; ip<ipSize; ip++) {
			Array.m_pItems[ip]=new ITEM;
			Stream >> *Array.m_pItems[ip];
		}
		return Stream;
	}

protected:
	virtual void OnItemCopy(INTPTR ipIndex)
	{
		if (this->m_pItems[ipIndex]) {
			this->m_pItems[ipIndex]=new ITEM(*this->m_pItems[ipIndex]);
		}
	}
	virtual void OnItemDestroy(INTPTR ipIndex)
	{
		if (this->m_pItems[ipIndex]) {
			delete this->m_pItems[ipIndex];
			this->m_pItems[ipIndex]=0;
		}
	}
};

/**
* Array to store large objects/classes or bigger data blocks.
* Class internal structure is equal to CFSObjArray, but I/O is masqueraded to contain classes, not class pointers.
* Typical usage: ClassArray.AddItem("tere");\n
* Element access, operation speeds and memory overhead are equal to CFSObjArray.
*/
template <class ITEM> class CFSClassArray
: public CFSObjArray<ITEM>
{
public:
	CFSClassArray() { }
	CFSClassArray(const CFSClassArray &Array) : CFSObjArray<ITEM>(Array) { }
#if defined (__FSCXX0X)
	CFSClassArray(CFSClassArray &&Array) : CFSObjArray<ITEM>(FSMove(Array)) { }
#endif
	virtual ~CFSClassArray() { }

	const ITEM &GetItem(INTPTR ipIndex) const
	{
		return *CFSObjArray<ITEM>::GetItem(ipIndex);
	}
	void InsertItem(INTPTR ipIndex, const ITEM &Item)
	{
		CFSObjArray<ITEM>::InsertItem(ipIndex, new ITEM(Item));
	}
	void AddItem(const ITEM &Item)
	{
		CFSObjArray<ITEM>::AddItem(new ITEM(Item));
	}

	const ITEM &operator[](INTPTR ipIndex) const
	{
		return *CFSObjArray<ITEM>::operator[](ipIndex);
	}
	ITEM &operator[](INTPTR ipIndex)
	{
		return *CFSObjArray<ITEM>::operator[](ipIndex);
	}

	CFSClassArray &operator =(const CFSClassArray &Array)
	{
		CFSObjArray<ITEM>::operator =(Array);
		return *this;
	}
#if defined (__FSCXX0X)
	CFSClassArray &operator =(CFSClassArray &&Array)
	{
		CFSObjArray<ITEM>::operator =(FSMove(Array));
		return *this;
	}
#endif

	CFSClassArray operator +(const CFSClassArray &Array) const
	{
		CFSClassArray Result;
		Result.Reserve(this->GetSize()+Array.GetSize());
		Result+=*this;
		Result+=Array;
		return Result;
	}

	CFSClassArray &operator +=(const CFSClassArray &Array)
	{
		CFSObjArray<ITEM>::operator +=(Array);
		return *this;
	}

	INTPTR Find(const ITEM &Item, INTPTR ipIndex=0) const
	{
		if (ipIndex<0) {
			ipIndex=0;
		}
		for (INTPTR ip=ipIndex; ip<this->GetSize(); ip++){
			if (*this->m_pItems[ip]==Item) {
				return ip;
			}
		}
		return -1;
	}

};

typedef CFSArray<char> CFSCharArray;
typedef CFSArray<UCHAR> CFSUCharArray;
typedef CFSArray<short> CFSShortArray;
typedef CFSArray<USHORT> CFSUShortArray;
typedef CFSArray<int> CFSIntArray;
typedef CFSArray<UINT> CFSUIntArray;
typedef CFSArray<long> CFSLongArray;
typedef CFSArray<ULONG> CFSULongArray;
typedef CFSArray<float> CFSFloatArray;
typedef CFSArray<double> CFSDoubleArray;
typedef CFSArray<INTPTR> CFSIntPtrArray;
typedef CFSArray<UINTPTR> CFSUIntPtrArray;

typedef CFSArray<INT8> CFSInt8Array;
typedef CFSArray<UINT8> CFSUInt8Array;
typedef CFSArray<INT16> CFSInt16Array;
typedef CFSArray<UINT16> CFSUInt16Array;
typedef CFSArray<INT32> CFSInt32Array;
typedef CFSArray<UINT32> CFSUInt32Array;
typedef CFSArray<INT64> CFSInt64Array;
typedef CFSArray<UINT64> CFSUInt64Array;

#define __FSQUEPAGESIZE ((INTPTR)(4096/sizeof(ITEM)>0 ? 4096/sizeof(ITEM) : 1))

/**
* Element sequence for FIFO and FILO structures.\n
* Element access: Direct\n
* Begin-Add: Element reference blocks are sometimes copied\n
* Mid-Add: Elements are copied\n
* End-Add: Element reference blocks are sometimes copied\n
* Begin-Remove: Nothing\n
* Mid-Remove: Elements are copied\n
* End-Remove: Nothing\n
* Memory overhead:\n
* Growing: up to 8kB (not depending on element size)\n
* Maximum: unlimited\n
* Compacted: up to 8kB (not depending on element size)
*/
template <class ITEM>
class CFSQue{
public:
	CFSQue(){
		m_ipFirst=0;
		m_ipSize=0;
		AddPages();
	}
	CFSQue(const CFSQue &Que)
	{
		m_ipFirst=0;
		m_ipSize=0;
		AddPages();
		operator =(Que);
	}
#if defined (__FSCXX0X)
	CFSQue(CFSQue &&Que)
	{
		m_ipFirst=Que.m_ipFirst;
		Que.m_ipFirst=0;
		m_ipSize=Que.m_ipSize;
		Que.m_ipSize=0;
		m_Array=FSMove(Que.m_Array);
		Que.AddPages();
	}
#endif
	virtual ~CFSQue()
	{
		Cleanup();
	}

/**
* Removes all elements and reinitializes the class.
*/
	void Cleanup()
	{
		while (m_ipSize) {
			RemoveLastItem();
		}
		for (INTPTR ip=0; ip<m_Array.GetSize(); ip++) {
			UnPreparePage(ip);
		}
		if (m_Array.GetSize()>1) {
			m_Array.Cleanup();
			AddPages();
		}
		m_ipFirst=0;
		m_ipSize=0;
	}

/**
* Compacts que and releases all unused resources.
*/
	void FreeExtra()
	{
		if (!m_ipSize) {
			Cleanup();
		}
		else{
			INTPTR ipFirstPage, ipFirstElem;
			CalculatePos(m_ipFirst, &ipFirstPage, &ipFirstElem);
			INTPTR ipLastPage, ipLastElem;
			CalculatePos(m_ipFirst+m_ipSize, &ipLastPage, &ipLastElem);
			if (ipFirstPage<=ipLastPage){
				for (INTPTR ip=ipLastPage+1; ip<m_Array.GetSize(); ip++) {
					UnPreparePage(ip);
				}
				m_Array.RemoveItem(ipLastPage+1, m_Array.GetSize()-ipLastPage-1);
				for (INTPTR ip=0; ip<ipFirstPage; ip++) {
					UnPreparePage(ip);
				}
				m_Array.RemoveItem(0, ipFirstPage);
				m_ipFirst=ipFirstElem;
			}
			else{
				for (INTPTR ip=ipLastPage+1; ip<ipFirstPage; ip++) {
					UnPreparePage(ip);
				}
				m_Array.RemoveItem(ipLastPage+1, ipFirstPage-ipLastPage-1);
				m_ipFirst-=(ipFirstPage-ipLastPage-1)*__FSQUEPAGESIZE;
			}
		}
	}

/**
* Returns size of the que.
* @return Number of elements in que.
*/
	INTPTR GetSize() const
	{
		return m_ipSize;
	}

/**
* Returns element of que.
* @param[in] ipIndex Index of element to receive.
* @return Element at requested index.
*/
	const ITEM &GetItem(INTPTR ipIndex) const
	{
		return operator[](ipIndex);
	}

/**
* Returns first element of que.
* @return First element of que.
*/
	const ITEM &GetFirstItem() const
	{
		return GetItem(0);
	}

/**
* Returns last element of que.
* @return Last element of que.
*/
	const ITEM &GetLastItem() const
	{
		return GetItem(GetSize()-1);
	}

/**
* Adds new element as first in que.
* @param[in] Item Element to add.
* @sa AddLastItem
*/
	void AddFirstItem(const ITEM &Item)
	{
		INTPTR ipNewPage, ipNewElem;
		if (!m_ipSize){
			CalculatePos(m_ipFirst, &ipNewPage, &ipNewElem);
		}
		else{
			INTPTR ipLastPage, ipLastElem;
			CalculatePos(m_ipFirst+m_ipSize-1, &ipLastPage, &ipLastElem);
			CalculatePos(m_ipFirst-1, &ipNewPage, &ipNewElem);
			if (ipNewPage==ipLastPage && ipNewElem>=ipLastElem){
				AddPages();
				CalculatePos(m_ipFirst-1, &ipNewPage, &ipNewElem);
			}
		}
		PreparePage(ipNewPage);
		CFSBlockAlloc<ITEM>::AssignCopy(&m_Array[ipNewPage][ipNewElem], &Item, 1);
		m_ipSize++;
		m_ipFirst=ipNewPage*__FSQUEPAGESIZE+ipNewElem;
	}

/**
* Adds new element as last in que.
* @param[in] Item Element to add.
* @sa AddFirstItem
*/
	void AddLastItem(const ITEM &Item)
	{
		INTPTR ipFirstPage, ipFirstElem;
		INTPTR ipNewPage, ipNewElem;
		CalculatePos(m_ipFirst, &ipFirstPage, &ipFirstElem);
		if (!m_ipSize){
			ipNewPage=ipFirstPage; ipNewElem=ipFirstElem;
		}
		else{
			CalculatePos(m_ipFirst+m_ipSize, &ipNewPage, &ipNewElem);
			if (ipNewPage==ipFirstPage && ipNewElem<=ipFirstElem){
				AddPages();
				CalculatePos(m_ipFirst+m_ipSize, &ipNewPage, &ipNewElem);
			}
		}
		PreparePage(ipNewPage);
		CFSBlockAlloc<ITEM>::AssignCopy(&m_Array[ipNewPage][ipNewElem], &Item, 1);
		m_ipSize++;
	}

/**
* Inserts new element into que.
* @param[in] ipIndex Index to add element to. ipIndex must be >=0 and <=GetSize().
* @param[in] Item Element to add.
* @sa AddFirstItem, AddLastItem
*/
	void InsertItem(INTPTR ipIndex, const ITEM &Item)
	{
		RT_ASSERT(m_ipSize>=0 && ipIndex<=m_ipSize);
		if (ipIndex>=m_ipSize) {
			AddLastItem(Item);
			return;
		}
		if (ipIndex<=0) {
			AddFirstItem(Item);
			return;
		}
		if (ipIndex<m_ipSize-ipIndex){
			AddFirstItem(GetFirstItem());
			for (INTPTR ip=1; ip<ipIndex; ip++) {
				(*this)[ip]=(*this)[ip+1];
			}
		}
		else{
			AddLastItem(GetLastItem());
			for (INTPTR ip=m_ipSize-2; ip>ipIndex; ip--) {
				(*this)[ip]=(*this)[ip-1];
			}
		}
		(*this)[ipIndex]=Item;
	}

/**
* Removes first element from que.
*/
	void RemoveFirstItem()
	{
		if (m_ipSize<=0) {
			return;
		}
		INTPTR ipFirstPage, ipFirstElem;
		CalculatePos(m_ipFirst, &ipFirstPage, &ipFirstElem);
		m_Array[ipFirstPage][ipFirstElem].~ITEM();
		m_ipSize--;
		if (m_ipSize){
			m_ipFirst++;
			while (m_ipFirst>=m_Array.GetSize()*__FSQUEPAGESIZE) {
				m_ipFirst-=m_Array.GetSize()*__FSQUEPAGESIZE;
			}
		}
	}

/**
* Removes last element from que.
*/
	void RemoveLastItem()
	{
		if (m_ipSize<=0) {
			return;
		}
		INTPTR ipLastPage, ipLastElem;
		CalculatePos(m_ipFirst+m_ipSize-1, &ipLastPage, &ipLastElem);
		m_Array[ipLastPage][ipLastElem].~ITEM();
		m_ipSize--;
	}

/**
* Removes element from que.
* @param[in] ipIndex Index of first element to remove.
* @param[in] ipCount Count of items to remove.
*/
	void RemoveItem(INTPTR ipIndex, INTPTR ipCount=1)
	{
		if (ipIndex>=m_ipSize) {
			return;
		}
		if (ipIndex<0) {
			ipCount+=ipIndex;
			ipIndex=0;
		}
		ipCount=FSMIN(ipCount, m_ipSize-ipIndex);
		if (ipCount<=0) {
			return;
		}

		if (ipIndex<m_ipSize-ipCount-ipIndex){
			for (INTPTR ip=ipIndex-1; ip>=0; ip--) {
				(*this)[ip+ipCount]=(*this)[ip];
			}
			for (INTPTR ip=0; ip<ipCount; ip++) {
				RemoveFirstItem();
			}
		}
		else{
			for (INTPTR ip=ipIndex; ip<m_ipSize-ipCount; ip++) {
				(*this)[ip]=(*this)[ip+ipCount];
			}
			for (INTPTR ip=0; ip<ipCount; ip++) {
				RemoveLastItem();
			}
		}
	}

/**
* Returns element of que.
* @param[in] ipIndex Index of element to receive.
* @return Element at requested index.
*/
	const ITEM &operator [](INTPTR ipIndex) const
	{
		RT_ASSERT(ipIndex>=0 && ipIndex<m_ipSize);
		INTPTR ipPage, ipElem;
		CalculatePos(m_ipFirst+ipIndex, &ipPage, &ipElem);
		return m_Array[ipPage][ipElem];
	}

/**
* Returns reference of que element.
* @param[in] ipIndex Index of element to receive.
* @return Reference of element at requested index.
*/
	ITEM &operator [](INTPTR ipIndex)
	{
		RT_ASSERT(ipIndex>=0 && ipIndex<m_ipSize);
		INTPTR ipPage, ipElem;
		CalculatePos(m_ipFirst+ipIndex, &ipPage, &ipElem);
		return m_Array[ipPage][ipElem];
	}

/*
* Copies one que to another.
* @param[in] Que Que to clone.
* @return Result of copy.
*/
	CFSQue &operator =(const CFSQue &Que)
	{
		if (this!=&Que){
			Cleanup();
			for (INTPTR ip=0; ip<Que.GetSize(); ip++) {
				AddLastItem(Que[ip]);
			}
		}
		return *this;
	}
#if defined (__FSCXX0X)
	CFSQue &operator =(CFSQue &&Que)
	{
		if (this!=&Que){
			Cleanup();
			m_ipFirst=Que.m_ipFirst;
			Que.m_ipFirst=0;
			m_ipSize=Que.m_ipSize;
			Que.m_ipSize=0;
			m_Array=FSMove(Que.m_Array);
			Que.AddPages();
		}
		return *this;
	}
#endif
/**
* Appends one que to another.
* @param[in] Que Que to append.
* @return Result of append (this).
* @sa Add
*/
	CFSQue &operator +=(const CFSQue &Que)
	{
		Add(Que);
		return *this;
	}

/**
* Appends one que to another.
* @param[in] Que Que to append.
* @sa operator +=
*/
	void Add(const CFSQue &Que)
	{
		INTPTR ipSize=Que.GetSize();
		for (INTPTR ip=0; ip<ipSize; ip++) {
			AddLastItem(Que[ip]);
		}
	}

/**
* Inserts one que into another.
* @param[in] ipIndex Index to insert que to. ipIndex must be >=0 and <=GetSize().
* @param[in] Que Que to insert.
* @sa operator +=
*/
	void Insert(INTPTR ipIndex, const CFSQue &Que)
	{
		RT_ASSERT(ipIndex>=0 && ipIndex<=m_ipSize);
		if (Que.m_ipSize<=0) {
			return;
		}
		if (this==&Que) {
			Insert(ipIndex, CFSQue(Que));
			return;
		}
		INTPTR ip;
		if (ipIndex<m_ipSize-ipIndex){
			INTPTR ipAssignOld=FSMIN(Que.m_ipSize, ipIndex);
			INTPTR ipAssignNew=Que.m_ipSize-ipAssignOld;
			INTPTR ipCopyOld=ipIndex-ipAssignOld;
			INTPTR ipCopyNew=Que.m_ipSize-ipAssignNew;
			for (ip=ipAssignNew-1; ip>=0; ip--) {
				AddFirstItem(Que[ip]);
			}
			for (ip=0; ip<ipAssignOld; ip++) {
				AddFirstItem((*this)[Que.m_ipSize-1]);
			}
			for (ip=0; ip<ipCopyOld; ip++) {
				(*this)[ipAssignOld+ip]=(*this)[ipAssignOld+ipAssignOld+ip];
			}
			for (ip=0; ip<ipCopyNew; ip++) {
				(*this)[ipIndex+ipAssignNew+ip]=Que[ipAssignNew+ip];
			}
		}
		else{
			INTPTR ipAssignOld=FSMIN(Que.m_ipSize, m_ipSize-ipIndex);
			INTPTR ipAssignNew=Que.m_ipSize-ipAssignOld;
			INTPTR ipCopyOld=m_ipSize-ipIndex-ipAssignOld;
			INTPTR ipCopyNew=Que.m_ipSize-ipAssignNew;
			for (ip=0; ip<ipAssignNew; ip++) {
				AddLastItem(Que[ipCopyNew+ip]);
			}
			for (ip=0; ip<ipAssignOld; ip++) {
				AddLastItem((*this)[ipIndex+ipCopyOld+ip]);
			}
			for (ip=ipCopyOld-1; ip>=0; ip--) {
				(*this)[ipIndex+Que.m_ipSize+ip]=(*this)[ipIndex+ip];
			}
			for (ip=0; ip<ipCopyNew; ip++) {
				(*this)[ipIndex+ip]=Que[ip];
			}
		}
	}

/**
* Finds element in que.
* @param[in] Item Find element, that matches Item.
* @param[in] ipIndex Index of element to start search from.
* @return Index of first element, that matches Item.
* @retval -1 Not found.
*/
	INTPTR Find(const ITEM &Item, INTPTR ipIndex=0) const
	{
		if (ipIndex<0) {
			ipIndex=0;
		}
		for (INTPTR ip=ipIndex; ip<m_ipSize; ip++){
			if ((*this)[ip]==Item) {
				return ip;
			}
		}
		return -1;
	}

/**
* Swaps two elements.
* @param[in] ipIndex1 Index of first element to swap.
* @param[in] ipIndex2 Index of second element to swap.
*/
	void Swap(INTPTR ipIndex1, INTPTR ipIndex2)
	{
		RT_ASSERT(ipIndex1>=0 && this-ipIndex1<m_ipSize);
		RT_ASSERT(ipIndex2>=0 && ipIndex2<m_ipSize);
		if (ipIndex1!=ipIndex2) {
			INTPTR ipPage1, ipElem1;
			CalculatePos(m_ipFirst+ipIndex1, &ipPage1, &ipElem1);
			INTPTR ipPage2, ipElem2;
			CalculatePos(m_ipFirst+ipIndex2, &ipPage2, &ipElem2);
			ITEM Item(FSMove(m_Array[ipPage1][ipElem1]));
			m_Array[ipPage1][ipElem1]=FSMove(m_Array[ipPage2][ipElem2]);
			m_Array[ipPage2][ipElem2]=FSMove(Item);
		}
	}

	friend CFSStream &operator<<(CFSStream &Stream, const CFSQue &Que)
	{
		Stream << (UINTPTR)Que.GetSize();
		for (INTPTR ip=0; ip<Que.GetSize(); ip++) {
			Stream << Que[ip];
		}
		return Stream;
	}

	friend CFSStream &operator>>(CFSStream &Stream, CFSQue &Que)
	{
		Que.Cleanup();
		INTPTR ipSize;
		Stream >> (UINTPTR &)ipSize;
		if (ipSize<0) {
			throw CFSFileException(CFSFileException::INVALIDDATA);
		}
		for (INTPTR ip=0; ip<ipSize; ip++) {
			ITEM Item;
			Que.AddLastItem(ITEM());
			Stream >> Que[Que.GetSize()-1];
		}
		return Stream;
	}

protected:
	void PreparePage(INTPTR ipIndex)
	{
		if (!m_Array[ipIndex]) {
			m_Array[ipIndex]=CFSBlockAlloc<ITEM>::Alloc(__FSQUEPAGESIZE);
		}
	}
	void UnPreparePage(INTPTR ipIndex)
	{
		if (m_Array[ipIndex]) {
			CFSBlockAlloc<ITEM>::Free(m_Array[ipIndex]);
			m_Array[ipIndex]=0;
		}
	}
	void AddPages()
	{
		if (!m_Array.GetSize()) {
			m_Array.AddItem(0);
			return;
		}
		INTPTR ipPage, ipFirstPage;
		CalculatePos(m_ipFirst, &ipPage, &ipFirstPage);
		ipFirstPage=ipPage;
		if (ipPage==0) {
			ipPage=m_Array.GetSize();
		}
		INTPTR ipNewPages=m_Array.GetSize()*5/10+1;
		CFSArray<ITEM *> ArrayTemp(ipNewPages);
		for (INTPTR ip=0; ip<ipNewPages; ip++) {
			ArrayTemp.AddItem(0);
		}
		m_Array.Insert(ipPage, ArrayTemp);
		if (ipFirstPage>=ipPage) {
			m_ipFirst+=__FSQUEPAGESIZE*ipNewPages;
		}
	}
	void CalculatePos(INTPTR ipIndex, INTPTR *pipPage, INTPTR *pipElem) const
	{
		while (ipIndex<0) {
			ipIndex+=m_Array.GetSize()*__FSQUEPAGESIZE;
		}
		*pipPage=ipIndex/__FSQUEPAGESIZE;
		*pipElem=ipIndex%__FSQUEPAGESIZE;
		while (*pipPage>=m_Array.GetSize()) {
			*pipPage-=m_Array.GetSize();
		}
	}

	CFSArray<ITEM *> m_Array;
	INTPTR m_ipFirst;
	INTPTR m_ipSize;
};

/**
* Fast lookup and simple store of key data.\n
* Element access: Logarithmical\n
* Add: Element references are copied\n
* Remove: Element references are copied\n
* Elements must implement operator <
*/
template <class ITEM>
class CFSSet{
public:
	CFSSet() { }
	CFSSet(const CFSSet &Set) : m_Items(Set.m_Items) { }
#if defined (__FSCXX0X)
	CFSSet(CFSSet &&Set) : m_Items(FSMove(Set.m_Items)) { }
#endif
	virtual ~CFSSet() { }

/**
* Removes all elements and reinitializes the class.
*/
	void Cleanup()
	{
		m_Items.Cleanup();
	}

/**
* Compacts set and releases all unused resources.
*/
	void FreeExtra() 
	{
		m_Items.FreeExtra();
	}

/**
* Returns size of the set.
* @return Number of elements in set.
*/
	INTPTR GetSize() const
	{
		return m_Items.GetSize();
	}

/**
* Reserves buffer for set. Only expands buffer, never shrinks.
* @param[in] ipSize New size of reserverd buffer.
*/
	void Reserve(INTPTR ipSize)
	{
		m_Items.Reserve(ipSize);
	}

/**
* Returns element in its logical position.
* @param[in] ipIndex Index of logical position.
* @return Element at requested index.
*/
	const ITEM &GetItem(INTPTR ipIndex) const
	{
		return *m_Items[ipIndex];
	}

/**
* Adds new element into set. If element already exist, set is not modified.
* @param[in] Item Element to add.
*/
	void AddItem(const ITEM &Item)
	{
		INTPTR ipInsert=0;
		INTPTR ipPos=GetPos(Item, &ipInsert);
		if (ipPos==-1) {
			m_Items.InsertItem(ipInsert, new ITEM(Item));
		}
	}

/**
* Removes element from set.
* @param[in] Item Element to remove.
*/
	int RemoveItem(const ITEM &Item)
	{
		INTPTR ipPos=GetPos(Item);
		if (ipPos==-1) {
			return -1;
		}
		m_Items.RemoveItem(ipPos);
		return 0;
	}

	CFSSet &operator =(const CFSSet &Set)
	{
		m_Items=Set.m_Items;
		return *this;
	}

#if defined (__FSCXX0X)
	CFSSet &operator =(CFSSet &&Set)
	{
		m_Items=FSMove(Set.m_Items);
		return *this;
	}
#endif

/**
* Compares two sets.
* @param[in] Set Set to compare to.
* @retval True Sets are identical.
* @retval False Otherwize.
*/
	bool operator ==(const CFSSet &Set) const
	{
		if (GetSize()!=Set.GetSize()) {
			return false;
		}
		for (INTPTR ip=0; ip<GetSize(); ip++) {
			if (GetItem(ip)<Set.GetItem(ip) || Set.GetItem(ip)<GetItem(ip)) { // we don't have ==
				return false;
			}
		}
		return true;
	}

/**
* Compares two sets.
* @param[in] Set Set to compare to.
* @retval True Sets are unidentical.
* @retval False Otherwize.
*/
	bool operator !=(const CFSSet &Set) const
	{
		return (!operator ==(Set));
	}

/**
* Compares two sets.
* @param[in] Set Set to compare to.
* @retval True Current set is a subset of another.
* @retval False Otherwize.
*/
	bool operator <=(const CFSSet &Set) const
	{
		INTPTR ip2=0;
		for (INTPTR ip=0; ip<GetSize(); ip++, ip2++) {
			for (;; ip2++) {
				if (GetSize()-ip>Set.GetSize()-ip2) {
					return false;
				}
				if (!(Set.GetItem(ip2) < GetItem(ip))) { // this.item <= Set.item
					break;
				}
			}
			if (GetItem(ip)<Set.GetItem(ip2)) return false;
		}
		return true;
	}

/**
* Checks whether set contains element.
* @param[in] Item Element to check.
* @retval True Set contains element.
* @retval False Otherwize.
* @sa Exist
*/
	bool operator [](const ITEM &Item) const
	{
		return Exist(Item);
	}

/**
* Adds another sets to this.
* @param[in] Set Set to add.
* @return Set of elements that are present in this or in another set (OR).
* @sa Add, operator +=
*/
	CFSSet &operator |=(const CFSSet &Set)
	{
		Add(Set);
		return *this;
	}

/**
* Adds another sets to this.
* @param[in] Set Set to add.
* @return Set of elements that are present in this or in another set (OR).
* @sa Add, operator |=
*/
	CFSSet &operator +=(const CFSSet &Set)
	{
		Add(Set);
		return *this;
	}

/**
* Multiplies another sets against this.
* @param[in] Set Set to multiply.
* @return Set of elements that are present in this and in another set (AND).
*/
	CFSSet &operator &=(const CFSSet &Set)
	{
		if (this==&Set) {
			return *this;
		}
		if (Set.GetSize()==0) {
			Cleanup();
			return *this;
		}

		INTPTR ipSrc1=0;
		INTPTR ipSrc2=0;
		INTPTR ipDest=0;
		while (ipSrc1<m_Items.GetSize()) {
			if (ipSrc2>=Set.GetSize()) {
				break;
			}
			if (*m_Items[ipSrc1]<*Set.m_Items[ipSrc2]) {
				delete m_Items[ipSrc1];
				m_Items[ipSrc1]=0;
				ipSrc1++;
			}
			else if (*Set.m_Items[ipSrc2]<*m_Items[ipSrc1]) {
				ipSrc2++;
			}
			else {
				m_Items[ipDest]=m_Items[ipSrc1];
				ipSrc1++;
				ipSrc2++;
				ipDest++;
			}

		}

		for (INTPTR ip=ipDest; ip<ipSrc1; ip++) {
			m_Items[ip]=0;
		}
		m_Items.SetSize(ipDest);

		return *this;
	}

/**
* Subtracts another sets from this.
* @param[in] Set Set to subtract.
* @return Set of elements that are present in this and not present is in another set.
*/
	CFSSet &operator -=(const CFSSet &Set)
	{
		if (this==&Set) {
			Cleanup();
			return *this;
		}
		if (Set.GetSize()==0) {
			return *this;
		}

		INTPTR ipSrc1=0;
		INTPTR ipSrc2=0;
		INTPTR ipDest=0;
		while (ipSrc1<m_Items.GetSize()) {
			if (ipSrc2>=Set.GetSize()) {
				break;
			}
			if (*m_Items[ipSrc1]<*Set.m_Items[ipSrc2]) {
				m_Items[ipDest++]=m_Items[ipSrc1++];
			}
			else if (*Set.m_Items[ipSrc2]<*m_Items[ipSrc1]) {
				ipSrc2++;
			}
			else {
				delete m_Items[ipSrc1];
				m_Items[ipSrc1]=0;
				ipSrc1++;
			}

		}

		while (ipSrc1<m_Items.GetSize()) {
			m_Items[ipDest++]=m_Items[ipSrc1++];
		}

		for (ipSrc1=ipDest; ipSrc1<m_Items.GetSize(); ipSrc1++) {
			m_Items[ipSrc1]=0;
		}
		m_Items.SetSize(ipDest);

		return *this;
	}

/**
* Calculates symmetrical difference of two sets.
* @param[in] Set Set to subtract.
* @return Set of elements that are present in this or in another set but not in both (XOR).
*/
	CFSSet &operator ^=(const CFSSet &Set)
	{
		if (this==&Set) {
			Cleanup();
			return *this;
		}
		if (Set.GetSize()==0) {
			return *this;
		}

		CFSSet Temp=Set;
		Temp-=*this;
		*this-=Set;
		*this+=Temp;

		return *this;
	}

/**
* Adds another sets to this.
* @param[in] Set Set to add.
* @return The sum of two sets.
* @sa operator |=, operator +=
*/
	void Add(const CFSSet &Set)
	{
		if (this==&Set || Set.GetSize()==0) return;

		INTPTR ipSrc1=GetSize()-1;
		INTPTR ipSrc2=Set.GetSize()-1;
		INTPTR ipDest=0;
		for (;;) {
			if (ipSrc1<0) {
				ipDest+=ipSrc2+1;
				break;
			}
			else if (ipSrc2<0) {
				ipDest+=ipSrc1+1;
				break;

			}
			else if (*m_Items[ipSrc1]<*Set.m_Items[ipSrc2]) {
				ipSrc2--;
				ipDest++;
			}
			else if (*Set.m_Items[ipSrc2]<*m_Items[ipSrc1]) {
				ipSrc1--;
				ipDest++;
			}
			else {
				ipSrc1--;
				ipSrc2--;
				ipDest++;
			}
		}

		ipSrc1=GetSize()-1;
		ipSrc2=Set.GetSize()-1;
		m_Items.SetSize(ipDest);
		ipDest--;
		for (;;) {
			if (ipSrc1<0) {
				if (ipSrc2<0) {
					break;
				}
				m_Items[ipDest]=new ITEM(*Set.m_Items[ipSrc2]);
				ipSrc2--;
				ipDest--;
			}
			else if (ipSrc2<0) {
				break;
			}
			else if (*m_Items[ipSrc1]<*Set.m_Items[ipSrc2]) {
				m_Items[ipDest]=new ITEM(*Set.m_Items[ipSrc2]);
				ipSrc2--;
				ipDest--;
			}
			else if (*Set.m_Items[ipSrc2]<*m_Items[ipSrc1]) {
				m_Items[ipDest]=m_Items[ipSrc1];
				ipSrc1--;
				ipDest--;
			}
			else {
				m_Items[ipDest]=m_Items[ipSrc1];
				ipSrc1--;
				ipSrc2--;
				ipDest--;
			}
		}
		ASSERT(ipDest==ipSrc1);
	}

/**
* Checks whether set contains element.
* @param[in] Item Element to check.
* @retval True Set contains element.
* @retval False Otherwize.
* @sa operator []
*/
	bool Exist(const ITEM &Item) const
	{
		return (GetPos(Item)!=-1);
	}

	friend CFSStream &operator<<(CFSStream &Stream, const CFSSet &Set)
	{
		return Stream << Set.m_Items;
	}

	friend CFSStream &operator>>(CFSStream &Stream, CFSSet &Set)
	{
		Stream >> Set.m_Items;
#if defined (_DEBUG)
		for (INTPTR ip=1; ip<Set.m_Items.GetSize(); ip++) {
			ASSERT(*Set.m_Items[ip-1]<*Set.m_Items[ip]);
		}
#endif
		return Stream;
	}

protected:
	INTPTR GetPos(const ITEM &Item, INTPTR *pCreatePos=0) const
	{
		INTPTR ipStart=0;
		INTPTR ipEnd=GetSize();
		for (;;) {
			if (ipStart>=ipEnd-1) {
				if (ipStart==ipEnd-1) {
					if (Item<*m_Items[ipStart]) {
						if (pCreatePos) *pCreatePos=ipStart;
						return -1;
					} else if (*m_Items[ipStart]<Item) {
						if (pCreatePos) *pCreatePos=ipStart+1;
						return -1;
					} else {
						return ipStart;
					}
				} else {
					if (pCreatePos) *pCreatePos=ipStart;
					return -1;
				}
			}

			INTPTR ipMiddle=(ipStart+ipEnd)/2;
			if (Item<*m_Items[ipMiddle]) {
				ipEnd=ipMiddle;
			} else {
				ipStart=ipMiddle;
			}
		}
	}

	CFSObjArray<ITEM> m_Items;
};

/**
* Compact class for bit operation and manipulation.\n
* Typical usage: Bitset.Set(1045); if (Bitset[1045]) { }
*/
class CFSBitSet
{
public:
	CFSBitSet() { m_ipSize=0; }

	INTPTR GetSize() const { return m_ipSize; }
	void Reserve(INTPTR ipSize);
	void SetSize(INTPTR ipSize, bool bReserveMore=true);
	INTPTR GetSetCount(bool bBit=true) const;

	bool operator [](INTPTR ipIndex) const;
	void Set(INTPTR ipIndex, bool bBit=true);

	bool operator ==(const CFSBitSet &BitSet) const;
	bool operator !=(const CFSBitSet &BitSet) const { return (!operator ==(BitSet)); }

	CFSBitSet &operator |=(const CFSBitSet &BitSet);
	CFSBitSet &operator &=(const CFSBitSet &BitSet);

	friend CFSStream &operator<<(CFSStream &Stream, const CFSBitSet &BitSet);
	friend CFSStream &operator>>(CFSStream &Stream, CFSBitSet &BitSet);

protected:
	INTPTR m_ipSize;
	CFSArray<UINT32> m_Array;
};

/**
* Fast lookup and simple store for data pairs.\n
* Typical usage: Population["Tartu"]=100000;
*/
template <class KEY, class VALUE> class CFSMap
{
public:
	class CFSMapItem
	{
	public:
		CFSMapItem() { }
		CFSMapItem(const KEY &Key0) : Key(Key0) { }
		CFSMapItem(const KEY &Key0, const VALUE &Value0) : Key(Key0), Value(Value0) { }

		friend CFSStream &operator<<(CFSStream &Stream, const CFSMapItem &Item) {
			return Stream << Item.Key << Item.Value;
		}

		friend CFSStream &operator>>(CFSStream &Stream, CFSMapItem &Item) {
			return Stream >> Item.Key >> Item.Value;
		}

		KEY Key;
		VALUE Value;
	};

	CFSMap() { }
	CFSMap(const CFSMap &Map) : m_Items(Map.m_Items) { }
#if defined (__FSCXX0X)
	CFSMap(CFSMap &&Map) : m_Items(FSMove(Map.m_Items)) { }
#endif
	virtual ~CFSMap() { }

/**
* Remove all items from map and reinitializes class.
*/
	void Cleanup()
	{
		m_Items.Cleanup();
	}

/**
* Compacts map and releases all unused resources.
*/
	void FreeExtra()
	{
		m_Items.FreeExtra();
	}

/**
* Receives a number of data pairs in the map.
* @return Number of elements in map.
*/
	INTPTR GetSize() const
	{
		return m_Items.GetSize();
	}

/**
* Reserves buffer for map. Only expands buffer, never shrinks.
* @param[in] ipSize New size of reserverd buffer.
*/
	void Reserve(INTPTR ipSize)
	{
		m_Items.Reserve(ipSize);
	}

/**
* Returns key-data pair in its logical position.
* @param[in] ipIndex Index of logical position.
* @return key-data pair.
*/
	const CFSMapItem &GetItem(INTPTR ipIndex) const
	{
		return *m_Items[ipIndex];
	}

	CFSMap &operator =(const CFSMap &Map) {
		m_Items=Map.m_Items;
		return *this;
	}

#if defined (__FSCXX0X)
	CFSMap &operator =(CFSMap &&Map) {
		m_Items=FSMove(Map.m_Items);
		return *this;
	}
#endif
/**
* Returns reference to value of data pair identified by Key.
* @param[in] Key Key to search for.
* @return Reference to value of data pair. If data pair does not exist, exception is thrown.
*/
	const VALUE &operator[](const KEY &Key) const
	{
		return m_Items[GetPos(Key)]->Value;
	}

/**
* Returns reference to value of data pair identified by Key.
* @param[in] Key Key to search for.
* @return Reference to value of data pair. If data pair does not exist, it is created.
*/
	VALUE &operator[](const KEY &Key)
	{
		INTPTR ipInsert=0;
		INTPTR ipPos=GetPos(Key, &ipInsert);
		if (ipPos!=-1) {
			return m_Items[ipPos]->Value;
		}
		else{
			m_Items.InsertItem(ipInsert, new CFSMapItem(Key));
			return m_Items[ipInsert]->Value;
		}
	}

/**
* Removes data pair from map.
* @param[in] Key Key that identifies data pair.
* @retval 0 Remove successful.
* @retval !=0 Otherwise.
*/
	int RemoveItem(const KEY &Key)
	{
		INTPTR ipPos=GetPos(Key);
		if (ipPos==-1) {
			return -1;
		}
		m_Items.RemoveItem(ipPos);
		return 0;
	}

/**
* Checks whether key exists in the map.
* @param[in] Key Key to search for.
* @param[out] pValue Optional paramter to receive Value field of the data pair.
* @retval true Key-data pair exists.
* @retval false Otherwise.
*/
	bool Exist(const KEY &Key, VALUE *pValue=0) const
	{
		INTPTR ip=GetPos(Key);
		if (ip==-1) {
			return false;
		}
		if (pValue) {
			*pValue=m_Items[ip]->Value;
		}
		return true;
	}

	friend CFSStream &operator<<(CFSStream &Stream, const CFSMap &Map)
	{
		return Stream << Map.m_Items;
	}

	friend CFSStream &operator>>(CFSStream &Stream, CFSMap &Map)
	{
		Stream >> Map.m_Items;
#if defined (_DEBUG)
		for (INTPTR ip=1; ip<Map.m_Items.GetSize(); ip++) {
			ASSERT(Map.m_Items[ip-1]->Key<Map.m_Items[ip]->Key);
		}
#endif
		return Stream;
	}

protected:
	INTPTR GetPos(const KEY &Key, INTPTR *pCreatePos=0) const
	{
		INTPTR ipStart=0;
		INTPTR ipEnd=GetSize();
		for (;;) {
			if (ipStart>=ipEnd-1) {
				if (ipStart==ipEnd-1) {
					if (Key<m_Items[ipStart]->Key) {
						if (pCreatePos) *pCreatePos=ipStart;
						return -1;
					} else if (m_Items[ipStart]->Key<Key) {
						if (pCreatePos) *pCreatePos=ipStart+1;
						return -1;
					} else {
						return ipStart;
					}
				} else {
					if (pCreatePos) *pCreatePos=ipStart;
					return -1;
				}
			}

			INTPTR ipMiddle=(ipStart+ipEnd)/2;
			if (Key<m_Items[ipMiddle]->Key) {
				ipEnd=ipMiddle;
			} else {
				ipStart=ipMiddle;
			}
		}
	}

	CFSObjArray<CFSMapItem> m_Items;
};

/**
* Base virtual sort class that implements different sort algorithms.
*/
class CFSSorter
{
public:
/**
* Sorts array with minimal exchanges.
* Average: O(n^2); Worst: O(n^2); Compare: (n^2)/2; Exchange: n; Memory: -; Stable: No
* @param[in] ipStart First element of array to sort. Typically = 0
* @param[in] ipEnd Last element of array to sort. Typically = ArraySize-1
*/
	void SelectionSort(INTPTR ipStart, INTPTR ipEnd);

/**
* Sorts array using Gnome sort algorithm. Keeps the order of equal elements.
* Average: O(n^2); Worst: O(n^2); Compare: (n^2)/4; Exchange: (n^2)/4; Memory: -; Stable: Yes
* @param[in] ipStart First element of array to sort. Typically = 0
* @param[in] ipEnd Last element of array to sort. Typically = ArraySize-1
*/
	void GnomeSort(INTPTR ipStart, INTPTR ipEnd);

/**
* Sorts array using Quick Sort algorithm and in worst case falls back to Heap Sort. Overall best, first choice.
* Average: O(n log n); Worst: O(n log n); Memory: -; Stable: No
* @param[in] ipStart First element of array to sort. Typically = 0
* @param[in] ipEnd Last element of array to sort. Typically = ArraySize-1
*/
	void IntroSort(INTPTR ipStart, INTPTR ipEnd);

/**
* Sorts array using heap sort algorithm. O(n log n) even in worst case, but in average slower of Quick Sort.
* Average: O(n log n); Worst: O(n log n); Memory: -; Stable: No
* @param[in] ipStart First element of array to sort. Typically = 0
* @param[in] ipEnd Last element of array to sort. Typically = ArraySize-1
*/
	void HeapSort(INTPTR ipStart, INTPTR ipEnd);

protected:
	void IntroSort(INTPTR ipStart, INTPTR ipEnd, int iLevel);
	void HeapBuild(INTPTR ipStart, INTPTR ipEnd);
	void HeapDown(INTPTR ipStart, INTPTR ipEnd, INTPTR ipIndex);

	virtual bool IsLessThan(INTPTR ipIndex1, INTPTR ipIndex2) = 0;
	virtual void Swap(INTPTR ipIndex1, INTPTR ipIndex2) = 0;
};

/**
* Class to sort CFSArray, CFSClassArray, CFSQue in ascending order.
*/
template <class ARRAY>
class CFSArraySorter : public CFSSorter
{
public:
/**
* @param[in] pArray Array to be sorted.
*/
	CFSArraySorter(ARRAY *pArray)
	{
		m_pArray=pArray;
	}

protected:
	virtual bool IsLessThan(INTPTR ipIndex1, INTPTR ipIndex2)
	{
		return (*m_pArray)[ipIndex1]<(*m_pArray)[ipIndex2];
	}
	virtual void Swap(INTPTR ipIndex1, INTPTR ipIndex2)
	{
		m_pArray->Swap(ipIndex1, ipIndex2);
	}

	ARRAY *m_pArray;
};

/**
* CFSChain adds chain functionality to any class.\n
* Typical usage: class CMyClass : public CFSChain<CMyClass> { }\n
* CMyClass *pClass=0;\n
* pClass=pClass->Append(new CMyClass);
*/
template <class ITEM> class CFSChain
{
public:
	DECLARE_FSNOCOPY(CFSChain);

	CFSChain()
	{
		m_pNext=0;
	}

/**
* On deletion, all following objects are deleted as well.
*/
	virtual ~CFSChain()
	{
		if (m_pNext){
			ITEM *pChain2;
			for (ITEM *pChain=m_pNext; pChain; ) {
				pChain2=pChain->m_pNext;
				pChain->m_pNext=0;
				delete pChain;
				pChain=pChain2;
			}
		}
	}

/**
* Reverses chain.
* @return New first element of chain.
*/
	ITEM *Reverse()
	{
		ITEM *pLast=0, *pChain2;
		for (ITEM *pChain=(ITEM *)this; pChain; ) {
			pChain2=pChain->m_pNext;
			pChain->m_pNext=pLast;
			pLast=pChain;
			pChain=pChain2;
		}
		return pLast;
	}

/**
* Appends new object or chain to existing one. this may be NULL!
* @param[in] pChain2 Element or chain to append.
* @return New first element of chain.
*/
	ITEM *Append(ITEM *pChain2)
	{
		if (!this) {
			return pChain2;
		}
		if (!pChain2) {
			return (ITEM *)this;
		}
		for (ITEM *pChain=(ITEM *)this; pChain; pChain=pChain->m_pNext){
			if (!pChain->m_pNext){
				pChain->m_pNext=pChain2;
				return (ITEM *)this;
			}
		}
		return 0;
	}

/**
* Reference to next object in chain.
*/
	ITEM *m_pNext;
};

#endif // _FSLIST_H_
