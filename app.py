from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import gensim
from gensim.models import word2vec
from gensim.models import KeyedVectors
from sklearn.metrics.pairwise import cosine_similarity
import pickle
from gensim.models.word2vec import Text8Corpus
from flask import Flask, render_template, request
import pickle
import numpy as np
import re
import nltk
from Classification import *
import PyPDF2
import textract
import re
import string
import pandas as pd
import matplotlib.pyplot as plt
nltk.download('stopwords')


app = Flask(__name__,template_folder='.')
new_dataset = []

w_tokenizer = nltk.tokenize.WhitespaceTokenizer()
stopwords = stopwords.words('english')
stopwords.append('\n')

# Start of function
def get_processed_text(text):
	tags = re.compile(r'<.*?>')
	tags.sub('', text)                                 # to remove content in HTML tags
	text = re.sub(r'http\S+', ' ', text)               # to remove URLs
	text = re.sub(r'[^\w\s]',' ', text)                 # to remove punctuations
	text = re.sub(r'[^a-zA-Z]', ' ', text).lower()
	tokens = [w for w in w_tokenizer.tokenize(text) if w not in stopwords and w[0] != '@'] # tokenizing across whitsepaces to extract words
	return tokens

# End of function


categories=['women','job','coding','competition','scholarships','mentors','commerce','law','arts','creative','digital','session','event','finance']

@app.route('/',methods=['GET'])
def main():
        return render_template("index.html")


@app.route('/find-opportunity',methods=['GET'])
def findopportunity():
        return render_template("find-opportunity.html")

@app.route('/post-opportunity',methods=['GET'])
def opportunity():
        return render_template("post-opportunity.html")

@app.route('/resume-screening',methods=['GET'])
def screening():
        return render_template("resume-screening.html")

@app.route('/interviews',methods=['GET'])
def interviews():
        return render_template("interviews.html")

@app.route('/social',methods=['GET'])
def social():
        return render_template("social.html")

@app.route('/login',methods=['GET'])
def login():
        return render_template("log-in.html")

@app.route('/signup',methods=['GET'])
def signup():
        return render_template("sign-up.html")

@app.route('/post-opportunity', methods=['POST'])
def classify():
	if request.method == 'POST':

		text_linked = str(request.form['newopportunity'])

		new_dataset=get_processed_text(text_linked)

		for i in new_dataset:
			i=i.lower()

		copy=similar_one_out(new_dataset)

		output =[]

		count = 0
		for i in copy:
			if i==1:
				output.append(categories[count])
			count = count + 1

		print(output)
		return render_template("post-opportunity.html",output = output)

@app.route('/resume-screening', methods=['POST'])
def resumescreening():
	get_ipython().run_line_magic('matplotlib', 'inline')
	pdfFileObj = open('resume.pdf','rb')
	pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
	num_pages = pdfReader.numPages
	count = 0
	text = ""
	while count < num_pages:
		pageObj = pdfReader.getPage(count)
		count +=1
		text += pageObj.extractText()
	text = text.lower()
	text = re.sub(r'\d+','',text)
	text = text.translate(str.maketrans('','',string.punctuation))
	terms = {'Quality/Six Sigma':['black belt','capability analysis','control charts','doe','dmaic','fishbone',
                              'gage r&r', 'green belt','ishikawa','iso','kaizen','kpi','lean','metrics',
                              'pdsa','performance improvement','process improvement','quality',
                              'quality circles','quality tools','root cause','six sigma',
                              'stability analysis','statistical analysis','tqm'],
        'Operations management':['automation','bottleneck','constraints','cycle time','efficiency','fmea',
                                 'machinery','maintenance','manufacture','line balancing','oee','operations',
                                 'operations research','optimization','overall equipment effectiveness',
                                 'pfmea','process','process mapping','production','resources','safety',
                                 'stoppage','value stream mapping','utilization'],
        'Supply chain':['abc analysis','apics','customer','customs','delivery','distribution','eoq','epq',
                        'fleet','forecast','inventory','logistic','materials','outsourcing','procurement',
                        'reorder point','rout','safety stock','scheduling','shipping','stock','suppliers',
                        'third party logistics','transport','transportation','traffic','supply chain',
                        'vendor','warehouse','wip','work in progress'],
        'Project management':['administration','agile','budget','cost','direction','feasibility analysis',
                              'finance','kanban','leader','leadership','management','milestones','planning',
                              'pmi','pmp','problem','project','risk','schedule','scrum','stakeholders'],
        'Data analytics':['analytics','api','aws','big data','business intelligence','clustering','code',
                          'coding','data','database','data mining','data science','deep learning','hadoop',
                          'hypothesis test','iot','internet','machine learning','modeling','nosql','nlp',
                          'predictive','programming','python','r','sql','tableau','text mining',
                          'visualuzation'],
        'Healthcare':['adverse events','care','clinic','cphq','ergonomics','healthcare',
                      'health care','health','hospital','human factors','medical','near misses',
                      'patient','reporting system']}
	quality = 0
	operations = 0
	supplychain = 0
	project = 0
	data = 0
	healthcare = 0
	scores = []
	for area in terms.keys():

		if area == 'Quality/Six Sigma':
			for word in terms[area]:
				if word in text:
					quality +=1
			scores.append(quality)



		elif area == 'Operations management':
			for word in terms[area]:
				if word in text:
					operations +=1
				scores.append(operations)

		elif area == 'Supply chain':
			for word in terms[area]:
				if word in text:
					supplychain +=1
			scores.append(supplychain)

		elif area == 'Project management':
			for word in terms[area]:
				if word in text:
					project +=1
			scores.append(project)

		elif area == 'Data analytics':
			for word in terms[area]:
				if word in text:
					data +=1
			scores.append(data)

		else:
			for word in terms[area]:
				if word in text:
					healthcare +=1
			scores.append(healthcare)

	summary = pd.DataFrame(scores,index=terms.keys(),columns=['score']).sort_values(by='score',ascending=False)
	summary
	output_dir= './static/'
	pie = plt.figure(figsize=(10,10))
	plt.pie(summary['score'], labels=summary.index, explode = (0.1,0.2,0.3,0.4,0.5,0.6), autopct='%1.0f%%',shadow=True,startangle=90)
	plt.title('Industrial Engineering Candidate - Resume Decomposition by Areas')
	plt.axis('equal')
	plt.show()
	pie.savefig('{}/resume_screening_results.png'.format(output_dir))

	# return render_template("resume-screening.html",output = image)
	return render_template("resume-screening.html")




if __name__ == "__main__":
	app.run(debug=True)
