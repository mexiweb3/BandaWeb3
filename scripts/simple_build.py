import json
import os
import shutil
from pathlib import Path
from datetime import datetime
from collections import Counter
import update_stats

def format_display_duration(duration_str):
    if not duration_str:
        return ""
    
    ds = str(duration_str).strip()
    
    if ':' in ds:
        parts = ds.split(':')
        if len(parts) == 3:
            h, m, s = parts
            try:
                ih = int(h)
                im = int(m)
                
                if ih > 0:
                    return f"{ih}h {im}m"
                else:
                    return f"{im}m"
            except ValueError:
                return ds
        elif len(parts) == 2:
            m, s = parts
            try:
                im = int(m)
                return f"{im}m"
            except ValueError:
                return ds
    
    return ds

def format_display_date(date_str):
    if not date_str:
        return ""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%d-%b-%y")
    except ValueError:
        return date_str

def generate():
    # Setup paths
    base_dir = Path(".")
    data_path = base_dir / "shared" / "episodes_database.json"
    consolidated_data_path = base_dir / "shared" / "consolidated_database.json"
    flyers_dir = base_dir / "shared" / "flyers"
    output_dir = base_dir / "website" / "output"
    static_src = base_dir / "website" / "static"
    static_dst = output_dir / "static"
    episodes_dst = output_dir / "episodes"
    flyers_dst = output_dir / "flyers"

    # Load data
    with open(data_path, "r") as f:
        data = json.load(f)
    
    # Load consolidated database for spoken page
    all_episodes = []
    if os.path.exists(consolidated_data_path):
        with open(consolidated_data_path, "r") as f:
             consolidated_data = json.load(f)
             all_episodes = consolidated_data.get("episodes", [])

    episodes = data["episodes"]
    
    # Filter episodes
    hosted_episodes = []
    cohosted_episodes = []
    numbered_episodes = []

    for ep in episodes:
        if ep.get('type') == 'co-hosted':
             cohosted_episodes.append(ep)
        else:
             hosted_episodes.append(ep)
             # Check if it's numbered (subset of hosted)
             if ep.get('is_numbered'):
                 numbered_episodes.append(ep)
    
    # Sort by number/date descending
    # ... (sorting logic) ...
    def robust_sort_key(ep):
        val = str(ep.get('number', '0'))
        if val.isdigit():
            return int(val)
        return val

    def hosted_sort(ep):
        num = str(ep.get('number', '0'))
        if num.isdigit():
             return int(num)
        try:
            return int(num)
        except ValueError:
            clean = "".join(filter(str.isdigit, num))
            return int(clean) if clean else 0

    hosted_episodes.sort(key=lambda x: x.get('date', ''), reverse=True)
    cohosted_episodes.sort(key=lambda x: x.get('date', ''), reverse=True)
    numbered_episodes.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    episodes.sort(key=lambda x: x.get('date', ''), reverse=True)

    def linkify_handle(handle):
        if not handle: return ""
        # Handle cases like "Host: @handle" or just "@handle"
        # We assume clean handle "@foo"
        if handle.startswith('@'):
             clean = handle.replace('@', '')
             return f'<a href="https://x.com/{clean}" target="_blank" style="text-decoration: none; color: inherit;">{handle}</a>'
        return handle

        return handle
    # Create directories
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    os.makedirs(static_dst)
    os.makedirs(episodes_dst)
    os.makedirs(flyers_dst)

    # Copy static assets
    if os.path.exists(static_src):
        shutil.copytree(str(static_src), str(static_dst), dirs_exist_ok=True)

    # Copy flyers
    print("Copying flyers...")
    for ep in episodes:
        flyers = []
        if ep.get('flyers'):
            flyers.extend(ep['flyers'])
        if ep.get('flyer_urls'):
            flyers.extend(ep['flyer_urls'])
        if ep.get('flyer_url'):
            flyers.append(ep['flyer_url'])
        if ep.get('participant_graph'):
            flyers.append(ep['participant_graph'])
            
        for flyer in flyers:
            # Handle potential paths (though usually just filename in DB)
            fname = os.path.basename(flyer)
            src = flyers_dir / fname
            dst = flyers_dst / fname
            
            if src.exists():
                shutil.copy2(src, dst)
            else:
                pass # print(f"Warning: Flyer not found {src}")

    # --- Generate Pages (Index, Hosted, Cohosted, Archive, Numbered) ---
    
    generate_subpage(output_dir, "index.html", "Todos los Episodios", f"Lo más reciente de BandaWeb3 ({len(episodes)} Episodios)", episodes)
    generate_subpage(output_dir, "hosted.html", "Hosted Spaces", f"Episodios hosteados por Mexi ({len(hosted_episodes)} Spaces)", hosted_episodes)
    generate_subpage(output_dir, "numbered.html", "Episodios Numerados", f"Colección 001 - 074 ({len(numbered_episodes)} Episodios)", numbered_episodes)
    generate_subpage(output_dir, "cohosted.html", "Co-Hosted Spaces", f"Episodios co-hosteados y participaciones ({len(cohosted_episodes)} Spaces)", cohosted_episodes)
    generate_subpage(output_dir, "archive.html", "Archivo de Episodios", f"Todos los episodios ({len(episodes)} total)", episodes)
    
    if all_episodes:
         generate_spoken_page(output_dir, "spoken.html", "All Episodes Database", f"Base de datos completa ({len(all_episodes)} Episodios)", all_episodes)
    
    print(f"Index generated with {len(numbered_episodes)} numbered episodes")

    # --- Generate Individual Pages ---
    for i, ep in enumerate(episodes):
        # ... (flyer logic) ...
        flyer_html_list = []
        if ep.get("flyers"):
            for flyer_name in ep["flyers"]:
                flyer_html_list.append(f'<img src="../flyers/{flyer_name}" alt="Flyer" style="width: 400px; border-radius: 12px; margin-bottom: 20px;">')
        elif ep.get("flyer_urls"):
            for url in ep["flyer_urls"]:
                 src = url if "/" in url else f"../flyers/{url}"
                 flyer_html_list.append(f'<img src="{src}" alt="Flyer" style="width: 400px; border-radius: 12px; margin-bottom: 20px;">')
        elif ep.get("flyer_url"):
             url = ep["flyer_url"]
             src = url if "/" in url else f"../flyers/{url}"
             flyer_html_list.append(f'<img src="{src}" alt="Flyer" style="width: 400px; border-radius: 12px; margin-bottom: 20px;">')
        
        flyers_section = "\n".join(flyer_html_list)

        ep_html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>#{ep['number']} - {ep['title']}</title>
    <link rel="stylesheet" href="../static/style.css">
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a href="../index.html" class="logo">
                <img src="../static/images/banda_dark.png" alt="BandaWeb3" style="height: 60px;">
            </a>
            <div class="nav-links">
                <a href="../numbered.html">Episodios Numerados</a>
                <a href="../hosted.html">Hosted Spaces</a>
                <a href="../cohosted.html">Co-Hosted Spaces</a>
                <a href="../archive.html">All Episodes</a>
                <a href="../about.html">Acerca de Mexi</a>
                <a href="../index.html">← Inicio</a>
            </div>
        </div>
    </nav>
    
    <main class="episode-detail">
        <div class="container">
            <article class="episode-full">
                <header class="episode-header">
                    <h1 class="episode-title-large">{ep['title']}</h1>
                    <span class="episode-number-large">#{ep['number']}</span>
                    <div class="episode-meta">
                        {f'<span class="status-badge cohosted" style="margin-right: 15px;">🤝 Co-Hosted</span>' if ep.get("type") == "co-hosted" else ""}
                        {f'<span class="status-badge" style="margin-right: 15px; background-color: #1DA1F2; color: white; padding: 4px 10px; border-radius: 4px; font-size: 0.85em;">📊 X Spaces Analytics</span>' if ep.get("analytics_source") else ""}
                        {f'<a href="{ep["space_url"]}" target="_blank" style="text-decoration: none;"><span class="status-badge" style="margin-right: 15px; background-color: #000000; color: white; padding: 4px 10px; border-radius: 4px; font-size: 0.85em;">🔗 Escuchar Space</span></a>' if ep.get("space_url") else ""}
                        <span>📅 {format_display_date(ep['date'])}</span>
                        <span>⏱ {format_display_duration(ep.get('duration'))}</span>
                        {f'<span>🎧 {ep["listeners"]}</span>' if ep.get("listeners") else ""}
                        {f'<span>🎤 Host: {linkify_handle(ep["host"])}</span>' if ep.get("host") else ""}
                        {f'<span>🤝 Co-Hosts: {", ".join(ep["cohosts"])}</span>' if ep.get("cohosts") else ""}
                        <span>👥 {', '.join(ep['guests'])}</span>
                    </div>
                </header>
                
                <div class="episode-content">
                    {flyers_section}
                    
                    <div class="description">
                        <h3>Sobre este episodio</h3>
                        <p>{ep['description']}</p>
                    </div>
                    
                    <div class="topics">
                        <h3>Temas</h3>
                        <div class="card-topics">
                            {''.join([f'<span class="topic-tag-small">{t}</span>' for t in ep['topics']])}
                        </div>
                    </div>
                    
                    <div class="links">
                        <h3>Enlaces</h3>
                        {f'<a href="{ep["space_url"]}" target="_blank" class="button" style="background-color: #000000; color: white; font-weight: bold; padding: 12px 24px; font-size: 1.1em;">🎙️ Escuchar en X Space</a>' if ep.get("space_url") else ""}
                        
                        {f'<a href="{ep["spacesdashboard_url"]}" target="_blank" class="button" style="background-color: #1DA1F2; color: white; margin-left: 10px;">📊 Ver en SpacesDashboard</a>' if ep.get("spacesdashboard_url") else ""}
                        
                        {f'<a href="{ep["instagram_url"]}" target="_blank" class="button" style="background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%); color: white; margin-left: 10px;">Ver en Instagram</a>' if ep.get("instagram_url") else ""}
                        
                        {f'<a href="{ep["arena_url"]}" target="_blank" class="button" style="background-color: #000000; margin-left: 10px;">Ver en Arena</a>' if ep.get("arena_url") else ""}
                        
                        {f'<a href="{ep["unlock_url"]}" target="_blank" class="button" style="background-color: #ff6b6b; margin-left: 10px;">Claim Unlock</a>' if ep.get("unlock_url") else ""}

                        {f'<a href="{ep["arbiscan_url"]}" target="_blank" class="button" style="background-color: #28A0F0; margin-left: 10px;">Ver en Arbiscan</a>' if ep.get("arbiscan_url") else ""}

                        {f'<a href="{ep["snowtrace_url"]}" target="_blank" class="button" style="background-color: #E84142; margin-left: 10px;">Ver en Snowtrace</a>' if ep.get("snowtrace_url") else ""}

                        {f'<a href="{ep["opensea_url"]}" target="_blank" class="button" style="background-color: #2081e2; margin-left: 10px;">OpenSea Collection</a>' if ep.get("opensea_url") else ""}
                        
                        {f'<a href="{ep["contract_url"]}" target="_blank" class="button" style="background-color: #3498db; margin-left: 10px;">Contract (Arbiscan)</a>' if ep.get("contract_url") else ""}
                    </div>

                    {f'''<div class="participant-graph" style="margin-top: 40px;">
                        <h3>Participant History</h3>
                        <img src="../flyers/{ep['participant_graph']}" alt="Participant History" style="width: 100%; border-radius: 12px; margin-bottom: 20px;">
                    </div>''' if ep.get('participant_graph') else ''}
                    
                    </div>
                </div>
            </article>
        </div>
    </main>

    <div class="container" style="margin-top: 20px; margin-bottom: 40px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            {f'<a href="episode_{episodes[i+1]["number"]}.html" class="button" style="background-color: #333;">&larr; Anterior ({episodes[i+1]["number"]})</a>' if i + 1 < len(episodes) else '<span class="button" style="background-color: #ccc; cursor: default;">&larr; Anterior</span>'}
            
            <a href="../archive.html" class="button" style="background-color: #e91e63;">Volver al Archivo</a>

            {f'<a href="episode_{episodes[i-1]["number"]}.html" class="button" style="background-color: #333;">Siguiente ({episodes[i-1]["number"]}) &rarr;</a>' if i > 0 else '<span class="button" style="background-color: #ccc; cursor: default;">Siguiente &rarr;</span>'}
        </div>
    </div>
</body>
</html>
"""
        with open(episodes_dst / f"episode_{ep['number']}.html", "w") as f:
            f.write(ep_html)

    # Partners section logic moved to generate_subpage
    
    # --- Generate About Page ---
    about_html = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Acerca de - BandaWeb3</title>
    <link rel="stylesheet" href="static/style.css">
    <style>
        .about-container { max-width: 800px; margin: 0 auto; padding: 40px 20px; }
        .profile-header { text-align: center; margin-bottom: 40px; }
        .profile-img { width: 200px; height: 200px; border-radius: 50%; object-fit: cover; border: 4px solid #e91e63; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(233, 30, 99, 0.3); }
        .bio-section { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 30px; color: #333; }
        .bio-lang { margin-bottom: 20px; }
        .bio-lang h3 { color: #e91e63; margin-bottom: 15px; }
        .bio-lang p { color: #333; }
        .bio-section h3 { color: #e91e63; }
        .bio-section p { color: #333; }
        .social-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-top: 30px; }
        .social-link { display: flex; align-items: center; justify-content: center; padding: 12px; background: #f8f9fa; border-radius: 8px; text-decoration: none; color: #333; font-weight: 500; transition: all 0.2s; }
        .social-link:hover { background: #e91e63; color: white; transform: translateY(-3px); }
        .brand-kit { margin-top: 50px; text-align: center; }
        .brand-kit h3 { color: #e91e63; }
        .brand-images { display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; margin-top: 20px; }
        .brand-img-container { background: white; padding: 10px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .brand-img { height: 80px; object-fit: contain; }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a href="index.html" class="logo">
                <img src="static/images/banda_dark.png" alt="BandaWeb3" style="height: 60px;">
            </a>
            <div class="nav-links">
                <a href="numbered.html">Episodios Numerados</a>
                <a href="hosted.html">Hosted Spaces</a>
                <a href="cohosted.html">Co-Hosted Spaces</a>
                <a href="archive.html">All Episodes</a>
                <a href="about.html" class="active">Acerca de Mexi</a>
                <a href="https://twitter.com/BandaWeb3" target="_blank">Twitter</a>
            </div>
        </div>
    </nav>

    <main class="about-container">
        <div class="profile-header">
            <img src="static/images/mexi_1.png" alt="Mexi" class="profile-img">
            <h1>Mauricio Cruz (Mexi)</h1>
            <p class="subtitle">Host de BandaWeb3 | Blockchain Consultant & Developer</p>
        </div>

        <div class="bio-section">
            <div class="bio-lang">
                <h3>🇲🇽 Español</h3>
                <p>Soy Mauricio Cruz, aka Mexi, Ingeniero en Electrónica y Comunicaciones y tengo una Maestría en Seguridad. Trabajé 20 años para empresas globales, donde lideré equipos de administración de proyectos de edificios inteligentes en Latam.</p>
                <p>Desde 2017, estoy involucrado en el ecosistema blockchain y, desde 2021, me convertí en emprendedor y creador de contenido, construyendo mi marca personal y comunidades en Web3. Cuento con certificaciones como Blockchain Developer y Blockchain Consultant de Blockchain Academy.</p>
            </div>
            
            <hr style="margin: 30px 0; border: 0; border-top: 1px solid #eee;">

            <div class="bio-lang">
                <h3>🇺🇸 English</h3>
                <p>I’m Mauricio Cruz, aka Mexi, an Electronics and Communications Engineer with a Master's degree in Security. I worked for 20 years in global companies, where I led project management teams across Latin America on intelligent building projects.</p>
                <p>Since 2017, I've been involved in the blockchain ecosystem and, from 2021, I transitioned to entrepreneurship and content creation, building my personal brand and communities in Web3. I hold certifications as a Blockchain Developer and Blockchain Consultant from Blockchain Academy.</p>
            </div>
        </div>

        <div class="bio-section">
            <h3>Conecta con Mexi</h3>
            <div class="social-grid">
                <a href="https://mexi.wtf" target="_blank" class="social-link">🌐 Website</a>
                <a href="https://x.com/meximalist" target="_blank" class="social-link">🐦 Twitter / X</a>
                <a href="https://www.linkedin.com/in/mauriciocruzcpp/" target="_blank" class="social-link">💼 LinkedIn</a>
                <a href="https://github.com/mexiweb3" target="_blank" class="social-link">💻 GitHub</a>
                <a href="https://www.instagram.com/mexiweb3" target="_blank" class="social-link">📸 Instagram</a>
                <a href="https://www.tiktok.com/@mexiweb3" target="_blank" class="social-link">🎵 TikTok</a>
                <a href="https://call.mexi.wtf" target="_blank" class="social-link">Dv Calendly</a>
            </div>
        </div>

        <div class="bio-section">
            <h3>Podcast & Comunidad</h3>
            <p><strong>Proof of Value:</strong> <a href="https://www.youtube.com/@proofofvalue" target="_blank">YouTube</a> | <a href="https://open.spotify.com/show/0LWyq4aXfYriitfZkMiXVz" target="_blank">Spotify</a></p>
            <p><strong>mxweb3:</strong> <a href="https://www.mxweb3.com/" target="_blank">Website</a> | <a href="https://x.com/mxweb3" target="_blank">Twitter</a> | <a href="https://www.instagram.com/mxweb3" target="_blank">Instagram</a></p>
        </div>

        <div class="brand-kit">
            <h3>BandaWeb3 Brand Kit</h3>
            <div class="brand-images">
                <div class="brand-img-container"><img src="static/images/banda_dark.png" alt="Logo Dark" class="brand-img" style="background: white;"></div>
                <div class="brand-img-container"><img src="static/images/banda_light.png" alt="Logo Light" class="brand-img" style="background: #333;"></div>
                <div class="brand-img-container"><img src="static/images/pixel.png" alt="Pixel Art" class="brand-img"></div>
            </div>
        </div>
    </main>
</body>
</html>
"""
    with open(output_dir / "about.html", "w") as f:
        f.write(about_html)

    # Update index.html to include link to about.html
    # We load it back and replace the navbar part or reconstruct it.
    # Actually, simpler to just modify the generation string above in future, but for now let's hot-patch it or assume the previous steps verified the structure enough.
    # Wait, the previous steps updated `html_content` variable in `generate()` but didn't save it until line 111.
    # Since I am replacing the end of the file, I need to make sure I am inside `generate()`.
    
    # Correct approach: Updating `generate()` to produce `about.html` and updating the `html_content` construction for `index.html` to include the link.
    
    # Let's read index.html and patch it if we can't easily modify the source string.
    # Actually, let's just create about.html here. The link in index.html needs to be added by modifying the source code of generate() earlier.
    # But since I can't easily do two non-contiguous edits without `multi_replace`, and I am using `replace_file_content` which is for single blocks...
    # I will stick to creating `about.html` at the end of `generate()`.
    # And I will use another tool call to update the navbar in `index.html` generation.
    
    
    
    # Removed duplicate calls to generate_subpage as they are now called earlier in the main block
    pass

def generate_spoken_page(output_dir, filename, title, subtitle, episodes_list):
    # Get unique hosts
    hosts = [ep.get('host', '') for ep in episodes_list if ep.get('host')]
    unique_hosts = sorted(set(hosts))
    host_counts = Counter(hosts)
    
    # Get unique types
    types = [ep.get('type', 'unknown') for ep in episodes_list]
    type_counts = Counter(types)
    
    # Build host filter options
    host_options = '<option value="all">All Hosts ({})</option>'.format(len(episodes_list))
    
    # Get top 5 hosts by episode count
    top_hosts = host_counts.most_common(5)
    
    # Get remaining hosts sorted alphabetically
    top_host_names = [host for host, count in top_hosts]
    remaining_hosts = sorted([host for host in unique_hosts if host not in top_host_names])
    
    # Add separator comment for top hosts
    host_options += '<option disabled>──────── Top 5 Hosts ────────</option>'
    
    # Add top 5 hosts
    for host, count in top_hosts:
        host_options += f'<option value="{host}">⭐ {host} ({count})</option>'
    
    # Add separator for other hosts
    if remaining_hosts:
        host_options += '<option disabled>──────── Other Hosts ────────</option>'
        
        # Add remaining hosts alphabetically
        for host in remaining_hosts:
            count = host_counts[host]
            host_options += f'<option value="{host}">{host} ({count})</option>'
    
    # Build type filter options
    type_options = '<option value="all">All Types ({})</option>'.format(len(episodes_list))
    type_labels = {
        'hosted': '🎙️ Hosted',
        'co-hosted': '🤝 Co-Hosted',
        'Spoken': '📢 Spoken',
        'unknown': '❓ Unknown'
    }
    for ep_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        label = type_labels.get(ep_type, ep_type)
        type_options += f'<option value="{ep_type}">{label} ({count})</option>'

    html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - BandaWeb3</title>
    <link rel="stylesheet" href="static/style.css">
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a href="index.html" class="logo">
                <img src="static/images/banda_dark.png" alt="BandaWeb3" style="height: 60px;">
            </a>
            <div class="nav-links">
                <a href="numbered.html">Episodios Numerados</a>
                <a href="hosted.html">Hosted Spaces</a>
                <a href="cohosted.html">Co-Hosted Spaces</a>
                <a href="spoken.html" class="active">Spoken</a>
                <a href="archive.html">All Episodes</a>
                <a href="about.html">Acerca de Mexi</a>
                <a href="https://twitter.com/BandaWeb3" target="_blank">Twitter</a>
            </div>
        </div>
    </nav>

    <header class="hero">
        <div class="container">
            <h1 class="hero-title">{title}</h1>
            <p class="hero-subtitle">{subtitle}</p>
        </div>
    </header>

    <main class="episodes-list">
        <div class="container">
            <div style="margin-bottom: 20px; display: flex; gap: 20px; flex-wrap: wrap;">
                <div>
                    <label for="typeFilter" style="font-weight: bold; margin-right: 10px;">Filter by Type:</label>
                    <select id="typeFilter" onchange="filterTable()" style="padding: 8px; border-radius: 5px; border: 1px solid #ccc;">
                        {type_options}
                    </select>
                </div>
                <div>
                    <label for="hostFilter" style="font-weight: bold; margin-right: 10px;">Filter by Host:</label>
                    <select id="hostFilter" onchange="filterTable()" style="padding: 8px; border-radius: 5px; border: 1px solid #ccc;">
                        {host_options}
                    </select>
                </div>
            </div>
            
            <div class="spoken-table-container">
                <table class="spoken-table" id="spokenTable">
                    <thead>
                        <tr>
                            <th onclick="sortTable(0)">Title</th>
                            <th onclick="sortTable(1)">Type</th>
                            <th onclick="sortTable(2)">Host</th>
                            <th onclick="sortTable(3, true)">#</th>
                            <th onclick="sortTable(4)">Duration</th>
                            <th onclick="sortTable(5, true)">Listeners</th>
                            <th onclick="sortTable(6)">Space</th>
                            <th onclick="sortTable(7)">Dash</th>
                            <th onclick="sortTable(8)">Date</th>
                        </tr>
                    </thead>
                    <tbody>
"""
    
    for ep in episodes_list:
        # Columns: Title, Type, Host, Number, Duration, Listeners, Link (Space), Link (Dashboard), Date
        title_text = ep.get('title', '')
        type_text = ep.get('type', 'unknown')
        type_icons = {
            'hosted': '🎙️',
            'co-hosted': '🤝',
            'Spoken': '📢',
            'unknown': '❓'
        }
        type_display = f"{type_icons.get(type_text, '❓')} {type_text}"
        host_text = ep.get('host', '')
        number_val = ep.get('number', 0)
        
        duration_display = format_display_duration(ep.get('duration'))
        duration_raw = ep.get('duration', '') # For sorting if desired, or text sort on display
        
        listeners_val = ep.get('listeners', 0)
        
        space_link = f'<a href="{ep["space_url"]}" target="_blank">🔗</a>' if ep.get("space_url") else ""
        dash_link = f'<a href="{ep["spacesdashboard_url"]}" target="_blank">📊</a>' if ep.get("spacesdashboard_url") else ""
        
        date_display = format_display_date(ep.get('date'))
        date_raw = ep.get('date', '') # YYYY-MM-DD for sorting

        html_content += f"""
                        <tr data-type="{type_text}">
                            <td>{title_text}</td>
                            <td>{type_display}</td>
                            <td>{host_text}</td>
                            <td data-val="{number_val}">{number_val}</td>
                            <td>{duration_display}</td>
                            <td data-val="{listeners_val}">{listeners_val}</td>
                            <td>{space_link}</td>
                            <td>{dash_link}</td>
                            <td data-val="{date_raw}">{date_display}</td>
                        </tr>
"""

    html_content += """
                    </tbody>
                </table>
            </div>

            <div id="paginationControls" style="display: flex; flex-wrap: wrap; justify-content: center; align-items: center; margin-top: 20px; gap: 5px;">
                <!-- Controls rendered by JS -->
            </div>
        </div>
    </main>

    <script>
    let currentPage = 1;
    const rowsPerPage = 25;
    
    // Run initial render when DOM is loaded
    document.addEventListener("DOMContentLoaded", function() {
        filterTable(); // This will effectively render page 1
    });

    function renderTable() {
        const table = document.getElementById("spokenTable");
        const tr = table.getElementsByTagName("tr");
        const paginationControls = document.getElementById("paginationControls");
        
        // Get all rows that MATCH the filters
        let filteredRows = [];
        const hostFilterInput = document.getElementById("hostFilter");
        const typeFilterInput = document.getElementById("typeFilter");
        const hostFilter = hostFilterInput.value.toUpperCase();
        const typeFilter = typeFilterInput.value.toUpperCase();
        
        for (let i = 1; i < tr.length; i++) {
             const hostTd = tr[i].getElementsByTagName("td")[2]; // Host column index 2 (after Type)
             const rowType = tr[i].getAttribute('data-type') || '';
             
             if (hostTd) {
                const hostValue = hostTd.textContent || hostTd.innerText;
                const hostMatch = hostFilter === "ALL" || hostValue.toUpperCase().includes(hostFilter) || hostValue.toUpperCase() === hostFilter;
                const typeMatch = typeFilter === "ALL" || rowType.toUpperCase() === typeFilter;
                
                if (hostMatch && typeMatch) {
                    filteredRows.push(tr[i]);
                } else {
                    tr[i].style.display = "none"; // Hide completely if not matching filters
                }
             }
        }
        
        // Now calculate pagination based on FILTERED rows
        const totalRows = filteredRows.length;
        const totalPages = Math.ceil(totalRows / rowsPerPage);
        
        if (currentPage > totalPages) currentPage = totalPages;
        if (currentPage < 1) currentPage = 1;
        
        const startIndex = (currentPage - 1) * rowsPerPage;
        const endIndex = startIndex + rowsPerPage;
        
        // Show/Hide filtered rows based on pagination
        for (let j = 0; j < filteredRows.length; j++) {
            if (j >= startIndex && j < endIndex) {
                filteredRows[j].style.display = "";
            } else {
                filteredRows[j].style.display = "none";
            }
        }
        
        // Update Controls - Numbered Links
        let controlsHTML = '';
        
        if (totalPages > 1) {
            // Add Previous
            controlsHTML += `<button onclick="changePage(${currentPage - 1})" style="padding: 5px 10px; cursor: pointer; border: 1px solid #ccc; background: ${currentPage === 1 ? '#eee' : '#fff'};" ${currentPage === 1 ? 'disabled' : ''}>&laquo;</button>`;
            
            // Numbered pages
            for (let p = 1; p <= totalPages; p++) {
                // Determine if we should show this page button (simple version: show all, or range)
                // Showing all for user request "ir a cualquiera rápido" unless it's huge. 
                // 657 / 25 = 27 pages. Showing 27 buttons is reasonable.
                controlsHTML += `<button onclick="changePage(${p})" style="padding: 5px 10px; cursor: pointer; border: 1px solid #ccc; background: ${p === currentPage ? '#e91e63' : '#fff'}; color: ${p === currentPage ? '#fff' : '#000'}; font-weight: ${p === currentPage ? 'bold' : 'normal'}; min-width: 30px;">${p}</button>`;
            }
            
            // Add Next
            controlsHTML += `<button onclick="changePage(${currentPage + 1})" style="padding: 5px 10px; cursor: pointer; border: 1px solid #ccc; background: ${currentPage === totalPages ? '#eee' : '#fff'};" ${currentPage === totalPages ? 'disabled' : ''}>&raquo;</button>`;
        }
        
        paginationControls.innerHTML = controlsHTML;
    }
    
    function changePage(pageNum) {
        if (pageNum < 1) return;
        // Max page check is done inside renderTable but verifying here is good too, 
        // though we need totalPages which is calculated inside renderTable.
        // renderTable handles bounds checks safely.
        currentPage = pageNum;
        renderTable();
        window.scrollTo(0, 0);
    }
    
    function filterTable() {
        // When filter changes, reset to page 1
        currentPage = 1;
        renderTable();
    }
    
    // function filterTableOld() { ... }

    function sortTable(n, isNumeric) {
        var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
        table = document.getElementById("spokenTable");
        switching = true;
        // Set the sorting direction to ascending:
        dir = "asc";
        
        // Reset headers classes
        var headers = table.getElementsByTagName("th");
        for (i = 0; i < headers.length; i++) {
            headers[i].classList.remove("sort-asc", "sort-desc");
        }

        while (switching) {
            switching = false;
            rows = table.rows;
            // Iterate only over visible rows? 
            // Standard sorting reorders DOM, so hidden rows would also be reordered.
            // This is fine. But for user experience, let's just sort all rows.
            
            for (i = 1; i < (rows.length - 1); i++) {
                shouldSwitch = false;
                x = rows[i].getElementsByTagName("TD")[n];
                y = rows[i + 1].getElementsByTagName("TD")[n];
                
                var xVal, yVal;
                
                if (x.hasAttribute('data-val')) {
                    xVal = x.getAttribute('data-val');
                    yVal = y.getAttribute('data-val');
                } else {
                    xVal = x.innerHTML.toLowerCase();
                    yVal = y.innerHTML.toLowerCase();
                }

                if (isNumeric) {
                     xVal = parseFloat(xVal) || 0;
                     yVal = parseFloat(yVal) || 0;
                }

                if (dir == "asc") {
                    if (xVal > yVal) {
                        shouldSwitch = true;
                        break;
                    }
                } else if (dir == "desc") {
                    if (xVal < yVal) {
                        shouldSwitch = true;
                        break;
                    }
                }
            }
            if (shouldSwitch) {
                rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                switching = true;
                switchcount ++;
            } else {
                if (switchcount == 0 && dir == "asc") {
                    dir = "desc";
                    switching = true;
                }
            }
        }
        // Re-render pagination after sorting to ensure correct view
        renderTable();
        
        // Update header class
        if (dir === "asc") {
            headers[n].classList.add("sort-asc");
        } else {
            headers[n].classList.add("sort-desc");
        }
    }
    </script>
</body>
</html>
"""
    with open(output_dir / filename, "w") as f:
        f.write(html_content)
    print(f"Generated {filename}")

def generate_subpage(output_dir, filename, title, subtitle, episodes_list):
    html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - BandaWeb3</title>
    <link rel="stylesheet" href="static/style.css">
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a href="index.html" class="logo">
                <img src="static/images/banda_dark.png" alt="BandaWeb3" style="height: 60px;">
            </a>
            <div class="nav-links">
                <a href="numbered.html" class="{'active' if filename == 'numbered.html' else ''}">Episodios Numerados</a>
                <a href="hosted.html" class="{'active' if filename == 'hosted.html' else ''}">Hosted Spaces</a>
                <a href="cohosted.html" class="{'active' if filename == 'cohosted.html' else ''}">Co-Hosted Spaces</a>
                <a href="spoken.html" class="{'active' if filename == 'spoken.html' else ''}">Spoken</a>
                <a href="archive.html" class="{'active' if filename == 'archive.html' else ''}">All Episodes</a>
                <a href="about.html">Acerca de Mexi</a>
                <a href="https://twitter.com/BandaWeb3" target="_blank">Twitter</a>
            </div>
        </div>
    </nav>

    <header class="hero">
        <div class="container">
            <h1 class="hero-title">{title}</h1>
            <p class="hero-subtitle">{subtitle}</p>
        </div>
    </header>

    <main class="episodes-list">
        <div class="container">
            <div class="controls">
                <label for="sort-select" style="color: var(--text); margin-right: 1rem;">Ordenar por:</label>
                <select id="sort-select" class="sort-select" onchange="sortEpisodes(this.value)">
                    <option value="date-desc">Fecha (Más reciente)</option>
                    <option value="date-asc">Fecha (Más antiguo)</option>
                    <option value="listeners-desc">Escuchas (Mayor a menor)</option>
                    <option value="listeners-asc">Escuchas (Menor a mayor)</option>
                </select>
            </div>
            <div class="episodes-grid" id="episodes-grid">
"""

    for ep in episodes_list:
        flyer_html = ""
        flyer_src = ""
        
        # Use flyers array from database
        if ep.get("flyers") and len(ep["flyers"]) > 0:
            flyer_src = f"flyers/{ep['flyers'][0]}"
        elif ep.get("flyer_urls") and len(ep["flyer_urls"]) > 0:
            url = ep["flyer_urls"][0]
            flyer_src = url if "/" in url else f"flyers/{url}"
        elif ep.get("flyer_url"):
            url = ep["flyer_url"]
            flyer_src = url if "/" in url else f"flyers/{url}"
            
        if flyer_src:
             # Fix path for index (relative to root)
             flyer_path = flyer_src.replace("../static", "static").replace("../flyers", "flyers")
             flyer_html = f'<img src="{flyer_path}" alt="Flyer" style="width:100%; border-radius: 8px; margin-bottom: 10px;">'

        html_content += f"""
                <article class="episode-card" data-date="{ep.get('date', '')}" data-listeners="{ep.get('listeners', 0)}">
                    <a href="episodes/episode_{ep['number']}.html" style="text-decoration: none; color: inherit;">
                        <div class="card-content">
                            {flyer_html}
                            <div class="card-header">
                                <span class="episode-number">#{ep['number']}</span>
                                {f'<span style="margin-left: 10px; font-size: 1.1em;" title="Co-Hosted">🤝</span>' if ep.get("type") == "co-hosted" else ""}
                                {f'<span style="margin-left: 10px; font-size: 1.1em;" title="X Spaces Analytics">📊</span>' if ep.get("analytics_source") else ""}
                                {f'<span style="margin-left: 10px; font-size: 1.1em;" title="Space Link Available">🔗</span>' if ep.get("space_url") else ""}
                                <span class="episode-date">{format_display_date(ep['date'])}</span>
                                {f'<span class="episode-listeners" style="margin-left: 10px; font-size: 0.9em; color: #666;">🎧 {ep["listeners"]}</span>' if ep.get("listeners") else ""}
                            </div>
                            <h2 class="card-title">{ep['title']}</h2>
                            <p class="card-description">{ep['description'][:150]}...</p>
                            {f'<p style="font-size: 0.85em; color: #666; margin: 5px 0;">🎤 Host: {ep["host"]}</p>' if ep.get("host") else ""}
                            {f'<p style="font-size: 0.85em; color: #666; margin: 5px 0;">🤝 Co-Hosts: {", ".join(ep["cohosts"])}</p>' if ep.get("cohosts") else ""}
                            <div class="card-topics">
                                {''.join([f'<span class="topic-tag-small">{t}</span>' for t in ep['topics'][:3]])}
                            </div>
                        </div>
                    </a>
                </article>
"""

    html_content += """
            </div>
        </div>
    </main>

    <section class="partners" style="text-align: center; margin: 40px auto; padding: 40px 20px; background-color: #fff0f5; border-radius: 12px; max-width: 800px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h2 style="color: #e91e63; margin-bottom: 20px;">Community Partners</h2>
        <p style="font-size: 1.2em; margin-bottom: 10px;"><strong>¿Quieres estar en Banda Web3?</strong></p>
        <p style="font-size: 1.1em; color: #555; margin-bottom: 30px;">Do you want to be in BandaWeb3?</p>
        
        <p style="margin-bottom: 10px;">Llena este formulario por favor / Please fill the form 👇</p>
        
        <a href="https://docs.google.com/forms/d/e/1FAIpQLSezH91i6mFeFOzjedL2yL1MpR7e8YmCvKkkosPdlD-kQ8ZtOA/viewform?usp=sf_link" target="_blank" class="button" style="background-color: #e91e63; color: white; padding: 15px 30px; text-decoration: none; border-radius: 30px; font-weight: bold; display: inline-block; margin-top: 10px; font-size: 1.1em; transition: transform 0.2s;">
            Become a Partner 🚀
        </a>
    </section>
    <script>
    function sortEpisodes(sortBy) {
        const grid = document.getElementById('episodes-grid');
        const episodes = Array.from(grid.getElementsByClassName('episode-card'));
        
        episodes.sort((a, b) => {
            if (sortBy === 'date-desc') {
                return b.dataset.date.localeCompare(a.dataset.date);
            } else if (sortBy === 'date-asc') {
                return a.dataset.date.localeCompare(b.dataset.date);
            } else if (sortBy === 'listeners-desc') {
                return parseInt(b.dataset.listeners || 0) - parseInt(a.dataset.listeners || 0);
            } else if (sortBy === 'listeners-asc') {
                return parseInt(a.dataset.listeners || 0) - parseInt(b.dataset.listeners || 0);
            }
            return 0;
        });
        
        // Clear and re-append sorted episodes
        grid.innerHTML = '';
        episodes.forEach(ep => grid.appendChild(ep));
    }
    </script>
</body>
</html>
"""
    
    with open(output_dir / filename, "w") as f:
        f.write(html_content)
    print(f"Generated {filename}")

if __name__ == "__main__":
    # Update database statistics
    print("Updating database statistics...")
    update_stats.update_stats()

    current_dir = Path(__file__).parent
    output_dir = current_dir.parent / "website" / "output"
    
    # Ensure raw generate() call works or update it if it expects an arg. 
    # Based on previous file content, generate() seemed to not take args in the original file, 
    # but let's see the definition. 
    # If generate() is defined as generate(), then:
    generate()
