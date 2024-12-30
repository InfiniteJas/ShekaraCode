from github import Github
from openai import OpenAI
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from dash import Dash, html, dcc, Input, Output, State
import plotly.graph_objects as go
import time
from tenacity import retry, stop_after_attempt, wait_exponential

class GitAnalyzer:
   def __init__(self, github_token: str, openai_key: str):
       self.github = Github(github_token)
       self.ai = OpenAI(api_key=openai_key)
       self.repo = self.github.get_repo("InfiniteJas/docintel")

   def get_commit_list(self):
       return list(self.repo.get_commits()[:10])

   @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
   def analyze_commit(self, commit_sha):
       commit = self.repo.get_commit(commit_sha)
       print(f"\nAnalyzing commit {commit.sha[:7]}...")
       
       changes = [
           {'file': f.filename, 'patch': f.patch[:500]}
           for f in commit.files 
           if f.patch and f.filename.endswith(('.py', '.js', '.ts', '.java'))
       ][:3]

       print(f"Found {len(changes)} code files to analyze")
       if not changes:
           return {"issues": [], "score": 0, "recommendations": []}

       try:
           print("Attempting analysis...")
           response = self.ai.chat.completions.create(
               model="gpt-3.5-turbo",
               messages=[{
                   "role": "system",
                   "content": "You are a code review expert."
               }, {
                   "role": "user",
                   "content": f"Changes:\n{json.dumps(changes)}"
               }],
               temperature=0.3
           )
           print("Analysis complete!")
           return json.loads(response.choices[0].message.content)
       except Exception as e:
           print(f"Analysis failed: {e}")
           return {"issues": [], "score": 0, "recommendations": []}

class Dashboard:
   def __init__(self):
       self.app = Dash(__name__)
       load_dotenv()
       self.analyzer = GitAnalyzer(
           github_token=os.getenv('GITHUB_TOKEN'),
           openai_key=os.getenv('OPENAI_API_KEY')
       )
       self.setup_layout()
       self.setup_callbacks()

   def setup_layout(self):
       self.app.layout = html.Div([
           html.H1("Git Commit Analyzer"),
           dcc.Dropdown(
               id='commit-selector',
               options=self.get_commit_options(),
               placeholder='Select a commit'
           ),
           html.Button('Analyze', id='analyze-button'),
           dcc.Loading(
               id="loading",
               children=[
                   html.Div(id='commit-info'),
                   html.Div(id='analysis-results')
               ]
           )
       ])

   def get_commit_options(self):
       commits = self.analyzer.get_commit_list()
       return [{'label': f"{c.sha[:7]} - {c.commit.message[:50]}", 
               'value': c.sha} for c in commits]

   def setup_callbacks(self):
       @self.app.callback(
           [Output('commit-info', 'children'),
            Output('analysis-results', 'children')],
           Input('analyze-button', 'n_clicks'),
           State('commit-selector', 'value'),
           prevent_initial_call=True
       )
       def analyze_selected_commit(n_clicks, commit_sha):
           if not commit_sha:
               return "Select a commit", ""
               
           analysis = self.analyzer.analyze_commit(commit_sha)
           
           return [
               html.Div([
                   html.H3(f"Commit: {commit_sha[:7]}"),
               ]),
               html.Div([
                   html.H3("Analysis Results"),
                   html.H4(f"Score: {analysis['score']}/10"),
                   html.H4("Issues:"),
                   html.Ul([
                       html.Li(f"{i['type']} ({i['severity']}): {i['description']}")
                       for i in analysis['issues']
                   ]),
                   html.H4("Recommendations:"),
                   html.Ul([html.Li(r) for r in analysis['recommendations']])
               ])
           ]

   def run(self):
       self.app.run_server(debug=True)

if __name__ == "__main__":
   dashboard = Dashboard()
   dashboard.run()