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
    
    # Grid Settings
    cell_size = 10
    gap = 4
    step = cell_size + gap
    cols = len(weeks_data) if weeks_data else 53
    rows = 7
    
    # SVG Dimensions
    width = cols * step + 16
    height = (rows + 3) * step + 16 
    ground_row = rows  # The row immediately below the grid is the ground
    
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
        '    .bg { fill: #0d1117; }',                      
        '    .empty { fill: #161b22; rx: 2; ry: 2; }',     
        '    .lvl1 { fill: #0e4429; rx: 2; ry: 2; }',      
        '    .lvl2 { fill: #006d32; rx: 2; ry: 2; }',
        '    .lvl3 { fill: #26a641; rx: 2; ry: 2; }',
        '    .lvl4 { fill: #39d353; rx: 2; ry: 2; }',      
        '    .ground { fill: #8B4513; }',                  
        '    .ground-top { fill: #5C2E0B; }',              
        '  </style>',
        '  <defs>'
    ]

    # --- PURE SVG PIXEL ART MARIO ---
    # This completely bypasses GitHub's image blocker!
    mario_pixels = [
        "  RRRRR     ",
        " RRRRRRRRR  ",
        " BBSSSO     ",
        " BOSSSOOOO  ",
        " BOSSSOOOO  ",
        "  BOOOOO    ",
        "  RROORR    ",
        " RRROORRR   ",
        " RRROORRRR  ",
        " SSRRRRYSS  ",
        " SSS  SSS   ",
        "BBBB  BBBB  "
    ]
    colors = {'R': '#e52521', 'S': '#ffcca6', 'B': '#8B4513', 'O': '#2038ec', 'Y': '#f8d820'}
    
    mario_scale = 1.2
    mario_height = len(mario_pixels) * mario_scale
    
    svg_elements.append('    <g id="mario">')
    for y_idx, row_str in enumerate(mario_pixels):
        for x_idx, char in enumerate(row_str):
            if char in colors:
                px = x_idx * mario_scale
                py = y_idx * mario_scale
                svg_elements.append(f'      <rect x="{px:.1f}" y="{py:.1f}" width="{mario_scale}" height="{mario_scale}" fill="{colors[char]}" />')
    svg_elements.append('    </g>')
    svg_elements.append('  </defs>')
    
    # Draw Background
    svg_elements.append(f'  <rect width="100%" height="100%" class="bg" />')
    svg_elements.append('  <g transform="translate(8, 8)">')

    # Draw Ground
    ground_y = ground_row * step
    svg_elements.append(f'    <rect x="0" y="{ground_y}" width="{cols * step}" height="{cell_size * 2}" class="ground" />')
    svg_elements.append(f'    <rect x="0" y="{ground_y}" width="{cols * step}" height="2" class="ground-top" />')

    # --- PARKOUR PATHFINDING ALGORITHM ---
    path_d = f"M -20 {ground_y - mario_height}"  # Start off-screen at ground level
    current_y = ground_y - mario_height

    # Draw the static grid AND calculate Mario's path simultaneously
    for col, week in enumerate(weeks_data):
        highest_block_row = ground_row # Default to ground level
        
        for row, day in enumerate(week['contributionDays']):
            lvl = level_map.get(day.get('contributionLevel', 'NONE'), 'empty')
            
            # Draw the grid block
            svg_elements.append(f'    <rect x="{col * step}" y="{row * step}" width="{cell_size}" height="{cell_size}" class="{lvl}" />')
            
            # Find the highest block for Mario to step on
            if lvl != 'empty' and row < highest_block_row:
                highest_block_row = row
        
        # Calculate Mario's target position for this column
        target_x = col * step
        target_y = (highest_block_row * step) - mario_height
        
        if target_y != current_y:
            # Mario jumps or falls! Draw a curved path (Q)
            control_x = target_x - (step / 2)
            # Make the jump arc a bit higher than the peak for game physics
            control_y = min(current_y, target_y) - 20 
            path_d += f" Q {control_x} {control_y} {target_x} {target_y}"
        else:
            # Mario runs straight across the blocks or ground (L)
            path_d += f" L {target_x} {target_y}"
            
        current_y = target_y

    # Have Mario run off the screen at the end
    path_d += f" L {cols * step + 20} {current_y}"

    # Embed the invisible motion path
    svg_elements.append(f'    <path id="parkour-path" d="{path_d}" fill="none" stroke="none" />')

    # Attach Mario to the path!
    svg_elements.append('    <use href="#mario">')
    svg_elements.append(f'      <animateMotion dur="15s" repeatCount="indefinite">')
    svg_elements.append(f'        <mpath href="#parkour-path"/>')
    svg_elements.append(f'      </animateMotion>')
    svg_elements.append('    </use>')
    
    svg_elements.append('  </g>')
    svg_elements.append('</svg>')
    
    with open(filename, "w") as f:
        f.write("\n".join(svg_elements))
    print(f"Successfully generated {filename} with Pure SVG Mario and Parkour physics!")

if __name__ == "__main__":
    generate_mario_github_svg()
