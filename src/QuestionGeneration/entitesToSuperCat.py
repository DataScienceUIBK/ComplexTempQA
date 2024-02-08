import db
import requests
import csv

instancesDict = {}

def update_dict(value):
    # Check if the value is already in the dictionary
    if value in instancesDict:
        # If yes, increment the number
        instancesDict[value] += 1
    else:
        # If no, add the value to the dictionary with the number 1
        instancesDict[value] = 1


entites = db.read_db('SELECT "EntityID" FROM "Entities" ORDER BY "EntityID" ASC ')

for e in entites:
    instances = db.getAttributeOfEntities('Q' + str(e[0]),'P31')
    for i in instances:
        update_dict(db.getNameOfEntity(i))




with open('entitiesSuperType4.csv', 'w', newline='') as csv_file:
    # Create a CSV writer
    csv_writer = csv.writer(csv_file)

    # Write the header
    csv_writer.writerow(["Value", "Number"])

    # Write each key-value pair to the CSV file
    for value, number in instancesDict.items():
        csv_writer.writerow([value, number])