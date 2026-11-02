# دليل المستودع

**النسخة المعتمدة في `main`.** يحتوي الفرع المصدر والنماذج اللازمة للتشغيل والنشر.
التنزيلات الجاهزة في [GitHub Releases](https://github.com/abdulazizalhwaiml-dot/Disease-prediction-model/releases/latest).
الفروع القديمة محفوظة للرجوع إليها، ولا تحتاجها لتشغيل النسخة الحالية.

| المطلوب | الدليل |
|---|---|
| تشغيل Windows | [WINDOWS.md](WINDOWS.md) |
| استضافة مجانية أو رخيصة | [STREAMLIT_CLOUD_AR.md](STREAMLIT_CLOUD_AR.md) |
| Docker وإعادة التدريب | [DEPLOYMENT.md](DEPLOYMENT.md) |
| التطوير وفحص الواجهة | [DEVELOPMENT.md](DEVELOPMENT.md) |
| تعريف البيانات والأمراض | [DATA_DICTIONARY.md](DATA_DICTIONARY.md) |
| المنهجية والقيود | [METHODOLOGY.md](METHODOLOGY.md) |
| الاختبارات المنفذة | [VALIDATION.md](../reports/VALIDATION.md) |
| نتائج النماذج الحالية | [MODEL_CARD.md](../reports/MODEL_CARD.md) |

`app/` للواجهة، و`src/nhanes_ai/` للبيانات والنماذج، و`scripts/` لأوامر التشغيل والتجهيز.
تبقى ملفات NHANES الأصلية وتقارير التدريب منفصلة عن الواجهة للحفاظ على إمكانية التحقق من النتائج.
