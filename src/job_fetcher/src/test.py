import json

from curl_cffi import requests
from rich import print
import requests

url = "https://www.upwork.com/api/graphql/v1"

payload = {
    "query": """
  query VisitorJobSearch($requestVariables: VisitorJobSearchV1Request!) {
    search {
      universalSearchNuxt {
        visitorJobSearchV1(request: $requestVariables) {
          paging {
            total
            offset
            count
          }
          
    facets {
      jobType 
    {
      key
      value
    }
  
      workload 
    {
      key
      value
    }
  
      clientHires 
    {
      key
      value
    }
  
      durationV3 
    {
      key
      value
    }
  
      amount 
    {
      key
      value
    }
  
      contractorTier 
    {
      key
      value
    }
  
      contractToHire 
    {
      key
      value
    }
  
      
    }
  
          results {
            id
            title
            description
            relevanceEncoded
            ontologySkills {
              uid
              parentSkillUid
              prefLabel
              prettyName: prefLabel
              freeText
              highlighted
            }
            
            jobTile {
              job {
                id
                ciphertext: cipherText
                jobType
                weeklyRetainerBudget
                hourlyBudgetMax
                hourlyBudgetMin
                hourlyEngagementType
                contractorTier
                sourcingTimestamp
                createTime
                publishTime
                
                hourlyEngagementDuration {
                  rid
                  label
                  weeks
                  mtime
                  ctime
                }
                fixedPriceAmount {
                  isoCurrencyCode
                  amount
                }
                fixedPriceEngagementDuration {
                  id
                  rid
                  label
                  weeks
                  ctime
                  mtime
                }
              }
            }
          }
        }
      }
    }
  }
  """,
    "variables": {
        "requestVariables": {
            "sort": "recency",
            "highlight": True,
            "paging": {"offset": 10, "count": 10},
        }
    },
}
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
    "Accept": "*/*",
    "Accept-Language": "en-GB,en;q=0.7,en-US;q=0.3",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Referer": "https://www.upwork.com/nx/search/jobs/?page=2",
    "X-Upwork-Accept-Language": "en-US",
    "Content-Type": "application/json",
    "Authorization": "Bearer oauth2v2_74738b726aeb9ed7c364cb855fd61d6b",
    "Origin": "https://www.upwork.com",
    "Connection": "keep-alive",
}

response = requests.post(url, json=payload, headers=headers)

print(response.text)
