import os
import json
import urllib.request

def fetch_contributions(username, token):
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

def draw_sprite(name, pixels, colors, scale, is_def=True):
    """Helper to convert ASCII art into SVG pixels."""
    svg = [f'    <g id="{name}">'] if is_def else ['    <g>']
    for y_idx, row_str in enumerate(pixels):
        for x_idx, char in enumerate(row_str):
            if char in colors:
                px = x_idx * scale
                py = y_idx * scale
                svg.append(f'      <rect x="{px:.1f}" y="{py:.1f}" width="{scale}" height="{scale}" fill="{colors[char]}" />')
    svg.append('    </g>')
    return "\n".join(svg)

def generate_mario_github_svg(filename="mario_contribution.svg"):
    username = os.environ.get("GITHUB_ACTOR", "User")
    token = os.environ.get("GITHUB_TOKEN")
    
    weeks_data = fetch_contributions(username, token) if token else []
    
    # --- LEVEL LAYOUT SETTINGS ---
    cell_size = 10
    gap = 4
    step = cell_size + gap
    cols = len(weeks_data) if weeks_data else 53
    rows = 7
    
    # Add padding for the Pipe (left), Flagpole (right), and Clouds (top)
    grid_x_offset = 40
    top_padding = 40
    
    width = grid_x_offset + (cols * step) + 60
    height = top_padding + (rows * step) + 40 
    ground_y = top_padding + (rows * step)
    
    level_map = {
        'NONE': 'empty', 'FIRST_QUARTILE': 'lvl1',
        'SECOND_QUARTILE': 'lvl2', 'THIRD_QUARTILE': 'lvl3', 'FOURTH_QUARTILE': 'lvl4'
    }
    
    svg_elements = [
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
        '  <style>',
        '    .bg { fill: #87CEEB; }',                      # Classic Mario Sky Blue! (Changed from Dark Mode)
        '    .empty { fill: rgba(255,255,255,0.2); rx: 2; ry: 2; }',  # Translucent empty blocks
        '    .lvl1 { fill: #0e4429; rx: 2; ry: 2; stroke: #000; stroke-width: 0.5; }',      
        '    .lvl2 { fill: #006d32; rx: 2; ry: 2; stroke: #000; stroke-width: 0.5; }',
        '    .lvl3 { fill: #26a641; rx: 2; ry: 2; stroke: #000; stroke-width: 0.5; }',
        '    .lvl4 { fill: #39d353; rx: 2; ry: 2; stroke: #000; stroke-width: 0.5; }',      
        '    .ground { fill: #c84c0c; }',                  # Classic retro ground color
        '    .ground-top { fill: #000000; }',              
        '  </style>',
        '  <defs>'
    ]

    # --- PURE SVG PIXEL ART DEFINITIONS ---
    mario_pixels = [
        "  RRRRR     ", " RRRRRRRRR  ", " BBSSSO     ", " BOSSSOOOO  ",
        " BOSSSOOOO  ", "  BOOOOO    ", "  RROORR    ", " RRROORRR   ",
        " RRROORRRR  ", " SSRRRRYSS  ", " SSS  SSS   ", "BBBB  BBBB  "
    ]
    cloud_pixels = [
        "      WWWW      ", "   WWWWWWWWWW   ", " WWWWWWWWWWWWWW ", " WWWWWWWWWWWWWW "
    ]
    bush_pixels = [
        "      GGGG      ", "   GGGGGGGGGG   ", " GGGGGGGGGGGGGG ", " GGGGGGGGGGGGGG "
    ]
    coin_pixels = [
        "  YYYY  ", " YYOOYY ", " YOOOOY ", " YOOOOY ", " YYOOYY ", "  YYYY  "
    ]
    
    mario_colors = {'R': '#e52521', 'S': '#ffcca6', 'B': '#8B4513', 'O': '#2038ec', 'Y': '#f8d820'}
    cloud_colors = {'W': '#FFFFFF'}
    bush_colors = {'G': '#00A800'}
    coin_colors = {'Y': '#f8d820', 'O': '#d8a000'}

    mario_scale = 1.2
    mario_height = len(mario_pixels) * mario_scale
    
    svg_elements.append(draw_sprite("mario", mario_pixels, mario_colors, mario_scale))
    svg_elements.append(draw_sprite("cloud", cloud_pixels, cloud_colors, 2.0))
    svg_elements.append(draw_sprite("bush", bush_pixels, bush_colors, 2.0))
    svg_elements.append(draw_sprite("coin", coin_pixels, coin_colors, 1.2))
    svg_elements.append('  </defs>')
    
    # 1. DRAW BACKGROUND & SCENERY
    svg_elements.append(f'  <rect width="100%" height="100%" class="bg" />')
    
    # Moving Clouds (Parallax effect)
    svg_elements.append('  <!-- Parallax Clouds -->')
    for i in range(4):
        start_x = (i * 250)
        y_pos = 10 if i % 2 == 0 else 30
        duration = 40 + (i * 5) # Different speeds
        svg_elements.append(f'  <use href="#cloud" x="0" y="{y_pos}">')
        svg_elements.append(f'    <animate attributeName="x" from="{width}" to="-100" dur="{duration}s" repeatCount="indefinite" />')
        svg_elements.append(f'  </use>')

    # Ground & Bushes
    svg_elements.append(f'  <rect x="0" y="{ground_y}" width="{width}" height="{height - ground_y}" class="ground" />')
    svg_elements.append(f'  <rect x="0" y="{ground_y}" width="{width}" height="2" class="ground-top" />')
    
    svg_elements.append('  <!-- Static Bushes -->')
    for i in range(10):
        svg_elements.append(f'  <use href="#bush" x="{i * 120 + 30}" y="{ground_y - 8}" />')

    # 2. DRAW START PIPE
    pipe_width = 24
    pipe_top = ground_y - 30
    pipe_x = 10
    svg_elements.append('  <!-- Start Pipe -->')
    svg_elements.append(f'  <rect x="{pipe_x}" y="{pipe_top}" width="{pipe_width}" height="30" fill="#00A800" stroke="#000" stroke-width="1"/>')
    svg_elements.append(f'  <rect x="{pipe_x - 2}" y="{pipe_top}" width="{pipe_width + 4}" height="10" fill="#00A800" stroke="#000" stroke-width="1"/>')

    # 3. DRAW GRID, COINS, AND PATHFINDING
    path_d = f"M {pipe_x + 4} {ground_y} "               # Mario starts inside the pipe
    path_d += f"L {pipe_x + 4} {pipe_top - mario_height} " # Mario rises out of the pipe
    
    current_x = pipe_x + 4
    current_y = pipe_top - mario_height
    
    for col, week in enumerate(weeks_data):
        highest_block_row = rows # Default to ground level
        col_x = grid_x_offset + col * step
        
        for row, day in enumerate(week['contributionDays']):
            lvl = level_map.get(day.get('contributionLevel', 'NONE'), 'empty')
            block_y = top_padding + row * step
            
            svg_elements.append(f'  <rect x="{col_x}" y="{block_y}" width="{cell_size}" height="{cell_size}" class="{lvl}" />')
            
            # Draw a Coin above Level 4 days!
            if lvl == 'lvl4':
                coin_y = block_y - 12
                svg_elements.append(f'  <use href="#coin" x="{col_x + 1}" y="{coin_y}">')
                # Coin bobbing animation
                svg_elements.append(f'    <animate attributeName="y" values="{coin_y};{coin_y-4};{coin_y}" dur="1.5s" repeatCount="indefinite" />')
                svg_elements.append(f'  </use>')
            
            # Find the highest block for Mario to step on
            if lvl != 'empty' and row < highest_block_row:
                highest_block_row = row
        
        # Calculate Mario's target position
        target_x = col_x
        target_y = (top_padding + highest_block_row * step) - mario_height
        
        if target_y != current_y: # JUMP!
            control_x = current_x + (target_x - current_x) / 2
            control_y = min(current_y, target_y) - 25 # Jump arc height
            path_d += f" Q {control_x} {control_y} {target_x} {target_y}"
        else: # RUN!
            path_d += f" L {target_x} {target_y}"
            
        current_x = target_x
        current_y = target_y

    # 4. DRAW END FLAGPOLE
    flag_x = grid_x_offset + (cols * step) + 15
    flag_top = top_padding - 10
    svg_elements.append('  <!-- End Flagpole -->')
    # Pole
    svg_elements.append(f'  <rect x="{flag_x}" y="{flag_top}" width="3" height="{ground_y - flag_top}" fill="#FFF" stroke="#000" stroke-width="0.5"/>')
    # Ball on top
    svg_elements.append(f'  <circle cx="{flag_x + 1.5}" cy="{flag_top}" r="4" fill="#f8d820" stroke="#000" stroke-width="0.5"/>')
    # Green Flag
    svg_elements.append(f'  <polygon points="{flag_x-15},{flag_top+5} {flag_x},{flag_top+5} {flag_x},{flag_top+15}" fill="#00A800" stroke="#000" stroke-width="0.5"/>')
    # Castle Base Block
    svg_elements.append(f'  <rect x="{flag_x - 5}" y="{ground_y - 10}" width="13" height="10" fill="#c84c0c" stroke="#000" stroke-width="1"/>')

    # Path to finish the level
    path_d += f" Q {current_x + 10} {current_y - 20} {flag_x - 4} {flag_top + 10}" # Jump to flag
    path_d += f" L {flag_x - 4} {ground_y - mario_height}"                         # Slide down
    path_d += f" L {width + 20} {ground_y - mario_height}"                         # Walk off screen

    # 5. ATTACH MARIO TO PATH
    svg_elements.append(f'  <path id="parkour-path" d="{path_d}" fill="none" stroke="none" />')
    svg_elements.append('  <use href="#mario">')
    # A 22-second epic animation to match the grand scale of the level
    svg_elements.append(f'    <animateMotion dur="22s" repeatCount="indefinite">')
    svg_elements.append(f'      <mpath href="#parkour-path"/>')
    svg_elements.append(f'    </animateMotion>')
    svg_elements.append('  </use>')
    
    svg_elements.append('</svg>')
    
    with open(filename, "w") as f:
        f.write("\n".join(svg_elements))
    print(f"Successfully generated Ultimate {filename}!")

if __name__ == "__main__":
    generate_mario_github_svg()
