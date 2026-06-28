# 📥 Maktabkhooneh Downloader

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/playwright-chromium-green)](https://playwright.dev/python/)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)

ابزار دانلود Batch ویدیوهای دوره‌های [Maktabkhooneh.org](https://maktabkhooneh.org) با استفاده از Playwright.

---

## 📋 پیشنیازها

- Python 3.10+
- حساب کاربری فعال در مکتب‌خونه با دسترسی به دوره

---

## 📦 نصب

```bash
pip install -r requirements.txt
playwright install chromium
```

---

## ▶️ نحوه استفاده

### ساده‌ترین حالت — پرسش تعاملی

```bash
python maktabkhooneh_dl.py
```

اسکریپت آدرس دوره را می‌پرسد. در صورت نیاز به لاگین، مرورگر باز می‌شود و بعد از لاگین Enter بزنید.

### با آرگومان CLI

```bash
python maktabkhooneh_dl.py \
  --url https://maktabkhooneh.org/course/آموزش-پایتون-mk123/ \
  --username my@email.com \
  --output ./downloads
```

> ⚠️ از دادن `--password` به عنوان flag **پرهیز کنید** — در shell history ذخیره می‌شود.

### با متغیرهای محیطی — امنترین روش

```bash
export MK_USERNAME="my@email.com"
export MK_PASSWORD="my_password"

python maktabkhooneh_dl.py \
  --url https://maktabkhooneh.org/course/آموزش-پایتون-mk123/
```

پسورد ردیابی نمی‌شود و در shell history ذخیره نمی‌ماند.

---

## 🛠️ آرگومان‌ها

| آرگومان | پیش‌فرض | توضیح |
|---|---|---|
| `--url URL` | — | آدرس کامل صفحه دوره |
| `-u` / `--username` | `MK_USERNAME` یا prompt | ایمیل یا شماره موبایل |
| `-p` / `--password` | `MK_PASSWORD` یا getpass | رمز عبور (ترجیح: env var یا prompt) |
| `--output DIR` | `./MK_Downloads` | پوشه ذخیره‌سازی |
| `--profile DIR` | `./mk_profile` | پوشه پروفایل مرورگر |
| `--no-skip` | — | دانلود مجدد فایل‌های موجود |

**اولویت اعتبارسنجی اطلاعات ورود:**
```
CLI flag  ➟  Env var (MK_USERNAME / MK_PASSWORD)  ➟  Interactive prompt
```

---

## 📂 ساختار خروجی

فایل‌ها به ترتیب فصل و جلسه ذخیره می‌شوند:

```
MK_Downloads/
├── 01 - مقدمه و نصب/
│   ├── 01-معرفی دوره.mp4
│   └── 02-نصب پایتون.mp4
├── 02 - مفاهیم پایه/
│   ├── 01-متغیرها.mp4
│   └── 02-حلقه‌ها.mp4
└── 03 - توابع/
    └── 01-تعریف تابع.mp4
```

---

## 🛠 سلکتورها

سلکتورها در ابتدای `maktabkhooneh_dl.py` تعریف شده‌اند. اگر مکتب‌خونه قالب سایت را تغییر داد، فقط آن بخش را به‌روز کنید:

```python
# -------------------- Selectors --------------------
CHAPTER_SELECTOR = "div[id^='course-chapter-']"
CHAPTER_TITLE_SELECTOR = "div[title^='فصل'] span.text-xl"
LESSON_SELECTOR = "a.group[href*='/ویدیو-']"
LESSON_TITLE_SELECTOR = "div.BaseChapterContentUnitTitle > span[title]"
DOWNLOAD_SELECTOR = ".unit-content--download a[download]"
LOGIN_BUTTON_SELECTOR = "button#login.button[type='button']"
# -------------------- End of Selectors --------------------
```

---

## ❓ سوالات متداول

**دانلود شروع نمی‌شود — خطای سلکتور می‌دهد**

احتمالاً مکتب‌خونه ساختار HTML را آپدیت کرده. سلکتورها را طبق بخش بالا به‌روز کنید.

**دانلود ناقص یا خراب است**

با `--no-skip` اجرا کنید تا فایل‌های ناقص مجدداً دانلود شوند.

**لاگین در هر اجرا پرسیده می‌شود**

پوشه `./mk_profile` را حذف نکنید. پروفایل مرورگر (session) را ذخیره می‌کند و بار بعدی نیازی به لاگین ندارید.

---

## 📄 لایسنس

[MIT](LICENSE)
