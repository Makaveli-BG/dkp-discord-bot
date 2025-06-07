import io
import logging
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.ticker import FuncFormatter

logger = logging.getLogger("dkp_bot.charts")

# Set up the style for all charts
def setup_chart_style():
    """Set up a custom dark theme visual style for all charts"""
    # Custom dark theme
    plt.style.use('dark_background')
    
    # Define custom colors
    background_color = '#1E1E1E'  # Dark background
    text_color = '#E0E0E0'        # Light text
    grid_color = '#333333'        # Dark grid
    
    # Set figure size and DPI
    plt.rcParams['figure.figsize'] = (12, 7)
    plt.rcParams['figure.dpi'] = 100
    
    # Font configuration
    plt.rcParams['font.size'] = 12
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans', 'sans-serif']
    plt.rcParams['font.family'] = 'sans-serif'
    
    # Text sizes
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['axes.titlesize'] = 18
    plt.rcParams['xtick.labelsize'] = 12
    plt.rcParams['ytick.labelsize'] = 12
    
    # Custom colors
    plt.rcParams['figure.facecolor'] = background_color
    plt.rcParams['axes.facecolor'] = background_color
    plt.rcParams['axes.edgecolor'] = grid_color
    plt.rcParams['axes.labelcolor'] = text_color
    plt.rcParams['text.color'] = text_color
    plt.rcParams['xtick.color'] = text_color
    plt.rcParams['ytick.color'] = text_color
    plt.rcParams['grid.color'] = grid_color
    
    # Line styles
    plt.rcParams['grid.linestyle'] = '--'
    plt.rcParams['grid.linewidth'] = 0.5
    plt.rcParams['axes.linewidth'] = 1.0
    
    # Custom palette for better visibility on dark background
    sns.set_palette(['#FF5733', '#33A8FF', '#58FF33', '#FF33E9', '#FFD133', '#33FFC1'])

def generate_dkp_chart(user_data):
    """Generate a modern, dark-themed chart showing the breakdown of user's DKP stats"""
    try:
        setup_chart_style()
        
        # Extract DKP-related fields
        dkp_data = {}
        for key, value in user_data.items():
            if 'DKP' in key and key != 'DKP SCORE':
                try:
                    if isinstance(value, str):
                        value = int(value.replace(',', ''))
                    # Sanitize keys to remove problematic characters
                    safe_key = ''.join([c if ord(c) < 128 else '' for c in key])
                    if not safe_key:  # If key becomes empty after sanitization
                        safe_key = f"DKP Type {len(dkp_data) + 1}"
                    dkp_data[safe_key] = value
                except (ValueError, TypeError):
                    dkp_data[key] = 0
        
        if not dkp_data:
            # If no DKP data found, create a simple chart with total score
            labels = ['Total DKP']
            values = [int(user_data.get('DKP SCORE', '0').replace(',', '')) if isinstance(user_data.get('DKP SCORE', '0'), str) else user_data.get('DKP SCORE', 0)]
        else:
            # Sort data by value for better visualization
            labels = list(dkp_data.keys())
            values = list(dkp_data.values())
            
            # Sort both lists based on values
            sorted_pairs = sorted(zip(labels, values), key=lambda x: x[1], reverse=True)
            labels, values = zip(*sorted_pairs) if sorted_pairs else ([], [])
        
        # Create figure with dark theme
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Create a gradient color map for the bars
        cmap = plt.cm.get_cmap('viridis', len(labels))
        colors = [cmap(i) for i in range(len(labels))]
        
        # Add subtle reflection effect
        alpha_gradient = np.linspace(0.7, 0.2, 100)
        
        # Create a stylish bar chart with a gradient effect
        bars = ax.bar(
            labels, 
            values, 
            width=0.6,
            color=colors,
            edgecolor='#333333',
            linewidth=0.5,
            alpha=0.9,
            zorder=10
        )
        
        # Add a reflection effect below each bar
        for i, bar in enumerate(bars):
            x = bar.get_x()
            y = 0
            width = bar.get_width()
            height = bar.get_height()
            reflection_height = height * 0.1  # 10% of the bar height
            
            # Draw reflection as a gradient
            for j, alpha in enumerate(alpha_gradient):
                if j < len(alpha_gradient) - 1:
                    reflection_slice = reflection_height / len(alpha_gradient)
                    rect = plt.Rectangle(
                        (x, y + j * reflection_slice),
                        width,
                        reflection_slice,
                        alpha=alpha,
                        color=colors[i],
                        zorder=5
                    )
                    ax.add_patch(rect)
        
        # Add a glowing effect to the bars
        for bar in bars:
            x, y = bar.get_xy()
            w, h = bar.get_width(), bar.get_height()
            glow = plt.Rectangle(
                (x-0.03*w, y-0.01*h),
                1.06*w,
                1.02*h,
                fill=False,
                alpha=0.3,
                color='white',
                linewidth=1.5,
                zorder=1
            )
            ax.add_patch(glow)
        
        # Add value labels on top of bars with custom styling
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2., 
                height + (max(values) * 0.02),  # Position slightly above bar
                f'{int(height):,}',
                ha='center', 
                va='bottom',
                fontweight='bold',
                color='#FFFFFF',
                fontsize=13,
                zorder=20,
                path_effects=[plt.patheffects.withStroke(linewidth=2, foreground='#000000')]  # Text outline for better visibility
            )
        
        # Set chart title and labels with custom styling
        in_game_name = user_data.get('In-Game Name', 'Unknown')
        ax.set_title(f'DKP Breakdown for {in_game_name}', fontsize=20, fontweight='bold', color='#FFFFFF',
                    path_effects=[plt.patheffects.withStroke(linewidth=3, foreground='#000000')])
        
        ax.set_xlabel('DKP Categories', fontsize=14, fontweight='bold', color='#CCCCCC')
        ax.set_ylabel('Points', fontsize=14, fontweight='bold', color='#CCCCCC')
        
        # Format y-axis with comma separators
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x):,}'))
        
        # Customize x-axis labels
        plt.xticks(rotation=30, ha='right', color='#CCCCCC', fontweight='bold')
        plt.yticks(color='#CCCCCC')
        
        # Add a stylish grid for better readability
        ax.grid(axis='y', linestyle='--', alpha=0.3, color='#AAAAAA', zorder=0)
        
        # Add subtle "live data" elements - animated dots in the background
        for i in range(20):
            x = np.random.uniform(0, len(labels)-1)
            y = np.random.uniform(0, max(values) * 0.8)
            size = np.random.uniform(10, 50)
            alpha = np.random.uniform(0.05, 0.15)
            ax.scatter(x, y, s=size, alpha=alpha, color='cyan', edgecolor=None, zorder=1)
        
        # Add a sleek border around the plot
        for spine in ax.spines.values():
            spine.set_edgecolor('#555555')
            spine.set_linewidth(1.5)
        
        # Add a subtle gradient background
        gradient = np.linspace(0, 1, 100).reshape(-1, 1)
        gradient = np.repeat(gradient, 10, axis=1)
        extent = [ax.get_xlim()[0], ax.get_xlim()[1], ax.get_ylim()[0], ax.get_ylim()[1]]
        ax.imshow(gradient, aspect='auto', extent=extent, alpha=0.1, zorder=0, cmap='Blues_r')
        
        # Add a watermark-style "DKP Stats" text
        fig.text(0.5, 0.02, "DKP Statistics", ha='center', va='bottom', color='#555555', 
                alpha=0.5, fontsize=14, fontweight='bold')
        
        # Add data timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        fig.text(0.95, 0.02, f"Generated: {timestamp}", ha='right', va='bottom', 
                color='#777777', alpha=0.7, fontsize=9)
        
        # Adjust layout
        plt.tight_layout(pad=2.0)
        
        # Save chart to a bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, facecolor='#1E1E1E')
        buf.seek(0)
        plt.close()
        
        return buf
    except Exception as e:
        logger.error(f"Error generating DKP chart: {e}")
        # Return a simple error chart
        plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, "Error generating chart", ha='center', va='center', fontsize=20, color='white')
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', facecolor='#1E1E1E')
        buf.seek(0)
        plt.close()
        return buf

def generate_comparison_chart(sheets_manager, user_data):
    """Generate a modern, dark-themed chart comparing the user's DKP with top players"""
    try:
        setup_chart_style()
        
        # Get top players
        top_players = sheets_manager.get_top_players(5)  # Get top 5
        
        # Extract user's data
        user_id = user_data.get('ID', '')
        user_name = user_data.get('In-Game Name', 'Unknown')
        try:
            user_dkp = int(user_data.get('DKP SCORE', '0').replace(',', '')) if isinstance(user_data.get('DKP SCORE', '0'), str) else user_data.get('DKP SCORE', 0)
        except (ValueError, TypeError):
            user_dkp = 0
        
        # Prepare data for chart
        names = []
        scores = []
        colors = []
        is_user = []  # Track which bar represents the user
        
        # Check if user is in top players, if not add them
        user_in_top = False
        
        for player in top_players:
            player_id = player.get('ID', '')
            # Sanitize player names to remove problematic characters
            player_name = player.get('In-Game Name', 'Unknown')
            safe_name = ''.join([c if ord(c) < 128 else '' for c in player_name])
            if not safe_name:  # If name becomes empty after sanitization
                safe_name = f"Player {len(names) + 1}"
                
            player_dkp = player.get('DKP SCORE', 0)
            
            names.append(safe_name)
            scores.append(player_dkp)
            
            if player_id == user_id:
                user_in_top = True
                colors.append('#FF5733')  # Highlight user's bar - orange
                is_user.append(True)
            else:
                colors.append('#3498DB')  # Default color for others - blue
                is_user.append(False)
        
        # If user is not in top players, add them to the chart
        if not user_in_top:
            names.append(user_name)
            scores.append(user_dkp)
            colors.append('#FF5733')
            is_user.append(True)
            
            # Sort data to maintain descending order
            sorted_data = sorted(zip(names, scores, colors, is_user), key=lambda x: x[1], reverse=True)
            names, scores, colors, is_user = zip(*sorted_data)
        
        # Create figure with dark theme
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Create a stylish horizontal bar chart 
        bars = ax.barh(
            names, 
            scores, 
            height=0.6,
            color=colors,
            edgecolor='#333333',
            linewidth=0.5,
            alpha=0.9,
            zorder=10
        )
        
        # Add glow effect for user's bar
        for i, bar in enumerate(bars):
            if is_user[i]:
                x, y = bar.get_xy()
                w, h = bar.get_width(), bar.get_height()
                
                # Multiple glows for a more intense effect
                for scale in [1.01, 1.02, 1.03]:
                    glow = plt.Rectangle(
                        (x, y - 0.02 * h),
                        w * scale,
                        h * 1.04,
                        fill=False,
                        alpha=0.3 / scale,
                        color='#FFA07A',  # Light salmon for glow
                        linewidth=2,
                        zorder=1
                    )
                    ax.add_patch(glow)
                
                # Add a "YOU" indicator
                ax.text(
                    w * 0.98, 
                    y + h/2,
                    " YOU",
                    ha='left',
                    va='center',
                    color='#FF5733',
                    fontweight='bold',
                    fontsize=14,
                    path_effects=[plt.patheffects.withStroke(linewidth=3, foreground='#000000')],
                    zorder=20
                )
        
        # Add fancy value labels with gradient backgrounds for each bar
        for i, bar in enumerate(bars):
            width = bar.get_width()
            label_x = width * 0.02  # Position at 2% from start of bar
            
            # Add background for text (rounded rectangle)
            text_bg = plt.Rectangle(
                (0, bar.get_y() + 0.1 * bar.get_height()),
                label_x * 2.5,
                bar.get_height() * 0.8,
                alpha=0.7,
                color='#111111',
                zorder=15,
                edgecolor='#444444',
                linewidth=1
            )
            ax.add_patch(text_bg)
            
            # Add score text
            ax.text(
                label_x,
                bar.get_y() + bar.get_height()/2,
                f'{int(width):,}',
                ha='left',
                va='center',
                fontweight='bold',
                color='white',
                fontsize=13,
                zorder=20
            )
        
        # Set chart title and labels with custom styling
        ax.set_title('DKP Comparison with Top Players', fontsize=20, fontweight='bold', color='#FFFFFF',
                    path_effects=[plt.patheffects.withStroke(linewidth=3, foreground='#000000')])
        
        ax.set_xlabel('Total DKP Score', fontsize=14, fontweight='bold', color='#CCCCCC')
        ax.set_ylabel('Players', fontsize=14, fontweight='bold', color='#CCCCCC')
        
        # Format x-axis with comma separators
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x):,}'))
        
        # Customize axis labels
        plt.yticks(color='#CCCCCC', fontweight='bold', fontsize=13)
        plt.xticks(color='#CCCCCC')
        
        # Add a stylish grid
        ax.grid(axis='x', linestyle='--', alpha=0.3, color='#AAAAAA', zorder=0)
        
        # Remove top and right spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Add rank numbers next to player names
        for i, (name, score) in enumerate(zip(names, scores)):
            rank = i + 1
            rank_suffix = 'st' if rank == 1 else 'nd' if rank == 2 else 'rd' if rank == 3 else 'th'
            
            # Create a circular background for rank
            circle = plt.Circle(
                (ax.get_xlim()[0] - max(scores) * 0.08, ax.get_yticks()[i]), 
                0.25,
                color='#333333',
                alpha=0.8,
                zorder=5
            )
            ax.add_patch(circle)
            
            # Add rank text
            ax.text(
                ax.get_xlim()[0] - max(scores) * 0.08,
                ax.get_yticks()[i],
                f'{rank}{rank_suffix}',
                ha='center',
                va='center',
                color='#FFFFFF',
                fontweight='bold',
                fontsize=12,
                zorder=10
            )
        
        # Add a progress bar look to the bars
        for bar in bars:
            x, y = bar.get_xy()
            w, h = bar.get_width(), bar.get_height()
            
            # Create stripes pattern
            for j in range(0, int(w), int(max(scores) / 50)):
                if j + int(max(scores) / 150) < w:  # Ensure stripe is within bar
                    stripe = plt.Rectangle(
                        (x + j, y),
                        int(max(scores) / 150),  # Width of stripe
                        h,
                        color='white',
                        alpha=0.05,
                        zorder=11
                    )
                    ax.add_patch(stripe)
        
        # Add animated-looking "data points"
        for i in range(30):
            x_pos = np.random.uniform(0, max(scores) * 0.9)
            y_pos = np.random.uniform(ax.get_ylim()[0], ax.get_ylim()[1])
            size = np.random.uniform(5, 30)
            alpha = np.random.uniform(0.05, 0.2)
            
            ax.scatter(x_pos, y_pos, s=size, alpha=alpha, color='cyan', edgecolor=None, zorder=1)
        
        # Add "live data" text with glow effect
        from matplotlib.patheffects import withStroke
        
        fig.text(
            0.02, 0.02, 
            "LIVE DKP DATA", 
            color='#00FF00', 
            fontsize=12, 
            fontweight='bold',
            alpha=0.8,
            path_effects=[withStroke(linewidth=3, foreground='#003300')]
        )
        
        # Add a timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        fig.text(
            0.98, 0.02, 
            f"Updated: {timestamp}", 
            ha='right', 
            color='#999999', 
            fontsize=10,
            alpha=0.7
        )
        
        # Adjust layout
        plt.tight_layout(pad=2.0)
        
        # Set figure background
        fig.patch.set_facecolor('#1E1E1E')
        
        # Save chart to a bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, facecolor='#1E1E1E', edgecolor='none')
        buf.seek(0)
        plt.close()
        
        return buf
    except Exception as e:
        logger.error(f"Error generating comparison chart: {e}")
        # Return a simple error chart
        plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, "Error generating comparison chart", ha='center', va='center', fontsize=20, color='white')
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', facecolor='#1E1E1E')
        buf.seek(0)
        plt.close()
        return buf scores[user_index]
            plt.annotate(
                'You are here',
                xy=(user_index, user_score),
                xytext=(user_index, user_score + max(scores) * 0.15),
                arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=7),
                horizontalalignment='center',
                fontsize=12,
                fontweight='bold'
            )
        
def generate_leaderboard_chart(sheets_manager, limit=10):
    """Generate a stylish leaderboard chart showing top DKP players"""
    try:
        setup_chart_style()
        
        # Get top players
        top_players = sheets_manager.get_top_players(limit)
        
        # Prepare data for chart
        names = []
        scores = []
        ranks = []
        
        for i, player in enumerate(top_players):
            player_name = player.get('In-Game Name', f'Player {i+1}')
            # Sanitize player names
            safe_name = ''.join([c if ord(c) < 128 else '' for c in player_name])
            if not safe_name:
                safe_name = f"Player {i+1}"
                
            player_dkp = player.get('DKP SCORE', 0)
            
            names.append(safe_name)
            scores.append(player_dkp)
            ranks.append(i + 1)
        
        # Create figure with dark theme
        fig, ax = plt.subplots(figsize=(12, max(7, len(names)*0.5)))
        
        # Create a horizontal bar chart
        bars = ax.barh(
            names[::-1],  # Reverse to have #1 at the top
            scores[::-1], 
            height=0.65,
            color=plt.cm.viridis(np.linspace(0, 0.8, len(names)))[::-1],  # Gradient colors
            edgecolor='#333333',
            linewidth=0.5,
            alpha=0.9,
            zorder=10
        )
        
        # Add reflections to bars
        for bar in bars:
            x, y = bar.get_xy()
            w, h = bar.get_width(), bar.get_height()
            
            # Add glossy highlight
            highlight = plt.Rectangle(
                (x, y),
                w,
                h * 0.4,
                color='white',
                alpha=0.1,
                zorder=11
            )
            ax.add_patch(highlight)
            
            # Add 3D-like shadow
            shadow = plt.Rectangle(
                (x, y - h * 0.05),
                w,
                h * 0.05,
                color='black',
                alpha=0.3,
                zorder=9
            )
            ax.add_patch(shadow)
        
        # Add rank medals for top 3
        medal_colors = ['#FFD700', '#C0C0C0', '#CD7F32']  # Gold, Silver, Bronze
        medal_names = ['🥇', '🥈', '🥉']
        
        # Add special effects for top 3 players
        for i in range(min(3, len(bars))):
            bar = bars[i]
            x, y = bar.get_xy()
            w, h = bar.get_width(), bar.get_height()
            
            # Add a special glow effect
            for j in range(3):
                glow = plt.Rectangle(
                    (x - j*2, y - j*0.05),
                    w + j*4,
                    h + j*0.1,
                    fill=False,
                    color=medal_colors[i],
                    alpha=0.3 - j*0.08,
                    linewidth=2,
                    zorder=8
                )
                ax.add_patch(glow)
            
            # Add medal icon
            ax.text(
                0,
                y + h/2,
                medal_names[i] + " ",
                ha='right',
                va='center',
                fontsize=16,
                fontweight='bold',
                path_effects=[plt.patheffects.withStroke(linewidth=3, foreground='#000000')],
                zorder=12
            )
        
        # Add value labels for each bar
        for i, bar in enumerate(bars):
            width = bar.get_width()
            rank = len(bars) - i  # Reverse to match bar order
            
            # Add background for score
            score_bg = plt.Rectangle(
                (width - width*0.15, bar.get_y() + 0.1 * bar.get_height()),
                width*0.18,
                bar.get_height() * 0.8,
                alpha=0.7,
                color='#111111',
                zorder=15,
                edgecolor='#444444',
                linewidth=1
            )
            ax.add_patch(score_bg)
            
            # Add score text
            ax.text(
                width - width*0.06,
                bar.get_y() + bar.get_height()/2,
                f'{int(width):,}',
                ha='center',
                va='center',
                fontweight='bold',
                color='white',
                fontsize=12,
                zorder=20
            )
            
            # Add indicator lines
            ax.plot(
                [0, width],
                [bar.get_y(), bar.get_y()],
                color='#444444',
                linestyle=':',
                linewidth=0.5,
                alpha=0.3,
                zorder=1
            )
        
        # Set chart title with special styling
        title_text = ax.set_title(
            'DKP Leaderboard', 
            fontsize=24, 
            fontweight='bold', 
            color='#FFFFFF',
            pad=20,
            path_effects=[plt.patheffects.withStroke(linewidth=3, foreground='#000000')]
        )
        
        # Add subtitle
        ax.text(
            0.5, 1.05,
            f"Top {len(names)} Players",
            transform=ax.transAxes,
            ha='center',
            va='center',
            fontsize=14,
            color='#AAAAAA',
            alpha=0.8
        )
        
        # Set axis labels with custom styling
        ax.set_xlabel('DKP Score', fontsize=14, fontweight='bold', color='#CCCCCC', labelpad=10)
        ax.set_ylabel('', fontsize=14)  # Empty label
        
        # Format x-axis with comma separators
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x):,}'))
        
        # Customize axis appearance
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#444444')
        ax.spines['bottom'].set_color('#444444')
        
        # Add a stylish grid
        ax.grid(axis='x', linestyle='--', alpha=0.2, color='#AAAAAA', zorder=0)
        
        # Customize axis labels
        plt.yticks(color='#CCCCCC', fontweight='bold')
        plt.xticks(color='#AAAAAA')
        
        # Add "data points" for dynamic effect
        for i in range(40):
            x_pos = np.random.uniform(0, max(scores))
            y_pos = np.random.uniform(0, len(names)-1)
            size = np.random.uniform(5, 20)
            alpha = np.random.uniform(0.05, 0.15)
            
            ax.scatter(x_pos, y_pos, s=size, alpha=alpha, color='cyan', edgecolor=None, zorder=2)
        
        # Add a timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        fig.text(
            0.98, 0.02, 
            f"Updated: {timestamp}", 
            ha='right', 
            color='#999999', 
            fontsize=10,
            alpha=0.7
        )
        
        # Add server name
        fig.text(
            0.02, 0.02, 
            "DKP LEADERBOARD", 
            color='#00FF00', 
            fontsize=12, 
            fontweight='bold',
            alpha=0.8,
            path_effects=[plt.patheffects.withStroke(linewidth=3, foreground='#003300')]
        )
        
        # Adjust layout
        plt.tight_layout(pad=2.5)
        
        # Save chart to a bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, facecolor='#1E1E1E', edgecolor='none')
        buf.seek(0)
        plt.close()
        
        return buf
    except Exception as e:
        logger.error(f"Error generating leaderboard chart: {e}")
        # Return a simple error chart
        plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, "Error generating leaderboard", ha='center', va='center', fontsize=20, color='white')
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', facecolor='#1E1E1E')
        buf.seek(0)
        plt.close()
        return buf
        
        # Adjust layout
        plt.tight_layout()
        
        # Save chart to a bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()
        
        return buf
    except Exception as e:
        logger.error(f"Error generating comparison chart: {e}")
        # Return a simple error chart
        plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, "Error generating comparison chart", ha='center', va='center', fontsize=20)
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        return buf