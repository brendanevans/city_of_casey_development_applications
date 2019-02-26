import requests
import json
import datetime
import dateutil.parser
import scraperwiki

def process(applications):
    url = 'https://www.casey.vic.gov.au'
    for row in applications['rows']:
        output = {}
        output['council_reference'] = row['application_number']
        output['address'] = row['field_coc_address'] + row['field_coc_suburb_ref']
        output['description'] = row['field_coc_proposal']
        output['info_url'] = url + row['field_coc_pdf'].strip('\n')
        output['comment_url'] = 'mailto:caseycc@casey.vic.gov.au'
        dateScraped = datetime.date.today().isoformat()
        output['date_scraped'] = dateScraped
        output['date_received'] = ''
        output['on_notice_from'] = ''
        date = dateutil.parser.parse(row['field_coc_date'], dayfirst=True)
        output['on_notice_to'] = date.strftime('%Y-%m-%d')
        try:
            alreadyExists = scraperwiki.sql.select('* FROM data WHERE council_reference=?', [da['council_reference']])
        except:
            alreadyExists = False

        if alreadyExists:
            print('Skipping: {}'.format(output['council_reference']))
        else:
            print('Saving: {}'.format(output['council_reference']))
            scraperwiki.sql.save(unique_keys=['council_reference'], data=output, table_name='data')

url = 'https://www.casey.vic.gov.au/api/planning-applications'

querystring = {'_format':'json', 'page':'0'}
payload = ''
response = requests.request('GET', url, data=payload, params=querystring)

applications = response.json()
process(applications)

pages = applications['pager']['total_pages']
if pages > 1:
    i = 1
    while i < pages:
        querystring = {'_format':'json', 'page':i}
        response = requests.request('GET', url, data=payload, params=querystring)
        applications = response.json()
        process(applications)
        i += 1