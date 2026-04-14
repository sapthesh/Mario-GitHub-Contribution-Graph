import os
import json
import urllib.request

def fetch_contributions(username, token):
    """Fetches the user's contribution graph from GitHub GraphQL API."""
    query = """
    query($userName:String!) {
      user(login: $userName){
        contributionsCollection {
          contributionCalendar {
            weeks {
              contributionDays {
                contributionLevel
              }
            }
          }
        }
      }
    }
    """
    req = urllib.request.Request(
        'https://api.github.com/graphql',
        data=json.dumps({'query': query, 'variables': {'userName': username}}).encode('utf-8'),
        headers={'Authorization': f'Bearer {token}'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
    except Exception as e:
        print(f"Error fetching data from GitHub API: {e}")
        return []

def generate_mario_github_svg(filename="mario_contribution.svg"):
    username = os.environ.get("GITHUB_ACTOR")
    token = os.environ.get("GITHUB_TOKEN")
    
    if not username or not token:
        print("Missing GITHUB_ACTOR or GITHUB_TOKEN environment variables.")
        return

    weeks_data = fetch_contributions(username, token)
    
    # GitHub graph dimensions
    cell_size = 10
    gap = 4
    step = cell_size + gap
    cols = len(weeks_data) if weeks_data else 53
    rows = 7
    
    # Increased height for Mario AND a ground floor
    width = cols * step + 16
    height = (rows + 3) * step + 16 
    
    # Map GitHub API contribution levels to CSS classes
    level_map = {
        'NONE': 'empty',
        'FIRST_QUARTILE': 'lvl1',
        'SECOND_QUARTILE': 'lvl2',
        'THIRD_QUARTILE': 'lvl3',
        'FOURTH_QUARTILE': 'lvl4'
    }
    
    svg_elements = [
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
        '  <style>',
        '    .bg { fill: #0d1117; }',                      # GitHub Dark Mode Background
        '    .empty { fill: #161b22; rx: 2; ry: 2; }',     # Empty contribution
        '    .lvl1 { fill: #0e4429; rx: 2; ry: 2; }',      # Light green
        '    .lvl2 { fill: #006d32; rx: 2; ry: 2; }',
        '    .lvl3 { fill: #26a641; rx: 2; ry: 2; }',
        '    .lvl4 { fill: #39d353; rx: 2; ry: 2; }',      # Dark green
        '    .ground { fill: #8B4513; }',                  # Classic Mario Brown Brick Color
        '    .ground-top { fill: #5C2E0B; }',              # Darker brown for ground texture
        '  </style>',
        f'  <rect width="100%" height="100%" class="bg" />',
        '  <g transform="translate(8, 8)">'
    ]
    
    # --- GAME SETTINGS ---
    animation_duration = 15.0  # SLOWER: Increased from 8s to 15s
    mario_y = (rows + 1) * step # Mario runs 1 row below the grid
    ground_y = mario_y + cell_size # Ground is immediately below Mario

    # Draw the Ground Floor
    svg_elements.append(f'    <!-- Game Ground -->')
    svg_elements.append(f'    <rect x="0" y="{ground_y}" width="{cols * step}" height="{cell_size * 2}" class="ground" />')
    svg_elements.append(f'    <rect x="0" y="{ground_y}" width="{cols * step}" height="2" class="ground-top" />')

    # Generate the Grid and the Block Animations
    for col, week in enumerate(weeks_data):
        t_action = col / float(cols)
        t_end = min(1.0, t_action + 0.04) # Slower pop-up duration

        for row, day in enumerate(week['contributionDays']):
            lvl = level_map.get(day.get('contributionLevel', 'NONE'), 'empty')
            
            # Empty background block
            svg_elements.append(f'    <rect x="{col * step}" y="{row * step}" width="{cell_size}" height="{cell_size}" class="empty" />')
            
            # Colored contribution block
            if lvl != 'empty':
                start_y = mario_y 
                real_y = row * step 
                
                svg_elements.append(f'    <rect x="{col * step}" y="{start_y}" width="{cell_size}" height="{cell_size}" class="{lvl}">')
                
                # PHYSICS: calcMode="spline" makes it shoot up fast and gently brake at the top!
                svg_elements.append(
                    f'      <animate attributeName="y" values="{start_y};{start_y};{real_y};{real_y}" '
                    f'keyTimes="0;{t_action:.3f};{t_end:.3f};1" dur="{animation_duration}s" '
                    f'calcMode="spline" keySplines="0 0 1 1; 0.25 1 0.5 1; 0 0 1 1" repeatCount="indefinite" />'
                )
                
                # Opacity animation
                svg_elements.append(
                    f'      <animate attributeName="opacity" values="0;0;1;1" '
                    f'keyTimes="0;{t_action:.3f};{t_action+0.001:.3f};1" dur="{animation_duration}s" repeatCount="indefinite" />'
                )
                
                svg_elements.append('    </rect>')

    # Add Mario Character Animation
    # Using a base64 string of a tiny 8-bit mushroom/Mario as a fallback, but ready for a real image!
    svg_elements.append('    <!-- Mario Character -->')
    
    # To use your own image, you can change this href to a URL like "https://raw.githubusercontent.com/YourName/Repo/main/mario.png"
    fallback_mario_url = "https://upload.wikimedia.org/wikipedia/commons/3/39/Mario_Step.gif" 
    
    svg_elements.append(f'    <image href="{fallback_mario_url}" x="0" y="{mario_y - 4}" width="{cell_size + 6}" height="{cell_size + 6}">')
    svg_elements.append(f'      <animate attributeName="x" from="-20" to="{cols * step}" dur="{animation_duration}s" repeatCount="indefinite" />')
    svg_elements.append('    </image>')
    
    svg_elements.append('  </g>')
    svg_elements.append('</svg>')
    
    with open(filename, "w") as f:
        f.write("\n".join(svg_elements))
    print(f"Successfully generated {filename} with game physics and slower pacing!")

if __name__ == "__main__":
    generate_mario_github_svg()
