# استضافة ميزانك من GitHub على Streamlit Community Cloud

GitHub يحفظ المصدر والملفات، وStreamlit Cloud يشغّل Python والتطبيق ويمنحك رابطًا للموقع.
GitHub Pages مخصص للمواقع الثابتة، ولا يشغّل تطبيق Streamlit الحالي.

## ما جُهّز في الفرع الرئيسي

- المستودع: `abdulazizalhwaiml-dot/Disease-prediction-model`.
- الفرع المعتمد: `main`، ويحتوي التطبيق والنماذج الحالية.
- نقطة الدخول: `streamlit_app.py`، وتضبط استيراد الحزمة المحلية في `src/`.
- نسخة نماذج موثوقة كاملة: `models/current.json` وثمانية ملفات joblib وmanifest.
- `requirements.txt` يثبت إصدارات حزم Python المستخدمة في النماذج.
- `packages.txt` يثبت `libgomp1` اللازم لـLightGBM على Linux.
- لا يلزم تدريب عند بدء كل جلسة أو مفتاح لخدمة ذكاء اصطناعي.

## الخطوة المتبقية في حسابك

1. افتح https://share.streamlit.io وسجّل الدخول بحساب GitHub صاحب المستودع.
2. اربط حساب GitHub؛ المستودع عام حاليًا. إذا جعلته خاصًا لاحقًا فامنح Streamlit الوصول إليه.
3. اضغط **Create app** ثم اختر النشر من GitHub.
4. أدخل القيم التالية:

| الإعداد | القيمة |
|---|---|
| Repository | `abdulazizalhwaiml-dot/Disease-prediction-model` |
| Branch | `main` |
| Main file path | `streamlit_app.py` |
| Python version — Advanced settings | **3.12** |

5. اختر اسم الرابط المتاح، ثم اضغط **Deploy**.
6. بعد نجاح النشر، افتح الرابط، واختر نعم/لا للسؤالين العائليين، ثم اختبر التقديرات والرسالة الموحدة.
7. راجع إعدادات المشاركة؛ خصوصية المستودع وخصوصية التطبيق إعدادان مختلفان.

لا تستخدم فروع `downloads/*` للنشر؛ فهي تحتوي حزم ZIP وليس ملفات التطبيق المفكوكة.
استخدم `main` للتطوير والتشغيل والنشر، و[Releases](https://github.com/abdulazizalhwaiml-dot/Disease-prediction-model/releases/latest)
لتنزيل الحزمة الجاهزة. الفروع السابقة محفوظة كسجل للإصدارات القديمة.

## المجاني والرخيص

راجعت صفحات الخدمات الرسمية في **3 نوفمبر 2026**؛ الأسعار والقيود قابلة للتغيير.

| الخدمة | التكلفة | الملاءمة |
|---|---|---|
| Streamlit Community Cloud | مجاني | الخيار الأول لهذا التطبيق: يقرأ `main` مباشرة ويمنحك HTTPS ورابط `streamlit.app` |
| Render Web Service | مجاني بموارد محدودة، أو حوسبة مدفوعة من 7 دولارات شهريًا | بديل يدعم Python؛ خطة 7 دولارات بذاكرة 512MB، وقد تحتاج خطة أكبر حسب الاستهلاك |

ابدأ بـStreamlit المجاني. التطبيقات غير النشطة تدخل السكون بعد 12 ساعة، ويوقظها الزائر؛
لا تتوقع ضمان تشغيل متواصل أو موارد غير محدودة. لا يحتاج التطبيق قاعدة بيانات أو GPU أو اشتراك API.
إذا ظهرت مشكلة موارد، راجع سجل الخدمة قبل اختيار خطة مدفوعة.

لا يصلح GitHub Pages لتشغيل Python/Streamlit. كذلك لا أفترض مجانية Hugging Face Docker Spaces:
توثيقهم الحالي يشترط خطة مدفوعة لإنشاء مساحات Docker، حتى عندما تكون CPU Basic بلا رسم ساعي.

### إعداد Render عند الحاجة

أنشئ **Web Service** من المستودع والفرع `main`، واختر بيئة **Python**، ثم:

```text
Build Command: pip install -r requirements.txt
Start Command: python -m streamlit run streamlit_app.py --server.address=0.0.0.0 --server.port=$PORT
Health Check Path: /_stcore/health
Environment Variable: PYTHON_VERSION=3.12.12
```

لم أختبر نشرًا فعليًا على Render. إذا أظهر سجل البناء نقص `libgomp1`، استخدم Dockerfile المرفق
بدل بيئة Python، واضبط المنفذ `8501` في أمر بدء الحاوية. لا تفعّل قرصًا أو قاعدة بيانات مدفوعة لهذا التطبيق.

## التحقق وحل المشكلات

- **إصدار Python غير متطابق:** اختر 3.12 عند إنشاء التطبيق؛ لا تتجاوز تحقق النموذج بتغيير manifest.
- **المستودع لا يظهر:** أكمل منح وصول Streamlit إلى المستودع الخاص من إعدادات الحساب/GitHub.
- **لا توجد نماذج صالحة:** تأكد من اختيار `main` ومن وجود `models/current.json` والمجلد المشار إليه.
- **خطأ libgomp:** تأكد أن `packages.txt` في جذر المستودع يحتوي `libgomp1`.
- **خطأ تثبيت حزمة:** راجع سجل البناء. لا ترقِّ الحزم عشوائيًا؛ النماذج تتحقق من إصداراتها.

الاختبارات المحلية وملفات النشر لا تعني أن موقعًا نُشر فعليًا. ربط حساب Streamlit
بالمستودع ومنحه الصلاحية يحتاج إكماله في حسابك؛ لا توجد أداة نشر Streamlit مرتبطة بهذه المحادثة.

الموقع يظل مشروعًا تجريبيًا غير معتمد طبيًا؛ الأداء على الموازين والسكان المحليين يحتاج تحققًا خارجيًا.

المراجع: [خطوات النشر الرسمية](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)،
[اعتماديات التطبيق](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies)،
[موارد Streamlit والسكون](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app#app-resources-and-limits)،
[أسعار Render](https://render.com/pricing)،
[متطلبات Hugging Face Spaces الحالية](https://huggingface.co/docs/hub/spaces-overview)،
[تعريف GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages).
