"""
Migrate extracted NAIN APK content into Dimhans new app projects.

Source:  DIMHANS_NAIN_Content_Extract/reusable_content + assets
Targets: H:/dhimans/codes/Dimhans/<app>
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

EXTRACT = Path(__file__).resolve().parent
DIMHANS = Path(r"H:\dhimans\codes\Dimhans")
DATA_OUT = DIMHANS / "data" / "nain_migrated"

TEAM_TO_APP = {
    "Team_2_IDD": {
        "app_dir": DIMHANS / "idd_care_app",
        "app_name": "IDD Care App",
        "backend_module": "idd_care",
    },
    "Team_3_SuicideAssess": {
        "app_dir": DIMHANS / "suicide_prevention_app",
        "app_name": "Sahaay (Suicide Prevention)",
        "backend_module": "suicide_prevention",
    },
    "Team_4_DepressionAware": {
        "app_dir": DIMHANS / "teacher_depression_app",
        "app_name": "Teacher Depression Awareness",
        "backend_module": "teacher_depression",
    },
    "Team_6_AlocoholRelapse": {
        "app_dir": DIMHANS / "alcohol_recovery_app",
        "app_name": "Alcohol Recovery",
        "backend_module": "alcohol_recovery",
    },
    "Team_10_NursingIntervention": {
        "app_dir": DIMHANS / "schizo_care_app",
        "app_name": "Schizo Care (Nursing Intervention)",
        "backend_module": "schizo_care",
    },
}

TEACHER_VIDEOS = [
    ("V01", "Understanding Student Part 1", "Foundation", "Teacher", "https://youtu.be/cxWWDRQsi_k"),
    ("V02", "Recognizing early signs of mental health challenges in students", "Symptoms", "Teacher", "https://youtu.be/wRDF7ixjarM"),
    ("V03", "Understanding depression symptoms", "Symptoms", "Teacher", "https://youtu.be/lcR2Xg0TChY"),
    ("V04", "Managing Mild Depression", "Support", "Teacher", "https://youtu.be/QARLq85nRNc"),
    ("V05", "Understanding Severe Depression", "Symptoms", "Teacher", "https://youtu.be/l78Ho49HA5k"),
    ("V06", "Recognizing Depression in Yourself", "Symptoms", "Teacher", "https://youtu.be/BTw1tS7yDMQ"),
    ("V07", "Myths of Depression", "Myths", "Teacher", "https://youtu.be/bYrlyUwGdOE"),
    ("V08", "Risk factors of Depression", "Foundation", "Teacher", "https://youtu.be/-G07bF7NrH0"),
    ("V09", "Promoting student wellbeing", "Support", "Teacher", "https://youtu.be/GGL5GrmYS-s"),
    ("V10", "Effective communication strategies", "Support", "Teacher", "https://youtu.be/IR1nISWZ7o8"),
    ("V11", "When to Seek Professional Help", "Support", "Teacher", "https://youtu.be/Vz1U0eYqVpg"),
    ("V12", "Self-Care Strategies for Teachers", "Support", "Teacher", "https://youtu.be/wAjEKVEFMRo"),
    ("V13", "Professional Mental Health Support", "Support", "Teacher", "https://youtu.be/afg3CrfODSA"),
    ("V14", "Emergency mental health resources", "Support", "Teacher", "https://youtu.be/SIaOnUbA0I4"),
    ("V15", "Mindfulness for Mental Health", "Support", "Both", "https://youtu.be/BaT8Ghj-KTw"),
    ("V16", "Supporting Colleagues in Crisis", "Support", "Teacher", "https://youtu.be/wQ1qP3bfzXw"),
    ("V17", "Working with mental health professionals", "Support", "Teacher", "https://youtu.be/VtRTrmExsm0"),
    ("V18", "Building positive classroom environments", "Support", "Teacher", "https://youtu.be/sLGvFWIwW4U"),
    ("V19", "Maintaining Mental Health as an Educator", "Support", "Teacher", "https://youtu.be/gPEGjnppKJg"),
    ("V20", "Coping with Teacher Burnout", "Support", "Teacher", "https://youtu.be/wc5LoQvUVhY"),
    ("V21", "Tips for maintaining good mental health", "Support", "Both", "https://youtu.be/GHz6BbkhQSE"),
]

ALCOHOL_VIDEOS = [
    ("Public", "Alcohol & Health", "https://www.youtube.com/watch?v=5h3CtiG99yE&t=2s"),
    ("Public", "Recovery awareness", "https://www.youtube.com/watch?v=FJJazKtH_9I"),
    ("Public", "Understanding addiction", "https://youtu.be/Z1jtmFlNB-c"),
    ("Student", "Alcohol's effect on Teenage Brain", "https://youtu.be/EY37BFmVxwQ"),
    ("Student", "Youth substance awareness", "https://youtu.be/jfhMlfxaIvw"),
    ("Student", "Peer support resources", "https://youtu.be/9IizjqPQyK8"),
]

TEACHER_QUIZ_QUESTIONS = [
    "Consequences of long term untreated depression are?",
    "What proportion of people experience depression at some point in their lives?",
    "Risk factors for depression are?",
    "What are the psychological risk factors for depression?",
    "The first step in the pathway to manage depression is?",
    "Sleep of a person with depression is usually?",
    "Increasing awareness about depression to the following will help in early identification?",
    "Reason for many people not taking treatment for depression is?",
    "Most typical of a person with depression are?",
    "Education and communication programmes about depression can increase?",
    "To diagnose depression the symptoms need to be present for a minimum period of at least?",
    "Individuals are ashamed to visit a mental health professional, due to?",
    "The treatment for depression in hospital includes?",
    "Depression can affect?",
    "Which of the following symptoms are expected in depressive patient?",
    "The burden of depression in India is?",
    "Awareness about depression for children and adolescents in educational setting aims to improve?",
    "Depression can contribute to?",
    "Activity level of a person with depression is usually?",
    "Which among following is not a social factor for risk of depression?",
    "Symptoms of depression in school going adolescent are?",
    "Which among the following are economic risk factors for depression?",
    "Which of following is not the warning sign of suicide in adolescent depression?",
    "At the worst of depression, person may?",
    "Depressive disorder is a?",
    "Which among the following is the cultural risk factor for depression?",
    "Depression may present with?",
    "Mood of a person with depression is?",
    "Biological risk factor for depression is?",
    "Depression is a?",
]


def transform_scenario(old: dict) -> dict:
    decisions = []
    for d in old.get("decisions", []):
        options = []
        for o in d.get("options", []):
            options.append(
                {
                    "text": o.get("text") or o.get("label", ""),
                    "is_correct": bool(o.get("is_correct", o.get("isCorrect", False))),
                    "feedback": o.get("feedback", ""),
                }
            )
        decisions.append({"question": d.get("question", ""), "options": options})
    return {
        "id": str(old.get("id", "")),
        "title": old.get("title", ""),
        "context": old.get("context", ""),
        "decisions": decisions,
    }


def transform_question(old: dict, idx: int) -> dict:
    correct = old.get("correct_index", old.get("correctIndex"))
    if correct is None:
        correct = 0
    qid = old.get("id", idx + 1)
    if isinstance(qid, str) and qid.isdigit():
        qid = int(qid)
    return {
        "id": qid if isinstance(qid, int) else idx + 1,
        "category": old.get("category", "general_knowledge"),
        "question": old.get("question", ""),
        "options": old.get("options", []),
        "correct_index": int(correct),
    }


def copy_files(src_files: list[Path], dest_dir: Path) -> list[str]:
    dest_dir.mkdir(parents=True, exist_ok=True)
    copied = []
    for src in src_files:
        if not src.exists():
            continue
        dest = dest_dir / src.name
        shutil.copy2(src, dest)
        copied.append(str(dest))
    return copied


def migrate_suicide_prevention() -> dict:
    team = "Team_3_SuicideAssess"
    reuse = EXTRACT / "reusable_content" / team
    app = TEAM_TO_APP[team]["app_dir"]
    assets_data = app / "assets" / "data"
    assets_images = app / "assets" / "images"
    assets_data.mkdir(parents=True, exist_ok=True)
    assets_images.mkdir(parents=True, exist_ok=True)

    scenarios_src = json.loads((reuse / "json" / "case_scenarios.json").read_text(encoding="utf-8"))
    scenarios = [transform_scenario(s) for s in scenarios_src]
    (assets_data / "scenarios.json").write_text(
        json.dumps(scenarios, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    questions_src = json.loads((reuse / "json" / "suicide_prevention_questions.json").read_text(encoding="utf-8"))
    questions = [transform_question(q, i) for i, q in enumerate(questions_src)]
    (assets_data / "questions.json").write_text(
        json.dumps(questions, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    additional = reuse / "json" / "additional_content.json"
    shutil.copy2(additional, assets_data / "additional_content.json")

    images = copy_files(list((reuse / "images").glob("*")), assets_images)

    pack = {
        "team": team,
        "app": TEAM_TO_APP[team]["app_name"],
        "scenarios": len(scenarios),
        "questions": len(questions),
        "additional_content": True,
        "images": len(images),
        "youtube_playlist": "https://www.youtube.com/playlist?list=PLkHgexqsdsq4fzpgfPrUk3mrIH0_RcKgT",
        "emergency_phones": ["14416", "0836-2440202"],
        "maps_link": "https://maps.app.goo.gl/ZYYGrWMwWGsLHLnj8",
    }
    (DATA_OUT / team).mkdir(parents=True, exist_ok=True)
    (DATA_OUT / team / "content_pack.json").write_text(json.dumps(pack, indent=2), encoding="utf-8")
    return pack


def migrate_teacher_depression() -> dict:
    team = "Team_4_DepressionAware"
    reuse = EXTRACT / "reusable_content" / team
    out = DATA_OUT / team
    out.mkdir(parents=True, exist_ok=True)

    videos = [
        {
            "id": vid,
            "title": {"en": title},
            "description": {"en": title},
            "url": url,
            "category": category,
            "audience": audience,
            "tags": [category],
        }
        for vid, title, category, audience, url in TEACHER_VIDEOS
    ]
    (out / "videos.json").write_text(json.dumps(videos, indent=2, ensure_ascii=False), encoding="utf-8")

    quiz = [
        {
            "id": i + 1,
            "category": "Depression Knowledge",
            "question_text": {"en": q},
            "options": [],
            "correct_option_id": None,
            "explanation": {"en": ""},
            "difficulty": "Medium",
            "source": "Team_4 APK — options to be finalized in CMS",
        }
        for i, q in enumerate(TEACHER_QUIZ_QUESTIONS)
    ]
    (out / "quiz_questions.json").write_text(json.dumps(quiz, indent=2, ensure_ascii=False), encoding="utf-8")

    images = copy_files(list((reuse / "images").glob("*")), out / "images")
    demo = copy_files(list((EXTRACT / "assets" / team / "videos").glob("*.mp4")), out / "videos")

    pack = {"team": team, "videos": len(videos), "quiz_questions": len(quiz), "images": len(images), "demo_videos": len(demo)}
    (out / "content_pack.json").write_text(json.dumps(pack, indent=2), encoding="utf-8")
    return pack


def migrate_idd() -> dict:
    team = "Team_2_IDD"
    reuse = EXTRACT / "reusable_content" / team
    out = DATA_OUT / team
    out.mkdir(parents=True, exist_ok=True)

    categories = [
        {"name_en": "Personal Hygiene", "icon": "bath.png", "activities": ["Hand Washing", "Brushing Teeth", "Bathing"]},
        {"name_en": "Dressing", "icon": "clothess.png", "activities": ["Getting Dressed"]},
        {"name_en": "Eating", "icon": "eating.png", "activities": ["Eating Independently"]},
    ]
    images = copy_files(list((reuse / "images").glob("*")), out / "images")
    demo = copy_files(list((EXTRACT / "assets" / team / "videos").glob("*.mp4")), out / "videos")

    pack = {
        "team": team,
        "categories": categories,
        "images": len(images),
        "demo_videos": len(demo),
        "note": "Instructional YouTube URLs were stripped from Dimhans_IDD_w_o_videos.apk; use full APK or source repo for video URLs.",
    }
    (out / "categories.json").write_text(json.dumps(categories, indent=2), encoding="utf-8")
    (out / "content_pack.json").write_text(json.dumps(pack, indent=2), encoding="utf-8")
    return pack


def migrate_alcohol() -> dict:
    team = "Team_6_AlocoholRelapse"
    reuse = EXTRACT / "reusable_content" / team
    out = DATA_OUT / team
    out.mkdir(parents=True, exist_ok=True)

    videos = [{"audience": a, "title": t, "url": u} for a, t, u in ALCOHOL_VIDEOS]
    (out / "videos.json").write_text(json.dumps(videos, indent=2), encoding="utf-8")
    images = copy_files(list((reuse / "images").glob("*")), out / "images")
    demo = copy_files(list((EXTRACT / "assets" / team / "videos").glob("*.mp4")), out / "videos")

    pack = {"team": team, "videos": len(videos), "images": len(images), "demo_videos": len(demo)}
    (out / "content_pack.json").write_text(json.dumps(pack, indent=2), encoding="utf-8")
    return pack


def migrate_schizo() -> dict:
    team = "Team_10_NursingIntervention"
    reuse = EXTRACT / "reusable_content" / team
    app = TEAM_TO_APP[team]["app_dir"]
    out = DATA_OUT / team
    out.mkdir(parents=True, exist_ok=True)

    # Merge translation keys from old APK into new app (keep existing app keys)
    trans_dest = app / "assets" / "translations"
    merged = 0
    for lang in ("en", "hi", "kn"):
        src_path = reuse / "json" / f"{lang}.json"
        dest_path = trans_dest / f"{lang}.json"
        if not src_path.exists() or not dest_path.exists():
            continue
        src = json.loads(src_path.read_text(encoding="utf-8"))
        dest = json.loads(dest_path.read_text(encoding="utf-8"))
        before = len(dest)
        for k, v in src.items():
            dest.setdefault(k, v)
        if len(dest) > before:
            merged += len(dest) - before
        dest_path.write_text(json.dumps(dest, indent=2, ensure_ascii=False), encoding="utf-8")

    images = copy_files(list((reuse / "images").glob("*")), out / "images")
    for lang in ("en", "hi", "kn"):
        src = reuse / "json" / f"{lang}.json"
        if src.exists():
            shutil.copy2(src, out / f"translations_{lang}.json")

    demo = copy_files(list((EXTRACT / "assets" / team / "videos").glob("*.mp4")), out / "videos")
    pack = {
        "team": team,
        "translation_keys_merged": merged,
        "images": len(images),
        "demo_videos": len(demo),
        "note": "Clinical videos/quizzes live in backend DB — seed from Team 10 source repo if available.",
    }
    (out / "content_pack.json").write_text(json.dumps(pack, indent=2), encoding="utf-8")
    return pack


def write_migration_map(results: dict):
    lines = [
        "# NAIN APK → Dimhans New Apps — Content Migration Map",
        "",
        "Generated by `migrate_content_to_dimhans.py`.",
        "",
        "| Old Team (APK) | New App | What was migrated |",
        "| -------------- | ------- | ----------------- |",
        f"| Team_3_SuicideAssess | `suicide_prevention_app` | {results['Team_3']['scenarios']} scenarios, {results['Team_3']['questions']} quiz Qs, additional_content.json, images |",
        f"| Team_4_DepressionAware | `teacher_depression_app` + backend seed | {results['Team_4']['videos']} YouTube videos, {results['Team_4']['quiz_questions']} quiz question texts |",
        f"| Team_2_IDD | `idd_care_app` + backend seed | Category images + structure (videos stripped in APK) |",
        f"| Team_6_AlocoholRelapse | `alcohol_recovery_app` | {results['Team_6']['videos']} video links catalog |",
        f"| Team_10_NursingIntervention | `schizo_care_app` | Translations merged, faculty images |",
        "",
        "## Paths",
        "",
        f"- **Extracted reusable content:** `{EXTRACT / 'reusable_content'}`",
        f"- **Migration output (JSON packs):** `{DATA_OUT}`",
        "",
        "## Next steps for developers",
        "",
        "1. **Suicide app** — Register `assets/data/additional_content.json` in `pubspec.yaml` if you add UI for it.",
        "2. **Teacher Depression** — Run backend seed using `data/nain_migrated/Team_4_DepressionAware/videos.json`.",
        "3. **IDD** — Replace placeholder activity videos in `seed_idd.py` when full APK/source is available.",
        "4. **Schizo Care** — Seed clinical videos/quizzes in centralized backend from Team 10 nursing content.",
        "",
    ]
    (EXTRACT / "APP_MIGRATION_MAP.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    DATA_OUT.mkdir(parents=True, exist_ok=True)
    results = {
        "Team_3": migrate_suicide_prevention(),
        "Team_4": migrate_teacher_depression(),
        "Team_2": migrate_idd(),
        "Team_6": migrate_alcohol(),
        "Team_10": migrate_schizo(),
    }
    write_migration_map(results)
    summary_path = DATA_OUT / "migration_summary.json"
    summary_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print("Migration complete:")
    for k, v in results.items():
        print(f"  {k}: {v}")
    print(f"\nSummary: {summary_path}")
    print(f"Map: {EXTRACT / 'APP_MIGRATION_MAP.md'}")


if __name__ == "__main__":
    main()
