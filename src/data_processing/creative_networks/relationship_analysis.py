"""Creative Network Relationship Analysis.

This module analyzes the relationships between networks and creative talent,
focusing on talent pools and role distributions.
"""

import logging
from pathlib import Path
from typing import Dict, List, Set

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)

class RelationshipAnalyzer:
    """Analyzer for network-creative relationships."""
    
    def __init__(self, shows_df: pd.DataFrame, team_df: pd.DataFrame):
        """Initialize the analyzer.
        
        Args:
            shows_df: DataFrame containing show information
            team_df: DataFrame containing team member information
        """
        self.shows_df = shows_df
        self.team_df = team_df
        
        # Merge shows and team data
        self.combined_df = pd.merge(
            self.team_df,
            self.shows_df[['show_name', 'network']],
            on='show_name'
        )
        
        # Log basic stats
        logger.info("Network-creative relationship stats:")
        network_counts = self.combined_df['network'].nunique()
        creator_counts = self.combined_df['name'].nunique()
        logger.info(f"  Networks: {network_counts}")
        logger.info(f"  Unique creators: {creator_counts}")
    
    def analyze_talent_pools(self) -> Dict:
        """Analyze network talent pools and relationships.
        
        Returns:
            Dictionary containing:
            - network_talent_sizes: Size of each network's talent pool by role
            - exclusive_talent: Creators who work with only one network
            - shared_talent: Creators who work with multiple networks
            - network_overlap: Pairs of networks that share talent
        """
        # Filter out networks with minimal data points
        MIN_SHOWS = 3  # Minimum shows for a network to be included
        network_show_counts = self.shows_df['network'].value_counts()
        valid_networks = network_show_counts[network_show_counts >= MIN_SHOWS].index
        filtered_df = self.combined_df[self.combined_df['network'].isin(valid_networks)]
        
        # Get unique creator-network pairs
        creator_networks = filtered_df.groupby('name')['network'].unique()
        
        # Calculate network talent sizes with role breakdowns
        network_talent_sizes = {}
        for network in valid_networks:
            network_df = filtered_df[filtered_df['network'] == network]
            
            # Get overall unique creator count
            unique_creators = network_df['name'].nunique()
            
            # Get role breakdowns
            role_counts = {}
            for role in ['Writer', 'Director', 'Executive Producer', 'Producer', 'Showrunner']:
                role_creators = network_df[network_df['roles'].str.contains(role, na=False)]['name'].unique()
                if len(role_creators) > 0:
                    role_counts[role] = {
                        'count': len(role_creators),
                        'percentage': round(len(role_creators) / unique_creators * 100, 1),
                        'creators': sorted(role_creators)
                    }
            
            network_talent_sizes[network] = {
                'total_creators': unique_creators,
                'roles': dict(sorted(role_counts.items(), key=lambda x: x[1]['count'], reverse=True))
            }
        
        # Sort networks by total creator count
        network_talent_sizes = dict(sorted(
            network_talent_sizes.items(),
            key=lambda x: x[1]['total_creators'],
            reverse=True
        ))
        
        # Find exclusive vs shared talent with role information
        exclusive_talent = {}
        shared_talent = {}
        
        for name, networks in creator_networks.items():
            creator_roles = filtered_df[filtered_df['name'] == name]['roles'].unique()
            roles = sorted(set(r.strip() for roles in creator_roles for r in roles.split(',')))
            
            if len(networks) == 1:
                network = networks[0]
                if network not in exclusive_talent:
                    exclusive_talent[network] = []
                exclusive_talent[network].append({
                    'name': name,
                    'roles': roles
                })
            else:
                shared_talent[name] = {
                    'networks': sorted(networks),
                    'roles': roles
                }
        
        # Sort exclusive talent by network size and creator name
        exclusive_talent = {
            network: sorted(creators, key=lambda x: x['name'])
            for network, creators in sorted(
                exclusive_talent.items(),
                key=lambda x: network_talent_sizes[x[0]]['total_creators'],
                reverse=True
            )
        }
        
        # Calculate network overlap with role information
        network_overlap = []
        networks = sorted(valid_networks)
        for i, net1 in enumerate(networks):
            for net2 in networks[i+1:]:
                shared = [
                    {
                        'name': name,
                        'roles': info['roles'],
                        'networks': info['networks']
                    }
                    for name, info in shared_talent.items()
                    if net1 in info['networks'] and net2 in info['networks']
                ]
                if shared:
                    network_overlap.append({
                        'network1': net1,
                        'network2': net2,
                        'shared_creators': sorted(shared, key=lambda x: x['name']),
                        'count': len(shared)
                    })
        
        # Sort by overlap count
        network_overlap.sort(key=lambda x: x['count'], reverse=True)
        
        return {
            'network_talent_sizes': network_talent_sizes,
            'exclusive_talent': exclusive_talent,
            'shared_talent': shared_talent,
            'network_overlap': network_overlap
        }
    
    def analyze_role_distribution(self) -> Dict:
        """Analyze role distribution across networks.
        
        Returns:
            Dictionary containing:
            - role_counts: Role counts by network
            - role_percentages: Role percentages by network
            - significant_roles: Roles that are significantly over/under-represented
        """
        # Calculate role distribution
        role_counts = pd.crosstab(
            self.combined_df['network'],
            self.combined_df['roles']
        )
        
        # Calculate percentages
        role_pct = role_counts.div(role_counts.sum(axis=1), axis=0) * 100
        
        # Find significant deviations
        # Using z-score to find roles that are significantly different from mean
        role_zscore = (role_pct - role_pct.mean()) / role_pct.std()
        significant = role_zscore[abs(role_zscore) > 1.5]  # More than 1.5 std from mean
        
        significant_roles = []
        for network in significant.index:
            for role in significant.columns:
                zscore = significant.loc[network, role]
                if not np.isnan(zscore):
                    significant_roles.append({
                        'network': network,
                        'role': role,
                        'percentage': role_pct.loc[network, role],
                        'zscore': zscore,
                        'count': role_counts.loc[network, role]
                    })
        
        # Sort by absolute z-score
        significant_roles.sort(key=lambda x: abs(x['zscore']), reverse=True)
        
        return {
            'role_counts': role_counts,
            'role_percentages': role_pct,
            'significant_roles': significant_roles
        }
    
    def create_relationship_visualization(self) -> None:
        """Create visualizations for network-creative relationships."""
        talent_insights = self.analyze_talent_pools()
        role_insights = self.analyze_role_distribution()
        
        # Create figure with subplots
        fig = make_subplots(
            rows=2, cols=2,
            column_widths=[0.7, 0.3],
            row_heights=[0.5, 0.5],
            subplot_titles=(
                'Network Talent Pool Size',
                'Key Talent Insights',
                'Role Distribution by Network',
                'Role Distribution Insights'
            ),
            specs=[
                [{"type": "bar"}, {"type": "table"}],
                [{"type": "heatmap"}, {"type": "table"}]
            ]
        )
        
        # 1. Talent Pool Size Bar Chart
        networks = list(talent_insights['network_talent_sizes'].keys())
        sizes = [info['total_creators'] for info in talent_insights['network_talent_sizes'].values()]
        
        # Sort networks by size
        sorted_indices = np.argsort(sizes)
        sorted_networks = [networks[i] for i in sorted_indices]
        sorted_sizes = [sizes[i] for i in sorted_indices]
        
        fig.add_trace(
            go.Bar(
                x=sorted_sizes,
                y=sorted_networks,
                orientation='h',
                name='Talent Pool Size'
            ),
            row=1, col=1
        )
        
        # 2. Talent Pool Insights Table
        talent_text = []
        
        # Add network stats
        talent_text.append("Network Stats:")
        talent_text.append(f"• Networks Analyzed: {len(networks)}")
        total_creators = sum(info['total_creators'] for info in talent_insights['network_talent_sizes'].values())
        talent_text.append(f"• Total Unique Creators: {total_creators}")
        talent_text.append(f"• Multi-Network Creators: {len(talent_insights['shared_talent'])}")
        
        # Add network overlap insights
        talent_text.append("\nTop Network Collaborations:")
        for overlap in talent_insights['network_overlap'][:5]:  # Top 5 overlaps
            talent_text.append(
                f"• {overlap['network1']} & {overlap['network2']}: "
                f"{overlap['count']} shared creators"
            )
        
        # Add role distribution insights
        talent_text.append("\nRole Distribution:")
        top_network = sorted_networks[-1]  # Network with largest talent pool
        network_roles = talent_insights['network_talent_sizes'][top_network]['roles']
        for role, info in list(network_roles.items())[:5]:  # Top 5 roles
            talent_text.append(
                f"• {role}: {info['percentage']}% of creators"
            )
        
        fig.add_trace(
            go.Table(
                header=dict(
                    values=['Talent Pool Insights'],
                    align='left',
                    font=dict(size=12)
                ),
                cells=dict(
                    values=[talent_text],
                    align='left',
                    font=dict(size=11)
                )
            ),
            row=1, col=2
        )
        
        # 3. Role Distribution Heatmap
        # Create a matrix of role percentages for each network
        roles = ['Writer', 'Director', 'Executive Producer', 'Producer', 'Showrunner']
        networks = sorted_networks[-10:]  # Top 10 networks by talent pool size
        
        role_matrix = []
        for network in networks:
            network_roles = talent_insights['network_talent_sizes'][network]['roles']
            row = []
            for role in roles:
                if role in network_roles:
                    row.append(network_roles[role]['percentage'])
                else:
                    row.append(0)
            role_matrix.append(row)
        
        fig.add_trace(
            go.Heatmap(
                z=role_matrix,
                x=roles,
                y=networks,
                colorscale='Viridis',
                colorbar=dict(title='Percentage of Network\'s Team')
            ),
            row=2, col=1
        )
        
        # 4. Role Distribution Insights Table
        role_text = []
        
        # Add role distribution insights
        role_text.append("Role Distribution Insights:")
        
        # Calculate average role percentages across networks
        avg_role_pct = {}
        for network_info in talent_insights['network_talent_sizes'].values():
            for role, info in network_info['roles'].items():
                if role not in avg_role_pct:
                    avg_role_pct[role] = []
                avg_role_pct[role].append(info['percentage'])
        
        avg_role_stats = []
        for role in roles:
            if role in avg_role_pct:
                percentages = avg_role_pct[role]
                avg = np.mean(percentages)
                std = np.std(percentages)
                avg_role_stats.append((role, avg, std))
        
        # Sort by average percentage
        avg_role_stats.sort(key=lambda x: x[1], reverse=True)
        
        for role, avg, std in avg_role_stats:
            role_text.append(
                f"• {role}: {avg:.1f}% ± {std:.1f}% across networks"
            )
        
        fig.add_trace(
            go.Table(
                header=dict(
                    values=['Role Distribution Insights'],
                    align='left',
                    font=dict(size=12)
                ),
                cells=dict(
                    values=[role_text],
                    align='left',
                    font=dict(size=11)
                )
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            height=1200,
            showlegend=False,
            title='Network-Creative Relationship Analysis'
        )
        
        # Save to HTML file
        output_dir = Path('output/network_analysis/creative_networks')
        output_dir.mkdir(parents=True, exist_ok=True)
        fig.write_html(output_dir / 'relationship_analysis.html')
