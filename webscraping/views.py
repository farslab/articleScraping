# web_scraping/views.py
from datetime import datetime
import random
from django import forms
from elasticsearch_dsl import Q
from .models import Publication
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Publication
from .documents import PublicationDocument



class PublicationListView(ListView):
    model = Publication
    template_name = 'home.html'
    context_object_name = 'publications'
    
    def get_queryset(self):
        author_filter = self.request.GET.get('author', None)
        title_filter = self.request.GET.get('title', None)
        date_filter = self.request.GET.get('date', None)
        sort_by = self.request.GET.get('sort_by', 'title') 

        q_filters = []
        if author_filter:
            q_filters.append(Q("wildcard", authors=f'*{author_filter}*'))
        if title_filter:
            q_filters.append(Q("wildcard", title=f'*{title_filter}*'))
        
        search = PublicationDocument.search().query('bool', filter=q_filters)
        count=search.count()
        print(f'{count} Sonuç Bulundu')
        response = search[0:count].execute()
        publication_ids = [hit.meta.id for hit in response]

        queryset = Publication.objects.filter(id__in=publication_ids).order_by(sort_by)
        return queryset
   
        
def check_search_query(search_query):
        url = f"https://scholar.google.com/scholar?hl=tr&q={search_query}" 
        # URL-encode username and password
        proxy_url = f'http://bordo:Bordo66156615@unblock.oxylabs.io:60000'
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        r = requests.get(url, proxies=proxies, verify=False)
        soup = BeautifulSoup(r.content, 'lxml')
      
        h2_a_tag = soup.select_one('#gs_res_ccl_top h2.gs_rt a')
        if h2_a_tag and h2_a_tag.text:
            h2_a_text = h2_a_tag.text
            search_query_changed = h2_a_text
            changed=True
        else:
            search_query_changed=search_query
            changed=False
        
        return search_query_changed,changed

def scrape(request):
    if request.method == 'POST':
        #search query control from googlescholar
        search_query_form = request.POST.get('url', '')
        search_query,is_changed=check_search_query(search_query_form)
        url = f"https://dergipark.org.tr/en/search?q={search_query}&section=articles" 

        # URL-encode username and password
        proxy_url = f'http://bordo:Bordo66156615@unblock.oxylabs.io:60000'
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }

        r = requests.get(url, proxies=proxies, verify=False,timeout=45)
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
            try:
                keywords_article= ', '.join([keyword.text.strip() for keyword in article_soup.find(class_="article-keywords data-section").find_all('a')]) 
            except:
                keywords_article="None"
                
            doi = article_soup.find('a', class_='doi-link').get('href').split('doi.org/')[-1] if article_soup.find('a', class_='doi-link') else None
            pdf_url= article_soup.find('a', title='Article PDF link').get('href') if  article_soup.find('a', title='Article PDF link') else None

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
                citation_count = random.randint(0,200)

            )
            publication.save()
            publications.append(publication)

        context={
            'searchObjects':publications,
            'searchKeyword': request.POST.get('url', ''),
        }
        if is_changed:
             context.update({'searchKeywordChanged': search_query})
        return render(request, 'results.html', context)
       
    

class PublicationDetailView(DetailView):
    model = Publication
    template_name = "publication_details.html"
    context_object_name = "publication"

    def get_object(self, queryset=None):
        id = self.kwargs.get('id')
        return get_object_or_404(Publication, id=id)

