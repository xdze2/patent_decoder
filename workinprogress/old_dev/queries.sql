#standardSQL

SELECT
  publication_number
FROM
  `patents-public-data.patents.publications`
WHERE 
  ipc.code = 'A45D29'
LIMIT
  1000
  
  
  
/* GETS ALL :  26Go */
  
#standardSQL

SELECT
  root.publication_number,
  publication_date,
  root.title_localized,
  root.cpc,
  root.citation
FROM
  `patents-public-data.patents.publications` root,
  UNNEST( cpc ) AS cpc
WHERE 
 cpc.code like 'A45D29/02' and
 country_code = 'US'
LIMIT
  1000
