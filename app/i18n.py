"""Short bilingual copy and definitions for the eight-input app."""

DISEASE_AR = {
    "high_cholesterol": "ارتفاع الكوليسترول",
    "high_blood_pressure": "ارتفاع ضغط الدم",
    "diabetes": "السكري",
    "coronary_artery_disease": "مرض الشرايين التاجية",
    "heart_attack": "النوبة القلبية",
    "angina": "الذبحة الصدرية",
    "heart_failure": "قصور القلب الاحتقاني",
    "stroke": "السكتة الدماغية",
}

TEXT = {
    "ar": {
        "brand": "ميزان",
        "tagline": "قياساتك، بمنظور أوضح",
        "research": "مشروع تجريبي · غير معتمد طبيًا",
        "eyebrow": "تركيب الجسم × التعلّم الآلي",
        "title": "قياسات بسيطة. رؤية أوضح.",
        "subtitle": "استكشف تقديرات ثماني حالات صحية من قياسات جسمك وتاريخ عائلتك.",
        "scope": "لغير الحوامل من عمر 20 إلى 79 سنة",
        "notice": "هذه تجربة بحثية، وليست تشخيصًا أو توقعًا للإصابة مستقبلًا. لم تُعتمد النماذج "
        "للاستخدام الطبي.",
        "assessment": "مساحة التقييم",
        "guide": "دليل القياسات",
        "input_count": "٨ مدخلات فقط",
        "derived_count": "٣ حسابات تلقائية",
        "disease_count": "٨ حالات صحية",
        "form_title": "لنبدأ ببياناتك",
        "form_note": "اضغط اسم أي خانة أو مرّر المؤشر فوقها لقراءة التوضيح.",
        "measurements": "01 / قياسات الجسم",
        "family": "02 / تاريخ العائلة",
        "age": "العمر (سنة)",
        "gender": "الجنس",
        "height_cm": "الطول (سم)",
        "weight_kg": "الوزن (كغ)",
        "waist_cm": "محيط الخصر (سم)",
        "body_fat_pct": "نسبة دهون الجسم (%)",
        "family_diabetes": "التاريخ العائلي للسكري",
        "family_heart_early": "التاريخ العائلي القلبي المبكر",
        "male": "ذكر",
        "female": "أنثى",
        "yes": "نعم",
        "no": "لا",
        "family_required": "اختر نعم أو لا للسؤالين العائليين للمتابعة. لا تعتبر عدم المعرفة إجابة "
        "«لا».",
        "family_diabetes_error": "اختر إجابة صحيحة للتاريخ العائلي للسكري.",
        "family_heart_early_error": "اختر إجابة صحيحة للتاريخ العائلي القلبي المبكر.",
        "bmi": "مؤشر كتلة الجسم",
        "fat_mass_kg": "كتلة الدهون",
        "fat_free_mass_kg": "الكتلة الخالية من الدهون",
        "automatic": "تُحسب لك تلقائيًا",
        "kg": "كغ",
        "submit": "اعرض تقديراتي",
        "running": "جارٍ حساب التقديرات…",
        "invalid": "راجع القيم ووحداتها؛ العمر المدعوم 20–79 سنة.",
        "results": "ملفك الاستكشافي",
        "results_subtitle": "تقديرات وجود حالات الدراسة، وليست مخاطر مستقبلية.",
        "empty": "ستظهر تقديراتك هنا",
        "empty_note": "أكمل قياساتك وتاريخ عائلتك، ثم اضغط «اعرض تقديراتي».",
        "waiting": "بانتظار التقييم",
        "probability": "الاحتمال المقدّر",
        "above": "تجاوز عتبة الدراسة",
        "below": "دون عتبة الدراسة",
        "threshold": "عتبة الدراسة",
        "legend": "الألوان بحسب عتبة كل نموذج: تركوازي دونها، كهرماني قربها، ومرجاني عند تجاوزها. "
        "ليست تصنيفًا طبيًا.",
        "outside_training": "بعض القياسات خارج نطاق التدريب المشاهد: ",
        "download": "تنزيل نتائج الجلسة",
        "no_models": "لم تُجهّز نماذج المدخلات الثمانية بعد. شغّل أمر التدريب أدناه.",
        "guide_title": "قياس صحيح، إدخال أوضح",
        "guide_note": "التعاريف العائلية تطابق أسئلة NHANES المستخدمة في التدريب، بما فيها حد 50 "
        "سنة للقلب لدى كلا الجنسين.",
        "formulas": "الحسابات التلقائية",
        "formula_note": "الكتلة الخالية من الدهون تشمل الماء والعضلات والأعضاء والمعادن؛ ليست كتلة "
        "العضلات وحدها.",
        "privacy": "مدخلاتك تبقى في ذاكرة الجلسة؛ لا تُحفظ في قاعدة بيانات ولا تُرسل إلى خدمة ذكاء "
        "اصطناعي خارجية.",
        "footer": "ميزان · بيانات NHANES · مشروع بحثي تجريبي",
        "help": {
            "age": "العمر بالسنوات المكتملة، من 20 إلى 79 سنة. أضيفت دورات NHANES القديمة "
            "لتغطية الأعمار 60–79. التطبيق تجريبي وغير مخصص للحوامل أو لمن هم خارج هذا "
            "النطاق.",
            "gender": "الجنس المسجل في بيانات الدراسة: ذكر أو أنثى. يُستخدم لأن توزيع تركيب "
            "الجسم والارتباطات الصحية قد يختلف بينهما.",
            "height_cm": "الطول بالسنتيمتر. قف حافيًا مستقيمًا، والكعبان على الأرض، وانظر "
            "للأمام. أدخل 175 مثلًا، وليس 1.75.",
            "weight_kg": "وزن الجسم بالكيلوغرام. استخدم ميزانًا على سطح صلب ومستوي، دون أحذية "
            "وبملابس خفيفة، ويفضل القياس في ظروف متقاربة كل مرة.",
            "waist_cm": "محيط الخصر بالسنتيمتر. وفق طريقة NHANES: مرّر شريطًا أفقيًا حول "
            "البطن عند مستوى أعلى العظم الحرقفي الأيمن، بعد زفير طبيعي، دون ضغط "
            "الجلد. ليس مقاس البنطال ولا القياس عند السرة بالضرورة.",
            "body_fat_pct": "نسبة الدهون من وزن الجسم، مثل 25 وليس 0.25. انسخ Body Fat % من "
            "تقرير جهازك واتبع تعليماته للقياس. نسبة الدهون في بيانات التدريب "
            "مقاسة بـDXA؛ الأداء على جهازك غير متحقق منه.",
            "family_diabetes": "هل سبق أن أخبر مختص صحي أحد أقاربك البيولوجيين: الأب أو الأم "
            "أو الإخوة أو الأخوات، الأحياء أو المتوفين، بأنه مصاب بالسكري؟ "
            "لا يوجد شرط عمر لهذا السؤال. لا يشمل الزوج أو الزوجة، ولا "
            "يقصد إصابتك أنت.",
            "family_heart_early": "هل سبق أن أخبر مختص صحي الأب أو الأم أو أحد الإخوة أو "
            "الأخوات البيولوجيين، الأحياء أو المتوفين، بإصابته بنوبة "
            "قلبية أو ذبحة صدرية قبل بلوغ 50 سنة؟ هذا تعريف NHANES "
            "المستخدم هنا، ولا يشمل كل أمراض القلب أو السكتة أو ضغط "
            "الدم.",
        },
        "attention_title": "خطوة صحية تبدأ اليوم",
        "attention_message": "تجاوز أحد التقديرات عتبة النموذج. احرص على النشاط البدني المنتظم "
        "والغذاء المتوازن، واستشر مختصًا لتحديد الفحوصات المناسبة. هذه "
        "النتيجة ليست تشخيصًا.",
        "maintain_title": "واصل عاداتك الصحية",
        "maintain_message": "لم تتجاوز التقديرات عتبات النماذج. واصل النشاط البدني والغذاء "
        "المتوازن والفحوصات الدورية؛ انخفاض التقدير لا يؤكد الخلو من المرض.",
        "older_note": "تستند بيانات الأعمار 60–79 إلى دورات 1999–2006؛ لم يُتحقق من الأداء على "
        "عينة حديثة لهذه الفئة.",
    },
    "en": {
        "brand": "MIZAN",
        "tagline": "A clearer view of your measurements",
        "research": "EXPERIMENTAL · NOT MEDICALLY VALIDATED",
        "eyebrow": "BODY COMPOSITION × MACHINE LEARNING",
        "title": "Simple measurements. Clearer perspective.",
        "subtitle": "Explore estimates for eight study conditions using your measurements and "
        "family history.",
        "scope": "Non-pregnant adults aged 20–79",
        "notice": "A research experiment, not a diagnosis or a forecast of future disease. These "
        "models are not validated for medical use.",
        "assessment": "Your assessment",
        "guide": "Measurement guide",
        "input_count": "8 simple inputs",
        "derived_count": "3 automatic calculations",
        "disease_count": "8 study conditions",
        "form_title": "Start with your measurements",
        "form_note": "Click any field name or hover over it for a definition and measuring "
        "instructions.",
        "measurements": "01 / BODY MEASUREMENTS",
        "family": "02 / FAMILY HISTORY",
        "age": "Age (years)",
        "gender": "Sex",
        "height_cm": "Height (cm)",
        "weight_kg": "Weight (kg)",
        "waist_cm": "Waist circumference (cm)",
        "body_fat_pct": "Body fat (%)",
        "family_diabetes": "Family history of diabetes",
        "family_heart_early": "Early family cardiac history",
        "male": "Male",
        "female": "Female",
        "yes": "Yes",
        "no": "No",
        "family_required": "Answer both family-history questions to continue. An unknown history "
        "should not be entered as No.",
        "family_diabetes_error": "Choose a valid diabetes family-history answer.",
        "family_heart_early_error": "Choose a valid early cardiac family-history answer.",
        "bmi": "Body mass index",
        "fat_mass_kg": "Fat mass",
        "fat_free_mass_kg": "Fat-free mass",
        "automatic": "Calculated automatically",
        "kg": "kg",
        "submit": "Explore my estimates",
        "running": "Calculating estimates…",
        "invalid": "Check measurements and units. Supported ages: 20–79.",
        "results": "Your research profile",
        "results_subtitle": "Estimates of existing study labels, not future disease risks.",
        "empty": "Your estimates will appear here",
        "empty_note": "Complete your measurements and family history, then select Explore my "
        "estimates.",
        "waiting": "Awaiting assessment",
        "probability": "Estimated probability",
        "above": "Above study threshold",
        "below": "Below study threshold",
        "threshold": "Study threshold",
        "legend": "Colors follow each model threshold: teal below, amber nearby, coral above. "
        "These are not clinical categories.",
        "outside_training": "Some measurements are outside the observed training range: ",
        "download": "Download session results",
        "no_models": "The eight-input models are not ready. Run the training command below.",
        "guide_title": "Better measurements, clearer inputs",
        "guide_note": "Family definitions match the source NHANES questions, including its "
        "under-50 cardiac definition for either sex.",
        "formulas": "Automatic calculations",
        "formula_note": "Fat-free mass includes water, muscle, organs and minerals. It is not "
        "muscle mass alone.",
        "privacy": "Inputs stay in session memory. They are not stored in a database or sent to an "
        "external AI service.",
        "footer": "MIZAN · NHANES data · Experimental research",
        "help": {
            "age": "Completed years, from 20 to 79. Older NHANES cycles supply ages 60–79. "
            "Experimental use only; not intended for pregnancy or ages outside this "
            "range.",
            "gender": "Recorded sex in the source survey: male or female. Body-composition "
            "distributions and health associations may differ by sex.",
            "height_cm": "Standing height in centimeters. Stand barefoot and upright with "
            "heels down and eyes forward. Enter 175 rather than 1.75.",
            "weight_kg": "Weight in kilograms. Place the scale on a hard, level surface; "
            "remove shoes and use light clothing. Measure under similar "
            "conditions over time.",
            "waist_cm": "NHANES method: a horizontal tape around the abdomen at the upper "
            "border of the right iliac bone, after a normal exhalation, without "
            "compressing skin. Not trouser size or necessarily navel level.",
            "body_fat_pct": "Body fat as a percentage of weight: enter 25, not 0.25. Copy "
            "Body Fat % from your device and follow its measuring "
            "instructions. Training uses DXA; performance on your device is "
            "unvalidated.",
            "family_diabetes": "Has a health professional ever told a biological father, "
            "mother, sister or brother, living or deceased, that they had "
            "diabetes? No age restriction applies. This excludes a spouse "
            "and does not ask about your own diagnosis.",
            "family_heart_early": "Has a health professional ever told a biological father, "
            "mother, sister or brother, living or deceased, that they "
            "had a heart attack or angina before age 50? This is the "
            "NHANES definition, not all cardiac disease, stroke or high "
            "blood pressure.",
        },
        "attention_title": "A healthy step starts today",
        "attention_message": "At least one estimate exceeded its model threshold. Keep physically "
        "active, eat a balanced diet, and consult a health professional about "
        "appropriate checks. This result is not a diagnosis.",
        "maintain_title": "Keep your healthy habits",
        "maintain_message": "No estimate exceeded its model threshold. Keep physically active, eat "
        "a balanced diet, and continue routine health checks. A lower estimate "
        "does not confirm absence of disease.",
        "older_note": "Ages 60–79 are supported by 1999–2006 data only; performance has not been "
        "validated in a contemporary older-adult sample.",
    },
}
