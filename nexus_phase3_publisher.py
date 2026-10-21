import os
import json
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ==========================================
# CONFIGURATION & PATHS
# ==========================================
BLUEPRINT_PATH = "output/master_production_blueprint.json"
FINAL_VIDEO_PATH = "output/final/nexus_final_video.mp4"
FINAL_THUMBNAIL_PATH = "output/final/nexus_thumbnail.jpg"

def load_blueprint():
    if not os.path.exists(BLUEPRINT_PATH):
        raise FileNotFoundError(f"Blueprint not found at {BLUEPRINT_PATH}. Run Phase 1 & 2 first.")
    with open(BLUEPRINT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# ==========================================
# 1. YOUTUBE AUTO-UPLOADER (VIDEO + THUMBNAIL + SEO)
# ==========================================
def upload_to_youtube(title, description, tags, video_path, thumbnail_path):
    client_id = os.environ.get("YT_CLIENT_ID")
    client_secret = os.environ.get("YT_CLIENT_SECRET")
    refresh_token = os.environ.get("YT_REFRESH_TOKEN")

    if not all([client_id, client_secret, refresh_token]):
        print("[PUBLISHER - YOUTUBE] Skipping live upload (YT OAuth secrets not added yet). Your final video & thumbnail are fully ready in GitHub Actions Artifacts!")
        return None

    if not os.path.exists(video_path):
        print(f"[PUBLISHER - YOUTUBE] Error: Final video not found at {video_path}")
        return None

    print("[PUBLISHER - YOUTUBE] Authenticating & uploading HD video to YouTube...")
    try:
        creds = Credentials(
            None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret
        )
        youtube = build("youtube", "v3", credentials=creds)

        body = {
            "snippet": {
                "title": title[:100],
                "description": description,
                "tags": tags,
                "categoryId": "24"  # Entertainment / Animation
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }

        media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = request.execute()
        video_id = response["id"]
        print(f"[SUCCESS] YouTube Video Uploaded! Video ID: {video_id}")

        # Upload Custom Viral Thumbnail if exists
        if os.path.exists(thumbnail_path):
            try:
                youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
                ).execute()
                print("[SUCCESS] Custom Viral Thumbnail Applied to YouTube Video!")
            except Exception as thumb_err:
                print(f"[PUBLISHER - YOUTUBE] Thumbnail upload note: {thumb_err}")

        return video_id
    except Exception as e:
        print(f"[PUBLISHER - YOUTUBE] Upload failed due to: {e}")
        return None

# ==========================================
# 2. INSTAGRAM & FACEBOOK GRAPH API AUTO-UPLOADER
# ==========================================
def upload_to_meta_platforms(caption):
    ig_user_id = os.environ.get("IG_USER_ID")
    fb_page_id = os.environ.get("FB_PAGE_ID")
    meta_access_token = os.environ.get("META_ACCESS_TOKEN")
    public_video_url = os.environ.get("PUBLIC_VIDEO_URL")  # Optional hosted artifact URL

    if not meta_access_token:
        print("[PUBLISHER - META] Skipping Instagram/Facebook upload (META_ACCESS_TOKEN not configured).")
        return

    if ig_user_id and public_video_url:
        print("[PUBLISHER - INSTAGRAM] Publishing Reel via Graph API...")
        try:
            create_url = f"https://graph.facebook.com/v21.0/{ig_user_id}/media"
            res = requests.post(create_url, data={
                "media_type": "REELS",
                "video_url": public_video_url,
                "caption": caption,
                "access_token": meta_access_token
            }).json()
            print(f"[PUBLISHER - INSTAGRAM] Response: {res}")
        except Exception as e:
            print(f"[PUBLISHER - INSTAGRAM] Error: {e}")

    if fb_page_id and public_video_url:
        print("[PUBLISHER - FACEBOOK] Publishing Video to Facebook Page...")
        try:
            fb_url = f"https://graph.facebook.com/v21.0/{fb_page_id}/videos"
            res = requests.post(fb_url, data={
                "file_url": public_video_url,
                "description": caption,
                "access_token": meta_access_token
            }).json()
            print(f"[PUBLISHER - FACEBOOK] Response: {res}")
        except Exception as e:
            print(f"[PUBLISHER - FACEBOOK] Error: {e}")

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    blueprint = load_blueprint()
    seo = blueprint["seo_and_thumbnail"]
    
    title = seo.get("locked_viral_title", "Amazing AI Story")
    desc = seo.get("seo_description", "")
    tags = seo.get("viral_tags", ["shorts", "animation", "ai"])
    full_caption = f"{title}\n\n{desc}\n\n" + " ".join([f"#{t.replace(' ', '')}" for t in tags])

    print(f"\n[PHASE 3 PUBLISHER] Preparing release package for title: {title}")
    
    # Run Publishers
    upload_to_youtube(title, full_caption, tags, FINAL_VIDEO_PATH, FINAL_THUMBNAIL_PATH)
    upload_to_meta_platforms(full_caption)
    
    print("[PHASE 3 PUBLISHER] Publishing pipeline execution completed successfully!")
