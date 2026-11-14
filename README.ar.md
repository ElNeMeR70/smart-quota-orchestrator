<div dir="rtl" align="center">

<p>
  <a href="https://sqo.elnemer-ai.com"><img src="https://img.shields.io/badge/🌐_المنصة_العالمية_التفاعلية-sqo.elnemer--ai.com-EC4899?style=for-the-badge" alt="المنصة الحية" /></a>
  <a href="./README.md"><img src="https://img.shields.io/badge/🇬🇧_English_Documentation-Read_Here-2563EB?style=for-the-badge" alt="English README" /></a>
  <a href="./docs/PLAYBOOK_AR.md"><img src="https://img.shields.io/badge/📗_كتاب_السيناريوهات_والحوارات-عربي-10B981?style=for-the-badge" alt="Arabic Playbook" /></a>
  <a href="./docs/PLAYBOOK_EN.md"><img src="https://img.shields.io/badge/📘_Engineering_Playbook-English-8B5CF6?style=for-the-badge" alt="English Playbook" /></a>
</p>

<img src="./assets/hero-banner.jpg" alt="Smart Quota & Swarm Orchestrator v7.0 Hero Banner" width="100%" />

# ⚡ Smart Quota & Swarm Orchestrator (`v7.0` Global Ecosystem)
### المنظومة العالمية المتكاملة لحماية الكوتا، `20` أداة MCP أصلية، مثبت `npx` عالمي، إضافة VS Code / Cursor، مركز القيادة المحلي الحي (`sqo serve`)، وضغط السياق بنسبة 96.8%

[![المنصة الحية](https://img.shields.io/badge/Live_Playground-sqo.elnemer--ai.com-EC4899?style=for-the-badge)](https://sqo.elnemer-ai.com)
[![الإصدار](https://img.shields.io/badge/Release-v7.0.0_Global_Ecosystem-6366F1?style=for-the-badge)](https://github.com/ElNeMeR70/smart-quota-orchestrator)
[![أدوات MCP](https://img.shields.io/badge/MCP_Server-20_Native_Tools-10B981?style=for-the-badge)](./mcp_server.py)
[![التوفير الفعلي](https://img.shields.io/badge/Verified_Savings-96.8%25_Tokens-F59E0B?style=for-the-badge)](./assets/benchmark-comparison.svg)
[![بدون مكتبات خارجية](https://img.shields.io/badge/Python_3.8%2B_%7C_npx-Zero_Dependencies-38BDF8?style=for-the-badge)](./package.json)

</div>

<div dir="rtl">

---

## 🌟 لماذا يحتاج كل مبرمج في العالم إلى هذه الأداة فوراً؟

عندما تعمل مع وكلاء الذكاء الاصطناعي الحديثين (**Gemini 4 Carbon / Argon / Hydrogen**، أو **Claude Opus / Sonnet 4.6**، أو **GPT**)، فإن الكوتا الخاصة بك لا تضيع بسبب الكود الفعلي الذي تكتبه، بل تبتلعها **سبع كوارث صامتة** تحدث في كل جلسة برمجة دون أن تشعر:

1. **إعادة استكشاف المشروع من الصفر في كل محادثة جديدة** (`15,000 – 30,000` توكن ضائعة).
2. **قراءة ملفات قفل وحزم عملاقة بالخطأ** مثل `package-lock.json` أو `pubspec.lock` أو `.js.map` (`50,000 – 180,000` توكن في ضغطة واحدة!).
3. **نسيان الوكيل وإعادة قراءته لنفس الملف 3 أو 4 مرات** رغم أن الملف لم يتغير على القرص إطلاقاً!
4. **قراءة ملف كود ضخم طوله 2,000 سطر بالكامل** من أجل تعديل دالة واحدة من 15 سطراً.
5. **دخول الوكيل في حلقة مفرغة (`Retry Loop`)** بتشغيل نفس أمر الاختبار الفاشل 4 مرات متتالية بدون تعديل أي كود.
6. **إرفاق صور شاشة بدقة `4K` أو ملفات PDF كبيرة** تلتهم عشرات آلاف توكنات الرؤية (`Vision Tiles`).
7. **كسر خصم الـ `KV-Cache` (الذي يوفر 90% من سعر التوكنز)** بسبب إضافة توقيت متغير في القواعد النظامية.

تتدخل منظومة **Smart Quota & Swarm Orchestrator `v5.0`** كـ **طبقة نظام تشغيل ذاتية التنفيذ (`Autonomous Agent OS`)** تعمل تلقائياً في أقل من **`15ms`** بدون الحاجة لتثبيت أي مكتبة خارجية (`Zero pip install`)!

---

## 🖼️ البنية المعمارية الكاملة للإصدار الخامس (`v5.0`)

<p align="center">
  <img src="./assets/architecture-v5.svg" alt="مخطط البنية المعمارية لمنظومة Smart Quota v5.0" width="100%" />
</p>

---

## 📊 نتائج القياس الفعلي الموثقة (`96.6%` توفير حقيقي في التوكنز!)

لا نعتمد على تقديرات نظرية؛ شغّل بنفسك الأمر `python sqo.py benchmark --workspace .` على أي مشروع لديك لترى الأرقام الحقيقية المقاسة مباشرة على ملفاتك:

<p align="center">
  <img src="./assets/benchmark-comparison.svg" alt="مقارنة استهلاك التوكنز قبل وبعد استخدام Smart Quota v5.0" width="100%" />
</p>

---

## 🛡️ كيف يعمل الدرع الذاتي ثلاثي المراحل تلقائياً أثناء كتابتك للكود؟

<p align="center">
  <img src="./assets/shield-lifecycle.svg" alt="دورة حياة الدرع الذاتي ثلاثي المراحل" width="100%" />
</p>

1. **المرحلة الأولى — `SessionStart` (ذاكرة فورية من اللحظة صفر)**:
   بمجرد فتح محادثة جديدة، يقرأ الـ Hook أهم 8 حقائق معمارية مخزنة في `.sqo/memory.db` ويحقنها مرة واحدة فقط في بداية الجلسة، فيفهم الوكيل بنية مشروعك فوراً بدون إهدار 20 ألف توكن في البحث العشوائي، مع الحفاظ بنسبة **100%** على ثبات بادئة الـ **KV-Cache**!
2. **المرحلة الثانية — `PreToolUse` (جدار ناري رباعي في أقل من `15ms`)**:
   - **حاجز قنابل التوكنز (`Token-Bomb Blocker`)**: يمنع القراءة الكاملة أو أوامر `cat` لملفات القفل والخرائط (`>50 KB`).
   - **مانع القراءات المكررة الذكي (`Stateful Deduplicator`)**: يحفظ بصمة `(المسار + mtime_ns + نطاق الأسطر)` ويرفض إعادة قراءة نفس الملف طالما لم يتغير على القرص!
   - **المُقلّم التلقائي للملفات العملاقة (`overwrite` Auto-Clamper)**: يحوّل أي قراءة عمياء لملف كود يتجاوز `1,200` سطر تلقائياً إلى قراءة أول `280` سطراً فقط (`StartLine: 1, EndLine: 280`).
   - **كاسر الحلقات المفرغة (`Retry-Loop Breaker`)**: يوقف المحاولة الثالثة المتتالية لنفس الأمر الفاشل إذا لم يقم الوكيل بتعديل أي ملف كود بين المحاولات.
3. **المرحلة الثالثة — `PostToolUse` + دفتر التوفير المالي الحي (`sqo roi`)**:
   يسجّل القراءات الناجحة، ويفتح قفل الملف فوراً عند تعديله بـ `edit_file`، ويوثّق كل توكن ودولار تم توفيره في قاعدة بيانات **`roi_ledger.db`**!

<p align="center">
  <img src="./assets/terminal-roi-preview.svg" alt="معاينة مخرجات دفتر التوفير المالي وفحص الطبيب الذكي في الطرفية" width="100%" />
</p>

---

## 🎭 حوارات واقعية كاملة: شاهد الفرق بنفسك (قبل ❌ وبعد ✅)

### السيناريو 1: عطل مفاجئ في الدفع الإلكتروني (`Stack Trace` من 6 ملفات)

| الوجه | ❌ الوكيل التقليدي (بدون الإضافة) | ✅ الوكيل مع Smart Quota `v5.0` |
| :--- | :--- | :--- |
| **طلب المبرمج** | *"عندي خطأ 500 في `/api/stripe/webhook` وده سجل الخطأ، صلحه!"* | *"عندي خطأ 500 في `/api/stripe/webhook` وده سجل الخطأ، صلحه!"* |
| **ما يفعله الوكيل** | يشغّل `grep` عشوائي ⬅️ يقرأ 3 ملفات كاملة (`3,200` سطر) ⬅️ يقرأ ملف `.js.map` بالخطأ ⬅️ يشغّل 200 اختبار دفعة واحدة! | يسترجع ملاحظة Stripe تلقائياً في الجولة 0 ⬅️ يستدعي `sqo_pinpoint_error` فيستخرج الـ 10 أسطر المحيطة بالخطأ فقط ⬅️ يشغّل الاختبار المتأثر فقط عبر `sqo_blast_radius`! |
| **عدد الجولات** | `5` إلى `7` جولات بطيئة | **جولتان فقط (في ثوانٍ!)** |
| **التوكنز المستهلكة** | **`109,700` توكن** (حرق 38% من الكوتا!) | **`1,120` توكن فقط (توفير 98.9%!)** |

### السيناريو 2: حوار حي مع دفتر التوفير المالي والصور (`v5.0` الجديد)

> **👨‍💻 المبرمج:** *"يا بطل، وريني وفرتلي كام توكن ودولار النهاردة، وافحصلي صور التصميم في مجلد `assets/` قبل ما أرفعها في الشات!"*
>
> **🤖 الوكيل (يستدعي `sqo_roi_ledger` و `sqo_media_budget` في أقل من 50 ملي ثانية):**
> - **تقرير التوفير الحي (`ROI Ledger`)**: تم اعتراض **94 عملية إهدار** تلقائياً وتوفير **`1,482,940` توكن** (ما يعادل **`$4.45`** على نماذج Sonnet/Carbon وحتى **`$22.24`** على نماذج Opus)!
> - **فحص ميزانية الصور (`Media Budget`)**: صورة `mockup-4k.png` أبعادها `3840×2160` وستكلفك **`3,870` توكن رؤية** في كل رسالة؛ نصيحة النظام: تصغير العرض الأقصى إلى `1280px` يخفض التكلفة بنسبة **`83%`** مع الحفاظ على وضوح النص الكامل!

📖 **لقراءة 4 حوارات تفصيلية إضافية وخطط عمل متكاملة حسب تخصصك:** افتح **[📗 الدليل العملي العربي الكامل (`docs/PLAYBOOK_AR.md`)](./docs/PLAYBOOK_AR.md)**.

---

## 🔌 جدول الـ 16 أداة المدمجة في خادم الـ MCP (`sqo-engine`)

بمجرد تثبيت الإضافة، يمتلك وكيلك الذكي هذه الأدوات الـ 16 تلقائياً:

| اسم أداة الـ MCP | الوظيفة الفورية | نسبة التوفير |
| :--- | :--- | :--- |
| **`sqo_code_search`** | بحث فوري بخوارزمية `SQLite FTS5 BM25` يرجع الدالة/الكلاس المطلوب بحدوده الدقيقة | **90% – 98%** |
| **`sqo_smart_outline`** | استخراج الهيكل الشجري (`AST Skeleton`) وأرقام الأسطر للملفات الكبيرة أو استخراج دالة بعينها | **85% – 96%** |
| **`sqo_context_pack`** | ضغط مجلد كامل في ميزانية توكنز صارمة (كود كامل للملفات الأساسية + هيكل للمساندة) | **75% – 96%** |
| **`sqo_blast_radius`** | حساب الملفات المتأثرة بالتعديل واختيار **أقل عدد من ملفات الـ Unit Tests** لتشغيلها | **80% – 95%** |
| **`sqo_pinpoint_error`** | تحليل أي `Stack Trace` واستخراج نافذة `±10` أسطر حول كل موقع خطأ محلي في خطوة واحدة | **93% – 96%** |
| **`sqo_code_hotspots`** | رسم بياني تزايدي بـ SQLite يكشف أعقد الملفات وأكثرها ارتباطاً والملفات غير المستوردة | **`<10ms` فوري** |
| **`sqo_api_routes`** | استخراج جدول مسارات الـ API والشاشات لـ Next.js وExpress وNestJS وFastAPI وLaravel وGo وFlutter | **95%+** |
| **`sqo_memory_vault`** | ذاكرة معمارية دائمة عبر الجلسات (`remember` / `recall` / `list`) تُحقن تلقائياً عند البدء | **يلغي إعادة الفحص** |
| **`sqo_dependency_slices`** | تقسيم ملفات المشروع إلى شرائح متوازية خالية 100% من تعارضات الدمج (`Zero Merge Conflicts`) | **يوفر 65%–81% كوتا** |
| **`sqo_budgeted_diff`** | ضغط فروقات `git diff` وحذف ملفات القفل والخرائط لمراجعة الكود بأقل تكلفة | **70% – 95%** |
| **`sqo_secret_scrub`** | فحص المشروع من أي مفاتيح سرية أو كلمات مرور مسربة وتنقية النصوص قبل الإرسال | **حماية أمنية 100%** |
| **`sqo_cache_audit`** | فحص القواعد والـ Hooks لضمان الحفاظ على خصم الـ **KV-Cache (90%)** | **خصم 90% مدخلات** |
| **`sqo_quota_pools`** | تجميع حصص النماذج المشتركة والاحتياطية وحساب معدل الاستهلاك الآمن بالساعة | **منع نفاد الكوتا** |
| **`sqo_benchmark`** | قياس عملي حي لنسبة توفير التوكنز على مشروعك الحالي بالأرقام الدقيقة | **إثبات رقمي حي** |
| **`sqo_roi_ledger`** | عرض سجل التوكنز والدولارات (`$USD`) التي وفّرها الدرع التلقائي | **قياس العائد المالي** |
| **`sqo_media_budget`** | حساب تكلفة الصور (`PNG/JPEG/WebP/GIF`) وملفات `PDF` عبر Gemini وClaude وOpenAI | **50% – 85%** |
| **`sqo_init_preset`** | **(جديد `v6.0`)** كشف تلقائي لنوع المشروع (`Flutter/Next.js/Laravel/Python/Go/Rust`) وتهيئة الدروع والذاكرة | **تهيئة فورية بضغطة** |
| **`sqo_context_health`** | **(جديد `v6.0`)** قياس تآكل وتضخم السياق (`Context Rot 0–100`) وتوليد ملخص تسليم فوري (`<350` توكن) | **توفير ~65% للجولة** |

---

## 🚀 التثبيت السريع في دقيقة واحدة (جميع الأنظمة والمحررات)

### 1️⃣ التثبيت الكامل في Google Antigravity
```powershell
git clone https://github.com/ElNeMeR70/smart-quota-orchestrator.git
cd smart-quota-orchestrator

# على نظام Windows (PowerShell):
powershell -ExecutionPolicy Bypass -File .\install.ps1

# على نظام macOS / Linux:
bash ./install.sh
```

### 2️⃣ تفعيل الحماية وخادم الـ MCP في 5 بيئات برمجة بأمر واحد!
يضبط تلقائياً كلاً من **Antigravity** و**Cursor** و**Claude Code** و**VS Code** و**Windsurf**:
```bash
python sqo.py sync-ide --workspace /path/to/your/project --ides all
```

### 3️⃣ التثبيت الفوري بسطر واحد من المنصة العالمية (`npx` / `irm` / `curl`)
```bash
# عبر npx مباشرة في أي مشروع
npx -y smart-quota-orchestrator init --workspace .

# ويندوز (PowerShell) بسطر واحد من الدومين الرسمي
irm https://sqo.elnemer-ai.com/install.ps1 | iex

# ماك ولينكس بسطر واحد من الدومين الرسمي
curl -fsSL https://sqo.elnemer-ai.com/install.sh | bash
```
- **إضافة شريط الحالة الرسمية لمحررات VS Code / Cursor / Antigravity / Windsurf**: متوفرة في مجلد [`vscode-extension/`](./vscode-extension/) لعرض التوكنز والدولارات الموفّرة لحظياً أسفل المحرر!

---

## 💻 أهم أوامر سطر الأوامر الموحد (`33` أداة في `sqo.py`)

```bash
python sqo.py init --workspace .                # كشف تلقائي لإطار العمل (Flutter/Laravel/Next.js...) وتهيئة كل الدروع!
python sqo.py serve --workspace . --open        # تشغيل مركز القيادة الحي في المتصفح على http://127.0.0.1:7890
python sqo.py compress-prompt -f noisy.json     # (جديد v7.0) ضغط مصفوفات JSON وسجلات الأخطاء المتكررة وحذف المفاتيح السرية
python sqo.py badge -w . -o badge.svg           # (جديد v7.0) توليد شارة SVG حية بنسبة ضغط التوكنز لمستودعك على GitHub
python sqo.py context-health --workspace .      # فحص تضخم السياق التربيعي وتجهيز ملخص التسليم الذكي
python sqo.py doctor --workspace .              # فحص شامل 8 في 1 للمشروع والـ KV-Cache والأمان والتوفير
python sqo.py roi                               # عرض إجمالي التوكنز والدولارات ($USD) التي تم توفيرها
python sqo.py media --workspace .               # حساب تكلفة الصور وملفات PDF بالتوكنز واكتشاف الصور الضخمة
python sqo.py git-guard --workspace .           # تثبيت حارس Git لمنع رفع أي مفتاح سري قبل الـ Commit
python sqo.py hotspots --workspace .            # كشف أعقد ملفات الكود وأكثرها ارتباطاً في أجزاء من الثانية
python sqo.py routes --workspace .              # طباعة جدول كافة مسارات الـ API وصفحات الواجهة
python sqo.py pinpoint -w . -f crash.log        # استخراج أسطر الخطأ بدقة من أي Stack Trace
python sqo.py search "verifyToken" -w .         # بحث دلالي فائق السرعة بخوارزمية BM25
python sqo.py dashboard -w . -o report.html     # توليد لوحة تحكم تفاعلية فخمة بصيغة HTML
```

🌐 **المنصة التفاعلية العالمية الحية (بـ 4 لغات + مختبر ضغط السياق الفوري في المتصفح)**: **[https://sqo.elnemer-ai.com](https://sqo.elnemer-ai.com)** • **حقيبة الإطلاق والنشر العالمي**: [`docs/LAUNCH_KIT.md`](./docs/LAUNCH_KIT.md)

---

## ❓ الأسئلة الشائعة (FAQ)

- **هل تحتاج الأداة إلى أي اشتراك أو مفتاح API أو مكتبات `pip` خارجية؟**
  إطلاقاً! تعمل بنسبة **100%** بالمكتبة القياسية المدمجة في Python (`sqlite3`, `ast`, `struct`, `json`) بدون أي اتصال خارجي، وبياناتك تبقى محلياً بالكامل على جهازك.
- **هل تستهلك الـ Hooks أو خادم الـ MCP أي معالج (CPU) في الخلفية؟**
  صفر بالمئة (`0.0% CPU`) في وضع الانتظار، وتتنفذ فحوصات `PreToolUse` في أقل من `10–15` ملي ثانية!
- **ماذا يحدث لو عدّلت ملفاً بعد قراءته؟ هل سيمنعني مانع التكرار من قراءته مجدداً؟**
  لا! يعتمد مانع التكرار على البصمة الزمنية بالنانوثانية (`st_mtime_ns`) + مرحلة `PostToolUse` التي تفتح القفل تلقائياً فور تعديل الملف.

---

<p align="center">
  صُمّم وطُوّر بشغف لخدمة مجتمع المطورين العالمي والعربي 🌍⚡<br/>
  إذا أفادتك الأداة في مضاعفة إنتاجيتك وتوفير الكوتا، لا تنسَ دعم المستودع بنجمة ⭐ على <a href="https://github.com/ElNeMeR70/smart-quota-orchestrator">GitHub</a>!
</p>

</div>
