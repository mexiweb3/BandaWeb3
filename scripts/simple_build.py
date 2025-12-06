import json
import os
import shutil
from pathlib import Path

def generate():
    # Setup paths
    base_dir = Path(".")
    data_path = base_dir / "data" / "episodes_database.json"
    output_dir = base_dir / "website" / "output"
    static_src = base_dir / "website" / "static"
    static_dst = output_dir / "static"
    episodes_dst = output_dir / "episodes"

    # Load data
    with open(data_path, "r") as f:
        data = json.load(f)
    
    episodes = data["episodes"]
    
    # Ensure output dirs
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)
    static_dst.mkdir(parents=True)
    episodes_dst.mkdir(parents=True)

    # Copy static assets
    for item in static_src.iterdir():
        if item.is_file():
            shutil.copy2(item, static_dst / item.name)
        elif item.is_dir():
            shutil.copytree(item, static_dst / item.name)

    # --- Generate Index Page ---
    html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BandaWeb3 - Archivo de Episodios</title>
    <link rel="stylesheet" href="static/style.css">
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a href="index.html" class="logo">
                <img src="static/images/logo.png" alt="BandaWeb3 Logo" style="height: 40px; vertical-align: middle; margin-right: 10px;">
                <span class="logo-text">BandaWeb3</span>
            </a>
            <div class="nav-links">
                <a href="about.html">Acerca de Mexi</a>
                <a href="https://twitter.com/BandaWeb3" target="_blank">Twitter</a>
            </div>
        </div>
    </nav>

    <header class="hero">
        <div class="container">
            <h1 class="hero-title">Archivo de Episodios</h1>
            <p class="hero-subtitle">Explora todos los episodios de BandaWeb3</p>
        </div>
    </header>

    <main class="episodes-list">
        <div class="container">
            <div class="episodes-grid">
"""

    # Iterate over ALL episodes to generate items on index page
    for ep in episodes:
        flyer_html = ""
        flyer_src = ""
        
        if ep.get("flyer_urls") and len(ep["flyer_urls"]) > 0:
            flyer_src = ep["flyer_urls"][0]
        elif ep.get("flyer_url"):
            flyer_src = ep["flyer_url"]
            
        if flyer_src:
             # Fix path for index (relative to root)
             flyer_path = flyer_src.replace("../static", "static")
             flyer_html = f'<img src="{flyer_path}" alt="Flyer" style="width:100%; border-radius: 8px; margin-bottom: 10px;">'

        html_content += f"""
                <article class="episode-card">
                    <a href="episodes/episode_{ep['number']}.html" style="text-decoration: none; color: inherit;">
                        <div class="card-content">
                            {flyer_html}
                            <div class="card-header">
                                <span class="episode-number">#{ep['number']}</span>
                                <span class="episode-date">{ep['date']}</span>
                                {f'<span class="episode-listeners" style="margin-left: 10px; font-size: 0.9em; color: #666;">🎧 {ep["listeners"]}</span>' if ep.get("listeners") else ""}
                            </div>
                            <h2 class="card-title">{ep['title']}</h2>
                            <p class="card-description">{ep['description'][:150]}...</p>
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
</body>
</html>
"""

    with open(output_dir / "index.html", "w") as f:
        f.write(html_content)

    # --- Generate Individual Pages ---
    for ep in episodes:
        flyer_html_list = []
        
        # Handle new schema (flyer_urls list)
        if ep.get("flyer_urls"):
            for url in ep["flyer_urls"]:
                 flyer_html_list.append(f'<img src="{url}" alt="Flyer" style="max-width:100%; border-radius: 12px; margin-bottom: 20px;">')
        
        # Backward compatibility for old schema (single flyer_url)
        elif ep.get("flyer_url"):
             flyer_html_list.append(f'<img src="{ep["flyer_url"]}" alt="Flyer" style="max-width:100%; border-radius: 12px; margin-bottom: 20px;">')
        
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
                <img src="../static/images/logo.png" alt="Logo" style="height: 40px; vertical-align: middle; margin-right: 10px;">
                <span class="logo-text">BandaWeb3</span>
            </a>
            <div class="nav-links">
                <a href="../index.html">← Volver al Archivo</a>
            </div>
        </div>
    </nav>

    <main class="episode-detail">
        <div class="container">
            <article class="episode-full">
                <header class="episode-header">
                    <span class="episode-number-large">#{ep['number']}</span>
                    <h1 class="episode-title-large">{ep['title']}</h1>
                    <div class="episode-meta">
                        <span>📅 {ep['date']}</span>
                        <span>⏱ {ep['duration'].replace("Duration: ", "") if ep.get('duration') else ""}</span>
                        {f'<span>🎧 {ep["listeners"]}</span>' if ep.get("listeners") else ""}
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
                        <a href="{ep['space_url']}" target="_blank" class="button">Ver en X (Twitter)</a>
                        
                        {f'<a href="{ep["unlock_url"]}" target="_blank" class="button" style="background-color: #ff6b6b; margin-left: 10px;">Claim Unlock</a>' if ep.get("unlock_url") else ""}
                        
                        {f'<a href="{ep["opensea_url"]}" target="_blank" class="button" style="background-color: #2081e2; margin-left: 10px;">OpenSea Collection</a>' if ep.get("opensea_url") else ""}
                        
                        {f'<a href="{ep["contract_url"]}" target="_blank" class="button" style="background-color: #3498db; margin-left: 10px;">Contract (Arbiscan)</a>' if ep.get("contract_url") else ""}
                    </div>
                </div>
            </article>
        </div>
    </main>
</body>
</html>
"""
        with open(episodes_dst / f"episode_{ep['number']}.html", "w") as f:
            f.write(ep_html)

    # --- Generate Partners Section in Index ---
    section_index = html_content.find('</body>')
    partners_section = """
    <section class="partners" style="text-align: center; margin: 40px auto; padding: 40px 20px; background-color: #fff0f5; border-radius: 12px; max-width: 800px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h2 style="color: #e91e63; margin-bottom: 20px;">Community Partners</h2>
        <p style="font-size: 1.2em; margin-bottom: 10px;"><strong>¿Quieres estar en Banda Web3?</strong></p>
        <p style="font-size: 1.1em; color: #555; margin-bottom: 30px;">Do you want to be in BandaWeb3?</p>
        
        <p style="margin-bottom: 10px;">Llena este formulario por favor / Please fill the form 👇</p>
        
        <a href="https://docs.google.com/forms/d/e/1FAIpQLSezH91i6mFeFOzjedL2yL1MpR7e8YmCvKkkosPdlD-kQ8ZtOA/viewform?usp=sf_link" target="_blank" class="button" style="background-color: #e91e63; color: white; padding: 15px 30px; text-decoration: none; border-radius: 30px; font-weight: bold; display: inline-block; margin-top: 10px; font-size: 1.1em; transition: transform 0.2s;">
            Become a Partner 🚀
        </a>
    </section>
    """
    # Only insert if not already present (hacky check handled by overwrite)
    # The previous code inserted it directly into the string, so we don't need to re-insert here if we just overwrite the index generation logic above properly.
    # But since we are replacing the full generate function or parts of it, let's just make sure about.html is generated.
    
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
        .bio-section { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 30px; }
        .bio-lang { margin-bottom: 20px; }
        .bio-lang h3 { color: #e91e63; margin-bottom: 15px; }
        .social-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-top: 30px; }
        .social-link { display: flex; align-items: center; justify-content: center; padding: 12px; background: #f8f9fa; border-radius: 8px; text-decoration: none; color: #333; font-weight: 500; transition: all 0.2s; }
        .social-link:hover { background: #e91e63; color: white; transform: translateY(-3px); }
        .brand-kit { margin-top: 50px; text-align: center; }
        .brand-images { display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; margin-top: 20px; }
        .brand-img-container { background: white; padding: 10px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .brand-img { height: 80px; object-fit: contain; }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a href="index.html" class="logo">
                <img src="static/images/logo.png" alt="BandaWeb3 Logo" style="height: 40px; vertical-align: middle; margin-right: 10px;">
                <span class="logo-text">BandaWeb3</span>
            </a>
            <div class="nav-links">
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
    
    
    
    print("Website generated successfully at website/output/index.html")

if __name__ == "__main__":
    generate()
