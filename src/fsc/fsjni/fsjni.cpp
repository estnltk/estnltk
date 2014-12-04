#include "fsjni.h"

CFSAString FSJNIStrtoA(JNIEnv *jEnv, jstring jString)
{
	const char *pStr=jEnv->GetStringUTFChars(jString, NULL);
	CFSAString szStr(pStr);
	jEnv->ReleaseStringUTFChars(jString, pStr);
	return szStr;
}

CFSWString FSJNIStrtoW(JNIEnv *jEnv, jstring jString)
{
	INTPTR ipLength=jEnv->GetStringLength(jString);
	CFSWString szStr;
	WCHAR *pStr2=szStr.GetBuffer(ipLength+1);

	const jchar *pStr=jEnv->GetStringChars(jString, NULL);
	for (INTPTR ip=0; ip<ipLength; ip++) {
		pStr2[ip]=(WCHAR)pStr[ip];
	}
	jEnv->ReleaseStringChars(jString, pStr);

	szStr.ReleaseBuffer(ipLength);
	FSStrCombineW2(szStr);
	return szStr;
}

jstring FSJNIAtoStr(JNIEnv *jEnv, const CFSAString &szStr)
{
	return jEnv->NewStringUTF(szStr);
}

jstring FSJNIWtoStr(JNIEnv *jEnv, const CFSWString &szStr)
{
	if (sizeof(WCHAR)==sizeof(jchar)) {
		return jEnv->NewString((const jchar *)(const WCHAR *)szStr, szStr.GetLength());
	} else {
		CFSData Data;
		Data.SetSize(sizeof(jchar)*szStr.GetLength()*2);
		jchar *pChar=(jchar *)Data.GetData();
		INTPTR ipLength=0;
		for (INTPTR ip=0; szStr[ip]; ip++){
			if ((LCHAR)szStr[ip]>=0x10000){
#if defined FSUTF16
				throw CFSJNIException();
#endif
				WCHAR Char1, Char2;
				if (FSLtoW2(szStr[ip], &Char1, &Char2)!=0) {
					throw CFSJNIException();
				}
				pChar[ipLength++]=(jchar)Char1;
				pChar[ipLength++]=(jchar)Char2;
			}
			else {
				pChar[ipLength++]=(jchar)szStr[ip];
			}
		}
		return jEnv->NewString(pChar, ipLength);
	}
}

void FSJNIGetField(JNIEnv *jEnv, jobject jObj, const char *pszName, const char *pszSignature, void *pResult)
{
	jclass jCls=jEnv->GetObjectClass(jObj);
	if (!jCls) {
		throw CFSJNIException();
	}
	jfieldID jFid=jEnv->GetFieldID(jCls, pszName, pszSignature);
	if (!jFid) {
		throw CFSJNIException();
	}

	switch (*pszSignature) {
		case 'Z':
			*(jboolean *)pResult=jEnv->GetBooleanField(jObj, jFid);
		break;
		case 'B':
			*(jbyte *)pResult=jEnv->GetByteField(jObj, jFid);
		break;
		case 'C':
			*(jchar *)pResult=jEnv->GetCharField(jObj, jFid);
		break;
		case 'S':
			*(jshort *)pResult=jEnv->GetShortField(jObj, jFid);
		break;
		case 'I':
			*(jint *)pResult=jEnv->GetIntField(jObj, jFid);
		break;
		case 'J':
			*(jlong *)pResult=jEnv->GetLongField(jObj, jFid);
		break;
		case 'F':
			*(jfloat *)pResult=jEnv->GetFloatField(jObj, jFid);
		break;
		case 'D':
			*(jdouble *)pResult=jEnv->GetDoubleField(jObj, jFid);
		break;
		case 'L':
			*(jobject *)pResult=jEnv->GetObjectField(jObj, jFid);
		break;
		default:
			throw CFSJNIException();
	}
}

#define FSJNIGETFIELD_WRAPPER(TYPE, NAME, INAME, SIGNATURE) \
TYPE FSJNIGet##NAME##Field(JNIEnv *jEnv, jobject jObj, const char *pszName) { \
	jclass jCls=jEnv->GetObjectClass(jObj); \
	if (!jCls) throw CFSJNIException(); \
	jfieldID jFid=jEnv->GetFieldID(jCls, pszName, SIGNATURE); \
	if (!jFid) throw CFSJNIException(); \
	TYPE jRes=jEnv->Get##INAME##Field(jObj, jFid); \
	if (jEnv->ExceptionCheck()) throw CFSJNIException(); \
	return jRes; \
}

FSJNIGETFIELD_WRAPPER(jboolean, Boolean, Boolean, "Z");
FSJNIGETFIELD_WRAPPER(jbyte, Byte, Byte, "B");
FSJNIGETFIELD_WRAPPER(jchar, Char, Char, "C");
FSJNIGETFIELD_WRAPPER(jshort, Short, Short, "S");
FSJNIGETFIELD_WRAPPER(jint, Int, Int, "I");
FSJNIGETFIELD_WRAPPER(jlong, Long, Long, "J");
FSJNIGETFIELD_WRAPPER(jfloat, Float, Float, "F");
FSJNIGETFIELD_WRAPPER(jdouble, Double, Double, "D");

jobject FSJNIGetObjectField(JNIEnv *jEnv, jobject jObj, const char *pszName, const char *pszSignature) {
	jclass jCls=jEnv->GetObjectClass(jObj);
	if (!jCls) throw CFSJNIException();
	jfieldID jFid=jEnv->GetFieldID(jCls, pszName, pszSignature);
	if (!jFid) throw CFSJNIException();
	jobject jRes=jEnv->GetObjectField(jObj, jFid);
	if (jEnv->ExceptionCheck()) throw CFSJNIException();
	return jRes;
}

jstring FSJNIGetStringField(JNIEnv *jEnv, jobject jObj, const char *pszName) {
	return (jstring)FSJNIGetObjectField(jEnv, jObj, pszName, "Ljava/lang/String;");
}

void FSJNISetField(JNIEnv *jEnv, jobject jObj, const char *pszName, const char *pszSignature, ...)
{
	va_list Args;
	va_start(Args, pszSignature);

	jclass jCls=jEnv->GetObjectClass(jObj);
	if (!jCls) {
		throw CFSJNIException();
	}
	jfieldID jFid=jEnv->GetFieldID(jCls, pszName, pszSignature);
	if (!jFid) {
		throw CFSJNIException();
	}

	switch (*pszSignature) {
		case 'Z':
			jEnv->SetBooleanField(jObj, jFid, va_arg(Args, int));
		break;
		case 'B':
			jEnv->SetByteField(jObj, jFid, va_arg(Args, int));
		break;
		case 'C':
			jEnv->SetCharField(jObj, jFid, va_arg(Args, int));
		break;
		case 'S':
			jEnv->SetShortField(jObj, jFid, va_arg(Args, int));
		break;
		case 'I':
			jEnv->SetIntField(jObj, jFid, va_arg(Args, jint));
		break;
		case 'J':
			jEnv->SetLongField(jObj, jFid, va_arg(Args, jlong));
		break;
		case 'F':
			jEnv->SetFloatField(jObj, jFid, (jfloat)va_arg(Args, double));
		break;
		case 'D':
			jEnv->SetDoubleField(jObj, jFid, va_arg(Args, double));
		break;
		case 'L':
			jEnv->SetObjectField(jObj, jFid, va_arg(Args, jobject));
		break;
		default:
			throw CFSJNIException();
	}

	va_end(Args);
}

#define FSJNISETFIELD_WRAPPER(TYPE, NAME, INAME, SIGNATURE) \
void FSJNISet##NAME##Field(JNIEnv *jEnv, jobject jObj, const char *pszName, TYPE jVal) { \
	jclass jCls=jEnv->GetObjectClass(jObj); \
	if (!jCls) throw CFSJNIException(); \
	jfieldID jFid=jEnv->GetFieldID(jCls, pszName, SIGNATURE); \
	if (!jFid) throw CFSJNIException(); \
	jEnv->Set##INAME##Field(jObj, jFid, jVal); \
	if (jEnv->ExceptionCheck()) throw CFSJNIException(); \
}

FSJNISETFIELD_WRAPPER(jboolean, Boolean, Boolean, "Z");
FSJNISETFIELD_WRAPPER(jbyte, Byte, Byte, "B");
FSJNISETFIELD_WRAPPER(jchar, Char, Char, "C");
FSJNISETFIELD_WRAPPER(jshort, Short, Short, "S");
FSJNISETFIELD_WRAPPER(jint, Int, Int, "I");
FSJNISETFIELD_WRAPPER(jlong, Long, Long, "J");
FSJNISETFIELD_WRAPPER(jfloat, Float, Float, "F");
FSJNISETFIELD_WRAPPER(jdouble, Double, Double, "D");

void FSJNISetObjectField(JNIEnv *jEnv, jobject jObj, const char *pszName, const char *pszSignature, jobject jVal) {
	jclass jCls=jEnv->GetObjectClass(jObj);
	if (!jCls) throw CFSJNIException();
	jfieldID jFid=jEnv->GetFieldID(jCls, pszName, pszSignature);
	if (!jFid) throw CFSJNIException();
	jEnv->SetObjectField(jObj, jFid, jVal);
	if (jEnv->ExceptionCheck()) throw CFSJNIException();
}

void FSJNISetStringField(JNIEnv *jEnv, jobject jObj, const char *pszName, jstring jVal) {
	FSJNISetObjectField(jEnv, jObj, pszName, "Ljava/lang/String;", jVal);
}

void FSJNICallMethod(JNIEnv *jEnv, jobject jObj, const char *pszName, const char *pszSignature, void *pResult, ...)
{
	va_list Args;
	va_start(Args, pResult);

	jclass jCls=jEnv->GetObjectClass(jObj);
	if (!jCls) {
		throw CFSJNIException();
	}
	jmethodID jMid=jEnv->GetMethodID(jCls, pszName, pszSignature);
	if (!jMid) {
		throw CFSJNIException();
	}
	
	const char *pResSig=FSStrChr(pszSignature, ')');
	if (pResSig) pResSig++;

	switch(pResSig[0]) {
		case 'V':
			jEnv->CallVoidMethodV(jObj, jMid, Args);
		break;
		case 'Z': {
			jboolean jRes=jEnv->CallBooleanMethodV(jObj, jMid, Args);
			if (pResult) *(jboolean *)pResult=jRes;
		} break;
		case 'B': {
			jbyte jRes=jEnv->CallByteMethodV(jObj, jMid, Args);
			if (pResult) *(jbyte *)pResult=jRes;
		} break;
		case 'C': {
			jchar jRes=jEnv->CallCharMethodV(jObj, jMid, Args);
			if (pResult) *(jchar *)pResult=jRes;
		} break;
		case 'S': {
			jshort jRes=jEnv->CallShortMethodV(jObj, jMid, Args);
			if (pResult) *(jshort *)pResult=jRes;
		} break;
		case 'I': {
			jint jRes=jEnv->CallIntMethodV(jObj, jMid, Args);
			if (pResult) *(jint *)pResult=jRes;
		} break;
		case 'J': {
			jlong jRes=jEnv->CallLongMethodV(jObj, jMid, Args);
			if (pResult) *(jlong *)pResult=jRes;
		} break;
		case 'F': {
			jfloat jRes=jEnv->CallFloatMethodV(jObj, jMid, Args);
			if (pResult) *(jfloat *)pResult=jRes;
		} break;
		case 'D': {
			jdouble jRes=jEnv->CallDoubleMethodV(jObj, jMid, Args);
			if (pResult) *(jdouble *)pResult=jRes;
		} break;
		case 'L': {
			jobject jRes=jEnv->CallObjectMethodV(jObj, jMid, Args);
			if (pResult) *(jobject *)pResult=jRes;
		} break;
		default:
			throw CFSJNIException();
	}

	if (jEnv->ExceptionCheck()) {
		//jEnv->ExceptionClear();
		throw CFSJNIException();
	}
	va_end(Args);
}

void FSJNICallVoidMethod(JNIEnv *jEnv, jobject jObj, const char *pszName, const char *pszSignature, ...)
{
	va_list Args;
	va_start(Args, pszSignature);
	jclass jCls=jEnv->GetObjectClass(jObj);
	if (!jCls) throw CFSJNIException();
	jmethodID jMid=jEnv->GetMethodID(jCls, pszName, pszSignature);
	if (!jMid) throw CFSJNIException();
	jEnv->CallVoidMethodV(jObj, jMid, Args);
	if (jEnv->ExceptionCheck()) throw CFSJNIException();
	va_end(Args);
}

#define FSJNICALLMETHOD_WRAPPER(TYPE, NAME, INAME) \
TYPE FSJNICall##NAME##Method(JNIEnv *jEnv, jobject jObj, const char *pszName, const char *pszSignature, ...) { \
	va_list Args; \
	va_start(Args, pszSignature); \
	jclass jCls=jEnv->GetObjectClass(jObj); \
	if (!jCls) throw CFSJNIException(); \
	jmethodID jMid=jEnv->GetMethodID(jCls, pszName, pszSignature); \
	if (!jMid) throw CFSJNIException(); \
	TYPE jRes=(TYPE)jEnv->Call##INAME##MethodV(jObj, jMid, Args); \
	if (jEnv->ExceptionCheck()) throw CFSJNIException(); \
	va_end(Args); \
	return jRes; \
}

FSJNICALLMETHOD_WRAPPER(jboolean, Boolean, Boolean);
FSJNICALLMETHOD_WRAPPER(jbyte, Byte, Byte);
FSJNICALLMETHOD_WRAPPER(jchar, Char, Char);
FSJNICALLMETHOD_WRAPPER(jshort, Short, Short);
FSJNICALLMETHOD_WRAPPER(jint, Int, Int);
FSJNICALLMETHOD_WRAPPER(jlong, Long, Long);
FSJNICALLMETHOD_WRAPPER(jfloat, Float, Float);
FSJNICALLMETHOD_WRAPPER(jdouble, Double, Double);
FSJNICALLMETHOD_WRAPPER(jobject, Object, Object);
FSJNICALLMETHOD_WRAPPER(jstring, String, Object);
