# تشغيل ميزان على Windows

## الطريقة الأسهل

1. ثبّت [Python3.12، نسخة64-bit](https://www.python.org/downloads/)، مع Python Launcher.
2. فك ضغط المشروع وافتح المجلد الذي يحتوي README.md وSTART_WINDOWS.bat.
3. انقر START_WINDOWS.bat مرتين وانتظر انتهاء التثبيت.
4. عندما يظهر رابط التشغيل افتح **http://localhost:8501**.

النسخة الجاهزة تتضمن النماذج الجديدة. إذا لم يجدها المشغّل أو كانت غير متوافقة، سينزّل
البيانات القديمة ويتحقق منها، ثم يعيد التدريب. قد يستغرق التثبيت الأول عدة دقائق؛ لا تغلق النافذة.
لا يحتاج التشغيل بطاقة رسومية أو مفتاح API. لا حاجة لتغيير سياسة PowerShell.

## التشغيل اليدوي

من شريط عنوان مجلد المشروع اكتب powershell واضغط Enter.
نفّذ **أمرًا واحدًا كل مرة**، وانتظر عودة السطر الذي يبدأ بـPS قبل تنفيذ التالي:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --require-hashes -r requirements-windows.lock
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

إذا أردت إعادة التدريب، نفذ قبل أمر التشغيل:

```powershell
.\.venv\Scripts\python.exe scripts/download_data.py
.\.venv\Scripts\python.exe -m nhanes_ai.train --jobs 2
.\.venv\Scripts\python.exe scripts/export_dataset.py
```

## المرات التالية

انقر START_WINDOWS.bat، أو شغّل آخر أمر فقط. أبق النافذة مفتوحة؛ Ctrl+C يوقف التطبيق.

## أخطاء شائعة

- requirements-windows.lock غير موجود: افتح PowerShell من مجلد المشروع الصحيح.
- py غير معروف: ثبّت Python3.12 مع Python Launcher وأعد فتح النافذة.
- DLL/WinError126 عند LightGBM: ثبّت [Microsoft Visual C++ x64](https://aka.ms/vs/17/release/vc_redist.x64.exe).
- ملفات قديمة ناقصة عند التدريب: أكمل scripts/download_data.py واتصال الإنترنت.
- نماذج غير متوافقة: أعد التدريب بالإصدارات المقفلة؛ لا تعدّل manifest أو بصمات الملفات.

العمر المدعوم **20–79** لغير الحوامل. المشروع تجريبي، وليس تشخيصًا أو دليلًا على السلامة.
المشغّل أعدّ لWindows، لكن اختبار Windows فعليًا غير متاح داخل بيئة Linux هذه.
