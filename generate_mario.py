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
    
    # Increase height to give Mario room to run at the bottom
    width = cols * step + 16
    height = (rows + 2) * step + 16 
    
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
        '    .mario { fill: #e52521; rx: 2; ry: 2; }',     # Mario Red
        '  </style>',
        f'  <rect width="100%" height="100%" class="bg" />',
        '  <g transform="translate(8, 8)">'
    ]
    
    animation_duration = 8.0  # Total time for Mario to run across the screen
    mario_y = (rows + 1) * step # Mario runs 1 row below the grid

    # 1. Generate the Grid and the Block Animations
    for col, week in enumerate(weeks_data):
        # Calculate when Mario passes this column
        t_action = col / float(cols)
        # The block finishes moving shortly after Mario passes
        t_end = min(1.0, t_action + 0.05) 

        for row, day in enumerate(week['contributionDays']):
            lvl = level_map.get(day.get('contributionLevel', 'NONE'), 'empty')
            
            # Draw the empty background block first so the grid looks complete
            svg_elements.append(f'    <rect x="{col * step}" y="{row * step}" width="{cell_size}" height="{cell_size}" class="empty" />')
            
            # If the user made a commit, animate the colored block shooting up
            if lvl != 'empty':
                start_y = mario_y  # Block starts at Mario's position at the bottom
                real_y = row * step # Block's final resting place
                
                svg_elements.append(f'    <rect x="{col * step}" y="{start_y}" width="{cell_size}" height="{cell_size}" class="{lvl}">')
                
                # Animate Y-axis (Shooting up from the bottom)
                svg_elements.append(f'      <animate attributeName="y" values="{start_y};{start_y};{real_y};{real_y}" keyTimes="0;{t_action:.3f};{t_end:.3f};1" dur="{animation_duration}s" repeatCount="indefinite" />')
                
                # Animate Opacity (Invisible until Mario gets there)
                svg_elements.append(f'      <animate attributeName="opacity" values="0;0;1;1" keyTimes="0;{t_action:.3f};{t_action+0.001:.3f};1" dur="{animation_duration}s" repeatCount="indefinite" />')
                
                svg_elements.append('    </rect>')

    # 2. Add Mario Character Animation
    svg_elements.append('    <!-- Mario Character -->')
    svg_elements.append(f'    <rect y="{mario_y}" width="{cell_size}" height="{cell_size}" class="mario">')
    # Mario slides across the bottom continuously
    svg_elements.append(f'      <animate attributeName="x" from="0" to="{cols * step}" dur="{animation_duration}s" repeatCount="indefinite" />')
    svg_elements.append('    </rect>')
    
    svg_elements.append('  </g>')
    svg_elements.append('</svg>')
    
    # Write to file
    with open(filename, "w") as f:
        f.write("\n".join(svg_elements))
    print(f"Successfully generated {filename} using real GitHub data!")

if __name__ == "__main__":
    generate_mario_github_svg()
