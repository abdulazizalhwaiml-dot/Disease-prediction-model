# استضافة ميزان من GitHub على Streamlit Community Cloud

GitHub يحفظ المصدر والملفات، وStreamlit Cloud يشغّل Python والتطبيق ويمنحك رابطًا للموقع.
GitHub Pages مخصص للمواقع الثابتة، ولا يشغّل تطبيق Streamlit الحالي.

## ما جُهّز في فرع النشر

- المستودع: `abdulazizalhwaiml-dot/Disease-prediction-model`.
- الفرع: `deploy/streamlit-cloud`.
- نقطة الدخول: `streamlit_app.py`، وتضبط استيراد الحزمة المحلية في `src/`.
- نسخة نماذج موثوقة كاملة: `models/current.json` وثمانية ملفات joblib وmanifest.
- `requirements.txt` يثبت إصدارات حزم Python المستخدمة في النماذج.
- `packages.txt` يثبت `libgomp1` اللازم لـLightGBM على Linux.
- لا يلزم تدريب عند بدء كل جلسة أو مفتاح لخدمة ذكاء اصطناعي.

## الخطوة المتبقية في حسابك

1. افتح https://share.streamlit.io وسجّل الدخول بحساب GitHub صاحب المستودع.
2. اسمح لـStreamlit بالوصول إلى هذا المستودع الخاص؛ راجع الصلاحيات في شاشة GitHub.
3. اضغط **Create app** ثم اختر النشر من GitHub.
4. أدخل القيم التالية:

| الإعداد | القيمة |
|---|---|
| Repository | `abdulazizalhwaiml-dot/Disease-prediction-model` |
| Branch | `deploy/streamlit-cloud` |
| Main file path | `streamlit_app.py` |
| Python version — Advanced settings | **3.12** |

5. اختر اسم الرابط المتاح، ثم اضغط **Deploy**.
6. بعد نجاح النشر، افتح الرابط، واختر نعم/لا للسؤالين العائليين، ثم اختبر التقديرات والتفسير.
7. راجع إعدادات المشاركة؛ خصوصية المستودع وخصوصية التطبيق إعدادان مختلفان.

لا تستخدم الفرع `downloads/mizan-v2` للنشر؛ فهو يحتوي حزمة ZIP للتنزيل، وليس ملفات
التطبيق المفكوكة. فرع النشر مستقل عن `main` وفرع المصدر السابق.

## التحقق وحل المشكلات

- **إصدار Python غير متطابق:** اختر 3.12 عند إنشاء التطبيق؛ لا تتجاوز تحقق النموذج بتغيير manifest.
- **المستودع لا يظهر:** أكمل منح وصول Streamlit إلى المستودع الخاص من إعدادات الحساب/GitHub.
- **لا توجد نماذج صالحة:** تأكد من اختيار فرع النشر ومن وجود `models/current.json` والمجلد المشار إليه.
- **خطأ libgomp:** تأكد أن `packages.txt` في جذر المستودع يحتوي `libgomp1`.
- **خطأ تثبيت حزمة:** راجع سجل البناء. لا ترقِّ الحزم عشوائيًا؛ النماذج تتحقق من إصداراتها.

الاختبارات المحلية وملفات النشر لا تعني أن موقعًا نُشر فعليًا. ربط حساب Streamlit
بالمستودع ومنحه الصلاحية يحتاج إكماله في حسابك؛ لا توجد أداة نشر Streamlit مرتبطة بهذه المحادثة.

الموقع يظل مشروعًا تجريبيًا غير معتمد طبيًا؛ نموذج BIA والسكان المحليين يحتاج تحققًا خارجيًا.

المراجع: [خطوات النشر الرسمية](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)،
[اعتماديات التطبيق](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies)،
[تعريف GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages).
