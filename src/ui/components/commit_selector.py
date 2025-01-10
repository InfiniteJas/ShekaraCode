# src/ui/components/commit_selector.py
from dash import html, dcc
from typing import List
from ...models.commit import CommitModel

def create_commit_selector(commits: List[CommitModel]) -> html.Div:
    return html.Div([
        html.H3("Select Commit", className="mb-4"),
        dcc.Dropdown(
            id='commit-selector',
            options=[
                {'label': commit.summary, 'value': commit.sha}
                for commit in commits
            ],
            placeholder='Select a commit to analyze',
            className="w-full"
        )
    ])