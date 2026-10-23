# تشغيل المشروع على Windows

## 1. تحميل الملفات وتثبيت Python

- ثبّت **Python 3.12 بنسخة 64-bit** من [الموقع الرسمي](https://www.python.org/downloads/).
  تأكد من تثبيت Python Launcher الذي يوفر الأمر `py`.
- افتح فرع المشروع الذي يحتوي على التطبيق في GitHub، ثم اختر **Code → Download ZIP**.
- فك ضغط الملف. افتح مجلد المشروع الذي يحتوي على `README.md` و`pyproject.toml` و`DATA_SET`.
  لا تفتح مجلد `app` وحده.
- انقر شريط عنوان المجلد في مستكشف الملفات، اكتب `powershell` ثم اضغط Enter.

## 2. التثبيت والتدريب للمرة الأولى

انسخ الأوامر التالية بالترتيب إلى PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --require-hashes -r requirements-windows.lock
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
.\.venv\Scripts\python.exe -m nhanes_ai.train --jobs 2
.\.venv\Scripts\python.exe -m streamlit run app/main.py
```

انتظر اكتمال كل أمر قبل تنفيذ التالي. التدريب يقارن أربع خوارزميات لكل واحد من الأمراض
الثمانية، ثم يحفظ النماذج داخل `models`. ملفات النماذج المولّدة لا تدخل ضمن تنزيل GitHub
العادي؛ لذلك يلزم تنفيذ التدريب عند تشغيل نسخة المصدر للمرة الأولى.

هذه الطريقة تستخدم Python الخاص بالبيئة مباشرة، فلا تحتاج تشغيل `Activate.ps1` أو تغيير
سياسة تنفيذ PowerShell. لا تحتاج مفتاح API أو بطاقة رسومية.

## 3. فتح الواجهة

بعد ظهور رسالة تشغيل Streamlit، افتح المتصفح واكتب `localhost:8501`.
اختر **العربية** من القائمة الجانبية. أبقِ نافذة PowerShell مفتوحة طوال استخدام التطبيق.

## التشغيل في المرات التالية

افتح PowerShell داخل المجلد نفسه وشغّل فقط:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app/main.py
```

لإيقاف التطبيق، اضغط `Ctrl+C` داخل PowerShell. لا تحتاج إعادة التدريب إلا بعد تغيير
البيانات أو تعريف الحالات أو كود النموذج أو تحديث الاعتماديات المستخدمة في النماذج.

## إذا ظهر خطأ

- **`py` غير معروف:** أعد تثبيت Python 3.12 مع Python Launcher، ثم أعد فتح PowerShell.
  تحقق بالأمر `py -3.12 --version`.
- **لم يُعثر على `requirements-windows.lock`:** افتح PowerShell داخل مجلد المشروع الصحيح،
  أو تأكد أنك حمّلت الفرع الذي يحتوي على التطبيق وليس النسخة القديمة من `main`.
- **لا توجد نماذج:** أكمل أمر التدريب؛ لا تنشئ ملفات `joblib` فارغة ولا تعدّل checksums.
- **`WinError 126` أو DLL مفقود عند تحميل LightGBM:** ثبّت حزمة
  [Microsoft Visual C++ Redistributable x64 الرسمية](https://aka.ms/vs/17/release/vc_redist.x64.exe)،
  ثم أعد فتح PowerShell والمحاولة.
- **المنفذ مشغول:** أغلق نسختك السابقة بـ`Ctrl+C` أو أضف `--server.port 8502` إلى أمر
  Streamlit، ثم افتح `localhost:8502`.

تم التحقق من توفر حزم Python 3.12 ووحداتها الجاهزة لـWindows x64 وحُفظ قفل مستقل لها.
الاختبارات الفعلية للتطبيق والحاوية أُجريت على Linux؛ لم يُنفّذ المشروع على جهاز Windows
داخل جلسة التطوير هذه.

النظام بحثي للفئة العمرية 20–59، وليس أداة تشخيص معتمدة. بعض أهداف القلب أظهرت أداءً
ضعيفاً في الاختبار المستقل؛ التفاصيل في `reports/MODEL_CARD.md`.
