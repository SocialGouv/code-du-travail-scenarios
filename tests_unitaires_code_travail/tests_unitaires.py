import pandas as pd
from query import *
name = "request_ut.csv"
resurl_nbr = 20

new_columns = ['Result']

expected = ["Expected_" + str(k) for k in range(1, 6)]
intop_columns = ["Url {k} res pos".format(k=k, n=resurl_nbr) for k in range(1, 6)]
new_columns.extend(intop_columns)
res_columns = ["res_url_" + str(k) for k in range(1, resurl_nbr+1)]
new_columns.extend(res_columns)
req = pd.read_csv(name)
req.fillna("_", inplace=True)
res_values = pd.Series(index=req.index)
for col in new_columns:
    req[col] = ''

for request in req["Request"]:
    print(request)
    results = search(request, "body")
    idx = req[req["Request"]==request].index
    url_set = set()
    for k in range(min(len(results), 20)):
        #print(k, results[k])
        try:
            _url = results[k]["_source"]["url"]
        except Exception as e:
            print(' '*10 ,e , results[k]["_source"])
            _url = "___"

        req.loc[idx, res_columns[k]] = _url
        url_set.add(_url)
    url_set.discard('')
    tot = 0
    found = 0
    for i, cl in enumerate(expected):
        _url_val = req.loc[idx, cl].values[0]
        if not _url_val ==  '_':
            tot = tot + 1
        if _url_val in url_set:
            #print(" "*10, request, "Adding", found)
            for pos in range(resurl_nbr):
                if req.loc[idx, res_columns[pos]].values[0] == _url_val:
                    req.loc[idx, intop_columns[i]] = pos + 1
            found =  found + 1
            #print(" "*10, request, "Added", found)
    _res = "{}/{}".format(found, tot)
    try:
        res_values[idx] = 100 *found/tot
    except:
        res_values[idx] = 0
    req.loc[idx, new_columns[0]] =_res

req.to_csv("result_ut.csv", index=False)



style = """<style>
table {
    border-collapse: collapse;
}

table, td, th {
    border: 1px solid black;
}
.White {
}
.Red {
background-color: red;
}
.Green {
background-color: green;
}
</style>
"""

_res_col = 7

header = "<tr>"
for col in req.columns:
     header += "<th>{}</th>".format(col)
header += "</th>"
def get_body(prop_name="class"):
    # prop_name = "bgcolor"
    body = "<tr>"
    for index, row in req.iterrows():
        #print(index, row)
        for i, val in enumerate(row):
            #color = "White"
            #print(i, val)
            style_ = ''
            if i == _res_col:
                color = "Red" if res_values[index]< 50 else "Green"
                style_ = '{}="{}"'.format(prop_name, color)
            body += '<td {} >{}</td>'.format(style_, val)
        body +="</tr>\n"
    return body



body = get_body("bgcolor")

output = """<!doctype html>
<html>
<head><meta charset="UTF-8"><title>Result</title>""" + style + """</head>
<body>
<table> """ + header + body + """
</table>
</body>
</html>"""

with open("result.html", "wt") as f:
    f.write(output)
