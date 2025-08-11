
#!/usr/bin/env python3
import json, statistics

def preprocess(values):
    return [(v - min(values)) / (max(values) - min(values) or 1) for v in values]

def train(values):
    return {"mean": statistics.mean(values), "stdev": statistics.pstdev(values)}

if __name__ == '__main__':
    data = [1,2,3,4,5]
    norm = preprocess(data)
    model = train(norm)
    print(json.dumps(model))
