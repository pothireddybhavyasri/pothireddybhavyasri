import sys
import numpy as np
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import scipy.ndimage as ndimage
import math
import random
import os

IMAGE_PATH = r"C:/Users/Bhavy/.gemini/antigravity/brain/7647b1ec-5512-4e7a-99ab-2556655efe67/.user_uploaded/media_1791550706474.jpg"

def process_portrait(image_path, is_dark_mode=True):
    img = Image.open(image_path).convert('RGB')
    
    # 3 & 4. Crop and resize to 300x340
    w, h = img.size
    target_w = w
    target_h = int(w * 340 / 300)
    if target_h > h:
        target_h = h
        target_w = int(h * 300 / 340)
    
    left = (w - target_w) // 2
    top = int(h * 0.05)
    if top + target_h > h:
        top = h - target_h
        
    img = img.crop((left, top, left + target_w, top + target_h))
    img = img.resize((300, 340), Image.Resampling.LANCZOS)
    
    # 5. Apply autocontrast with cutoff=1
    img = ImageOps.autocontrast(img, cutoff=1)
    
    # 6. Apply approximately 1.3x contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.3)
    
    # 7. Apply UnsharpMask with radius=3 and percent=140
    img = img.filter(ImageFilter.UnsharpMask(radius=3, percent=140, threshold=0))
    
    mask = None
    if is_dark_mode:
        img_np = np.array(img)
        bg_color = np.median(img_np[:20, :20], axis=(0,1))
        dist = np.linalg.norm(img_np - bg_color, axis=2)
        mask_bool = dist > 40
        mask_bool = ndimage.binary_closing(mask_bool, structure=np.ones((5,5)))
        mask_bool = ndimage.binary_fill_holes(mask_bool)
        labeled, num_features = ndimage.label(mask_bool)
        if num_features > 0:
            sizes = ndimage.sum(mask_bool, labeled, range(1, num_features + 1))
            largest_label = np.argmax(sizes) + 1
            mask_bool = labeled == largest_label
        mask = mask_bool
        img_np[~mask] = [255, 255, 255]
        img = Image.fromarray(img_np)
        
    img_gray = img.convert('L')
    img_gray_np = np.array(img_gray, dtype=float)
    h, w = img_gray_np.shape
    dithered = np.zeros_like(img_gray_np)
    
    for y in range(h):
        direction = 1 if y % 2 == 0 else -1
        x_range = range(w) if direction == 1 else range(w-1, -1, -1)
        for x in x_range:
            old_pixel = img_gray_np[y, x]
            new_pixel = 255 if old_pixel > 127 else 0
            img_gray_np[y, x] = new_pixel
            dithered[y, x] = new_pixel
            
            quant_error = old_pixel - new_pixel
            if direction == 1:
                if x + 1 < w: img_gray_np[y, x + 1] += quant_error * 7 / 16
                if y + 1 < h:
                    if x > 0: img_gray_np[y + 1, x - 1] += quant_error * 3 / 16
                    img_gray_np[y + 1, x] += quant_error * 5 / 16
                    if x + 1 < w: img_gray_np[y + 1, x + 1] += quant_error * 1 / 16
            else:
                if x - 1 >= 0: img_gray_np[y, x - 1] += quant_error * 7 / 16
                if y + 1 < h:
                    if x + 1 < w: img_gray_np[y + 1, x + 1] += quant_error * 3 / 16
                    img_gray_np[y + 1, x] += quant_error * 5 / 16
                    if x - 1 >= 0: img_gray_np[y + 1, x - 1] += quant_error * 1 / 16
                    
    if is_dark_mode and mask is not None:
        dithered[~mask] = 255
        
    dots = []
    for y in range(h):
        for x in range(w):
            if dithered[y, x] == 0:
                dots.append((x, y))
    return dots

def generate_banner(is_dark_mode=True):
    bg_color = "#0A101F" if is_dark_mode else "#FFFFFF"
    portrait_color = "#A78BFA" if is_dark_mode else "#7C3AED"
    text_color = "#94A3B8"
    accent_color = "#10B981"
    cyan_color = "#22D3EE" if is_dark_mode else "#0891B2"
    handle_bg = cyan_color
    handle_fg = "#0A101F" if is_dark_mode else "#FFFFFF"
    
    dots = process_portrait(IMAGE_PATH, is_dark_mode)
    
    # SVG canvas: 1180 x 610
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1180 610" width="1180" height="610">']
    svg.append(f'<rect width="1180" height="610" fill="{bg_color}" rx="15"/>')
    svg.append(f'<g font-family="monospace" font-size="14" fill="{text_color}">')
    
    svg.append(f'<text x="40" y="40" font-size="13" fill="{cyan_color}">profile.sh --live</text>')
    
    # LIVE badge
    svg.append(f'<g transform="translate(980, 25)">')
    svg.append(f'<rect width="45" height="20" rx="4" fill="{accent_color}" opacity="0.2"/>')
    svg.append(f'<circle cx="12" cy="10" r="4" fill="{accent_color}">')
    svg.append(f'<animate attributeName="opacity" values="1;0.2;1" dur="2s" repeatCount="indefinite"/>')
    svg.append(f'</circle>')
    svg.append(f'<text x="22" y="14" font-size="12" fill="{accent_color}" font-weight="bold">LIVE</text>')
    svg.append(f'</g>')
    
    # Handle pill
    svg.append(f'<g transform="translate(1035, 25)">')
    svg.append(f'<rect width="140" height="20" rx="10" fill="{handle_bg}"/>')
    svg.append(f'<text x="70" y="14" font-size="12" fill="{handle_fg}" text-anchor="middle" font-weight="bold">pothireddybhavyasri</text>')
    svg.append(f'</g>')
    
    # Intro animation groups
    svg.append(f'<text x="40" y="80" fill="{cyan_color}">VISUAL.MAP</text>')
    svg.append(f'<g transform="translate(60, 100)" fill="{portrait_color}" shape-rendering="crispEdges">')
    
    random.seed(42)
    random.shuffle(dots)
    
    num_groups = 60
    dots_per_group = len(dots) // num_groups
    for i in range(num_groups):
        group_dots = dots[i*dots_per_group : (i+1)*dots_per_group]
        if i == num_groups - 1:
            group_dots = dots[i*dots_per_group:]
            
        path_d = "".join([f"M{x},{y}h1v1h-1z" for x, y in group_dots])
        delay = i * (2.0 / num_groups)
        svg.append(f'<path d="{path_d}" opacity="0">')
        svg.append(f'<animate attributeName="opacity" values="0;1" dur="1s" begin="{delay}s" fill="freeze"/>')
        svg.append(f'</path>')
        
    svg.append(f'</g>')
    
    # System Info
    svg.append(f'<text x="500" y="80" fill="{cyan_color}">SYSTEM.INFO</text>')
    svg.append(f'<g transform="translate(500, 120)">')
    
    def add_row(y, label, value):
        total_len = 65
        dots_count = max(0, total_len - len(label) - len(value))
        leader = "." * dots_count
        svg.append(f'<text y="{y}">{label}<tspan fill="{text_color}" opacity="0.4">{leader}</tspan><tspan fill="{text_color}">{value}</tspan></text>')
    
    rows = [
        ("Subject", "Bhavya Sri"),
        ("Role", "Full-Stack Developer / Computer Science Student"),
        ("Origin", "-"),
        ("Education", "B.Tech CSE, ACE Engineering College"),
        ("Status", "Building + Learning + Shipping"),
        ("ToolChain", "Git, Docker, VS Code"),
        ("Core.Lang", "Python, Java, JavaScript, TypeScript, C++"),
        ("Core.Frontend", "React, HTML5, CSS3, Tailwind"),
        ("Core.Backend", "Node.js, Express"),
        ("Core.Database", "MongoDB, MySQL"),
        ("Core.Infra", "Vercel")
    ]
    
    y = 0
    for label, value in rows:
        add_row(y, label, value)
        y += 23
        
    svg.append(f'<text y="{y+23}" fill="{cyan_color}">NETWORK.LINKS</text>')
    
    y += 46
    links = [
        ("Grid.Mail", "-"),
        ("Grid.Portfolio", "https://bhavya-sri-portfolio-three.vercel.app/"),
        ("Grid.LinkedIn", "linkedin.com/in/pothireddy-bhavya-sri-031193328/"),
        ("Grid.GitHub", "pothireddybhavyasri"),
        ("Grid.Facebook", "-")
    ]
    for label, value in links:
        add_row(y, label, value)
        y += 23
        
    svg.append(f'</g>')
    svg.append(f'</g>')
    svg.append(f'</svg>')
    
    filename = "dark.svg" if is_dark_mode else "light.svg"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\\n".join(svg))

generate_banner(True)
generate_banner(False)
print("Banners generated.")
