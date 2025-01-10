# src/ui/components/analysis_display.py
from dash import html
from ...models.analysis_result import AnalysisResult

def create_analysis_display(analysis: AnalysisResult) -> html.Div:
    return html.Div([
        html.H3("Analysis Results", className="mb-4"),
        
        # Quality Score
        html.Div([
            html.H4("Quality Score"),
            html.Div(
                f"{analysis.quality_score:.1f}/10",
                className=_get_score_class(analysis.quality_score)
            )
        ], className="mb-4"),
        
        # Issues
        html.Div([
            html.H4("Issues Found"),
            html.Ul([
                html.Li([
                    html.Span(
                        issue.type,
                        className=f"badge badge-{issue.severity.lower()}"
                    ),
                    html.Span(f": {issue.description}")
                ])
                for issue in analysis.issues
            ])
        ], className="mb-4"),
        
        # Security Concerns
        html.Div([
            html.H4("Security Concerns"),
            html.Ul([
                html.Li([
                    html.Span(
                        concern.level,
                        className=f"badge badge-{_get_security_class(concern.level)}"
                    ),
                    html.Span(f": {concern.description}")
                ])
                for concern in analysis.security_concerns
            ])
        ], className="mb-4"),
        
        # Recommendations
        html.Div([
            html.H4("Recommendations"),
            html.Ul([
                html.Li(rec) for rec in analysis.recommendations
            ])
        ])
    ])

def _get_score_class(score: float) -> str:
    if score >= 8:
        return "text-green-600 font-bold text-xl"
    elif score >= 6:
        return "text-yellow-600 font-bold text-xl"
    else:
        return "text-red-600 font-bold text-xl"

def _get_security_class(level: str) -> str:
    return {
        'HIGH': 'error',
        'MEDIUM': 'warning',
        'LOW': 'info'
    }.get(level.upper(), 'default')