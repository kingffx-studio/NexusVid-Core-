import os
import json
import asyncio
import edge_tts
from google import genai
from google.genai import types
from googleapiclient.discovery import build

# ==========================================
# CONFIGURATION & API KEYS (From GitHub Secrets)
# ==========================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")

USER_CATEGORY = os.environ.get("USER_CATEGORY", "3D Cartoon Moral & Suspense Story")
VIDEO_FORMAT = os.environ.get("VIDEO_FORMAT", "Shorts")  # Options: "Shorts" or "Long"
TARGET_TOPIC = os.environ.get("TARGET_TOPIC", "A poor boy finds a magical futuristic watch")

# Initialize Gemini Client
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_ID = "gemini-2.5-flash"

# ==========================================
# STEP 0: AUTO-CREATE STORAGE FOLDERS (GODOWN)
# ==========================================
FOLDERS = [
    "assets/characters_png",
    "assets/backgrounds",
    "assets/sfx_and_bgm",
    "output/scenes",
    "output/final"
]

def setup_directories():
    print("[SYSTEM] Initializing NexusVid-Core Directory Architecture...")
    for folder in FOLDERS:
        os.makedirs(folder, exist_ok=True)
    print("[SYSTEM] All asset and output directories verified.")

def call_gemini_json(system_instruction, user_prompt):
    """Helper function to force clean JSON output from Gemini Agents."""
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            temperature=0.7
        )
    )
    return json.loads(response.text.strip())

# ==========================================
# DEPARTMENT 1: 4 NICHE & VIABILITY AGENTS
# ==========================================
def run_department_1_topic_check(category, video_format, topic):
    print("\n[DEPT 1] Running 4 Niche & Topic Viability Agents...")
    sys_prompt = """
    You are a committee of 4 YouTube & Instagram Strategy Agents:
    1. User Profiler Agent: Analyzes category and format (Shorts vs Long).
    2. Trend Checker Agent: Checks if the topic has high viral potential today.
    3. Audience Mood Reader: Identifies the core emotion (Suspense, Shock, Curiosity, Fun).
    4. Topic Improver Agent: Twists the topic to make it 10x more clickable and viral.
    """
    prompt = f"""
    Category: {category}
    Format: {video_format}
    Initial Topic: {topic}

    Return JSON with this exact structure:
    {{
        "is_initially_viral": true,
        "viability_score_out_of_10": 8,
        "audience_emotion": "string",
        "improved_viral_topic": "string",
        "improvement_reason": "string"
    }}
    """
    result = call_gemini_json(sys_prompt, prompt)
    print(f"[DEPT 1] Upgraded Viral Topic: {result['improved_viral_topic']} (Score: {result['viability_score_out_of_10']}/10)")
    return result

# ==========================================
# DEPARTMENT 2: 4 DEEP RESEARCH & SPY AGENTS
# (Small Channels, Big Channels, IG Trends, Channel Doctor)
# ==========================================
def fetch_youtube_competitors(query):
    """Fetches real YouTube video data and channel subscriber counts."""
    if not YOUTUBE_API_KEY:
        print("[DEPT 2] No YOUTUBE_API_KEY found. Using AI Trend Simulation...")
        return "Simulated Data: Fast-paced hooks under 3 seconds, high-contrast cartoon characters, suspense cliffhangers."

    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        search_res = youtube.search().list(
            q=query, part="snippet", type="video", order="viewCount", maxResults=8
        ).execute()

        video_ids = [item["id"]["videoId"] for item in search_res.get("items", [])]
        channel_ids = list(set([item["snippet"]["channelId"] for item in search_res.get("items", [])]))

        if not video_ids:
            return "No direct videos found."

        vid_stats = youtube.videos().list(part="statistics,snippet", id=",".join(video_ids)).execute()
        chan_stats = youtube.channels().list(part="statistics", id=",".join(channel_ids)).execute()

        sub_map = {
            c["id"]: int(c["statistics"].get("subscriberCount", 0))
            for c in chan_stats.get("items", [])
        }

        report = []
        for v in vid_stats.get("items", []):
            cid = v["snippet"]["channelId"]
            subs = sub_map.get(cid, 0)
            views = int(v["statistics"].get("viewCount", 0))
            title = v["snippet"]["title"]
            channel_type = "SMALL_CHANNEL_OUTLIER" if subs < 50000 else "BIG_AUTHORITY_CHANNEL"
            report.append(f"[{channel_type}] Title: {title} | Views: {views} | Subscribers: {subs}")

        return "\n".join(report)
    except Exception as e:
        print(f"[DEPT 2] YouTube API Warning: {e}")
        return "Fallback Data: High retention hooks, emotional storytelling, clear character consistency."

def run_department_2_spy_squad(category, improved_topic):
    print("\n[DEPT 2] Deploying 4 Spy Agents (Small Channels, Big Channels, IG Trends, Channel Doctor)...")
    raw_yt_data = fetch_youtube_competitors(f"{category} {improved_topic}")

    sys_prompt = """
    You are a Research Squad of 4 Spy Agents:
    1. Small Channel Spy: Finds how low-subscriber channels get massive views.
    2. Big Channel Mastermind: Extracts quality & storytelling secrets from big channels.
    3. Instagram & Cross-Platform Trend Spy: Identifies current viral audio, pacing, and visual hooks on Instagram Reels (both AI and non-AI).
    4. Channel Doctor Agent: Lists exact mistakes to avoid so the video doesn't flop.
    """
    prompt = f"""
    Category: {category}
    Upgraded Topic: {improved_topic}
    Real YouTube Market Data:
    {raw_yt_data}

    Return JSON with this exact structure:
    {{
        "small_channel_secret": "string",
        "big_channel_formula": "string",
        "instagram_viral_trend_to_copy": "string",
        "mistakes_to_avoid": "string",
        "winning_hook_formula": "string"
    }}
    """
    result = call_gemini_json(sys_prompt, prompt)
    print(f"[DEPT 2] Winning Hook Formula Identified: {result['winning_hook_formula']}")
    return result

# ==========================================
# DEPARTMENT 3: WRITER + 6 STRICT SCRIPT JUDGES
# ==========================================
def run_department_3_script_and_6_judges(topic_data, spy_data, video_format):
    print("\n[DEPT 3] Starting Script Writer & 6-Judge Quality Board Loop...")
    target_duration = "50 to 60 seconds" if video_format.lower() == "shorts" else "4 to 5 minutes"

    feedback_notes = "No previous feedback. Write the first draft."
    for attempt in range(1, 4):
        print(f"  -> Script Draft Attempt #{attempt}...")
        writer_sys = "You are a Master Viral Scriptwriter for YouTube and Instagram."
        writer_prompt = f"""
        Topic: {topic_data['improved_viral_topic']}
        Target Duration: {target_duration}
        Spy Report: {json.dumps(spy_data)}
        Previous Judge Feedback to Fix: {feedback_notes}

        Write an engaging Hindi script (written in clean Hinglish/Hindi for natural spoken voiceover).
        Return JSON:
        {{
            "hook_first_3_sec": "string",
            "full_spoken_script_hindi": "string (ONLY spoken words, no stage directions)",
            "visual_story_summary": "string"
        }}
        """
        draft = call_gemini_json(writer_sys, writer_prompt)

        # Now 6 Judges inspect the script
        judges_sys = """
        You are the 6 Strict Script Judges:
        Judge 1: 3-Second Hook Tester
        Judge 2: Anti-Boredom & Retention Inspector
        Judge 3: Conversational Hindi Tone Checker
        Judge 4: Suspense & Emotion Evaluator
        Judge 5: Visual & Cartoon Feasibility Checker
        Judge 6: Final Viral Score Predictor
        If ANY judge gives a score below 8/10, set 'approved' to false and give strict improvement instructions.
        """
        judges_prompt = f"""
        Evaluate this script draft:
        {json.dumps(draft, ensure_ascii=False)}

        Return JSON:
        {{
            "judge_1_hook_score": 9,
            "judge_2_retention_score": 9,
            "judge_3_tone_score": 9,
            "judge_4_emotion_score": 9,
            "judge_5_visual_score": 9,
            "judge_6_viral_score": 9,
            "approved": true,
            "combined_critique_if_failed": "string"
        }}
        """
        verdict = call_gemini_json(judges_sys, judges_prompt)
        avg_score = (
            verdict["judge_1_hook_score"] + verdict["judge_2_retention_score"] +
            verdict["judge_3_tone_score"] + verdict["judge_4_emotion_score"] +
            verdict["judge_5_visual_score"] + verdict["judge_6_viral_score"]
        ) / 6.0

        print(f"  -> 6 Judges Average Score: {avg_score:.1f}/10 | Approved: {verdict['approved']}")
        if verdict["approved"] and avg_score >= 8.0:
            return draft
        feedback_notes = verdict["combined_critique_if_failed"]

    return draft

# ==========================================
# DEPARTMENT 4 & 5: 8-10s SCENE SLICER + SMART PNG WARDROBE PLANNER
# ==========================================
def run_department_4_and_5_scene_and_png_planner(approved_script, category):
    print("\n[DEPT 4 & 5] Slicing Script into 8-10s Chunks & Locking Main Character PNG Wardrobe...")
    sys_prompt = """
    You are a team of 4 Scene Slicer Agents and 4 Character/Background Consistency Agents.
    Rules:
    1. Identify ONLY the most frequently used Main Character(s) and create a 'master_character_png_bank' for them.
    2. If a main character changes clothes in the story, keep the EXACT SAME face/body description and create a second PNG entry for the new outfit (e.g., 'raju_default.png' and 'raju_suit.png'). Both PNGs must be saved and referenced accurately.
    3. Identify recurring backgrounds and list them in 'background_bank'.
    4. Slice the story into 8 to 10-second scenes. Each scene must specify which Character PNG file, which Background file, Camera Angle, Color Grading mood, and Sound Effect (SFX) to use.
    """
    prompt = f"""
    Visual Style / Category: {category}
    Approved Script:
    {approved_script['full_spoken_script_hindi']}

    Return JSON with this exact structure:
    {{
        "master_character_png_bank": [
            {{
                "character_id": "char_1",
                "png_filename": "assets/characters_png/main_hero_default.png",
                "base_face_and_body_prompt": "Detailed English prompt for character face, age, hair, style on solid white background, full body standing",
                "outfit_description": "Default outfit description",
                "is_outfit_variant": false
            }}
        ],
        "background_bank": [
            {{
                "bg_id": "bg_1",
                "bg_filename": "assets/backgrounds/village_house.jpg",
                "bg_prompt": "Detailed English prompt for empty background without any people"
            }}
        ],
        "scenes_8_to_10_sec": [
            {{
                "scene_number": 1,
                "duration_seconds": 9,
                "spoken_narration_hindi": "string",
                "active_character_png": "assets/characters_png/main_hero_default.png",
                "active_background_img": "assets/backgrounds/village_house.jpg",
                "image_to_video_action_prompt": "English prompt describing how the PNG character moves/acts in this 9-second video clip",
                "camera_motion": "Slow zoom in / Pan right",
                "color_grading_style": "Warm cinematic / Dark suspense",
                "sfx_sound_cue": "footsteps on wood, wind blowing"
            }}
        ]
    }}
    """
    plan = call_gemini_json(sys_prompt, prompt)
    print(f"[DEPT 4 & 5] Created {len(plan['master_character_png_bank'])} Character PNG Outfits, "
          f"{len(plan['background_bank'])} Backgrounds, and {len(plan['scenes_8_to_10_sec'])} Scenes (8-10s each).")
    return plan

# ==========================================
# DEPARTMENT 7 & 8: 4 SEO AGENTS + 4 THUMBNAIL AGENTS
# ==========================================
def run_department_7_and_8_seo_and_thumbnail(topic_data, approved_script):
    print("\n[DEPT 7 & 8] Running 4 Title/SEO Agents & 4 Thumbnail Judge Agents...")
    sys_prompt = """
    You are 4 SEO Agents and 4 Thumbnail Viral Judge Agents.
    Generate 5 titles, test them, and lock the #1 highest-CTR title, description, tags, and the #1 viral thumbnail design.
    """
    prompt = f"""
    Topic: {topic_data['improved_viral_topic']}
    Script Summary: {approved_script['visual_story_summary']}

    Return JSON:
    {{
        "tested_titles": ["title 1", "title 2", "title 3"],
        "locked_viral_title": "string",
        "seo_description": "string",
        "viral_tags": ["tag1", "tag2", "tag3"],
        "thumbnail_blueprint": {{
            "visual_prompt": "Detailed English prompt for high-CTR YouTube thumbnail using main character face",
            "big_bold_text_on_thumbnail": "2-3 shocking words in Hindi/English",
            "color_psychology_used": "Yellow text on dark high-contrast background",
            "ctr_judge_score": 9.5
        }}
    }}
    """
    seo_thumb = call_gemini_json(sys_prompt, prompt)
    print(f"[DEPT 7 & 8] Locked Viral Title: {seo_thumb['locked_viral_title']}")
    return seo_thumb

# ==========================================
# AUDIO ENGINE: FIXED CONSISTENT HINDI VOICEOVER
# ==========================================
async def generate_locked_voiceover(full_script_text, output_path="output/master_voiceover.mp3"):
    print("\n[AUDIO ENGINE] Generating 100% Consistent Hindi Voiceover...")
    communicate = edge_tts.Communicate(full_script_text, "hi-IN-MadhurNeural", rate="+5%")
    await communicate.save(output_path)
    print(f"[AUDIO ENGINE] Master Voiceover saved at: {output_path}")

# ==========================================
# MAIN EXECUTION PIPELINE
# ==========================================
if __name__ == "__main__":
    setup_directories()

    # 1. Niche & Topic Viability (4 Agents)
    topic_report = run_department_1_topic_check(USER_CATEGORY, VIDEO_FORMAT, TARGET_TOPIC)

    # 2. Spy Research Squad (4 Agents: Small/Big Channels + IG Trends)
    spy_report = run_department_2_spy_squad(USER_CATEGORY, topic_report["improved_viral_topic"])

    # 3. Writer + 6 Judges Loop
    final_script = run_department_3_script_and_6_judges(topic_report, spy_report, VIDEO_FORMAT)

    # 4 & 5. 8-10s Scene Slicer + Smart Character PNG Wardrobe Bank
    production_plan = run_department_4_and_5_scene_and_png_planner(final_script, USER_CATEGORY)

    # 7 & 8. 4 Title/SEO Agents + 4 Thumbnail Judges
    seo_and_thumbnail = run_department_7_and_8_seo_and_thumbnail(topic_report, final_script)

    # Combine Everything into Master Blueprint JSON for Phase 2 Video Engine
    master_blueprint = {
        "topic_analysis": topic_report,
        "spy_research": spy_report,
        "approved_script": final_script,
        "production_plan": production_plan,
        "seo_and_thumbnail": seo_and_thumbnail
    }

    with open("output/master_production_blueprint.json", "w", encoding="utf-8") as f:
        json.dump(master_blueprint, f, ensure_ascii=False, indent=4)
    print("\n[SUCCESS] Master Production Blueprint saved to output/master_production_blueprint.json")

    # Generate Locked Voiceover Audio
    asyncio.run(generate_locked_voiceover(final_script["full_spoken_script_hindi"]))
