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
#if !defined _FSJNI_H_
#define _FSJNI_H_

#include "fsc.h"
#include <jni.h>

class CFSJNIException : public CFSException { };

CFSAString FSJNIStrtoA(JNIEnv *jEnv, jstring jString);
CFSWString FSJNIStrtoW(JNIEnv *jEnv, jstring jString);
jstring FSJNIAtoStr(JNIEnv *jEnv, const CFSAString &szStr);
jstring FSJNIWtoStr(JNIEnv *jEnv, const CFSWString &szStr);

void FSJNIGetField(JNIEnv *jEnv, jobject jObj, const char *pszName, const char *pszSignature, void *pResult);
jboolean FSJNIGetBooleanField(JNIEnv *jEnv, jobject jObj, const char *pszName);
jbyte FSJNIGetByteField(JNIEnv *jEnv, jobject jObj, const char *pszName);
jchar FSJNIGetCharField(JNIEnv *jEnv, jobject jObj, const char *pszName);
jshort FSJNIGetShortField(JNIEnv *jEnv, jobject jObj, const char *pszName);
jint FSJNIGetIntField(JNIEnv *jEnv, jobject jObj, const char *pszName);
jlong FSJNIGetLongField(JNIEnv *jEnv, jobject jObj, const char *pszName);
jfloat FSJNIGetFloatField(JNIEnv *jEnv, jobject jObj, const char *pszName);
jdouble FSJNIGetDoubleField(JNIEnv *jEnv, jobject jObj, const char *pszName);
jstring FSJNIGetStringField(JNIEnv *jEnv, jobject jObj, const char *pszName);
jobject FSJNIGetObjectField(JNIEnv *jEnv, jobject jObj, const char *pszName, const char *pszSignature);

void FSJNISetField(JNIEnv *jEnv, jobject jObj, const char *pszName, const char *pszSignature, ...);
void FSJNISetBooleanField(JNIEnv *jEnv, jobject jObj, const char *pszName, jboolean jVal);
void FSJNISetByteField(JNIEnv *jEnv, jobject jObj, const char *pszName, jbyte jVal);
void FSJNISetCharField(JNIEnv *jEnv, jobject jObj, const char *pszName, jchar jVal);
void FSJNISetShortField(JNIEnv *jEnv, jobject jObj, const char *pszName, jshort jVal);
void FSJNISetIntField(JNIEnv *jEnv, jobject jObj, const char *pszName, jint jVal);
void FSJNISetLongField(JNIEnv *jEnv, jobject jObj, const char *pszName, jlong jVal);
void FSJNISetFloatField(JNIEnv *jEnv, jobject jObj, const char *pszName, jfloat jVal);
void FSJNISetDoubleField(JNIEnv *jEnv, jobject jObj, const char *pszName, jdouble jVal);
void FSJNISetStringField(JNIEnv *jEnv, jobject jObj, const char *pszName, jstring jVal);
void FSJNISetObjectField(JNIEnv *jEnv, jobject jObj, const char *pszName, const char *pszSignature, jobject jVal);

void FSJNICallMethod(JNIEnv *jEnv, jobject jObj, const char *pszName, const char *pszSignature, void *pResult, ...);
void FSJNICallVoidMethod(JNIEnv *jEnv, jobject jObj, const char *pszName, const char *pszSignature, ...);
jboolean FSJNICallBooleanMethod(JNIEnv *jEnv, jobject jObj, const char *pszName, const char *pszSignature, ...);
jbyte FSJNICallByteMethod(JNIEnv *jEnv, jobject jObj, const char *pszName, const char *pszSignature, ...);
jchar FSJNICallCharMethod(JNIEnv *jEnv, jobject jObj, const char *pszName, const char *pszSignature, ...);
jshort FSJNICallShortMethod(JNIEnv *jEnv, jobject jObj, const char *pszName, const char *pszSignature, ...);
jint FSJNICallIntMethod(JNIEnv *jEnv, jobject jObj, const char *pszName, const char *pszSignature, ...);
jlong FSJNICallLongMethod(JNIEnv *jEnv, jobject jObj, const char *pszName, const char *pszSignature, ...);
jfloat FSJNICallFloatMethod(JNIEnv *jEnv, jobject jObj, const char *pszName, const char *pszSignature, ...);
jdouble FSJNICallDoubleMethod(JNIEnv *jEnv, jobject jObj, const char *pszName, const char *pszSignature, ...);
jobject FSJNICallObjectMethod(JNIEnv *jEnv, jobject jObj, const char *pszName, const char *pszSignature, ...);
jstring FSJNICallStringMethod(JNIEnv *jEnv, jobject jObj, const char *pszName, const char *pszSignature, ...);

#endif // _FSJNI_H_