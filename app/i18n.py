"""Bilingual Mizanak copy and measurement definitions."""

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
        "brand": "ميزانك",
        "tagline": "قياساتك، ببساطة",
        "research": "مشروع تجريبي · غير معتمد طبيًا",
        "eyebrow": "مساحة صغيرة للاهتمام بنفسك",
        "title": "خطوة بسيطة. اهتمام أكبر.",
        "subtitle": "أدخل قياساتك، واستكشف تقريرًا خفيفًا يساعدك على الاهتمام بعاداتك الصحية.",
        "scope": "لغير الحوامل من عمر 20 إلى 79 سنة",
        "notice": "هذه تجربة بحثية، وليست تشخيصًا أو توقعًا للإصابة مستقبلًا. لم تُعتمد النماذج "
        "للاستخدام الطبي.",
        "form_title": "لنبدأ بقياساتك",
        "form_note": "ثمانية مدخلات فقط. زر «توضيح» بجانب كل خانة يساعدك في القياس.",
        "family": "وماذا عن تاريخ العائلة؟",
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
        "automatic": "قيم حسبناها لك تلقائيًا",
        "kg": "كغ",
        "submit": "اعرض تقريري",
        "running": "جارٍ حساب التقديرات…",
        "invalid": "راجع القيم ووحداتها؛ العمر المدعوم 20–79 سنة.",
        "results": "تقريرك",
        "results_subtitle": "اضغط أي بطاقة للتعرّف على الحالة. هذه تقديرات بحثية وليست تشخيصًا.",
        "empty": "تقريرك يبدأ من قياساتك",
        "empty_note": "أكمل المدخلات بالأعلى، ثم اضغط «اعرض تقريري».",
        "above": "إشارة أعلى من عتبة النموذج",
        "below": "إشارة أقل من عتبة النموذج",
        "legend": "لون البطاقة يتبع عتبة النموذج البحثية؛ لا يعني تشخيصًا أو تأكيدًا للسلامة.",
        "outside_training": "بعض القياسات خارج نطاق التدريب المشاهد: ",
        "download": "احفظ تقريري",
        "no_models": "لم تُجهّز نماذج المدخلات الثمانية بعد. شغّل أمر التدريب أدناه.",
        "formula_note": "الكتلة الخالية من الدهون تشمل الماء والعضلات والأعضاء والمعادن؛ ليست كتلة "
        "العضلات وحدها.",
        "privacy": "مدخلاتك تبقى في ذاكرة الجلسة؛ لا تُحفظ في قاعدة بيانات ولا تُرسل إلى خدمة ذكاء "
        "اصطناعي خارجية.",
        "footer": "ميزانك · مشروع بحثي تجريبي",
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
        "help_button": "توضيح",
        "near": "قريب من عتبة النموذج",
        "image_alt": {
            "height_cm": "شخص حافي القدمين يقف مستقيمًا أمام مقياس الطول، والرأس ينظر للأمام.",
            "waist_cm": "شريط أفقي عند مستوى أعلى عظم الحوض الأيمن، مع رسم يوضح موضع "
            "العظم والزفير الطبيعي.",
        },
        "image_note": {
            "height_cm": "حافيًا، بوضع مستقيم، مع النظر للأمام. استخدم أداة أفقية فوق الرأس.",
            "waist_cm": "النقطة في الرسم تحدد أعلى عظم الحوض الأيمن؛ الشريط أفقي دون "
            "ضغط الجلد، بعد زفير طبيعي.",
        },
        "conditions": {
            "high_cholesterol": "ارتفاع الكوليسترول وفق الإبلاغ السابق أو نتيجة non-HDL "
            "في الدراسة. لا يمكن تأكيده من قياسات الجسم وحدها.",
            "high_blood_pressure": "ارتفاع ضغط الدم وفق الإبلاغ السابق أو قراءات الفحص. "
            "قياس الضغط الفعلي ضروري للتقييم.",
            "diabetes": "السكري وفق الإبلاغ السابق أو تحليل HbA1c في الدراسة. هذا "
            "التقدير لا يغني عن التحليل.",
            "coronary_artery_disease": "مرض الشرايين التي تغذي القلب، وفق تشخيص سابق "
            "أبلغ عنه المشاركون في الدراسة.",
            "heart_attack": "نوبة قلبية سابقة أبلغ عنها المشارك؛ ليس توقعًا لموعد نوبة "
            "قلبية مستقبلية.",
            "angina": "ذبحة صدرية سابقة أبلغ عنها المشارك في الدراسة، وليست تقييمًا لألم صدر حالي.",
            "heart_failure": "قصور القلب الاحتقاني وفق تشخيص سابق أبلغ عنه المشارك في الدراسة.",
            "stroke": "سكتة دماغية سابقة أبلغ عنها المشارك؛ ليس توقعًا لحدوث سكتة مستقبلًا.",
        },
    },
    "en": {
        "brand": "Mizanak",
        "tagline": "Your measurements, made simple",
        "research": "EXPERIMENTAL · NOT MEDICALLY VALIDATED",
        "eyebrow": "A little space to care for yourself",
        "title": "A small step. A little more care.",
        "subtitle": "Enter your measurements and explore a simple report to support healthier "
        "habits.",
        "scope": "Non-pregnant adults aged 20–79",
        "notice": "A research experiment, not a diagnosis or a forecast of future disease. These "
        "models are not validated for medical use.",
        "form_title": "Start with your measurements",
        "form_note": "Just eight inputs. Select Help beside any field for measuring guidance.",
        "family": "A little about your family",
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
        "automatic": "Calculated for you automatically",
        "kg": "kg",
        "submit": "Show my report",
        "running": "Calculating estimates…",
        "invalid": "Check measurements and units. Supported ages: 20–79.",
        "results": "Your report",
        "results_subtitle": "Tap a card to learn about the condition. Research estimates, not a "
        "diagnosis.",
        "empty": "Your report starts with your measurements",
        "empty_note": "Complete the inputs above, then select Show my report.",
        "above": "Above the model threshold",
        "below": "Below the model threshold",
        "legend": "Card colors follow research model thresholds; they do not establish a diagnosis "
        "or medical safety.",
        "outside_training": "Some measurements are outside the observed training range: ",
        "download": "Save my report",
        "no_models": "The eight-input models are not ready. Run the training command below.",
        "formula_note": "Fat-free mass includes water, muscle, organs and minerals. It is not "
        "muscle mass alone.",
        "privacy": "Inputs stay in session memory. They are not stored in a database or sent to an "
        "external AI service.",
        "footer": "Mizanak · Experimental research",
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
        "help_button": "Help",
        "near": "Near the model threshold",
        "image_alt": {
            "height_cm": "A barefoot person stands straight at a stadiometer, looking "
            "horizontally ahead.",
            "waist_cm": "Horizontal tape at the upper border of the right iliac crest, "
            "with a pelvic landmark inset and normal exhalation.",
        },
        "image_note": {
            "height_cm": "Stand barefoot and upright, looking forward. Use a level "
            "headpiece touching the crown.",
            "waist_cm": "The dot marks the top of the right iliac crest. Keep the tape "
            "level, without compressing skin, after a normal exhalation.",
        },
        "conditions": {
            "high_cholesterol": "The study combines a reported cholesterol diagnosis "
            "with non-HDL laboratory results. Body measurements "
            "alone cannot confirm it.",
            "high_blood_pressure": "The study combines reported hypertension with "
            "examination readings. Actual blood-pressure "
            "measurements are needed for assessment.",
            "diabetes": "The study combines reported diabetes with HbA1c results. This "
            "estimate cannot replace laboratory testing.",
            "coronary_artery_disease": "Disease affecting the arteries supplying the "
            "heart, based on a prior diagnosis reported by "
            "study participants.",
            "heart_attack": "A previously reported heart attack, not a forecast of when "
            "a future heart attack might occur.",
            "angina": "Previously reported angina in the survey; this does not assess "
            "current chest pain.",
            "heart_failure": "Congestive heart failure based on a prior diagnosis "
            "reported by study participants.",
            "stroke": "A previously reported stroke, not a forecast of a future stroke.",
        },
    },
}
