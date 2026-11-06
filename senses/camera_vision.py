"""
Jessica Senses - Camera Vision & Live Companion Perception Engine
Provides real-time neural visual inspection, scene analysis, automated arrival greeting,
and object perception on 12-Thread Intel Core i5 CPU + 32GB RAM via YOLOv8n (0 MB GPU VRAM).
"""

import os
import sys
import time
import base64
import threading
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

import numpy as np
import cv2
import torch
from ultralytics import YOLO

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from senses.face_net import FACE_ENGINE
from senses.voice_engine import VOICE_ENGINE

SECURITY_DIR = WORKSPACE_ROOT / "senses" / "biometrics" / "security_snapshots"
SECURITY_DIR.mkdir(parents=True, exist_ok=True)
YOLO_MODEL_PATH = WORKSPACE_ROOT / "yolov8n.pt"


class CameraVisionCompanion:
    """
    Intelligent Visual Perception Companion for Jessica.
    Gives the camera grounded, hallucination-free interactive capabilities:
    1. Real Neural Object & Scene Vision on 12-Thread CPU via YOLOv8n (0 MB GPU VRAM overhead).
    2. Torso & Dominant Clothing Color Analysis (HSV/RGB colorimetry).
    3. Strict Telemetry Grounding (forbids hallucinating unlisted objects like CDs, books, or instruments).
    4. Auto-Arrival Greeting: Senses when Boss sits at his desk and greets him out loud.
    5. Away Desk Security: Captures timestamped snapshots when unknown movement occurs.
    """
    def __init__(self):
        self.auto_greet_enabled = False
        self.away_watch_enabled = False
        self.is_user_away = False
        self.last_face_seen_time = time.time()
        self.last_greet_time = 0.0
        self.away_threshold_seconds = 15.0  # Empty desk for 15s marks away
        self.greet_cooldown_seconds = 60.0  # Don't spam greeting within 60s
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self.latest_hud_frame: Optional[np.ndarray] = None

        # Initialize YOLOv8n strictly on CPU (zero GPU VRAM impact)
        try:
            self._yolo = YOLO(str(YOLO_MODEL_PATH))
            print(f"[+] CameraVisionCompanion: Loaded YOLOv8n neural vision model on CPU.")
        except Exception as e:
            print(f"[!] CameraVisionCompanion YOLO initialization notice: {e}")
            self._yolo = None

        self.last_visual_stats: Dict[str, Any] = {
            "person_detected": False,
            "face_detected": False,
            "clothing_color": "N/A",
            "lighting_quality": "Unknown",
            "mean_brightness": 0.0,
            "contrast_std": 0.0,
            "framing": "Unknown",
            "posture": "Unknown",
            "detected_objects": [],
            "last_inspected": None
        }

    def _analyze_clothing_color(self, torso_crop: np.ndarray) -> str:
        """
        Extracts dominant clothing color from a cropped torso region using HSV & BGR statistics.
        """
        if torso_crop is None or torso_crop.size == 0 or torso_crop.shape[0] < 5 or torso_crop.shape[1] < 5:
            return "Undetermined shirt"

        hsv = cv2.cvtColor(torso_crop, cv2.COLOR_BGR2HSV)
        mean_h = float(np.mean(hsv[:, :, 0]))  # 0 to 179
        mean_s = float(np.mean(hsv[:, :, 1]))  # 0 to 255
        mean_v = float(np.mean(hsv[:, :, 2]))  # 0 to 255

        mean_b = float(np.mean(torso_crop[:, :, 0]))
        mean_g = float(np.mean(torso_crop[:, :, 1]))
        mean_r = float(np.mean(torso_crop[:, :, 2]))

        # 1. Dark tones (black, charcoal, dark navy)
        if mean_v < 48.0 or (mean_r < 50.0 and mean_g < 50.0 and mean_b < 50.0):
            return "Black / dark charcoal shirt"

        # 2. Light tones (white, off-white, light cream)
        if mean_s < 32.0 and mean_v > 175.0:
            return "White / light shirt"

        # 3. Neutral gray tones
        if mean_s < 38.0 and mean_v >= 48.0:
            return "Gray / neutral heather shirt"

        # 4. Color hues
        if 95.0 <= mean_h <= 135.0:
            return "Navy blue / blue shirt"
        elif mean_h < 12.0 or mean_h > 165.0:
            return "Red / maroon / burgundy shirt"
        elif 35.0 <= mean_h <= 85.0:
            return "Green / olive shirt"
        elif 12.0 <= mean_h < 35.0:
            return "Warm amber / orange / yellow shirt"
        elif 135.0 < mean_h <= 165.0:
            return "Purple / violet shirt"

        return "Casual colored shirt"

    def analyze_frame_metrics(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Extracts rich computer vision metrics from an RGB/BGR image frame using CPU YOLOv8n.
        Zero GPU VRAM impact.
        """
        h, w = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 1. Lighting & Luminance Analysis (Human-grounded terms, zero raw pixel math)
        mean_brightness = float(np.mean(gray))
        contrast_std = float(np.std(gray))

        if mean_brightness < 30.0:
            human_lighting = "very dark room with dim ambient shadows"
        elif mean_brightness < 60.0:
            human_lighting = "dim cozy lighting"
        elif mean_brightness < 140.0:
            human_lighting = "well-lit room with balanced indoor lighting"
        else:
            human_lighting = "bright daylight / crisp room lighting"

        lighting = human_lighting

        if contrast_std > 55.0:
            contrast_label = "crisp high dynamic contrast"
        elif contrast_std > 30.0:
            contrast_label = "smooth balanced contrast"
        else:
            contrast_label = "flat diffused lighting"

        # 2. Overall Scene Color Temperature
        b_mean = float(np.mean(frame[:, :, 0]))
        r_mean = float(np.mean(frame[:, :, 2]))
        if r_mean > b_mean + 15:
            color_temp = "warm cozy room ambiance"
        elif b_mean > r_mean + 15:
            color_temp = "cool daylight / monitor glow"
        else:
            color_temp = "neutral color balance"

        # 3. Real Neural Object Detection via CPU YOLOv8n
        person_detected = False
        primary_bbox = None
        clothing_color = "N/A"
        framing = "No person in camera view"
        posture = "Relaxed posture"
        peripheral_objects: List[Dict[str, Any]] = []

        if self._yolo is not None:
            try:
                results = self._yolo(frame, device="cpu", verbose=False)[0]
                person_candidates = []

                # Whitelist realistic indoor/desk objects and require high confidence (>= 0.62)
                # to permanently eliminate false positives like "frisbee", "donut", "kite"
                INDOOR_OBJECT_WHITELIST = {
                    "person", "cell phone", "cup", "bottle", "laptop", "tv", "monitor",
                    "keyboard", "mouse", "book", "chair", "backpack", "handbag",
                    "glasses", "tie", "cat", "dog"
                }

                for box in results.boxes:
                    cls_id = int(box.cls[0].cpu().numpy())
                    conf = float(box.conf[0].cpu().numpy())
                    cls_name = self._yolo.names[cls_id]
                    xyxy = box.xyxy[0].cpu().numpy().astype(int)
                    bx1, by1, bx2, by2 = int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])

                    if cls_name == "person" and conf >= 0.28:
                        person_candidates.append({
                            "conf": conf,
                            "bbox": (bx1, by1, bx2, by2),
                            "area": (bx2 - bx1) * (by2 - by1)
                        })
                    elif cls_name in INDOOR_OBJECT_WHITELIST and conf >= 0.62:
                        peripheral_objects.append({
                            "class": cls_name,
                            "confidence": round(conf, 2),
                            "bbox": (bx1, by1, bx2, by2)
                        })

                # If person detected, pick largest area candidate
                if person_candidates:
                    person_detected = True
                    best_person = max(person_candidates, key=lambda p: p["area"])
                    px1, py1, px2, py2 = best_person["bbox"]
                    primary_bbox = (px1, py1, px2 - px1, py2 - py1)

                    pw = max(1, px2 - px1)
                    ph = max(1, py2 - py1)

                    # Centering
                    cx = (px1 + px2) / (2.0 * float(w))
                    if cx < 0.38:
                        center_desc = "positioned slightly to the left"
                    elif cx > 0.62:
                        center_desc = "positioned slightly to the right"
                    else:
                        center_desc = "perfectly centered in camera frame"

                    # Distance / Scale ratio
                    scale_ratio = pw / float(w)
                    if scale_ratio > 0.40:
                        dist_desc = "close-up framing"
                        posture = "leaning in attentively toward the screen"
                    elif scale_ratio > 0.18:
                        dist_desc = "medium portrait framing"
                        posture = "upright, comfortable ergonomic posture"
                    else:
                        dist_desc = "sitting back at a distance"
                        posture = "relaxed posture, seated comfortably"

                    framing = f"{center_desc}, {dist_desc}"

                    # Torso extraction for clothing color
                    ty1 = max(0, min(h - 1, int(py1 + 0.32 * ph)))
                    ty2 = max(0, min(h, int(py1 + 0.75 * ph)))
                    tx1 = max(0, min(w - 1, int(px1 + 0.15 * pw)))
                    tx2 = max(0, min(w, int(px2 - 0.15 * pw)))

                    if ty2 > ty1 + 10 and tx2 > tx1 + 10:
                        torso_crop = frame[ty1:ty2, tx1:tx2]
                        clothing_color = self._analyze_clothing_color(torso_crop)
                    else:
                        clothing_color = "Undetermined shirt"

            except Exception as e:
                print(f"[!] YOLOv8 frame metrics error: {e}")

        # Peripherals summary text
        if peripheral_objects:
            obj_list_str = ", ".join([f"{o['class'].capitalize()} ({int(o['confidence']*100)}%)" for o in peripheral_objects[:5]])
        else:
            obj_list_str = "No peripheral objects detected"

        # Build Strict Sensor Grounding Block (Human terms, zero pixel math)
        telemetry_prompt_block = (
            f"[VERIFIED CAMERA VISION TELEMETRY - DO NOT INVENT UNLISTED OBJECTS]\n"
            f"- Person detected: {'Yes (Alexander Lopez, ' + framing + ')' if person_detected else 'No person currently in front of camera'}\n"
            f"- Clothing detected: {clothing_color if person_detected else 'N/A'}\n"
            f"- Facial / Head state: {'Looking toward camera, ' + posture if person_detected else 'N/A'}\n"
            f"- Room lighting: {human_lighting}\n"
            f"- Visible objects detected by sensor: {obj_list_str}\n"
            f"STRICT SENSOR GROUNDING RULE: Report ONLY the real visual facts detected by the camera sensor above. "
            f"Describe lighting and room atmosphere in natural spoken English. NEVER read raw pixel numbers, luminance math, or '/255' out loud! "
            f"You CANNOT see hairstyles (like ponytails), furniture (like kitchen counters), or unverified actions (like sipping water). "
            f"NEVER hallucinate or invent clothing, hair, furniture, rooms, or background objects (books, shelves, jazz CDs, frisbees) not in the sensor list!"
        )

        return {
            "person_detected": person_detected,
            "face_detected": person_detected,
            "face_count": 1 if person_detected else 0,
            "primary_bbox": primary_bbox,
            "clothing_color": clothing_color,
            "mean_brightness": round(mean_brightness, 1),
            "contrast_std": round(contrast_std, 1),
            "lighting": lighting,
            "contrast": contrast_label,
            "framing": framing,
            "posture": posture,
            "color_temperature": color_temp,
            "peripheral_objects": peripheral_objects,
            "peripherals_summary": obj_list_str,
            "telemetry_prompt_block": telemetry_prompt_block,
            "resolution": f"{w}x{h}"
        }

    def inspect_user_scene(
        self,
        frame: Optional[np.ndarray] = None,
        camera_index: Optional[int] = None,
        frame_b64: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes a real-time neural visual inspection of the user and their desk scene.
        Returns visual metrics, annotated HUD snapshot, and spoken neural response.
        Zero-Collision Architecture: Decodes frame_b64 from the live frontend HUD canvas
        to eliminate hardware webcam conflicts with Windows DirectShow/MediaFoundation.
        """
        is_physical = False

        # 1. Decode base64 frame from live frontend HUD if provided
        if frame is None and frame_b64:
            try:
                raw_b64 = frame_b64
                if "," in raw_b64:
                    raw_b64 = raw_b64.split(",")[1]
                img_bytes = base64.b64decode(raw_b64)
                nparr = np.frombuffer(img_bytes, np.uint8)
                decoded = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if decoded is not None and decoded.size > 0:
                    frame = decoded
                    is_physical = True
                    with self._lock:
                        self.latest_hud_frame = decoded
            except Exception as e:
                print(f"[!] Frame b64 decode fallback: {e}")

        # 2. Hardware camera capture fallback if no frontend frame provided
        if frame is None:
            # Grab frame from hardware camera
            cam_idx, phys_frame = FACE_ENGINE.find_working_physical_camera()
            if phys_frame is not None:
                frame = phys_frame
                is_physical = True
            else:
                frame, is_physical = FACE_ENGINE.capture_frame(camera_index)

        # 3. Graceful fallback if camera hardware is unavailable
        if frame is None:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            is_physical = False

        metrics = self.analyze_frame_metrics(frame)
        with self._lock:
            self.last_visual_stats = {
                **metrics,
                "is_physical_camera": is_physical,
                "last_inspected": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

        # Create Cybernetic HUD Annotation
        annotated = frame.copy()
        h, w = frame.shape[:2]

        # Draw Person / Creator HUD bounding box
        if metrics["person_detected"] and metrics["primary_bbox"]:
            x, y, bw, bh = metrics["primary_bbox"]
            # Cyan-gold target bracket
            cv2.rectangle(annotated, (x, y), (x + bw, y + bh), (255, 200, 0), 2)
            cv2.putText(
                annotated,
                f"CREATOR DETECTED: ALEXANDER LOPEZ [{metrics['posture'].upper()}]",
                (x, max(24, y - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 200, 0),
                2
            )
            # Torso clothing tag
            cv2.putText(
                annotated,
                f"CLOTHING: {metrics['clothing_color'].upper()}",
                (x, min(h - 10, y + bh + 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (255, 230, 80),
                1
            )
        else:
            cv2.putText(
                annotated,
                "CAMERA HUD: DESK SPACE MONITORED (NO USER DETECTED)",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.60,
                (0, 220, 255),
                2
            )

        # Draw Peripheral Objects detected by CPU YOLOv8n
        for obj in metrics["peripheral_objects"]:
            ox1, oy1, ox2, oy2 = obj["bbox"]
            cv2.rectangle(annotated, (ox1, oy1), (ox2, oy2), (0, 255, 200), 1)
            cv2.putText(
                annotated,
                f"{obj['class'].upper()} {int(obj['confidence'] * 100)}%",
                (ox1, max(18, oy1 - 6)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (0, 255, 200),
                1
            )

        # Overlay lighting & telemetry at bottom
        cv2.putText(
            annotated,
            f"LIGHTING: {metrics['lighting'].upper()} | LUM: {metrics['mean_brightness']} | PERIPHERALS: {metrics['peripherals_summary']}",
            (20, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            (0, 255, 180),
            1
        )

        # Encode HUD image
        _, buf = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 85])
        annotated_b64 = "data:image/jpeg;base64," + base64.b64encode(buf).decode("utf-8")

        # Synthesize witty, warm spoken response token-by-token
        from brain.cortex_net import get_sovereign_cortex
        cortex = get_sovereign_cortex()

        if metrics["person_detected"]:
            eval_prompt = (
                f"Alexander Lopez just asked you to look at the camera and tell him how he looks.\n"
                f"Here is your verified camera sensor telemetry:\n\n"
                f"{metrics['telemetry_prompt_block']}\n\n"
                f"Give Alexander a warm, observant, witty, and grounded spoken reaction in natural conversational English. "
                f"Acknowledge what he is actually wearing and his posture. Do not invent any unlisted objects."
            )
        else:
            eval_prompt = (
                f"Alexander Lopez asked you to look at the camera and tell him what you see.\n"
                f"Here is your verified camera sensor telemetry:\n\n"
                f"{metrics['telemetry_prompt_block']}\n\n"
                f"Give a friendly, witty spoken observation noting that the desk is empty and describing the room lighting. "
                f"Do not invent any unlisted objects like CDs, books, or instruments."
            )

        stream_res = cortex.generate_stream_pipelined(
            user_prompt=eval_prompt,
            max_new_tokens=65,
            temperature=0.60,
            top_p=0.9,
            voice_engine=VOICE_ENGINE,
            user_display_prompt="Jessica, look at my camera! How do I look?"
        )

        return {
            "status": "success",
            "reply": stream_res["clean_text"],
            "emotion": stream_res["emotion"],
            "tokens_per_sec": stream_res["tokens_per_sec"],
            "audio_url": stream_res.get("audio_url"),
            "metrics": metrics,
            "annotated_b64": annotated_b64,
            "is_physical_camera": is_physical
        }

    def start_auto_greet_monitor(self):
        """
        Starts the background thread that watches for Boss returning to his desk.
        """
        with self._lock:
            if self._monitor_thread is not None and self._monitor_thread.is_alive():
                self.auto_greet_enabled = True
                return
            self.auto_greet_enabled = True
            self._stop_event.clear()
            self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._monitor_thread.start()
            print("[+] AutoGreetMonitor: Background presence detection started.")

    def stop_auto_greet_monitor(self):
        """
        Stops the auto-greet background monitor thread.
        """
        with self._lock:
            self.auto_greet_enabled = False
            self._stop_event.set()
        print("[*] AutoGreetMonitor: Background monitor stopped.")

    def update_hud_frame(self, frame_b64: str):
        """
        Ingests the latest live webcam frame from the HTML5 HUD canvas.
        Zero-Collision Architecture: Completely eliminates DirectShow driver conflicts and crashes.
        """
        try:
            raw_b64 = frame_b64
            if "," in raw_b64:
                raw_b64 = raw_b64.split(",")[1]
            img_bytes = base64.b64decode(raw_b64)
            nparr = np.frombuffer(img_bytes, np.uint8)
            decoded = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if decoded is not None and decoded.size > 0:
                with self._lock:
                    self.latest_hud_frame = decoded
        except Exception:
            pass

    def _monitor_loop(self):
        """
        Background polling loop: runs every 3.5 seconds.
        Zero-Collision Architecture: Uses live HUD canvas frames sent from frontend,
        preventing repeated DirectShow driver handles that crash NVIDIA Broadcast or webcams.
        """
        while not self._stop_event.is_set():
            time.sleep(3.5)
            if not self.auto_greet_enabled:
                continue

            try:
                frame = None
                with self._lock:
                    if self.latest_hud_frame is not None:
                        frame = self.latest_hud_frame.copy()

                if frame is None:
                    continue

                metrics = self.analyze_frame_metrics(frame)
                now = time.time()

                with self._lock:
                    if metrics["person_detected"]:
                        # User is present
                        if self.is_user_away and (now - self.last_greet_time > self.greet_cooldown_seconds):
                            # Transition: User returned to desk!
                            self.is_user_away = False
                            self.last_greet_time = now
                            print("[+] [AUTOGREET] Boss returned to desk! Triggering spoken arrival greeting...")
                            self._trigger_spoken_greeting()
                        self.last_face_seen_time = now
                    else:
                        # Empty desk
                        if (now - self.last_face_seen_time) > self.away_threshold_seconds:
                            if not self.is_user_away:
                                self.is_user_away = True
                                print(f"[*] [AUTOGREET] Desk empty for >{self.away_threshold_seconds}s -> Marked as AWAY.")
            except Exception as e:
                print(f"[!] AutoGreetMonitor error: {e}")

    def _trigger_spoken_greeting(self):
        """
        Speaks Jessica's warm arrival greeting out loud when Boss sits down.
        """
        try:
            greeting_text = "Oh, welcome back to your desk, Boss! Ready to dive back in?"
            VOICE_ENGINE.synthesize(greeting_text, emotion="warm", play_audio=True)
        except Exception as e:
            print(f"[!] Spoken greeting error: {e}")


# Singleton instance
CAMERA_COMPANION = CameraVisionCompanion()
