"""Role Distribution Analysis.

This module focuses on analyzing and visualizing role patterns across networks,
including role specialization, combinations, and career progression.
"""

import logging
from pathlib import Path
from typing import Dict, List, Set

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)

class RoleAnalyzer:
    """Analyzer for role distributions and patterns."""
    
    # Role categories
    ROLE_CATEGORIES = {
        'Creator': 'Creative',
        'Writer': 'Creative',
        'Director': 'Creative',
        'Showrunner': 'Creative',
        'Co-Showrunner': 'Creative',
        'Writer/Executive Producer': 'Creative',
        'Creative Producer': 'Creative',
        
        'Executive Producer': 'Production',
        'Producer': 'Production',
        'Co-Producer': 'Production',
        'Line Producer': 'Production',
        
        'Studio Executive': 'Development',
        'Network Executive': 'Development',
        'Development Executive': 'Development',
        
        'Actor': 'Talent',
        'Host': 'Talent'
    }
    
    def __init__(self, shows_df: pd.DataFrame, team_df: pd.DataFrame):
        """Initialize the analyzer.
        
        Args:
            shows_df: DataFrame containing show information
            team_df: DataFrame containing team member information
        """
        self.shows_df = shows_df
        self.team_df = team_df
        
        # Ensure required columns exist
        required_cols = {
            'shows_df': ['show_name', 'network'],
            'team_df': ['show_name', 'roles']
        }
        
        for df_name, cols in required_cols.items():
            df = getattr(self, df_name)
            missing = [col for col in cols if col not in df.columns]
            if missing:
                logger.error(f"Missing required columns in {df_name}: {missing}")
                raise ValueError(f"Missing required columns in {df_name}: {missing}")
        
        # Merge shows and team data
        self.combined_df = pd.merge(
            self.team_df,
            self.shows_df[['show_name', 'network']],
            on='show_name',
            how='inner'  # Only keep matches
        )
        
        # Log basic stats
        logger.info("Role analysis stats:")
        try:
            role_counts = len(self._get_all_roles())
            logger.info(f"  Distinct roles: {role_counts}")
        except Exception as e:
            logger.error(f"Error getting role stats: {e}")
    
    def _normalize_roles(self, role_str: str) -> List[str]:
        """Normalize role string into a list of standardized roles.
        
        Args:
            role_str: Raw role string from the data
            
        Returns:
            List of standardized role strings
        """
        if pd.isna(role_str) or not str(role_str).strip():
            return []
        
        # Split on commas and clean up
        roles = []
        raw_roles = str(role_str).split(',')
        
        # Load role mappings from role_types.csv
        role_types_path = 'docs/sheets/STS Sales Database - role_types.csv'
        role_df = pd.read_csv(role_types_path)
        
        # Build role mappings from standard roles and aliases
        role_mappings = {}
        for _, row in role_df.iterrows():
            # Add standard role name
            role_mappings[row['role'].lower()] = row['role']
            
            # Add aliases
            if pd.notna(row['aliases']):
                for alias in row['aliases'].split(','):
                    role_mappings[alias.strip().lower()] = row['role']
        
        # Process each role
        for r in raw_roles:
            r = r.strip().lower()
            if not r:
                continue
            
            # Clean up and normalize
            r = r.strip().lower()
            if not r:
                continue
                
            # Try direct mapping
            if r in role_mappings:
                roles.append(role_mappings[r])
                continue
                
            # Try without special characters
            r_clean = r.replace('.', ' ').replace('-', ' ').replace('/', ' ')
            r_clean = ' '.join(r_clean.split())  # Normalize whitespace
            
            if r_clean in role_mappings:
                roles.append(role_mappings[r_clean])
            else:
                logger.warning(f"Unrecognized role: {r}")
                roles.append(r.title())
        
        # Remove duplicates and sort
        roles = list(set(roles))
        return sorted(roles)
    
    def _get_all_roles(self) -> Set[str]:
        """Get set of all unique roles across the dataset."""
        all_roles = set()
        for roles in self.combined_df['roles']:
            all_roles.update(self._normalize_roles(roles))
        return all_roles
    
    def analyze_role_distribution(self) -> Dict:
        """Analyze role distribution across networks.
        
        Returns:
            Dictionary containing:
            - role_counts: Role counts by network
            - role_percentages: Role percentages by network
            - role_combinations: Common role combinations
            - career_progression: Common role progression patterns
        """
        # Analyze role distribution by network
        network_roles = {}
        network_creators = {}
        role_combinations = {}
        
        for network in self.combined_df['network'].unique():
            network_df = self.combined_df[self.combined_df['network'] == network]
            
            # Track roles and creators
            roles = {}
            creators = {}
            
            for _, row in network_df.iterrows():
                name = row['name']
                normalized_roles = self._normalize_roles(row['roles'])
                
                # Count roles
                for role in normalized_roles:
                    roles[role] = roles.get(role, 0) + 1
                
                # Track creator roles
                if name not in creators:
                    creators[name] = set()
                creators[name].update(normalized_roles)
                
                # Track role combinations
                if len(normalized_roles) > 1:
                    combo = tuple(sorted(normalized_roles))
                    role_combinations[combo] = role_combinations.get(combo, 0) + 1
            
            network_roles[network] = roles
            network_creators[network] = creators
        
        # Calculate role percentages
        role_percentages = {}
        for network, roles in network_roles.items():
            total_roles = sum(roles.values())
            percentages = {
                role: (count / total_roles * 100)
                for role, count in roles.items()
            }
            role_percentages[network] = percentages
        
        # Analyze career progression
        career_progression = {}
        for network, creators in network_creators.items():
            for creator, roles in creators.items():
                if len(roles) > 1:
                    for role1 in roles:
                        for role2 in roles:
                            if role1 < role2:  # Use alphabetical order
                                pair = (role1, role2)
                                if pair not in career_progression:
                                    career_progression[pair] = {'count': 0, 'creators': set()}
                                career_progression[pair]['count'] += 1
                                career_progression[pair]['creators'].add(creator)
        
        return {
            'network_roles': network_roles,
            'role_percentages': role_percentages,
            'role_combinations': role_combinations,
            'career_progression': career_progression
        }
    
    def create_visualization(self) -> None:
        """Create visualizations for role distribution analysis."""
        role_insights = self.analyze_role_distribution()
        
        # Create figure with subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Network Role Preferences',
                'Common Role Combinations',
                'Role Progression Patterns',
                'Role Distribution Heatmap'
            ),
            specs=[
                [{"type": "table"}, {"type": "table"}],
                [{"type": "table"}, {"type": "heatmap"}]
            ],
            horizontal_spacing=0.08,
            vertical_spacing=0.15
        )
        
        # 1. Network Role Preferences Table
        network_specialties = []
        networks = sorted(self.combined_df['network'].unique())
        
        for network in networks:
            network_df = self.combined_df[self.combined_df['network'] == network]
            
            # Get role distribution
            network_roles = {}
            creator_roles = {}
            
            # Debug logging
            logger.info(f"\nAnalyzing network: {network}")
            logger.info(f"Network data shape: {network_df.shape}")
            logger.info("Sample of raw roles:")
            for _, row in network_df.head().iterrows():
                logger.info(f"  {row['name']}: {row['roles']}")
            
            for _, row in network_df.iterrows():
                name = row['name']
                raw_roles = row['roles']
                roles = self._normalize_roles(raw_roles)
                
                # Debug logging for each creator's roles
                logger.info(f"Processing {name}:")
                logger.info(f"  Raw roles: {raw_roles}")
                logger.info(f"  Normalized roles: {roles}")
                
                # Count total role occurrences
                for role in roles:
                    network_roles[role] = network_roles.get(role, 0) + 1
                
                # Track roles per creator
                if name not in creator_roles:
                    creator_roles[name] = set()
                creator_roles[name].update(roles)
            
            # Calculate percentages and get top roles
            total_roles = sum(network_roles.values())
            role_info = {}
            for role, count in network_roles.items():
                percentage = (count / total_roles) * 100
                role_info[role] = {'count': count, 'percentage': percentage}
            
            # Sort roles by percentage and get top 3
            top_roles = sorted(
                role_info.items(),
                key=lambda x: x[1]['percentage'],
                reverse=True
            )[:3]
            
            # Debug logging for role data
            logger.info(f"\nNetwork: {network}")
            logger.info(f"Total creators: {len(creator_roles)}")
            logger.info("Multi-role creators:")
            for name, roles in creator_roles.items():
                if len(roles) > 1:
                    logger.info(f"  {name}: {roles}")
            
            # Calculate percentage of people with multiple roles
            multi_role_creators = [name for name, roles in creator_roles.items() if len(roles) > 1]
            multi_role_count = len(multi_role_creators)
            total_creators = len(creator_roles)
            multi_role_pct = (multi_role_count / total_creators) * 100 if total_creators > 0 else 0
            
            logger.info(f"Multi-role count: {multi_role_count}")
            logger.info(f"Total creators: {total_creators}")
            logger.info(f"Multi-role percentage: {multi_role_pct:.1f}%")
            
            # Skip networks with no multi-role creators
            if multi_role_count == 0:
                continue
            
            # Find most common role combinations
            role_combos = []
            for creator, roles in creator_roles.items():
                if len(roles) > 1:
                    role_combos.append(tuple(sorted(roles)))
            
            combo_counts = {}
            for combo in role_combos:
                combo_counts[combo] = combo_counts.get(combo, 0) + 1
            
            # Get top 2 most common combinations
            top_combos = sorted(combo_counts.items(), key=lambda x: x[1], reverse=True)[:2]
            common_roles = '; '.join(f"{' + '.join(combo)} ({count})" for combo, count in top_combos) if top_combos else 'N/A'
            
            network_specialties.append({
                'network': network,
                'top_roles': '; '.join(f"{role} ({info['percentage']:.1f}%)" for role, info in top_roles),
                'multi_role_pct': f"{multi_role_pct:.1f}%",
                'common_combos': common_roles
            })
        
        # Sort by multi-role percentage
        network_specialties.sort(key=lambda x: float(x['multi_role_pct'].rstrip('%')), reverse=True)
        
        # Filter out networks with no multi-role creators
        network_specialties = [n for n in network_specialties if float(n['multi_role_pct'].rstrip('%')) > 0]
        
        fig.add_trace(
            go.Table(
                header=dict(
                    values=['Network', 'Top Roles', 'Multi-Role %', 'Common Role Combinations'],
                    align='left',
                    font=dict(size=12, color='white'),
                    fill_color='rgb(0, 75, 150)'
                ),
                cells=dict(
                    values=[
                        [d['network'] for d in network_specialties],
                        [d['top_roles'] for d in network_specialties],
                        [d['multi_role_pct'] for d in network_specialties],
                        [d['common_combos'] for d in network_specialties]
                    ],
                    align=['left', 'left', 'right', 'left'],
                    font=dict(size=11),
                    fill_color=['rgb(245, 245, 250)'],
                    height=30
                )
            ),
            row=1, col=1
        )
        
        # 2. Common Role Combinations Table
        role_combos = []
        for combo, count in sorted(
            role_insights['role_combinations'].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            # Skip combinations with low frequency
            if count < 2:  # Require at least 2 occurrences
                continue
            role_combos.append({
                'roles': ' + '.join(combo),
                'count': count,
                'percentage': count / len(self.combined_df) * 100
            })
        
        fig.add_trace(
            go.Table(
                header=dict(
                    values=['Role Combination', 'Count', 'Percentage'],
                    align='left',
                    font=dict(size=12, color='white'),
                    fill_color='rgb(0, 75, 150)'
                ),
                cells=dict(
                    values=[
                        [d['roles'] for d in role_combos],
                        [d['count'] for d in role_combos],
                        [f"{d['percentage']:.1f}%" for d in role_combos]
                    ],
                    align=['left', 'right', 'right'],
                    font=dict(size=11),
                    fill_color=['rgb(245, 245, 250)'],
                    height=30
                )
            ),
            row=1, col=2
        )
        
        # 3. Role Progression Table
        progressions = []
        for (role1, role2), data in sorted(
            role_insights['career_progression'].items(),
            key=lambda x: x[1]['count'],
            reverse=True
        ):
            # Skip progressions with low frequency
            if data['count'] < 3:  # Require at least 3 occurrences
                continue
            progressions.append({
                'path': f"{role1} → {role2}",
                'count': data['count'],
                'examples': '; '.join(sorted(list(data['creators']))[:3])  # Show up to 3 examples
            })
        
        fig.add_trace(
            go.Table(
                header=dict(
                    values=['Career Path', 'Count', 'Example Creators'],
                    align='left',
                    font=dict(size=12, color='white'),
                    fill_color='rgb(0, 75, 150)'
                ),
                cells=dict(
                    values=[
                        [d['path'] for d in progressions],
                        [d['count'] for d in progressions],
                        [d['examples'] for d in progressions]
                    ],
                    align=['left', 'right', 'left'],
                    font=dict(size=11),
                    fill_color=['rgb(245, 245, 250)'],
                    height=30
                )
            ),
            row=2, col=1
        )
        
        # 4. Role Distribution Heatmap
        # Calculate role frequencies across all networks
        all_roles = list(self._get_all_roles())
        role_freqs = {role: 0 for role in all_roles}
        
        for network in self.combined_df['network'].unique():
            network_roles = role_insights['network_roles'][network]
            for role, count in network_roles.items():
                role_freqs[role] += count
        
        # Sort roles by frequency
        all_roles.sort(key=lambda r: role_freqs[r], reverse=True)
        networks = sorted(self.combined_df['network'].unique())
        
        heatmap_data = []
        for network in networks:
            row = []
            total_roles = sum(role_insights['network_roles'][network].values())
            for role in all_roles:
                count = role_insights['network_roles'][network].get(role, 0)
                percentage = (count / total_roles * 100) if total_roles > 0 else 0
                row.append(percentage)
            heatmap_data.append(row)
        
        fig.add_trace(
            go.Heatmap(
                z=heatmap_data,
                x=all_roles,
                y=networks,
                colorscale='YlOrRd',
                colorbar=dict(title='%'),
                hoverongaps=False
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            height=1200,  # Increased height
            showlegend=False,
            title_text="Role Distribution Analysis",
            title_x=0.5
        )
        
        # Save visualization
        output_dir = Path("output/network_analysis/creative_networks")
        output_dir.mkdir(exist_ok=True, parents=True)
        fig.write_html(output_dir / "role_analysis.html")
