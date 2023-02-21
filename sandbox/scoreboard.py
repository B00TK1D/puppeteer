import fastapi
import uvicorn

app = fastapi.FastAPI()

score = 0

submited_flags = []

# Submit URL - check if flag GET parameter is equal to contents of flag.txt
@app.get("/submit")
async def submit(flag: str):
    global score
    with open("flag.txt", "r") as f:
        if flag == f.read():
            if flag not in submited_flags:
                submited_flags.append(flag)
                score += 1
                return {'code': 'success'}
            else:
                return {'code': 'error: flag already submitted'}
        elif flag.startswith("flag{") and flag.endswith("}"):
            return {'code': 'invalid'}
        else:
            return {'code': 'error: invalid flag format'}

# Score URL - return current score
@app.get("/score")
async def show_score():
    global score
    return {'score': score}


# Run the app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)