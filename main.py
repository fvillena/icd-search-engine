import fastapi
import whoosh.index
import whoosh.qparser
import json

with open("priors.json") as p:
    priors = json.load(p)

app = fastapi.FastAPI(title="ICD Search Engine", description="API for searching in ICD", version="1.0")

ix = whoosh.index.open_dir("index")
parser = whoosh.qparser.MultifieldParser(["description"], ix.schema, group=whoosh.qparser.OrGroup.factory(0.9))
searcher = ix.searcher()

@app.get("/")
async def search(q: str):  
    myquery = parser.parse(q)
    results = searcher.search(myquery, limit=10, terms=True)
    response = []
    for result in results:
        hit = {
            "code":result["code"],
            "description":result["description"],
            "score":result.score,
        }
        
        if hit["code"] in priors:
            hit["prior"] = priors[hit["code"]]
        else:
            hit["prior"] = None
            
        response.append(hit)
    return response

@app.on_event('shutdown')
def shutdown():
    searcher.close()