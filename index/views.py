# from django.shortcuts import render 
from django.http import HttpResponse
from django.shortcuts import render
from pymongo import MongoClient
import nltk
import pdb
# Create your views here.
def index(request):
	context={}
	return render(request,'index.html');

def results(request):
	client = MongoClient('localhost', 27017)
	db=client.business
	query=request.POST.get("term",False)
	query = query.lower()
	tokens = nltk.word_tokenize(query)
	rank = dict()
	for token in tokens:
		query=db.invertedIndex.find({"key":token})

		if query.count()==0:
			continue
		# pdb.set_trace()
		data = dict(query[0])#query could return multiple object
		idf = data['idf']
		for docID, tf,position in data['list']:
			#get the link by docID
			linkQuery=db.doc_pair.find({"key":docID})
			link=dict(linkQuery[0])
			if docID not in rank:
				rank[link['link']] = tf*idf
			else:
				rank[link['link']] += tf*idf


    # if no correspond url
	if not rank:
		render(request,'index.html');

	linkQuery=db.doc_pair.find()
	link=dict(linkQuery[0])

    # convert to list [[docID, tfidf score]] and sort the score
	rank_lst = []
	for key, value in rank.items():
		rank_lst.append([key, value])
	sort_rank = sorted(rank_lst, key=lambda item: item[1], reverse=True)
	context={"result":sort_rank}


	return render(request,'result.html',context);

