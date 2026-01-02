import sys
from pathlib import Path

html = """<! DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>RAG Test Case Generator</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 1400px; margin: 0 auto; background: white; border-radius: 16px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); overflow: hidden; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; text-align: center; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.1em; opacity: 0.9; }
        .content { padding: 40px; }
        .query-section { margin-bottom: 30px; }
        .query-section label { display: block; font-weight: 600; margin-bottom: 10px; color: #333; font-size: 1.1em; }
        textarea { width: 100%; padding: 15px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 16px; font-family: inherit; min-height: 120px; transition: border-color 0.3s; }
        textarea:focus { outline: none; border-color: #667eea; }
        .button-group { display: flex; gap:  15px; margin-top: 20px; }
        button { padding: 15px 30px; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; transition:  all 0.3s; flex: 1; }
        . btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3); }
        .btn-secondary { background: #f5f5f5; color: #333; }
        .btn-secondary:hover { background: #e0e0e0; }
        button:disabled { opacity: 0.5; cursor: not-allowed; transform: none ! important; }
        .loading { display: none; background: #e3f2fd; color: #1976d2; padding: 20px; border-radius: 8px; margin:  20px 0; text-align: center; font-weight: 600; }
        . loading. show { display: block; }
        .results { margin-top: 30px; }
        .alert { padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid; }
        .alert-warning { background: #fff3cd; border-color: #ffc107; color: #856404; }
        .alert-error { background: #f8d7da; border-color: #dc3545; color: #721c24; }
        .alert h3 { margin-bottom: 10px; }
        .use-case { background: #f9f9f9; border-radius: 12px; padding: 30px; margin-bottom: 25px; border-left: 6px solid #667eea; transition: transform 0.2s; }
        .use-case:hover { transform: translateX(5px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        .use-case h3 { color:  #667eea; font-size: 1.5em; margin-bottom: 20px; }
        .section { margin-bottom: 20px; }
        .section-title { font-weight: 700; color: #555; margin-bottom: 8px; font-size: 1.05em; }
        .section-content { padding-left: 20px; }
        .steps { list-style: decimal; padding-left: 30px; }
        .steps li { margin:  10px 0; }
        ul { padding-left: 20px; }
        ul li { margin: 8px 0; }
        .metadata { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); padding: 25px; border-radius: 12px; margin-top: 30px; }
        .metadata-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px; }
        .metadata-item { background: white; padding: 15px; border-radius: 8px; }
        .metadata-item strong { display: block; color: #667eea; margin-bottom: 5px; }
        pre { background: #2d2d2d; color: #f8f8f2; padding:  15px; border-radius:  8px; overflow-x:  auto; font-size: 0.9em; }
        . badge { display: inline-block; padding: 5px 10px; border-radius: 4px; font-size: 0.85em; font-weight: 600; margin:  3px; }
        .badge-success { background: #d4edda; color: #155724; }
        @media (max-width: 768px) {
            .header h1 { font-size:  1.8em; }
            . content { padding: 20px; }
            .button-group { flex-direction: column; }
        }
    </style>
</head>
<body>
    <div class='container'>
        <div class='header'>
            <h1> RAG Test Case Generator</h1>
            <p>Evidence-Grounded Multimodal Test Case Generation</p>
        </div>
        <div class='content'>
            <div class='query-section'>
                <label for='query'>Enter Your Query</label>
                <textarea id='query' placeholder='Example: Create use cases for user signup with email validation'>Create use cases for user signup with email validation</textarea>
            </div>
            <div class='button-group'>
                <button class='btn-primary' onclick='generate(false)'> Generate Test Cases</button>
                <button class='btn-secondary' onclick='generate(true)'> Debug Mode</button>
                <button class='btn-secondary' onclick='showStats()'> Stats</button>
            </div>
            <div id='loading' class='loading'>
                <div> Generating test cases...</div>
                <div style='font-size: 0.9em; margin-top: 10px;'>This may take 10-30 seconds</div>
            </div>
            <div id='results' class='results'></div>
        </div>
    </div>
    <script>
        async function generate(debug = false) {
            const query = document.getElementById('query').value.trim();
            if (!query) { alert('Please enter a query'); return; }
            
            const resultsDiv = document.getElementById('results');
            const loadingDiv = document.getElementById('loading');
            loadingDiv.classList.add('show');
            resultsDiv.innerHTML = '';
            
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query, debug, top_k: 5 })
                });
                
                if (!response.ok) throw new Error('Server error');
                const data = await response.json();
                displayResults(data);
            } catch (error) {
                resultsDiv.innerHTML = "<div class='alert alert-error'><h3>Error</h3><p>" + error.message + "</p></div>";
            } finally {
                loadingDiv.classList.remove('show');
            }
        }
        
        function displayResults(data) {
            const container = document.getElementById('results');
            let html = '';
            
            if (data. status === 'insufficient_evidence' || data.status === 'low_confidence') {
                html = "<div class='alert alert-warning'><h3> " + data.message + "</h3>";
                if (data.clarifying_questions) {
                    html += "<ul>";
                    data.clarifying_questions.forEach(q => html += "<li>" + q + "</li>");
                    html += "</ul>";
                }
                html += "</div>";
                container.innerHTML = html;
                return;
            }
            
            if (data.use_cases && data.use_cases.length > 0) {
                data.use_cases.forEach(uc => {
                    html += "<div class='use-case'>";
                    html += "<h3>" + uc.title + "</h3>";
                    html += "<div class='section'><div class='section-title'>Goal</div><div class='section-content'><p>" + uc.goal + "</p></div></div>";
                    
                    if (uc.preconditions && uc.preconditions.length) {
                        html += "<div class='section'><div class='section-title'>Preconditions</div><div class='section-content'><ul>";
                        uc. preconditions.forEach(p => html += "<li>" + p + "</li>");
                        html += "</ul></div></div>";
                    }
                    
                    html += "<div class='section'><div class='section-title'>Steps</div><div class='section-content'><ol class='steps'>";
                    uc.steps.forEach(s => html += "<li>" + s + "</li>");
                    html += "</ol></div></div>";
                    
                    html += "<div class='section'><div class='section-title'>Expected Results</div><div class='section-content'><ul>";
                    uc.expected_results.forEach(r => html += "<li>" + r + "</li>");
                    html += "</ul></div></div>";
                    
                    if (uc.negative_cases && uc.negative_cases.length) {
                        html += "<div class='section'><div class='section-title'>Negative Cases</div><div class='section-content'><ul>";
                        uc.negative_cases.forEach(n => html += "<li>" + n + "</li>");
                        html += "</ul></div></div>";
                    }
                    
                    if (uc.boundary_cases && uc. boundary_cases.length) {
                        html += "<div class='section'><div class='section-title'>Boundary Cases</div><div class='section-content'><ul>";
                        uc. boundary_cases.forEach(b => html += "<li>" + b + "</li>");
                        html += "</ul></div></div>";
                    }
                    
                    html += "</div>";
                });
                
                html += "<div class='metadata'><h3> Metadata</h3><div class='metadata-grid'>";
                html += "<div class='metadata-item'><strong>Model</strong>" + (data.model_used || 'N/A') + "</div>";
                html += "<div class='metadata-item'><strong>Evidence Chunks</strong>" + (data.total_evidence_chunks || 0) + "</div>";
                html += "<div class='metadata-item'><strong>Score</strong>" + (data.avg_evidence_score || 0).toFixed(3) + "</div>";
                html += "<div class='metadata-item'><strong>Time</strong>" + (data.generation_time_seconds || 0).toFixed(2) + "s</div>";
                html += "</div></div>";
            }
            
            container.innerHTML = html;
        }
        
        async function showStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                const html = "<div class='metadata'><h3> Stats</h3>" +
                    "<p>Total Chunks: " + (data.total_chunks || 0) + "</p>" +
                    "<p>Sources:  " + (data.unique_sources || 0) + "</p>" +
                    "</div>";
                document.getElementById('results').innerHTML = html;
            } catch (error) {
                document.getElementById('results').innerHTML = "<div class='alert alert-error'><p>Error loading stats</p></div>";
            }
        }
    </script>
</body>
</html>"""

Path('src/templates').mkdir(parents=True, exist_ok=True)
Path('src/templates/index.html').write_text(html, encoding='utf-8')
print(' Created index.html')
