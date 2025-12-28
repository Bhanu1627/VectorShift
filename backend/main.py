from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# allow local frontend to call this API during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for the most recently POSTed pipeline (nodes/edges)
last_submission = {"nodes": [], "edges": []}


@app.get('/')
def read_root():
    return {'Ping': 'Pong'}


@app.get('/pipelines/parse')
def parse_pipeline_info():
    """Informational GET endpoint so browser visits don't return 405.
    Use POST with a JSON body containing `nodes` and `edges` to get counts and DAG check.
    """
    # Return the last submitted pipeline (if any) and usage instructions
    return {
        'detail': 'POST to this endpoint with JSON body {nodes: [], edges: []} to receive {num_nodes, num_edges, is_dag}.',
        'last_submission': last_submission,
    }


@app.post('/pipelines/parse')
async def parse_pipeline(request: Request):
    """Accepts a JSON body with `nodes` and `edges` arrays.
    Returns {num_nodes, num_edges, is_dag}.
    """
    body = await request.json()
    nodes = body.get('nodes', []) if isinstance(body, dict) else []
    edges = body.get('edges', []) if isinstance(body, dict) else []

    # persist the received pipeline in-memory so GET can return it
    try:
        last_submission['nodes'] = nodes
        last_submission['edges'] = edges
    except Exception:
        # best-effort: if last_submission can't be updated, ignore
        pass

    # derive node IDs and counts from provided node objects (more robust)
    node_ids = {n.get('id') for n in nodes if isinstance(n, dict) and n.get('id')}

    # num_nodes should reflect unique valid node ids
    num_nodes = len(node_ids)

    # count only edges that reference known nodes
    valid_edge_count = 0
    for e in edges:
        if not isinstance(e, dict):
            continue
        src = e.get('source')
        tgt = e.get('target')
        if src in node_ids and tgt in node_ids:
            valid_edge_count += 1
    num_edges = valid_edge_count

    # build adjacency for directed graph: use node.id
    adj = {nid: [] for nid in node_ids}
    indegree = {nid: 0 for nid in node_ids}

    for e in edges:
        # edges may be objects with source/target fields
        if not isinstance(e, dict):
            continue
        src = e.get('source')
        tgt = e.get('target')
        if src in node_ids and tgt in node_ids:
            adj[src].append(tgt)
            indegree[tgt] = indegree.get(tgt, 0) + 1

    # Kahn's algorithm for cycle detection
    queue = [n for n, d in indegree.items() if d == 0]
    visited = 0
    from collections import deque
    q = deque(queue)
    while q:
        u = q.popleft()
        visited += 1
        for v in adj.get(u, []):
            indegree[v] -= 1
            if indegree[v] == 0:
                q.append(v)

    is_dag = (visited == len(node_ids))

    return {'num_nodes': num_nodes, 'num_edges': num_edges, 'is_dag': is_dag}
