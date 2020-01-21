#!/usr/bin/env python
# coding: utf-8
import pickle
import csv
import os
import pandas as pd
import sys
sys.path.append(".")
sys.path.append("..")

if __name__ == "__main__":
        
    classifier = input("Input Classifier yang diinginkan: ")
#     classifier = "D3"
    print("--"*25)

    w, h = 4, 2;
    clf_model = [[0 for x in range(w)] for y in range(h)] 

    # [x][y]

    # X:
    # urgency = 0
    # impact  = 1

    # Y:
    # title            = 0
    # body             = 1
    # category         = 2
    # business service = 3

    predicts = ["urgency","impact"]
    columns = ["title","body","category","business_service"]

    i = 0
    j = 0
    for column_to_predict in predicts:
        j = 0
        for text_columns in columns:
            clf_model[i][j] = pickle.load(open('./pickle/text_'+classifier+'_'+text_columns+'_'+column_to_predict+'_model.pickle',"rb"))
            j+=1
        i+=1

    title_content = input("Masukkan judul insiden        : ")
    body_content = input("Masukkan deskripsi insiden    : ")
    cat_content = input("Masukkan kategory insiden     : ")
    bus_content = input("Masukkan bus. service insiden : ")
    print("--"*25)

    title = {"title":[title_content]}
    body = {"body":[body_content]}
    category = {"category": [cat_content]}
    business_service = {"business_service":[bus_content]}

    urgency_title = clf_model[0][0].predict(title)
    urgency_body = clf_model[0][1].predict(body)
    urgency_category = clf_model[0][2].predict(category)
    urgency_business_service = clf_model[0][0].predict(business_service)

    urgency_data = {"title":urgency_title,
                    "body":urgency_body,
                    "category":urgency_category,
                    "business service":urgency_business_service,
                    "result":None}

    urgency_df = pd.DataFrame(urgency_data)

    urgency_vars = urgency_df.iloc[:,:-1]

    urgency_model = pickle.load(open('./pickle/'+classifier+'_urgency_weight_model.pickle',"rb"))
    predicted_urgency = urgency_model.predict(urgency_vars)
    # print(predicted_urgency)

    impact_title = clf_model[1][0].predict(title)
    impact_body = clf_model[1][1].predict(body)
    impact_category = clf_model[1][2].predict(category)
    impact_business_service = clf_model[1][0].predict(business_service)

    impact_data = {"title":impact_title,
                    "body":impact_body,
                    "category":impact_category,
                    "business service":impact_business_service,
                    "result":None}

    impact_df = pd.DataFrame(impact_data)

    impact_vars = impact_df.iloc[:,:-1]

    impact_model = pickle.load(open('./pickle/'+classifier+'_impact_weight_model.pickle',"rb"))
    predicted_impact = impact_model.predict(impact_vars)
    # print(predicted_impact)

    final_data = {"urgency":predicted_urgency,
                "impact":predicted_impact,
                "result":None}

    final_df = pd.DataFrame(final_data)

    final_vars = final_df.iloc[:,:-1]

    final_model = pickle.load(open('./pickle/'+classifier+'_priority_model.pickle',"rb"))

    priority = final_model.predict(final_vars)

    symbols = ["/","?","<",".","!",",","[","]","(",")","{","}","`","/","*","-","+"]

    final_title = title["title"][0].lower()
    final_body = body["body"][0].lower()

    for symbol in symbols:
        final_body = final_body.replace(symbol,"")

    final_category = category["category"][0]
    final_business = business_service["business_service"][0]
    final_urgency = final_data["urgency"][0]
    final_impact = final_data["impact"][0]
    final_priority = priority[0]

    print("Title            :",final_title)
    print("Body             :",final_body)
    print("Category         :",final_category)
    print("Business Service :",final_business)
    print("Urgency          :",final_urgency)
    print("Impact           :",final_impact)
    print("Priority         :",final_priority)
    print("--"*25)
    give_feedback = True

    while give_feedback :
        choice = input("Apakah masih ada yang ingin diperbaiki? (Y/N)")
        if choice == "N" or choice == "n":
            give_feedback = False
        else:    
            print("Apa yang ingin anda review?")
            print("1. Urgency")
            print("2. Impact")
            print("3. Priority")
            review_item = input("Pilih bagian yang ingin anda review (1/2/3): ")
            print("--"*25)
            if review_item == "1":
                final_urgency = input("Input Urgency - 1/2/3: ")
            elif review_item == "2":    
                final_impact = input("Input Impact - 1/2/3: ")
            elif review_item == "3":
                final_priority = input("Input Priority - 1/2/3: ")
            print("--"*25)
            
            print("Title            :",final_title)
            print("Body             :",final_body)
            print("Category         :",final_category)
            print("Business Service :",final_business)
            print("Urgency          :",final_urgency)
            print("Impact           :",final_impact)
            print("Priority         :",final_priority)
            
            print("--"*25)

    add_to_dataset = [final_title, final_body, final_category, final_business, final_urgency, final_impact, final_priority]

    with open('./datasets/all_tickets.csv', 'a', newline='') as csvfile:  
        csvwriter = csv.writer(csvfile)  
        csvwriter.writerow(add_to_dataset)