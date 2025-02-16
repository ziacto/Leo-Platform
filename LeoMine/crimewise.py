from utils.modules import *

def CrimewiseScrapper() :

    data = get_data("./database/data.json")
    locs = get_locations_list(data)
    spellings = get_spelling_list("./database/spell.csv")
    nlp = load_locations(locs, spellings)
    crime_list = get_crime_list("./database/crimes.csv")
    cities = get_cities(data)
    print("setup done")
    df = get_articles(0, crime_list, "./database/articles_crimewise.csv")
    # df = get_articles(0, crime_list, "./database/articles_crimewise.csv")
    print(df.shape)
    df_ = get_locations(df, data, nlp, cities, spellings, 0)
    print(df_)
    print("entering")
    df = preprocessing2(df, data)
    df["date"] = None
    df_with_date = df
    # df_final = check_for_duplicates(df_with_date, "./database/headlines.csv")
    df_final = df_with_date
    headlines_lst = []
    for index, row in df_final.iterrows():
        print(index)
        row["text"] = row["text"].replace("\n\n", " ")
        row["text"] = row["text"].replace("\n", " ")
        headline = row["text"].split(".")[0]
        headlines_lst.append(headline)
    df_final["headline"] = headlines_lst
    #saving_articles(df_final, "./database/headlines.csv")
    data_ = preprocessing(df_, data)
    save_data(data_, "./database/data.json")
    print("done scrappimg..")
    return df_final
    

   
