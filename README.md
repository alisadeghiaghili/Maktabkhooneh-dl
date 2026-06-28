# 📥 Maktabkhooneh Downloader

[Maktabkhooneh](https://maktabkhooneh.org) یکی از بزرگ‌ترین پلتفرم‌های MOOC فارسی است که دوره‌های خود را از بهترین دانشگاه‌های ایران گردآوری می‌کند.

این ابزار به شما کمک می‌کند تا ویدیوهای دوره‌ها را به صورت batch دانلود کنید. برای دسترسی به ویدیوها، نیاز به حساب کاربری مکتب‌خونه دارید.

---

## 📦 نصب

```bash
pip install -r requirements.txt
playwright install chromium
```

---

## ▶️ اجرا

```bash
python maktabkhooneh_dl.py
```

بعد از اجرا، آدرس دوره را وارد کنید. مثال:

```
https://maktabkhooneh.org/course/آموزش-پایتون-mk123/
```

اگر لاگین نشده باشید، مرورگر باز می‌شود و می‌توانید لاگین کنید. بعد از لاگین، Enter بزنید.

---

## 📂 ساختار خروجی

```
MK_Downloads/
├── 01 - نام فصل اول/
│   ├── 01-نام جلسه.mp4
│   └── 02-نام جلسه.mp4
└── 02 - نام فصل دوم/
    └── 01-نام جلسه.mp4
```

---

## 🛠 سلکتورها

اگر مکتب‌خونه قالب سایت را تغییر داد، کافیست سلکتورها را در ابتدای فایل `maktabkhooneh_dl.py` به‌روز کنید:

```python
CHAPTER_SELECTOR = "div[id^='course-chapter-']"
CHAPTER_TITLE_SELECTOR = "div[title^='فصل'] span.text-xl"
LESSON_SELECTOR = "a.group[href*='/ویدیو-']"
LESSON_TITLE_SELECTOR = "div.BaseChapterContentUnitTitle > span[title]"
DOWNLOAD_SELECTOR = ".unit-content--download a[download]"
LOGIN_BUTTON_SELECTOR = "button#login.button[type='button']"
```

---

## 📋 نکات

- فایل‌هایی که از قبل دانلود شده‌اند مجدداً دانلود نمی‌شوند (`skip_if_exists = True`)
- Profile مرورگر در `./mk_profile` ذخیره می‌شود؛ لاگین شما در اجراهای بعدی حفظ می‌شود
- در صورت پیدا نشدن دکمه دانلود، آن جلسه skip می‌شود و بقیه ادامه پیدا می‌کنند
