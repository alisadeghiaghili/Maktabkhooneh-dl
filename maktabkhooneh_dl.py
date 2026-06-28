#!/usr/bin/env python3

# Standard library imports
import re
from pathlib import Path

# Third-party imports
from playwright.sync_api import sync_playwright

# -------------------- Selectors --------------------
# Course page selectors
CHAPTER_SELECTOR = "div[id^='course-chapter-']"
CHAPTER_TITLE_SELECTOR = "div[title^='فصل'] span.text-xl"
LESSON_SELECTOR = "a.group[href*='/ویدیو-']"
LESSON_TITLE_SELECTOR = "div.BaseChapterContentUnitTitle > span[title]"
# Download button on lesson page
DOWNLOAD_SELECTOR = ".unit-content--download a[download]"
# Login button
LOGIN_BUTTON_SELECTOR = "button#login.button[type='button']"
# -------------------- End of Selectors --------------------


def slugify(txt: str) -> str:
    txt = re.sub(r"[^\w\s\-\.]", "", txt, flags=re.UNICODE)
    txt = re.sub(r"\s+", " ", txt, flags=re.UNICODE).strip()
    txt = txt.replace("/", "-")
    return txt


def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def main():
    course_url = input("Please enter the course URL: ").strip()
    output_dir = Path("MK_Downloads")
    user_data_dir = Path("./mk_profile")
    skip_if_exists = True

    ensure_dir(output_dir)
    ensure_dir(user_data_dir)

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(user_data_dir),
            headless=False,
            viewport={"width": 1920, "height": 1080},
        )
        page = browser.new_page()

        page.goto(course_url, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)

        if page.query_selector(LOGIN_BUTTON_SELECTOR):
            print("[INFO] Not logged in. Please log in via the browser...")
            page.click(LOGIN_BUTTON_SELECTOR)
            page.wait_for_timeout(15000)
            input("✅ After logging in, press Enter to continue...")

        page.wait_for_selector(CHAPTER_SELECTOR)

        chapters = page.query_selector_all(CHAPTER_SELECTOR)
        print(f"[INFO] Found {len(chapters)} chapter(s).")

        chapters_data = []
        for ch_idx, ch in enumerate(chapters, start=1):
            ch_title_el = ch.query_selector(CHAPTER_TITLE_SELECTOR)
            ch_title = slugify(ch_title_el.inner_text()) if ch_title_el else f"Chapter_{ch_idx}"

            lessons = ch.query_selector_all(LESSON_SELECTOR)
            lesson_infos = []
            for l_idx, lesson in enumerate(lessons, start=1):
                l_title_el = lesson.query_selector(LESSON_TITLE_SELECTOR)
                l_title = (
                    slugify(l_title_el.get_attribute("title") or l_title_el.inner_text())
                    if l_title_el
                    else f"Lesson_{l_idx}"
                )
                lesson_href = lesson.get_attribute("href")
                if not lesson_href:
                    print(f"[WARN] Lesson {l_idx} in chapter {ch_idx} has no href, skipping.")
                    continue
                if not lesson_href.startswith("http"):
                    lesson_href = "https://maktabkhooneh.org" + lesson_href
                lesson_infos.append((l_idx, l_title, lesson_href))

            chapters_data.append((ch_idx, ch_title, lesson_infos))

        for ch_idx, ch_title, lesson_infos in chapters_data:
            chapter_dir = output_dir / f"{ch_idx:02d} - {ch_title}"
            ensure_dir(chapter_dir)
            for l_idx, l_title, lesson_href in lesson_infos:
                out_path = chapter_dir / f"{l_idx:02d}-{l_title}.mp4"
                if skip_if_exists and out_path.exists():
                    print(f"[SKIP] {out_path.name}")
                    continue
                print(f"[INFO] Downloading: {out_path.name}")
                page.goto(lesson_href, wait_until="domcontentloaded")
                try:
                    page.wait_for_selector(DOWNLOAD_SELECTOR, timeout=15000)
                except Exception:
                    print(f"[ERROR] Download button not found for lesson {l_idx}, skipping.")
                    continue
                with page.expect_download(timeout=600000) as dl_info:
                    page.click(DOWNLOAD_SELECTOR)
                dl_info.value.save_as(str(out_path))

        browser.close()


if __name__ == "__main__":
    main()
