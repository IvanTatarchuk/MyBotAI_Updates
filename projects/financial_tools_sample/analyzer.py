
#!/usr/bin/env python3
import json
p = json.load(open('portfolio.json'))
print(len(p.get('positions', [])))
