import sys
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import csv
import json
esclient = Elasticsearch(['0.0.0.0'], port=9200)
request_file = 'requests.csv'


def search(val, field='all'):
  body = {
      "query": {
          "bool": {
              # Celui ci prend une très grande importance
              "must": [
                  {
                      "bool": {
                          "should": [
                              {
                                  "match": {
                                      "all_text": {
                                          "query": val,
                                          "operator": "and",
                                          "cutoff_frequency": 0.0007,
                                          "fuzziness": "AUTO"
                                      }
                                  }
                              },
                              {
                                  "match": {
                                      "all_text": {
                                          "query": val,
                                          "operator": "and",
                                          "cutoff_frequency": 0.0007,
                                          "fuzziness": "AUTO"
                                      }
                                  }
                              }
                          ]
                      }
                  }
              ]
          }
      },
      "highlight": {
          "order": "score",
          "pre_tags": [
              "<mark>"
          ],
          "post_tags": [
              "</mark>"
          ],
          "fragment_size": 40,
          "fields": {
              "title.french_stemmed": {},
              "title.french_exact": {},
              "all_text.french_stemmed": {},
              "all_text.french_exact": {},
              "all_text.shingle": {},
              "path.french_stemmed": {},
              "path.french_exact": {}
          }
      },
      "size": 1000
  }
  res = esclient.search(index="code_du_travail_numerique", body=body)['hits']
  return res["hits"]


def search_requests(field):
  with open(request_file, newline='') as file:
    requests = csv.reader(file, delimiter=',', quotechar='|')
    # print(requests)
    with open('results/output2.csv', 'w', newline='') as output_csv_file:
      results_writer = csv.writer(
          output_csv_file, delimiter='	', quotechar='|')
      results_writer.writerow(
          ["request", "Number of Hits", "keys", "response urls"])
      for row in requests:
        print(row[0])
        results, summary = search(row[0], field=field)
        results_writer.writerow(
            [row[0]] + [summary["Number"]] + [summary["Keys"]] + results)


if __name__ == "__main__":
  field = sys.argv[1]
  arg = str(' '.join(sys.argv[2:]))
  search_requests(field=field)
