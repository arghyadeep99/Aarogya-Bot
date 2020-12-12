import os
import json
import pandas as pd
from py2neo import Graph,Node

class MedicalGraph:
	def __init__(self):
		self.g = Graph(
			host="127.0.0.1",
			http_port=7474,  
			user="neo4j",
			password="root")

	def read_nodes(self):
		departments, diseases, symptoms, disease_infos = [], [], [], []

		rels_department, rels_symptom, rels_accompany, rels_category = [], [], [], []


		file = "./data/medical_kb.csv"
		df = pd.read_csv(file, encoding='utf-8')
		count = 0
		# rows = ['name', 'desc', 'prevent', 'cause', 'symptom', 'accompany', 'cure_department', 'cure_way']
		for index, row in df.iterrows():
			disease_dict = {}
			count += 1
			print(count)
			disease = row['name']
			disease_dict['name'] = disease
			diseases.append(disease)
			disease_dict['desc'] = ''
			disease_dict['prevent'] = ''
			disease_dict['cause'] = ''
			disease_dict['symptom'] = ''
			disease_dict['accompany'] = ''           
			disease_dict['cure_department'] = ''
			disease_dict['cure_way'] = ''

			symptom_temp = row['symptom'].replace('[','').replace(']','').replace("'",'').split(",")
			symptoms += symptom_temp
			for symptom in symptom_temp:
				rels_symptom.append([disease, symptom])

			accompany_temp = row['accompany'].replace('[','').replace(']','').replace("'",'').split(",")
			for accompany in accompany_temp:
				rels_accompany.append([disease, accompany])

			disease_dict['desc'] = row['desc']

			disease_dict['prevent'] = row['prevent']

			disease_dict['cause'] = row['cause']

			cure_department = row['cure_department'].replace('[','').replace(']','').replace("'",'').split(",")
			if len(cure_department) == 1:
				 rels_category.append([disease, cure_department[0]])
			if len(cure_department) == 2:
				big = cure_department[0]
				small = cure_department[1]
				rels_department.append([small, big])
				rels_category.append([disease, small])

			disease_dict['cure_department'] = cure_department
			departments += cure_department

			disease_dict['cure_way'] = row['cure_way'].replace('[','').replace(']','').replace("'",'').split(",")

			disease_infos.append(disease_dict)
		return set(departments), set(symptoms), set(diseases), disease_infos,\
			   rels_department, rels_symptom, rels_accompany, rels_category

	def create_node(self, label, nodes):
		count = 0
		for node_name in nodes:
			node = Node(label, name=node_name)
			self.g.create(node)
			count += 1
			print(count, len(nodes))
		return

	def create_diseases_nodes(self, disease_infos):
		count = 0
		for disease_dict in disease_infos:
			node = Node("Disease", name=disease_dict['name'], desc=disease_dict['desc'],
						prevent=disease_dict['prevent'] ,cause=disease_dict['cause'],
						cure_department=disease_dict['cure_department']
						,cure_way=disease_dict['cure_way'])
			self.g.create(node)
			count += 1
			print(count)
		return

	def create_graphnodes(self):
		Departments, Symptoms, Diseases, disease_infos, rels_department, rels_symptom, rels_acompany, rels_category = self.read_nodes()
		self.create_diseases_nodes(disease_infos)

		self.create_node('Department', Departments)
		print(len(Departments))

		self.create_node('Symptom', Symptoms)
		return

	def create_graphrels(self):
		Departments, Symptoms, Diseases, disease_infos, rels_department, rels_symptom, rels_acompany, rels_category = self.read_nodes()
		
		self.create_relationship('Department', 'Department', rels_department, 'belongs_to', 'belong')
		self.create_relationship('Disease', 'Symptom', rels_symptom, 'has_symptom', 'symptom')
		self.create_relationship('Disease', 'Disease', rels_acompany, 'accompany_with', 'complication')
		self.create_relationship('Disease', 'Department', rels_category, 'disease_belongs_to', 'department')

	def create_relationship(self, start_node, end_node, edges, rel_type, rel_name):
		count = 0
		set_edges = []
		for edge in edges:
			set_edges.append('###'.join(edge))
		all = len(set(set_edges))
		for edge in set(set_edges):
			edge = edge.split('###')
			p = edge[0]
			q = edge[1]
			query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (
				start_node, end_node, p, q, rel_type, rel_name)
			try:
				self.g.run(query)
				count += 1
				print(rel_type, count, all)
			except Exception as e:
				print(e)
		return

	def export_data(self):
		Departments, Symptoms, Diseases, Cause, Accompany, Prevent, Cureway, Desc, disease_infos, rels_department, rels_symptom, rels_acompany, rels_category = self.read_nodes()
		f_department = open('dict/department.txt', 'w+')
		f_symptom = open('dict/symptoms.txt', 'w+')
		f_disease = open('dict/disease.txt', 'w+')


		f_department.write('\n'.join(list(Departments)))
		f_symptom.write('\n'.join(list(Symptoms)))
		f_disease.write('\n'.join(list(Diseases)))


		f_department.close()
		f_symptom.close()
		f_disease.close()

		return



if __name__ == '__main__':
	handler = MedicalGraph()
	handler.create_graphnodes()
	handler.create_graphrels()
	#handler.export_data()