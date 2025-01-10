# src/ui/dashboard.py
from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State
from ..config.settings import Settings
from ..api.github_service import GitHubService
from ..api.openai_service import OpenAIService
from ..analysis.code_analyzer import CodeAnalyzer
from ..analysis.metrics_calculator import MetricsCalculator
from .components.commit_selector import create_commit_selector
from .components.analysis_display import create_analysis_display
from ..utils.logging import get_logger
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd

logger = get_logger(__name__)

class Dashboard:
    def __init__(self, settings: Settings):
        self.app = Dash(
            __name__,
            external_stylesheets=[
                'https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css'
            ]
        )
        self.settings = settings
        
        # Initialize services
        self.github_service = GitHubService(settings)
        self.openai_service = OpenAIService(settings)
        self.metrics_calculator = MetricsCalculator()
        
        self.analyzer = CodeAnalyzer(
            self.github_service,
            self.openai_service,
            self.metrics_calculator
        )
        
        self.setup_layout()
        self.setup_callbacks()

    def setup_layout(self):
        """Setup the dashboard layout."""
        self.app.layout = html.Div([
            # Header
            html.Div([
                html.H1(
                    "ShekaraCode Analysis Dashboard",
                    className="text-2xl font-bold mb-4"
                ),
                html.P(
                    "AI-powered Git repository analysis",
                    className="text-gray-600"
                )
            ], className="mb-8 p-4 bg-white shadow-lg"),
            
            # Main content
            html.Div([
                # Left panel - Repository and commit selection
                html.Div([
                    html.Div([
                        html.H2("Repository Statistics", className="text-xl mb-4"),
                        dcc.Loading(id="repo-stats")
                    ], className="mb-8"),
                    
                    html.Div([
                        html.H2("Commit Selection", className="text-xl mb-4"),
                        dcc.Dropdown(
                            id='commit-selector',
                            placeholder='Select a commit',
                            className="w-full mb-4"
                        ),
                        html.Button(
                            'Analyze',
                            id='analyze-button',
                            className="bg-blue-500 text-white px-4 py-2 rounded"
                        )
                    ])
                ], className="w-1/3 p-4"),
                
                # Right panel - Analysis results
                html.Div([
                    dcc.Loading(
                        id="loading-analysis",
                        children=[
                            html.Div(id='analysis-results')
                        ],
                        type="circle"
                    )
                ], className="w-2/3 p-4")
            ], className="flex"),
            
            # Trends and metrics
            html.Div([
                html.H2("Code Quality Trends", className="text-xl mb-4"),
                dcc.Graph(id='quality-trends')
            ], className="mt-8 p-4"),
            
            # Footer
            html.Footer([
                html.P(
                    "ShekaraCode © 2024",
                    className="text-center text-gray-600"
                )
            ], className="mt-8 p-4")
        ], className="container mx-auto")

    def setup_callbacks(self):
        """Setup all dashboard callbacks."""
        self.setup_repo_stats_callback()
        self.setup_commit_list_callback()
        self.setup_analysis_callback()
        self.setup_trends_callback()

    def setup_repo_stats_callback(self):
        @self.app.callback(
            Output('repo-stats', 'children'),
            Input('repo-stats', 'id')
        )
        async def update_repo_stats(_):
            """Update repository statistics."""
            try:
                stats = await self.github_service.get_repo_statistics()
                return html.Div([
                    html.Div([
                        html.Strong("Stars: "),
                        html.Span(stats['stars'])
                    ], className="mb-2"),
                    html.Div([
                        html.Strong("Forks: "),
                        html.Span(stats['forks'])
                    ], className="mb-2"),
                    html.Div([
                        html.Strong("Open Issues: "),
                        html.Span(stats['open_issues'])
                    ], className="mb-2"),
                    html.Div([
                        html.Strong("Main Language: "),
                        html.Span(stats['language'])
                    ])
                ])
            except Exception as e:
                logger.error(f"Error fetching repo stats: {str(e)}")
                return html.Div(
                    "Error loading repository statistics",
                    className="text-red-500"
                )

    def setup_commit_list_callback(self):
        @self.app.callback(
            Output('commit-selector', 'options'),
            Input('commit-selector', 'id')
        )
        async def update_commit_list(_):
            """Update the list of commits."""
            try:
                commits = await self.github_service.get_recent_commits()
                return [
                    {'label': commit.summary, 'value': commit.sha}
                    for commit in commits
                ]
            except Exception as e:
                logger.error(f"Error fetching commits: {str(e)}")
                return []

    def setup_analysis_callback(self):
        @self.app.callback(
            Output('analysis-results', 'children'),
            Input('analyze-button', 'n_clicks'),
            State('commit-selector', 'value'),
            prevent_initial_call=True
        )
        async def analyze_commit(n_clicks, commit_sha):
            """Perform analysis when a commit is selected."""
            if not commit_sha:
                return "Please select a commit to analyze"
                
            try:
                analysis = await self.analyzer.analyze_commit(commit_sha)
                return create_analysis_display(analysis)
            except Exception as e:
                logger.error(f"Error analyzing commit: {str(e)}")
                return html.Div(
                    "Error performing analysis",
                    className="text-red-500"
                )

    def setup_trends_callback(self):
        @self.app.callback(
            Output('quality-trends', 'figure'),
            Input('quality-trends', 'id')
        )
        async def update_trends(_):
            """Update quality trends graph."""
            try:
                # Get recent commits and their analysis
                commits = await self.github_service.get_recent_commits(20)
                analyses = await self.analyzer.analyze_multiple_commits(
                    [c.sha for c in commits]
                )
                
                # Prepare data for visualization
                dates = [c.date for c in commits]
                scores = [a.quality_score for a in analyses]
                
                # Create trend line
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=scores,
                    mode='lines+markers',
                    name='Code Quality Score',
                    line=dict(color='#3B82F6')
                ))
                
                fig.update_layout(
                    title='Code Quality Trend',
                    xaxis_title='Date',
                    yaxis_title='Quality Score',
                    yaxis_range=[0, 10],
                    template='plotly_white'
                )
                
                return fig
                
            except Exception as e:
                logger.error(f"Error updating trends: {str(e)}")
                return {}

    def run(self, debug: bool = False, port: int = 8050):
        """Run the dashboard server."""
        self.app.run_server(debug=debug, port=port)

if __name__ == "__main__":
    settings = Settings()
    dashboard = Dashboard(settings)
    dashboard.run(debug=True)