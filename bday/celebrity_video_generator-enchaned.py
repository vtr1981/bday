import subprocess
import os
import json
import random
import shutil
import sys
from pathlib import Path
import glob
import datetime
import gc
import time
import signal
import re

def generate_collage_positions(num_images):
    """
    Generate dynamic positions, sizes, rotations, and z-order for photo collage
    Returns list of dicts with x, y, size, rotation for each image
    """
    # Define layout presets for different image counts
    # Increased sizes to fill more vertical space (300-1400px range)
    layouts = {
        1: [  # Single centered image
            {'x': 240, 'y': 500, 'size': 600, 'rotation': 'PI/30', 'z_order': 0}
        ],
        2: [  # Two overlapping images
            {'x': 120, 'y': 400, 'size': 520, 'rotation': '-PI/15', 'z_order': 0},
            {'x': 480, 'y': 550, 'size': 500, 'rotation': 'PI/18', 'z_order': 1}
        ],
        3: [  # Three images in triangle
            {'x': 100, 'y': 280, 'size': 480, 'rotation': '-PI/12', 'z_order': 0},
            {'x': 520, 'y': 320, 'size': 460, 'rotation': 'PI/15', 'z_order': 1},
            {'x': 280, 'y': 880, 'size': 520, 'rotation': '-PI/20', 'z_order': 2}
        ],
        4: [  # Four corners
            {'x': 80, 'y': 250, 'size': 440, 'rotation': '-PI/18', 'z_order': 0},
            {'x': 560, 'y': 280, 'size': 420, 'rotation': 'PI/20', 'z_order': 1},
            {'x': 100, 'y': 850, 'size': 460, 'rotation': 'PI/15', 'z_order': 2},
            {'x': 540, 'y': 920, 'size': 440, 'rotation': '-PI/12', 'z_order': 3}
        ],
        5: [  # Five images with center focus
            {'x': 60, 'y': 240, 'size': 400, 'rotation': '-PI/20', 'z_order': 0},
            {'x': 620, 'y': 220, 'size': 380, 'rotation': 'PI/18', 'z_order': 1},
            {'x': 290, 'y': 550, 'size': 500, 'rotation': '-PI/25', 'z_order': 4},  # Center - highest z
            {'x': 50, 'y': 950, 'size': 420, 'rotation': 'PI/15', 'z_order': 2},
            {'x': 560, 'y': 1020, 'size': 400, 'rotation': '-PI/16', 'z_order': 3}
        ],
        6: [  # Six images scattered
            {'x': 50, 'y': 220, 'size': 380, 'rotation': '-PI/22', 'z_order': 0},
            {'x': 420, 'y': 200, 'size': 400, 'rotation': 'PI/20', 'z_order': 1},
            {'x': 720, 'y': 260, 'size': 360, 'rotation': '-PI/18', 'z_order': 2},
            {'x': 80, 'y': 700, 'size': 420, 'rotation': 'PI/16', 'z_order': 3},
            {'x': 480, 'y': 780, 'size': 400, 'rotation': '-PI/20', 'z_order': 4},
            {'x': 660, 'y': 1080, 'size': 380, 'rotation': 'PI/25', 'z_order': 5}
        ],
        7: [  # Seven images with overlap
            {'x': 40, 'y': 200, 'size': 370, 'rotation': '-PI/25', 'z_order': 0},
            {'x': 360, 'y': 180, 'size': 390, 'rotation': 'PI/22', 'z_order': 1},
            {'x': 680, 'y': 240, 'size': 360, 'rotation': '-PI/18', 'z_order': 2},
            {'x': 70, 'y': 620, 'size': 400, 'rotation': 'PI/20', 'z_order': 3},
            {'x': 430, 'y': 680, 'size': 420, 'rotation': '-PI/15', 'z_order': 4},
            {'x': 120, 'y': 1050, 'size': 380, 'rotation': 'PI/18', 'z_order': 5},
            {'x': 570, 'y': 1120, 'size': 370, 'rotation': '-PI/22', 'z_order': 6}
        ],
        8: [  # Eight images densely packed
            {'x': 30, 'y': 200, 'size': 360, 'rotation': '-PI/28', 'z_order': 0},
            {'x': 340, 'y': 180, 'size': 380, 'rotation': 'PI/25', 'z_order': 1},
            {'x': 660, 'y': 220, 'size': 350, 'rotation': '-PI/20', 'z_order': 2},
            {'x': 60, 'y': 590, 'size': 390, 'rotation': 'PI/22', 'z_order': 3},
            {'x': 410, 'y': 640, 'size': 400, 'rotation': '-PI/18', 'z_order': 4},
            {'x': 730, 'y': 680, 'size': 370, 'rotation': 'PI/20', 'z_order': 5},
            {'x': 100, 'y': 1000, 'size': 380, 'rotation': '-PI/16', 'z_order': 6},
            {'x': 560, 'y': 1070, 'size': 360, 'rotation': 'PI/24', 'z_order': 7}
        ],
        9: [  # Nine images grid-like with variation
            {'x': 20, 'y': 180, 'size': 350, 'rotation': '-PI/30', 'z_order': 0},
            {'x': 330, 'y': 160, 'size': 370, 'rotation': 'PI/28', 'z_order': 1},
            {'x': 650, 'y': 200, 'size': 340, 'rotation': '-PI/22', 'z_order': 2},
            {'x': 50, 'y': 560, 'size': 380, 'rotation': 'PI/24', 'z_order': 3},
            {'x': 380, 'y': 600, 'size': 390, 'rotation': '-PI/20', 'z_order': 4},
            {'x': 710, 'y': 640, 'size': 360, 'rotation': 'PI/18', 'z_order': 5},
            {'x': 80, 'y': 960, 'size': 370, 'rotation': '-PI/25', 'z_order': 6},
            {'x': 410, 'y': 1020, 'size': 360, 'rotation': 'PI/22', 'z_order': 7},
            {'x': 690, 'y': 1080, 'size': 350, 'rotation': '-PI/18', 'z_order': 8}
        ],
        10: [  # Ten images maximum density
            {'x': 20, 'y': 160, 'size': 340, 'rotation': '-PI/32', 'z_order': 0},
            {'x': 310, 'y': 140, 'size': 360, 'rotation': 'PI/30', 'z_order': 1},
            {'x': 630, 'y': 180, 'size': 330, 'rotation': '-PI/25', 'z_order': 2},
            {'x': 800, 'y': 240, 'size': 320, 'rotation': 'PI/22', 'z_order': 3},
            {'x': 40, 'y': 520, 'size': 370, 'rotation': '-PI/28', 'z_order': 4},
            {'x': 360, 'y': 570, 'size': 380, 'rotation': 'PI/20', 'z_order': 5},
            {'x': 680, 'y': 600, 'size': 350, 'rotation': '-PI/18', 'z_order': 6},
            {'x': 60, 'y': 900, 'size': 360, 'rotation': 'PI/24', 'z_order': 7},
            {'x': 380, 'y': 960, 'size': 350, 'rotation': '-PI/22', 'z_order': 8},
            {'x': 650, 'y': 1030, 'size': 340, 'rotation': 'PI/26', 'z_order': 9}
        ]
    }
    
    # Return preset layout or default to 5-image layout if more than 10
    if num_images <= 10:
        return layouts.get(num_images, layouts[5])
    else:
        # If more than 10, use first 10 images with the 10-image layout
        return layouts[10]


def create_page3_collage_filter(valid_known_images, has_celebrity_image, bg_stream, page3_start, page3_end):
    """
    Create FFmpeg filter for Page 3 photo collage with PROPER white Polaroid frames
    Returns list of filter strings and final stream name
    """
    filter_parts = []
    
    if not valid_known_images:
        return filter_parts, bg_stream
    
    # Limit to 10 images max
    num_images = min(len(valid_known_images), 10)
    positions = generate_collage_positions(num_images)
    
    # Sort by z_order to ensure proper layering
    sorted_positions = sorted(enumerate(positions[:num_images]), key=lambda x: x[1]['z_order'])
    
    current_stream = bg_stream
    
    for idx, (original_idx, pos) in enumerate(sorted_positions):
        # Calculate input index - adjusted for page6_bg
        img_idx = 7 if has_celebrity_image else 6
        img_idx += original_idx
        
        # Calculate timing - stagger the appearance
        stagger_delay = 0.15 * idx  # Each image appears 0.15s after previous
        img_start = page3_start + stagger_delay
        img_end = page3_end
        
        # Get image size
        size = pos['size']
        border_width = 25  # White frame thickness
        
        # Calculate inner size (image area inside the white frame)
        inner_size = size - (border_width * 2)
        
        # Simpler approach: Create white-framed image, then rotate
        # This ensures the white frame is visible and no color distortion
        image_filter = (
            f"[{img_idx}:v]"
            f"scale={inner_size}:{inner_size}:force_original_aspect_ratio=decrease,"
            f"pad={inner_size}:{inner_size}:(ow-iw)/2:(oh-ih)/2:color=black,"  # Center image in inner area
            f"pad={size}:{size}:{border_width}:{border_width}:color=white,"  # Add solid white frame
            f"rotate={pos['rotation']}:c=none:ow='hypot(iw,ih)':oh='hypot(iw,ih)'"  # Rotate with auto-size
            f"[known{original_idx}]"
        )
        
        # Overlay with enable condition using escaped commas
        overlay_filter = (
            f"{current_stream}[known{original_idx}]"
            f"overlay={pos['x']}:{pos['y']}:"
            f"enable='between(t\\,{img_start}\\,{img_end})'"
            f"[known_overlay{idx}]"
        )
        
        # Combine both filters with semicolon
        combined_filter = f"{image_filter};{overlay_filter}"
        filter_parts.append(combined_filter)
        
        current_stream = f"[known_overlay{idx}]"
    
    return filter_parts, current_stream


# Global flag for graceful shutdown
SHUTDOWN_REQUESTED = False

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    global SHUTDOWN_REQUESTED
    print("\n\nSHUTDOWN REQUESTED - Will stop after current video completes...")
    SHUTDOWN_REQUESTED = True

# Register signal handler
signal.signal(signal.SIGINT, signal_handler)

def load_celebrity_events(events_json_path):
    """Load celebrity events from JSON file"""
    try:
        with open(events_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
        return []
        
    except Exception as e:
        print(f"Error loading celebrity events: {e}")
        return []

def get_music_files(music_dir):
    """Get list of MP3 files from the music directory"""
    music_extensions = ['*.mp3', '*.wav', '*.m4a', '*.aac']
    music_files = []
    
    for extension in music_extensions:
        pattern = os.path.join(music_dir, extension)
        music_files.extend(glob.glob(pattern))
    
    return music_files

def get_background_media(media_dir):
    """Get list of image/video files from the specified directory"""
    extensions = ['*.mp4', '*.avi', '*.mov', '*.mkv', '*.jpg', '*.jpeg', '*.png', '*.webp']
    media_files = []
    
    for extension in extensions:
        pattern = os.path.join(media_dir, extension)
        media_files.extend(glob.glob(pattern))
    
    return media_files

def load_processing_log(log_path):
    """Load processing log to track completed events"""
    try:
        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "processed_link_ids": [],
            "skipped_records": [],
            "last_updated": "",
            "music_index": 0,
            "background_index": 0,
            "page1_bg_index": 0,
            "page2_bg_index": 0,
            "page5_bg_index": 0,
            "page6_bg_index": 0,
            "page1_bg_used": [],
            "page2_bg_used": [],
            "page5_bg_used": [],
            "page6_bg_used": []
        }
    except Exception as e:
        print(f"Error loading processing log: {e}")
        return {
            "processed_link_ids": [],
            "skipped_records": [],
            "last_updated": "",
            "music_index": 0,
            "background_index": 0,
            "page1_bg_index": 0,
            "page2_bg_index": 0,
            "page5_bg_index": 0,
            "page6_bg_index": 0,
            "page1_bg_used": [],
            "page2_bg_used": [],
            "page5_bg_used": [],
            "page6_bg_used": []
        }

def save_processing_log(log_path, processed_link_ids, skipped_records, music_index, background_index, 
                       page1_bg_index, page2_bg_index, page5_bg_index, page6_bg_index,
                       page1_bg_used, page2_bg_used, page5_bg_used, page6_bg_used):
    """Save processing log"""
    try:
        log_data = {
            "processed_link_ids": processed_link_ids,
            "skipped_records": skipped_records,
            "last_updated": datetime.datetime.now().isoformat(),
            "music_index": music_index,
            "background_index": background_index,
            "page1_bg_index": page1_bg_index,
            "page2_bg_index": page2_bg_index,
            "page5_bg_index": page5_bg_index,
            "page6_bg_index": page6_bg_index,
            "page1_bg_used": page1_bg_used,
            "page2_bg_used": page2_bg_used,
            "page5_bg_used": page5_bg_used,
            "page6_bg_used": page6_bg_used
        }
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving processing log: {e}")

def is_valid_record(record):
    """Check if record has valid birthday (not N/A)"""
    birthday = record.get('birthday', 'N/A')
    return birthday != 'N/A' and birthday.strip() != ''

def is_duplicate_record(record, processed_link_ids):
    """Check if link_ID already processed"""
    link_id = record.get('link_ID', '')
    return link_id in processed_link_ids

def wrap_text_to_lines(text, max_chars=25):
    """Split text into lines with maximum character limit"""
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        if not current_line:
            current_line = word
            continue
        
        test_line = current_line + " " + word
        if len(test_line) > max_chars:
            lines.append(current_line)
            current_line = word
        else:
            current_line = test_line
    
    if current_line:
        lines.append(current_line)
    
    return lines

def get_system_font_path():
    """Get font path for different systems"""
    import platform
    system = platform.system().lower()
    
    if system == 'windows':
        fonts = [
            r"C\:/Windows/Fonts/impact.ttf",
            r"C\:/Windows/Fonts/georgia.ttf",
            r"C\:/Windows/Fonts/arialbd.ttf",
        ]
        for font in fonts:
            check_path = font.replace(r'C\:/', 'C:/')
            if os.path.exists(check_path):
                return font
        return r"C\:/Windows/Fonts/arial.ttf"
    elif system == 'darwin':
        return "/System/Library/Fonts/Helvetica.ttc"
    else:
        return "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def get_vibrant_colors():
    """Get vibrant colors for text backgrounds"""
    return [
        '#FF1744',  # Vibrant Red
        '#FF6D00',  # Vibrant Orange
        '#00C853',  # Vibrant Green
        '#00B8D4',  # Vibrant Cyan
        '#D500F9',  # Vibrant Purple
        '#FFD600',  # Vibrant Yellow
        '#FF4081',  # Vibrant Pink
        '#00E676',  # Vibrant Light Green
        '#2979FF',  # Vibrant Blue
        '#FF9100'   # Vibrant Amber
    ]

def get_random_segment_title(segment_index):
    """Get random title for each segment"""
    segment_titles = {
        0: ["Quick Bio", "Fast Facts", "Meet Clara"],
        1: ["Career Highlights", "Rising Star", "On Screen"],
        2: ["Her Journey", "Career Path", "Talent Watch"]
    }
    
    if segment_index in segment_titles:
        return random.choice(segment_titles[segment_index])
    return f"Segment {segment_index + 1}"

def get_random_unused_file(file_list, used_list):
    """
    Get a random file from file_list that hasn't been used yet.
    Once all files are used, reset and start over.
    Returns: (selected_file, updated_used_list)
    """
    if not file_list:
        return None, used_list
    
    # Get list of unused files
    unused_files = [f for f in file_list if f not in used_list]
    
    # If all files have been used, reset the used list
    if not unused_files:
        used_list = []
        unused_files = file_list.copy()
    
    # Pick a random unused file
    selected_file = random.choice(unused_files)
    
    # Add to used list
    updated_used_list = used_list + [selected_file]
    
    return selected_file, updated_used_list


def cleanup_temp_files(temp_files):
    """Safely cleanup temporary files"""
    for temp_file in temp_files:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                break
            except:
                if attempt < max_retries - 1:
                    time.sleep(0.5)
                else:
                    print(f"Warning: Could not remove temp file {temp_file}")

def calculate_celebrity_overlay():
    """
    Calculate overlay position and scale for celebrity image.
    """
    print("Using static centered position for celebrity image.")
    target_width = 1080 
    image_size = 700 
    overlay_x = (target_width - image_size) // 2
    overlay_y = 300
    print(f"Celebrity image (base): size={image_size}x{image_size}, position=({overlay_x}, {overlay_y})")
    return (image_size, image_size, overlay_x, overlay_y)


def get_text_design_style(force_design=None):
    """Always generate unlimited random designs"""
    return 0  # Unlimited mode


def generate_unlimited_box_design():
    """Generate completely unique random box design with SAFE BOUNDARIES
    
    Returns dict with randomized parameters that guarantee text fits in 1080x1920 frame
    """
    
    # 15 vibrant color palettes
    color_palettes = [
        ['#FF1744', '#FF6D00', '#00C853', '#00B8D4', '#D500F9', '#FFD600', '#FF4081'],  # Vibrant
        ['#E91E63', '#9C27B0', '#673AB7', '#3F51B5', '#2196F3', '#03A9F4', '#00BCD4'],  # Purple-Blue
        ['#FF5722', '#FF9800', '#FFC107', '#FFEB3B', '#CDDC39', '#8BC34A', '#4CAF50'],  # Warm-Green
        ['#F44336', '#E91E63', '#9C27B0', '#673AB7', '#3F51B5', '#2196F3', '#00BCD4'],  # Rainbow
        ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE'],  # Pastel
        ['#00E676', '#76FF03', '#C6FF00', '#FFEA00', '#FFC400', '#FF9100', '#FF3D00'],  # Neon
        ['#FF0080', '#FF8C00', '#FFD700', '#00FF00', '#00CED1', '#1E90FF', '#9400D3'],  # Electric
        ['#FF1493', '#FF69B4', '#FFB6C1', '#FFA500', '#FFD700', '#ADFF2F', '#7FFF00'],  # Pink-Yellow
        ['#8B00FF', '#9D00FF', '#B026FF', '#C752FF', '#DA70D6', '#EE82EE', '#FF00FF'],  # Purple
        ['#00FFFF', '#00E5FF', '#00B8D4', '#0091EA', '#2979FF', '#3D5AFE', '#651FFF'],  # Cyan-Blue
        ['#FFEB3B', '#FFC107', '#FF9800', '#FF5722', '#F44336', '#E91E63', '#9C27B0'],  # Fire
        ['#76FF03', '#64DD17', '#00E676', '#1DE9B6', '#00BFA5', '#00ACC1', '#0097A7'],  # Green-Cyan
        ['#FF80AB', '#FF4081', '#F50057', '#C51162', '#AD1457', '#880E4F', '#4A148C'],  # Deep Pink
        ['#FFFF00', '#FFD600', '#FFAB00', '#FF6D00', '#DD2C00', '#BF360C', '#3E2723'],  # Yellow-Brown
        ['#00E5FF', '#18FFFF', '#76FF03', '#C6FF00', '#EEFF41', '#FFFF00', '#FFD600']   # Bright
    ]
    
    # Random parameters with SAFE ranges
    design = {
        'palette': random.choice(color_palettes),
        'border_size': random.choice([18, 20, 22, 25, 28]),  # Box thickness (safe range)
        'base_angle': random.uniform(-4, 4),  # Base rotation angle (safe ±4°)
        'angle_type': random.choice(['fixed', 'slight_vary', 'alternate', 'per_line']),
        'uppercase': random.choice([True, False]),
        'spacing': random.randint(125, 138),  # SAFE spacing to fit 8-10 lines
        'fade_speed': random.choice([150, 200, 250]),
        'title_y': 280,  # Fixed safe title position
        'start_y': 450,  # Fixed safe start position for lines
        'max_y': 1650,  # STRICT maximum Y position (stays in frame)
    }
    
    return design


def create_ass_subtitles(lines_data, output_path, video_width=1080, video_height=1920):
    """Create ASS subtitle file with vibrant colored backgrounds and no black boxes"""
    
    # Vibrant colors for different elements
    vibrant_colors = get_vibrant_colors()
    
    # ASS file header with proper styling
    # Note: ASS Colors are &H<Alpha><Blue><Green><Red>
    # For backgrounds, we'll use vibrant colors with slight transparency
    ass_content = f"""[Script Info]
Title: Celebrity Bio Subtitles
ScriptType: v4.00+
WrapStyle: 0
PlayResX: {video_width}
PlayResY: {video_height}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Page1Name1,Impact,110,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,8,0,5,10,10,10,1
Style: Page1Name2,Impact,110,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,8,0,5,10,10,10,1
Style: Page1Name3,Impact,110,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,8,0,5,10,10,10,1

Style: Title,Impact,120,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,8,0,5,10,10,10,1
Style: Page3Title,Impact,120,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,8,0,5,10,10,10,1
Style: Engagement,Impact,120,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,8,0,5,10,10,10,1

Style: Line1,Impact,90,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,8,0,5,10,10,10,1
Style: Line2,Impact,90,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,8,0,5,10,10,10,1
Style: Line3,Impact,90,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,8,0,5,10,10,10,1
Style: Line4,Impact,90,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,8,0,5,10,10,10,1
Style: Line5,Impact,90,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,8,0,5,10,10,10,1
Style: Line6,Impact,90,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,8,0,5,10,10,10,1
Style: Line7,Impact,90,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,8,0,5,10,10,10,1
Style: Line8,Impact,90,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,8,0,5,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    
    def format_time(seconds):
        """Convert seconds to ASS time format (h:mm:ss.cc)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}:{minutes:02d}:{secs:05.2f}"
    
    # Add all subtitle events
    for line_data in lines_data:
        start_time = format_time(line_data['start'])
        end_time = format_time(line_data['end'])
        style = line_data['style']
        text = line_data['text']
        y_pos = line_data.get('y_pos', 0)
        
        # Get color and fade tags
        fade_tag = line_data.get('fade_tag', '{\\fad(250,0)}')
        color_tag = line_data.get('color_tag', '')
        
        # Position text with \pos tag
        if y_pos > 0:
            pos_tag = f"{{\\pos({video_width//2},{y_pos})}}"
        else:
            pos_tag = ""
        
        ass_content += f"Dialogue: 0,{start_time},{end_time},{style},,0,0,0,,{pos_tag}{fade_tag}{color_tag}{text}\n"
    
    # Write ASS file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(ass_content)
    
    return output_path


def create_celebrity_video(event_data, background_media_path, music_path, output_path, page1_background_path, page2_background_path, page5_background_path, page6_background_path, resolution='HD', force_design=None):
    """Create celebrity bio video with dynamic timing based on content
    
    Args:
        resolution: 'HD' for 1080x1920 or '4K' for 2160x3840
        force_design: If provided (1-5), force this specific text design instead of random
    """
    
    temp_files = []
    process = None
    
    try:
        # Select text design style for this video (1-5)
        text_design = get_text_design_style(force_design)
        print(f"Using Text Design Style {text_design} for pages 2-4")
        
        # Set resolution based on choice
        if resolution == '4K':
            video_width = 2160
            video_height = 3840
            print("Creating 4K video (2160x3840)...")
        else:
            video_width = 1080
            video_height = 1920
            print("Creating HD video (1080x1920)...")
        
        print("Creating celebrity bio video...")
        
        # Extract data
        name = event_data.get('name', 'Unknown')
        birthday = event_data.get('birthday', 'N/A')
        about = event_data.get('about', '')
        segments = event_data.get('segments', [])
        image_path = event_data.get('image_path', '')
        known_imgpath = event_data.get('known_imgpath', [])
        youtube_title = event_data.get('youtube_title', '').strip()
        youtube_description = event_data.get('youtube_description', '').strip()
        
        # Validate segments
        valid_segments = [seg for seg in segments if seg.get('lines', [])]
        
        # Helper function to clean text for subtitles
        def clean_text_for_subtitles(text):
            """Clean text for ASS subtitles"""
            text = text.replace('\\', '\\\\')
            text = text.replace('{', '\\{')
            text = text.replace('}', '\\}')
            return text
        
        # CALCULATE DYNAMIC TIMING
        reading_time_per_line = 2.0
        line_gap = 0.3
        
        total_typing_time = 0
        segment_timing_info = []
        
        for seg_idx, segment in enumerate(valid_segments[:3]):
            # Use random title instead of segment name
            random_title = get_random_segment_title(seg_idx)
            lines = segment.get('lines', [])
            
            all_wrapped = []
            for line in lines:
                all_wrapped.extend(wrap_text_to_lines(line, max_chars=25))
            
            segment_lines = all_wrapped[:8]
            
            seg_typing_time = 0
            for line in segment_lines:
                seg_typing_time += 0.5 + line_gap
            
            seg_typing_time += reading_time_per_line
            
            segment_timing_info.append({
                'name': random_title,
                'lines': segment_lines,
                'duration': seg_typing_time
            })
            total_typing_time += seg_typing_time
        
        # Dynamic page durations
        page1_duration = 5
        page2_duration = max(15, total_typing_time + 2)
        page3_duration = 7
        page4_duration = 6
        
        total_duration = page1_duration + page2_duration + page3_duration + page4_duration
        
        page2_start = page1_duration
        page2_end = page2_start + page2_duration
        page3_start = page2_end
        page3_end = page3_start + page3_duration
        page4_start = page3_end
        page4_end = page4_start + page4_duration
        
        print(f"Name: {name}")
        print(f"Birthday: {birthday}")
        print(f"Valid segments: {len(valid_segments)}")
        print(f"Resolution: {video_width}x{video_height}")
        print(f"Dynamic timing:")
        print(f"  Page 1: 0-{page1_duration}s")
        print(f"  Page 2: {page2_start}-{page2_end}s")
        print(f"  Page 3: {page3_start}-{page3_end}s (Also Known For)")
        print(f"  Page 4: {page4_start}-{page4_end}s")
        print(f"  Total: {total_duration}s")
        
        font_path = get_system_font_path()
        font_param = f"fontfile={font_path}"
        
        print(f"Font path: {font_path}")
        
        page1_ext = os.path.splitext(page1_background_path)[1].lower()
        is_page1_image = page1_ext in ['.jpg', '.jpeg', '.png', '.webp']
        
        # Get vibrant colors
        vibrant_colors = get_vibrant_colors()
        
        # All text is now handled in ASS subtitles with colored backgrounds
        name_lines = wrap_text_to_lines(name, max_chars=25)
        page3_title = "Also Known For..."
        
        # Pre-process audio
        temp_audio = f"temp_audio_{os.getpid()}.aac"
        temp_files.append(temp_audio)
        
        audio_cmd = [
            'ffmpeg', '-y', '-stream_loop', '-1', '-i', music_path,
            '-t', str(total_duration), '-c:a', 'aac', '-b:a', '128k', temp_audio
        ]
        
        subprocess.run(audio_cmd, capture_output=True, timeout=30)
        
        # BUILD ASS SUBTITLE FILE with resolution-adjusted positions
        subtitle_lines = []
        
        # Scale factor for 4K (2x for positions and sizes)
        scale_factor = 2.0 if resolution == '4K' else 1.0
        
        # Adjust font sizes for 4K
        if resolution == '4K':
            # Font sizes will be handled by ASS at double resolution
            name_font_size = 220
            title_font_size = 240
            line_font_size = 180
        else:
            name_font_size = 110
            title_font_size = 120
            line_font_size = 90
        
        # =============== PAGE 2, 3, 4 WITH UNLIMITED RANDOM BOX DESIGNS ===============
        # Generate unique random box design for THIS video
        box_design = generate_unlimited_box_design()
        
        print(f"✨ Generated UNLIMITED random box design:")
        print(f"   - Color palette: {len(box_design['palette'])} vibrant colors")
        print(f"   - Border: {box_design['border_size']}px thick boxes")
        print(f"   - Base angle: {box_design['base_angle']:.2f}°")
        print(f"   - Angle type: {box_design['angle_type']}")
        print(f"   - Text case: {'UPPERCASE' if box_design['uppercase'] else 'Mixed'}")
        print(f"   - Spacing: {box_design['spacing']}px (SAFE - fits in frame)")
        
        current_time = page2_start + 0.5
        color_index = 0
        
        for seg_idx, seg_info in enumerate(segment_timing_info):
            seg_name = clean_text_for_subtitles(seg_info['name'])
            segment_lines = seg_info['lines']
            
            seg_start = current_time
            seg_end = min(current_time + seg_info['duration'], page2_end)
            
            # === TITLE with random box design ===
            title_color = box_design['palette'][color_index % len(box_design['palette'])]
            color_index += 1
            r = int(title_color[1:3], 16)
            g = int(title_color[3:5], 16)
            b = int(title_color[5:7], 16)
            
            # Calculate title angle
            if box_design['angle_type'] == 'fixed':
                title_angle = box_design['base_angle']
            else:
                title_angle = box_design['base_angle'] + random.uniform(-0.5, 0.5)
            
            # Build title with thick border (creates colored box background)
            page2_title_tag = f"{{\\fad({box_design['fade_speed']},0)\\bord{box_design['border_size']}\\shad0\\frz{title_angle:.1f}}}"
            title_color_tag = f"{{\\3c&H{b:02X}{g:02X}{r:02X}&}}"
            
            display_text = seg_name.upper() if box_design['uppercase'] else seg_name
            
            subtitle_lines.append({
                'start': seg_start,
                'end': seg_end,
                'style': 'Title',
                'text': display_text,
                'y_pos': int(box_design['title_y'] * scale_factor),
                'fade_tag': page2_title_tag,
                'color_tag': title_color_tag
            })
            
            # === LINES with random box designs ===
            y = int(box_design['start_y'] * scale_factor)
            line_time = seg_start + 0.3
            max_y_scaled = int(box_design['max_y'] * scale_factor)
            
            for line_idx, line_text in enumerate(segment_lines):
                if not line_text.strip():
                    continue
                
                line_start_time = line_time
                display_until = seg_end
                
                # CRITICAL: Stop if we'd go beyond safe boundary
                if line_start_time >= seg_end or y > max_y_scaled:
                    break
                
                # Get line color from palette
                line_color = box_design['palette'][color_index % len(box_design['palette'])]
                color_index += 1
                r = int(line_color[1:3], 16)
                g = int(line_color[3:5], 16)
                b = int(line_color[5:7], 16)
                
                # Calculate line angle based on angle type
                if box_design['angle_type'] == 'fixed':
                    line_angle = box_design['base_angle']
                elif box_design['angle_type'] == 'slight_vary':
                    line_angle = box_design['base_angle'] + random.uniform(-0.8, 0.8)
                elif box_design['angle_type'] == 'alternate':
                    line_angle = box_design['base_angle'] * (1 if line_idx % 2 == 0 else -1)
                else:  # per_line
                    line_angle = random.uniform(-4, 4)
                
                # Build line with colored box (slightly smaller border than title)
                line_border = max(15, box_design['border_size'] - 3)
                fade_tag = f"{{\\fad({box_design['fade_speed']},0)\\bord{line_border}\\shad0\\frz{line_angle:.1f}}}"
                line_color_tag = f"{{\\3c&H{b:02X}{g:02X}{r:02X}&}}"
                
                style_name = f'Line{(line_idx % 8) + 1}'
                display_line = clean_text_for_subtitles(line_text)
                if box_design['uppercase']:
                    display_line = display_line.upper()
                
                subtitle_lines.append({
                    'start': line_start_time,
                    'end': display_until,
                    'style': style_name,
                    'text': display_line,
                    'y_pos': y,
                    'fade_tag': fade_tag,
                    'color_tag': line_color_tag
                })
                
                # Move to next line with SAFE spacing
                y += int(box_design['spacing'] * scale_factor)
                line_time += 0.45
            
            current_time = seg_end + 0.5
        
        # =============== PAGE 3 TITLE WITH MATCHING BOX DESIGN ===============
        page3_color = box_design['palette'][0]
        r = int(page3_color[1:3], 16)
        g = int(page3_color[3:5], 16)
        b = int(page3_color[5:7], 16)
        
        # Use same style parameters for consistency
        page3_border = box_design['border_size'] + 3
        page3_angle = box_design['base_angle']
        
        page3_fade_tag = f"{{\\fad(300,300)\\bord{page3_border}\\shad0\\frz{page3_angle:.1f}}}"
        page3_color_tag = f"{{\\3c&H{b:02X}{g:02X}{r:02X}&}}"
        
        page3_display = page3_title.upper() if box_design['uppercase'] else page3_title
        
        subtitle_lines.append({
            'start': page3_start,
            'end': page3_end,
            'style': 'Page3Title',
            'text': clean_text_for_subtitles(page3_display),
            'y_pos': int(150 * scale_factor),
            'fade_tag': page3_fade_tag,
            'color_tag': page3_color_tag
        })
        
        # =============== PAGE 1 DATA (UNCHANGED - Celebrity Name) ===============
        name_line_height = int(130 * scale_factor)
        name_start_y = int(1400 * scale_factor)
        page1_colors = ['#FF1744', '#FF6D00', '#00C853']
        angles = [-3, 3, -2]

        for idx, line in enumerate(name_lines):
            style = f'Page1Name{(idx % 3) + 1}'
            y_pos = name_start_y + (idx * name_line_height)
            color = page1_colors[idx % len(page1_colors)]
            
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            
            angle_tag = f"{{\\frz{angles[idx % len(angles)]}}}"
            shad_value = int(30 * scale_factor)
            color_tag = f"{{\\3c&H{b:02X}{g:02X}{r:02X}&\\shad{shad_value}}}"
            fade_tag = '{\\fad(250,0)}'
            
            subtitle_lines.append({
                'start': 1.0,
                'end': page1_duration,
                'style': style,
                'text': clean_text_for_subtitles(line),
                'y_pos': y_pos,
                'fade_tag': f"{fade_tag}{angle_tag}",
                'color_tag': color_tag
            })
        
        # Page 4: No engagement text (UNCHANGED)
        
        # Create ASS subtitle file with resolution-specific settings
        ass_subtitle_path = f"temp_subtitles_{os.getpid()}.ass"
        create_ass_subtitles_scaled(subtitle_lines, ass_subtitle_path, video_width, video_height, resolution)
        temp_files.append(ass_subtitle_path)
        
        print(f"Created ASS subtitle file with {len(subtitle_lines)} text entries (Design Style {text_design})")
        
        # Build FFmpeg command
        cmd = ['ffmpeg', '-y']
        
        # Input 0: Page 1 background
        if is_page1_image:
            cmd.extend(['-loop', '1', '-i', page1_background_path])
        else:
            cmd.extend(['-stream_loop', '-1', '-i', page1_background_path])
        
        # Input 1: Regular background for Page 4
        bg_ext = os.path.splitext(background_media_path)[1].lower()
        is_image = bg_ext in ['.jpg', '.jpeg', '.png', '.webp']
        
        if is_image:
            cmd.extend(['-loop', '1', '-i', background_media_path])
        else:
            cmd.extend(['-stream_loop', '-1', '-i', background_media_path])
        
        # Input 2: Audio
        cmd.extend(['-i', temp_audio])
        
        # Input 3: Page 2 Background
        page2_ext = os.path.splitext(page2_background_path)[1].lower()
        is_page2_image = page2_ext in ['.jpg', '.jpeg', '.png', '.webp']
        if is_page2_image:
            cmd.extend(['-loop', '1', '-i', page2_background_path])
        else:
            cmd.extend(['-stream_loop', '-1', '-i', page2_background_path])
        
        # Input 4: Page 5 Background
        page5_ext = os.path.splitext(page5_background_path)[1].lower()
        is_page5_image = page5_ext in ['.jpg', '.jpeg', '.png', '.webp']
        if is_page5_image:
            cmd.extend(['-loop', '1', '-i', page5_background_path])
        else:
            cmd.extend(['-stream_loop', '-1', '-i', page5_background_path])
        
        # Input 5: Page 6 Background
        page6_ext = os.path.splitext(page6_background_path)[1].lower()
        is_page6_image = page6_ext in ['.jpg', '.jpeg', '.png', '.webp']
        if is_page6_image:
            cmd.extend(['-loop', '1', '-i', page6_background_path])
        else:
            cmd.extend(['-stream_loop', '-1', '-i', page6_background_path])
        
        # Input 6: Celebrity profile image
        input_idx = 6
        has_celebrity_image = image_path and os.path.exists(image_path)
        if has_celebrity_image:
            cmd.extend(['-i', image_path])
            input_idx += 1
        
        # Input 7+: Known images
        valid_known_images = []
        for known_img in known_imgpath:
            if os.path.exists(known_img):
                cmd.extend(['-i', known_img])
                valid_known_images.append(known_img)
                input_idx += 1
        
        # Build filter complex with resolution
        filter_parts = []
        
        # PAGE 1 BACKGROUND
        page1_filter = (
            f"[0:v]scale={video_width}:{video_height}:force_original_aspect_ratio=increase,"
            f"crop={video_width}:{video_height},fps=30,setsar=1[page1_bg]"
        )
        filter_parts.append(page1_filter)
        
        # PAGE 2 BACKGROUND
        if is_page2_image:
            page2_bg_filter = (
                f"[3:v]scale={video_width}:{video_height}:force_original_aspect_ratio=increase,"
                f"crop={video_width}:{video_height},gblur=sigma=2,eq=brightness=-0.1:contrast=1.1,"
                "fps=30,setsar=1[page2_bg]"
            )
        else:
            page2_bg_filter = (
                f"[3:v]scale={video_width}:{video_height}:force_original_aspect_ratio=increase,"
                f"crop={video_width}:{video_height},"
                "gblur=sigma=2,eq=brightness=-0.1:contrast=1.1,"
                "fps=30[page2_bg]"
            )
        filter_parts.append(page2_bg_filter)
        
        # PAGE 5 BACKGROUND
        if is_page5_image:
            page5_bg_filter = (
                f"[4:v]scale={video_width}:{video_height}:force_original_aspect_ratio=increase,"
                f"crop={video_width}:{video_height},gblur=sigma=3,eq=brightness=-0.2:contrast=1.1,"
                "fps=30,setsar=1[page5_bg]"
            )
        else:
            page5_bg_filter = (
                f"[4:v]scale={video_width}:{video_height}:force_original_aspect_ratio=increase,"
                f"crop={video_width}:{video_height},"
                "gblur=sigma=3,eq=brightness=-0.2:contrast=1.1,"
                "fps=30[page5_bg]"
            )
        filter_parts.append(page5_bg_filter)
        
        # PAGE 6 BACKGROUND
        if is_page6_image:
            page6_bg_filter = (
                f"[5:v]scale={video_width}:{video_height}:force_original_aspect_ratio=increase,"
                f"crop={video_width}:{video_height},gblur=sigma=3,eq=brightness=-0.2:contrast=1.1,"
                "fps=30,setsar=1[page6_bg]"
            )
        else:
            page6_bg_filter = (
                f"[5:v]scale={video_width}:{video_height}:force_original_aspect_ratio=increase,"
                f"crop={video_width}:{video_height},"
                "gblur=sigma=3,eq=brightness=-0.2:contrast=1.1,"
                "fps=30[page6_bg]"
            )
        filter_parts.append(page6_bg_filter)
        
        # Merge backgrounds
        bg_merge_filter = (
            f"[page1_bg][page2_bg]xfade=transition=fade:duration=0.5:offset={page1_duration - 0.5}[bg_1_2];"
            f"[bg_1_2][page5_bg]xfade=transition=fade:duration=0.5:offset={page2_end - 0.5}[bg_1_2_5];"
            f"[bg_1_2_5][page6_bg]xfade=transition=fade:duration=0.5:offset={page3_end - 0.5}[bg_merged]"
        )
        filter_parts.append(bg_merge_filter)
        
        # PAGE 1: Celebrity Image (scaled for resolution)
        if has_celebrity_image:
            img_size = int(700 * scale_factor)
            overlay_x = (video_width - img_size) // 2
            overlay_y = int(650 * scale_factor)
            border_thickness = int(20 * scale_factor)
            
            celebrity_img_filter = (
                f"[6:v]scale={img_size}:{img_size}:force_original_aspect_ratio=increase,"
                f"crop={img_size}:{img_size},"
                f"colorlevels=rimax=0.9:gimax=0.9:bimax=0.9,"
                f"vignette=0.5,"
                f"drawbox=x=0:y=0:w={img_size}:h={img_size}:color=white:t={border_thickness},"
                "format=rgba[celeb_img];"
                f"[bg_merged][celeb_img]overlay={overlay_x}:{overlay_y}:enable='between(t\\,0.5\\,{page1_duration})'"
                f"[bg_with_celeb]"
            )
            
            filter_parts.append(celebrity_img_filter)
            bg_stream = "[bg_with_celeb]"
        else:
            bg_stream = "[bg_merged]"
        
        # PAGE 3: Known images with scaled Polaroid frames
        if valid_known_images:
            page3_filters, bg_stream = create_page3_collage_filter_scaled(
                valid_known_images, 
                has_celebrity_image, 
                bg_stream, 
                page3_start, 
                page3_end,
                scale_factor
            )
            filter_parts.extend(page3_filters)
        
        final_stream = bg_stream
        
        # Add ASS subtitles
        ass_path_escaped = ass_subtitle_path.replace('\\', '/').replace(':', '\\:')
        subtitle_filter = f"{final_stream}subtitles='{ass_path_escaped}'[final]"
        filter_parts.append(subtitle_filter)
        
        # Build complete filter
        filter_complex = ";".join(filter_parts)
        
        print(f"Filter complex length: {len(filter_complex)} characters")
        
        # Execute FFmpeg with resolution-appropriate settings
        if resolution == '4K':
            # 4K encoding settings
            cmd.extend([
                '-filter_complex', filter_complex,
                '-map', '[final]', '-map', '2:a',
                '-t', str(total_duration),
                '-c:v', 'libx264', '-preset', 'slow', '-crf', '17',
                '-c:a', 'aac', '-b:a', '192k',
                '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart'
            ])
        else:
            # HD encoding settings
            cmd.extend([
                '-filter_complex', filter_complex,
                '-map', '[final]', '-map', '2:a',
                '-t', str(total_duration),
                '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
                '-c:a', 'aac', '-b:a', '128k',
                '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart'
            ])
        
        if youtube_title:
            cmd.extend(['-metadata', f'title={youtube_title}'])
        if youtube_description:
            cmd.extend(['-metadata', f'description={youtube_description}'])
        
        cmd.append(str(output_path))
        
        # Execute
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        stdout, stderr = process.communicate(timeout=900)  # Increased timeout for 4K
        
        if process.returncode == 0 and os.path.exists(output_path):
            print(f"SUCCESS: Video created ({os.path.getsize(output_path) / 1024 / 1024:.2f} MB)")
            return True
        else:
            print(f"FAILED: Return code {process.returncode}")
            print(f"FFMPEG STDERR: {stderr[-2000:]}")
            return False
            
    except Exception as e:
        if isinstance(e, subprocess.TimeoutExpired):
            print("ERROR: FFmpeg process timed out.")
        else:
            print(f"ERROR: {str(e)}")
        if process:
            process.kill()
        return False
    finally:
        cleanup_temp_files(temp_files)
        gc.collect()


def create_ass_subtitles_scaled(lines_data, output_path, video_width=1080, video_height=1920, resolution='HD'):
    """Create ASS subtitle file with resolution-scaled font sizes"""
    
    vibrant_colors = get_vibrant_colors()
    
    # Adjust font sizes based on resolution
    if resolution == '4K':
        name_font = 220
        title_font = 240
        page3_font = 240
        line_font = 180
        outline = 16
        shadow = 0
    else:
        name_font = 110
        title_font = 120
        page3_font = 120
        line_font = 90
        outline = 8
        shadow = 0
    
    ass_content = f"""[Script Info]
Title: Celebrity Bio Subtitles
ScriptType: v4.00+
WrapStyle: 0
PlayResX: {video_width}
PlayResY: {video_height}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Page1Name1,Impact,{name_font},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,{outline},{shadow},5,10,10,10,1
Style: Page1Name2,Impact,{name_font},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,{outline},{shadow},5,10,10,10,1
Style: Page1Name3,Impact,{name_font},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,{outline},{shadow},5,10,10,10,1

Style: Title,Impact,{title_font},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,{outline},{shadow},5,10,10,10,1
Style: Page3Title,Impact,{page3_font},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,{outline},{shadow},5,10,10,10,1
Style: Engagement,Impact,{title_font},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,{outline},{shadow},5,10,10,10,1

Style: Line1,Impact,{line_font},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,{outline},{shadow},5,10,10,10,1
Style: Line2,Impact,{line_font},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,{outline},{shadow},5,10,10,10,1
Style: Line3,Impact,{line_font},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,{outline},{shadow},5,10,10,10,1
Style: Line4,Impact,{line_font},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,{outline},{shadow},5,10,10,10,1
Style: Line5,Impact,{line_font},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,{outline},{shadow},5,10,10,10,1
Style: Line6,Impact,{line_font},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,{outline},{shadow},5,10,10,10,1
Style: Line7,Impact,{line_font},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,{outline},{shadow},5,10,10,10,1
Style: Line8,Impact,{line_font},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,{outline},{shadow},5,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    
    def format_time(seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}:{minutes:02d}:{secs:05.2f}"
    
    for line_data in lines_data:
        start_time = format_time(line_data['start'])
        end_time = format_time(line_data['end'])
        style = line_data['style']
        text = line_data['text']
        y_pos = line_data.get('y_pos', 0)
        
        fade_tag = line_data.get('fade_tag', '{\\fad(250,0)}')
        color_tag = line_data.get('color_tag', '')
        
        if y_pos > 0:
            pos_tag = f"{{\\pos({video_width//2},{y_pos})}}"
        else:
            pos_tag = ""
        
        ass_content += f"Dialogue: 0,{start_time},{end_time},{style},,0,0,0,,{pos_tag}{fade_tag}{color_tag}{text}\n"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(ass_content)
    
    return output_path


def create_page3_collage_filter_scaled(valid_known_images, has_celebrity_image, bg_stream, page3_start, page3_end, scale_factor=1.0):
    """Create FFmpeg filter for Page 3 photo collage with scaled positions for 4K"""
    filter_parts = []
    
    if not valid_known_images:
        return filter_parts, bg_stream
    
    num_images = min(len(valid_known_images), 10)
    positions = generate_collage_positions(num_images)
    
    sorted_positions = sorted(enumerate(positions[:num_images]), key=lambda x: x[1]['z_order'])
    
    current_stream = bg_stream
    
    for idx, (original_idx, pos) in enumerate(sorted_positions):
        img_idx = 7 if has_celebrity_image else 6
        img_idx += original_idx
        
        stagger_delay = 0.15 * idx
        img_start = page3_start + stagger_delay
        img_end = page3_end
        
        # Scale positions and sizes for resolution
        size = int(pos['size'] * scale_factor)
        x_pos = int(pos['x'] * scale_factor)
        y_pos = int(pos['y'] * scale_factor)
        border_width = int(25 * scale_factor)
        
        inner_size = size - (border_width * 2)
        
        image_filter = (
            f"[{img_idx}:v]"
            f"scale={inner_size}:{inner_size}:force_original_aspect_ratio=decrease,"
            f"pad={inner_size}:{inner_size}:(ow-iw)/2:(oh-ih)/2:color=black,"
            f"pad={size}:{size}:{border_width}:{border_width}:color=white,"
            f"rotate={pos['rotation']}:c=none:ow='hypot(iw,ih)':oh='hypot(iw,ih)'"
            f"[known{original_idx}]"
        )
        
        overlay_filter = (
            f"{current_stream}[known{original_idx}]"
            f"overlay={x_pos}:{y_pos}:"
            f"enable='between(t\\,{img_start}\\,{img_end})'"
            f"[known_overlay{idx}]"
        )
        
        combined_filter = f"{image_filter};{overlay_filter}"
        filter_parts.append(combined_filter)
        
        current_stream = f"[known_overlay{idx}]"
    
    return filter_parts, current_stream


def main():
    # Base directory where script is located
    BASE_DIR = r"D:\codebase\ytube\THEMOVIEDB"
    
    # Input paths
    MUSIC_DIR = os.path.join(BASE_DIR, "music")
    BACKGROUND_DIR = os.path.join(BASE_DIR, "image")
    PAGE1_BG_DIR = os.path.join(BASE_DIR, "page1_bg")
    PAGE2_BG_DIR = os.path.join(BASE_DIR, "page2_bg")
    PAGE5_BG_DIR = os.path.join(BASE_DIR, "page5_bg")
    PAGE6_BG_DIR = os.path.join(BASE_DIR, "page6_bg")
    EVENTS_JSON = os.path.join(BASE_DIR, "celebrities_json_new.json")
    
    # Output paths
    OUTPUT_DIR = r"D:\codebase\ytube\THEMOVIEDB\output-video"
    PROCESSING_LOG = os.path.join(OUTPUT_DIR, "processing_log.json")
    
    # Create output directory if it doesn't exist
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    Path(PAGE1_BG_DIR).mkdir(parents=True, exist_ok=True)
    Path(PAGE2_BG_DIR).mkdir(parents=True, exist_ok=True)
    Path(PAGE5_BG_DIR).mkdir(parents=True, exist_ok=True)
    Path(PAGE6_BG_DIR).mkdir(parents=True, exist_ok=True)
    
    # Mode selection
    print("SELECT MODE:")
    print("1. Test Mode - Process 1-5 videos")
    print("2. Production Mode - Process all videos")
    
    while True:
        choice = input("Enter mode (1 or 2): ").strip()
        if choice in ['1', '2']:
            mode = "test" if choice == '1' else "production"
            break
    
    # Resolution selection
    print("\nSELECT RESOLUTION:")
    print("1. HD (1080x1920)")
    print("2. 4K (2160x3840)")
    
    while True:
        res_choice = input("Enter resolution (1 or 2): ").strip()
        if res_choice in ['1', '2']:
            resolution = "HD" if res_choice == '1' else "4K"
            break
    
    # Text Design selection
    print("\nSELECT TEXT DESIGN:")
    print("0. Random (different design for each video)")
    print("1. Design 1 - Slide In From Sides")
    print("2. Design 2 - Bounce Up From Bottom")
    print("3. Design 3 - Zoom In With Rotation")
    print("4. Design 4 - Typewriter Effect")
    print("5. Design 5 - Pulse/Scale Animation")
    
    while True:
        design_choice = input("Enter design (0-5): ").strip()
        if design_choice in ['0', '1', '2', '3', '4', '5']:
            force_design = None if design_choice == '0' else int(design_choice)
            break
    
    print(f"\nMode: {mode.upper()}")
    print(f"Resolution: {resolution}")
    print(f"Script location: {BASE_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    if force_design:
        design_names = {
            1: "Slide In From Sides",
            2: "Bounce Up From Bottom", 
            3: "Zoom In With Rotation",
            4: "Typewriter Effect",
            5: "Pulse/Scale Animation"
        }
        print(f"Text Design: FORCED - Design {force_design} ({design_names[force_design]}) for ALL videos")
    else:
        print("Text Design: Random selection (1-5 styles) per video")
    
    # Load resources
    music_files = get_music_files(MUSIC_DIR)
    background_media = get_background_media(BACKGROUND_DIR)
    page1_backgrounds = get_background_media(PAGE1_BG_DIR)
    page2_backgrounds = get_background_media(PAGE2_BG_DIR)
    page5_backgrounds = get_background_media(PAGE5_BG_DIR)
    page6_backgrounds = get_background_media(PAGE6_BG_DIR)
    
    if not music_files:
        print(f"ERROR: No music files found in {MUSIC_DIR}")
        return
    
    if not background_media:
        print(f"ERROR: No background media files found in {BACKGROUND_DIR}")
        return

    if not page1_backgrounds:
        print(f"ERROR: No Page 1 background files found in {PAGE1_BG_DIR}")
        print("Please add at least one image to this directory.")
        return
        
    if not page2_backgrounds:
        print(f"ERROR: No Page 2 background files found in {PAGE2_BG_DIR}")
        print("Please add at least one image/video to this directory.")
        return
    
    if not page5_backgrounds:
        print(f"ERROR: No Page 5 background files found in {PAGE5_BG_DIR}")
        print("Please add at least one image/video to this directory for the 'Also Known For' section.")
        return
    
    if not page6_backgrounds:
        print(f"ERROR: No Page 6 background files found in {PAGE6_BG_DIR}")
        print("Please add at least one image/video to this directory for the final page.")
        return
    
    if not os.path.exists(EVENTS_JSON):
        print(f"ERROR: JSON file not found at {EVENTS_JSON}")
        return
    
    print(f"Found {len(music_files)} music files")
    print(f"Found {len(background_media)} background files")
    print(f"Found {len(page1_backgrounds)} Page 1 background files")
    print(f"Found {len(page2_backgrounds)} Page 2 background files")
    print(f"Found {len(page5_backgrounds)} Page 5 background files")
    print(f"Found {len(page6_backgrounds)} Page 6 background files")
    
    # Load processing log
    log = load_processing_log(PROCESSING_LOG)
    processed_link_ids = log.get('processed_link_ids', [])
    skipped_records = log.get('skipped_records', [])
    music_index = log.get('music_index', 0)
    background_index = log.get('background_index', 0)
    page1_bg_index = log.get('page1_bg_index', 0)
    page2_bg_index = log.get('page2_bg_index', 0)
    page5_bg_index = log.get('page5_bg_index', 0)
    page6_bg_index = log.get('page6_bg_index', 0)
    page1_bg_used = log.get('page1_bg_used', [])
    page2_bg_used = log.get('page2_bg_used', [])
    page5_bg_used = log.get('page5_bg_used', [])
    page6_bg_used = log.get('page6_bg_used', [])
    
    print(f"\nPreviously processed: {len(processed_link_ids)} videos")
    print(f"Skipped records: {len(skipped_records)}")
    
    # Load events
    all_events = load_celebrity_events(EVENTS_JSON)
    print(f"Loaded {len(all_events)} total records from JSON")
    
    # Filter events
    events_to_process = []
    invalid_birthday_count = 0
    duplicate_count = 0
    
    for event in all_events:
        link_id = event.get('link_ID', '')
        name = event.get('name', 'Unknown')
        
        if not is_valid_record(event):
            if link_id and link_id not in skipped_records:
                skipped_records.append(link_id)
            invalid_birthday_count += 1
            continue
        
        if is_duplicate_record(event, processed_link_ids):
            duplicate_count += 1
            continue
        
        events_to_process.append(event)
    
    print(f"\nFiltering summary:")
    print(f"   - Invalid birthday (N/A): {invalid_birthday_count}")
    print(f"   - Duplicates: {duplicate_count}")
    print(f"   - Available to process: {len(events_to_process)}")
    
    if not events_to_process:
        print("\nNo valid records to process!")
        return
    
    # Apply test mode limit
    if mode == "test":
        while True:
            try:
                count = int(input("\nHow many videos to process (1-5)? ").strip())
                if 1 <= count <= 5:
                    break
                print("Please enter a number between 1 and 5.")
            except ValueError:
                print("Please enter a valid number.")
        
        events_to_process = events_to_process[:min(count, len(events_to_process))]
    
    print(f"\n{'='*60}")
    print(f"STARTING PROCESSING - {len(events_to_process)} videos to create")
    print(f"Resolution: {resolution}")
    print(f"Output location: {OUTPUT_DIR}")
    print(f"{'='*60}\n")
    
    # Process events
    processed = 0
    failed = 0
    
    for idx, event in enumerate(events_to_process):
        if SHUTDOWN_REQUESTED:
            print("\nShutdown detected, stopping loop...")
            break
        
        name = event.get('name', 'Unknown')
        link_id = event.get('link_ID', '')
        
        safe_name = re.sub(r'[\\/*?:"<>|]', '', name)
        
        # Add resolution suffix to filename
        res_suffix = "_4K" if resolution == "4K" else "_HD"
        filename = event.get('filename', f'video_{safe_name}_{link_id}')[:180] + res_suffix
        
        print(f"\n[{idx + 1}/{len(events_to_process)}] Processing: {name} (ID: {link_id}) - {resolution}")
        
        current_music = music_files[music_index % len(music_files)]
        current_bg = background_media[background_index % len(background_media)]
        
        # Use random unique selection for page backgrounds
        current_page1_bg, page1_bg_used = get_random_unused_file(page1_backgrounds, page1_bg_used)
        current_page2_bg, page2_bg_used = get_random_unused_file(page2_backgrounds, page2_bg_used)
        current_page5_bg, page5_bg_used = get_random_unused_file(page5_backgrounds, page5_bg_used)
        current_page6_bg, page6_bg_used = get_random_unused_file(page6_backgrounds, page6_bg_used)
        
        print(f"   - Page 1 BG: {os.path.basename(current_page1_bg)}")
        print(f"   - Page 2 BG: {os.path.basename(current_page2_bg)}")
        print(f"   - Page 5 BG: {os.path.basename(current_page5_bg)} (for Page 3 - Also Known For)")
        print(f"   - Page 6 BG: {os.path.basename(current_page6_bg)} (for Page 4 - Final)")
        print(f"   - Main BG:   {os.path.basename(current_bg)}")
        print(f"   - Music:     {os.path.basename(current_music)}")
        
        output_path = Path(OUTPUT_DIR) / f"{filename}.mp4"
        
        success = create_celebrity_video(
            event, current_bg, current_music, output_path, 
            current_page1_bg, current_page2_bg, current_page5_bg, current_page6_bg,
            resolution,  # Pass resolution parameter
            force_design  # Pass force_design parameter for testing
        )
        
        if success:
            processed += 1
            processed_link_ids.append(link_id)
            music_index = (music_index + 1) % len(music_files)
            background_index = (background_index + 1) % len(background_media)
            
            if mode == "production":
                save_processing_log(PROCESSING_LOG, processed_link_ids, skipped_records, 
                                    music_index, background_index, page1_bg_index, page2_bg_index, 
                                    page5_bg_index, page6_bg_index,
                                    page1_bg_used, page2_bg_used, page5_bg_used, page6_bg_used)
                print(f"Progress saved to log")
        else:
            failed += 1
            print(f"FAILED: {filename}.mp4")
        
        gc.collect()
        time.sleep(1)
    
    print(f"\n{'='*60}")
    print("SESSION COMPLETE!")
    print(f"{'='*60}")
    print(f"Mode: {mode.upper()}")
    print(f"Resolution: {resolution}")
    print(f"Successfully processed: {processed} videos")
    print(f"Failed: {failed} videos")
    
    if mode == "production":
        print(f"Total records processed: {len(processed_link_ids)}")
        print(f"Processing log: {PROCESSING_LOG}")
    else:
        print("Test mode: Log not updated. Run in production to save progress.")
    
    print(f"Output location: {OUTPUT_DIR}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()