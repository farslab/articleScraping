# web_scraping/views.py
import csv
from datetime import datetime
from io import BytesIO
import json
import re
from urllib.parse import quote
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.text import slugify
from .models import Publication
import requests
from bs4 import BeautifulSoup
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.shortcuts import render, get_object_or_404
import os


def scrape(request):
    
    selected_source = request.POST.get('source', '')
    if request.method == 'POST' and selected_source=="dergipark" :
        search_query = request.POST.get('url', '')
        
        search_query = slugify(search_query)
        url = f"https://dergipark.org.tr/en/search?q={search_query}&section=articles" 

        # URL-encode username and password
        proxy_url = f'http://bordo:Bordo66156615@unblock.oxylabs.io:60000'
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }

        r = requests.get(url, proxies=proxies, verify=False,timeout=30)
        soup = BeautifulSoup(r.content, 'lxml')
        # get the required data from soup object
        title = soup.title.string
        
        #ilk 14 sonuc
        result_list = [card.find('h5', class_='card-title').find('a').get("href") 
               for card in soup.find_all('div', class_='card article-card dp-card-outline')[:14]]

        publications=[]
        for article_link in result_list:
            response = requests.get(article_link)
            article_html = response.content
            
            # Parse the HTML content with BeautifulSoup
            article_soup = BeautifulSoup(article_html, 'html.parser')

            # Extract data from the article page
            title = article_soup.find('meta', property='og:title')['content'] if article_soup.find('meta', property='og:title') else None
            authors = ', '.join([author.text.strip() for author in article_soup.find('p', class_='article-authors').find_all('a')]) if article_soup.find('p', class_='article-authors').find('a') else article_soup.find('p', class_='article-authors').text
            publication_type = article_soup.find('span', class_='kt-font-bold').text.strip() if article_soup.find('span', class_='kt-font-bold') else None
            publisher_name= article_soup.find('h1',id="journal-title")
            if publisher_name:
                publisher_name = publisher_name.text.strip()
            else:
                publisher_name = None
            print(publisher_name)
            try:
                keywords_article= ', '.join([keyword.text.strip() for keyword in article_soup.find(class_="article-keywords data-section").find_all('a')]) 
            except:
                keywords_article="None"
                
            doi = article_soup.find('a', class_='doi-link').get('href').split('doi.org/')[-1] if article_soup.find('a', class_='doi-link') else None
            pdf_url= article_soup.find('a', title='Article PDF link').get('href') if  article_soup.find('a', title='Article PDF link').get('href') else None

            date_element = article_soup.find('span', class_='article-subtitle')
            publication_date = None
            if date_element:
                try:
                    
                    date_string = date_element.text.strip().split(',')[-1].strip()
                    publication_date = datetime.strptime(date_string, '%d.%m.%Y').date()
                except:
                    publication_date = None

            abstract_element = article_soup.find('div', class_='article-abstract')
            abstract = abstract_element.find('p').text.strip() if abstract_element else None

            references_element = article_soup.find('div', class_='article-citations')
            references = references_element.text.strip() if references_element else None

            # Create a Publication instance and save it
            publication = Publication(
                title=title,
                authors=authors,
                publication_type=publication_type,
                publisher_name=publisher_name,
                publication_date=publication_date,
                keywords_searched=request.POST.get('url', ''),
                keywords_article=keywords_article,
                abstract=abstract,
                references=references,
                website_url=article_link,
                url=f'https://dergipark.org.tr{pdf_url}',
                doi_number=doi,
            )
            publication.save()
            publications.append(publication)

        context={
            'searchObjects':publications,
            'searchKeyword': request.POST.get('url', ''),

        }
        return render(request, 'results.html', context)
       
    if request.method == 'POST' and selected_source=="google_scholar":
        
        search_query = request.POST.get('url', '')
        search_query = slugify(search_query)
        url = f"https://scholar.google.com/scholar?hl=tr&q={search_query}" 
        # URL-encode username and password
        proxy_url = f'http://bordo:Bordo66156615@unblock.oxylabs.io:60000'
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        r = requests.get(url, proxies=proxies, verify=False)
        soup = BeautifulSoup(r.content, 'lxml')
        # get the required data from soup object
        title = soup.title.string
        headings = []
        authors_list = []
        citation_counts = []
        download_links = []
        website_urls=[]
        pdf_urls = []  # List to store PDF download URLs
        #search recommendation keyword
        
        
        h2_a_tag = soup.select_one('#gs_res_ccl_top h2.gs_rt a')

        if h2_a_tag and h2_a_tag.text:
            h2_a_text = h2_a_tag.text
            search_query_changed = h2_a_text
        else:
            search_query_changed = None
        for result in soup.find_all('div', class_='gs_r gs_or gs_scl'):
            heading = result.find(class_='gs_rt')
            if heading:
                headings.append(heading.text.strip())
            website_url=heading.find('a')['href']
            website_urls.append(website_url)
            
            authors_elem = result.find(class_='gs_a')
            if authors_elem:
                # Check if there are any <a> tags within gs_a
                author_links = authors_elem.find_all('a')
                if author_links:
                    # Extract and join the text content of each <a> tag (author name)
                    author_names = ', '.join(a.text.strip() for a in author_links)
                    authors_text = authors_elem.get_text(strip=True)
                    # Split the text using the '-' character and take the first part (author names)
                    author_names = authors_text.split('-')[0].strip()
                else:
                    # If there are no <a> tags, use the plain text content
                    authors_text = authors_elem.get_text(strip=True)
                    # Split the text using the '-' character and take the first part (author names)
                    author_names = authors_text.split('-')[0].strip()
                authors_list.append(author_names)
                
            citation_link = result.find('a', class_='gs_or_cit gs_or_btn gs_nph')
            if citation_link:
                citation_count_link = citation_link.find_next('a')

                if citation_count_link:
                    citation_count_text = citation_count_link.text.strip()
                    citation_count_match = re.search(r'\d+', citation_count_text)

                    if citation_count_match:
                        citation_count = int(citation_count_match.group())
                        citation_counts.append(citation_count)
                    else:
                        citation_counts.append(0)
                else:
                    citation_counts.append(0)
            else:
                citation_counts.append(0)
                
            download_link = result.find(class_='gs_or_ggsm').find('a')['href'] if result.find(class_='gs_or_ggsm') else ''
            download_links.append(download_link)
        # for website_url in website_urls:
        #         try:
        #             # Combine proxy and website URL
        #             full_url = website_url
        #             # Send a request to the website
        #             website_response = requests.get(full_url, verify=False)
                    
        #             if website_response.status_code == 200:
        #                 website_soup = BeautifulSoup(website_response.content, 'html.parser')
        #                 # Find the PDF link in the website's HTML
        #                 pdf_link = website_soup.find('a', {'href': re.compile(r'\.pdf$', re.I)})
                        
        #                 if pdf_link:
        #                     pdf_url = pdf_link.get('href')
        #                     # Ensure the PDF URL is absolute
        #                     if not pdf_url.startswith('http'):
        #                         pdf_url = urllib.parse.urljoin(website_url, pdf_url)
        #                     pdf_urls.append(pdf_url)
        #         except Exception as e:
        #             # Handle exceptions if any occur
        #             print(f"Error while processing {website_url}: {str(e)}")
        searchResultObjects=[]            
        for x, authors, download,citation_count,website_url in zip(headings, authors_list,download_links,citation_counts,website_urls):
            
            if website_url.endswith('pdf'):
                # If website_url ends with 'pdf', set url to website_url
                url = website_url
                print('url changed')
            else:
                # Otherwise, use the provided download link
                print('url not changed')

                url = download
                
            publication_obj = Publication.objects.create(
                title="%s" % x,
                authors="%s" % authors,
                keywords_searched="%s" % request.POST.get('url', ''),
                url="%s"% download,
                citation_count=citation_count,
                website_url=website_url,
               
            )
            searchResultObjects.append(publication_obj)
        
        context = {
            'title': title,
            'searchKeyword': request.POST.get('url', ''),
            'searchObjects': searchResultObjects,
        }
        if search_query_changed!=None:
             context.update({'searchKeywordChanged': search_query_changed})
        return render(request, 'results.html', context)
    else:
        return render(request, 'home.html')

    
    
def publicationDetails(request,id):
    
    publication = get_object_or_404(Publication, id=id)
    
    context={
        'publication':publication,
    }
    
    return render(request, 'publication_details.html',context)    
    
def home(request):
    context={
        'previousResults':Publication.objects.all().order_by('title')
    }
    
    return render(request, 'home.html',context)

def download_file(request):
    if 'scraped_data' in request.session:
        context = request.session['scraped_data']
        response = HttpResponse(content_type='')
        if request.POST['download_type'] == 'pdf':
            template_path = 'results.html'
            template = get_template(template_path)
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')
            filename = f"{context['title']}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            buffer = BytesIO()
            pisa_status = pisa.CreatePDF(html, dest=response, encoding='utf-8')
            if pisa_status.err:
                return HttpResponse('PDF generation failed')
        elif request.POST['download_type'] == 'csv':
            response = HttpResponse(content_type='text/csv')
            filename = f"{context['title']}.csv"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            writer = csv.writer(response)
            writer.writerow(['Title', 'Headings', 'Paragraphs'])
            rows = zip([context['title']], context['headings'], context['paragraphs'])
            for row in rows:
                writer.writerow(row)
        elif request.POST['download_type'] == 'json':
            response = HttpResponse(content_type='application/json')
            filename = f"{context['title']}.json"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            json.dump(context, response, indent=4)
        return response
    else:
        return render(request, 'home.html')