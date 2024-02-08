import psycopg2
import json
import db
import sys

#array = sys.argv[2]

def writeInFile(tax,name,year):
	#rows = db.read_db('select "ID", question, answer from "AnswerEntity" where (tax_type = ARRAY['+ array +']) ORDER BY random() limit 1000')#limit 10000000 OFFSET 20000000')
	rows = db.read_db('select "ID", question, answer from "AnswerEvent" where (tax_type = ARRAY['+ tax +"]) and date_part('year', timeframe[1]) = " +year+" AND date_part('year', timeframe[2]) = " +year+' ORDER BY random() limit 50')

	#rows = db.read_db('select id, question, answer, timeframe from "AnswerFinal" where (tax_type like  ' + "'%"+ tax +"%'" + ") and date_part('year', timeframe[1]::date) = " +year+" AND date_part('year', timeframe[2]::date) = " +year+' ORDER BY random() limit 50')

	# Convert data to a list of dictionaries
	data = [{"ID": row[0], "question": row[1], "answer": row[2]} for row in rows]


	# Write data to a JSON file
	with open('/run/media/raphael/T7/MasterJSON/uploads/' + year+ "/" + name + tax + '.json', 'w') as json_file:
		json.dump(data, json_file, indent=2)
	print(str(year) + " " + str(len(rows)))
tax = sys.argv[2]
name =  sys.argv[1]

for year in range(1987, 2008):
	writeInFile(tax,name,str(year))



